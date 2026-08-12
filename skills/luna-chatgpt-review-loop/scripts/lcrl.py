#!/usr/bin/env python3
"""SuperLuna durable controller with stable LCRL compatibility entrypoints.

The module deliberately uses only the Python standard library. It keeps mutable
workflow state outside prompts, observes the previous Codex runtime turn, and
permits only identity-gated one-shot checks while the owning task waits for Chat.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import secrets
import sys
import tempfile
import time
from urllib.parse import urlsplit
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator, Iterable

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python >= 3.11 is required
    tomllib = None


SCHEMA_VERSION = 7
CONTROLLER_VERSION = 50
SKILL_REVISION = "2026-08-12.4"
MAX_HEARTBEAT_BYTES = 1200
BINDING_REGISTRY_VERSION = 1
NAMING_TEMPLATE_VERSION = 3
SUPPORTED_NAMING_TEMPLATE_VERSIONS = {1, 2, 3}
MODEL_POLICY_VERSION = 5
VALID_IMPLEMENTATION_ROLES = {"luna_medium", "terra_medium"}
PRO_THRESHOLD_ACTIVE_MINUTES = 180
PRO_MINIMUM_MEANINGFUL_STEPS = 3
MAX_PROGRESS_EVENTS = 256
ACTIVE_STATUSES = {
    "local_work",
    "review_submit_pending",
    "review_receipt_pending",
    "review_waiting",
    "result_received",
    "result_quarantined",
}
MONITOR_STATUSES = {"review_receipt_pending", "review_waiting"}
USER_STATUS_LABELS = {
    "local_work": "正在开发",
    "review_submit_pending": "正在开发",
    "review_receipt_pending": "需要你决定",
    "review_waiting": "等待 Chat",
    "result_received": "正在按 Chat 意见修改",
    "result_quarantined": "需要你决定",
    "external_blocked": "需要你决定",
    "completed": "已完成",
}
USER_STATUS_MESSAGES = {
    "正在开发": ("正在继续处理项目。", "无需操作。"),
    "等待 Chat": ("已交给 Chat，原任务正在等待回复。", "无需操作；原任务会在回复到达后继续。"),
    "正在按 Chat 意见修改": ("已读到 Chat 的意见，正在按意见修改。", "无需操作。"),
    "需要你决定": ("现在无法安全地自动继续。", "请说明要继续、调整方向，还是停止。"),
    "已完成": ("用户总体目标已经完成。", "无需操作。"),
}
VALID_STATUSES = ACTIVE_STATUSES | {"external_blocked", "completed"}
VALID_REQUEST_REASONING_MODES = {"none", "extreme", "unconfirmed", "legacy"}
ALLOWED_TRANSITIONS = {
    "local_work": {"local_work", "review_submit_pending", "external_blocked", "completed"},
    "review_submit_pending": {"review_submit_pending", "review_receipt_pending", "review_waiting", "local_work", "external_blocked"},
    "review_receipt_pending": {"review_receipt_pending", "review_waiting", "external_blocked"},
    "review_waiting": {"review_waiting", "result_received", "result_quarantined", "external_blocked"},
    "result_received": {"local_work", "external_blocked", "completed"},
    "result_quarantined": {"result_quarantined", "result_received", "review_submit_pending", "external_blocked"},
    "external_blocked": VALID_STATUSES,
    "completed": {"completed"},
}
VALID_PAYLOAD_MODES = {"inline_packet", "app_attachment", "mcp_readonly"}
VALID_ATTACHMENT_CAPABILITIES = {"native", "manual", "unavailable"}
VALID_FILESYSTEM_CAPABILITIES = {"inline", "mcp_verified", "unavailable"}
VALID_COORDINATION_CAPABILITIES = {"available", "unavailable", "unknown"}
VALID_STARTUP_BROWSER_STATES = {"initialized", "uninitialized"}
VALID_STARTUP_CHAT_LOGIN_STATES = {"logged_in", "not_logged_in"}
VALID_STARTUP_CHAT_SELECTION_STATES = {"unique", "not_unique"}
VALID_COORDINATION_MODES = {"foreground", "automatic"}
VALID_GOAL_MODES = {"continuous", "single_stage"}
VALID_COORDINATION_REVIEW_MODES = {"unconfirmed", "extreme", "pro"}
VALID_REVIEW_TRANSPORTS = {"app_chat_review", "in_app_browser"}
BROWSER_REFRESH_INTERVAL_SECONDS = 180
BROWSER_RATE_LIMIT_INITIAL_BACKOFF_SECONDS = 900
BROWSER_RATE_LIMIT_MAX_BACKOFF_SECONDS = 3600
VALID_ATTACHMENT_VERIFICATION = {"not_required", "unverified", "verified", "manual_confirmed", "unavailable"}
VALID_PRO_STATUSES = {"tracking", "eligible", "confirmation_required", "in_review"}
VALID_TERRA_STATUSES = {"idle", "requested", "approved"}
VALID_NEXT_OPERATION_STATUSES = {"none", "validated", "applied"}
VALID_TERRA_SIGNALS = {
    "repeated_test_failure",
    "cross_module_refactor",
    "debugger_impasse",
    "performance_investigation",
    "migration_complexity",
}
VALID_MODEL_ROUTES = {"medium", "high_once", "terra_request"}
VALID_EXECUTION_STATUSES = {"unknown", "authorized", "verified"}
VALID_EXECUTION_SOURCES = {"none", "manual_confirmed"}
VALID_EXECUTION_VERIFICATION_TYPES = {"none", "manual_attested"}
VALID_HIGH_SIGNALS = {
    "safety_concurrency_recovery",
    "cross_contract_change",
    "two_failed_attempts",
    "evidence_conflict",
}
MODEL_ROUTE_BEGIN = "[SUPERLUNA_MODEL_ROUTE]"
MODEL_ROUTE_END = "[/SUPERLUNA_MODEL_ROUTE]"
HIGH_MAX_LAST_10_STEPS = 2
TERRA_MAX_LAST_20_STEPS = 1
MAX_MODEL_ROUTE_EVENTS = 64
RESULT_BEGIN = "[LCRL_RESULT_V2]"
RESULT_END = "[LCRL_RESULT_V2_END]"
RESULT_END_ALIASES = (RESULT_END, "[/LCRL_RESULT_V2]")
LEGACY_RESULT_BEGIN = "[LCRL_RESULT_V1]"
LEGACY_RESULT_END = "[LCRL_RESULT_END]"
NETWORK_ERROR_PATTERN = re.compile(
    r"stream disconnected before completion|error sending request|connection reset|"
    r"network(?:\s+error)?|timed?\s*out|econnreset|fetch failed",
    re.IGNORECASE,
)
POLICY_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"gpt[-\s]?5(?:\.6)?[-\s]?sol",
        r"codex\s+sol",
        r"禁止\s*luna",
        r"改用\s*sol",
        r"review_transport",
        r"chatgptworkcloud",
        r"create_thread",
        r"review_quota_source",
        r"implementation_role",
        r"codex_review_forbidden",
    )
]

# These phrases are deliberately conservative.  They only decide whether the
# controller can hand a prose reply back to the implementation task; they do
# not attempt to implement the review itself.
DESTRUCTIVE_REPLY_PATTERN = re.compile(
    r"\b(delete|remove)\b|删除|移除",
    re.IGNORECASE,
)
OTHER_HIGH_IMPACT_REPLY_PATTERN = re.compile(
    r"\b(publish|deploy|release|pay|payment|permission|credential)\b|"
    r"发布|部署|上线|付款|支付|权限|凭证",
    re.IGNORECASE,
)
LOCAL_COUNTEREXAMPLE_MUTATION_PATTERN = re.compile(
    r"counterexample|fixture|synthetic|in[- ]memory|sqlite|temporary test data|"
    r"反例|测试夹具|合成数据|内存数据库|临时测试数据",
    re.IGNORECASE,
)
REJECTED_MUTATION_ASSERTION_PATTERN = re.compile(
    r"\b(?:delete|remove|mutation|operation)\s+must\s+be\s+rejected\b|"
    r"\bmust\s+remain\s+unchanged\b|"
    r"删除(?:必须|应当|应该)被拒绝|(?:必须|应当|应该)保持不变",
    re.IGNORECASE,
)
DATABASE_ROW_CONTEXT_PATTERN = re.compile(
    r"\b(?:fk|foreign key|cascade|table|row|association|sqlite|database)\b|"
    r"外键|级联|数据表|数据行|关联|数据库",
    re.IGNORECASE,
)
EXTERNAL_DESTRUCTIVE_TARGET_PATTERN = re.compile(
    r"\b(production|prod|live|customer|user data|repository|source files?)\b|"
    r"生产(?:环境|数据库|数据)?|线上|真实用户|用户数据|仓库|项目文件|源码",
    re.IGNORECASE,
)
VAGUE_REPLY_PATTERN = re.compile(
    r"^(?:整体|总体|方向|看起来|感觉)?[^。！？\n]{0,24}(?:没问题|可以|通过|不错|很好)[。！？!！]?$|"
    r"^(?:looks? good|seems? fine|approved|okay|ok)[.!]?$",
    re.IGNORECASE,
)
EXPLICIT_NEXT_STEP_HEADING_PATTERN = re.compile(
    r"(?im)^(?:#{1,6}\s*)?(?:(?:唯一)?下一步|"
    r"(?:minimum\s+)?in[- ]scope\s+next\s+step)\s*[｜|:：]\s*.+$"
)
EXPLICIT_STOP_ACTION_PATTERN = re.compile(
    r"(?im)^(?:#{1,6}\s*)?(?:最终结论\s*[｜|:：]\s*)?"
    r"(?:建议|应当|应该|请|可以)?\s*停止(?:本|当前|该)?"
    r"[^\n]{0,80}(?:评审|审阅|开发)[^\n]{0,30}(?:循环|流程)?[。.]?\s*$"
)
DEFERRED_SCOPE_LINE_PATTERN = re.compile(
    r"(?:如果|若).{0,80}通过.{0,160}(?:剩余|其余).{0,160}(?:后续|转交|另行)|"
    r"(?:剩余|其余).{0,160}(?:后续|转交|另行)|"
    r"(?:if|once).{0,80}(?:pass|complete).{0,160}(?:remaining|rest).{0,160}"
    r"(?:later|follow[- ]?up|defer|hand[- ]?off)",
    re.IGNORECASE,
)


class LCRLError(RuntimeError):
    """User-facing deterministic controller error."""


class StateRevisionConflict(LCRLError):
    """Another process updated the state file between load and compare-and-write."""


class StateLockTimeout(LCRLError):
    """The short-lived cross-process state lock could not be acquired in time."""


STATE_LOCK_TIMEOUT_SECONDS = 2.0
STATE_LOCK_POLL_SECONDS = 0.01


def state_lock_path(state_path: Path) -> Path:
    """Sidecar lock file next to the durable state JSON."""
    return state_path.parent / f".{state_path.name}.lock"


@contextmanager
def acquire_state_lock(
    state_path: str | Path,
    timeout: float = STATE_LOCK_TIMEOUT_SECONDS,
) -> Iterator[None]:
    """Acquire a short-lived exclusive lock for state compare-and-write.

    Uses fcntl on POSIX and msvcrt on Windows. The operating system releases
    the lock if this process exits, so a crash cannot leave a permanent lock
    that requires manual deletion. The critical section must stay millisecond
    scale: never hold this lock across App Chat, network, or project work.
    """
    path = Path(state_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_file = state_lock_path(path)
    fd = os.open(str(lock_file), os.O_RDWR | os.O_CREAT, 0o644)
    locked = False
    deadline = time.monotonic() + max(0.0, float(timeout))
    try:
        # Windows byte-range locks require at least one lockable byte.
        if os.fstat(fd).st_size == 0:
            os.write(fd, b"0")
            os.lseek(fd, 0, os.SEEK_SET)
        while True:
            try:
                if os.name == "nt":  # pragma: no cover - exercised on Windows
                    import msvcrt

                    os.lseek(fd, 0, os.SEEK_SET)
                    msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise StateLockTimeout("state lock busy") from None
                time.sleep(STATE_LOCK_POLL_SECONDS)
        yield
    finally:
        if locked:
            try:
                if os.name == "nt":  # pragma: no cover - exercised on Windows
                    import msvcrt

                    os.lseek(fd, 0, os.SEEK_SET)
                    msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(fd, fcntl.LOCK_UN)
            except OSError:
                pass
        os.close(fd)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_time(value: str | None) -> datetime | None:
    if not value or value == "none":
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def is_timestamp(value: Any) -> bool:
    try:
        return isinstance(value, str) and parse_time(value) is not None
    except ValueError:
        return False


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def title_component(value: str, field: str, max_chars: int) -> str:
    cleaned = re.sub(r"[\r\n｜]+", " ", str(value)).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    if not cleaned or cleaned == "none":
        raise LCRLError(f"{field} is required")
    if len(cleaned) > max_chars:
        raise LCRLError(f"{field} must be at most {max_chars} characters")
    return cleaned


def build_binding_titles(
    display_name: str,
    iteration: str,
    work_status_label: str,
    template_version: int = NAMING_TEMPLATE_VERSION,
) -> dict[str, str]:
    """Generate matching titles without putting mutable model choices in identity labels."""
    display = title_component(display_name, "display_name", 12)
    cycle = title_component(iteration, "iteration", 12)
    work_status = title_component(work_status_label, "work_status_label", 12)
    if template_version == 1:
        return {
            "work": f"🛠 {display}｜执行｜{cycle}{work_status}",
            "chat": f"💬 {display}｜Chat评审｜{cycle}·Sol极高",
            "automation": f"🔄 {display}｜恢复检查",
        }
    if template_version == 2:
        return {
            "work": f"{display}｜执行｜{cycle}",
            "chat": f"{display}｜评审｜{cycle}",
            "automation": f"{display}｜等待｜{cycle}",
        }
    if template_version != NAMING_TEMPLATE_VERSION:
        raise LCRLError(f"unsupported naming template version: {template_version}")
    return {
        "work": f"🛠 {display}｜执行｜{cycle}",
        "chat": f"💬 {display}｜评审｜{cycle}",
        "automation": f"⏳ {display}｜等待｜{cycle}",
    }


def default_execution_fact(status: str = "unknown") -> dict[str, str]:
    """Describe only the execution fact the controller can actually prove."""
    return {
        "execution_status": status,
        "execution_source": "none",
        "execution_proof": "none",
        "execution_verified_at": "none",
        "execution_verification_type": "none",
    }


def apply_execution_fact_defaults(record: dict[str, Any], *, legacy_authorized: bool = False) -> None:
    """Safely migrate old permission records without inventing execution proof."""
    if "execution_status" not in record:
        record["execution_status"] = "authorized" if legacy_authorized else "unknown"
    record.setdefault("execution_source", "none")
    record.setdefault("execution_proof", "none")
    record.setdefault("execution_verified_at", "none")
    # Alpha.16 had only a human-supplied verification source. Preserve that
    # fact honestly during migration instead of implying platform verification.
    if "execution_verification_type" not in record:
        record["execution_verification_type"] = (
            "manual_attested"
            if record["execution_status"] == "verified" and record["execution_source"] == "manual_confirmed"
            else "none"
        )


def default_model_policy(implementation_role: str = "luna_medium") -> dict[str, Any]:
    if implementation_role not in VALID_IMPLEMENTATION_ROLES:
        raise LCRLError("implementation_role must be luna_medium or terra_medium")
    return {
        "version": MODEL_POLICY_VERSION,
        "automatic_model_switch": False,
        "automatic_thread_creation": False,
        "executor": {"default": implementation_role, "current": implementation_role},
        "reviewer": {"default": "sol_extreme", "current": "sol_extreme"},
        "progress": {
            "active_minutes_since_pro": 0,
            "meaningful_steps_since_pro": 0,
            "events": [],
        },
        "routing": {
            "medium_minimum_percent": 80,
            "high_maximum_last_10_steps": HIGH_MAX_LAST_10_STEPS,
            "terra_maximum_last_20_steps": TERRA_MAX_LAST_20_STEPS,
            "meaningful_step_index": 0,
            "advice": {
                "requested": "medium",
                "effective": "medium",
                "status": "default",
                "reason": "no_valid_escalation_advice",
                "response_message_id": "none",
                "blocker_id": "none",
                "signal": "none",
                "high_attempt_id": "none",
                "evidence": "none",
                "scope": "none",
                "exit_criteria": "none",
                "recorded_at": "none",
                **default_execution_fact(),
            },
            "high_attempts": [],
            "terra_turns": [],
        },
        "pro": {
            "threshold_active_minutes": PRO_THRESHOLD_ACTIVE_MINUTES,
            "minimum_meaningful_steps": PRO_MINIMUM_MEANINGFUL_STEPS,
            "status": "tracking",
            "eligibility_notified": False,
            "request_id": "none",
            "requested_at": "none",
            "user_confirmed": False,
            "started_at": "none",
            "last_request_id": "none",
            "last_outcome": "none",
            "last_reason": "none",
            "last_completed_at": "none",
            "last_guide_version": "none",
            "last_guide_path": "none",
            "last_guide_sha256": "none",
            "review_count": 0,
        },
        "terra": {
            "status": "idle",
            "request_id": "none",
            "signal": "none",
            "reason": "none",
            "requested_at": "none",
            "user_confirmed": False,
            "approved_at": "none",
            "blocker_id": "none",
            "high_attempt_id": "none",
            "evidence_fingerprint": "none",
            "advice_response_message_id": "none",
            "last_request_id": "none",
            "last_outcome": "none",
            "last_reason": "none",
            "last_completed_at": "none",
            "request_count": 0,
            **default_execution_fact(),
        },
    }


def pro_is_eligible(model_policy: dict[str, Any]) -> bool:
    progress = model_policy["progress"]
    pro = model_policy["pro"]
    return (
        progress["active_minutes_since_pro"] >= pro["threshold_active_minutes"]
        and progress["meaningful_steps_since_pro"] >= pro["minimum_meaningful_steps"]
    )


def empty_binding_registry() -> dict[str, Any]:
    return {"schema_version": BINDING_REGISTRY_VERSION, "revision": 0, "updated_at": utc_now(), "tasks": []}


def validate_binding_registry(value: dict[str, Any]) -> None:
    errors: list[str] = []
    if value.get("schema_version") != BINDING_REGISTRY_VERSION:
        errors.append(f"registry schema_version must be {BINDING_REGISTRY_VERSION}")
    if not isinstance(value.get("revision"), int) or value.get("revision", -1) < 0:
        errors.append("registry revision must be a non-negative integer")
    tasks = value.get("tasks")
    if not isinstance(tasks, list):
        errors.append("registry tasks must be a list")
        tasks = []
    seen: dict[str, set[str]] = {key: set() for key in ("task_id", "implementation_thread_id", "reviewer_thread_id", "automation_id")}
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            errors.append(f"registry task {index} must be an object")
            continue
        for key in seen:
            value_id = str(task.get(key, "")).strip()
            if key == "automation_id" and value_id == "none":
                continue
            if not value_id or value_id == "none":
                errors.append(f"registry task {index} requires {key}")
            elif value_id in seen[key]:
                errors.append(f"duplicate {key}: {value_id}")
            else:
                seen[key].add(value_id)
        try:
            template_version = task.get("naming_template_version", 1)
            if template_version not in SUPPORTED_NAMING_TEMPLATE_VERSIONS:
                raise LCRLError(f"unsupported naming template version: {template_version}")
            expected = build_binding_titles(
                task.get("display_name", ""), task.get("iteration", ""),
                task.get("work_status_label", ""), template_version,
            )
        except LCRLError as exc:
            errors.append(f"registry task {index}: {exc}")
            continue
        titles = task.get("titles", {})
        for role, title in expected.items():
            if titles.get(role) != title:
                errors.append(f"registry task {index} has stale {role} title")
    if errors:
        raise LCRLError("; ".join(errors))


def load_binding_registry(path: str | Path, allow_missing: bool = False) -> dict[str, Any]:
    registry_path = Path(path).expanduser().resolve()
    if not registry_path.exists():
        if allow_missing:
            return empty_binding_registry()
        raise LCRLError(f"binding registry not found: {registry_path}")
    try:
        value = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LCRLError(f"invalid binding registry {registry_path}: {exc}") from exc
    validate_binding_registry(value)
    return value


def _save_binding_registry_locked(
    registry_path: Path,
    value: dict[str, Any],
    expected_revision: int | None = None,
) -> int:
    """Persist a registry while its sidecar lock is already held."""
    if registry_path.exists() and expected_revision is not None:
        current = json.loads(registry_path.read_text(encoding="utf-8"))
        if current.get("revision") != expected_revision:
            raise LCRLError(
                f"registry revision conflict: expected {expected_revision}, found {current.get('revision')}"
            )
    updated = deepcopy(value)
    updated["schema_version"] = BINDING_REGISTRY_VERSION
    updated["revision"] = int(value.get("revision", 0)) + 1
    updated["updated_at"] = utc_now()
    validate_binding_registry(updated)
    payload = json.dumps(updated, ensure_ascii=False, indent=2) + "\n"
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{registry_path.name}.", suffix=".tmp", dir=registry_path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, registry_path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    value.clear()
    value.update(updated)
    return updated["revision"]


def save_binding_registry(path: str | Path, value: dict[str, Any], expected_revision: int | None = None) -> int:
    registry_path = Path(path).expanduser().resolve()
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    with acquire_state_lock(registry_path):
        return _save_binding_registry_locked(registry_path, value, expected_revision)


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def registry() -> dict[str, Any]:
    path = skill_root() / "references" / "controller.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_state(path: str | Path) -> dict[str, Any]:
    state_path = Path(path).expanduser().resolve()
    if not state_path.is_file():
        raise LCRLError(f"state file not found: {state_path}")
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LCRLError(f"invalid state file {state_path}: {exc}") from exc
    apply_state_defaults(state)
    validate_state(state)
    return state


def apply_state_defaults(state: dict[str, Any]) -> None:
    """Add forward-compatible V8 defaults without changing the active review loop."""
    automation = state.setdefault("automation", {})
    automation.setdefault("interval_minutes", 0)
    automation.setdefault("heartbeat_mode", "foreground_only")
    automation.setdefault("title", "none")
    legacy_waiting = state.get("review", {}).get("status") == "review_waiting"
    automation.setdefault("waiting_check_active", legacy_waiting)
    automation.setdefault("waiting_check_automation_id", "none")
    automation.setdefault("waiting_check_claimed_id", "none")
    automation.setdefault(
        "waiting_check_token",
        "wait-legacy-" + fingerprint({
            "cycle": state.get("review", {}).get("cycle_id", "none"),
            "request": state.get("review", {}).get("request_message_id", "none"),
        })[:12] if legacy_waiting else "none",
    )
    policy = state.setdefault("policy", {})
    if policy.get("implementation_role") == "luna_high":
        policy["implementation_role"] = "luna_medium"
    policy.setdefault("reviewer_reasoning_required", "extreme")
    if policy.get("reviewer_reasoning_control") == "bound_chat_browser":
        policy["reviewer_reasoning_control"] = "manual_app_chat"
    policy.setdefault("reviewer_reasoning_control", "manual_app_chat")
    confirmation = state.setdefault("confirmation", {})
    confirmation.setdefault("reviewer_reasoning_mode", "unconfirmed")
    confirmation.setdefault("reviewer_reasoning_confirmed", False)
    confirmation.setdefault("reviewer_reasoning_confirmed_at", "none")
    legacy_reasoning_confirmed = confirmation.get("reviewer_reasoning_confirmed") is True
    confirmation.setdefault("reviewer_reasoning_control_source", "user" if legacy_reasoning_confirmed else "none")
    confirmation.setdefault("reviewer_reasoning_observed_label", "极高" if legacy_reasoning_confirmed else "none")
    confirmation.setdefault(
        "reviewer_reasoning_observed_thread_id",
        confirmation.get("reviewer_thread_id", "none") if legacy_reasoning_confirmed else "none",
    )
    confirmation.setdefault("reviewer_reasoning_native_app_instance_id", "none")
    if confirmation.get("reviewer_reasoning_control_source") == "bound_chat_browser":
        confirmation.update({
            "reviewer_reasoning_mode": "unconfirmed",
            "reviewer_reasoning_confirmed": False,
            "reviewer_reasoning_confirmed_at": "none",
            "reviewer_reasoning_control_source": "none",
            "reviewer_reasoning_observed_label": "none",
            "reviewer_reasoning_observed_thread_id": "none",
            "reviewer_reasoning_native_app_instance_id": "none",
            "reviewer_reasoning_invalidated_reason": "browser_and_app_chat_modes_are_independent",
        })
    runtime = state.setdefault("runtime", {})
    runtime.setdefault("action_lease_id", "none")
    runtime.setdefault("action_lease_acquired_at", "none")
    runtime.setdefault("action_lease_expires_at", "none")
    runtime.setdefault("action_lease_reason", "none")
    runtime.setdefault("browser_submission_reopen_browser_id", "none")
    runtime.setdefault("browser_submission_send_authorized_lease_id", "none")
    runtime.setdefault("browser_submission_send_authorized_revision", 0)
    runtime.setdefault("resume_checkpoint", checkpoint_for_status(
        state.get("review", {}).get("status", "local_work")
    ))
    runtime.setdefault("resume_checkpoint_at", "none")
    review = state.setdefault("review", {})
    review.setdefault("transport", "app_chat_review")
    review.setdefault("cycle_id", "none")
    review.setdefault("request_stage", "none")
    review.setdefault("request_reasoning_mode", "none")
    review.setdefault("request_native_app_instance_id", "none")
    review.setdefault("response_stage", "none")
    review.setdefault("response_valid_for_apply", False)
    review.setdefault("response_quarantined_reason", "none")
    # Alpha states did not distinguish a reviewed stage from the whole goal.
    # Keep their historical single-stage meaning; new runs record this choice.
    review.setdefault("goal_mode", "single_stage")
    review.setdefault("overall_completion_confirmed", False)
    review.setdefault("overall_completion_evidence", "none")
    browser_binding = state.setdefault("browser_binding", {})
    browser_binding.setdefault(
        "status", "unbound" if review.get("transport") == "in_app_browser" else "not_applicable"
    )
    browser_binding.setdefault("browser_id", "none")
    browser_binding.setdefault("provider_tab_id", "none")
    browser_binding.setdefault("provisioned_chat", False)
    browser_binding.setdefault("conversation_id", "none")
    browser_binding.setdefault("conversation_url", "none")
    browser_binding.setdefault("observed_title", "none")
    browser_binding.setdefault("bound_at", "none")
    recovery = state.setdefault("recovery", {})
    recovery.setdefault("browser_consecutive_network_errors", 0)
    recovery.setdefault("browser_consecutive_rate_limits", 0)
    recovery.setdefault("browser_last_observation_at", "none")
    recovery.setdefault("browser_reload_same_tab_required", False)
    state.setdefault("review_history", [])
    state.setdefault("binding", {
        "status": "unbound",
        "registry_path": "none",
        "task_id": "none",
        "display_name": "none",
        "iteration": "none",
        "work_status_label": "none",
        "naming_template_version": NAMING_TEMPLATE_VERSION,
        "expected_work_title": "none",
        "expected_chat_title": "none",
        "expected_automation_title": "none",
    })
    attachment = state.setdefault("attachment", {})
    attachment.setdefault("required", False)
    attachment.setdefault("verification", "not_required")
    attachment.setdefault("expected_names", [])
    attachment.setdefault("observed_names", [])
    attachment.setdefault("verified_at", "none")
    capability_probes = state.setdefault("capability_probes", {})
    capability_probes.setdefault("terra_next_turn", "unverified")
    next_operation = state.setdefault("next_operation", {})
    next_operation.setdefault("status", "none")
    next_operation.setdefault("path", "none")
    next_operation.setdefault("sha256", "none")
    next_operation.setdefault("source_response_message_id", "none")
    next_operation.setdefault("source_stage", "none")
    next_operation.setdefault("next_stage", "none")
    next_operation.setdefault("result_hash", "none")
    next_operation.setdefault("validated_at", "none")
    next_operation.setdefault("applied_at", "none")
    defaults = default_model_policy(policy.get("implementation_role", "luna_medium"))
    model_policy = state.setdefault("model_policy", {})
    legacy_model_policy = model_policy.get("version") in {1, 2, 3, 4}
    if legacy_model_policy:
        executor = model_policy.setdefault("executor", {})
        if executor.get("default") == "luna_high":
            executor["default"] = "luna_medium"
        if executor.get("current") in {"luna_high", "terra"}:
            executor["current"] = "luna_medium"
        model_policy["version"] = MODEL_POLICY_VERSION
    for key in ("version", "automatic_model_switch", "automatic_thread_creation"):
        model_policy.setdefault(key, defaults[key])
    for section in ("executor", "reviewer", "progress", "routing", "pro", "terra"):
        current = model_policy.setdefault(section, {})
        for key, value in defaults[section].items():
            current.setdefault(key, deepcopy(value))
    routing = model_policy["routing"]
    apply_execution_fact_defaults(routing["advice"])
    for high_attempt in routing["high_attempts"]:
        if isinstance(high_attempt, dict):
            apply_execution_fact_defaults(high_attempt)
    for terra_turn in routing["terra_turns"]:
        if isinstance(terra_turn, dict):
            apply_execution_fact_defaults(terra_turn)
    terra = model_policy["terra"]
    apply_execution_fact_defaults(
        terra,
        legacy_authorized=(
            legacy_model_policy
            and terra.get("status") == "approved"
            and terra.get("user_confirmed") is True
        ),
    )
    if (
        legacy_model_policy
        and terra.get("status") == "approved"
        and terra.get("user_confirmed") is True
        and terra.get("execution_status") == "unknown"
    ):
        terra["execution_status"] = "authorized"
    current_stage = review.get("current_stage", "initial")
    if (
        review.get("status") == "review_submit_pending"
        and review.get("cycle_id") in (None, "", "none")
        and review.get("submission_fingerprint") not in (None, "", "none")
    ):
        review["cycle_id"] = "legacy-pending-" + fingerprint({
            "stage": current_stage,
            "submission_fingerprint": review.get("submission_fingerprint"),
        })[:16]
    if review.get("request_message_id") not in (None, "", "none"):
        if review.get("cycle_id") in (None, "", "none"):
            review["cycle_id"] = "legacy-" + fingerprint({
                "stage": current_stage,
                "request_message_id": review.get("request_message_id"),
            })[:16]
        if review.get("request_stage") in (None, "", "none"):
            review["request_stage"] = current_stage
        if review.get("request_reasoning_mode") in (None, "", "none"):
            review["request_reasoning_mode"] = "unconfirmed"
    if review.get("response_message_id") not in (None, "", "none"):
        if review.get("response_stage") in (None, "", "none"):
            review["response_stage"] = current_stage
    if review.get("status") == "result_received" and not review.get("response_valid_for_apply", False):
        review["status"] = "result_quarantined"
        review["response_quarantined_reason"] = "legacy_or_unconfirmed_review_mode"


def save_state(path: str | Path, state: dict[str, Any], expected_revision: int | None = None) -> int:
    """Compare-and-write state under a cross-process lock; return the new revision.

    The lock covers the full critical section: re-read disk revision, check
    expected_revision, validate, fsync temp file, and os.replace. os.replace
    alone is not a CAS; without the lock two processes can both pass a stale
    revision check and both claim waiting-check or reply-consumption rights.
    """
    state_path = Path(path).expanduser().resolve()
    state_path.parent.mkdir(parents=True, exist_ok=True)
    new_state = deepcopy(state)
    current_revision = int(state.get("revision", 0))
    new_state["revision"] = max(current_revision + 1, 1)
    new_state["updated_at"] = utc_now()
    # Validate before taking the lock so policy errors never hold the mutex.
    validate_state(new_state)
    payload = json.dumps(new_state, ensure_ascii=False, indent=2) + "\n"
    with acquire_state_lock(state_path):
        if state_path.exists() and expected_revision is not None:
            try:
                current = json.loads(state_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise LCRLError(f"invalid state file {state_path}: {exc}") from exc
            if current.get("revision") != expected_revision:
                raise StateRevisionConflict(
                    f"state revision conflict: expected {expected_revision}, found {current.get('revision')}"
                )
        descriptor, temp_name = tempfile.mkstemp(
            prefix=f".{state_path.name}.", suffix=".tmp", dir=state_path.parent
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, state_path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
    state.clear()
    state.update(new_state)
    return new_state["revision"]


def new_state(
    automation_id: str,
    implementation_thread_id: str,
    project_path: str,
    reviewer_thread_id: str,
    profile: str = "generic",
    codex_root: str | None = None,
    continuation_mode: str = "foreground",
    review_transport: str = "app_chat_review",
    implementation_role: str = "luna_medium",
    goal_mode: str = "continuous",
) -> dict[str, Any]:
    if continuation_mode not in VALID_COORDINATION_MODES:
        raise LCRLError("continuation_mode must be automatic or foreground")
    if review_transport not in VALID_REVIEW_TRANSPORTS:
        raise LCRLError("review_transport must be app_chat_review or in_app_browser")
    if implementation_role not in VALID_IMPLEMENTATION_ROLES:
        raise LCRLError("implementation_role must be luna_medium or terra_medium")
    if goal_mode not in VALID_GOAL_MODES:
        raise LCRLError("goal_mode must be continuous or single_stage")
    heartbeat_mode = "waiting_only" if continuation_mode == "automatic" else "foreground_only"
    now = utc_now()
    lease_seed = f"{automation_id}|{implementation_thread_id}|{reviewer_thread_id}"
    lease_id = "lease-" + hashlib.sha256(lease_seed.encode()).hexdigest()[:16]
    return {
        "schema_version": SCHEMA_VERSION,
        "revision": 0,
        "created_at": now,
        "updated_at": now,
        "automation": {
            "id": automation_id,
            "implementation_thread_id": implementation_thread_id,
            "project_path": str(Path(project_path).expanduser().resolve()),
            "profile": profile,
            "interval_minutes": 0,
            "heartbeat_mode": heartbeat_mode,
            "title": "none",
            "waiting_check_token": "none",
            "waiting_check_active": False,
            "waiting_check_automation_id": "none",
            "waiting_check_claimed_id": "none",
        },
        "policy": {
            "implementation_role": implementation_role,
            "reviewer_kind": "chatgpt",
            "review_quota_source": "chatgpt",
            "codex_review_forbidden": True,
            "transport_locked": True,
            "reviewer_read_only": True,
            "reviewer_reasoning_required": "extreme",
            "reviewer_reasoning_control": (
                "in_app_browser" if review_transport == "in_app_browser" else "manual_app_chat"
            ),
        },
        "confirmation": {
            "lease_id": lease_id,
            "reviewer_thread_id": reviewer_thread_id,
            "reviewer_context_mode": "existing_chat",
            "confirmed_at": now,
            "valid": True,
            "invalidated_reason": "none",
            "reviewer_reasoning_mode": "unconfirmed",
            "reviewer_reasoning_confirmed": False,
            "reviewer_reasoning_confirmed_at": "none",
            "reviewer_reasoning_control_source": "none",
            "reviewer_reasoning_observed_label": "none",
            "reviewer_reasoning_observed_thread_id": "none",
            "reviewer_reasoning_native_app_instance_id": "none",
        },
        "capabilities": {
            # Runtime access belongs to the implementation task and must be
            # proven by autonomous-preflight; a fresh state never invents it.
            "chat_list": False,
            "chat_read": False,
            "chat_send": False,
            "chat_create": "manual",
            "attachment_send": "manual",
            "filesystem_read": "inline",
        },
        "review": {
            "transport": review_transport,
            "payload_mode": "inline_packet",
            "current_stage": "initial",
            "status": "local_work",
            "cycle_id": "none",
            "request_turn_id": "none",
            "request_message_id": "none",
            "request_persisted_at": "none",
            "request_stage": "none",
            "request_reasoning_mode": "none",
            "request_native_app_instance_id": "none",
            "response_turn_id": "none",
            "response_message_id": "none",
            "response_completed_at": "none",
            "response_complete": False,
            "response_envelope_hash": "none",
            "response_stage": "none",
            "response_valid_for_apply": False,
            "response_quarantined_reason": "none",
            "goal_mode": goal_mode,
            "overall_completion_confirmed": False,
            "overall_completion_evidence": "none",
            "reviewer_execution_status": "idle",
            "waiting_since": "none",
            "last_progress_at": now,
            "submission_fingerprint": "none",
            "artifacts_summary": "none",
            "recovery_action": "none",
        },
        "review_history": [],
        "browser_binding": {
            "status": "unbound" if review_transport == "in_app_browser" else "not_applicable",
            "browser_id": "none",
            "provider_tab_id": "none",
            "provisioned_chat": False,
            "conversation_id": "none",
            "conversation_url": "none",
            "observed_title": "none",
            "bound_at": "none",
        },
        "binding": {
            "status": "unbound",
            "registry_path": "none",
            "task_id": "none",
            "display_name": "none",
            "iteration": "none",
            "work_status_label": "none",
            "naming_template_version": NAMING_TEMPLATE_VERSION,
            "expected_work_title": "none",
            "expected_chat_title": "none",
            "expected_automation_title": "none",
        },
        "attachment": {
            "required": False,
            "verification": "not_required",
            "expected_names": [],
            "observed_names": [],
            "verified_at": "none",
        },
        "capability_probes": {"terra_next_turn": "unverified"},
        "next_operation": {
            "status": "none",
            "path": "none",
            "sha256": "none",
            "source_response_message_id": "none",
            "source_stage": "none",
            "next_stage": "none",
            "result_hash": "none",
            "validated_at": "none",
            "applied_at": "none",
        },
        "model_policy": default_model_policy(implementation_role),
        "recovery": {
            "network_state": "healthy",
            "network_error_count": 0,
            "last_network_error_at": "none",
            "last_network_error_fingerprint": "none",
            "last_runtime_event_at": "none",
            "next_retry_not_before": "none",
            "consecutive_no_progress_checks": 0,
            "reviewer_wake_count": 0,
            "user_notified_stall": False,
            "browser_consecutive_network_errors": 0,
            "browser_consecutive_rate_limits": 0,
            "browser_last_observation_at": "none",
            "browser_reload_same_tab_required": False,
        },
        "alternative": {"sent": False, "scope": "none", "fingerprint": "none"},
        "runtime": {
            "codex_root": str(Path(codex_root).expanduser().resolve()) if codex_root else "auto",
            "session_log": "auto",
            "last_observed_runtime_timestamp": "none",
            "action_lease_id": "none",
            "action_lease_acquired_at": "none",
            "action_lease_expires_at": "none",
            "action_lease_reason": "none",
            "browser_submission_reopen_browser_id": "none",
            "browser_submission_send_authorized_lease_id": "none",
            "browser_submission_send_authorized_revision": 0,
            "resume_checkpoint": "local_work",
            "resume_checkpoint_at": now,
        },
    }


def validate_execution_fact(record: dict[str, Any], label: str, errors: list[str]) -> None:
    status = record.get("execution_status")
    source = record.get("execution_source")
    proof = record.get("execution_proof")
    verified_at = record.get("execution_verified_at")
    verification_type = record.get("execution_verification_type")
    if status not in VALID_EXECUTION_STATUSES:
        errors.append(f"{label}.execution_status is invalid")
        return
    if source not in VALID_EXECUTION_SOURCES:
        errors.append(f"{label}.execution_source is invalid")
    if verification_type not in VALID_EXECUTION_VERIFICATION_TYPES:
        errors.append(f"{label}.execution_verification_type is invalid")
    if status == "verified":
        if (
            source != "manual_confirmed"
            or verification_type != "manual_attested"
            or proof in (None, "", "none")
            or not is_timestamp(verified_at)
        ):
            errors.append(f"{label}.verified execution requires a manual attestation, proof, and timestamp")
    elif (
        source != "none"
        or proof not in (None, "", "none")
        or verified_at not in (None, "", "none")
        or verification_type != "none"
    ):
        errors.append(f"{label} may only contain execution proof after verification")


def validate_state(state: dict[str, Any]) -> None:
    errors: list[str] = []
    if state.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version must be 7")
    if not isinstance(state.get("revision"), int) or state.get("revision", -1) < 0:
        errors.append("revision must be a non-negative integer")
    automation = state.get("automation", {})
    interval_minutes = automation.get("interval_minutes")
    heartbeat_mode = automation.get("heartbeat_mode")
    if heartbeat_mode not in {"foreground_only", "waiting_only", "legacy_fixed"}:
        errors.append("heartbeat_mode must be foreground_only, waiting_only, or legacy_fixed")
    if interval_minutes not in {0, 3}:
        errors.append("heartbeat interval must be 0 for foreground recovery or 3 for legacy state")
    if heartbeat_mode == "waiting_only" and interval_minutes != 0:
        errors.append("wait-bound one-shot mode requires a zero recurring interval")
    if heartbeat_mode == "legacy_fixed" and interval_minutes != 3:
        errors.append("legacy heartbeat mode requires a 3 minute interval")
    review = state.get("review", {})
    review_transport = review.get("transport")
    if review_transport not in VALID_REVIEW_TRANSPORTS:
        errors.append("review transport must be app_chat_review or in_app_browser")
    policy = state.get("policy", {})
    implementation_role = policy.get("implementation_role")
    if implementation_role not in VALID_IMPLEMENTATION_ROLES:
        errors.append("policy.implementation_role must be 'luna_medium' or 'terra_medium'")
    expected_policy = {
        "reviewer_kind": "chatgpt",
        "review_quota_source": "chatgpt",
        "codex_review_forbidden": True,
        "transport_locked": True,
        "reviewer_read_only": True,
        "reviewer_reasoning_required": "extreme",
        "reviewer_reasoning_control": (
            "in_app_browser" if review_transport == "in_app_browser" else "manual_app_chat"
        ),
    }
    for key, expected in expected_policy.items():
        if policy.get(key) != expected:
            errors.append(f"policy.{key} must be {expected!r}")
    confirmation = state.get("confirmation", {})
    browser_binding = state.get("browser_binding", {})
    browser_binding_status = browser_binding.get("status")
    if browser_binding_status not in {"not_applicable", "unbound", "bound"}:
        errors.append("browser_binding.status must be not_applicable, unbound, or bound")
    if "tab_id" in browser_binding:
        errors.append("browser_binding must not persist a run-local tab_id")
    provisioned_chat = browser_binding.get("provisioned_chat")
    if not isinstance(provisioned_chat, bool):
        errors.append("browser_binding.provisioned_chat must be a boolean")
    if review_transport == "app_chat_review" and browser_binding_status != "not_applicable":
        errors.append("App Chat review cannot bind an in-app browser tab")
    if review_transport == "in_app_browser" and browser_binding_status == "not_applicable":
        errors.append("in-app browser review requires a browser binding state")
    if browser_binding_status == "bound":
        for key in (
            "browser_id", "provider_tab_id", "conversation_id", "conversation_url", "bound_at",
        ):
            if browser_binding.get(key) in (None, "", "none"):
                errors.append(f"bound browser tab requires browser_binding.{key}")
        expected_conversation_id = confirmation.get("reviewer_thread_id")
        expected_url = f"https://chatgpt.com/c/{expected_conversation_id}"
        if browser_binding.get("conversation_id") != expected_conversation_id:
            errors.append("browser tab binding must match the bound reviewer Chat")
        if browser_binding.get("conversation_url") != expected_url:
            errors.append("browser tab binding must use the canonical bound conversation URL")
        if not is_timestamp(browser_binding.get("bound_at")):
            errors.append("browser tab binding requires a timestamp")
        if (
            browser_binding.get("provider_tab_id") == "pending_handoff"
            and provisioned_chat is not True
        ):
            errors.append("pending_handoff is only valid for a provisioned Chat")
    if (
        review_transport == "in_app_browser"
        and review.get("status") in (ACTIVE_STATUSES - {"local_work"})
        and browser_binding_status != "bound"
    ):
        errors.append("active in-app browser review requires a persisted browser tab binding")
    if confirmation.get("reviewer_reasoning_confirmed") is True:
        if confirmation.get("reviewer_reasoning_mode") != "extreme":
            errors.append("confirmed reviewer reasoning must be extreme")
        control_source = confirmation.get("reviewer_reasoning_control_source")
        if control_source not in {"user", "main_app", "native_app", "in_app_browser"}:
            errors.append("confirmed reviewer reasoning requires a trusted control source")
        if confirmation.get("reviewer_reasoning_observed_label") != "极高":
            errors.append("confirmed reviewer reasoning requires an observed 极高 label")
        if confirmation.get("reviewer_reasoning_observed_thread_id") != confirmation.get("reviewer_thread_id"):
            errors.append("reviewer reasoning evidence must match the bound App Chat")
        native_instance = confirmation.get("reviewer_reasoning_native_app_instance_id", "none")
        if control_source == "native_app" and native_instance in (None, "", "none"):
            errors.append("native App reasoning confirmation requires an App instance identity")
        if control_source in {"user", "main_app", "in_app_browser"} and native_instance not in (None, "", "none"):
            errors.append("non-native reasoning confirmation cannot claim a native App instance")
        if review_transport == "in_app_browser" and control_source != "in_app_browser":
            errors.append("in-app browser review requires browser reasoning confirmation")
        if review_transport == "in_app_browser" and browser_binding_status != "bound":
            errors.append("in-app browser reasoning confirmation requires a browser tab binding")
        if review_transport == "app_chat_review" and control_source == "in_app_browser":
            errors.append("App Chat review cannot use browser reasoning confirmation")
    status = review.get("status")
    if status not in VALID_STATUSES:
        errors.append(f"invalid review status: {status!r}")
    goal_mode = review.get("goal_mode")
    overall_completion_confirmed = review.get("overall_completion_confirmed")
    overall_completion_evidence = review.get("overall_completion_evidence")
    if goal_mode not in VALID_GOAL_MODES:
        errors.append("review.goal_mode must be continuous or single_stage")
    if not isinstance(overall_completion_confirmed, bool):
        errors.append("review.overall_completion_confirmed must be boolean")
    if overall_completion_confirmed is True and overall_completion_evidence in (None, "", "none"):
        errors.append("confirmed overall completion requires evidence")
    if goal_mode == "continuous" and status == "completed" and overall_completion_confirmed is not True:
        errors.append("continuous goal completion requires explicit overall completion evidence")
    if status in ACTIVE_STATUSES:
        if confirmation.get("valid") is not True:
            errors.append("active workflow requires a valid confirmation lease")
        if confirmation.get("reviewer_thread_id") in (None, "", "none"):
            errors.append("active workflow requires a confirmed App Chat id")
    if review.get("payload_mode") not in VALID_PAYLOAD_MODES:
        errors.append("invalid review payload_mode")
    capabilities = state.get("capabilities", {})
    if capabilities.get("attachment_send") not in VALID_ATTACHMENT_CAPABILITIES:
        errors.append("invalid attachment_send capability")
    if capabilities.get("filesystem_read") not in VALID_FILESYSTEM_CAPABILITIES:
        errors.append("invalid filesystem_read capability")
    attachment = state.get("attachment", {})
    if attachment.get("verification") not in VALID_ATTACHMENT_VERIFICATION:
        errors.append("invalid attachment verification state")
    if not isinstance(attachment.get("expected_names"), list) or not isinstance(attachment.get("observed_names"), list):
        errors.append("attachment names must be lists")
    if review.get("payload_mode") == "app_attachment":
        if attachment.get("required") is not True:
            errors.append("app_attachment requires attachment.required=true")
        if attachment.get("verification") not in {"verified", "manual_confirmed", "unverified"}:
            errors.append("app_attachment requires an explicit attachment verification state")
    binding = state.get("binding", {})
    if binding.get("status") not in {"unbound", "bound"}:
        errors.append("binding.status must be unbound or bound")
    if binding.get("status") == "bound":
        for key in ("registry_path", "task_id", "display_name", "iteration", "expected_work_title", "expected_chat_title", "expected_automation_title"):
            if binding.get(key) in (None, "", "none"):
                errors.append(f"bound workflow requires binding.{key}")
        if binding.get("naming_template_version") not in SUPPORTED_NAMING_TEMPLATE_VERSIONS:
            errors.append("unsupported naming template version")
    if state.get("capability_probes", {}).get("terra_next_turn") not in {"unverified", "supported", "unsupported"}:
        errors.append("invalid terra_next_turn capability probe")
    recovery = state.get("recovery", {})
    if not isinstance(recovery.get("browser_consecutive_network_errors", 0), int) or recovery.get("browser_consecutive_network_errors", 0) < 0:
        errors.append("browser consecutive network error count must be a non-negative integer")
    if not isinstance(recovery.get("browser_consecutive_rate_limits", 0), int) or recovery.get("browser_consecutive_rate_limits", 0) < 0:
        errors.append("browser consecutive rate-limit count must be a non-negative integer")
    if not isinstance(recovery.get("browser_reload_same_tab_required", False), bool):
        errors.append("browser reload requirement must be boolean")
    next_operation = state.get("next_operation", {})
    next_operation_status = next_operation.get("status")
    if next_operation_status not in VALID_NEXT_OPERATION_STATUSES:
        errors.append("invalid next_operation status")
    if next_operation_status in {"validated", "applied"}:
        for field in (
            "path", "sha256", "source_response_message_id", "source_stage",
            "next_stage", "result_hash", "validated_at",
        ):
            if next_operation.get(field) in (None, "", "none"):
                errors.append(f"next_operation.{field} is required when persisted")
        if next_operation_status == "applied" and next_operation.get("applied_at") in (None, "", "none"):
            errors.append("next_operation.applied_at is required after apply")
    model_policy = state.get("model_policy", {})
    if model_policy.get("version") != MODEL_POLICY_VERSION:
        errors.append(f"model_policy.version must be {MODEL_POLICY_VERSION}")
    if model_policy.get("automatic_model_switch") is not False:
        errors.append("automatic model switching must remain disabled")
    if model_policy.get("automatic_thread_creation") is not False:
        errors.append("automatic thread creation must remain disabled")
    executor = model_policy.get("executor", {})
    reviewer = model_policy.get("reviewer", {})
    if (
        implementation_role not in VALID_IMPLEMENTATION_ROLES
        or executor.get("default") != implementation_role
        or executor.get("current") != implementation_role
    ):
        errors.append("invalid model policy executor")
    if reviewer.get("default") != "sol_extreme" or reviewer.get("current") not in {"sol_extreme", "chat_pro"}:
        errors.append("invalid model policy reviewer")
    progress = model_policy.get("progress", {})
    if not isinstance(progress.get("active_minutes_since_pro"), int) or progress.get("active_minutes_since_pro", -1) < 0:
        errors.append("active Pro progress minutes must be a non-negative integer")
    if not isinstance(progress.get("meaningful_steps_since_pro"), int) or progress.get("meaningful_steps_since_pro", -1) < 0:
        errors.append("meaningful Pro progress steps must be a non-negative integer")
    progress_events = progress.get("events")
    if not isinstance(progress_events, list) or len(progress_events) > MAX_PROGRESS_EVENTS:
        errors.append(f"progress events must be a list with at most {MAX_PROGRESS_EVENTS} entries")
        progress_events = []
    event_ids: set[str] = set()
    evidence_fingerprints: set[str] = set()
    for event in progress_events:
        if not isinstance(event, dict) or event.get("event_id") in (None, "", "none"):
            errors.append("every progress event requires an event_id")
            continue
        if event["event_id"] in event_ids:
            errors.append(f"duplicate progress event id: {event['event_id']}")
        event_ids.add(event["event_id"])
        evidence = event.get("evidence_fingerprint")
        if evidence in (None, "", "none"):
            errors.append("every progress event requires an evidence_fingerprint")
        elif evidence in evidence_fingerprints:
            errors.append(f"duplicate progress evidence fingerprint: {evidence}")
        else:
            evidence_fingerprints.add(evidence)
        if not isinstance(event.get("active_minutes"), int) or not 1 <= event.get("active_minutes", 0) <= 120:
            errors.append("progress event active_minutes must be between 1 and 120")
        if not isinstance(event.get("meaningful_step"), bool):
            errors.append("progress event meaningful_step must be boolean")
        if not is_timestamp(event.get("recorded_at")):
            errors.append("progress event recorded_at must be an ISO-8601 timestamp")
    routing = model_policy.get("routing", {})
    if routing.get("medium_minimum_percent") != 80:
        errors.append("normal Luna Medium share must remain at least 80 percent")
    if routing.get("high_maximum_last_10_steps") != HIGH_MAX_LAST_10_STEPS:
        errors.append("Luna High ceiling must remain two turns per ten meaningful steps")
    if routing.get("terra_maximum_last_20_steps") != TERRA_MAX_LAST_20_STEPS:
        errors.append("Terra ceiling must remain one turn per twenty meaningful steps")
    if not isinstance(routing.get("meaningful_step_index"), int) or routing.get("meaningful_step_index", -1) < 0:
        errors.append("model routing meaningful_step_index must be a non-negative integer")
    advice = routing.get("advice", {})
    if advice.get("requested") not in VALID_MODEL_ROUTES or advice.get("effective") not in VALID_MODEL_ROUTES:
        errors.append("invalid model route advice")
    if advice.get("status") not in {"default", "accepted", "rejected", "consumed"}:
        errors.append("invalid model route advice status")
    validate_execution_fact(advice, "model routing advice", errors)
    for collection_name in ("high_attempts", "terra_turns"):
        collection = routing.get(collection_name)
        if not isinstance(collection, list) or len(collection) > MAX_MODEL_ROUTE_EVENTS:
            errors.append(f"model routing {collection_name} must contain at most {MAX_MODEL_ROUTE_EVENTS} entries")
            continue
        identities: set[str] = set()
        id_field = "attempt_id" if collection_name == "high_attempts" else "request_id"
        for item in collection:
            if not isinstance(item, dict) or item.get(id_field) in (None, "", "none"):
                errors.append(f"every {collection_name} item requires {id_field}")
                continue
            if item[id_field] in identities:
                errors.append(f"duplicate {collection_name} identity: {item[id_field]}")
            identities.add(item[id_field])
            if item.get("blocker_id") in (None, "", "none"):
                errors.append(f"every {collection_name} item requires blocker_id")
            if not isinstance(item.get("meaningful_step_index"), int) or item.get("meaningful_step_index", -1) < 0:
                errors.append(f"every {collection_name} item requires a non-negative meaningful_step_index")
            else:
                validate_execution_fact(item, f"{collection_name} item", errors)
    pro = model_policy.get("pro", {})
    if pro.get("threshold_active_minutes") != PRO_THRESHOLD_ACTIVE_MINUTES:
        errors.append(f"Pro threshold must remain {PRO_THRESHOLD_ACTIVE_MINUTES} active minutes")
    if pro.get("minimum_meaningful_steps") != PRO_MINIMUM_MEANINGFUL_STEPS:
        errors.append(f"Pro minimum must remain {PRO_MINIMUM_MEANINGFUL_STEPS} meaningful steps")
    if pro.get("status") not in VALID_PRO_STATUSES:
        errors.append("invalid Pro policy status")
    if not isinstance(pro.get("review_count"), int) or pro.get("review_count", -1) < 0:
        errors.append("Pro review_count must be a non-negative integer")
    if pro.get("last_outcome") not in {"none", "completed", "cancelled"}:
        errors.append("invalid Pro last_outcome")
    if pro.get("status") in {"eligible", "confirmation_required", "in_review"} and not pro_is_eligible(model_policy):
        errors.append("Pro status requires the active-time and meaningful-step thresholds")
    if pro.get("status") in {"confirmation_required", "in_review"} and not is_timestamp(pro.get("requested_at")):
        errors.append("active Pro request requires requested_at")
    if pro.get("status") == "in_review":
        if pro.get("user_confirmed") is not True or pro.get("request_id") in (None, "", "none"):
            errors.append("active Pro review requires explicit confirmation and request identity")
        if reviewer.get("current") != "chat_pro":
            errors.append("active Pro review requires reviewer.current=chat_pro")
        if not is_timestamp(pro.get("started_at")):
            errors.append("active Pro review requires started_at")
    elif reviewer.get("current") != "sol_extreme":
        errors.append("normal review requires reviewer.current=sol_extreme")
    terra = model_policy.get("terra", {})
    validate_execution_fact(terra, "terra", errors)
    if terra.get("status") not in VALID_TERRA_STATUSES:
        errors.append("invalid Terra policy status")
    if not isinstance(terra.get("request_count"), int) or terra.get("request_count", -1) < 0:
        errors.append("Terra request_count must be a non-negative integer")
    if terra.get("last_outcome") not in {"none", "completed", "cancelled", "capability_downgraded"}:
        errors.append("invalid Terra last_outcome")
    if terra.get("status") in {"requested", "approved"}:
        if terra.get("request_id") in (None, "", "none") or terra.get("signal") not in VALID_TERRA_SIGNALS:
            errors.append("active Terra request requires an id and allowed difficulty signal")
        if not is_timestamp(terra.get("requested_at")):
            errors.append("active Terra request requires requested_at")
        for field in ("blocker_id", "high_attempt_id", "evidence_fingerprint", "advice_response_message_id"):
            if terra.get(field) in (None, "", "none"):
                errors.append(f"active Terra request requires {field}")
    if terra.get("status") == "approved":
        if terra.get("user_confirmed") is not True or terra.get("execution_status") not in {"authorized", "verified"}:
            errors.append("approved Terra request requires explicit confirmation and authorization")
        if not is_timestamp(terra.get("approved_at")):
            errors.append("approved Terra execution requires approved_at")
    if terra.get("status") == "approved" and pro.get("status") == "in_review":
        errors.append("Terra execution and Pro milestone review cannot be active together")
    if review.get("payload_mode") == "mcp_readonly" and capabilities.get("filesystem_read") != "mcp_verified":
        errors.append("mcp_readonly requires filesystem_read=mcp_verified")
    if review.get("payload_mode") != "mcp_readonly" and capabilities.get("filesystem_read") == "mcp_verified":
        errors.append("mcp_verified may only be used with mcp_readonly payloads")
    if review.get("request_reasoning_mode") not in VALID_REQUEST_REASONING_MODES:
        errors.append("invalid request_reasoning_mode")
    history = state.get("review_history", [])
    if not isinstance(history, list) or len(history) > 20:
        errors.append("review_history must be a list with at most 20 entries")
    empty = (None, "", "none")
    request_fields = ("request_turn_id", "request_message_id", "request_persisted_at")
    response_fields = ("response_turn_id", "response_message_id", "response_completed_at", "response_envelope_hash")
    if status == "review_submit_pending":
        if review.get("submission_fingerprint") in empty:
            errors.append("review_submit_pending requires a submission fingerprint")
        if review.get("cycle_id") in empty:
            errors.append("review_submit_pending requires a cycle_id")
        if any(review.get(field) not in empty for field in request_fields + response_fields):
            errors.append("review_submit_pending requires a clean request and response identity")
        if review.get("request_stage") not in empty or review.get("response_stage") not in empty:
            errors.append("review_submit_pending requires clean request and response stages")
        if review.get("request_reasoning_mode") != "none":
            errors.append("review_submit_pending requires request_reasoning_mode=none")
        if review.get("request_native_app_instance_id") not in empty:
            errors.append("review_submit_pending requires a clean native App instance identity")
        if review.get("response_complete") is not False or review.get("response_valid_for_apply") is not False:
            errors.append("review_submit_pending cannot contain an actionable response")
    if status == "review_waiting":
        if review.get("submission_fingerprint") in (None, "", "none"):
            errors.append("review_waiting requires a submission fingerprint")
        if review.get("waiting_since") in (None, "", "none"):
            errors.append("review_waiting requires waiting_since")
        if review.get("cycle_id") in empty:
            errors.append("review_waiting requires a cycle_id")
        if any(review.get(field) in empty for field in request_fields):
            errors.append("review_waiting requires persisted request turn/message identity")
        if review.get("request_stage") != review.get("current_stage"):
            errors.append("review_waiting request_stage must match current_stage")
        if review.get("request_reasoning_mode") not in {"extreme", "unconfirmed", "legacy"}:
            errors.append("review_waiting requires a recorded request reasoning mode")
        if confirmation.get("reviewer_reasoning_control_source") == "native_app" and (
            review.get("request_native_app_instance_id")
            != confirmation.get("reviewer_reasoning_native_app_instance_id")
        ):
            errors.append("review_waiting submission must use the App instance that confirmed Extreme")
        if any(review.get(field) not in empty for field in response_fields):
            errors.append("review_waiting cannot contain stale response identity")
        if review.get("response_stage") not in empty or review.get("response_complete") is not False:
            errors.append("review_waiting cannot contain a completed response")
        if review.get("response_valid_for_apply") is not False:
            errors.append("review_waiting response cannot be valid for apply")
    if status == "review_receipt_pending":
        if review.get("submission_fingerprint") in empty or review.get("cycle_id") in empty:
            errors.append("review_receipt_pending requires a cycle and submission fingerprint")
        if review.get("waiting_since") in empty:
            errors.append("review_receipt_pending requires waiting_since")
        if review.get("request_stage") != review.get("current_stage"):
            errors.append("review_receipt_pending request_stage must match current_stage")
        if review.get("request_reasoning_mode") != "extreme":
            errors.append("review_receipt_pending requires confirmed Extreme request mode")
        if any(review.get(field) not in empty for field in request_fields + response_fields):
            errors.append("review_receipt_pending must not invent request or response identity")
        if review.get("response_stage") not in empty or review.get("response_complete") is not False:
            errors.append("review_receipt_pending cannot contain a completed response")
        if review.get("response_valid_for_apply") is not False:
            errors.append("review_receipt_pending response cannot be valid for apply")
    if status in {"result_received", "result_quarantined"}:
        if review.get("cycle_id") in empty or any(review.get(field) in empty for field in request_fields):
            errors.append(f"{status} requires persisted request identity")
        if review.get("request_stage") != review.get("current_stage"):
            errors.append(f"{status} request_stage must match current_stage")
        if review.get("response_complete") is not True:
            errors.append(f"{status} requires response_complete=true")
        if any(review.get(field) in empty for field in response_fields):
            errors.append(f"{status} requires complete response identity")
        if review.get("response_stage") != review.get("current_stage"):
            errors.append(f"{status} response_stage must match current_stage")
    if status == "result_received":
        if review.get("request_reasoning_mode") != "extreme":
            errors.append("result_received requires an Extreme review request")
        if review.get("response_valid_for_apply") is not True:
            errors.append("result_received requires response_valid_for_apply=true")
        if not (
            confirmation.get("reviewer_reasoning_confirmed") is True
            and confirmation.get("reviewer_reasoning_mode") == "extreme"
        ):
            errors.append("result_received requires currently confirmed Extreme mode")
    if status == "result_quarantined":
        if review.get("response_valid_for_apply") is not False:
            errors.append("result_quarantined cannot be valid for apply")
        if review.get("response_quarantined_reason") in empty:
            errors.append("result_quarantined requires a quarantine reason")
    request_message = review.get("request_message_id")
    response_message = review.get("response_message_id")
    if request_message not in (None, "", "none") and request_message == response_message:
        errors.append("request and response message ids must be distinct")
    if state.get("recovery", {}).get("network_state") not in {"healthy", "disconnected", "recovering", "rate_limited"}:
        errors.append("invalid recovery.network_state")
    runtime = state.get("runtime", {})
    lease_id = runtime.get("action_lease_id", "none")
    lease_expiry = runtime.get("action_lease_expires_at", "none")
    if (lease_id == "none") != (lease_expiry == "none"):
        errors.append("action lease id and expiry must be set or cleared together")
    reopen_browser_id = runtime.get("browser_submission_reopen_browser_id", "none")
    if runtime.get("action_lease_reason") == "browser_submission_reopen":
        if reopen_browser_id in (None, "", "none"):
            errors.append("browser submission reopen lease requires a browser identity")
    elif reopen_browser_id not in (None, "", "none"):
        errors.append("browser submission reopen browser identity requires its lease")
    send_authorized_lease_id = runtime.get(
        "browser_submission_send_authorized_lease_id", "none"
    )
    send_authorized_revision = runtime.get(
        "browser_submission_send_authorized_revision", 0
    )
    if send_authorized_lease_id not in (None, "", "none"):
        if (
            runtime.get("action_lease_reason") != "browser_submission_reopen"
            or send_authorized_lease_id != lease_id
        ):
            errors.append("browser submission send authorization requires its reopen lease")
        if not isinstance(send_authorized_revision, int) or send_authorized_revision < 1:
            errors.append("browser submission send authorization requires a state revision")
    elif send_authorized_revision != 0:
        errors.append("browser submission send authorization revision requires its lease")
    waiting_check_active = automation.get("waiting_check_active")
    waiting_check_token = automation.get("waiting_check_token", "none")
    waiting_check_automation_id = automation.get("waiting_check_automation_id", "none")
    waiting_check_claimed_id = automation.get("waiting_check_claimed_id", "none")
    expected_waiting_check_active = (
        status in MONITOR_STATUSES and heartbeat_mode == "waiting_only"
    )
    if waiting_check_active is not expected_waiting_check_active:
        errors.append("waiting check activity must match waiting-only continuation mode and review status")
    if (waiting_check_token == "none") == bool(waiting_check_active):
        errors.append("waiting check token must exist exactly while its check is active")
    if not waiting_check_active and (
        waiting_check_automation_id != "none" or waiting_check_claimed_id != "none"
    ):
        errors.append("inactive waiting check cannot retain an automation or claim id")
    if waiting_check_claimed_id != "none" and waiting_check_claimed_id != waiting_check_automation_id:
        errors.append("waiting check claim must match the current automation id")
    if errors:
        raise LCRLError("; ".join(errors))


def read_toml(path: Path) -> dict[str, Any]:
    if tomllib is None:
        raise LCRLError("Python 3.11 or newer is required for TOML migration")
    with path.open("rb") as handle:
        return tomllib.load(handle)


def extract_value(text: str, keys: Iterable[str], default: str = "none") -> str:
    for key in keys:
        patterns = (
            rf'(?im)^\s*{re.escape(key)}\s*[:=]\s*["\']?([^\r\n"\']+)',
            rf'(?i)"{re.escape(key)}"\s*:\s*"([^"]+)"',
        )
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
    return default


def discover_session_log(codex_root: Path, implementation_thread_id: str) -> Path | None:
    sessions = codex_root / "sessions"
    if not sessions.exists():
        return None
    matches = list(sessions.rglob(f"*{implementation_thread_id}*.jsonl"))
    if not matches:
        return None
    return max(matches, key=lambda item: item.stat().st_mtime)


def migrate_v6(args: argparse.Namespace) -> dict[str, Any]:
    automation_path = Path(args.automation_toml).expanduser().resolve()
    config = read_toml(automation_path)
    prompt = str(config.get("prompt", ""))
    automation_id = str(config.get("id") or args.automation_id or automation_path.parent.name)
    thread_id = str(
        config.get("thread_id")
        or config.get("target_thread_id")
        or extract_value(prompt, ("implementation_thread_id", "codex_thread_id", "thread_id"))
    )
    reviewer_id = extract_value(prompt, ("reviewer_thread_id", "review_chat_id", "chatgpt_thread_id"))
    project_path = extract_value(prompt, ("project_path", "workspace", "cwd"), str(Path.cwd()))
    if thread_id == "none" or reviewer_id == "none":
        raise LCRLError("could not extract implementation and reviewer App Chat ids from V6 automation")
    codex_root = Path(args.codex_root).expanduser().resolve() if args.codex_root else Path.home() / ".codex"
    state = new_state(
        automation_id,
        thread_id,
        project_path,
        reviewer_id,
        args.profile,
        str(codex_root),
        goal_mode="single_stage",
    )
    review = state["review"]
    legacy_status = extract_value(prompt, ("current_status", "review_status", "status"), "local_work")
    status_map = {
        "review_waiting": "review_waiting",
        "waiting": "review_waiting",
        "result_received": "result_received",
        "local_work": "local_work",
        "completed": "completed",
        "external_blocked": "external_blocked",
    }
    review["status"] = status_map.get(legacy_status, "local_work")
    review["current_stage"] = extract_value(prompt, ("current_stage", "stage", "iteration"), "legacy")
    review["submission_fingerprint"] = extract_value(prompt, ("submission_fingerprint", "review_fingerprint"))
    review["waiting_since"] = extract_value(prompt, ("waiting_since",))
    legacy_turn = extract_value(prompt, ("last_complete_reviewer_turn_id", "last_reviewer_turn_id"))
    if legacy_turn != "none":
        review["legacy_last_complete_reviewer_turn_id"] = legacy_turn
    payload_mode = extract_value(prompt, ("review_payload_mode", "payload_mode"), "inline_packet")
    if payload_mode in VALID_PAYLOAD_MODES:
        review["payload_mode"] = payload_mode
    if review["payload_mode"] == "mcp_readonly":
        state["capabilities"]["filesystem_read"] = "mcp_verified"
    if review["status"] == "review_waiting":
        if review["submission_fingerprint"] == "none":
            review["submission_fingerprint"] = fingerprint({"stage": review["current_stage"], "source": "v6"})
        if review["waiting_since"] == "none":
            review["waiting_since"] = state["created_at"]
        # V6 did not reliably persist distinct request turn/message identifiers.
        # Do not invent them and do not let a legacy wait state become actionable.
        review["status"] = "external_blocked"
        review["recovery_action"] = "reconcile_legacy_review_request_identity"
    if review["status"] == "result_received":
        # V6 did not distinguish request and response message ids, so do not guess.
        review["status"] = "external_blocked"
        review["submission_fingerprint"] = review["submission_fingerprint"] if review["submission_fingerprint"] != "none" else fingerprint({"stage": review["current_stage"], "source": "v6"})
        review["recovery_action"] = "verify_legacy_result_identity"
    session_log = discover_session_log(codex_root, thread_id)
    state["runtime"]["session_log"] = str(session_log) if session_log else "auto"
    save_state(args.state_output, state)
    return {"ok": True, "state": str(Path(args.state_output).resolve()), "revision": state["revision"]}


def render_heartbeat(state_path: str | Path, validate_only: bool = False) -> str:
    path = Path(state_path).expanduser().resolve()
    state = load_state(path)
    reg = registry()
    template_path = skill_root() / reg["heartbeat_template"]
    template = template_path.read_text(encoding="utf-8")
    replacements = {
        "controller_version": str(reg["controller_version"]),
        "skill_revision": str(reg["skill_revision"]),
        "automation_id": str(state["automation"]["id"]),
        "state_file": str(path),
        "cli_path": str(Path(__file__).resolve()),
    }
    result = template
    for key, value in replacements.items():
        result = result.replace("{{" + key + "}}", value)
    unresolved = re.findall(r"{{[^}]+}}", result)
    if unresolved:
        raise LCRLError(f"unresolved heartbeat placeholders: {unresolved}")
    size = len(result.encode("utf-8"))
    if size > int(reg.get("max_heartbeat_bytes", MAX_HEARTBEAT_BYTES)):
        raise LCRLError(f"heartbeat is {size} bytes, over the {MAX_HEARTBEAT_BYTES}-byte limit")
    if validate_only:
        return canonical_json({"ok": True, "bytes": size})
    return result


def runtime_log_path(state: dict[str, Any]) -> Path | None:
    configured = state["runtime"].get("session_log", "auto")
    if configured != "auto":
        path = Path(configured)
        return path if path.is_file() else None
    root_value = state["runtime"].get("codex_root", "auto")
    root = Path(root_value) if root_value != "auto" else Path.home() / ".codex"
    return discover_session_log(root, state["automation"]["implementation_thread_id"])


def iter_runtime_completions(path: Path) -> Iterable[dict[str, str]]:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("type") != "event_msg":
                continue
            payload = record.get("payload", {})
            terminal_type = payload.get("type")
            if terminal_type not in {"task_complete", "turn_aborted"}:
                continue
            error = payload.get("error")
            if terminal_type == "turn_aborted":
                error = f"turn_aborted:{payload.get('reason', 'unknown')}"
            if isinstance(error, dict):
                error = canonical_json(error)
            yield {
                "timestamp": str(record.get("timestamp", "none")),
                "error": str(error or ""),
                "success": str(not bool(error)).lower(),
                "terminal_type": str(terminal_type),
            }


def new_runtime_completions(path: Path, last_timestamp: str) -> list[dict[str, str]]:
    records = list(iter_runtime_completions(path))
    if last_timestamp == "none":
        return records[-1:] if records else []
    for index, record in enumerate(records):
        if record["timestamp"] == last_timestamp:
            return records[index + 1 :]
    return records[-1:] if records else []


def normalized_network_error(message: str) -> str:
    normalized = re.sub(r"https?://\S+", "<url>", message.lower())
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized[:1000]


def record_network_observation(state: dict[str, Any], event: dict[str, str]) -> bool:
    timestamp = event.get("timestamp", "none")
    if timestamp == state["runtime"].get("last_observed_runtime_timestamp"):
        return False
    state["runtime"]["last_observed_runtime_timestamp"] = timestamp
    state["recovery"]["last_runtime_event_at"] = timestamp
    acquired = parse_time(state["runtime"].get("action_lease_acquired_at"))
    terminal_at = parse_time(timestamp)
    if (
        state["runtime"].get("action_lease_id", "none") != "none"
        and acquired is not None
        and terminal_at is not None
        and terminal_at >= acquired
    ):
        clear_action_lease(state)
    error = event.get("error", "")
    if error and NETWORK_ERROR_PATTERN.search(error):
        normalized = normalized_network_error(error)
        state["recovery"]["network_state"] = "disconnected"
        state["recovery"]["network_error_count"] = int(state["recovery"].get("network_error_count", 0)) + 1
        state["recovery"]["last_network_error_at"] = timestamp
        state["recovery"]["last_network_error_fingerprint"] = fingerprint(normalized)
        delay_minutes = min(15, 3 * max(1, state["recovery"]["network_error_count"]))
        event_time = parse_time(timestamp) or datetime.now(timezone.utc)
        state["recovery"]["next_retry_not_before"] = (
            event_time + timedelta(minutes=delay_minutes)
        ).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        return True
    if event.get("success") == "true" and state["recovery"].get("network_state") != "healthy":
        state["recovery"]["network_state"] = "healthy"
        state["recovery"]["next_retry_not_before"] = "none"
    return True


def choose_action(state: dict[str, Any]) -> str:
    status = state["review"]["status"]
    if status == "external_blocked":
        return "external_blocked"
    if status == "completed":
        return status
    if state["recovery"]["network_state"] == "disconnected":
        retry = parse_time(state["recovery"].get("next_retry_not_before"))
        if retry and datetime.now(timezone.utc) < retry:
            return "network_backoff"
        state["recovery"]["network_state"] = "recovering"
    action = {
        "local_work": "local_work",
        "review_submit_pending": "review_submit",
        "review_receipt_pending": "review_receipt_reconcile",
        "review_waiting": "review_poll",
        "result_received": "apply_result",
        "result_quarantined": "quarantined_result",
    }[status]
    confirmation = state["confirmation"]
    if action == "review_submit" and state["review"].get("payload_mode") == "app_attachment":
        if state.get("attachment", {}).get("verification") not in {"verified", "manual_confirmed"}:
            return "attachment_verification_blocked"
    if action == "review_submit" and not (
        confirmation.get("reviewer_reasoning_confirmed") is True
        and confirmation.get("reviewer_reasoning_mode") == "extreme"
    ):
        return "review_mode_blocked"
    if action == "apply_result" and not (
        state["review"].get("response_valid_for_apply") is True
        and state["review"].get("request_reasoning_mode") == "extreme"
    ):
        return "quarantined_result"
    if action == "apply_result":
        operation = state.get("next_operation", {})
        if not (
            operation.get("status") == "validated"
            and operation.get("source_response_message_id") == state["review"].get("response_message_id")
        ):
            return "operation_persistence_blocked"
    return action


def active_action_lease(state: dict[str, Any]) -> bool:
    runtime = state["runtime"]
    if runtime.get("action_lease_id", "none") == "none":
        return False
    expiry = parse_time(runtime.get("action_lease_expires_at"))
    return bool(expiry and datetime.now(timezone.utc) < expiry)


def clear_action_lease(state: dict[str, Any]) -> None:
    state["runtime"].update({
        "action_lease_id": "none",
        "action_lease_acquired_at": "none",
        "action_lease_expires_at": "none",
        "action_lease_reason": "none",
        "browser_submission_reopen_browser_id": "none",
        "browser_submission_send_authorized_lease_id": "none",
        "browser_submission_send_authorized_revision": 0,
    })


def checkpoint_for_status(status: str) -> str:
    """Return the last controller boundary that can safely be resumed."""
    return {
        "local_work": "local_work",
        "review_submit_pending": "before_review_submission",
        "review_receipt_pending": "submission_needs_confirmation",
        "review_waiting": "review_submission_confirmed",
        "result_received": "reply_consumed",
        "result_quarantined": "needs_user_decision",
        "external_blocked": "needs_user_decision",
        "completed": "completed",
    }.get(status, "unknown")


def record_resume_checkpoint(state: dict[str, Any], checkpoint: str | None = None) -> None:
    state["runtime"].update({
        "resume_checkpoint": checkpoint or checkpoint_for_status(state["review"]["status"]),
        "resume_checkpoint_at": utc_now(),
    })


def claim_action_lease(state: dict[str, Any], reason: str, minutes: int = 4) -> str:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    lease_id = "run-" + secrets.token_hex(8)
    state["runtime"].update({
        "action_lease_id": lease_id,
        "action_lease_acquired_at": now.isoformat().replace("+00:00", "Z"),
        "action_lease_expires_at": (now + timedelta(minutes=minutes)).isoformat().replace("+00:00", "Z"),
        "action_lease_reason": reason,
    })
    return lease_id


def user_status_label(status: str) -> str:
    if status == "review_receipt_pending":
        return USER_STATUS_LABELS["review_waiting"]
    return USER_STATUS_LABELS.get(status, "需要你决定")


def user_status_exit(status: str) -> dict[str, Any]:
    """The only plain-language status surface intended for people."""
    label = user_status_label(status)
    message, next_choice = USER_STATUS_MESSAGES[label]
    return {
        "user_status": label,
        "user_message": message,
        "user_next_choice": next_choice,
        "user_choice_required": status in {"result_quarantined", "external_blocked"},
        "choice_output_allowed": False,
        "turn_completion_allowed": status in {
            "review_receipt_pending", "review_waiting", "external_blocked", "completed",
        },
    }


def waiting_check_binding_pending(state: dict[str, Any]) -> bool:
    automation = state["automation"]
    return bool(
        state["review"]["status"] in MONITOR_STATUSES
        and automation.get("heartbeat_mode") == "waiting_only"
        and automation.get("waiting_check_active") is True
        and automation.get("waiting_check_token", "none") != "none"
        and automation.get("waiting_check_automation_id", "none") == "none"
    )


def add_platform_wait_contract(result: dict[str, Any]) -> dict[str, Any]:
    """Make the platform schedule shape explicit wherever one wait is requested."""
    output = dict(result)
    if output.get("waiting_check_action") in {"schedule_once", "keep_once", "update_once"}:
        output.update({
            "platform_wait_rule": "single_rdate",
            "platform_rrule_prefix": "RDATE:",
            "recurring_platform_rule_allowed": False,
        })
    return output


def add_user_status_exit(result: dict[str, Any]) -> dict[str, Any]:
    """Attach the stable five-state view without removing internal controller data."""
    output = add_platform_wait_contract(result)
    if "status" in output:
        output.update(user_status_exit(str(output["status"])))
        if (
            str(output["status"]) in MONITOR_STATUSES
            and output.get("waiting_check_action") == "schedule_once"
            and output.get("waiting_check_automation_id", "none") == "none"
        ):
            output.update({
                "user_status": "正在开发",
                "user_message": "本轮已提交，正在建立唯一等待检查。",
                "user_next_choice": "无需操作。",
                "user_choice_required": False,
                "continuation_required": True,
                "next_action": "create_and_bind_waiting_check",
                "turn_completion_allowed": False,
            })
    return output


def progress_query_command(args: argparse.Namespace) -> dict[str, Any]:
    """Read the saved workflow position without observing Chat or mutating state."""
    state = load_state(Path(args.state).expanduser().resolve())
    status = state["review"]["status"]
    operation = state.get("next_operation", {})
    completed_step, next_step = {
        "local_work": (
            "上一项修改已完成，正在准备或处理当前工作。" if operation.get("status") == "applied" else "正在处理当前工作。",
            "Codex 继续当前项目工作。",
        ),
        "review_submit_pending": (
            "本轮开发已完成，正在准备提交。",
            "SuperLuna 自动核验并提交到固定 Chat。",
        ),
        "review_receipt_pending": ("评审内容已准备好。", "请核对原 Chat 后确认本轮提交。"),
        "review_waiting": ("本轮已交给 Chat。", "无需操作；原任务会在回复到达后继续。"),
        "result_received": ("已读到 Chat 的意见。", "Codex 正在按意见修改并验证。"),
        "result_quarantined": ("已收到需要人工判断的意见。", "请说明要继续、调整方向，还是停止。"),
        "external_blocked": ("自动可做部分已经完成。", "请说明要继续、调整方向，还是停止。"),
        "completed": ("用户总体目标已经完成。", "无需操作。"),
    }[status]
    output = {
        "ok": True,
        "completed_step": completed_step,
        "next_step": next_step,
        **user_status_exit(status),
    }
    if waiting_check_binding_pending(state):
        output.update({
            "user_status": "正在开发",
            "user_message": "本轮已提交，正在建立唯一等待检查。",
            "user_next_choice": "无需操作。",
            "completed_step": "本轮已交给 Chat。",
            "next_step": "SuperLuna 创建并绑定唯一单次等待检查。",
            "user_choice_required": False,
            "continuation_required": True,
            "next_action": "create_and_bind_waiting_check",
            "turn_completion_allowed": False,
        })
    return output


def _load_app_thread_snapshot(path_value: str | Path) -> dict[str, Any]:
    path = Path(path_value).expanduser().resolve()
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LCRLError(f"invalid App thread snapshot {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise LCRLError("App thread snapshot must be an object")
    return value


def _atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def _main_app_chat_messages(snapshot: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, str]]]:
    """Extract stable user-message identities from one read_thread snapshot."""
    thread = snapshot.get("thread")
    if not isinstance(thread, dict):
        raise LCRLError("main App Chat snapshot requires a thread object")
    thread_id = title_component(str(thread.get("id", "")), "App Chat stable ID", 180)
    if thread.get("kind") != "chatgpt":
        raise LCRLError("main App submission snapshot must target a regular App Chat")
    turns = snapshot.get("turns")
    if not isinstance(turns, list):
        raise LCRLError("main App Chat snapshot turns must be a list")
    messages: list[dict[str, str]] = []
    seen: dict[str, tuple[str, str]] = {}
    for turn in turns:
        if not isinstance(turn, dict):
            raise LCRLError("main App Chat snapshot contains an invalid turn")
        turn_id = title_component(str(turn.get("id", "")), "App Chat turn ID", 180)
        items = turn.get("items", [])
        if not isinstance(items, list):
            raise LCRLError("main App Chat snapshot turn items must be a list")
        for item in items:
            if not isinstance(item, dict) or item.get("type") != "userMessage":
                continue
            message_id = title_component(
                str(item.get("id", "")), "App Chat request message ID", 180
            )
            content = item.get("content", [])
            if not isinstance(content, list):
                raise LCRLError("main App Chat request content must be a list")
            text_value = "".join(
                str(block.get("text", ""))
                for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            )
            identity = (turn_id, text_value)
            if message_id in seen and seen[message_id] != identity:
                raise LCRLError(f"App Chat request message ID {message_id} has conflicting content")
            seen[message_id] = identity
    for message_id, (turn_id, text_value) in seen.items():
        normalized_text = _normalize_main_app_text(text_value)
        messages.append({
            "turn_id": turn_id,
            "message_id": message_id,
            "text": text_value,
            "normalized_text": normalized_text,
            "text_sha256": hashlib.sha256(normalized_text.encode("utf-8")).hexdigest(),
        })
    return {"id": thread_id, "title": str(thread.get("title", ""))}, messages


def _read_utf8_text(path_value: str | Path, label: str) -> str:
    path = Path(path_value).expanduser().resolve()
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise LCRLError(f"cannot read {label} {path}: {exc}") from exc


def _normalize_main_app_text(value: str) -> str:
    """Match the main App composer, which does not preserve terminal line breaks."""
    return value.rstrip("\r\n")


def prepare_main_app_submission_command(args: argparse.Namespace) -> dict[str, Any]:
    """Persist the pre-send baseline required to reconcile an asynchronous main-App send."""
    state_path = Path(args.state).expanduser().resolve()
    state = load_state(state_path)
    review = state["review"]
    if review.get("status") != "review_submit_pending":
        raise LCRLError("main App submission baseline requires review_submit_pending")
    confirmation = state["confirmation"]
    if confirmation.get("reviewer_reasoning_control_source") != "main_app":
        raise LCRLError("main App submission baseline requires main_app reasoning confirmation")
    snapshot = _load_app_thread_snapshot(args.snapshot)
    thread, messages = _main_app_chat_messages(snapshot)
    reviewer_thread_id = confirmation.get("reviewer_thread_id")
    if thread["id"] != reviewer_thread_id:
        raise LCRLError("main App submission baseline targets a different Chat")
    payload = _read_utf8_text(args.text_file, "main App review text")
    normalized_payload = _normalize_main_app_text(payload)
    timeout_seconds = int(args.timeout_seconds)
    if timeout_seconds < 1 or timeout_seconds > 120:
        raise LCRLError("main App submission reconcile timeout must be between 1 and 120 seconds")
    created = parse_time(getattr(args, "at", None) or utc_now())
    if created is None:
        raise LCRLError("main App submission context requires a timestamp")
    context = {
        "schema_version": 1,
        "transport": "main_app_thread_api",
        "reviewer_thread_id": reviewer_thread_id,
        "cycle_id": review.get("cycle_id"),
        "submission_fingerprint": review.get("submission_fingerprint"),
        "stage": review.get("current_stage"),
        "payload_sha256": hashlib.sha256(normalized_payload.encode("utf-8")).hexdigest(),
        "payload_normalization": "terminal_newlines_v1",
        "baseline_message_ids": sorted(message["message_id"] for message in messages),
        "created_at": created.isoformat().replace("+00:00", "Z"),
        "expires_at": (created + timedelta(seconds=timeout_seconds)).isoformat().replace("+00:00", "Z"),
    }
    context_path = Path(args.context_file).expanduser().resolve()
    _atomic_write_json(context_path, context)
    return {
        "ok": True,
        "action": "main_app_submission_prepared",
        "reviewer_thread_id": reviewer_thread_id,
        "payload_sha256": context["payload_sha256"],
        "baseline_message_count": len(context["baseline_message_ids"]),
        "context_file": str(context_path),
        "expires_at": context["expires_at"],
    }


def reconcile_main_app_submission_command(args: argparse.Namespace) -> dict[str, Any]:
    """Confirm only one exact request that became visible after the saved baseline."""
    state_path = Path(args.state).expanduser().resolve()
    state = load_state(state_path)
    review = state["review"]
    recovering_external_block = review.get("status") == "external_blocked"
    if recovering_external_block and not getattr(args, "user_authorized_recovery", False):
        raise LCRLError("late main App receipt recovery requires explicit user authorization")
    if review.get("status") not in {
        "review_submit_pending", "review_receipt_pending", "external_blocked"
    }:
        raise LCRLError("main App submission reconciliation requires review_submit_pending")
    source = getattr(args, "source", None) or "foreground"
    if source not in {"foreground", "waiting_check"}:
        raise LCRLError("main App submission reconciliation source is invalid")
    context = _load_app_thread_snapshot(args.context_file)
    if context.get("schema_version") != 1 or context.get("transport") != "main_app_thread_api":
        raise LCRLError("main App submission reconcile context is invalid")
    confirmation = state["confirmation"]
    if confirmation.get("reviewer_reasoning_control_source") != "main_app":
        raise LCRLError("main App submission reconciliation requires main_app confirmation")
    expected_thread_id = confirmation.get("reviewer_thread_id")
    if context.get("reviewer_thread_id") != expected_thread_id:
        raise LCRLError("main App submission reconcile context targets a different Chat")
    for context_field, review_field in (
        ("cycle_id", "cycle_id"),
        ("submission_fingerprint", "submission_fingerprint"),
        ("stage", "current_stage"),
    ):
        if context.get(context_field) != review.get(review_field):
            raise LCRLError(f"main App submission reconcile context has a stale {context_field}")
    baseline = context.get("baseline_message_ids")
    if (
        not isinstance(baseline, list)
        or len(baseline) > 10_000
        or len(set(baseline)) != len(baseline)
        or any(not isinstance(value, str) or not value for value in baseline)
    ):
        raise LCRLError("main App submission reconcile baseline is invalid")
    payload = _read_utf8_text(args.text_file, "main App review text")
    normalized_payload = _normalize_main_app_text(payload)
    payload_sha256 = hashlib.sha256(normalized_payload.encode("utf-8")).hexdigest()
    legacy_raw_payload_sha256 = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    if context.get("payload_sha256") not in {payload_sha256, legacy_raw_payload_sha256}:
        raise LCRLError("main App submission reconcile context targets different review text")
    observed_at = parse_time(getattr(args, "at", None) or utc_now())
    expires_at = parse_time(context.get("expires_at"))
    if observed_at is None or expires_at is None:
        raise LCRLError("main App submission reconcile timestamps are invalid")
    window_expired = observed_at > expires_at
    snapshot = _load_app_thread_snapshot(args.snapshot)
    thread, messages = _main_app_chat_messages(snapshot)
    if thread["id"] != expected_thread_id:
        raise LCRLError("main App submission snapshot targets a different Chat")
    baseline_ids = set(baseline)
    matches = [
        message for message in messages
        if message["message_id"] not in baseline_ids
        and message["text_sha256"] == payload_sha256
        and message["normalized_text"] == normalized_payload
    ]
    if len(matches) > 1:
        raise LCRLError("multiple matching main App submission receipts were found")
    if not matches:
        if recovering_external_block:
            return {
                "ok": True,
                "action": "submission_receipt_window_expired",
                "reviewer_thread_id": expected_thread_id,
                "payload_sha256": payload_sha256,
                "expires_at": context["expires_at"],
                "resend_allowed": False,
                **user_status_exit("external_blocked"),
            }
        if review.get("status") == "review_submit_pending":
            pending = transition(argparse.Namespace(
                state=str(state_path), status="review_receipt_pending", stage=None,
                payload_mode=None, fingerprint=None,
                waiting_since=getattr(args, "at", None) or utc_now(),
                request_turn_id=None, request_message_id=None,
                request_persisted_at=None, request_stage=None,
                request_reasoning_mode=None, request_native_app_instance_id=None,
                response_turn_id=None, response_message_id=None,
                response_completed_at=None, response_complete=None,
                response_envelope_hash=None, response_stage=None,
                artifacts_summary=None,
                recovery_action="main_app_receipt_waiting",
                attachment_send=None, filesystem_read=None,
                quarantine_unconfirmed=False, recovery_override=False,
                deleted_automation_id=None,
            ))
        else:
            automation = state["automation"]
            pending = {
                "status": "review_receipt_pending",
                "waiting_check_action": (
                    "schedule_once"
                    if automation.get("waiting_check_automation_id", "none") == "none"
                    else "keep_once"
                ),
                "waiting_check_token": automation.get("waiting_check_token", "none"),
                "waiting_check_automation_id": automation.get(
                    "waiting_check_automation_id", "none"
                ),
                "waiting_check_previous_automation_id": "none",
            }
        return add_user_status_exit({
            "ok": True,
            "action": "submission_receipt_not_visible_yet",
            "status": "review_receipt_pending",
            "reviewer_thread_id": expected_thread_id,
            "payload_sha256": payload_sha256,
            "expires_at": context["expires_at"],
            "active_poll_window_expired": window_expired,
            "resend_allowed": False,
            "waiting_check_action": pending["waiting_check_action"],
            "waiting_check_token": pending["waiting_check_token"],
            "waiting_check_automation_id": pending["waiting_check_automation_id"],
            "waiting_check_previous_automation_id": pending[
                "waiting_check_previous_automation_id"
            ],
        })
    match = matches[0]
    if recovering_external_block:
        transition_result = transition(argparse.Namespace(
            state=str(state_path), status="review_waiting", stage=None,
            payload_mode=None, fingerprint=None,
            waiting_since=getattr(args, "at", None) or utc_now(),
            request_turn_id=match["turn_id"], request_message_id=match["message_id"],
            request_persisted_at=getattr(args, "at", None) or utc_now(),
            request_stage=review.get("current_stage"), request_reasoning_mode="extreme",
            request_native_app_instance_id="none",
            response_turn_id=None, response_message_id=None,
            response_completed_at=None, response_complete=None,
            response_envelope_hash=None, response_stage=None,
            artifacts_summary=None, recovery_action="late_main_app_receipt_confirmed",
            attachment_send=None, filesystem_read=None,
            quarantine_unconfirmed=False, recovery_override=True,
        ))
        confirmed = add_user_status_exit({
            "ok": True, "action": "submission_confirmed", "confirmed": True,
            "status": transition_result["status"],
            "request_message_id": match["message_id"], "attachment_count": 0,
            "waiting_check_action": transition_result["waiting_check_action"],
            "waiting_check_token": transition_result["waiting_check_token"],
            "waiting_check_automation_id": transition_result["waiting_check_automation_id"],
        })
    else:
        confirmed = confirm_review_submission_command(argparse.Namespace(
            state=str(state_path), reviewer_thread_id=expected_thread_id,
            request_turn_id=match["turn_id"], request_message_id=match["message_id"],
            native_app_instance_id=None, attachment_name=None,
            submitted_at=getattr(args, "at", None) or utc_now(),
            deleted_automation_id=getattr(args, "deleted_automation_id", None),
        ))
    confirmed.update({
        "request_turn_id": match["turn_id"],
        "request_message_id": match["message_id"],
        "payload_sha256": payload_sha256,
        "reconciled": True,
        "recovered_from_external_block": recovering_external_block,
    })
    return confirmed


def _ordinary_app_chats(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    chats: dict[str, dict[str, Any]] = {}
    for collection_name in ("pinnedThreads", "threads"):
        collection = snapshot.get(collection_name, [])
        if not isinstance(collection, list):
            raise LCRLError(f"App thread snapshot {collection_name} must be a list")
        for item in collection:
            if not isinstance(item, dict) or item.get("kind") != "chatgpt":
                continue
            stable_id = title_component(str(item.get("id", "")), "App Chat stable ID", 180)
            title = title_component(str(item.get("title", "")), "App Chat title", 180)
            candidate = {
                "stable_id": stable_id,
                "title": title,
                "updated_at": item.get("updatedAt"),
            }
            existing = chats.get(stable_id)
            if existing and existing["title"] != title:
                raise LCRLError(f"App Chat stable ID {stable_id} has conflicting titles")
            chats[stable_id] = candidate
    return chats


def discover_reviewer_chat_command(args: argparse.Namespace) -> dict[str, Any]:
    """Find a newly created ordinary App Chat without mutating workflow state."""
    before = _ordinary_app_chats(_load_app_thread_snapshot(args.before_snapshot))
    after = _ordinary_app_chats(_load_app_thread_snapshot(args.after_snapshot))
    candidates = [after[key] for key in sorted(after.keys() - before.keys())]
    expected_title = str(getattr(args, "expected_title", "") or "").strip()
    matching = [item for item in candidates if item["title"] == expected_title] if expected_title else candidates

    if not candidates:
        return {
            "ok": True,
            "action": "needs_user_decision",
            "reason": "no_new_app_chat",
            "candidates": [],
            "requires_user_confirmation": True,
            "binding_created": False,
            "state_created": False,
            "user_status": "需要你决定",
            "user_message": "没有发现新建的普通 App Chat。",
            "user_next_choice": "请新建一个普通 Chat，然后重新检查。",
        }
    if expected_title and not matching:
        return {
            "ok": True,
            "action": "needs_user_decision",
            "reason": "expected_title_not_found",
            "candidates": candidates,
            "requires_user_confirmation": True,
            "binding_created": False,
            "state_created": False,
            "user_status": "需要你决定",
            "user_message": "发现了新 Chat，但没有一个与用户确认的标题一致。",
            "user_next_choice": "请选择正确的普通 Chat。",
        }
    if len(matching) != 1:
        return {
            "ok": True,
            "action": "needs_user_decision",
            "reason": "multiple_new_app_chats",
            "candidates": matching,
            "requires_user_confirmation": True,
            "binding_created": False,
            "state_created": False,
            "user_status": "需要你决定",
            "user_message": "同时发现多个可能的新普通 Chat，无法安全自动选择。",
            "user_next_choice": "请从候选中选择一个 Chat。",
        }

    return {
        "ok": True,
        "action": "confirm_reviewer_candidate",
        "candidate": matching[0],
        "additional_new_chat_count": len(candidates) - 1,
        "requires_user_confirmation": True,
        "binding_created": False,
        "state_created": False,
        "user_status": "需要你决定",
        "user_message": f"已找到新普通 Chat：{matching[0]['title']}。",
        "user_next_choice": "请确认这是本项目的固定评审 Chat。",
    }


def autonomous_preflight_command(args: argparse.Namespace) -> dict[str, Any]:
    """Verify that the implementation task can own the selected Chat review loop."""
    review_transport = getattr(args, "transport", None) or "app_chat_review"
    if review_transport not in VALID_REVIEW_TRANSPORTS:
        raise LCRLError("review transport must be app_chat_review or in_app_browser")
    binding_key = "browser_chat_binding" if review_transport == "in_app_browser" else "app_chat_binding"
    read_key = "browser_chat_read" if review_transport == "in_app_browser" else "app_chat_read"
    send_key = "browser_chat_send" if review_transport == "in_app_browser" else "app_chat_send"
    implementation_thread_id = title_component(
        args.implementation_thread_id, "implementation_thread_id", 180
    )
    implementation_role = getattr(args, "implementation_role", "luna_medium")
    if implementation_role not in VALID_IMPLEMENTATION_ROLES:
        raise LCRLError("implementation_role must be luna_medium or terra_medium")
    reviewer_thread_id = str(args.reviewer_thread_id or "none").strip()
    if reviewer_thread_id and reviewer_thread_id != "none":
        reviewer_thread_id = title_component(reviewer_thread_id, "reviewer_thread_id", 180)
        if reviewer_thread_id == implementation_thread_id:
            raise LCRLError("implementation task and reviewer Chat must have different stable IDs")

    missing: list[str] = []
    if reviewer_thread_id in {"", "none"}:
        missing.append(binding_key)
    if args.chat_read != "available":
        missing.append(read_key)
    if args.chat_send != "available":
        missing.append(send_key)
    if args.review_mode == "unconfirmed":
        missing.append("review_mode_confirmation")
    if args.mode == "automatic" and args.one_shot_automation != "available":
        missing.append("waiting_check_automation")

    if missing:
        if binding_key in missing:
            message = "还没有为这个项目选择固定的评审 Chat。"
            next_choice = "请先在内置浏览器中打开或选择本项目专用 Chat。"
        elif read_key in missing or send_key in missing:
            message = "当前主执行任务还不能完整读取和发送固定评审 Chat。"
            next_choice = "请先恢复内置浏览器 Chat 通道；在此之前不会启动自动循环。"
        elif "review_mode_confirmation" in missing:
            message = "还没有确认本轮 Chat 评审模式。"
            next_choice = "请在 App Chat 中确认使用 Pro 或极高。"
        else:
            message = "当前环境不能安全创建只在等待期间运行的一次检查。"
            next_choice = "请选择前台继续，或先补齐等待检查能力。"
        return {
            "ok": True,
            "action": "needs_user_decision",
            "ready": False,
            "dispatch_allowed": False,
            "monitor_task_allowed": False,
            "mode": args.mode,
            "implementation_role": implementation_role,
            "transport": review_transport,
            "chat_owner": "implementation_task",
            "coordinator_role": "exception_only",
            "missing": missing,
            "user_status": "需要你决定",
            "user_message": message,
            "user_next_choice": next_choice,
        }

    return {
        "ok": True,
        "action": "ready_automatic" if args.mode == "automatic" else "ready_foreground",
        "ready": True,
        "dispatch_allowed": True,
        "monitor_task_allowed": True,
        "mode": args.mode,
        "transport": review_transport,
        "chat_owner": "implementation_task",
        "submission_owner": "implementation_task",
        "reply_reader": "implementation_task",
        "continuation_owner": "implementation_task",
        "coordinator_role": "exception_only",
        "implementation_thread_id": implementation_thread_id,
        "implementation_role": implementation_role,
        "reviewer_thread_id": reviewer_thread_id,
        "review_mode": args.review_mode,
        "waiting_check_supported": args.one_shot_automation == "available",
        "user_status": "正在开发",
        "user_message": "启动前条件已经确认，可以开始执行。",
        "user_next_choice": "无需操作。",
    }


def startup_diagnostics_command(args: argparse.Namespace) -> dict[str, Any]:
    """Diagnose startup from caller-provided facts without touching runtime state.

    This is deliberately separate from autonomous-preflight: it is the gate
    before a new implementation task initializes SuperLuna.  It performs no
    browser, Chat, state, or automation operation and reports only the first
    blocking fact in a stable order.
    """
    implementation_thread_id = str(args.implementation_thread_id or "").strip()
    reviewer_thread_id = str(args.reviewer_thread_id or "").strip()
    facts = {
        "browser": args.browser,
        "chat_login": args.chat_login,
        "chat_selection": args.chat_selection,
        "chat_read": args.chat_read,
        "chat_send": args.chat_send,
        "one_shot_wait": args.one_shot_wait,
        "implementation_thread_id": implementation_thread_id,
        "reviewer_thread_id": reviewer_thread_id,
    }
    checks = (
        (
            args.browser != "initialized",
            "browser_not_initialized",
            "当前实施任务的内置浏览器尚未初始化。",
            "请先初始化当前实施任务自己的内置浏览器，再重新运行启动自检。",
        ),
        (
            args.chat_login != "logged_in",
            "chat_not_logged_in",
            "固定 Chat 页面尚未确认登录。",
            "请在当前实施任务的内置浏览器登录 ChatGPT，并重新运行启动自检。",
        ),
        (
            args.chat_selection != "unique",
            "chat_not_unique",
            "当前没有唯一可用的 reviewer Chat。",
            "请只选择一个固定的 ChatGPT reviewer Chat，再重新运行启动自检。",
        ),
        (
            args.chat_read != "available",
            "chat_read_unavailable",
            "当前不具备读取 reviewer Chat 的能力。",
            "请恢复当前实施任务的 Chat 读取能力，再重新运行启动自检。",
        ),
        (
            args.chat_send != "available",
            "chat_send_unavailable",
            "当前不具备向 reviewer Chat 发送的能力。",
            "请恢复当前实施任务的 Chat 发送能力，再重新运行启动自检。",
        ),
        (
            args.one_shot_wait != "available",
            "one_shot_wait_unavailable",
            "当前不具备单次等待任务能力。",
            "请提供一个可绑定且不重复执行的单次等待任务能力，再重新运行启动自检。",
        ),
        (
            bool(implementation_thread_id)
            and bool(reviewer_thread_id)
            and implementation_thread_id == reviewer_thread_id,
            "identity_conflict",
            "实施任务 identity 与 reviewer Chat identity 相同，角色发生冲突。",
            "请为实施任务和 reviewer Chat 提供两个不同的稳定 identity，再重新运行启动自检。",
        ),
    )
    for blocked, code, reason, next_step in checks:
        if blocked:
            return {
                "ok": False,
                "action": "startup_blocked",
                "ready": False,
                "reason_code": code,
                "reason": reason,
                "user_status": "需要你决定",
                "user_message": reason,
                "user_next_choice": next_step,
                "facts": facts,
            }

    return {
        "ok": True,
        "action": "startup_ready",
        "ready": True,
        "reason": "可以开始",
        "user_status": "正在开发",
        "user_message": "可以开始",
        "user_next_choice": "无需操作。",
        "facts": facts,
    }


def coordination_preflight_command(args: argparse.Namespace) -> dict[str, Any]:
    """Compatibility alias for callers that also coordinate a read-only monitor."""
    return autonomous_preflight_command(args)


def resume_command(args: argparse.Namespace) -> dict[str, Any]:
    """Resume only from the last durable controller boundary in the same task."""
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    checkpoint = state["runtime"].get("resume_checkpoint", "unknown")
    if checkpoint == "unknown":
        result = {
            "ok": True,
            "action": "needs_user_decision",
            "status": state["review"]["status"],
            "recovered_from": "unknown",
        }
        result.update(user_status_exit("external_blocked"))
        result["user_message"] = "无法确认上次已经做到哪里。"
        result["user_next_choice"] = "请选择：重新核对后继续，或停止并说明新的处理方式。"
        return result
    if state["runtime"].get("action_lease_id", "none") != "none":
        revision = state["revision"]
        clear_action_lease(state)
        save_state(path, state, expected_revision=revision)
    result = tick(path, source="foreground")
    result["recovered_from"] = checkpoint
    return result


def tick(state_path: str | Path, source: str = "foreground") -> dict[str, Any]:
    path = Path(state_path).expanduser().resolve()
    state = load_state(path)
    if source not in {"foreground", "heartbeat"}:
        raise LCRLError("tick source must be foreground or heartbeat")
    if source == "heartbeat":
        return add_user_status_exit({
            "ok": True,
            "action": "monitor_retired",
            "automation_id": state["automation"]["id"],
            "stage": state["review"]["current_stage"],
            "status": state["review"]["status"],
            "network": state["recovery"]["network_state"],
            "revision": state["revision"],
            "reviewer_thread_id": state["confirmation"]["reviewer_thread_id"],
            "payload_mode": state["review"]["payload_mode"],
            "lease_id": "none",
            "lease_expires_at": "none",
            "operation_path": state.get("next_operation", {}).get("path", "none"),
            "operation_sha256": state.get("next_operation", {}).get("sha256", "none"),
            "next_stage": state.get("next_operation", {}).get("next_stage", "none"),
            "source": source,
        })
    original_revision = state["revision"]
    log_path = runtime_log_path(state)
    changed = False
    if log_path:
        observations = new_runtime_completions(
            log_path, state["runtime"].get("last_observed_runtime_timestamp", "none")
        )
        for observation in observations:
            changed = record_network_observation(state, observation) or changed
    if active_action_lease(state):
        action = "concurrent_backoff"
        lease_id = state["runtime"]["action_lease_id"]
    else:
        if state["runtime"].get("action_lease_id", "none") != "none":
            clear_action_lease(state)
            changed = True
        action = choose_action(state)
        one_shot_actions = {
            "external_blocked": ("external_blocked_notify", "external_blocked_wait"),
            "review_mode_blocked": ("review_mode_blocked_notify", "review_mode_blocked_wait"),
            "attachment_verification_blocked": ("attachment_verification_blocked_notify", "attachment_verification_blocked_wait"),
            "quarantined_result": ("quarantined_result_notify", "quarantined_result_wait"),
            "operation_persistence_blocked": ("operation_persistence_blocked_notify", "operation_persistence_blocked_wait"),
        }
        if action in one_shot_actions:
            first, later = one_shot_actions[action]
            if state["recovery"].get("user_notified_stall") is True:
                action = later
            else:
                state["recovery"]["user_notified_stall"] = True
                action = first
                changed = True
        elif state["recovery"].get("user_notified_stall") is True:
            state["recovery"]["user_notified_stall"] = False
            changed = True
        lease_id = "none"
        if action not in {
            "network_backoff", "concurrent_backoff", "review_mode_blocked_notify",
            "review_mode_blocked_wait", "external_blocked_notify", "external_blocked_wait",
            "attachment_verification_blocked_notify", "attachment_verification_blocked_wait",
            "quarantined_result_notify", "quarantined_result_wait", "completed",
            "operation_persistence_blocked_notify", "operation_persistence_blocked_wait",
        }:
            lease_id = claim_action_lease(state, action)
            changed = True
    if state["recovery"].get("network_state") == "recovering":
        changed = True
    if changed:
        save_state(path, state, expected_revision=original_revision)
    return add_user_status_exit({
        "ok": True,
        "action": action,
        "automation_id": state["automation"]["id"],
        "stage": state["review"]["current_stage"],
        "status": state["review"]["status"],
        "network": state["recovery"]["network_state"],
        "revision": state["revision"],
        "reviewer_thread_id": state["confirmation"]["reviewer_thread_id"],
        "payload_mode": state["review"]["payload_mode"],
        "lease_id": lease_id,
        "lease_expires_at": state["runtime"].get("action_lease_expires_at", "none"),
        "operation_path": state.get("next_operation", {}).get("path", "none"),
        "operation_sha256": state.get("next_operation", {}).get("sha256", "none"),
        "next_stage": state.get("next_operation", {}).get("next_stage", "none"),
        "source": source,
    })


def _waiting_check_preconditions(state: dict[str, Any], token: str, automation_id: str) -> str | None:
    """Return waiting_check_expired/busy when this check must not claim, else None."""
    automation = state["automation"]
    if (automation.get("heartbeat_mode") != "waiting_only"
            or state["review"]["status"] not in MONITOR_STATUSES
            or automation.get("waiting_check_active") is not True
            or automation.get("waiting_check_token") != token
            or automation.get("waiting_check_automation_id", "none") != automation_id):
        return "waiting_check_expired"
    if active_action_lease(state):
        return "waiting_check_busy"
    if automation.get("waiting_check_claimed_id", "none") != "none":
        return "waiting_check_expired"
    return None


def _waiting_check_blocked_result(state: dict[str, Any], action: str) -> dict[str, Any]:
    """Describe a blocked one-shot without consuming it or authorizing a Chat read."""
    result: dict[str, Any] = {"ok": True, "action": action}
    if action == "waiting_check_busy":
        result.update({
            "waiting_check_action": "update_once",
            "waiting_check_token": state["automation"].get("waiting_check_token", "none"),
            "waiting_check_automation_id": state["automation"].get(
                "waiting_check_automation_id", "none"
            ),
            "retry_not_before": state["runtime"].get("action_lease_expires_at", "none"),
        })
    return add_platform_wait_contract(result)


def waiting_check_command(args: argparse.Namespace) -> dict[str, Any]:
    """A queued wait-only check; stale checks are deliberately silent no-ops.

    Concurrent processes compete on the same state revision. Exactly one may
    claim review_poll; losers reload and return busy or expired without Chat
    reads, project writes, or user-status noise.
    """
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    blocked = _waiting_check_preconditions(state, args.token, args.automation_id)
    if blocked is not None:
        return _waiting_check_blocked_result(state, blocked)
    revision = state["revision"]
    status = state["review"]["status"]
    state["automation"]["waiting_check_claimed_id"] = args.automation_id
    lease_id = claim_action_lease(state, "waiting_review_poll", minutes=2)
    try:
        save_state(path, state, expected_revision=revision)
    except (StateRevisionConflict, StateLockTimeout):
        # Another process claimed first or wrote state; re-evaluate without mutating.
        latest = load_state(path)
        resolved = _waiting_check_preconditions(latest, args.token, args.automation_id)
        if resolved is None:
            # Unrelated concurrent write left the wait claimable; refuse rather
            # than race again so callers never see a user-facing revision error.
            resolved = "waiting_check_busy"
        return _waiting_check_blocked_result(latest, resolved)
    return add_user_status_exit({
        "ok": True,
        "action": "receipt_reconcile" if status == "review_receipt_pending" else "review_poll",
        "status": status,
        "lease_id": lease_id,
        "schedule_next_if_no_reply": True,
    })


def authorize_waiting_chat_read_command(args: argparse.Namespace) -> dict[str, Any]:
    """Recheck a claimed one-shot immediately before its single Chat read."""
    state = load_state(Path(args.state).expanduser().resolve())
    automation = state["automation"]
    runtime = state["runtime"]
    authorized = (
        state["review"]["status"] in MONITOR_STATUSES
        and automation.get("waiting_check_active") is True
        and automation.get("waiting_check_token") == args.token
        and automation.get("waiting_check_automation_id", "none") == args.automation_id
        and automation.get("waiting_check_claimed_id", "none") == args.automation_id
        and runtime.get("action_lease_id", "none") == args.lease_id
        and runtime.get("action_lease_reason", "none") == "waiting_review_poll"
        and active_action_lease(state)
    )
    if not authorized:
        return {"ok": True, "action": "waiting_check_expired", "chat_read_allowed": False}
    browser_transport = state["review"].get("transport") == "in_app_browser"
    reload_required = (
        browser_transport
        and state["recovery"].get("browser_reload_same_tab_required") is True
    )
    result = {
        "ok": True,
        "action": (
            "browser_refresh_authorized" if reload_required
            else "browser_read_authorized" if browser_transport
            else "chat_read_authorized"
        ),
        "chat_read_allowed": True,
        "reload_same_tab_once": reload_required,
        "review_transport": state["review"].get("transport", "app_chat_review"),
        "status": state["review"]["status"],
        "reviewer_thread_id": state["confirmation"]["reviewer_thread_id"],
    }
    if browser_transport:
        result["browser_binding"] = deepcopy(state["browser_binding"])
        provisioned_pending_handoff = (
            state["browser_binding"].get("provisioned_chat") is True
            and state["browser_binding"].get("provider_tab_id") == "pending_handoff"
        )
        canonical_url_only_binding = (
            state["browser_binding"].get("provisioned_chat") is False
            and state["browser_binding"].get("provider_tab_id") == "canonical_url_only"
        )
        url_identity_fallback = provisioned_pending_handoff or canonical_url_only_binding
        result["canonical_url_only_binding"] = canonical_url_only_binding
        result["provisioned_url_fallback_allowed"] = url_identity_fallback
        result["provisioned_url_reopen_allowed"] = url_identity_fallback
        result["canonical_url_reopen_allowed"] = _bound_browser_chat_can_reopen(
            state
        )
    return result


def _bound_browser_chat_can_reopen(state: dict[str, Any]) -> bool:
    """Whether one exact canonical URL may recover the already-bound Chat.

    This does not prove that the tab is absent.  The caller must first find no
    exact URL in either current browser listing and must reverify the page and
    request/payload identity after the occurrence-authorized open.
    """
    binding = state.get("browser_binding", {})
    reviewer_thread_id = state.get("confirmation", {}).get("reviewer_thread_id")
    provider_tab_id = binding.get("provider_tab_id")
    return bool(
        state.get("review", {}).get("transport") == "in_app_browser"
        and binding.get("status") == "bound"
        and provider_tab_id not in (None, "", "none")
        and reviewer_thread_id not in (None, "", "none")
        and binding.get("conversation_id") == reviewer_thread_id
        and binding.get("conversation_url")
        == f"https://chatgpt.com/c/{reviewer_thread_id}"
    )


def authorize_browser_submission_reopen_command(args: argparse.Namespace) -> dict[str, Any]:
    """Lease one exact-URL reopen for a later submission to a provisioned Chat.

    This is deliberately narrower than general tab recovery.  It exists only for
    a Chat that this same run provisioned and still identifies as
    ``pending_handoff`` after the platform discarded its ephemeral tab.  The
    caller must verify the canonical conversation and visible Extreme label
    before sending, then prove this lease to ``confirm-review-submission``.
    """
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    review = state["review"]
    binding = state["browser_binding"]
    confirmation = state["confirmation"]
    automation = state["automation"]
    runtime = state["runtime"]
    fingerprint_arg = str(getattr(args, "fingerprint", "") or "").strip()
    browser_id = str(getattr(args, "browser_id", "") or "").strip()
    browser_id_valid = (
        browser_id not in {"", "none"}
        and not any(character in browser_id for character in "\r\n\t")
        and len(browser_id) <= 240
    )
    empty = (None, "", "none")
    authorized = (
        review.get("transport") == "in_app_browser"
        and review.get("status") == "review_submit_pending"
        and review.get("submission_fingerprint") not in empty
        and fingerprint_arg == review.get("submission_fingerprint")
        and all(review.get(field) in empty for field in (
            "request_turn_id", "request_message_id", "request_persisted_at",
            "response_turn_id", "response_message_id",
        ))
        and confirmation.get("reviewer_reasoning_confirmed") is True
        and confirmation.get("reviewer_reasoning_mode") == "extreme"
        and confirmation.get("reviewer_reasoning_control_source") == "in_app_browser"
        and confirmation.get("reviewer_reasoning_observed_thread_id")
        == confirmation.get("reviewer_thread_id")
        and _bound_browser_chat_can_reopen(state)
        and binding.get("conversation_id") == confirmation.get("reviewer_thread_id")
        and binding.get("conversation_url")
        == f"https://chatgpt.com/c/{confirmation.get('reviewer_thread_id')}"
        and automation.get("waiting_check_active") is False
        and browser_id_valid
    )
    if not authorized:
        return {
            "ok": True,
            "action": "browser_submission_reopen_forbidden",
            "open_canonical_url_once": False,
            "lease_id": "none",
        }
    if active_action_lease(state):
        return {
            "ok": True,
            "action": "browser_submission_reopen_busy",
            "open_canonical_url_once": False,
            "lease_id": "none",
        }
    revision = state["revision"]
    lease_id = claim_action_lease(state, "browser_submission_reopen", minutes=10)
    state["runtime"]["browser_submission_reopen_browser_id"] = browser_id
    save_state(path, state, expected_revision=revision)
    return {
        "ok": True,
        "action": "browser_submission_reopen_authorized",
        "open_canonical_url_once": True,
        "send_allowed_after_verification": False,
        "next_action": "open_canonical_url_once_then_authorize_send",
        "lease_id": lease_id,
        "submission_fingerprint": review["submission_fingerprint"],
        "reviewer_thread_id": confirmation["reviewer_thread_id"],
        "authorized_browser_id": browser_id,
        "browser_rebind_required": browser_id != binding.get("browser_id"),
        "browser_binding": deepcopy(binding),
        "revision": state["revision"],
    }


def authorize_browser_submission_send_command(args: argparse.Namespace) -> dict[str, Any]:
    """Recheck the reopen lease immediately before the one visible send."""
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    revision = state["revision"]
    review = state["review"]
    runtime = state["runtime"]
    lease_id = str(getattr(args, "lease_id", "") or "").strip()
    browser_id = str(getattr(args, "browser_id", "") or "").strip()
    fingerprint = str(getattr(args, "fingerprint", "") or "").strip()
    expiry = parse_time(runtime.get("action_lease_expires_at"))
    enough_time_to_send = bool(
        expiry and datetime.now(timezone.utc) + timedelta(seconds=60) <= expiry
    )
    authorized = bool(
        review.get("status") == "review_submit_pending"
        and review.get("transport") == "in_app_browser"
        and review.get("submission_fingerprint") == fingerprint
        and runtime.get("action_lease_reason") == "browser_submission_reopen"
        and runtime.get("action_lease_id") == lease_id
        and runtime.get("browser_submission_reopen_browser_id") == browser_id
        and active_action_lease(state)
        and enough_time_to_send
        and _bound_browser_chat_can_reopen(state)
        and all(review.get(field) in (None, "", "none") for field in (
            "request_turn_id", "request_message_id", "request_persisted_at",
            "response_turn_id", "response_message_id",
        ))
    )
    if not authorized:
        return {
            "ok": True,
            "action": "browser_submission_send_forbidden",
            "send_allowed": False,
            "lease_id": "none",
        }
    runtime["browser_submission_send_authorized_lease_id"] = lease_id
    runtime["browser_submission_send_authorized_revision"] = revision + 1
    save_state(path, state, expected_revision=revision)
    return {
        "ok": True,
        "action": "browser_submission_send_authorized",
        "send_allowed": True,
        "send_once": True,
        "lease_id": lease_id,
        "authorized_browser_id": browser_id,
        "submission_fingerprint": fingerprint,
        "lease_expires_at": runtime["action_lease_expires_at"],
        "revision": state["revision"],
    }


def authorize_browser_startup_reopen_command(args: argparse.Namespace) -> dict[str, Any]:
    """Authorize one exact-URL open in a newly started implementation task.

    A coordinator may provision the sole reviewer Chat before handing the run to
    its implementation task.  Browser bindings are task-local, so the durable
    ``pending_handoff`` identity cannot by itself make that Chat visible in the
    new task.  This read-only gate authorizes opening only the already-bound
    canonical URL before any local work or formal submission.
    """
    state = load_state(Path(args.state).expanduser().resolve())
    review = state["review"]
    binding = state["browser_binding"]
    confirmation = state["confirmation"]
    automation = state["automation"]
    browser_id = str(getattr(args, "browser_id", "") or "").strip()
    browser_id_valid = (
        browser_id not in {"", "none"}
        and not any(character in browser_id for character in "\r\n\t")
        and len(browser_id) <= 240
    )
    empty = (None, "", "none")
    authorized = (
        review.get("transport") == "in_app_browser"
        and review.get("status") == "local_work"
        and all(review.get(field) in empty for field in (
            "request_turn_id", "request_message_id", "request_persisted_at",
            "response_turn_id", "response_message_id",
        ))
        and binding.get("status") == "bound"
        and binding.get("provisioned_chat") is True
        and binding.get("provider_tab_id") == "pending_handoff"
        and binding.get("conversation_id") == confirmation.get("reviewer_thread_id")
        and binding.get("conversation_url")
        == f"https://chatgpt.com/c/{confirmation.get('reviewer_thread_id')}"
        and automation.get("waiting_check_active") is False
        and not active_action_lease(state)
        and browser_id_valid
    )
    if not authorized:
        return {
            "ok": True,
            "action": "browser_startup_reopen_forbidden",
            "open_canonical_url_once": False,
        }
    return {
        "ok": True,
        "action": "browser_startup_reopen_authorized",
        "open_canonical_url_once": True,
        "send_allowed": False,
        "conversation_url": binding["conversation_url"],
        "reviewer_thread_id": confirmation["reviewer_thread_id"],
        "authorized_browser_id": browser_id,
        "browser_rebind_required": browser_id != binding.get("browser_id"),
        "expected_revision": state["revision"],
    }


def confirm_browser_startup_rebind_command(args: argparse.Namespace) -> dict[str, Any]:
    """Commit a verified task-local browser binding after startup auto-open."""
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    expected_revision = int(args.expected_revision)
    if state["revision"] != expected_revision:
        raise StateRevisionConflict(
            f"expected revision {expected_revision}, found {state['revision']}"
        )
    review = state["review"]
    binding = state["browser_binding"]
    confirmation = state["confirmation"]
    empty = (None, "", "none")
    if not (
        review.get("transport") == "in_app_browser"
        and review.get("status") == "local_work"
        and all(review.get(field) in empty for field in (
            "request_turn_id", "request_message_id", "request_persisted_at",
            "response_turn_id", "response_message_id",
        ))
        and binding.get("status") == "bound"
        and binding.get("provisioned_chat") is True
        and binding.get("provider_tab_id") == "pending_handoff"
        and binding.get("conversation_id") == confirmation.get("reviewer_thread_id")
        and not active_action_lease(state)
    ):
        raise LCRLError("browser startup rebind requires a pristine provisioned handoff")

    browser_id = str(getattr(args, "browser_id", "") or "").strip()
    provider_tab_id = str(getattr(args, "provider_tab_id", "") or "").strip()
    observed_url = str(getattr(args, "url", "") or "").strip()
    observed_title = str(getattr(args, "observed_title", "") or "none").strip() or "none"
    if browser_id in {"", "none"} or provider_tab_id in {"", "none"}:
        raise LCRLError("browser startup rebind requires browser and provider identities")
    if any(character in browser_id + provider_tab_id for character in "\r\n\t"):
        raise LCRLError("browser startup identities must be single-line values")
    if len(browser_id) > 240 or len(provider_tab_id) > 240:
        raise LCRLError("browser startup identities are too long")
    expected_url = f"https://chatgpt.com/c/{confirmation.get('reviewer_thread_id')}"
    parsed = urlsplit(observed_url)
    if (
        observed_url != expected_url
        or binding.get("conversation_url") != expected_url
        or parsed.scheme != "https"
        or parsed.netloc != "chatgpt.com"
        or parsed.query
        or parsed.fragment
    ):
        raise LCRLError("browser startup rebind URL must match the reviewer Chat exactly")

    binding.update({
        "browser_id": browser_id,
        "provider_tab_id": provider_tab_id,
        "observed_title": observed_title[:240],
        "bound_at": getattr(args, "at", None) or utc_now(),
    })
    save_state(path, state, expected_revision=expected_revision)
    return {
        "ok": True,
        "action": "browser_startup_rebound",
        "continuation_required": True,
        "next_action": "continue_local_work",
        "turn_completion_allowed": False,
        "browser_binding": deepcopy(state["browser_binding"]),
        "revision": state["revision"],
    }


def bind_browser_tab_command(args: argparse.Namespace) -> dict[str, Any]:
    """Persist stable browser/provider identity, never a run-local Tab.id handle."""
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    revision = state["revision"]
    if state["review"].get("transport") != "in_app_browser":
        raise LCRLError("browser tab binding requires the in-app browser transport")

    browser_id = str(getattr(args, "browser_id", "") or "").strip()
    provider_tab_id = str(getattr(args, "provider_tab_id", "") or "").strip()
    provisioned_chat = bool(getattr(args, "provisioned_chat", False))
    canonical_url_only = bool(getattr(args, "canonical_url_only", False))
    observed_url = str(getattr(args, "url", "") or "").strip()
    observed_title = str(getattr(args, "observed_title", "") or "none").strip() or "none"
    if browser_id in {"", "none"} or provider_tab_id in {"", "none"}:
        raise LCRLError("browser and provider tab identities are required")
    if provider_tab_id == "pending_handoff" and not provisioned_chat:
        raise LCRLError("pending_handoff is only valid for a provisioned Chat")
    if provider_tab_id == "canonical_url_only" and not canonical_url_only:
        raise LCRLError("canonical URL-only identity requires explicit binding authorization")
    if canonical_url_only and provider_tab_id != "canonical_url_only":
        raise LCRLError("canonical URL-only authorization requires its fixed identity marker")
    if canonical_url_only and provisioned_chat:
        raise LCRLError("canonical URL-only binding is for an existing Chat")
    if any(character in browser_id + provider_tab_id for character in "\r\n\t"):
        raise LCRLError("browser and provider tab identities must be single-line values")
    if len(browser_id) > 240 or len(provider_tab_id) > 240:
        raise LCRLError("browser and provider tab identities are too long")

    reviewer_thread_id = state["confirmation"]["reviewer_thread_id"]
    expected_url = f"https://chatgpt.com/c/{reviewer_thread_id}"
    parsed = urlsplit(observed_url)
    if (
        observed_url != expected_url
        or parsed.scheme != "https"
        or parsed.netloc != "chatgpt.com"
        or parsed.query
        or parsed.fragment
    ):
        raise LCRLError("browser tab URL must match the bound reviewer Chat exactly")

    candidate = {
        "status": "bound",
        "browser_id": browser_id,
        "provider_tab_id": provider_tab_id,
        "provisioned_chat": provisioned_chat,
        "conversation_id": reviewer_thread_id,
        "conversation_url": expected_url,
        "observed_title": observed_title[:240],
        "bound_at": getattr(args, "at", None) or utc_now(),
    }
    current = state["browser_binding"]
    if current.get("status") == "bound":
        stable_keys = (
            "browser_id", "provider_tab_id", "provisioned_chat", "conversation_id",
            "conversation_url",
        )
        if any(current.get(key) != candidate[key] for key in stable_keys):
            raise LCRLError("the persisted browser tab binding cannot change during this run")
        return {
            "ok": True,
            "action": "browser_tab_already_bound",
            "browser_binding": deepcopy(current),
            "revision": revision,
        }

    if state["review"].get("status") != "local_work":
        raise LCRLError("browser tab binding must be completed before formal review starts")

    state["browser_binding"] = candidate
    save_state(path, state, expected_revision=revision)
    return {
        "ok": True,
        "action": "browser_tab_bound",
        "browser_binding": deepcopy(state["browser_binding"]),
        "revision": state["revision"],
    }


def promote_browser_tab_binding_command(args: argparse.Namespace) -> dict[str, Any]:
    """Replace a provisioned Chat's handoff placeholder with provider identity.

    This mutation is allowed only inside the first still-valid waiting read
    lease.  All other binding fields remain fixed, so the promotion cannot be
    used to switch browser instances, conversations, or tabs.
    """
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    if state["review"].get("transport") != "in_app_browser":
        raise LCRLError("browser tab promotion requires the in-app browser transport")

    binding = state["browser_binding"]
    browser_id = str(getattr(args, "browser_id", "") or "").strip()
    provider_tab_id = str(getattr(args, "provider_tab_id", "") or "").strip()
    observed_url = str(getattr(args, "url", "") or "").strip()
    if browser_id in {"", "none"} or provider_tab_id in {
        "", "none", "pending_handoff", "canonical_url_only"
    }:
        raise LCRLError("a real browser provider tab identity is required for promotion")
    if any(character in browser_id + provider_tab_id for character in "\r\n\t"):
        raise LCRLError("browser and provider tab identities must be single-line values")
    if len(browser_id) > 240 or len(provider_tab_id) > 240:
        raise LCRLError("browser and provider tab identities are too long")

    reviewer_thread_id = state["confirmation"]["reviewer_thread_id"]
    expected_url = f"https://chatgpt.com/c/{reviewer_thread_id}"
    parsed = urlsplit(observed_url)
    if (
        observed_url != expected_url
        or parsed.scheme != "https"
        or parsed.netloc != "chatgpt.com"
        or parsed.query
        or parsed.fragment
    ):
        raise LCRLError("browser tab URL must match the bound reviewer Chat exactly")
    if binding.get("browser_id") != browser_id:
        raise LCRLError("browser identity cannot change during provider promotion")
    if binding.get("conversation_url") != expected_url:
        raise LCRLError("browser conversation cannot change during provider promotion")

    current_provider_id = binding.get("provider_tab_id")
    if current_provider_id not in {"pending_handoff", "canonical_url_only"}:
        if current_provider_id == provider_tab_id:
            return {
                "ok": True,
                "action": "browser_provider_identity_already_promoted",
                "browser_binding": deepcopy(binding),
                "revision": state["revision"],
            }
        raise LCRLError("browser provider identity is already fixed and cannot change")
    promotable_placeholder = (
        binding.get("status") == "bound"
        and (
            (
                current_provider_id == "pending_handoff"
                and binding.get("provisioned_chat") is True
            )
            or (
                current_provider_id == "canonical_url_only"
                and binding.get("provisioned_chat") is False
            )
        )
    )
    if not promotable_placeholder:
        raise LCRLError("only an authorized placeholder browser binding can be promoted")

    automation = state["automation"]
    runtime = state["runtime"]
    authorized = (
        state["review"]["status"] in MONITOR_STATUSES
        and automation.get("heartbeat_mode") == "waiting_only"
        and automation.get("waiting_check_active") is True
        and automation.get("waiting_check_token") == args.token
        and automation.get("waiting_check_automation_id", "none") == args.automation_id
        and automation.get("waiting_check_claimed_id", "none") == args.automation_id
        and runtime.get("action_lease_id", "none") == args.lease_id
        and runtime.get("action_lease_reason", "none") == "waiting_review_poll"
        and active_action_lease(state)
    )
    if not authorized:
        raise LCRLError("browser provider promotion requires the active waiting read lease")

    revision = state["revision"]
    binding["provider_tab_id"] = provider_tab_id
    save_state(path, state, expected_revision=revision)
    return {
        "ok": True,
        "action": "browser_provider_identity_promoted",
        "browser_binding": deepcopy(state["browser_binding"]),
        "revision": state["revision"],
    }


def browser_network_observation_command(args: argparse.Namespace) -> dict[str, Any]:
    """Record one authorized web-page health result after its read lease is released."""
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    automation = state["automation"]
    if state["review"].get("transport") != "in_app_browser":
        raise LCRLError("browser network observations require the in-app browser transport")
    if (
        state["review"]["status"] not in MONITOR_STATUSES
        or automation.get("waiting_check_active") is not True
        or automation.get("waiting_check_token") != args.token
        or automation.get("waiting_check_automation_id", "none") != args.automation_id
        or automation.get("waiting_check_claimed_id", "none") != args.automation_id
    ):
        raise LCRLError("cannot record a browser observation for a stale waiting check")
    if active_action_lease(state):
        raise LCRLError("browser observation requires the Chat read lease to be released")
    if args.outcome not in {"network_error", "rate_limited", "loaded"}:
        raise LCRLError("browser outcome must be network_error, rate_limited, or loaded")

    revision = state["revision"]
    observed_at = args.at or utc_now()
    recovery = state["recovery"]
    recovery["browser_last_observation_at"] = observed_at
    if args.outcome == "network_error":
        error = str(args.error or "browser page network error")
        normalized = normalized_network_error(error)
        recovery["network_state"] = "disconnected"
        recovery["network_error_count"] = int(recovery.get("network_error_count", 0)) + 1
        recovery["browser_consecutive_network_errors"] = int(
            recovery.get("browser_consecutive_network_errors", 0)
        ) + 1
        recovery["browser_consecutive_rate_limits"] = 0
        recovery["browser_reload_same_tab_required"] = True
        recovery["last_network_error_at"] = observed_at
        recovery["last_network_error_fingerprint"] = fingerprint(normalized)
        event_time = parse_time(observed_at) or datetime.now(timezone.utc)
        recovery["next_retry_not_before"] = (
            event_time + timedelta(seconds=BROWSER_REFRESH_INTERVAL_SECONDS)
        ).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        action = "schedule_browser_refresh"
        retry_after_seconds = BROWSER_REFRESH_INTERVAL_SECONDS
    elif args.outcome == "rate_limited":
        error = str(args.error or "browser page rate limited")
        count = int(recovery.get("browser_consecutive_rate_limits", 0)) + 1
        retry_after_seconds = min(
            BROWSER_RATE_LIMIT_INITIAL_BACKOFF_SECONDS * (2 ** min(count - 1, 2)),
            BROWSER_RATE_LIMIT_MAX_BACKOFF_SECONDS,
        )
        recovery["network_state"] = "rate_limited"
        recovery["browser_consecutive_network_errors"] = 0
        recovery["browser_consecutive_rate_limits"] = count
        recovery["browser_reload_same_tab_required"] = False
        recovery["last_network_error_at"] = observed_at
        recovery["last_network_error_fingerprint"] = fingerprint(error)
        event_time = parse_time(observed_at) or datetime.now(timezone.utc)
        recovery["next_retry_not_before"] = (
            event_time + timedelta(seconds=retry_after_seconds)
        ).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        action = "schedule_browser_rate_limit_probe"
    else:
        recovery["network_state"] = "healthy"
        recovery["browser_consecutive_network_errors"] = 0
        recovery["browser_consecutive_rate_limits"] = 0
        recovery["browser_reload_same_tab_required"] = False
        recovery["next_retry_not_before"] = "none"
        action = "browser_page_ready"
        retry_after_seconds = 0

    save_state(path, state, expected_revision=revision)
    return add_user_status_exit({
        "ok": True,
        "action": action,
        "status": state["review"]["status"],
        "retry_after_seconds": retry_after_seconds,
        "reload_same_tab_once": args.outcome == "network_error",
        "browser_consecutive_network_errors": recovery["browser_consecutive_network_errors"],
        "browser_consecutive_rate_limits": recovery["browser_consecutive_rate_limits"],
        "waiting_check_automation_id": args.automation_id,
    })


def directory_digest(root: Path, excluded: Path | None = None) -> str:
    """Hash a disposable acceptance directory without following outside paths."""
    root = root.resolve()
    if not root.is_dir():
        raise LCRLError(f"project path not found: {root}")
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file() and not item.is_symlink()):
        resolved = path.resolve()
        if excluded is not None and resolved == excluded.resolve():
            continue
        digest.update(str(resolved.relative_to(root)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(resolved.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def mac_queue_replay_check(args: argparse.Namespace) -> dict[str, Any]:
    """Replay one already-queued stale check and record release-gate evidence."""
    state_path = Path(args.state).expanduser().resolve()
    project_path = Path(args.project_path).expanduser().resolve()
    evidence_path = Path(args.evidence).expanduser().resolve() if args.evidence else None
    before_state = state_path.read_bytes()
    before_revision = load_state(state_path)["revision"]
    before_project = directory_digest(project_path, evidence_path)
    result = waiting_check_command(argparse.Namespace(
        state=str(state_path), token=args.token, automation_id="queued-stale-check"
    ))
    after_state = state_path.read_bytes()
    after = load_state(state_path)
    after_project = directory_digest(project_path, evidence_path)
    evidence = {
        "ok": True,
        "gate": "mac_queue_replay",
        "action": result.get("action"),
        "stale_check_silent": "user_status" not in result,
        "chat_read_count": 0 if result.get("action") == "waiting_check_expired" else 1,
        "project_write_count": 0 if before_project == after_project else 1,
        "state_version_before": before_revision,
        "state_version_after": after["revision"],
        "state_bytes_unchanged": before_state == after_state,
        "lease_id": after["runtime"].get("action_lease_id", "none"),
    }
    passed = (
        evidence["action"] == "waiting_check_expired"
        and evidence["stale_check_silent"] is True
        and evidence["chat_read_count"] == 0
        and evidence["project_write_count"] == 0
        and evidence["state_version_before"] == evidence["state_version_after"]
        and evidence["state_bytes_unchanged"] is True
        and evidence["lease_id"] == "none"
    )
    evidence["ok"] = passed
    if evidence_path is not None:
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not passed:
        raise LCRLError("Mac queue replay gate failed")
    return evidence


def bind_waiting_check_command(args: argparse.Namespace) -> dict[str, Any]:
    """Bind the current one-shot scheduler job to the current wait identity."""
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    automation = state["automation"]
    if automation.get("heartbeat_mode") != "waiting_only":
        raise LCRLError("foreground-only state cannot bind an automatic waiting check")
    if (state["review"]["status"] not in MONITOR_STATUSES
            or automation.get("waiting_check_active") is not True
            or automation.get("waiting_check_token") != args.token):
        raise LCRLError("cannot bind a waiting check after its wait has ended")
    current_id = automation.get("waiting_check_automation_id", "none")
    claimed_id = automation.get("waiting_check_claimed_id", "none")
    if current_id == args.automation_id:
        return add_user_status_exit({
            "ok": True, "action": "waiting_check_bound", "status": state["review"]["status"],
            "bound": True, "duplicate": True, "automation_id": args.automation_id,
        })
    if current_id != "none":
        if claimed_id != current_id or active_action_lease(state):
            raise LCRLError("cannot replace an unclaimed or still-running waiting check")
    revision = state["revision"]
    automation["waiting_check_automation_id"] = args.automation_id
    automation["waiting_check_claimed_id"] = "none"
    save_state(path, state, expected_revision=revision)
    return add_user_status_exit({
        "ok": True, "action": "waiting_check_bound", "status": state["review"]["status"],
        "bound": True, "duplicate": False, "automation_id": args.automation_id,
    })


def rearm_waiting_check_command(args: argparse.Namespace) -> dict[str, Any]:
    """Rotate one occurrence token while reusing the platform heartbeat ID."""
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    automation = state["automation"]
    if (automation.get("heartbeat_mode") != "waiting_only"
            or state["review"]["status"] not in MONITOR_STATUSES
            or automation.get("waiting_check_active") is not True
            or automation.get("waiting_check_token") != args.token
            or automation.get("waiting_check_automation_id", "none") != args.automation_id
            or automation.get("waiting_check_claimed_id", "none") != args.automation_id):
        raise LCRLError("cannot rearm a stale or unclaimed waiting check")
    if active_action_lease(state):
        raise LCRLError("cannot rearm a waiting check while its Chat read lease is active")
    revision = state["revision"]
    next_token = "wait-" + secrets.token_hex(8)
    automation["waiting_check_token"] = next_token
    automation["waiting_check_claimed_id"] = "none"
    try:
        save_state(path, state, expected_revision=revision)
    except (StateRevisionConflict, StateLockTimeout):
        latest = load_state(path)
        if latest["automation"].get("waiting_check_token") != args.token:
            return {"ok": True, "action": "waiting_check_expired"}
        return {"ok": True, "action": "waiting_check_busy"}
    return add_user_status_exit({
        "ok": True,
        "action": "update_once",
        "waiting_check_action": "update_once",
        "status": state["review"]["status"],
        "waiting_check_token": next_token,
        "waiting_check_automation_id": args.automation_id,
    })


def deactivate_waiting_check(state: dict[str, Any]) -> str:
    automation_id = state["automation"].get("waiting_check_automation_id", "none")
    state["automation"]["waiting_check_token"] = "none"
    state["automation"]["waiting_check_active"] = False
    state["automation"]["waiting_check_automation_id"] = "none"
    state["automation"]["waiting_check_claimed_id"] = "none"
    if state["runtime"].get("action_lease_reason") == "waiting_review_poll":
        clear_action_lease(state)
    return automation_id


def register_binding_command(args: argparse.Namespace) -> dict[str, Any]:
    state_path = Path(args.state).expanduser().resolve()
    registry_path = Path(args.registry).expanduser().resolve()
    state = load_state(state_path)
    state_revision = state["revision"]
    titles = build_binding_titles(args.display_name, args.iteration, args.work_status_label)
    entry = {
        "task_id": title_component(args.task_id, "task_id", 32),
        "display_name": title_component(args.display_name, "display_name", 12),
        "implementation_thread_id": state["automation"]["implementation_thread_id"],
        "reviewer_thread_id": state["confirmation"]["reviewer_thread_id"],
        "automation_id": state["automation"]["id"],
        "iteration": title_component(args.iteration, "iteration", 12),
        "work_status_label": title_component(args.work_status_label, "work_status_label", 12),
        "titles": titles,
        "naming_template_version": NAMING_TEMPLATE_VERSION,
        "updated_at": utc_now(),
    }
    with acquire_state_lock(registry_path):
        # Registry read, uniqueness validation, state bind, and registry replace
        # share one short critical section. Competing registrations therefore
        # merge against the latest durable task set instead of racing on a
        # stale revision and forcing otherwise independent bindings to fail.
        binding_registry = load_binding_registry(registry_path, allow_missing=True)
        registry_revision = binding_registry["revision"]
        tasks = [task for task in binding_registry["tasks"] if task.get("task_id") != entry["task_id"]]
        tasks.append(entry)
        candidate_registry = deepcopy(binding_registry)
        candidate_registry["tasks"] = tasks
        validate_binding_registry(candidate_registry)
        state["binding"] = {
            "status": "bound",
            "registry_path": str(registry_path),
            "task_id": entry["task_id"],
            "display_name": entry["display_name"],
            "iteration": entry["iteration"],
            "work_status_label": entry["work_status_label"],
            "naming_template_version": NAMING_TEMPLATE_VERSION,
            "expected_work_title": titles["work"],
            "expected_chat_title": titles["chat"],
            "expected_automation_title": titles["automation"],
        }
        state["automation"]["title"] = titles["automation"]
        save_state(state_path, state, expected_revision=state_revision)
        try:
            _save_binding_registry_locked(
                registry_path, candidate_registry, expected_revision=registry_revision,
            )
        except Exception:
            state["binding"]["status"] = "unbound"
            state["binding"]["registry_path"] = "none"
            state["automation"]["title"] = "none"
            save_state(state_path, state, expected_revision=state["revision"])
            raise
    return {
        "ok": True,
        "task_id": entry["task_id"],
        "state_revision": state["revision"],
        "registry_revision": candidate_registry["revision"],
        "titles": titles,
        "title_actions": [
            {
                "surface": "implementation_thread",
                "stable_id": entry["implementation_thread_id"],
                "title": titles["work"],
            },
            {
                "surface": "reviewer_chat",
                "stable_id": entry["reviewer_thread_id"],
                "title": titles["chat"],
            },
            {
                "surface": "waiting_check",
                "stable_id": entry["automation_id"],
                "title": titles["automation"],
            },
        ],
    }


def doctor_registry_command(args: argparse.Namespace) -> dict[str, Any]:
    registry_path = Path(args.registry).expanduser().resolve()
    findings: list[dict[str, str]] = []
    try:
        value = load_binding_registry(registry_path)
    except LCRLError as exc:
        return {"ok": False, "registry": str(registry_path), "findings": [{"severity": "error", "code": "registry_invalid", "detail": str(exc)}]}
    if not value["tasks"]:
        findings.append({"severity": "warning", "code": "registry_empty"})
    return {
        "ok": not any(item["severity"] == "error" for item in findings),
        "registry": str(registry_path),
        "revision": value["revision"],
        "task_count": len(value["tasks"]),
        "tasks": [{"task_id": task["task_id"], "titles": task["titles"]} for task in value["tasks"]],
        "findings": findings,
    }


def confirm_attachment_command(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    revision = state["revision"]
    expected = sorted({title_component(name, "attachment name", 180) for name in args.expected_name})
    observed = sorted({title_component(name, "attachment name", 180) for name in args.observed_name})
    if expected != observed:
        raise LCRLError("observed attachment names must exactly match expected attachment names")
    state["attachment"] = {
        "required": True,
        "verification": args.mode,
        "expected_names": expected,
        "observed_names": observed,
        "verified_at": args.at or utc_now(),
    }
    save_state(path, state, expected_revision=revision)
    return {"ok": True, "verification": args.mode, "attachments": observed, "revision": state["revision"]}


def reset_attachment_command(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    revision = state["revision"]
    state["attachment"] = {
        "required": bool(args.required),
        "verification": "unverified" if args.required else "not_required",
        "expected_names": list(args.expected_name or []),
        "observed_names": [],
        "verified_at": "none",
    }
    save_state(path, state, expected_revision=revision)
    return {"ok": True, "verification": state["attachment"]["verification"], "revision": state["revision"]}


def record_progress_command(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    revision = state["revision"]
    if not 1 <= args.active_minutes <= 120:
        raise LCRLError("active_minutes must be between 1 and 120")
    event = {
        "event_id": title_component(args.event_id, "event_id", 64),
        "stage": title_component(args.stage, "stage", 32),
        "active_minutes": args.active_minutes,
        "meaningful_step": bool(args.meaningful_step),
        "evidence_fingerprint": title_component(args.evidence_fingerprint, "evidence_fingerprint", 128),
        "recorded_at": args.at or utc_now(),
    }
    parse_time(event["recorded_at"])
    model_policy = state["model_policy"]
    progress = model_policy["progress"]
    existing = next((item for item in progress["events"] if item["event_id"] == event["event_id"]), None)
    if existing:
        comparable = {key: event[key] for key in ("event_id", "stage", "active_minutes", "meaningful_step", "evidence_fingerprint")}
        previous = {key: existing[key] for key in comparable}
        if comparable != previous:
            raise LCRLError("progress event_id already exists with different evidence")
        return {
            "ok": True,
            "duplicate": True,
            "event_id": event["event_id"],
            "active_minutes_since_pro": progress["active_minutes_since_pro"],
            "meaningful_steps_since_pro": progress["meaningful_steps_since_pro"],
            "pro_eligible": pro_is_eligible(model_policy),
            "revision": revision,
        }
    evidence_replay = next(
        (item for item in progress["events"] if item["evidence_fingerprint"] == event["evidence_fingerprint"]),
        None,
    )
    if evidence_replay:
        raise LCRLError("evidence_fingerprint already belongs to another progress event")
    if len(progress["events"]) >= MAX_PROGRESS_EVENTS:
        raise LCRLError("progress ledger is full; complete or diagnose the pending Pro milestone before recording more events")
    progress["events"].append(event)
    progress["active_minutes_since_pro"] += args.active_minutes
    if args.meaningful_step:
        progress["meaningful_steps_since_pro"] += 1
        model_policy["routing"]["meaningful_step_index"] += 1
    pro = model_policy["pro"]
    if pro["status"] == "tracking" and pro_is_eligible(model_policy):
        pro["status"] = "eligible"
        pro["eligibility_notified"] = False
    save_state(path, state, expected_revision=revision)
    return {
        "ok": True,
        "duplicate": False,
        "event_id": event["event_id"],
        "active_minutes_since_pro": progress["active_minutes_since_pro"],
        "meaningful_steps_since_pro": progress["meaningful_steps_since_pro"],
        "pro_eligible": pro_is_eligible(model_policy),
        "pro_status": pro["status"],
        "revision": state["revision"],
    }


def require_model_change_boundary(state: dict[str, Any], allowed_statuses: set[str]) -> None:
    if state["review"]["status"] not in allowed_statuses:
        raise LCRLError(f"model change requires review status in {sorted(allowed_statuses)}")
    if active_action_lease(state):
        raise LCRLError("model change is blocked while an implementation action lease is active")


def record_high_attempt_command(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    revision = state["revision"]
    require_model_change_boundary(state, {"local_work", "result_received"})
    routing = state["model_policy"]["routing"]
    advice = routing["advice"]
    if advice["status"] != "accepted" or advice["effective"] != "high_once":
        raise LCRLError("a High attempt requires one accepted Chat HIGH_ONCE recommendation")
    blocker_id = title_component(args.blocker_id, "blocker_id", 128)
    if blocker_id != advice["blocker_id"]:
        raise LCRLError("High attempt blocker must match the accepted Chat recommendation")
    attempt_id = title_component(args.attempt_id, "attempt_id", 128)
    evidence = title_component(args.evidence_fingerprint, "evidence_fingerprint", 128)
    existing = next((item for item in routing["high_attempts"] if item["attempt_id"] == attempt_id), None)
    if existing:
        if existing["blocker_id"] != blocker_id or existing["evidence_fingerprint"] != evidence:
            raise LCRLError("High attempt identity already exists with different evidence")
        return {"ok": True, "duplicate": True, "attempt_id": attempt_id, "revision": revision}
    step_index = routing["meaningful_step_index"]
    recent = [item for item in routing["high_attempts"] if item["meaningful_step_index"] > step_index - 10]
    if len(recent) >= HIGH_MAX_LAST_10_STEPS:
        raise LCRLError("Luna High two-of-ten ceiling has been reached")
    event = {
        "attempt_id": attempt_id,
        "blocker_id": blocker_id,
        "evidence_fingerprint": evidence,
        "advice_response_message_id": advice["response_message_id"],
        "meaningful_step_index": step_index,
        "completed_at": args.at or utc_now(),
        **default_execution_fact("authorized"),
    }
    parse_time(event["completed_at"])
    routing["high_attempts"] = (routing["high_attempts"] + [event])[-MAX_MODEL_ROUTE_EVENTS:]
    advice.update({"effective": "medium", "status": "consumed", "reason": "high_once_authorized_pending_execution"})
    save_state(path, state, expected_revision=revision)
    return {
        "ok": True, "duplicate": False, "attempt_id": attempt_id,
        "execution_status": "authorized", "executor": "luna_medium", "revision": state["revision"],
    }


def verify_execution_command(args: argparse.Namespace) -> dict[str, Any]:
    """Record caller-supplied execution evidence without claiming an automatic switch."""
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    revision = state["revision"]
    require_model_change_boundary(state, {"local_work", "result_received"})
    execution_id = title_component(args.execution_id, "execution_id", 128)
    proof = title_component(args.proof, "proof", 240)
    verified_at = args.at or utc_now()
    parse_time(verified_at)
    routing = state["model_policy"]["routing"]
    if args.target == "high":
        record = next((item for item in routing["high_attempts"] if item["attempt_id"] == execution_id), None)
        if record is None:
            raise LCRLError("High execution record does not exist")
        label = "High"
    else:
        record = state["model_policy"]["terra"]
        if record["status"] != "approved" or record["request_id"] != execution_id:
            raise LCRLError("Terra execution verification requires the matching approved request")
        label = "Terra"
    if record["execution_status"] == "verified":
        if (
            record["execution_source"] != args.source
            or record["execution_proof"] != proof
            or record["execution_verification_type"] != "manual_attested"
        ):
            raise LCRLError(f"{label} execution identity already has different verification evidence")
        return {
            "ok": True, "duplicate": True, "target": args.target,
            "execution_id": execution_id, "execution_status": "verified",
            "verification_type": "manual_attested", "revision": revision,
        }
    if record["execution_status"] != "authorized":
        raise LCRLError(f"{label} execution must be authorized before it can be verified")
    record.update({
        "execution_status": "verified",
        "execution_source": args.source,
        "execution_proof": proof,
        "execution_verified_at": verified_at,
        "execution_verification_type": "manual_attested",
    })
    save_state(path, state, expected_revision=revision)
    return {
        "ok": True, "duplicate": False, "target": args.target,
        "execution_id": execution_id, "execution_status": "verified",
        "verification_type": "manual_attested",
        "executor": "luna_medium", "revision": state["revision"],
    }


def request_pro_command(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    revision = state["revision"]
    require_model_change_boundary(state, {"local_work"})
    model_policy = state["model_policy"]
    pro = model_policy["pro"]
    if pro["status"] != "eligible" or not pro_is_eligible(model_policy):
        raise LCRLError("Pro milestone is not eligible yet")
    if model_policy["terra"]["status"] != "idle":
        raise LCRLError("finish or cancel the Terra request before requesting Pro")
    request_id = "pro-" + secrets.token_hex(8)
    pro.update({
        "status": "confirmation_required",
        "request_id": request_id,
        "requested_at": args.at or utc_now(),
        "user_confirmed": False,
        "started_at": "none",
    })
    parse_time(pro["requested_at"])
    save_state(path, state, expected_revision=revision)
    return {
        "ok": True,
        "request_id": request_id,
        "action": "user_select_chat_pro",
        "automatic_switch": False,
        "revision": state["revision"],
    }


def confirm_pro_command(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    revision = state["revision"]
    require_model_change_boundary(state, {"local_work"})
    model_policy = state["model_policy"]
    pro = model_policy["pro"]
    if pro["status"] != "confirmation_required" or pro["request_id"] != args.request_id:
        raise LCRLError("Pro request identity does not match the pending confirmation")
    pro.update({"status": "in_review", "user_confirmed": True, "started_at": args.at or utc_now()})
    parse_time(pro["started_at"])
    model_policy["reviewer"]["current"] = "chat_pro"
    save_state(path, state, expected_revision=revision)
    return {
        "ok": True,
        "request_id": pro["request_id"],
        "reviewer": "chat_pro",
        "automatic_switch": False,
        "revision": state["revision"],
    }


def cancel_pro_command(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    revision = state["revision"]
    reason = title_component(args.reason, "reason", 240)
    model_policy = state["model_policy"]
    pro = model_policy["pro"]
    if pro["status"] not in {"confirmation_required", "in_review"} or pro["request_id"] != args.request_id:
        raise LCRLError("Pro cancellation does not match an active request")
    if pro["status"] == "in_review" and not args.force:
        raise LCRLError("cancelling an active Pro review requires --force after verifying no response will be applied")
    previous_request = pro["request_id"]
    pro.update({
        "status": "eligible",
        "eligibility_notified": True,
        "request_id": "none",
        "requested_at": "none",
        "user_confirmed": False,
        "started_at": "none",
        "last_request_id": previous_request,
        "last_outcome": "cancelled",
        "last_reason": reason,
    })
    model_policy["reviewer"]["current"] = "sol_extreme"
    save_state(path, state, expected_revision=revision)
    return {
        "ok": True,
        "request_id": previous_request,
        "reason": reason,
        "pro_status": "eligible",
        "reviewer_restored": "sol_extreme",
        "revision": state["revision"],
    }


def resolve_project_file(state: dict[str, Any], value: str) -> Path:
    project_root = Path(state["automation"]["project_path"]).resolve()
    candidate = Path(value).expanduser()
    path = (project_root / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
    try:
        path.relative_to(project_root)
    except ValueError as exc:
        raise LCRLError("milestone guide must remain inside the project root") from exc
    return path


def complete_pro_command(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    revision = state["revision"]
    model_policy = state["model_policy"]
    pro = model_policy["pro"]
    guide = resolve_project_file(state, args.guide_path)
    if not guide.is_file() or guide.suffix.lower() != ".md":
        raise LCRLError("Pro milestone guide must be an existing Markdown file")
    observed_hash = hashlib.sha256(guide.read_bytes()).hexdigest()
    expected_hash = args.guide_sha256.lower()
    if not re.fullmatch(r"[0-9a-f]{64}", expected_hash) or observed_hash != expected_hash:
        raise LCRLError("Pro milestone guide SHA-256 does not match")
    guide_version = title_component(args.guide_version, "guide_version", 32)
    if (
        pro["status"] == "tracking"
        and pro["last_request_id"] == args.request_id
        and pro["last_outcome"] == "completed"
    ):
        if pro["last_guide_path"] != str(guide) or pro["last_guide_sha256"] != observed_hash:
            raise LCRLError("completed Pro request is being replayed with different evidence")
        return {"ok": True, "duplicate": True, "request_id": args.request_id, "revision": revision}
    if pro["status"] != "in_review" or pro["request_id"] != args.request_id:
        raise LCRLError("Pro completion does not match the active review")
    completed_at = args.at or utc_now()
    parse_time(completed_at)
    pro.update({
        "status": "tracking",
        "eligibility_notified": False,
        "request_id": "none",
        "requested_at": "none",
        "user_confirmed": False,
        "started_at": "none",
        "last_request_id": args.request_id,
        "last_outcome": "completed",
        "last_reason": "none",
        "last_completed_at": completed_at,
        "last_guide_version": guide_version,
        "last_guide_path": str(guide),
        "last_guide_sha256": observed_hash,
        "review_count": pro["review_count"] + 1,
    })
    model_policy["reviewer"]["current"] = "sol_extreme"
    model_policy["progress"] = {
        "active_minutes_since_pro": 0,
        "meaningful_steps_since_pro": 0,
        "events": [],
    }
    save_state(path, state, expected_revision=revision)
    return {
        "ok": True,
        "duplicate": False,
        "request_id": args.request_id,
        "guide_version": guide_version,
        "guide_path": str(guide),
        "guide_sha256": observed_hash,
        "reviewer_restored": "sol_extreme",
        "revision": state["revision"],
    }


def request_terra_command(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    revision = state["revision"]
    require_model_change_boundary(state, {"local_work", "result_received"})
    if state["capability_probes"]["terra_next_turn"] != "supported":
        raise LCRLError("Terra next-turn capability is not verified as supported")
    model_policy = state["model_policy"]
    terra = model_policy["terra"]
    if terra["status"] != "idle":
        raise LCRLError("a Terra request is already active")
    if model_policy["pro"]["status"] == "in_review":
        raise LCRLError("Terra cannot be requested during a Pro milestone review")
    routing = model_policy["routing"]
    advice = routing["advice"]
    if advice["status"] != "accepted" or advice["effective"] != "terra_request":
        raise LCRLError("Terra requires one accepted Chat TERRA_REQUEST recommendation")
    if advice["signal"] != args.signal:
        raise LCRLError("Terra signal must match the accepted Chat recommendation")
    high = next(
        (item for item in routing["high_attempts"] if item["attempt_id"] == advice["high_attempt_id"]),
        None,
    )
    if high is None or high["blocker_id"] != advice["blocker_id"]:
        raise LCRLError("Terra requires a matching Luna High record for the same blocker")
    if high.get("execution_status") != "verified":
        raise LCRLError("Terra requires verified High execution for the same blocker")
    step_index = routing["meaningful_step_index"]
    recent_terra = [item for item in routing["terra_turns"] if item["meaningful_step_index"] > step_index - 20]
    if len(recent_terra) >= TERRA_MAX_LAST_20_STEPS:
        raise LCRLError("Terra one-of-twenty ceiling has been reached")
    reason = title_component(args.reason, "reason", 240)
    request_id = "terra-" + secrets.token_hex(8)
    terra.update({
        "status": "requested",
        "request_id": request_id,
        "signal": args.signal,
        "reason": reason,
        "requested_at": args.at or utc_now(),
        "user_confirmed": False,
        "approved_at": "none",
        "blocker_id": advice["blocker_id"],
        "high_attempt_id": advice["high_attempt_id"],
        "evidence_fingerprint": fingerprint(advice["evidence"]),
        "advice_response_message_id": advice["response_message_id"],
        **default_execution_fact(),
    })
    parse_time(terra["requested_at"])
    save_state(path, state, expected_revision=revision)
    return {
        "ok": True,
        "request_id": request_id,
        "signal": args.signal,
        "action": "confirm_one_terra_turn",
        "automatic_switch": False,
        "revision": state["revision"],
    }


def set_terra_capability_command(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    revision = state["revision"]
    terra = state["model_policy"]["terra"]
    if args.status != "supported" and terra["status"] != "idle":
        if terra["status"] == "approved" and not args.force:
            raise LCRLError("downgrading an approved Terra turn requires --force after verifying it has stopped")
        previous_request = terra["request_id"]
        terra.update({
            "status": "idle",
            "request_id": "none",
            "signal": "none",
            "reason": "none",
            "requested_at": "none",
            "user_confirmed": False,
            "approved_at": "none",
            "blocker_id": "none",
            "high_attempt_id": "none",
            "evidence_fingerprint": "none",
            "advice_response_message_id": "none",
            "last_request_id": previous_request,
            "last_outcome": "capability_downgraded",
            "last_reason": f"capability={args.status}",
            **default_execution_fact(),
        })
    state["capability_probes"]["terra_next_turn"] = args.status
    save_state(path, state, expected_revision=revision)
    return {
        "ok": True,
        "terra_next_turn": args.status,
        "executor": state["model_policy"]["executor"]["current"],
        "revision": state["revision"],
    }


def confirm_terra_command(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    revision = state["revision"]
    require_model_change_boundary(state, {"local_work", "result_received"})
    if state["capability_probes"]["terra_next_turn"] != "supported":
        raise LCRLError("Terra next-turn capability is no longer supported")
    model_policy = state["model_policy"]
    terra = model_policy["terra"]
    if terra["status"] != "requested" or terra["request_id"] != args.request_id:
        raise LCRLError("Terra request identity does not match the pending confirmation")
    terra.update({
        "status": "approved",
        "user_confirmed": True,
        "approved_at": args.at or utc_now(),
        **default_execution_fact("authorized"),
    })
    parse_time(terra["approved_at"])
    save_state(path, state, expected_revision=revision)
    return {
        "ok": True,
        "request_id": args.request_id,
        "executor": "luna_medium",
        "requested_executor": "terra",
        "execution_status": "authorized",
        "scope": "one_bounded_turn",
        "automatic_switch": False,
        "revision": state["revision"],
    }


def complete_terra_command(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    revision = state["revision"]
    model_policy = state["model_policy"]
    terra = model_policy["terra"]
    if (
        terra["status"] == "idle"
        and terra["last_request_id"] == args.request_id
        and terra["last_outcome"] == "completed"
    ):
        return {"ok": True, "duplicate": True, "request_id": args.request_id, "revision": revision}
    if terra["status"] != "approved" or terra["request_id"] != args.request_id:
        raise LCRLError("Terra completion does not match the approved turn")
    completed_at = args.at or utc_now()
    parse_time(completed_at)
    routing = model_policy["routing"]
    routing["terra_turns"] = (routing["terra_turns"] + [{
        "request_id": args.request_id,
        "blocker_id": terra["blocker_id"],
        "high_attempt_id": terra["high_attempt_id"],
        "evidence_fingerprint": terra["evidence_fingerprint"],
        "meaningful_step_index": routing["meaningful_step_index"],
        "completed_at": completed_at,
        "execution_status": terra["execution_status"],
        "execution_source": terra["execution_source"],
        "execution_proof": terra["execution_proof"],
        "execution_verified_at": terra["execution_verified_at"],
        "execution_verification_type": terra["execution_verification_type"],
    }])[-MAX_MODEL_ROUTE_EVENTS:]
    terra.update({
        "status": "idle",
        "request_id": "none",
        "signal": "none",
        "reason": "none",
        "requested_at": "none",
        "user_confirmed": False,
        "approved_at": "none",
        "blocker_id": "none",
        "high_attempt_id": "none",
        "evidence_fingerprint": "none",
        "advice_response_message_id": "none",
        "last_request_id": args.request_id,
        "last_outcome": "completed",
        "last_reason": "none",
        "last_completed_at": completed_at,
        "request_count": terra["request_count"] + 1,
        **default_execution_fact(),
    })
    routing["advice"].update({
        "effective": "medium", "status": "consumed", "reason": "terra_turn_completed",
    })
    save_state(path, state, expected_revision=revision)
    return {
        "ok": True,
        "duplicate": False,
        "request_id": args.request_id,
        "executor": "luna_medium",
        "execution_status": routing["terra_turns"][-1]["execution_status"],
        "revision": state["revision"],
    }


def cancel_terra_command(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    revision = state["revision"]
    reason = title_component(args.reason, "reason", 240)
    terra = state["model_policy"]["terra"]
    if terra["status"] not in {"requested", "approved"} or terra["request_id"] != args.request_id:
        raise LCRLError("Terra cancellation does not match an active request")
    if terra["status"] == "approved" and not args.force:
        raise LCRLError("cancelling an approved Terra turn requires --force after verifying it has stopped")
    previous_request = terra["request_id"]
    terra.update({
        "status": "idle",
        "request_id": "none",
        "signal": "none",
        "reason": "none",
        "requested_at": "none",
        "user_confirmed": False,
        "approved_at": "none",
        "blocker_id": "none",
        "high_attempt_id": "none",
        "evidence_fingerprint": "none",
        "advice_response_message_id": "none",
        "last_request_id": previous_request,
        "last_outcome": "cancelled",
        "last_reason": reason,
        **default_execution_fact(),
    })
    state["model_policy"]["routing"]["advice"].update({
        "effective": "medium", "status": "consumed", "reason": "terra_request_cancelled",
    })
    save_state(path, state, expected_revision=revision)
    return {
        "ok": True,
        "request_id": previous_request,
        "reason": reason,
        "executor_restored": state["model_policy"]["executor"]["current"],
        "revision": state["revision"],
    }


def model_status_command(args: argparse.Namespace) -> dict[str, Any]:
    state = load_state(args.state)
    model_policy = state["model_policy"]
    pro = model_policy["pro"]
    terra = model_policy["terra"]
    routing = model_policy["routing"]
    advice = routing["advice"]
    latest_high = routing["high_attempts"][-1] if routing["high_attempts"] else None
    if pro["status"] == "in_review":
        next_action = "complete_pro_after_saving_versioned_guide"
    elif pro["status"] == "confirmation_required":
        next_action = "user_confirm_chat_pro_then_confirm_pro"
    elif terra["status"] == "approved":
        next_action = "record_terra_execution_fact_or_complete_authorization"
    elif terra["status"] == "requested":
        next_action = "confirm_or_reject_terra_request"
    elif pro_is_eligible(model_policy):
        next_action = "request_pro_at_safe_boundary"
    else:
        next_action = "continue_luna_with_sol_extreme_review"
    return {
        "ok": True,
        "executor": model_policy["executor"]["current"],
        "reviewer": model_policy["reviewer"]["current"],
        "automatic_model_switch": False,
        "automatic_thread_creation": False,
        "active_minutes_since_pro": model_policy["progress"]["active_minutes_since_pro"],
        "meaningful_steps_since_pro": model_policy["progress"]["meaningful_steps_since_pro"],
        "model_routing_meaningful_step_index": model_policy["routing"]["meaningful_step_index"],
        "pro_eligible": pro_is_eligible(model_policy),
        "pro_status": pro["status"],
        "terra_status": terra["status"],
        "chat_model_advice": advice["effective"],
        "chat_model_advice_status": advice["status"],
        "chat_model_advice_reason": advice["reason"],
        "chat_model_advice_execution_status": advice["execution_status"],
        "latest_high_attempt_id": latest_high["attempt_id"] if latest_high else "none",
        "latest_high_execution_status": latest_high["execution_status"] if latest_high else "none",
        "latest_high_execution_verification_type": latest_high["execution_verification_type"] if latest_high else "none",
        "latest_high_execution_source": latest_high["execution_source"] if latest_high else "none",
        "terra_execution_status": terra["execution_status"],
        "terra_execution_verification_type": terra["execution_verification_type"],
        "terra_execution_source": terra["execution_source"],
        "next_action": next_action,
        "revision": state["revision"],
    }


def guard_action(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.state).resolve()
    state = load_state(path)
    revision = state["revision"]
    status = state["review"]["status"]
    if status in MONITOR_STATUSES:
        return add_user_status_exit({
            "ok": True,
            "action": "waiting_turn_blocked",
            "status": status,
            "execution_allowed": False,
            "project_read_allowed": False,
            "project_write_allowed": False,
            "browser_access_allowed": False,
            "waiting_check_only": True,
            "lease_id": "none",
            "revision": revision,
        })
    recovered_same_task_lease = False
    if active_action_lease(state):
        implementation_thread_id = str(
            getattr(args, "implementation_thread_id", None) or "none"
        ).strip()
        same_task_recovery = bool(
            implementation_thread_id != "none"
            and implementation_thread_id == state["automation"].get("implementation_thread_id")
            and state["runtime"].get("action_lease_reason") in {"turn_entry", "apply_result"}
        )
        if not same_task_recovery:
            raise LCRLError("an unexpired action lease already exists")
        recovered_same_task_lease = True
    clear_action_lease(state)
    lease_id = claim_action_lease(state, args.reason, args.minutes)
    save_state(path, state, expected_revision=revision)
    return {
        "ok": True,
        "action": "turn_entry_allowed",
        "execution_allowed": True,
        "lease_id": lease_id,
        "expires_at": state["runtime"]["action_lease_expires_at"],
        "recovered_same_task_lease": recovered_same_task_lease,
    }


def release_action(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.state).resolve()
    state = load_state(path)
    revision = state["revision"]
    current = state["runtime"].get("action_lease_id", "none")
    if current == "none":
        return {"ok": True, "released": False, "reason": "already_clear", "revision": revision}
    if args.lease_id != current and not args.force:
        raise LCRLError("lease id does not match the active action lease")
    clear_action_lease(state)
    save_state(path, state, expected_revision=revision)
    return {"ok": True, "released": True, "revision": state["revision"]}


def confirm_review_mode(args: argparse.Namespace) -> dict[str, Any]:
    if args.mode != "extreme":
        raise LCRLError("the review reasoning mode must be extreme")
    path = Path(args.state).resolve()
    state = load_state(path)
    revision = state["revision"]
    source = getattr(args, "source", None) or "user"
    observed_label = getattr(args, "observed_label", None) or "极高"
    observed_thread_id = getattr(args, "reviewer_thread_id", None) or state["confirmation"]["reviewer_thread_id"]
    native_instance_id = getattr(args, "native_app_instance_id", None) or "none"
    review_transport = state["review"].get("transport", "app_chat_review")
    if source not in {"user", "main_app", "native_app", "in_app_browser"}:
        raise LCRLError(
            "review mode confirmation must come from the selected formal review surface"
        )
    if review_transport == "in_app_browser" and source != "in_app_browser":
        raise LCRLError("in-app browser review mode must be confirmed in the bound web Chat")
    if (
        review_transport == "in_app_browser"
        and state.get("browser_binding", {}).get("status") != "bound"
    ):
        raise LCRLError("in-app browser review mode requires a persisted browser tab binding")
    if review_transport == "app_chat_review" and source == "in_app_browser":
        raise LCRLError("browser reasoning evidence cannot confirm an App Chat review")
    if source == "native_app" and native_instance_id == "none":
        raise LCRLError("native App reasoning confirmation requires an App instance identity")
    if source in {"user", "main_app", "in_app_browser"} and native_instance_id != "none":
        raise LCRLError("non-native reasoning confirmation cannot claim a native App instance")
    if observed_label != "极高":
        raise LCRLError("the observed review reasoning label must be 极高")
    if observed_thread_id != state["confirmation"]["reviewer_thread_id"]:
        raise LCRLError("review mode evidence must come from the bound reviewer Chat")
    state["confirmation"].update({
        "reviewer_reasoning_mode": "extreme",
        "reviewer_reasoning_confirmed": True,
        "reviewer_reasoning_confirmed_at": args.at or utc_now(),
        "reviewer_reasoning_control_source": source,
        "reviewer_reasoning_observed_label": observed_label,
        "reviewer_reasoning_observed_thread_id": observed_thread_id,
        "reviewer_reasoning_native_app_instance_id": native_instance_id,
    })
    save_state(path, state, expected_revision=revision)
    return {
        "ok": True,
        "mode": "extreme",
        "source": source,
        "reviewer_thread_id": observed_thread_id,
        "native_app_instance_id": native_instance_id,
        "revision": state["revision"],
    }


def confirm_review_submission_command(args: argparse.Namespace) -> dict[str, Any]:
    """Record the one visible App Chat submission before the loop may wait."""
    path = Path(args.state).resolve()
    state = load_state(path)
    review = state["review"]
    if review["status"] not in {"review_submit_pending", "review_receipt_pending"}:
        if review.get("request_message_id") == args.request_message_id:
            automation = state["automation"]
            automatic_wait = (
                review["status"] == "review_waiting"
                and automation.get("heartbeat_mode") == "waiting_only"
                and automation.get("waiting_check_active") is True
            )
            waiting_action = "keep_once"
            if automatic_wait and automation.get("waiting_check_automation_id", "none") == "none":
                waiting_action = "schedule_once"
            elif not automatic_wait:
                waiting_action = "foreground_resume_required"
            return add_user_status_exit({
                "ok": True,
                "action": "already_confirmed",
                "confirmed": False,
                "status": review["status"],
                "request_message_id": args.request_message_id,
                "waiting_check_action": waiting_action,
                "waiting_check_token": automation.get("waiting_check_token", "none"),
                "waiting_check_automation_id": automation.get(
                    "waiting_check_automation_id", "none"
                ),
            })
        raise LCRLError("review submission is not pending")
    if args.reviewer_thread_id != state["confirmation"]["reviewer_thread_id"]:
        raise LCRLError("submission target must match the bound App Chat")
    native_instance_id = getattr(args, "native_app_instance_id", None) or "none"
    if state["confirmation"].get("reviewer_reasoning_control_source") == "native_app":
        if native_instance_id != state["confirmation"].get("reviewer_reasoning_native_app_instance_id"):
            raise LCRLError("submission must use the App instance that confirmed Extreme")
    elif native_instance_id != "none":
        raise LCRLError("single main App review confirmation cannot accept a native App submission identity")
    reopen_lease_id = str(
        getattr(args, "browser_reopen_lease_id", None) or "none"
    ).strip()
    reopen_browser_id = str(getattr(args, "browser_id", None) or "none").strip()
    runtime = state["runtime"]
    active_reopen_lease = (
        runtime.get("action_lease_reason") == "browser_submission_reopen"
        and active_action_lease(state)
    )
    if active_reopen_lease and reopen_lease_id != runtime.get("action_lease_id"):
        raise LCRLError("browser submission reopen lease proof is required")
    if active_reopen_lease and reopen_browser_id != runtime.get(
        "browser_submission_reopen_browser_id", "none"
    ):
        raise LCRLError("submission must use the authorized browser identity")
    if reopen_lease_id != "none" and not (
        active_reopen_lease
        and reopen_lease_id == runtime.get("action_lease_id")
        and _bound_browser_chat_can_reopen(state)
    ):
        raise LCRLError("browser submission reopen lease proof is invalid or expired")
    if reopen_lease_id != "none":
        send_authorization_revision = getattr(
            args, "browser_send_authorization_revision", None
        )
        if not (
            send_authorization_revision == state["revision"]
            and runtime.get("browser_submission_send_authorized_lease_id")
            == reopen_lease_id
            and runtime.get("browser_submission_send_authorized_revision")
            == send_authorization_revision
        ):
            raise LCRLError(
                "fresh browser submission send authorization is required"
            )
    submission_lease_id = reopen_lease_id
    if (
        submission_lease_id == "none"
        and runtime.get("action_lease_reason") == "turn_entry"
        and active_action_lease(state)
    ):
        # The entry lease protects local work and the visible send. Keeping it
        # after a durable submission would make the first legal waiting check
        # collide with work that has already finished.
        submission_lease_id = str(runtime.get("action_lease_id") or "none")
    expected = sorted(state["attachment"].get("expected_names", [])) if review["payload_mode"] == "app_attachment" else []
    observed = sorted(args.attachment_name or [])
    if expected != observed:
        raise LCRLError("submission attachment names must match the confirmed list")
    result = transition(argparse.Namespace(
        state=str(path), status="review_waiting", stage=None, payload_mode=None, fingerprint=None,
        waiting_since=args.submitted_at or utc_now(), request_turn_id=args.request_turn_id,
        request_message_id=args.request_message_id, request_persisted_at=args.submitted_at or utc_now(),
        request_stage=None, request_reasoning_mode=None,
        request_native_app_instance_id=native_instance_id,
        response_turn_id=None, response_message_id=None,
        response_completed_at=None, response_complete=None, response_envelope_hash=None, response_stage=None,
        artifacts_summary=None, recovery_action="review_submission_confirmed", attachment_send=None,
        filesystem_read=None, quarantine_unconfirmed=False, recovery_override=False,
        deleted_automation_id=getattr(args, "deleted_automation_id", None),
        release_action_lease_id=(
            submission_lease_id if submission_lease_id != "none" else None
        ),
        browser_rebind_id=(
            reopen_browser_id if reopen_lease_id != "none" else None
        ),
    ))
    return add_user_status_exit({
        "ok": True,
        "action": "submission_confirmed",
        "confirmed": True,
        "status": result["status"],
        "request_message_id": args.request_message_id,
        "attachment_count": len(observed),
        "waiting_check_action": result["waiting_check_action"],
        "waiting_check_token": result["waiting_check_token"],
        "waiting_check_automation_id": result["waiting_check_automation_id"],
        "waiting_check_previous_automation_id": result[
            "waiting_check_previous_automation_id"
        ],
    })


def invalidate_review_mode(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.state).resolve()
    state = load_state(path)
    revision = state["revision"]
    state["confirmation"].update({
        "reviewer_reasoning_mode": "unconfirmed",
        "reviewer_reasoning_confirmed": False,
        "reviewer_reasoning_confirmed_at": "none",
        "reviewer_reasoning_control_source": "none",
        "reviewer_reasoning_observed_label": "none",
        "reviewer_reasoning_observed_thread_id": "none",
        "reviewer_reasoning_native_app_instance_id": "none",
        "reviewer_reasoning_invalidated_reason": args.reason,
    })
    save_state(path, state, expected_revision=revision)
    return {"ok": True, "mode": "unconfirmed", "revision": state["revision"]}


def record_network_error_command(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.state).resolve()
    state = load_state(path)
    revision = state["revision"]
    event = {"timestamp": args.at or utc_now(), "error": args.message, "success": "false"}
    record_network_observation(state, event)
    save_state(path, state, expected_revision=revision)
    return {"ok": True, "network": state["recovery"]["network_state"], "revision": state["revision"]}


def set_monitor_mode_command(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.state).resolve()
    state = load_state(path)
    revision = state["revision"]
    state["automation"]["heartbeat_mode"] = args.mode
    if args.mode == "foreground_only":
        state["automation"]["interval_minutes"] = 0
    save_state(path, state, expected_revision=revision)
    return {"ok": True, "mode": args.mode, "revision": state["revision"]}


def clear_review_cycle(review: dict[str, Any]) -> None:
    review.update({
        "cycle_id": "none",
        "request_turn_id": "none",
        "request_message_id": "none",
        "request_persisted_at": "none",
        "request_stage": "none",
        "request_reasoning_mode": "none",
        "request_native_app_instance_id": "none",
        "response_turn_id": "none",
        "response_message_id": "none",
        "response_completed_at": "none",
        "response_complete": False,
        "response_envelope_hash": "none",
        "response_stage": "none",
        "response_valid_for_apply": False,
        "response_quarantined_reason": "none",
        "waiting_since": "none",
        "submission_fingerprint": "none",
        "reviewer_execution_status": "idle",
    })


def archive_review_cycle(state: dict[str, Any], reason: str) -> None:
    review = state["review"]
    meaningful = any(
        review.get(field) not in (None, "", "none", False)
        for field in ("cycle_id", "submission_fingerprint", "request_message_id", "response_message_id")
    )
    if meaningful:
        snapshot = {
            key: deepcopy(review.get(key))
            for key in (
                "cycle_id", "current_stage", "status", "submission_fingerprint",
                "request_turn_id", "request_message_id", "request_persisted_at",
                "request_stage", "request_reasoning_mode", "response_turn_id",
                "request_native_app_instance_id",
                "response_message_id", "response_completed_at", "response_complete",
                "response_envelope_hash", "response_stage", "response_valid_for_apply",
                "response_quarantined_reason",
            )
        }
        snapshot.update({"archived_at": utc_now(), "archive_reason": reason})
        state.setdefault("review_history", []).append(snapshot)
        state["review_history"] = state["review_history"][-20:]
    clear_review_cycle(review)


def transition(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.state).resolve()
    state = load_state(path)
    revision = state["revision"]
    review = state["review"]
    old_status = review["status"]
    if args.status == "completed":
        overall_goal_complete = bool(getattr(args, "overall_goal_complete", False))
        completion_evidence = getattr(args, "completion_evidence", None)
        evidence_present = completion_evidence not in (None, "", "none")
        if review.get("goal_mode") == "continuous":
            if old_status != "result_received":
                raise LCRLError(
                    "continuous overall goal completion requires a reviewed result_received boundary"
                )
            if not overall_goal_complete or not evidence_present:
                raise LCRLError(
                    "continuous overall goal completion requires explicit overall goal completion evidence"
                )
        if overall_goal_complete:
            if not evidence_present:
                raise LCRLError("overall goal completion requires --completion-evidence")
            review["overall_completion_confirmed"] = True
            review["overall_completion_evidence"] = completion_evidence
        elif evidence_present:
            raise LCRLError("--completion-evidence requires --overall-goal-complete")
    if not getattr(args, "recovery_override", False) and args.status not in ALLOWED_TRANSITIONS[old_status]:
        raise LCRLError(f"illegal transition: {old_status} -> {args.status}")
    if (
        old_status == "result_quarantined"
        and args.status == "result_received"
        and getattr(args, "recovery_action", None) in (None, "", "none")
    ):
        raise LCRLError("recovering a quarantined natural-language reply requires explicit user authorization")
    if getattr(args, "quarantine_unconfirmed", False) and args.status != "review_waiting":
        raise LCRLError("--quarantine-unconfirmed is only valid for review_waiting")
    if args.status == "review_submit_pending":
        archive_review_cycle(state, "new_review_submission")
    elif args.status in {"local_work", "completed"} and old_status in {"result_received", "result_quarantined"}:
        if args.status == "local_work" and old_status == "result_received":
            operation = state.get("next_operation", {})
            if not (
                operation.get("status") == "validated"
                and operation.get("source_response_message_id") == review.get("response_message_id")
            ):
                raise LCRLError("cannot apply result before its operation package is durably persisted")
            operation["status"] = "applied"
            operation["applied_at"] = utc_now()
        archive_review_cycle(state, f"transition_to_{args.status}")
    review["status"] = args.status
    mapping = {
        "stage": "current_stage",
        "payload_mode": "payload_mode",
        "fingerprint": "submission_fingerprint",
        "waiting_since": "waiting_since",
        "request_turn_id": "request_turn_id",
        "request_message_id": "request_message_id",
        "request_persisted_at": "request_persisted_at",
        "request_stage": "request_stage",
        "request_reasoning_mode": "request_reasoning_mode",
        "request_native_app_instance_id": "request_native_app_instance_id",
        "response_turn_id": "response_turn_id",
        "response_message_id": "response_message_id",
        "response_completed_at": "response_completed_at",
        "response_envelope_hash": "response_envelope_hash",
        "response_stage": "response_stage",
        "artifacts_summary": "artifacts_summary",
        "recovery_action": "recovery_action",
    }
    for argument, field in mapping.items():
        value = getattr(args, argument, None)
        if value is not None:
            review[field] = value
    if getattr(args, "response_complete", None) is not None:
        review["response_complete"] = args.response_complete == "true"
    if getattr(args, "attachment_send", None):
        state["capabilities"]["attachment_send"] = args.attachment_send
    if getattr(args, "filesystem_read", None):
        state["capabilities"]["filesystem_read"] = args.filesystem_read
    empty = (None, "", "none")
    if args.status == "review_submit_pending":
        if review.get("submission_fingerprint") in empty:
            raise LCRLError("review_submit_pending requires --fingerprint")
        review["cycle_id"] = "cycle-" + fingerprint({
            "stage": review["current_stage"],
            "fingerprint": review["submission_fingerprint"],
            "created_at": utc_now(),
        })[:16]
    elif args.status in {"review_receipt_pending", "review_waiting"}:
        review["request_stage"] = review["current_stage"]
        confirmed_extreme = (
            state["confirmation"].get("reviewer_reasoning_confirmed") is True
            and state["confirmation"].get("reviewer_reasoning_mode") == "extreme"
        )
        if args.status == "review_receipt_pending":
            if not confirmed_extreme:
                raise LCRLError("cannot reconcile a review receipt before the selected App Chat is confirmed Extreme")
            if any(review.get(field) not in empty for field in ("request_turn_id", "request_message_id", "request_persisted_at")):
                raise LCRLError("review_receipt_pending must not contain invented request identity")
            review["request_reasoning_mode"] = "extreme"
            review["waiting_since"] = review.get("waiting_since") if review.get("waiting_since") not in empty else utc_now()
            review["response_quarantined_reason"] = "none"
        elif getattr(args, "quarantine_unconfirmed", False):
            review["request_reasoning_mode"] = "unconfirmed"
            review["response_quarantined_reason"] = "request_sent_before_extreme_confirmation"
        else:
            if not confirmed_extreme:
                raise LCRLError("cannot enter review_waiting before the selected App Chat is confirmed Extreme")
            review["request_reasoning_mode"] = "extreme"
            review["response_quarantined_reason"] = "none"
        review["response_valid_for_apply"] = False
    elif args.status in {"result_received", "result_quarantined"}:
        review["response_stage"] = review.get("response_stage") if review.get("response_stage") not in empty else review["current_stage"]
        confirmed_extreme = (
            state["confirmation"].get("reviewer_reasoning_confirmed") is True
            and state["confirmation"].get("reviewer_reasoning_mode") == "extreme"
            and review.get("request_reasoning_mode") == "extreme"
            and review.get("request_stage") == review.get("current_stage")
            and review.get("response_stage") == review.get("current_stage")
        )
        if args.status == "result_received" and not confirmed_extreme:
            review["status"] = "result_quarantined"
            review["response_valid_for_apply"] = False
            review["response_quarantined_reason"] = "review_mode_or_stage_not_verified"
        elif args.status == "result_received":
            review["response_valid_for_apply"] = True
            review["response_quarantined_reason"] = "none"
        else:
            review["response_valid_for_apply"] = False
            if review.get("response_quarantined_reason") in empty:
                review["response_quarantined_reason"] = "explicit_quarantine"
    if old_status != "external_blocked" or review["status"] != "external_blocked":
        state["recovery"]["user_notified_stall"] = False
    review["last_progress_at"] = utc_now()
    waiting_check_action = "none"
    waiting_check_automation_id = state["automation"].get("waiting_check_automation_id", "none")
    waiting_check_previous_automation_id = "none"
    old_monitored = old_status in MONITOR_STATUSES
    new_monitored = review["status"] in MONITOR_STATUSES
    phase_changed = old_monitored and new_monitored and old_status != review["status"]
    if phase_changed:
        waiting_check_previous_automation_id = state["automation"].get(
            "waiting_check_automation_id", "none"
        )
        deleted_id = getattr(args, "deleted_automation_id", None) or "none"
        if (
            waiting_check_previous_automation_id != "none"
            and deleted_id != waiting_check_previous_automation_id
        ):
            raise LCRLError("phase change requires deletion of the current waiting check")
        deactivate_waiting_check(state)

    if new_monitored and (not old_monitored or phase_changed):
        if state["automation"].get("heartbeat_mode") == "waiting_only":
            state["automation"]["waiting_check_token"] = "wait-" + secrets.token_hex(8)
            state["automation"]["waiting_check_active"] = True
            state["automation"]["waiting_check_automation_id"] = "none"
            state["automation"]["waiting_check_claimed_id"] = "none"
            waiting_check_automation_id = "none"
            waiting_check_action = "schedule_once"
        else:
            deactivate_waiting_check(state)
            waiting_check_action = "foreground_resume_required"
    elif new_monitored:
        waiting_check_action = "keep_once"
    elif old_monitored:
        waiting_check_automation_id = deactivate_waiting_check(state)
        waiting_check_action = "cancel_once"
    release_action_lease_id = getattr(args, "release_action_lease_id", None)
    if release_action_lease_id is not None:
        if state["runtime"].get("action_lease_id") != release_action_lease_id:
            raise LCRLError("action lease changed before the authorized transition")
        browser_rebind_id = getattr(args, "browser_rebind_id", None)
        if browser_rebind_id is not None:
            binding = state["browser_binding"]
            if not (
                state["runtime"].get("action_lease_reason")
                == "browser_submission_reopen"
                and state["runtime"].get(
                    "browser_submission_reopen_browser_id", "none"
                ) == browser_rebind_id
                and review.get("transport") == "in_app_browser"
                and binding.get("status") == "bound"
                and _bound_browser_chat_can_reopen(state)
                and binding.get("conversation_id")
                == state["confirmation"].get("reviewer_thread_id")
            ):
                raise LCRLError("browser rebind is outside the authorized submission reopen")
            binding["browser_id"] = browser_rebind_id
        clear_action_lease(state)
    elif (
        review["status"] in {"local_work", "review_submit_pending", "completed"}
        and state["runtime"].get("action_lease_reason") == "apply_result"
    ):
        # Crossing out of result application is the durable proof that this
        # local apply action finished.  Do not strand the next submission or a
        # terminal state behind an orphaned implementation lease.
        clear_action_lease(state)
    record_resume_checkpoint(state)
    save_state(path, state, expected_revision=revision)
    browser_submission_preflight_required = (
        review["status"] == "review_submit_pending"
        and review.get("transport") == "in_app_browser"
    )
    pending_wait_binding = waiting_check_binding_pending(state)
    continuous_active = (
        review.get("goal_mode") == "continuous"
        and review["status"] in {"local_work", "result_received", "review_submit_pending"}
    )
    continuous_next_action = {
        "local_work": "continue_local_work",
        "result_received": "apply_review_result",
        "review_submit_pending": "submit_review_once",
    }.get(review["status"], "none")
    if pending_wait_binding:
        continuous_next_action = "create_and_bind_waiting_check"
    return add_platform_wait_contract({
        "ok": True,
        "status": review["status"],
        "revision": state["revision"],
        "waiting_check_action": waiting_check_action,
        "waiting_check_token": state["automation"]["waiting_check_token"],
        "waiting_check_automation_id": waiting_check_automation_id,
        "waiting_check_previous_automation_id": waiting_check_previous_automation_id,
        "browser_submission_preflight_required": browser_submission_preflight_required,
        "missing_exact_tab_action": (
            "authorize-browser-submission-reopen"
            if browser_submission_preflight_required else "none"
        ),
        "direct_claim_missing_tab_allowed": False,
        "continuation_required": continuous_active or pending_wait_binding,
        "next_action": continuous_next_action,
        "turn_completion_allowed": not (continuous_active or pending_wait_binding),
    })


def parse_result(text: str) -> dict[str, Any]:
    original_text = text.strip()
    if not original_text:
        raise LCRLError("review result is empty")
    contract_version = "legacy_unmarked"
    if RESULT_BEGIN in text:
        start = text.index(RESULT_BEGIN) + len(RESULT_BEGIN)
        closing_markers = [marker for marker in RESULT_END_ALIASES if marker in text[start:]]
        if not closing_markers:
            raise LCRLError("result envelope is missing its closing marker")
        end = min(text.index(marker, start) for marker in closing_markers)
        text = text[start:end]
        contract_version = "v2"
    elif LEGACY_RESULT_BEGIN in text:
        start = text.index(LEGACY_RESULT_BEGIN) + len(LEGACY_RESULT_BEGIN)
        if LEGACY_RESULT_END not in text[start:]:
            raise LCRLError("legacy result envelope is missing its closing marker")
        end = text.index(LEGACY_RESULT_END, start)
        text = text[start:end]
        contract_version = "v1_legacy"
    try:
        result = json.loads(text.strip())
    except json.JSONDecodeError as exc:
        if contract_version != "legacy_unmarked":
            raise LCRLError(f"review result is not valid JSON: {exc}") from exc
        result = {
            "verdict": "natural_language",
            "findings": [],
            "next_step": original_text,
            "acceptance": [],
        }
        contract_version = "natural_language"
    if contract_version == "legacy_unmarked":
        contract_version = "unmarked_json" if isinstance(result, dict) and isinstance(result.get("operation_package"), dict) else "natural_language"
    if contract_version in {"v2", "unmarked_json"}:
        # Compatibility for V8 prompts that accidentally requested a single
        # top-level `next_operation` object. This is a lossless structural
        # normalization. Canonical fields, when present, always win.
        legacy_next_operation = result.get("next_operation")
        if "operation_package" not in result and isinstance(legacy_next_operation, dict):
            result["operation_package"] = deepcopy(legacy_next_operation)
        if "next_step" not in result and isinstance(legacy_next_operation, dict):
            result["next_step"] = {
                key: deepcopy(legacy_next_operation[key])
                for key in ("id", "stage", "title", "objective")
                if key in legacy_next_operation
            }
        operation = result.get("operation_package")
        if isinstance(operation, dict):
            alias_fields = {
                "ordered_actions": "ordered_operations",
                "interface_constraints": "interfaces",
                "final_tests": "tests",
                "next_round_evidence": "evidence_contract",
            }
            for alias, canonical in alias_fields.items():
                if canonical not in operation and alias in operation:
                    operation[canonical] = operation[alias]
        if "next_step" not in result and isinstance(operation, dict):
            objective = operation.get("objective")
            if isinstance(objective, dict):
                result["next_step"] = objective
        if "acceptance" not in result and "automatic_acceptance" in result:
            result["acceptance"] = result["automatic_acceptance"]
        if result.get("verdict") == "pass" and "findings" not in result:
            result["findings"] = []
    required = {"verdict", "findings", "next_step", "acceptance"}
    if contract_version in {"v2", "v1_legacy", "unmarked_json"}:
        required.add("stage")
    missing = sorted(required - set(result))
    if missing:
        raise LCRLError(f"review result is missing fields: {', '.join(missing)}")
    valid_verdicts = {"pass", "changes_requested", "blocked"}
    if contract_version == "natural_language":
        valid_verdicts.add("natural_language")
    if result["verdict"] not in valid_verdicts:
        raise LCRLError("invalid review verdict")
    if contract_version in {"v2", "unmarked_json"}:
        operation = result.get("operation_package")
        if not isinstance(operation, dict):
            raise LCRLError("V2 result requires operation_package")
        required_operation = {
            "objective", "read_first", "allowed_files", "forbidden_files", "ordered_operations",
            "interfaces", "local_validation", "tests", "failure_branches", "stop_conditions",
            "rollback", "evidence_contract",
        }
        operation_missing = sorted(required_operation - set(operation))
        if operation_missing:
            raise LCRLError(f"operation_package is missing fields: {', '.join(operation_missing)}")
    violations: list[dict[str, str]] = []
    for field in ("next_step", "forbidden", "acceptance", "operation_package"):
        value = result.get(field, "")
        rendered = canonical_json(value) if not isinstance(value, str) else value
        matched = sorted({pattern.pattern for pattern in POLICY_PATTERNS if pattern.search(rendered)})
        if matched:
            violations.append({"field": field, "patterns": ", ".join(matched)})
    return {
        "ok": True,
        "accepted": True,
        "result": result,
        "result_hash": fingerprint(result),
        "contract_version": contract_version,
        "ignored_meta_directives": violations,
        "policy_firewall": "clean" if not violations else "filtered",
    }


def validate_result_command(args: argparse.Namespace) -> dict[str, Any]:
    sources = [bool(args.result_file), bool(args.result_json), bool(args.result_base64)]
    if sum(sources) != 1:
        raise LCRLError("provide exactly one result source")
    if args.result_file:
        text = Path(args.result_file).read_text(encoding="utf-8")
    elif args.result_base64:
        text = base64.b64decode(args.result_base64).decode("utf-8")
    else:
        text = args.result_json
    parsed = parse_result(text)
    state_argument = getattr(args, "state", None)
    if not state_argument:
        return parsed
    if parsed["contract_version"] not in {"v2", "unmarked_json", "natural_language"}:
        raise LCRLError("only a complete structured or natural-language result can be persisted for apply")
    if parsed["policy_firewall"] != "clean":
        raise LCRLError("operation package contains policy directives and cannot be persisted for apply")
    state_path = Path(state_argument).expanduser().resolve()
    state = load_state(state_path)
    revision = state["revision"]
    review = state["review"]
    if review.get("status") != "result_received":
        raise LCRLError("persisting an operation package requires status=result_received")
    if (
        parsed["contract_version"] in {"v2", "unmarked_json"}
        and parsed["result"].get("stage") != review.get("current_stage")
    ):
        raise LCRLError("operation package stage must match the current reviewed stage")
    response_message_id = review.get("response_message_id")
    if response_message_id in (None, "", "none"):
        raise LCRLError("operation package persistence requires a real response message id")
    next_step = parsed["result"].get("next_step")
    if parsed["contract_version"] == "natural_language":
        next_stage = review["current_stage"]
        action_scope = natural_language_action_scope(str(next_step))
        operation_package = {
            "format": "natural_language",
            "review_text": next_step,
            "action_scope": action_scope,
            "instruction": (
                "Implement only action_scope while retaining review_text as context. Continue immediately "
                "when the intent is clear; deferred high-impact mentions are not authorization; "
                "otherwise stop for the user only when the reply is ambiguous, conflicts with the project, "
                "or requires a destructive, release, payment, permission, or direction-changing decision."
            ),
        }
    elif isinstance(next_step, dict):
        next_stage = str(next_step.get("id") or next_step.get("stage") or next_step.get("title") or "next")
        operation_package = parsed["result"]["operation_package"]
    else:
        next_stage = "next"
        operation_package = parsed["result"]["operation_package"]
    safe_stage = re.sub(r"[^A-Za-z0-9._-]+", "-", next_stage).strip("-.") or "next"
    persisted = {
        "schema_version": 1,
        "source": {
            "automation_id": state["automation"]["id"],
            "reviewer_thread_id": state["confirmation"]["reviewer_thread_id"],
            "response_message_id": response_message_id,
            "reviewed_stage": review["current_stage"],
            "reasoning_mode": review["request_reasoning_mode"],
            "result_hash": parsed["result_hash"],
            "validated_at": utc_now(),
        },
        "verdict": parsed["result"]["verdict"],
        "next_step": next_step,
        "acceptance": parsed["result"].get("acceptance", []),
        "operation_package": operation_package,
    }
    payload = json.dumps(persisted, ensure_ascii=False, indent=2) + "\n"
    operation_sha256 = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    operation_root = state_path.parent / "operations"
    operation_root.mkdir(parents=True, exist_ok=True)
    operation_path = operation_root / f"{state['automation']['id']}-{safe_stage}-{operation_sha256[:16]}.json"
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{operation_path.name}.", suffix=".tmp", dir=operation_root)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, operation_path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    state["next_operation"] = {
        "status": "validated",
        "path": str(operation_path),
        "sha256": operation_sha256,
        "source_response_message_id": response_message_id,
        "source_stage": review["current_stage"],
        "next_stage": next_stage,
        "result_hash": parsed["result_hash"],
        "validated_at": persisted["source"]["validated_at"],
        "applied_at": "none",
    }
    save_state(state_path, state, expected_revision=revision)
    parsed.update({
        "operation_path": str(operation_path),
        "operation_sha256": operation_sha256,
        "next_stage": next_stage,
        "revision": state["revision"],
    })
    return parsed


def response_already_consumed(state: dict[str, Any], response_message_id: str) -> bool:
    """Return whether this App Chat response was already handed to Work."""
    if state["review"].get("response_message_id") == response_message_id:
        return True
    if state.get("next_operation", {}).get("source_response_message_id") == response_message_id:
        return True
    return any(item.get("response_message_id") == response_message_id for item in state.get("review_history", []))


def parse_model_route_advice(text: str, parsed: dict[str, Any]) -> dict[str, str]:
    """Parse one explicit final routing block; ordinary model words are ignored."""
    default = {
        "requested": "medium", "verdict": "none", "blocker_id": "none",
        "signal": "none", "high_attempt_id": "none", "evidence": "none",
        "scope": "none", "exit_criteria": "none", "syntax": "absent",
        "reason": "no_valid_escalation_advice",
    }
    structured = parsed.get("result", {}).get("model_route")
    fields: dict[str, str]
    if isinstance(structured, dict):
        fields = {str(key).upper(): str(value).strip() for key, value in structured.items()}
    else:
        if text.count(MODEL_ROUTE_BEGIN) != 1 or text.count(MODEL_ROUTE_END) != 1:
            return default
        match = re.search(
            re.escape(MODEL_ROUTE_BEGIN) + r"\s*(.*?)\s*" + re.escape(MODEL_ROUTE_END) + r"\s*$",
            text,
            re.DOTALL,
        )
        if not match:
            return {**default, "syntax": "invalid", "reason": "routing_block_must_be_unique_and_final"}
        fields = {}
        for raw_line in match.group(1).splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if ":" not in line:
                return {**default, "syntax": "invalid", "reason": "routing_block_contains_invalid_line"}
            key, value = line.split(":", 1)
            key = key.strip().upper()
            if key in fields:
                return {**default, "syntax": "invalid", "reason": "routing_block_contains_duplicate_field"}
            fields[key] = value.strip()
    route_map = {"MEDIUM": "medium", "HIGH_ONCE": "high_once", "TERRA_REQUEST": "terra_request"}
    requested = route_map.get(fields.get("MODEL_ROUTE", ""))
    if requested is None:
        return {**default, "syntax": "invalid", "reason": "invalid_model_route"}
    verdict = fields.get("VERDICT", "").upper()
    if verdict not in {"PASS", "REVISE", "BLOCKED"}:
        return {**default, "syntax": "invalid", "reason": "routing_block_requires_verdict"}
    advice = {
        **default,
        "requested": requested,
        "verdict": verdict.lower(),
        "syntax": "valid",
        "reason": "parsed",
    }
    key_map = {
        "BLOCKER_ID": "blocker_id", "SIGNAL": "signal", "HIGH_ATTEMPT": "high_attempt_id",
        "EVIDENCE": "evidence", "SCOPE": "scope", "EXIT_CRITERIA": "exit_criteria",
    }
    for source, target in key_map.items():
        if fields.get(source):
            advice[target] = title_component(fields[source], source.lower(), 240)
    if requested != "medium":
        required = {"blocker_id", "signal", "evidence", "scope", "exit_criteria"}
        if requested == "terra_request":
            required.add("high_attempt_id")
        missing = sorted(field for field in required if advice[field] == "none")
        if missing:
            return {**default, "requested": requested, "syntax": "invalid", "reason": "missing_" + "_".join(missing)}
    return advice


def assess_model_route_advice(
    state: dict[str, Any], text: str, parsed: dict[str, Any], response_message_id: str,
) -> dict[str, Any]:
    advice = parse_model_route_advice(text, parsed)
    requested = advice["requested"]
    effective = "medium"
    status = "default" if advice["syntax"] == "absent" else "rejected"
    reason = advice["reason"]
    routing = state["model_policy"]["routing"]
    step_index = routing["meaningful_step_index"]
    if advice["syntax"] == "valid" and requested == "medium":
        status, reason = "accepted", "chat_recommended_normal_execution"
    elif advice["syntax"] == "valid" and advice["verdict"] == "pass":
        reason = "pass_cannot_escalate"
    elif advice["syntax"] == "valid" and requested == "high_once":
        if advice["signal"] not in VALID_HIGH_SIGNALS:
            reason = "high_signal_not_allowed"
        else:
            recent = [
                item for item in routing["high_attempts"]
                if item["meaningful_step_index"] > step_index - 10
            ]
            if len(recent) >= HIGH_MAX_LAST_10_STEPS:
                reason = "high_two_of_ten_ceiling_reached"
            else:
                effective, status, reason = "high_once", "accepted", "evidence_backed_high_once"
    elif advice["syntax"] == "valid" and requested == "terra_request":
        if advice["signal"] not in VALID_TERRA_SIGNALS:
            reason = "terra_signal_not_allowed"
        else:
            high = next(
                (item for item in routing["high_attempts"] if item["attempt_id"] == advice["high_attempt_id"]),
                None,
            )
            recent_terra = [
                item for item in routing["terra_turns"]
                if item["meaningful_step_index"] > step_index - 20
            ]
            if high is None or high["blocker_id"] != advice["blocker_id"]:
                reason = "terra_requires_matching_high_attempt"
            elif high.get("execution_status") != "verified":
                reason = "terra_requires_verified_high_execution"
            elif len(recent_terra) >= TERRA_MAX_LAST_20_STEPS:
                reason = "terra_one_of_twenty_ceiling_reached"
            else:
                effective, status, reason = "terra_request", "accepted", "terra_eligible_for_user_confirmation"
    return {
        "requested": requested,
        "effective": effective,
        "status": status,
        "reason": reason,
        **default_execution_fact(),
        "response_message_id": response_message_id,
        "blocker_id": advice["blocker_id"],
        "signal": advice["signal"],
        "high_attempt_id": advice["high_attempt_id"],
        "evidence": advice["evidence"],
        "scope": advice["scope"],
        "exit_criteria": advice["exit_criteria"],
        "recorded_at": utc_now(),
    }


def persist_model_route_advice(path: Path, advice: dict[str, Any]) -> None:
    state = load_state(path)
    revision = state["revision"]
    state["model_policy"]["routing"]["advice"] = advice
    save_state(path, state, expected_revision=revision)


def reply_requires_user_decision(parsed: dict[str, Any]) -> bool:
    """Keep clearly unsafe or merely congratulatory prose out of auto-continue."""
    if parsed["policy_firewall"] != "clean":
        return True
    if parsed["contract_version"] != "natural_language":
        return False
    reply = str(parsed["result"].get("next_step", "")).strip()
    action_scope = natural_language_action_scope(reply)
    return bool(
        _action_scope_requires_high_impact_decision(action_scope)
        or VAGUE_REPLY_PATTERN.fullmatch(reply)
    )


def _action_scope_requires_high_impact_decision(action_scope: str) -> bool:
    """Distinguish a local counterexample mutation from a real destructive act."""
    if OTHER_HIGH_IMPACT_REPLY_PATTERN.search(action_scope):
        return True
    if not DESTRUCTIVE_REPLY_PATTERN.search(action_scope):
        return False
    local_counterexample = (
        LOCAL_COUNTEREXAMPLE_MUTATION_PATTERN.search(action_scope)
        or (
            REJECTED_MUTATION_ASSERTION_PATTERN.search(action_scope)
            and DATABASE_ROW_CONTEXT_PATTERN.search(action_scope)
        )
    )
    external_target = EXTERNAL_DESTRUCTIVE_TARGET_PATTERN.search(action_scope)
    return not (local_counterexample and not external_target)


def natural_language_action_scope(reply: str) -> str:
    """Return the explicit current action without deferred release-scope notes.

    Natural-language reviews remain preserved in full.  This narrower view is
    used only by the high-impact gate and the operation handoff when the reviewer
    labels one concrete next-step section.  A real high-impact instruction inside
    that section is still blocked; only lines that explicitly defer remaining
    work to a later handoff are excluded.
    """
    match = EXPLICIT_NEXT_STEP_HEADING_PATTERN.search(reply)
    if match is None:
        stop_match = EXPLICIT_STOP_ACTION_PATTERN.search(reply)
        return stop_match.group(0).strip() if stop_match is not None else reply
    scope = reply[match.start():].split("[SUPERLUNA_MODEL_ROUTE]", 1)[0]
    kept = [
        line for line in scope.splitlines()
        if not DEFERRED_SCOPE_LINE_PATTERN.search(line)
    ]
    return "\n".join(kept).strip()


def _already_consumed_result(state: dict[str, Any], response_message_id: str) -> dict[str, Any]:
    return add_user_status_exit({
        "ok": True, "action": "already_consumed", "consumed": False,
        "status": state["review"]["status"],
        "response_message_id": response_message_id, "lease_id": "none",
    })


def resume_from_reply_command(args: argparse.Namespace) -> dict[str, Any]:
    """Consume one App Chat reply and hand it to the bound Work once.

    Concurrent resume-from-reply on the same response_message_id yields exactly
    one consumption. The loser reloads after a revision conflict and returns
    already_consumed without a second operation package or action lease.
    """
    sources = [bool(args.result_file), bool(args.result_json), bool(args.result_base64)]
    if sum(sources) != 1:
        raise LCRLError("provide exactly one reply source")
    if args.result_file:
        text = Path(args.result_file).read_text(encoding="utf-8")
    elif args.result_base64:
        text = base64.b64decode(args.result_base64).decode("utf-8")
    else:
        text = args.result_json
    parsed = parse_result(text)
    path = Path(args.state).expanduser().resolve()
    response_message_id = args.response_message_id
    last_conflict: Exception | None = None
    # One automatic retry after a lost race covers the common two-process case.
    for _attempt in range(2):
        state = load_state(path)
        review = state["review"]
        if response_already_consumed(state, response_message_id):
            return _already_consumed_result(state, response_message_id)
        source = getattr(args, "source", "foreground")
        resumed_waiting_automation_id = "none"
        if source == "waiting_check":
            deleted_id = getattr(args, "deleted_automation_id", None)
            current_id = state["automation"].get("waiting_check_automation_id", "none")
            claimed_id = state["automation"].get("waiting_check_claimed_id", "none")
            if current_id == "none" or claimed_id != current_id or deleted_id != current_id:
                raise LCRLError("scheduled reply resume requires proof that its current one-shot was deleted")
            resumed_waiting_automation_id = current_id
        if review["status"] != "review_waiting":
            # Peer may have just consumed; treat as already_consumed when applicable.
            if response_already_consumed(state, response_message_id):
                return _already_consumed_result(state, response_message_id)
            raise LCRLError("foreground resume requires status=review_waiting and a new App Chat reply")
        if response_message_id == review.get("request_message_id"):
            raise LCRLError("response message id must differ from the review request")
        if not (
            state["confirmation"].get("reviewer_reasoning_confirmed") is True
            and state["confirmation"].get("reviewer_reasoning_mode") == "extreme"
            and review.get("request_reasoning_mode") == "extreme"
        ):
            raise LCRLError("foreground resume requires the bound App Chat to be confirmed Extreme")

        now = args.response_completed_at or utc_now()
        try:
            if reply_requires_user_decision(parsed):
                revision = state["revision"]
                quarantine_reason = f"{source}_reply_requires_user_decision"
                review.update({
                    "status": "external_blocked",
                    "response_turn_id": args.response_turn_id,
                    "response_message_id": response_message_id,
                    "response_completed_at": now,
                    "response_complete": True,
                    "response_envelope_hash": parsed["result_hash"],
                    "response_stage": review["current_stage"],
                    "response_valid_for_apply": False,
                    "response_quarantined_reason": quarantine_reason,
                    "recovery_action": quarantine_reason,
                    "last_progress_at": utc_now(),
                })
                cancelled_id = deactivate_waiting_check(state)
                save_state(path, state, expected_revision=revision)
                return add_user_status_exit({
                    "ok": True, "action": "needs_user_decision", "consumed": True,
                    "status": "external_blocked",
                    "response_message_id": response_message_id, "lease_id": "none", "source": source,
                    "waiting_check_action": "already_deleted" if source == "waiting_check" else "cancel_once",
                    "waiting_check_automation_id": cancelled_id,
                })

            model_route = assess_model_route_advice(state, text, parsed, response_message_id)
            transition(argparse.Namespace(
                state=str(path), status="result_received", stage=None, payload_mode=None, fingerprint=None,
                waiting_since=None, request_turn_id=None, request_message_id=None, request_persisted_at=None,
                request_stage=None, request_reasoning_mode=None, response_turn_id=args.response_turn_id,
                response_message_id=response_message_id, response_completed_at=now, response_complete="true",
                response_envelope_hash=parsed["result_hash"], response_stage=None, artifacts_summary=None,
                recovery_action="foreground_reply_consumed", attachment_send=None, filesystem_read=None,
                quarantine_unconfirmed=False, recovery_override=False,
            ))
            persist_model_route_advice(path, model_route)
            validated = validate_result_command(argparse.Namespace(
                state=str(path), result_file=args.result_file, result_json=args.result_json,
                result_base64=args.result_base64,
            ))
            action = tick(path, source="foreground")
            return add_user_status_exit({
                "ok": True, "action": action["action"], "consumed": True,
                "status": action["status"],
                "response_message_id": response_message_id, "lease_id": action["lease_id"],
                "operation_path": validated["operation_path"],
                "model_route": model_route["effective"],
                "model_route_status": model_route["status"],
                "model_route_reason": model_route["reason"],
                "source": source,
                "waiting_check_action": "already_deleted" if source == "waiting_check" else "cancel_once",
                "waiting_check_automation_id": resumed_waiting_automation_id,
            })
        except (StateRevisionConflict, StateLockTimeout) as exc:
            last_conflict = exc
            latest = load_state(path)
            if response_already_consumed(latest, response_message_id):
                return _already_consumed_result(latest, response_message_id)
            continue
        except LCRLError:
            # Peer may have already left review_waiting after consuming the same reply
            # (illegal transition / validation race). Prefer deterministic already_consumed.
            latest = load_state(path)
            if response_already_consumed(latest, response_message_id):
                return _already_consumed_result(latest, response_message_id)
            raise
    if last_conflict is not None:
        latest = load_state(path)
        if response_already_consumed(latest, response_message_id):
            return _already_consumed_result(latest, response_message_id)
        raise last_conflict
    raise LCRLError("resume-from-reply could not claim a unique consumption")


def doctor(state_path: str | Path, automation_toml: str | None = None, registry_path: str | None = None) -> dict[str, Any]:
    path = Path(state_path).resolve()
    findings: list[dict[str, str]] = []
    try:
        state = load_state(path)
    except LCRLError as exc:
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
            apply_state_defaults(state)
        except (OSError, json.JSONDecodeError) as raw_exc:
            return {
                "ok": False,
                "state": str(path),
                "revision": 0,
                "heartbeat_bytes": 0,
                "session_log": "missing",
                "network": "unknown",
                "network_error_count": 0,
                "findings": [{"severity": "error", "code": "state_unreadable", "detail": str(raw_exc)}],
            }
        findings.append({"severity": "error", "code": "state_invariant_violation", "detail": str(exc)})
    log = runtime_log_path(state)
    if not log:
        findings.append({"severity": "warning", "code": "session_log_missing"})
    if state["review"]["payload_mode"] == "app_attachment":
        if state["capabilities"]["attachment_send"] not in {"native", "manual"}:
            findings.append({"severity": "error", "code": "attachment_transport_unavailable"})
        if state.get("attachment", {}).get("verification") not in {"verified", "manual_confirmed"}:
            findings.append({"severity": "error", "code": "attachment_not_verified"})
    if state["review"]["status"] == "review_submit_pending" and not (
        state["confirmation"].get("reviewer_reasoning_confirmed") is True
        and state["confirmation"].get("reviewer_reasoning_mode") == "extreme"
    ):
        findings.append({"severity": "error", "code": "reviewer_extreme_mode_unconfirmed"})
    if state["review"]["status"] == "review_waiting" and state["review"].get("request_reasoning_mode") != "extreme":
        findings.append({"severity": "error", "code": "review_request_not_extreme"})
    if state["review"]["status"] == "result_quarantined":
        findings.append({"severity": "error", "code": "review_result_quarantined"})
    if state["review"]["status"] == "external_blocked" and state["recovery"].get("user_notified_stall") is True:
        findings.append({"severity": "info", "code": "external_blocker_already_notified"})
    if state["automation"].get("heartbeat_mode") == "legacy_fixed":
        findings.append({"severity": "warning", "code": "recurring_monitor_must_be_retired"})
    model_policy = state["model_policy"]
    pro = model_policy["pro"]
    terra = model_policy["terra"]
    routing = model_policy["routing"]
    unverified_high_attempts = [
        item["attempt_id"] for item in routing["high_attempts"]
        if item["execution_status"] != "verified"
    ]
    if pro["status"] == "eligible":
        findings.append({"severity": "info", "code": "pro_milestone_eligible"})
    elif pro["status"] == "confirmation_required":
        findings.append({"severity": "warning", "code": "pro_waiting_for_user_confirmation"})
    elif pro["status"] == "in_review":
        findings.append({"severity": "info", "code": "pro_review_active"})
    if terra["status"] == "requested":
        findings.append({"severity": "warning", "code": "terra_waiting_for_confirmation"})
    elif terra["status"] == "approved":
        findings.append({"severity": "info", "code": "terra_one_turn_approved"})
        if terra["execution_status"] != "verified":
            findings.append({"severity": "info", "code": "terra_execution_unverified"})
    if unverified_high_attempts:
        findings.append({"severity": "info", "code": "high_execution_unverified"})
    binding = state.get("binding", {})
    effective_registry = registry_path or (binding.get("registry_path") if binding.get("status") == "bound" else None)
    if binding.get("status") != "bound":
        findings.append({"severity": "warning", "code": "task_binding_not_registered"})
    elif effective_registry:
        try:
            task_registry = load_binding_registry(effective_registry)
            matches = [task for task in task_registry["tasks"] if task.get("task_id") == binding.get("task_id")]
            if len(matches) != 1:
                findings.append({"severity": "error", "code": "task_binding_registry_mismatch"})
            else:
                entry = matches[0]
                identity = {
                    "implementation_thread_id": state["automation"]["implementation_thread_id"],
                    "reviewer_thread_id": state["confirmation"]["reviewer_thread_id"],
                    "automation_id": state["automation"]["id"],
                }
                if any(entry.get(key) != value for key, value in identity.items()):
                    findings.append({"severity": "error", "code": "task_binding_identity_mismatch"})
                expected = build_binding_titles(
                    binding["display_name"], binding["iteration"], binding["work_status_label"],
                    binding.get("naming_template_version", 1),
                )
                recorded = {
                    "work": binding.get("expected_work_title"),
                    "chat": binding.get("expected_chat_title"),
                    "automation": binding.get("expected_automation_title"),
                }
                if recorded != expected or entry.get("titles") != expected:
                    findings.append({"severity": "error", "code": "task_binding_title_drift"})
        except LCRLError as exc:
            findings.append({"severity": "error", "code": "task_binding_registry_invalid", "detail": str(exc)})
    try:
        heartbeat = render_heartbeat(path)
    except LCRLError:
        heartbeat = ""
    if automation_toml:
        config = read_toml(Path(automation_toml).resolve())
        prompt = str(config.get("prompt", ""))
        if "[LCRL_HEARTBEAT_V8_P0_BEGIN]" not in prompt:
            findings.append({"severity": "error", "code": "automation_not_v8_p0"})
        if str(config.get("status", "")).upper() == "ACTIVE":
            findings.append({"severity": "error", "code": "recurring_automation_still_active"})
    return {
        "ok": not any(item["severity"] == "error" for item in findings),
        "state": str(path),
        "revision": state["revision"],
        "heartbeat_bytes": len(heartbeat.encode("utf-8")),
        "session_log": str(log) if log else "missing",
        "network": state["recovery"]["network_state"],
        "network_error_count": state["recovery"]["network_error_count"],
        "binding": state.get("binding", {}),
        "model_policy": {
            "executor": model_policy["executor"]["current"],
            "reviewer": model_policy["reviewer"]["current"],
            "pro_status": pro["status"],
            "terra_status": terra["status"],
            "terra_execution_status": terra["execution_status"],
            "terra_execution_verification_type": terra["execution_verification_type"],
            "terra_execution_source": terra["execution_source"],
            "chat_advice_execution_status": routing["advice"]["execution_status"],
            "unverified_high_attempt_ids": unverified_high_attempts,
            "active_minutes_since_pro": model_policy["progress"]["active_minutes_since_pro"],
            "meaningful_steps_since_pro": model_policy["progress"]["meaningful_steps_since_pro"],
        },
        "findings": findings,
    }


def audit(args: argparse.Namespace) -> dict[str, Any]:
    state = load_state(args.state)
    automation_root = Path(args.automation_root).resolve()
    candidates = list(automation_root.rglob("automation.toml"))
    if args.automation_id:
        candidates = [item for item in candidates if item.parent.name == args.automation_id]
    target = None
    active_for_thread = 0
    for candidate in candidates:
        config = read_toml(candidate)
        configured_thread = str(config.get("target_thread_id") or config.get("thread_id") or "")
        if str(config.get("status", "")).upper() == "ACTIVE" and configured_thread == state["automation"]["implementation_thread_id"]:
            active_for_thread += 1
        if candidate.parent.name == state["automation"]["id"] or str(config.get("id", "")) == state["automation"]["id"]:
            target = (candidate, config)
    findings = []
    if target:
        candidate, config = target
        prompt = str(config.get("prompt", ""))
        if "[LCRL_HEARTBEAT_V8_P0_BEGIN]" not in prompt or "[LCRL_HEARTBEAT_V8_P0_END]" not in prompt:
            findings.append("heartbeat_markers_missing")
        if len(prompt.encode("utf-8")) > MAX_HEARTBEAT_BYTES:
            findings.append("heartbeat_too_large")
        automation_active = str(config.get("status", "")).upper() == "ACTIVE"
        if automation_active:
            findings.append("recurring_automation_still_active")
        configured_thread = str(config.get("target_thread_id") or config.get("thread_id") or "")
        if configured_thread != state["automation"]["implementation_thread_id"]:
            findings.append("target_thread_mismatch")
    if active_for_thread > 0:
        findings.append("active_recurring_automation_for_thread")
    routing = state["model_policy"]["routing"]
    return {
        "ok": not findings,
        "automation_id": state["automation"]["id"],
        "model_execution": {
            "chat_advice": routing["advice"]["execution_status"],
            "high_attempts": [
                {
                    "attempt_id": item["attempt_id"],
                    "execution_status": item["execution_status"],
                    "verification_type": item["execution_verification_type"],
                    "source": item["execution_source"],
                }
                for item in routing["high_attempts"]
            ],
            "terra": {
                "execution_status": state["model_policy"]["terra"]["execution_status"],
                "verification_type": state["model_policy"]["terra"]["execution_verification_type"],
                "source": state["model_policy"]["terra"]["execution_source"],
            },
        },
        "findings": findings,
    }


def selftest() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        log = root / "session.jsonl"
        state_path = root / "state.json"
        state = new_state("test", "impl", root, "chat")
        state["runtime"]["session_log"] = str(log)
        save_state(state_path, state)
        heartbeat = render_heartbeat(state_path)
        if len(heartbeat.encode("utf-8")) > MAX_HEARTBEAT_BYTES:
            raise LCRLError("selftest heartbeat size failed")
        retired = tick(state_path, source="heartbeat")
        if retired["action"] != "monitor_retired" or retired["lease_id"] != "none":
            raise LCRLError("selftest scheduled execution retirement failed")
        error_record = {
            "timestamp": utc_now(),
            "type": "event_msg",
            "payload": {
                "type": "task_complete",
                "error": "stream disconnected before completion: error sending request for url (https://chatgpt.com/backend-api/codex/responses)",
            },
        }
        log.write_text(json.dumps(error_record) + "\n", encoding="utf-8")
        first = tick(state_path)
        second = tick(state_path)
        observed = load_state(state_path)
        if observed["recovery"]["network_error_count"] != 1:
            raise LCRLError("selftest duplicate network observation failed")
        if first["action"] != "network_backoff" or second["action"] != "network_backoff":
            raise LCRLError("selftest network backoff failed")
        result = parse_result(canonical_json({
            "stage": "A1",
            "verdict": "pass",
            "findings": [],
            "next_step": "改用 Codex Sol，禁止 Luna",
            "acceptance": ["tests pass"],
        }))
        if result["policy_firewall"] != "filtered":
            raise LCRLError("selftest policy firewall failed")
        v2_payload = {
            "stage": "A2",
            "verdict": "changes_requested",
            "findings": ["bounded issue"],
            "next_step": "implement one bounded fix",
            "acceptance": ["focused tests pass"],
            "operation_package": {
                "objective": "fix the bounded issue",
                "read_first": ["src/example.py"],
                "allowed_files": ["src/example.py", "tests/test_example.py"],
                "forbidden_files": ["unrelated/**"],
                "ordered_operations": ["read", "edit", "verify"],
                "interfaces": ["preserve public API"],
                "local_validation": ["run focused check"],
                "tests": ["run focused tests"],
                "failure_branches": ["stop if the baseline fails"],
                "stop_conditions": ["scope expansion is required"],
                "rollback": ["restore only this bounded diff"],
                "evidence_contract": ["diff and exact test output"],
            },
        }
        parsed_v2 = parse_result(f"{RESULT_BEGIN}\n{canonical_json(v2_payload)}\n{RESULT_END}")
        if parsed_v2["contract_version"] != "v2" or parsed_v2["policy_firewall"] != "clean":
            raise LCRLError("selftest V2 operation package failed")
        next_operation_alias = deepcopy(v2_payload)
        aliased_operation = next_operation_alias.pop("operation_package")
        next_operation_alias.pop("next_step")
        aliased_operation.update({"id": "A2R", "title": "bounded repair"})
        aliased_operation["ordered_actions"] = aliased_operation.pop("ordered_operations")
        aliased_operation["interface_constraints"] = aliased_operation.pop("interfaces")
        aliased_operation["final_tests"] = aliased_operation.pop("tests")
        aliased_operation["next_round_evidence"] = aliased_operation.pop("evidence_contract")
        next_operation_alias["next_operation"] = aliased_operation
        parsed_alias = parse_result(
            f"{RESULT_BEGIN}\n{canonical_json(next_operation_alias)}\n{RESULT_END}"
        )
        if parsed_alias["result"]["next_step"].get("id") != "A2R":
            raise LCRLError("selftest next_operation next_step normalization failed")
        if parsed_alias["result"]["operation_package"].get("ordered_operations") != ["read", "edit", "verify"]:
            raise LCRLError("selftest next_operation operation package normalization failed")
        gated = new_state("gate", "impl", root, "chat")
        gated["review"]["status"] = "review_submit_pending"
        if choose_action(gated) != "review_mode_blocked":
            raise LCRLError("selftest extreme review gate failed")
        if "review_waiting" in ALLOWED_TRANSITIONS["local_work"]:
            raise LCRLError("selftest illegal stage skip failed")
        blocked_path = root / "blocked.json"
        blocked = new_state("blocked", "impl", root, "chat")
        blocked["review"]["status"] = "external_blocked"
        save_state(blocked_path, blocked)
        if tick(blocked_path)["action"] != "external_blocked_notify":
            raise LCRLError("selftest first blocker notification failed")
        if tick(blocked_path)["action"] != "external_blocked_wait":
            raise LCRLError("selftest duplicate blocker suppression failed")
        attachment = new_state("attachment", "impl-attachment", root, "chat-attachment")
        attachment["review"]["status"] = "review_submit_pending"
        attachment["review"]["cycle_id"] = "cycle-attachment"
        attachment["review"]["submission_fingerprint"] = "attachment-fingerprint"
        attachment["review"]["payload_mode"] = "app_attachment"
        attachment["attachment"] = {
            "required": True,
            "verification": "unverified",
            "expected_names": ["evidence.zip"],
            "observed_names": [],
            "verified_at": "none",
        }
        if choose_action(attachment) != "attachment_verification_blocked":
            raise LCRLError("selftest attachment verification gate failed")
        receipt = new_state("receipt", "impl-receipt", root, "chat-receipt")
        receipt["confirmation"].update({
            "reviewer_reasoning_mode": "extreme",
            "reviewer_reasoning_confirmed": True,
            "reviewer_reasoning_confirmed_at": utc_now(),
            "reviewer_reasoning_control_source": "user",
            "reviewer_reasoning_observed_label": "极高",
            "reviewer_reasoning_observed_thread_id": "chat-receipt",
        })
        receipt["review"].update({
            "status": "review_receipt_pending",
            "cycle_id": "cycle-receipt",
            "current_stage": "R1",
            "request_stage": "R1",
            "request_reasoning_mode": "extreme",
            "submission_fingerprint": "receipt-fingerprint",
            "waiting_since": utc_now(),
        })
        validate_state(receipt)
        if choose_action(receipt) != "review_receipt_reconcile":
            raise LCRLError("selftest review receipt reconciliation failed")
        aborted_path = root / "aborted.json"
        aborted_log = root / "aborted.jsonl"
        aborted = new_state("aborted", "impl-aborted", root, "chat-aborted")
        aborted["runtime"]["session_log"] = str(aborted_log)
        stale_lease = claim_action_lease(aborted, "apply_result", minutes=20)
        save_state(aborted_path, aborted)
        aborted_log.write_text(canonical_json({
            "timestamp": utc_now(),
            "type": "event_msg",
            "payload": {"type": "turn_aborted", "reason": "interrupted"},
        }) + "\n", encoding="utf-8")
        recovered = tick(aborted_path)
        if recovered["action"] == "concurrent_backoff" or recovered["lease_id"] == stale_lease:
            raise LCRLError("selftest interrupted action lease recovery failed")
        titles = build_binding_titles("主线代码", "A36", "评审准备")
        if titles["work"] != "🛠 主线代码｜执行｜A36":
            raise LCRLError("selftest readable title generation failed")
        registry_value = empty_binding_registry()
        registry_value["tasks"] = [{
            "task_id": "main",
            "display_name": "主线代码",
            "implementation_thread_id": "impl-main",
            "reviewer_thread_id": "chat-main",
            "automation_id": "watch-main",
            "iteration": "A36",
            "work_status_label": "评审准备",
            "titles": titles,
            "naming_template_version": NAMING_TEMPLATE_VERSION,
            "updated_at": utc_now(),
        }]
        validate_binding_registry(registry_value)
        model_policy = default_model_policy()
        if model_policy["automatic_model_switch"] or model_policy["automatic_thread_creation"]:
            raise LCRLError("selftest model automation safety defaults failed")
        model_policy["progress"].update({
            "active_minutes_since_pro": PRO_THRESHOLD_ACTIVE_MINUTES,
            "meaningful_steps_since_pro": PRO_MINIMUM_MEANINGFUL_STEPS,
        })
        if not pro_is_eligible(model_policy):
            raise LCRLError("selftest Pro eligibility calculation failed")
    return {"ok": True, "tests": 15, "controller_version": CONTROLLER_VERSION}


def closure_check() -> dict[str, Any]:
    """Summarize local controller coverage without claiming a release gate."""
    selftest()
    checks = {
        "主任务自主提交、等待、读取和继续": "not_run_by_closure_check",
        "四个中断位置恢复": "not_run_by_closure_check",
        "防重复提交、读取和应用": "not_run_by_closure_check",
        "退役后台入口无副作用": "not_run_by_closure_check",
        "等待检查排队补跑零副作用": "not_run_by_closure_check",
    }
    return {
        "ok": True,
        "result": "控制器内置 selftest 通过；仓库测试未执行",
        "scope": "local_controller_only",
        "executed_checks": ["controller_selftest"],
        "repository_tests_run": False,
        "repository_tests_passed": None,
        "real_device_gate_passed": False,
        "public_beta_gate_passed": False,
        "checks": checks,
        "user_status": "正在开发",
        "user_message": "控制器内置 selftest 通过；仓库测试、真实设备与公开 Beta 发布门均未由本命令验证。",
        "user_next_choice": "另行运行仓库测试，并继续完成真实设备和发布证据验证。",
    }


def output(value: Any) -> None:
    if isinstance(value, str):
        print(value)
    else:
        # Keep deterministic CLI output safe on Windows consoles whose active
        # code page cannot encode the optional title emoji.
        print(json.dumps(value, ensure_ascii=True, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lcrl", description="SuperLuna controller (LCRL compatibility CLI)")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("--state", required=True)
    init.add_argument("--automation-id", default="none")
    init.add_argument("--implementation-thread-id", required=True)
    init.add_argument("--project-path", required=True)
    init.add_argument("--reviewer-thread-id", required=True)
    init.add_argument("--profile", default="generic")
    init.add_argument(
        "--implementation-role", choices=sorted(VALID_IMPLEMENTATION_ROLES),
        default="luna_medium",
    )
    init.add_argument("--codex-root")
    init.add_argument(
        "--continuation-mode", choices=sorted(VALID_COORDINATION_MODES), required=True
    )
    init.add_argument(
        "--review-transport", choices=sorted(VALID_REVIEW_TRANSPORTS),
        default="in_app_browser",
    )
    init.add_argument(
        "--goal-mode", choices=sorted(VALID_GOAL_MODES), default="continuous"
    )

    migrate = sub.add_parser("migrate-v6")
    migrate.add_argument("--automation-toml", required=True)
    migrate.add_argument("--state-output", required=True)
    migrate.add_argument("--automation-id")
    migrate.add_argument("--profile", default="generic")
    migrate.add_argument("--codex-root")

    heartbeat = sub.add_parser("render-heartbeat")
    heartbeat.add_argument("--state", required=True)
    heartbeat.add_argument("--validate-only", action="store_true")

    tick_parser = sub.add_parser("tick")
    tick_parser.add_argument("--state", required=True)
    tick_parser.add_argument("--source", choices=("heartbeat", "foreground"), default="foreground")

    waiting_check = sub.add_parser("waiting-check")
    waiting_check.add_argument("--state", required=True)
    waiting_check.add_argument("--token", required=True)
    waiting_check.add_argument("--automation-id", required=True)

    authorize_waiting_read = sub.add_parser("authorize-waiting-chat-read")
    authorize_waiting_read.add_argument("--state", required=True)
    authorize_waiting_read.add_argument("--token", required=True)
    authorize_waiting_read.add_argument("--automation-id", required=True)
    authorize_waiting_read.add_argument("--lease-id", required=True)

    authorize_submission_reopen = sub.add_parser("authorize-browser-submission-reopen")
    authorize_submission_reopen.add_argument("--state", required=True)
    authorize_submission_reopen.add_argument("--fingerprint", required=True)
    authorize_submission_reopen.add_argument("--browser-id", required=True)

    authorize_submission_send = sub.add_parser("authorize-browser-submission-send")
    authorize_submission_send.add_argument("--state", required=True)
    authorize_submission_send.add_argument("--fingerprint", required=True)
    authorize_submission_send.add_argument("--browser-id", required=True)
    authorize_submission_send.add_argument("--lease-id", required=True)

    authorize_startup_reopen = sub.add_parser("authorize-browser-startup-reopen")
    authorize_startup_reopen.add_argument("--state", required=True)
    authorize_startup_reopen.add_argument("--browser-id", required=True)

    confirm_startup_rebind = sub.add_parser("confirm-browser-startup-rebind")
    confirm_startup_rebind.add_argument("--state", required=True)
    confirm_startup_rebind.add_argument("--expected-revision", required=True, type=int)
    confirm_startup_rebind.add_argument("--browser-id", required=True)
    confirm_startup_rebind.add_argument("--provider-tab-id", required=True)
    confirm_startup_rebind.add_argument("--url", required=True)
    confirm_startup_rebind.add_argument("--observed-title")
    confirm_startup_rebind.add_argument("--at")

    bind_browser_tab = sub.add_parser("bind-browser-tab")
    bind_browser_tab.add_argument("--state", required=True)
    bind_browser_tab.add_argument("--browser-id", required=True)
    bind_browser_tab.add_argument("--provider-tab-id", required=True)
    bind_browser_tab.add_argument("--url", required=True)
    bind_browser_tab.add_argument("--observed-title")
    bind_browser_tab.add_argument("--provisioned-chat", action="store_true")
    bind_browser_tab.add_argument("--canonical-url-only", action="store_true")
    bind_browser_tab.add_argument("--at")

    promote_browser_tab = sub.add_parser("promote-browser-tab-binding")
    promote_browser_tab.add_argument("--state", required=True)
    promote_browser_tab.add_argument("--browser-id", required=True)
    promote_browser_tab.add_argument("--provider-tab-id", required=True)
    promote_browser_tab.add_argument("--url", required=True)
    promote_browser_tab.add_argument("--token", required=True)
    promote_browser_tab.add_argument("--automation-id", required=True)
    promote_browser_tab.add_argument("--lease-id", required=True)

    bind_waiting_check = sub.add_parser("bind-waiting-check")
    bind_waiting_check.add_argument("--state", required=True)
    bind_waiting_check.add_argument("--token", required=True)
    bind_waiting_check.add_argument("--automation-id", required=True)

    rearm_waiting_check = sub.add_parser("rearm-waiting-check")
    rearm_waiting_check.add_argument("--state", required=True)
    rearm_waiting_check.add_argument("--token", required=True)
    rearm_waiting_check.add_argument("--automation-id", required=True)

    browser_observation = sub.add_parser("browser-network-observation")
    browser_observation.add_argument("--state", required=True)
    browser_observation.add_argument("--token", required=True)
    browser_observation.add_argument("--automation-id", required=True)
    browser_observation.add_argument(
        "--outcome", required=True, choices=("network_error", "rate_limited", "loaded")
    )
    browser_observation.add_argument("--error")
    browser_observation.add_argument("--at")

    queue_replay = sub.add_parser("mac-queue-replay-check")
    queue_replay.add_argument("--state", required=True)
    queue_replay.add_argument("--token", required=True)
    queue_replay.add_argument("--project-path", required=True)
    queue_replay.add_argument("--evidence")

    resume = sub.add_parser("resume")
    resume.add_argument("--state", required=True)

    progress_query = sub.add_parser("show-status")
    progress_query.add_argument("--state", required=True)

    discover_reviewer = sub.add_parser("discover-reviewer-chat")
    discover_reviewer.add_argument("--before-snapshot", required=True)
    discover_reviewer.add_argument("--after-snapshot", required=True)
    discover_reviewer.add_argument("--expected-title")

    prepare_main_app_submission = sub.add_parser("prepare-main-app-submission")
    prepare_main_app_submission.add_argument("--state", required=True)
    prepare_main_app_submission.add_argument("--snapshot", required=True)
    prepare_main_app_submission.add_argument("--text-file", required=True)
    prepare_main_app_submission.add_argument("--context-file", required=True)
    prepare_main_app_submission.add_argument("--timeout-seconds", type=int, default=120)
    prepare_main_app_submission.add_argument("--at")

    reconcile_main_app_submission = sub.add_parser("reconcile-main-app-submission")
    reconcile_main_app_submission.add_argument("--state", required=True)
    reconcile_main_app_submission.add_argument("--snapshot", required=True)
    reconcile_main_app_submission.add_argument("--text-file", required=True)
    reconcile_main_app_submission.add_argument("--context-file", required=True)
    reconcile_main_app_submission.add_argument("--at")
    reconcile_main_app_submission.add_argument(
        "--source", choices=("foreground", "waiting_check"), default="foreground"
    )
    reconcile_main_app_submission.add_argument("--deleted-automation-id")
    reconcile_main_app_submission.add_argument("--user-authorized-recovery", action="store_true")

    coordination_preflight = sub.add_parser("coordination-preflight")
    coordination_preflight.add_argument("--implementation-thread-id", required=True)
    coordination_preflight.add_argument(
        "--implementation-role", choices=sorted(VALID_IMPLEMENTATION_ROLES),
        default="luna_medium",
    )
    coordination_preflight.add_argument("--reviewer-thread-id")
    coordination_preflight.add_argument(
        "--chat-read", required=True, choices=sorted(VALID_COORDINATION_CAPABILITIES)
    )
    coordination_preflight.add_argument(
        "--chat-send", required=True, choices=sorted(VALID_COORDINATION_CAPABILITIES)
    )
    coordination_preflight.add_argument(
        "--one-shot-automation", required=True, choices=sorted(VALID_COORDINATION_CAPABILITIES)
    )
    coordination_preflight.add_argument(
        "--mode", choices=sorted(VALID_COORDINATION_MODES), default="automatic"
    )
    coordination_preflight.add_argument(
        "--review-mode", choices=sorted(VALID_COORDINATION_REVIEW_MODES), default="unconfirmed"
    )
    coordination_preflight.add_argument(
        "--transport", choices=sorted(VALID_REVIEW_TRANSPORTS),
        default="in_app_browser",
    )

    autonomous_preflight = sub.add_parser("autonomous-preflight")
    autonomous_preflight.add_argument("--implementation-thread-id", required=True)
    autonomous_preflight.add_argument(
        "--implementation-role", choices=sorted(VALID_IMPLEMENTATION_ROLES),
        default="luna_medium",
    )
    autonomous_preflight.add_argument("--reviewer-thread-id")
    autonomous_preflight.add_argument(
        "--chat-read", required=True, choices=sorted(VALID_COORDINATION_CAPABILITIES)
    )
    autonomous_preflight.add_argument(
        "--chat-send", required=True, choices=sorted(VALID_COORDINATION_CAPABILITIES)
    )
    autonomous_preflight.add_argument(
        "--one-shot-automation", required=True, choices=sorted(VALID_COORDINATION_CAPABILITIES)
    )
    autonomous_preflight.add_argument(
        "--mode", choices=sorted(VALID_COORDINATION_MODES), default="automatic"
    )
    autonomous_preflight.add_argument(
        "--review-mode", choices=sorted(VALID_COORDINATION_REVIEW_MODES), default="unconfirmed"
    )
    autonomous_preflight.add_argument(
        "--transport", choices=sorted(VALID_REVIEW_TRANSPORTS),
        default="in_app_browser",
    )

    startup_diagnostics = sub.add_parser(
        "startup-diagnostics",
        help="只读检查新实施任务初始化前的宿主能力事实",
    )
    startup_diagnostics.add_argument("--implementation-thread-id", required=True)
    startup_diagnostics.add_argument("--reviewer-thread-id", required=True)
    startup_diagnostics.add_argument(
        "--browser", required=True, choices=sorted(VALID_STARTUP_BROWSER_STATES),
    )
    startup_diagnostics.add_argument(
        "--chat-login", required=True, choices=sorted(VALID_STARTUP_CHAT_LOGIN_STATES),
    )
    startup_diagnostics.add_argument(
        "--chat-selection", required=True, choices=sorted(VALID_STARTUP_CHAT_SELECTION_STATES),
    )
    startup_diagnostics.add_argument(
        "--chat-read", required=True, choices=sorted(VALID_COORDINATION_CAPABILITIES),
    )
    startup_diagnostics.add_argument(
        "--chat-send", required=True, choices=sorted(VALID_COORDINATION_CAPABILITIES),
    )
    startup_diagnostics.add_argument(
        "--one-shot-wait", required=True, choices=sorted(VALID_COORDINATION_CAPABILITIES),
    )

    network = sub.add_parser("record-network-error")
    network.add_argument("--state", required=True)
    network.add_argument("--message", required=True)
    network.add_argument("--at")

    monitor_mode = sub.add_parser("set-monitor-mode")
    monitor_mode.add_argument("--state", required=True)
    monitor_mode.add_argument("--mode", choices=("foreground_only",), required=True)

    guard = sub.add_parser("guard")
    guard.add_argument("--state", required=True)
    guard.add_argument("--minutes", type=int, default=20)
    guard.add_argument("--reason", required=True)
    guard.add_argument("--implementation-thread-id")
    guard.add_argument("--replace", action="store_true")

    release = sub.add_parser("release")
    release.add_argument("--state", required=True)
    release.add_argument("--lease-id", required=True)
    release.add_argument("--force", action="store_true")

    review_mode = sub.add_parser("confirm-review-mode")
    review_mode.add_argument("--state", required=True)
    review_mode.add_argument("--mode", required=True, choices=("extreme",))
    review_mode.add_argument(
        "--source", choices=("user", "main_app", "native_app", "in_app_browser"),
        default="user",
    )
    review_mode.add_argument("--reviewer-thread-id")
    review_mode.add_argument("--observed-label", default="极高")
    review_mode.add_argument("--native-app-instance-id")
    review_mode.add_argument("--at")

    submission = sub.add_parser("confirm-review-submission")
    submission.add_argument("--state", required=True)
    submission.add_argument("--reviewer-thread-id", required=True)
    submission.add_argument("--request-turn-id", required=True)
    submission.add_argument("--request-message-id", required=True)
    submission.add_argument("--native-app-instance-id")
    submission.add_argument("--attachment-name", action="append")
    submission.add_argument("--submitted-at")
    submission.add_argument("--browser-reopen-lease-id")
    submission.add_argument("--browser-id")
    submission.add_argument("--browser-send-authorization-revision", type=int)

    invalidate_mode = sub.add_parser("invalidate-review-mode")
    invalidate_mode.add_argument("--state", required=True)
    invalidate_mode.add_argument("--reason", required=True)

    register_binding = sub.add_parser("register-binding")
    register_binding.add_argument("--state", required=True)
    register_binding.add_argument("--registry", required=True)
    register_binding.add_argument("--task-id", required=True)
    register_binding.add_argument("--display-name", required=True)
    register_binding.add_argument("--iteration", required=True)
    register_binding.add_argument("--work-status-label", required=True)

    registry_doctor = sub.add_parser("doctor-registry")
    registry_doctor.add_argument("--registry", required=True)

    confirm_attachment = sub.add_parser("confirm-attachment")
    confirm_attachment.add_argument("--state", required=True)
    confirm_attachment.add_argument("--expected-name", action="append", required=True)
    confirm_attachment.add_argument("--observed-name", action="append", required=True)
    confirm_attachment.add_argument("--mode", required=True, choices=("verified", "manual_confirmed"))
    confirm_attachment.add_argument("--at")

    reset_attachment = sub.add_parser("reset-attachment")
    reset_attachment.add_argument("--state", required=True)
    reset_attachment.add_argument("--required", action="store_true")
    reset_attachment.add_argument("--expected-name", action="append")

    progress = sub.add_parser("record-progress")
    progress.add_argument("--state", required=True)
    progress.add_argument("--event-id", required=True)
    progress.add_argument("--stage", required=True)
    progress.add_argument("--active-minutes", type=int, required=True)
    progress.add_argument("--meaningful-step", action="store_true")
    progress.add_argument("--evidence-fingerprint", required=True)
    progress.add_argument("--at")

    pro_request = sub.add_parser("request-pro")
    pro_request.add_argument("--state", required=True)
    pro_request.add_argument("--at")

    pro_confirm = sub.add_parser("confirm-pro")
    pro_confirm.add_argument("--state", required=True)
    pro_confirm.add_argument("--request-id", required=True)
    pro_confirm.add_argument("--at")

    pro_cancel = sub.add_parser("cancel-pro")
    pro_cancel.add_argument("--state", required=True)
    pro_cancel.add_argument("--request-id", required=True)
    pro_cancel.add_argument("--reason", required=True)
    pro_cancel.add_argument("--force", action="store_true")

    pro_complete = sub.add_parser("complete-pro")
    pro_complete.add_argument("--state", required=True)
    pro_complete.add_argument("--request-id", required=True)
    pro_complete.add_argument("--guide-version", required=True)
    pro_complete.add_argument("--guide-path", required=True)
    pro_complete.add_argument("--guide-sha256", required=True)
    pro_complete.add_argument("--at")

    high_attempt = sub.add_parser("record-high-attempt")
    high_attempt.add_argument("--state", required=True)
    high_attempt.add_argument("--attempt-id", required=True)
    high_attempt.add_argument("--blocker-id", required=True)
    high_attempt.add_argument("--evidence-fingerprint", required=True)
    high_attempt.add_argument("--at")

    execution_verify = sub.add_parser("verify-execution")
    execution_verify.add_argument("--state", required=True)
    execution_verify.add_argument("--target", required=True, choices=("high", "terra"))
    execution_verify.add_argument("--execution-id", required=True)
    execution_verify.add_argument("--source", required=True, choices=("manual_confirmed",))
    execution_verify.add_argument("--proof", required=True)
    execution_verify.add_argument("--at")

    terra_request = sub.add_parser("request-terra")
    terra_request.add_argument("--state", required=True)
    terra_request.add_argument("--signal", required=True, choices=sorted(VALID_TERRA_SIGNALS))
    terra_request.add_argument("--reason", required=True)
    terra_request.add_argument("--at")

    terra_capability = sub.add_parser("set-terra-capability")
    terra_capability.add_argument("--state", required=True)
    terra_capability.add_argument("--status", required=True, choices=("unverified", "supported", "unsupported"))
    terra_capability.add_argument("--force", action="store_true")

    terra_confirm = sub.add_parser("confirm-terra")
    terra_confirm.add_argument("--state", required=True)
    terra_confirm.add_argument("--request-id", required=True)
    terra_confirm.add_argument("--at")

    terra_complete = sub.add_parser("complete-terra")
    terra_complete.add_argument("--state", required=True)
    terra_complete.add_argument("--request-id", required=True)
    terra_complete.add_argument("--at")

    terra_cancel = sub.add_parser("cancel-terra")
    terra_cancel.add_argument("--state", required=True)
    terra_cancel.add_argument("--request-id", required=True)
    terra_cancel.add_argument("--reason", required=True)
    terra_cancel.add_argument("--force", action="store_true")

    model_status = sub.add_parser("model-status")
    model_status.add_argument("--state", required=True)

    change = sub.add_parser("transition")
    change.add_argument("--state", required=True)
    change.add_argument("--status", required=True, choices=sorted(VALID_STATUSES))
    change.add_argument("--stage")
    change.add_argument("--payload-mode", choices=sorted(VALID_PAYLOAD_MODES))
    change.add_argument("--fingerprint")
    change.add_argument("--waiting-since")
    change.add_argument("--request-turn-id")
    change.add_argument("--request-message-id")
    change.add_argument("--request-persisted-at")
    change.add_argument("--request-stage")
    change.add_argument("--request-reasoning-mode", choices=sorted(VALID_REQUEST_REASONING_MODES))
    change.add_argument("--request-native-app-instance-id")
    change.add_argument("--response-turn-id")
    change.add_argument("--response-message-id")
    change.add_argument("--response-completed-at")
    change.add_argument("--response-complete", choices=("true", "false"))
    change.add_argument("--response-envelope-hash")
    change.add_argument("--response-stage")
    change.add_argument("--artifacts-summary")
    change.add_argument("--recovery-action")
    change.add_argument("--attachment-send", choices=sorted(VALID_ATTACHMENT_CAPABILITIES))
    change.add_argument("--filesystem-read", choices=sorted(VALID_FILESYSTEM_CAPABILITIES))
    change.add_argument("--quarantine-unconfirmed", action="store_true")
    change.add_argument("--recovery-override", action="store_true")
    change.add_argument("--overall-goal-complete", action="store_true")
    change.add_argument("--completion-evidence")

    result = sub.add_parser("validate-result")
    result.add_argument("--state")
    result.add_argument("--result-file")
    result.add_argument("--result-json")
    result.add_argument("--result-base64")

    resume_reply = sub.add_parser("resume-from-reply")
    resume_reply.add_argument("--state", required=True)
    resume_reply.add_argument("--response-turn-id", required=True)
    resume_reply.add_argument("--response-message-id", required=True)
    resume_reply.add_argument("--response-completed-at")
    resume_reply.add_argument("--result-file")
    resume_reply.add_argument("--result-json")
    resume_reply.add_argument("--result-base64")
    resume_reply.add_argument("--source", choices=("foreground", "waiting_check"), default="foreground")
    resume_reply.add_argument("--deleted-automation-id")

    doctor_parser = sub.add_parser("doctor")
    doctor_parser.add_argument("--state", required=True)
    doctor_parser.add_argument("--automation-toml")
    doctor_parser.add_argument("--registry")

    audit_parser = sub.add_parser("audit")
    audit_parser.add_argument("--automation-root", required=True)
    audit_parser.add_argument("--state", required=True)
    audit_parser.add_argument("--automation-id")

    sub.add_parser("revision")
    sub.add_parser("selftest")
    sub.add_parser("closure-check")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            state = new_state(
                args.automation_id,
                args.implementation_thread_id,
                args.project_path,
                args.reviewer_thread_id,
                args.profile,
                args.codex_root,
                args.continuation_mode,
                args.review_transport,
                args.implementation_role,
                args.goal_mode,
            )
            save_state(args.state, state)
            result: Any = {"ok": True, "state": str(Path(args.state).resolve()), "revision": state["revision"]}
        elif args.command == "migrate-v6":
            result = migrate_v6(args)
        elif args.command == "render-heartbeat":
            result = render_heartbeat(args.state, args.validate_only)
        elif args.command == "tick":
            result = tick(args.state, source=args.source)
        elif args.command == "waiting-check":
            result = waiting_check_command(args)
        elif args.command == "authorize-waiting-chat-read":
            result = authorize_waiting_chat_read_command(args)
        elif args.command == "authorize-browser-submission-reopen":
            result = authorize_browser_submission_reopen_command(args)
        elif args.command == "authorize-browser-submission-send":
            result = authorize_browser_submission_send_command(args)
        elif args.command == "authorize-browser-startup-reopen":
            result = authorize_browser_startup_reopen_command(args)
        elif args.command == "confirm-browser-startup-rebind":
            result = confirm_browser_startup_rebind_command(args)
        elif args.command == "bind-browser-tab":
            result = bind_browser_tab_command(args)
        elif args.command == "promote-browser-tab-binding":
            result = promote_browser_tab_binding_command(args)
        elif args.command == "bind-waiting-check":
            result = bind_waiting_check_command(args)
        elif args.command == "rearm-waiting-check":
            result = rearm_waiting_check_command(args)
        elif args.command == "browser-network-observation":
            result = browser_network_observation_command(args)
        elif args.command == "mac-queue-replay-check":
            result = mac_queue_replay_check(args)
        elif args.command == "resume":
            result = resume_command(args)
        elif args.command == "show-status":
            result = progress_query_command(args)
        elif args.command == "discover-reviewer-chat":
            result = discover_reviewer_chat_command(args)
        elif args.command == "prepare-main-app-submission":
            result = prepare_main_app_submission_command(args)
        elif args.command == "reconcile-main-app-submission":
            result = reconcile_main_app_submission_command(args)
        elif args.command == "coordination-preflight":
            result = coordination_preflight_command(args)
        elif args.command == "autonomous-preflight":
            result = autonomous_preflight_command(args)
        elif args.command == "startup-diagnostics":
            result = startup_diagnostics_command(args)
        elif args.command == "record-network-error":
            result = record_network_error_command(args)
        elif args.command == "set-monitor-mode":
            result = set_monitor_mode_command(args)
        elif args.command == "guard":
            result = guard_action(args)
        elif args.command == "release":
            result = release_action(args)
        elif args.command == "confirm-review-mode":
            result = confirm_review_mode(args)
        elif args.command == "confirm-review-submission":
            result = confirm_review_submission_command(args)
        elif args.command == "invalidate-review-mode":
            result = invalidate_review_mode(args)
        elif args.command == "register-binding":
            result = register_binding_command(args)
        elif args.command == "doctor-registry":
            result = doctor_registry_command(args)
        elif args.command == "confirm-attachment":
            result = confirm_attachment_command(args)
        elif args.command == "reset-attachment":
            result = reset_attachment_command(args)
        elif args.command == "record-progress":
            result = record_progress_command(args)
        elif args.command == "request-pro":
            result = request_pro_command(args)
        elif args.command == "confirm-pro":
            result = confirm_pro_command(args)
        elif args.command == "cancel-pro":
            result = cancel_pro_command(args)
        elif args.command == "complete-pro":
            result = complete_pro_command(args)
        elif args.command == "record-high-attempt":
            result = record_high_attempt_command(args)
        elif args.command == "verify-execution":
            result = verify_execution_command(args)
        elif args.command == "request-terra":
            result = request_terra_command(args)
        elif args.command == "set-terra-capability":
            result = set_terra_capability_command(args)
        elif args.command == "confirm-terra":
            result = confirm_terra_command(args)
        elif args.command == "complete-terra":
            result = complete_terra_command(args)
        elif args.command == "cancel-terra":
            result = cancel_terra_command(args)
        elif args.command == "model-status":
            result = model_status_command(args)
        elif args.command == "transition":
            result = transition(args)
        elif args.command == "validate-result":
            result = validate_result_command(args)
        elif args.command == "resume-from-reply":
            result = resume_from_reply_command(args)
        elif args.command == "doctor":
            result = doctor(args.state, args.automation_toml, args.registry)
        elif args.command == "audit":
            result = audit(args)
        elif args.command == "revision":
            result = {"controller_version": CONTROLLER_VERSION, "schema_version": SCHEMA_VERSION, "skill_revision": SKILL_REVISION}
        elif args.command == "selftest":
            result = selftest()
        elif args.command == "closure-check":
            result = closure_check()
        else:  # pragma: no cover
            parser.error("unknown command")
        output(result)
        return 0
    except (LCRLError, OSError, ValueError):
        print(json.dumps({
            "ok": False,
            **user_status_exit("external_blocked"),
        }, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
