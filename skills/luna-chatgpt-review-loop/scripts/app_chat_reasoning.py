#!/usr/bin/env python3
"""Switch and verify the reasoning level in a native ChatGPT App Chat.

This adapter talks only to a localhost Chrome DevTools endpoint exposed by a
separate ChatGPT desktop App process. It never controls chatgpt.com in a
browser tab and it refuses non-loopback endpoints.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import secrets
import socket
import struct
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


APP_PAGE_URL = "app://-/index.html"
LEVEL_LABELS = {"extreme": "极高"}


class AppChatControlError(RuntimeError):
    pass


class SubmissionReceiptUncertain(AppChatControlError):
    """A send click occurred but its new request identity was not confirmed."""

    def __init__(self, message: str, reconcile_context: dict[str, Any]) -> None:
        super().__init__(message)
        self.reconcile_context = reconcile_context


def is_loopback_endpoint(endpoint: str) -> bool:
    parsed = urllib.parse.urlparse(endpoint)
    return (
        parsed.scheme == "http"
        and parsed.hostname in {"127.0.0.1", "localhost", "::1"}
        and parsed.port is not None
        and parsed.username is None
        and parsed.password is None
    )


def sidebar_selector(thread_id: str) -> str:
    if not thread_id or any(char not in "0123456789abcdef-" for char in thread_id.lower()):
        raise AppChatControlError("Chat ID must be a stable hexadecimal UUID")
    key = f"chatgpt:conversation:{thread_id}"
    return f'[data-sidebar-chatgpt-conversation-key={json.dumps(key)}]'


def _deadline(timeout: float) -> float:
    if timeout <= 0 or timeout > 120:
        raise AppChatControlError("timeout must be greater than 0 and at most 120 seconds")
    return time.monotonic() + timeout


def _remaining(deadline: float) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise AppChatControlError("timed out while waiting for the native App Chat")
    return remaining


def _read_http_json(url: str, deadline: float) -> Any:
    with urllib.request.urlopen(url, timeout=min(3, _remaining(deadline))) as response:
        return json.load(response)


class _WebSocket:
    def __init__(self, sock: socket.socket) -> None:
        self.sock = sock
        self.next_id = 1

    @classmethod
    def connect(cls, url: str, deadline: float) -> "_WebSocket":
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "ws" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise AppChatControlError("DevTools WebSocket must be loopback-only")
        port = parsed.port or 80
        sock = socket.create_connection((parsed.hostname, port), timeout=_remaining(deadline))
        key = base64.b64encode(secrets.token_bytes(16)).decode("ascii")
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {parsed.hostname}:{port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        ).encode("ascii")
        sock.sendall(request)
        response = b""
        while b"\r\n\r\n" not in response:
            sock.settimeout(_remaining(deadline))
            chunk = sock.recv(4096)
            if not chunk:
                raise AppChatControlError("DevTools WebSocket closed during handshake")
            response += chunk
            if len(response) > 65536:
                raise AppChatControlError("invalid DevTools WebSocket handshake")
        headers = response.split(b"\r\n\r\n", 1)[0].decode("latin-1")
        if not headers.startswith("HTTP/1.1 101"):
            raise AppChatControlError("DevTools WebSocket upgrade was rejected")
        header_values = {}
        for line in headers.split("\r\n")[1:]:
            if ":" not in line:
                continue
            name, value = line.split(":", 1)
            header_values[name.strip().lower()] = value.strip()
        expected = base64.b64encode(
            hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")).digest()
        ).decode("ascii")
        if header_values.get("sec-websocket-accept") != expected:
            raise AppChatControlError("DevTools WebSocket handshake could not be verified")
        return cls(sock=sock)

    def close(self) -> None:
        try:
            self._send_frame(0x8, b"")
        except OSError:
            pass
        self.sock.close()

    def _send_frame(self, opcode: int, payload: bytes) -> None:
        mask = secrets.token_bytes(4)
        length = len(payload)
        header = bytearray([0x80 | opcode])
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header.extend(struct.pack("!H", length))
        else:
            header.append(0x80 | 127)
            header.extend(struct.pack("!Q", length))
        header.extend(mask)
        masked = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
        self.sock.sendall(bytes(header) + masked)

    def _recv_exact(self, length: int, deadline: float) -> bytes:
        chunks: list[bytes] = []
        remaining = length
        while remaining:
            self.sock.settimeout(_remaining(deadline))
            chunk = self.sock.recv(remaining)
            if not chunk:
                raise AppChatControlError("DevTools WebSocket closed unexpectedly")
            chunks.append(chunk)
            remaining -= len(chunk)
        return b"".join(chunks)

    def _recv_text(self, deadline: float) -> str:
        parts: list[bytes] = []
        active_opcode: int | None = None
        while True:
            first, second = self._recv_exact(2, deadline)
            finished = bool(first & 0x80)
            opcode = first & 0x0F
            masked = bool(second & 0x80)
            length = second & 0x7F
            if length == 126:
                length = struct.unpack("!H", self._recv_exact(2, deadline))[0]
            elif length == 127:
                length = struct.unpack("!Q", self._recv_exact(8, deadline))[0]
            mask = self._recv_exact(4, deadline) if masked else b""
            payload = self._recv_exact(length, deadline)
            if masked:
                payload = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
            if opcode == 0x8:
                raise AppChatControlError("DevTools WebSocket closed unexpectedly")
            if opcode == 0x9:
                self._send_frame(0xA, payload)
                continue
            if opcode == 0xA:
                continue
            if opcode in {0x1, 0x2}:
                active_opcode = opcode
                parts = [payload]
            elif opcode == 0x0 and active_opcode is not None:
                parts.append(payload)
            else:
                continue
            if finished:
                if active_opcode != 0x1:
                    raise AppChatControlError("unexpected binary DevTools response")
                return b"".join(parts).decode("utf-8")

    def call(self, method: str, params: dict[str, Any], deadline: float) -> dict[str, Any]:
        request_id = self.next_id
        self.next_id += 1
        self._send_frame(
            0x1,
            json.dumps({"id": request_id, "method": method, "params": params}).encode("utf-8"),
        )
        while True:
            message = json.loads(self._recv_text(deadline))
            if message.get("id") != request_id:
                continue
            if "error" in message:
                raise AppChatControlError(f"DevTools command failed: {message['error']}")
            return message.get("result", {})

    def evaluate(self, expression: str, deadline: float) -> Any:
        result = self.call(
            "Runtime.evaluate",
            {"expression": expression, "returnByValue": True, "awaitPromise": True},
            deadline,
        )
        remote = result.get("result", {})
        if remote.get("subtype") == "error":
            raise AppChatControlError(remote.get("description", "App evaluation failed"))
        return remote.get("value")

    def click_point(self, x: float, y: float, deadline: float) -> None:
        common = {"x": x, "y": y, "button": "left", "clickCount": 1}
        self.call("Input.dispatchMouseEvent", {"type": "mousePressed", **common}, deadline)
        self.call("Input.dispatchMouseEvent", {"type": "mouseReleased", **common}, deadline)

    def insert_text(self, value: str, deadline: float) -> None:
        self.call("Input.insertText", {"text": value}, deadline)


def _wait_for_value(ws: _WebSocket, expression: str, deadline: float) -> Any:
    while True:
        value = ws.evaluate(expression, deadline)
        if value is not None and value is not False and value != "":
            return value
        time.sleep(min(0.2, _remaining(deadline)))


def _point_for(ws: _WebSocket, expression: str, deadline: float) -> dict[str, Any]:
    point = ws.evaluate(expression, deadline)
    if not isinstance(point, dict) or not all(key in point for key in ("x", "y")):
        raise AppChatControlError("target App control is not visible")
    return point


def _connect_native_app(endpoint: str, deadline: float) -> tuple[_WebSocket, str]:
    endpoint = endpoint.rstrip("/")
    version = _read_http_json(endpoint + "/json/version", deadline)
    browser_socket = version.get("webSocketDebuggerUrl")
    if not isinstance(browser_socket, str) or not browser_socket.startswith("ws://"):
        raise AppChatControlError("native App instance identity is unavailable")
    instance_id = "native-app-" + hashlib.sha256(browser_socket.encode("utf-8")).hexdigest()[:20]
    page: dict[str, Any] | None = None
    while page is None:
        targets = _read_http_json(endpoint + "/json/list", deadline)
        page = next(
            (target for target in targets if target.get("type") == "page" and target.get("url") == APP_PAGE_URL),
            None,
        )
        if page is None:
            time.sleep(min(0.2, _remaining(deadline)))
    return _WebSocket.connect(page["webSocketDebuggerUrl"], deadline), instance_id


def _navigate_and_verify(
    ws: _WebSocket,
    thread_id: str,
    expected_title: str | None,
    deadline: float,
) -> None:
    selector = sidebar_selector(thread_id)
    target_js = json.dumps(selector)
    _wait_for_value(
        ws,
        f'''(()=>{{const item=document.querySelector({target_js});const button=item?.querySelector('[role="button"]');if(!button)return null;button.click();return true}})()''',
        deadline,
    )
    title_js = json.dumps(expected_title) if expected_title else "null"
    _wait_for_value(
        ws,
        f'''(()=>{{const button=document.querySelector('button[aria-label="选择 ChatGPT 模型"]');if(!button)return null;const expected={title_js};if(!expected)return true;return [...document.querySelectorAll('button')].some(e=>e.innerText.trim()===expected&&!e.closest({target_js})&&e.getBoundingClientRect().width>0&&e.getBoundingClientRect().height>0)}})()''',
        deadline,
    )


def _message_records(ws: _WebSocket, deadline: float) -> list[dict[str, Any]]:
    records = ws.evaluate(
        r'''(()=>{const out=[];const walk=(root,visit)=>{const seen=new Set(),stack=[[root,0]];while(stack.length){const [v,d]=stack.pop();if(!v||typeof v!=='object'||seen.has(v)||d>4)continue;seen.add(v);visit(v);if(Array.isArray(v)){for(const x of v.slice(0,80))stack.push([x,d+1]);continue}for(const k of Object.keys(v).slice(0,120)){if(k==='children'||k==='item'||k==='turn'||k==='message'||k==='content'||k==='turnId'||k==='conversationId'||d<2){try{stack.push([v[k],d+1])}catch(_){}}}}};for(const e of document.querySelectorAll('[data-content-search-unit-key]')){const fk=Object.keys(e).find(k=>k.startsWith('__reactFiber'));if(!fk)continue;let f=e[fk],item=null,turn=null,turnId=null,conversationId=null;for(let i=0;f&&i<24;i++,f=f.return){const p=f.memoizedProps??{};if(!item&&['user-message','assistant-message'].includes(p.item?.type)&&typeof p.item?.messageId==='string')item=p.item;if(!turn&&typeof p.turn?.status==='string')turn=p.turn;if(!turnId&&typeof p.turnId==='string')turnId=p.turnId;if(!conversationId&&typeof p.conversationId==='string')conversationId=p.conversationId;walk(p,v=>{if(!item&&['user-message','assistant-message'].includes(v.type)&&typeof v.messageId==='string')item=v;if(!turn&&typeof v.status==='string'&&['complete','in_progress','pending'].includes(v.status)&&(v.id||v.turnId||v.messages))turn=v;if(!turnId&&typeof v.turnId==='string')turnId=v.turnId;if(!conversationId&&typeof v.conversationId==='string')conversationId=v.conversationId})}if(!item)continue;out.push({dom_key:e.getAttribute('data-content-search-unit-key'),turn_key:turnId??turn?.turnId??turn?.id??null,conversation_id:conversationId,turn_status:turn?.status??(item.completed===true?'complete':null),item_type:item.type,message_id:item.messageId,latest_message_id:item.latestMessageId??null,completed:item.type==='user-message'?true:item.completed===true,content:item.type==='user-message'?(item.message??item.content??''):(item.content??item.message??'')})}return out})()''',
        deadline,
    )
    if not isinstance(records, list):
        raise AppChatControlError("native App message identity could not be read")
    return records


def _stable_turn_identity(record: dict[str, Any]) -> str:
    """Identity for submission receipts: real turn_key, else durable message_id fallback."""
    turn_key = record.get("turn_key")
    if isinstance(turn_key, str) and turn_key and not turn_key.startswith("fallback-turn-"):
        return turn_key
    return str(record["message_id"])


def _trusted_turn_identity(record: dict[str, Any]) -> str | None:
    """Strict turn identity for request/reply pairing only.

    Returns a non-empty real turn_key string, or None. Never falls back to
    message_id, DOM order, content, or treats missing keys as equal (None==None).
    Fallback and blank keys are rejected so an unrelated complete reply cannot
    be paired with the current request.
    """
    turn_key = record.get("turn_key")
    if not isinstance(turn_key, str):
        return None
    cleaned = turn_key.strip()
    if not cleaned:
        return None
    if cleaned.startswith("fallback-turn-"):
        return None
    return cleaned


def _logical_composer_text(value: str) -> str:
    """Ignore contenteditable-only blank-line expansion, but preserve line content/order."""
    return "\n".join(line.strip() for line in value.replace("\r", "").split("\n") if line.strip())


def _build_reconcile_context(
    instance_id: str, thread_id: str, payload: str, baseline_ids: set[str],
) -> dict[str, Any]:
    return {
        "version": 1,
        "native_app_instance_id": instance_id,
        "thread_id": thread_id,
        "payload_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "baseline_message_ids": sorted(baseline_ids),
    }


def _validate_reconcile_context(
    context: dict[str, Any], instance_id: str, thread_id: str, payload: str,
) -> set[str]:
    if context.get("version") != 1:
        raise AppChatControlError("submission reconcile context version is invalid")
    if context.get("native_app_instance_id") != instance_id:
        raise AppChatControlError("native App instance changed before submission reconciliation")
    if context.get("thread_id") != thread_id:
        raise AppChatControlError("submission reconcile context targets a different Chat")
    expected_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    if context.get("payload_sha256") != expected_hash:
        raise AppChatControlError("submission reconcile context targets different review text")
    baseline = context.get("baseline_message_ids")
    if not isinstance(baseline, list) or len(baseline) > 10_000:
        raise AppChatControlError("submission reconcile baseline is invalid")
    if any(not isinstance(value, str) or not value for value in baseline):
        raise AppChatControlError("submission reconcile baseline contains an invalid message id")
    if len(set(baseline)) != len(baseline):
        raise AppChatControlError("submission reconcile baseline contains duplicate message ids")
    return set(baseline)


def _composer_state(ws: _WebSocket, deadline: float) -> dict[str, Any]:
    state = ws.evaluate(
        '''(()=>{const e=document.querySelector('[contenteditable="true"][role="textbox"][aria-label="给 ChatGPT 发消息"]');if(!e)return null;return {text:e.innerText,disabled:e.getAttribute('aria-disabled')==='true'}})()''',
        deadline,
    )
    if not isinstance(state, dict):
        raise AppChatControlError("native App composer state could not be read")
    return state


def _wait_for_submitted_request(
    ws: _WebSocket, deadline: float, baseline_ids: set[str], payload: str,
) -> dict[str, Any]:
    expected = _logical_composer_text(payload)
    while True:
        matches = [
            record for record in _message_records(ws, deadline)
            if record.get("item_type") == "user-message"
            and record.get("message_id") not in baseline_ids
            and _logical_composer_text(str(record.get("content", ""))) == expected
        ]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise AppChatControlError("multiple matching native App submission receipts were found")
        if time.monotonic() >= deadline:
            raise AppChatControlError("native App submission receipt was not visible before timeout")
        time.sleep(min(0.2, _remaining(deadline)))


def reconcile_submission(
    endpoint: str,
    thread_id: str,
    expected_title: str | None,
    text: str,
    context: dict[str, Any],
    timeout: float,
) -> dict[str, Any]:
    """Recover only a request proven new relative to the pre-click baseline."""
    if not is_loopback_endpoint(endpoint):
        raise AppChatControlError("endpoint must be an explicit loopback HTTP address with a port")
    payload = text.rstrip("\n")
    if not payload.strip():
        raise AppChatControlError("review text is empty")
    deadline = _deadline(timeout)
    ws, instance_id = _connect_native_app(endpoint, deadline)
    try:
        _navigate_and_verify(ws, thread_id, expected_title, deadline)
        expected = _logical_composer_text(payload)
        baseline_ids = _validate_reconcile_context(
            context, instance_id, thread_id, payload
        )
        matches = [
            record for record in _message_records(ws, deadline)
            if record.get("item_type") == "user-message"
            and record.get("message_id") not in baseline_ids
            and _logical_composer_text(str(record.get("content", ""))) == expected
        ]
        if len(matches) == 1:
            request = matches[0]
            return {
                "action": "app_chat_submission_reconciled",
                "channel": "chatgpt_desktop_app",
                "native_app_instance_id": instance_id,
                "thread_id": thread_id,
                "request_turn_id": _stable_turn_identity(request),
                "request_message_id": request["message_id"],
                "payload_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
                "verified": True,
            }
        if len(matches) > 1:
            raise AppChatControlError("multiple matching native App messages make the receipt ambiguous")
        composer = _composer_state(ws, deadline)
        draft = _logical_composer_text(str(composer.get("text", "")))
        if draft == expected:
            return {
                "action": "app_chat_submission_not_sent",
                "channel": "chatgpt_desktop_app",
                "native_app_instance_id": instance_id,
                "thread_id": thread_id,
                "draft_preserved": True,
                "safe_to_submit_once": True,
                "verified": True,
            }
        raise AppChatControlError(
            "no matching message or preserved draft was found; submission remains uncertain"
        )
    finally:
        ws.close()


def set_reasoning(
    endpoint: str,
    thread_id: str,
    level: str,
    expected_title: str | None,
    timeout: float,
) -> dict[str, Any]:
    if not is_loopback_endpoint(endpoint):
        raise AppChatControlError("endpoint must be an explicit loopback HTTP address with a port")
    label = LEVEL_LABELS.get(level)
    if label is None:
        raise AppChatControlError(f"unsupported reasoning level: {level}")
    deadline = _deadline(timeout)
    selector = sidebar_selector(thread_id)
    ws, instance_id = _connect_native_app(endpoint, deadline)
    try:
        target_js = json.dumps(selector)
        navigated = _wait_for_value(
            ws,
            f'''(()=>{{const item=document.querySelector({target_js});const button=item?.querySelector('[role="button"]');if(!button)return null;button.click();return true}})()''',
            deadline,
        )
        if not navigated:
            raise AppChatControlError("fixed App Chat could not be opened")
        title_js = json.dumps(expected_title) if expected_title else "null"
        state = _wait_for_value(
            ws,
            f'''(()=>{{const button=document.querySelector('button[aria-label="选择 ChatGPT 模型"]');if(!button)return null;const expected={title_js};let titleMatched=true;if(expected){{titleMatched=[...document.querySelectorAll('*')].some(e=>e.childElementCount===0&&e.textContent?.trim()===expected&&!e.closest({target_js})&&e.getBoundingClientRect().width>0&&e.getBoundingClientRect().height>0)}}if(!titleMatched)return null;return {{selected:button.innerText.trim(),titleMatched}}}})()''',
            deadline,
        )
        before = state["selected"]
        if before != label:
            trigger = _point_for(
                ws,
                '''(()=>{const e=document.querySelector('button[aria-label="选择 ChatGPT 模型"]');if(!e)return null;const r=e.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()''',
                deadline,
            )
            ws.click_point(trigger["x"], trigger["y"], deadline)
            option = _wait_for_value(
                ws,
                f'''(()=>{{const e=[...document.querySelectorAll('[role="menuitem"]')].find(x=>x.innerText.trim()==={json.dumps(label)});if(!e)return null;const r=e.getBoundingClientRect();return {{x:r.x+r.width/2,y:r.y+r.height/2}}}})()''',
                deadline,
            )
            ws.click_point(option["x"], option["y"], deadline)
        after = _wait_for_value(
            ws,
            f'''(()=>{{const b=document.querySelector('button[aria-label="选择 ChatGPT 模型"]');return b?.innerText.trim()==={json.dumps(label)}?b.innerText.trim():null}})()''',
            deadline,
        )
        menu_open = bool(ws.evaluate('!!document.querySelector(\'[role="menu"][data-state="open"]\')', deadline))
        if after != label or menu_open:
            raise AppChatControlError("App Chat reasoning readback did not settle")
        return {
            "action": "app_chat_reasoning_set",
            "channel": "chatgpt_desktop_app",
            "native_app_instance_id": instance_id,
            "thread_id": thread_id,
            "expected_title": expected_title,
            "before": before,
            "after": after,
            "changed": before != after,
            "verified": True,
        }
    finally:
        ws.close()


def submit_review(
    endpoint: str,
    thread_id: str,
    expected_title: str | None,
    text: str,
    timeout: float,
) -> dict[str, Any]:
    """Set Extreme and submit one inline review through the same App instance."""
    if not is_loopback_endpoint(endpoint):
        raise AppChatControlError("endpoint must be an explicit loopback HTTP address with a port")
    payload = text.rstrip("\n")
    if not payload.strip():
        raise AppChatControlError("review text is empty")
    if "\x00" in payload:
        raise AppChatControlError("review text contains a NUL byte")
    if len(payload.encode("utf-8")) > 200_000:
        raise AppChatControlError("review text exceeds the 200 KB native inline limit")
    mode = set_reasoning(endpoint, thread_id, "extreme", expected_title, timeout)
    deadline = _deadline(timeout)
    ws, instance_id = _connect_native_app(endpoint, deadline)
    clicked_send = False
    baseline_ids: set[str] = set()
    try:
        if instance_id != mode["native_app_instance_id"]:
            raise AppChatControlError("native App instance changed after reasoning confirmation")
        _navigate_and_verify(ws, thread_id, expected_title, deadline)
        baseline_ids = {
            record["message_id"]
            for record in _message_records(ws, deadline)
            if record.get("item_type") == "user-message"
        }
        composer_state = _composer_state(ws, deadline)
        if composer_state.get("disabled"):
            raise AppChatControlError("native App composer is disabled")
        existing_draft = str(composer_state.get("text", ""))
        if existing_draft.strip() and _logical_composer_text(existing_draft) != _logical_composer_text(payload):
            raise AppChatControlError("native App composer contains a different existing draft")
        if not existing_draft.strip():
            composer = _point_for(
                ws,
                '''(()=>{const e=document.querySelector('[contenteditable="true"][role="textbox"][aria-label="给 ChatGPT 发消息"]');if(!e)return null;const r=e.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()''',
                deadline,
            )
            ws.click_point(composer["x"], composer["y"], deadline)
            ws.insert_text(payload, deadline)
        payload_js = json.dumps(payload)
        _wait_for_value(
            ws,
            f'''(()=>{{const norm=s=>s.replace(/\\r/g,'').split(/\\n+/).map(x=>x.trim()).filter(Boolean).join('\\n');const e=document.querySelector('[contenteditable="true"][role="textbox"][aria-label="给 ChatGPT 发消息"]');return e&&norm(e.innerText)===norm({payload_js})}})()''',
            deadline,
        )
        ready = _wait_for_value(
            ws,
            '''(()=>{const model=document.querySelector('button[aria-label="选择 ChatGPT 模型"]');const send=document.querySelector('button[aria-label="发送"]');if(!model||model.innerText.trim()!=='极高'||!send||send.disabled)return null;const r=send.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()''',
            deadline,
        )
        ws.click_point(ready["x"], ready["y"], deadline)
        clicked_send = True
        receipt = _wait_for_submitted_request(ws, deadline, baseline_ids, payload)
        request = {
            "message_id": receipt["message_id"],
            "turn_key": receipt.get("turn_key"),
        }
        return {
            "action": "app_chat_review_submitted",
            "channel": "chatgpt_desktop_app",
            "native_app_instance_id": instance_id,
            "thread_id": thread_id,
            "expected_title": expected_title,
            "reasoning": "极高",
            "request_turn_id": _stable_turn_identity(request),
            "request_message_id": request["message_id"],
            "payload_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
            "verified": True,
        }
    except AppChatControlError as error:
        if clicked_send:
            raise SubmissionReceiptUncertain(
                "native App submission receipt is uncertain; reconcile from the captured pre-send baseline before any resend",
                _build_reconcile_context(instance_id, thread_id, payload, baseline_ids),
            ) from error
        raise
    finally:
        ws.close()


def read_reply(
    endpoint: str,
    thread_id: str,
    expected_title: str | None,
    request_message_id: str,
    timeout: float,
) -> dict[str, Any]:
    """Read only a complete assistant reply paired by trusted turn identity.

    Pairing requires the same non-empty real turn_key on request and assistant.
    Missing, blank, or fallback identities fail closed without returning reply
    body or a response message id. message_id fallback is never used here.
    """
    if not is_loopback_endpoint(endpoint):
        raise AppChatControlError("endpoint must be an explicit loopback HTTP address with a port")
    if not request_message_id:
        raise AppChatControlError("request message id is required")
    deadline = _deadline(timeout)
    ws, instance_id = _connect_native_app(endpoint, deadline)
    try:
        _navigate_and_verify(ws, thread_id, expected_title, deadline)
        records: list[dict[str, Any]] = []
        request: dict[str, Any] | None = None
        while request is None:
            records = _message_records(ws, deadline)
            request = next(
                (
                    record
                    for record in records
                    if record.get("item_type") == "user-message"
                    and record.get("message_id") == request_message_id
                ),
                None,
            )
            if request is not None or time.monotonic() >= deadline:
                break
            time.sleep(min(0.2, _remaining(deadline)))
        if request is None:
            return {
                "action": "app_chat_request_not_visible",
                "channel": "chatgpt_desktop_app",
                "native_app_instance_id": instance_id,
                "thread_id": thread_id,
                "request_message_id": request_message_id,
                "reply_complete": False,
            }
        request_turn = _trusted_turn_identity(request)
        if request_turn is None:
            return {
                "action": "app_chat_reply_identity_unavailable",
                "channel": "chatgpt_desktop_app",
                "native_app_instance_id": instance_id,
                "thread_id": thread_id,
                "request_message_id": request_message_id,
                "reply_complete": False,
            }
        replies = [
            record
            for record in records
            if record.get("item_type") == "assistant-message"
            and _trusted_turn_identity(record) == request_turn
            and record.get("message_id") != request_message_id
        ]
        complete = next(
            (
                record
                for record in reversed(replies)
                if record.get("completed") is True
                and record.get("turn_status") == "complete"
                and str(record.get("content", "")).strip()
            ),
            None,
        )
        if complete is None:
            return {
                "action": "app_chat_reply_pending",
                "channel": "chatgpt_desktop_app",
                "native_app_instance_id": instance_id,
                "thread_id": thread_id,
                "request_message_id": request_message_id,
                "reply_complete": False,
            }
        return {
            "action": "app_chat_reply_complete",
            "channel": "chatgpt_desktop_app",
            "native_app_instance_id": instance_id,
            "thread_id": thread_id,
            "request_message_id": request_message_id,
            "response_turn_id": request_turn,
            "response_message_id": complete["message_id"],
            "reply": complete["content"],
            "reply_complete": True,
        }
    finally:
        ws.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Control a native ChatGPT desktop App Chat")
    subparsers = parser.add_subparsers(dest="command", required=True)
    command = subparsers.add_parser("set-reasoning")
    command.add_argument("--endpoint", required=True)
    command.add_argument("--thread-id", required=True)
    command.add_argument("--level", choices=sorted(LEVEL_LABELS), required=True)
    command.add_argument("--expected-title")
    command.add_argument("--timeout", type=float, default=30)
    submit = subparsers.add_parser("submit-review")
    submit.add_argument("--endpoint", required=True)
    submit.add_argument("--thread-id", required=True)
    submit.add_argument("--expected-title")
    submit.add_argument("--text-file", required=True)
    submit.add_argument("--timeout", type=float, default=45)
    reconcile = subparsers.add_parser("reconcile-submission")
    reconcile.add_argument("--endpoint", required=True)
    reconcile.add_argument("--thread-id", required=True)
    reconcile.add_argument("--expected-title")
    reconcile.add_argument("--text-file", required=True)
    reconcile.add_argument("--context-file", required=True)
    reconcile.add_argument("--timeout", type=float, default=20)
    read = subparsers.add_parser("read-reply")
    read.add_argument("--endpoint", required=True)
    read.add_argument("--thread-id", required=True)
    read.add_argument("--expected-title")
    read.add_argument("--request-message-id", required=True)
    read.add_argument("--timeout", type=float, default=20)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "set-reasoning":
            result = set_reasoning(
                endpoint=args.endpoint,
                thread_id=args.thread_id,
                level=args.level,
                expected_title=args.expected_title,
                timeout=args.timeout,
            )
        elif args.command == "submit-review":
            result = submit_review(
                endpoint=args.endpoint,
                thread_id=args.thread_id,
                expected_title=args.expected_title,
                text=Path(args.text_file).read_text(encoding="utf-8"),
                timeout=args.timeout,
            )
        elif args.command == "reconcile-submission":
            context_value = json.loads(Path(args.context_file).read_text(encoding="utf-8"))
            if isinstance(context_value, dict) and "reconcile_context" in context_value:
                context_value = context_value["reconcile_context"]
            if not isinstance(context_value, dict):
                raise AppChatControlError("submission reconcile context file is invalid")
            result = reconcile_submission(
                endpoint=args.endpoint,
                thread_id=args.thread_id,
                expected_title=args.expected_title,
                text=Path(args.text_file).read_text(encoding="utf-8"),
                context=context_value,
                timeout=args.timeout,
            )
        elif args.command == "read-reply":
            result = read_reply(
                endpoint=args.endpoint,
                thread_id=args.thread_id,
                expected_title=args.expected_title,
                request_message_id=args.request_message_id,
                timeout=args.timeout,
            )
        else:
            raise AppChatControlError(f"unsupported command: {args.command}")
    except SubmissionReceiptUncertain as error:
        print(json.dumps({
            "action": "app_chat_submission_uncertain",
            "error": str(error),
            "reconcile_context": error.reconcile_context,
        }, ensure_ascii=False))
        return 2
    except (AppChatControlError, OSError, ValueError, json.JSONDecodeError, urllib.error.URLError) as error:
        print(json.dumps({"action": "needs_user_decision", "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
