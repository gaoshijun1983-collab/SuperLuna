from __future__ import annotations

import importlib.util
import json
import re
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "luna-chatgpt-review-loop"
LCRL_SCRIPT = SKILL_ROOT / "scripts" / "lcrl.py"
LCRL_SPEC = importlib.util.spec_from_file_location("lcrl_package_test", LCRL_SCRIPT)
lcrl = importlib.util.module_from_spec(LCRL_SPEC)
assert LCRL_SPEC and LCRL_SPEC.loader
LCRL_SPEC.loader.exec_module(lcrl)


class PackageTests(unittest.TestCase):
    def test_release_version_is_consistent_across_metadata_and_readmes(self):
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        report = json.loads((ROOT / "release" / "alpha_release_report.json").read_text(encoding="utf-8"))
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
        semver = manifest["version"]
        pep440 = re.sub(r"-alpha\.(\d+)$", r"a\1", semver)

        self.assertEqual(report["package_version"], semver)
        self.assertEqual(pyproject["project"]["version"], pep440)
        self.assertEqual(lock["package"][0]["version"], pep440)
        self.assertIn(f"`{semver}`", (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn(f"`{semver}`", (ROOT / "README.zh-CN.md").read_text(encoding="utf-8"))

    def test_plugin_manifest_has_strict_semver_and_real_skill_path(self):
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "luna-review-loop")
        self.assertEqual(manifest["interface"]["displayName"], "SuperLuna")
        self.assertRegex(
            manifest["version"],
            re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?$"),
        )
        self.assertTrue((ROOT / manifest["skills"]).is_dir())
        self.assertLessEqual(len(manifest["interface"]["defaultPrompt"]), 3)

    def test_skill_frontmatter_stays_minimal(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        frontmatter = text.split("---", 2)[1]
        keys = {
            line.split(":", 1)[0].strip()
            for line in frontmatter.splitlines()
            if ":" in line
        }
        self.assertEqual(keys, {"name", "description"})
        self.assertIn("name: luna-chatgpt-review-loop", text)
        self.assertIn("SuperLuna", text)

    def test_skill_forbids_stage_end_choices_during_automatic_loop(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("自动模式活动期间不得输出三选一", text)
        self.assertIn("不得在每次正式提交前重复请求用户确认", text)
        self.assertIn("只有真实的新授权阻塞", text)
        self.assertIn("continuation_required=true", text)
        self.assertIn("turn_completion_allowed=false", text)
        self.assertIn("在同一 turn 继续", text)

    def test_skill_requires_a_fail_closed_turn_entry_guard_during_waiting(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        protocol = (SKILL_ROOT / "references" / "protocol.md").read_text(
            encoding="utf-8"
        )
        source = (SKILL_ROOT / "scripts" / "lcrl.py").read_text(encoding="utf-8")
        for requirement in (
            "每个新 turn 的入口门",
            "--reason turn_entry",
            "action=waiting_turn_blocked",
            "不得读取项目",
            "普通外部消息不能冒充等待 occurrence",
            "`--replace` 是兼容参数",
            "传入 `--replace` 也不会改变该判定",
        ):
            self.assertIn(requirement, skill)
        for requirement in (
            "first executable action",
            "waiting_turn_blocked",
            "creates no action lease",
            "cannot\nclaim that source",
            "cannot preempt any active lease",
            "Cross-task,\nwaiting-read, and browser-reopen leases remain non-reclaimable",
        ):
            self.assertIn(requirement, protocol)
        for requirement in (
            '"action": "waiting_turn_blocked"',
            '"execution_allowed": False',
            '"project_write_allowed": False',
            '"browser_access_allowed": False',
        ):
            self.assertIn(requirement, source)

    def test_controller_registry_matches_source_revision(self):
        registry = json.loads((SKILL_ROOT / "references" / "controller.json").read_text(encoding="utf-8"))
        source = (SKILL_ROOT / "scripts" / "lcrl.py").read_text(encoding="utf-8")
        self.assertIn(f'CONTROLLER_VERSION = {registry["controller_version"]}', source)
        self.assertIn(f'SKILL_REVISION = "{registry["skill_revision"]}"', source)

    def test_published_state_schema_accepts_every_runtime_reasoning_source(self):
        schema = json.loads(
            (SKILL_ROOT / "references" / "state_schema_v7.json").read_text(encoding="utf-8")
        )
        published_sources = set(
            schema["properties"]["confirmation"]["properties"]
            ["reviewer_reasoning_control_source"]["enum"]
        )
        self.assertEqual(
            published_sources,
            {"none", "user", "main_app", "native_app", "in_app_browser"},
        )

    def test_published_state_schema_enforces_continuous_goal_completion_contract(self):
        schema = json.loads(
            (SKILL_ROOT / "references" / "state_schema_v7.json").read_text(
                encoding="utf-8"
            )
        )
        review = schema["properties"]["review"]
        completion_fields = {
            "goal_mode",
            "overall_completion_confirmed",
            "overall_completion_evidence",
        }

        self.assertTrue(completion_fields.issubset(review["required"]))
        self.assertEqual(
            set(review["properties"]["goal_mode"]["enum"]),
            {"continuous", "single_stage"},
        )
        completion_rule = review["allOf"][0]
        self.assertEqual(
            completion_rule["if"]["properties"]["goal_mode"]["const"],
            "continuous",
        )
        self.assertEqual(
            completion_rule["if"]["properties"]["status"]["const"],
            "completed",
        )
        self.assertTrue(
            completion_rule["then"]["properties"]
            ["overall_completion_confirmed"]["const"]
        )
        self.assertEqual(
            set(
                completion_rule["then"]["properties"]
                ["overall_completion_evidence"]["not"]["enum"]
            ),
            {"", "none"},
        )

    def test_published_review_submit_pending_schema_rejects_actionable_response(self):
        state = lcrl.new_state("a1", "implementation", ".", "review-chat")
        state["review"].update({
            "status": "review_submit_pending",
            "current_stage": "A1",
            "cycle_id": "cycle-1",
            "submission_fingerprint": "fingerprint-1",
            "response_complete": True,
            "response_valid_for_apply": True,
        })
        with self.assertRaisesRegex(
            lcrl.LCRLError,
            "review_submit_pending cannot contain an actionable response",
        ):
            lcrl.validate_state(state)

        schema = json.loads(
            (SKILL_ROOT / "references" / "state_schema_v7.json").read_text(
                encoding="utf-8"
            )
        )
        review = schema["properties"]["review"]
        pending_rules = [
            rule
            for rule in review["allOf"]
            if rule.get("if", {}).get("properties", {}).get("status", {}).get("const")
            == "review_submit_pending"
        ]
        self.assertEqual(len(pending_rules), 1)
        pending_response = pending_rules[0]["then"]["properties"]
        self.assertFalse(pending_response["response_complete"]["const"])
        self.assertFalse(pending_response["response_valid_for_apply"]["const"])

    def test_published_state_schema_accepts_runtime_naming_versions(self):
        schema = json.loads(
            (SKILL_ROOT / "references" / "state_schema_v7.json").read_text(encoding="utf-8")
        )
        naming_versions = schema["properties"]["binding"]["properties"]
        self.assertEqual(naming_versions["naming_template_version"]["enum"], [1, 2, 3])
        source = (SKILL_ROOT / "scripts" / "lcrl.py").read_text(encoding="utf-8")
        self.assertIn("SUPPORTED_NAMING_TEMPLATE_VERSIONS = {1, 2, 3}", source)

    def test_published_state_schema_declares_every_runtime_top_level_section(self):
        schema = json.loads(
            (SKILL_ROOT / "references" / "state_schema_v7.json").read_text(encoding="utf-8")
        )
        runtime_sections = {
            "schema_version", "revision", "created_at", "updated_at", "automation",
            "policy", "confirmation", "capabilities", "review", "review_history",
            "browser_binding", "binding", "attachment", "capability_probes",
            "next_operation", "model_policy", "recovery", "alternative", "runtime",
        }

        self.assertEqual(set(schema["required"]), runtime_sections)
        self.assertTrue(runtime_sections.issubset(schema["properties"]))

    def test_published_policy_schema_matches_runtime_role_and_transport_locks(self):
        schema = json.loads(
            (SKILL_ROOT / "references" / "state_schema_v7.json").read_text(encoding="utf-8")
        )
        policy = schema["properties"]["policy"]
        expected_constants = {
            "reviewer_kind": "chatgpt",
            "review_quota_source": "chatgpt",
            "codex_review_forbidden": True,
            "transport_locked": True,
            "reviewer_read_only": True,
            "reviewer_reasoning_required": "extreme",
        }

        self.assertEqual(
            set(policy["required"]),
            set(expected_constants) | {"implementation_role", "reviewer_reasoning_control"},
        )
        self.assertEqual(
            set(policy["properties"]["implementation_role"]["enum"]),
            {"luna_medium", "terra_medium"},
        )
        for field, expected in expected_constants.items():
            self.assertEqual(policy["properties"][field]["const"], expected)
        self.assertEqual(
            set(policy["properties"]["reviewer_reasoning_control"]["enum"]),
            {"manual_app_chat", "in_app_browser"},
        )

        transport_pairs = {
            (
                rule["if"]["properties"]["review"]["properties"]["transport"]["const"],
                rule["then"]["properties"]["policy"]["properties"]
                ["reviewer_reasoning_control"]["const"],
            )
            for rule in schema["allOf"]
            if "review" in rule.get("if", {}).get("properties", {})
            and "policy" in rule.get("then", {}).get("properties", {})
        }
        self.assertEqual(
            transport_pairs,
            {
                ("app_chat_review", "manual_app_chat"),
                ("in_app_browser", "in_app_browser"),
            },
        )

    def test_published_quota_ledger_schema_matches_runtime_event_contract(self):
        schema = json.loads(
            (SKILL_ROOT / "references" / "state_schema_v7.json").read_text(
                encoding="utf-8"
            )
        )
        progress = schema["properties"]["model_policy"]["properties"]["progress"]
        self.assertEqual(
            set(progress["required"]),
            {"active_minutes_since_pro", "meaningful_steps_since_pro", "events"},
        )
        self.assertEqual(
            progress["properties"]["events"]["maxItems"],
            lcrl.MAX_PROGRESS_EVENTS,
        )
        event = progress["properties"]["events"]["items"]
        self.assertEqual(
            set(event["required"]),
            {
                "event_id",
                "stage",
                "active_minutes",
                "meaningful_step",
                "evidence_fingerprint",
                "recorded_at",
            },
        )
        self.assertEqual(event["properties"]["active_minutes"], {"type": "integer", "minimum": 1, "maximum": 120})
        self.assertEqual(event["properties"]["meaningful_step"], {"type": "boolean"})

    def test_published_confirmation_schema_requires_runtime_trust_evidence(self):
        schema = json.loads(
            (SKILL_ROOT / "references" / "state_schema_v7.json").read_text(encoding="utf-8")
        )
        confirmation = schema["properties"]["confirmation"]
        runtime_fields = {
            "lease_id",
            "reviewer_thread_id",
            "reviewer_context_mode",
            "confirmed_at",
            "valid",
            "invalidated_reason",
            "reviewer_reasoning_mode",
            "reviewer_reasoning_confirmed",
            "reviewer_reasoning_confirmed_at",
            "reviewer_reasoning_control_source",
            "reviewer_reasoning_observed_label",
            "reviewer_reasoning_observed_thread_id",
            "reviewer_reasoning_native_app_instance_id",
        }
        self.assertEqual(set(confirmation["required"]), runtime_fields)
        self.assertEqual(
            set(confirmation["properties"]["reviewer_reasoning_mode"]["enum"]),
            {"unconfirmed", "extreme"},
        )
        self.assertEqual(
            confirmation["properties"]["reviewer_reasoning_confirmed"]["type"],
            "boolean",
        )

        active_statuses = {
            "local_work",
            "review_submit_pending",
            "review_receipt_pending",
            "review_waiting",
            "result_received",
            "result_quarantined",
        }
        active_rules = [
            rule
            for rule in schema["allOf"]
            if set(
                rule.get("if", {})
                .get("properties", {})
                .get("review", {})
                .get("properties", {})
                .get("status", {})
                .get("enum", [])
            )
            == active_statuses
        ]
        self.assertEqual(len(active_rules), 1)
        active_confirmation = active_rules[0]["then"]["properties"]["confirmation"]
        self.assertTrue(active_confirmation["properties"]["valid"]["const"])
        self.assertEqual(
            set(
                active_confirmation["properties"]["reviewer_thread_id"]["not"]["enum"]
            ),
            {"", "none"},
        )

        confirmed_rules = [
            rule
            for rule in schema["allOf"]
            if rule.get("if", {}).get("properties", {}).get("confirmation", {})
            .get("properties", {}).get("reviewer_reasoning_confirmed", {}).get("const") is True
            and "review" not in rule.get("if", {}).get("properties", {})
        ]
        self.assertEqual(len(confirmed_rules), 1)
        trusted = confirmed_rules[0]["then"]["properties"]["confirmation"]
        self.assertEqual(
            trusted["properties"]["reviewer_reasoning_mode"]["const"], "extreme"
        )
        self.assertEqual(
            trusted["properties"]["reviewer_reasoning_observed_label"]["const"], "极高"
        )
        self.assertEqual(
            set(trusted["properties"]["reviewer_reasoning_control_source"]["enum"]),
            {"user", "main_app", "native_app", "in_app_browser"},
        )

        browser_confirmation_rules = [
            rule
            for rule in schema["allOf"]
            if set(rule.get("if", {}).get("properties", {})) == {"review", "confirmation"}
            and rule["if"]["properties"]["review"]["properties"]["transport"]["const"]
            == "in_app_browser"
        ]
        self.assertEqual(len(browser_confirmation_rules), 1)
        self.assertEqual(
            browser_confirmation_rules[0]["then"]["properties"]["confirmation"]
            ["properties"]["reviewer_reasoning_control_source"]["const"],
            "in_app_browser",
        )

    def test_published_capabilities_schema_matches_runtime_payload_contract(self):
        schema = json.loads(
            (SKILL_ROOT / "references" / "state_schema_v7.json").read_text(
                encoding="utf-8"
            )
        )
        capabilities = schema["properties"]["capabilities"]

        self.assertEqual(
            set(capabilities["required"]),
            {"attachment_send", "filesystem_read"},
        )
        self.assertEqual(
            set(capabilities["properties"]["attachment_send"]["enum"]),
            {"native", "manual", "unavailable"},
        )
        self.assertEqual(
            set(capabilities["properties"]["filesystem_read"]["enum"]),
            {"inline", "mcp_verified", "unavailable"},
        )
        for field in ("chat_list", "chat_read", "chat_send"):
            self.assertEqual(capabilities["properties"][field]["type"], "boolean")
        self.assertEqual(capabilities["properties"]["chat_create"]["type"], "string")
        self.assertEqual(
            schema["properties"]["capability_probes"]["required"],
            ["terra_next_turn"],
        )

        mcp_rules = [
            rule
            for rule in schema["allOf"]
            if rule.get("if", {})
            .get("properties", {})
            .get("review", {})
            .get("properties", {})
            .get("payload_mode", {})
            .get("const")
            == "mcp_readonly"
        ]
        self.assertEqual(len(mcp_rules), 1)
        self.assertEqual(
            mcp_rules[0]["then"]["properties"]["capabilities"]["properties"]
            ["filesystem_read"]["const"],
            "mcp_verified",
        )

        verified_rules = [
            rule
            for rule in schema["allOf"]
            if rule.get("if", {})
            .get("properties", {})
            .get("capabilities", {})
            .get("properties", {})
            .get("filesystem_read", {})
            .get("const")
            == "mcp_verified"
        ]
        self.assertEqual(len(verified_rules), 1)
        self.assertEqual(
            verified_rules[0]["then"]["properties"]["review"]["properties"]
            ["payload_mode"]["const"],
            "mcp_readonly",
        )

    def test_published_model_policy_schema_preserves_runtime_automation_locks(self):
        schema = json.loads(
            (SKILL_ROOT / "references" / "state_schema_v7.json").read_text(
                encoding="utf-8"
            )
        )
        model_policy = schema["properties"]["model_policy"]

        self.assertEqual(
            set(model_policy["required"]),
            {
                "version",
                "automatic_model_switch",
                "automatic_thread_creation",
                "executor",
                "reviewer",
                "progress",
                "routing",
                "pro",
                "terra",
            },
        )
        self.assertEqual(model_policy["properties"]["version"]["const"], 5)
        self.assertFalse(
            model_policy["properties"]["automatic_model_switch"]["const"]
        )
        self.assertFalse(
            model_policy["properties"]["automatic_thread_creation"]["const"]
        )

        executor = model_policy["properties"]["executor"]
        self.assertEqual(set(executor["required"]), {"default", "current"})
        self.assertEqual(
            set(executor["properties"]["default"]["enum"]),
            {"luna_medium", "terra_medium"},
        )
        self.assertEqual(
            set(executor["properties"]["current"]["enum"]),
            {"luna_medium", "terra_medium"},
        )

        implementation_pairs = {
            (
                rule["if"]["properties"]["policy"]["properties"]
                ["implementation_role"]["const"],
                rule["then"]["properties"]["model_policy"]["properties"]
                ["executor"]["properties"]["current"]["const"],
            )
            for rule in schema["allOf"]
            if "policy" in rule.get("if", {}).get("properties", {})
        }
        self.assertEqual(
            implementation_pairs,
            {("luna_medium", "luna_medium"), ("terra_medium", "terra_medium")},
        )

        reviewer = model_policy["properties"]["reviewer"]
        self.assertEqual(set(reviewer["required"]), {"default", "current"})
        self.assertEqual(reviewer["properties"]["default"]["const"], "sol_extreme")
        self.assertEqual(
            set(reviewer["properties"]["current"]["enum"]),
            {"sol_extreme", "chat_pro"},
        )

    def test_published_automation_contract_matches_wait_bound_runtime(self):
        schema = json.loads(
            (SKILL_ROOT / "references" / "state_schema_v7.json").read_text(encoding="utf-8")
        )
        automation = schema["properties"]["automation"]
        self.assertIn("heartbeat_mode", automation["required"])
        self.assertIn("waiting_check_active", automation["required"])
        pairs = {
            (
                rule["if"]["properties"]["heartbeat_mode"]["const"],
                rule["then"]["properties"]["interval_minutes"]["const"],
            )
            for rule in automation["allOf"]
        }
        self.assertEqual(
            pairs,
            {("foreground_only", 0), ("waiting_only", 0), ("legacy_fixed", 3)},
        )

        controller = json.loads(
            (SKILL_ROOT / "references" / "controller.json").read_text(encoding="utf-8")
        )
        self.assertEqual(controller["heartbeat_mode"], "waiting_only")
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("--continuation-mode automatic", skill)
        self.assertIn("不得静默降级", skill)
        protocol = (SKILL_ROOT / "references" / "protocol.md").read_text(
            encoding="utf-8"
        )
        for text in (skill, protocol):
            self.assertIn("RDATE:YYYYMMDDTHHMMSSZ", text)
            self.assertIn("禁止使用 `FREQ=`", text)
            self.assertIn("waiting_check_busy", text)
            self.assertIn("retry_not_before", text)
            self.assertIn("platform_wait_rule", text)
            self.assertIn("recurring_platform_rule_allowed", text)
        self.assertIn("第一项可执行动作必须是", skill)
        self.assertIn("first executable action", protocol.lower())

    def test_published_wait_state_schema_rejects_runtime_invalid_wait_binding(self):
        schema = json.loads(
            (SKILL_ROOT / "references" / "state_schema_v7.json").read_text(
                encoding="utf-8"
            )
        )
        monitor_statuses = {"review_receipt_pending", "review_waiting"}
        wait_state_rules = [
            rule
            for rule in schema["allOf"]
            if rule.get("if", {}).get("properties", {}).get("automation", {})
            .get("properties", {}).get("heartbeat_mode", {}).get("const")
            == "waiting_only"
            and set(
                rule.get("if", {}).get("properties", {}).get("review", {})
                .get("properties", {}).get("status", {}).get("enum", [])
            )
            == monitor_statuses
        ]

        self.assertEqual(len(wait_state_rules), 1)
        wait_state_rule = wait_state_rules[0]
        active = wait_state_rule["then"]["properties"]["automation"]["properties"]
        inactive = wait_state_rule["else"]["properties"]["automation"]["properties"]
        self.assertTrue(active["waiting_check_active"]["const"])
        self.assertEqual(active["waiting_check_token"]["not"]["const"], "none")
        self.assertFalse(inactive["waiting_check_active"]["const"])
        for field in (
            "waiting_check_token",
            "waiting_check_automation_id",
            "waiting_check_claimed_id",
        ):
            self.assertEqual(inactive[field]["const"], "none")

        source = (SKILL_ROOT / "scripts" / "lcrl.py").read_text(encoding="utf-8")
        self.assertIn(
            'MONITOR_STATUSES = {"review_receipt_pending", "review_waiting"}',
            source,
        )
        self.assertIn(
            "status in MONITOR_STATUSES and heartbeat_mode == \"waiting_only\"",
            source,
        )

    def test_source_tree_contains_no_python_cache_artifacts(self):
        artifacts = [
            path for path in ROOT.rglob("*")
            if path.name == "__pycache__" or path.suffix == ".pyc"
        ]
        self.assertEqual(artifacts, [])

    def test_handoff_release_files_exist(self):
        self.assertTrue((ROOT / "LICENSE").is_file())
        self.assertTrue((ROOT / "README.zh-CN.md").is_file())
        self.assertTrue((ROOT / "docs" / "MAC_HANDOFF_2026-08-03.md").is_file())
        self.assertTrue((ROOT / "docs" / "MAC_HANDOFF_2026-08-03.zh-CN.md").is_file())
        self.assertTrue((ROOT / "scripts" / "install-skill.sh").is_file())
        self.assertTrue((ROOT / "scripts" / "install-skill.ps1").is_file())
        self.assertTrue((ROOT / "release" / "alpha_release_report.json").is_file())
        self.assertTrue((SKILL_ROOT / "scripts" / "app_chat_reasoning.py").is_file())
        self.assertTrue((SKILL_ROOT / "scripts" / "native_app_session.py").is_file())

    def test_review_packet_requires_independent_evidence_based_review(self):
        packet = (SKILL_ROOT / "references" / "review_packet.md").read_text(encoding="utf-8")
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("review_packet.md", skill)
        for requirement in ("已证明", "合理推断", "尚未验证", "寻找反例", "PASS / REVISE / BLOCKED"):
            self.assertIn(requirement, packet)
        self.assertIn("本地文件路径不是 Chat 能看到的证据", packet)

    def test_skill_binds_one_user_selected_web_chat_without_creating_it(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for requirement in (
            "https://chatgpt.com/c/<conversation-id>",
            "同一个内置浏览器标签",
            "不自动新建 Chat",
            "标题和当前焦点不是身份",
            "认领该现有标签",
        ):
            self.assertIn(requirement, skill)

    def test_skill_reconciles_uncertain_browser_submission_before_resending(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        protocol = (SKILL_ROOT / "references" / "protocol.md").read_text(encoding="utf-8")
        for requirement in (
            "发送前",
            "不得重发",
            "可见用户消息身份基线",
            "同一标签",
            "正文一致",
            "旧轮次同文消息",
        ):
            self.assertIn(requirement, skill)
        for requirement in (
            "message baseline",
            "Submit once",
            "never permits\na resend",
            "same tab",
        ):
            self.assertIn(requirement, protocol)

    def test_skill_reuses_one_shot_gate_while_request_receipt_is_eventually_visible(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        protocol = (SKILL_ROOT / "references" / "protocol.md").read_text(encoding="utf-8")
        source = (SKILL_ROOT / "scripts" / "lcrl.py").read_text(encoding="utf-8")
        for requirement in (
            "review_receipt_pending",
            "rearm-waiting-check",
        ):
            self.assertIn(requirement, skill)
            self.assertIn(requirement, protocol)
        for requirement in (
            "waiting-check",
            "authorize-waiting-chat-read",
            "--source waiting_check",
            "--deleted-automation-id",
        ):
            self.assertIn(requirement, skill)
        self.assertIn("one stable platform heartbeat id", protocol)
        self.assertIn("updates that existing platform wait", protocol)
        self.assertIn("status in MONITOR_STATUSES", source)
        self.assertNotIn("恢复固定周期", skill)

    def test_browser_first_contract_uses_one_wait_gate_and_guarded_same_tab_reload(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        browser_protocol = (
            SKILL_ROOT / "references" / "browser_transport.md"
        ).read_text(encoding="utf-8")
        registry = json.loads(
            (SKILL_ROOT / "references" / "controller.json").read_text(encoding="utf-8")
        )
        readme = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        for requirement in (
            "in_app_browser",
            "browser-network-observation",
            "reload_same_tab_once",
            "180",
        ):
            self.assertIn(requirement, skill)
            self.assertIn(requirement, browser_protocol)
        self.assertIn("同一个内置浏览器标签", skill)
        self.assertIn("不得切回 App Chat", browser_protocol)
        self.assertIn("内置浏览器", readme)
        self.assertEqual(registry["default_transport"], "in_app_browser")

    def test_browser_wait_contract_reclaims_the_persisted_provider_tab_each_occurrence(self):
        schema = json.loads(
            (SKILL_ROOT / "references" / "state_schema_v7.json").read_text(encoding="utf-8")
        )
        browser_binding = schema["properties"]["browser_binding"]
        self.assertIn("provider_tab_id", browser_binding["properties"])
        self.assertNotIn("tab_id", browser_binding["properties"])

        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        protocol = (SKILL_ROOT / "references" / "browser_transport.md").read_text(
            encoding="utf-8"
        )
        for requirement in (
            "providerTabId",
            "user.openTabs()",
            "user.claimTab(tab)",
            'status: "handoff"',
            "不得持久化或跨轮复用 `Tab.id`",
        ):
            self.assertIn(requirement, skill)
            self.assertIn(requirement, protocol)

    def test_explicit_new_reviewer_chat_authorization_provisions_exactly_once(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        provisioning = (
            SKILL_ROOT / "references" / "browser_chat_provisioning.md"
        ).read_text(encoding="utf-8")
        for requirement in (
            "一次性新 Chat 授权",
            "只创建一个",
            "初始化消息不计入正式回合",
            "providerTabId",
            "bind-browser-tab",
            "不得自动切换模型或推理档位",
            "pending_handoff",
            "promote-browser-tab-binding",
            "provisioned_url_fallback_allowed",
            "provisioned_url_reopen_allowed",
            "authorize-browser-submission-reopen",
            "--browser-reopen-lease-id",
        ):
            self.assertIn(requirement, skill)
            self.assertIn(requirement, provisioning)

    def test_new_task_startup_opens_and_rebinds_the_existing_web_chat(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        provisioning = (
            SKILL_ROOT / "references" / "browser_chat_provisioning.md"
        ).read_text(encoding="utf-8")
        transport = (SKILL_ROOT / "references" / "browser_transport.md").read_text(
            encoding="utf-8"
        )
        for requirement in (
            "browser:control-in-app-browser",
            "authorize-browser-startup-reopen",
            "confirm-browser-startup-rebind",
            "新实现任务自己的内置浏览器",
        ):
            self.assertIn(requirement, skill)
            self.assertIn(requirement, provisioning)
        self.assertIn("browser_startup_reopen_authorized", transport)
        self.assertIn("before local project work", transport)
        self.assertIn("不得在仅完成启动重绑后结束本次 turn", skill)

    def test_bound_existing_chat_can_reopen_without_creating_a_replacement(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        transport = (SKILL_ROOT / "references" / "browser_transport.md").read_text(
            encoding="utf-8"
        )
        protocol = (SKILL_ROOT / "references" / "protocol.md").read_text(
            encoding="utf-8"
        )
        for text in (skill, transport, protocol):
            self.assertIn("canonical_url_reopen_allowed", text)
        self.assertIn("两个当前列表都不存在其精确 URL", skill)
        self.assertIn("任何已经绑定的固定 Chat", skill)
        self.assertIn("any fixed Chat already bound", transport)
        self.assertIn("never authorizes a new Chat", transport)

    def test_submission_reopen_navigation_timeout_is_reconciled_on_same_tab(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        transport = (SKILL_ROOT / "references" / "browser_transport.md").read_text(
            encoding="utf-8"
        )
        provisioning = (
            SKILL_ROOT / "references" / "browser_chat_provisioning.md"
        ).read_text(encoding="utf-8")
        for text in (skill, transport, provisioning):
            normalized = " ".join(text.split())
            self.assertIn("navigation result is uncertain", normalized)
            self.assertIn("inspect the same opened tab", normalized)
            self.assertIn("must not open, navigate, or reload again", normalized)
            self.assertIn(
                "must not close the tab merely because the navigation call timed out",
                normalized,
            )
            self.assertIn("authorize-browser-submission-send", normalized)
            self.assertIn("browser_submission_send_authorized", normalized)
            self.assertIn("--browser-send-authorization-revision", normalized)
        normalized_transport = " ".join(transport.split())
        self.assertIn("within the existing ten-minute lease", normalized_transport)
        self.assertIn("no second reopen authorization", normalized_transport)

    def test_explicit_existing_chat_without_provider_identity_uses_url_only_binding(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        transport = (SKILL_ROOT / "references" / "browser_transport.md").read_text(
            encoding="utf-8"
        )
        for requirement in (
            "canonical_url_only",
            "--canonical-url-only",
            "不得持久化数字 `Tab.id`",
        ):
            self.assertIn(requirement, skill)
            self.assertIn(requirement, transport)

    def test_browser_submission_never_consumes_a_reply_in_the_same_occurrence(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        transport = (SKILL_ROOT / "references" / "browser_transport.md").read_text(
            encoding="utf-8"
        )
        protocol = (SKILL_ROOT / "references" / "protocol.md").read_text(
            encoding="utf-8"
        )
        for requirement in (
            "同一 occurrence 不读取回复",
            "即使回复已经可见或完整",
            "waiting_check",
            'status: "handoff"',
        ):
            self.assertIn(requirement, skill)
        self.assertIn("must not consume a reply in that same occurrence", transport)
        self.assertIn("even if the assistant reply is already complete", protocol)

    def test_browser_submission_visual_evidence_never_captures_reply_viewport(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        transport = (SKILL_ROOT / "references" / "browser_transport.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("提交后不得截取整页或全视口", skill)
        self.assertIn("directly capture only the new user-message region", transport)
        self.assertIn("omit the post-submit screenshot", transport)

    def test_startup_browser_confirmation_is_visible_user_evidence_not_model_control(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        protocol = (SKILL_ROOT / "references" / "protocol.md").read_text(encoding="utf-8")
        for requirement in (
            "用户亲眼确认",
            "SuperLuna 不替用户切换",
            "用户报告或亲眼看到档位变化",
        ):
            self.assertIn(requirement, skill)
        self.assertIn("The user explicitly confirms the visible reviewer mode", protocol)
        self.assertIn("never creates a replacement\nChat, switches model/reasoning", protocol)

    def test_skill_preflight_uses_the_runtime_extreme_review_mode_enum(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("--review-mode extreme", skill)
        self.assertNotIn("--review-mode confirmed", skill)

    def test_alpha_release_report_matches_package_and_controller(self):
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        report = json.loads((ROOT / "release" / "alpha_release_report.json").read_text(encoding="utf-8"))
        registry = json.loads((SKILL_ROOT / "references" / "controller.json").read_text(encoding="utf-8"))
        self.assertEqual(report["product_name"], "SuperLuna")
        self.assertEqual(report["package_version"], manifest["version"])
        self.assertEqual(report["controller_version"], registry["controller_version"])
        self.assertEqual(report["skill_revision"], registry["skill_revision"])
        self.assertEqual(report["compatibility_entrypoints"]["skill"], "luna-chatgpt-review-loop")
        self.assertEqual(report["compatibility_entrypoints"]["plugin"], "luna-review-loop")
        closure = report["automated_evidence"]["controller_closure_check"]
        self.assertTrue(closure["passed"])
        self.assertEqual(closure["scope"], "local_controller_only")
        self.assertEqual(closure["executed_checks"], ["controller_selftest"])
        self.assertFalse(closure["repository_tests_run"])
        self.assertIsNone(closure["repository_tests_passed"])
        self.assertFalse(closure["real_device_gate_passed"])
        self.assertFalse(closure["public_beta_gate_passed"])
        self.assertEqual(report["real_device_evidence"]["consecutive_real_project_cycles"], 0)
        self.assertEqual(report["real_device_evidence"]["historical_real_project_cycles"], 3)
        self.assertFalse(
            report["real_device_evidence"]["macos_host_turn_finalization_enforcement_available"]
        )
        self.assertIn(
            "codex_host_same_turn_continuation_enforcement",
            report["beta_gate_status"]["blocking_items"],
        )
        self.assertFalse(report["beta_gate_status"]["ready"])
        self.assertFalse(report["public_beta_ready"])

    def test_release_tree_excludes_known_live_identifiers_and_paths(self):
        forbidden = (
            "019f6658" + "-7bd4-7753-ba93-ebf125decc8d",
            "6a6c4519" + "-9e0c-83ea-8df8-f27da2d10dc9",
            "F:" + "\\\\西行2025-11-30",
            "C:" + "\\\\Users\\\\Administrator\\\\.codex\\\\lcrl",
        )
        for path in ROOT.rglob("*"):
            if not path.is_file() or path.suffix in {".zip", ".pyc"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for value in forbidden:
                self.assertNotIn(value, text, f"private value found in {path}")


if __name__ == "__main__":
    unittest.main()
