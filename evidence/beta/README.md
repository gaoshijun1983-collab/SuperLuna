# Beta evidence / Beta 证据

Store one sanitized UTF-8 JSON file per already-observed real-device result in
this directory. Do not include Chat text, conversation IDs, account details,
tokens, secrets, or unrelated project content.

每个已经真实发生的设备测试使用一个 UTF-8 JSON 文件。不要保存 Chat 正文、
对话 ID、账号信息、令牌、密钥或其他项目内容。

The file is evidence, not a test instruction. Creating it must not start a
browser, send a message, create an automation, or claim an unobserved result.

这个文件只是证据记录，不是测试指令；创建文件不得启动浏览器、发送消息、创建
自动任务，也不得填写未真实观察到的结果。

## Common fields / 通用字段

```json
{
  "id": "unique-evidence-id",
  "gate": "one exact gate name from docs/beta_evidence_matrix.json",
  "source": "real_device",
  "platform": "macos",
  "os_version": "observed operating-system version",
  "codex_version": "observed Codex Desktop version",
  "observed_at": "2026-08-15T00:00:00Z",
  "result": "pass",
  "candidate_version": "0.2.0-alpha.63",
  "candidate_commit": "e24edd00ec3775108e283460d4b5b5625eae8c73"
}
```

Windows-only gates require `platform: "windows"`; the macOS version-matrix
gate requires `platform: "macos"`. The gate name, platform, candidate, and full
artifact body are checked before the result can count.

Windows 专属门槛必须填写 `platform: "windows"`；macOS 版本矩阵必须填写
`platform: "macos"`。gate、平台、候选版本及整个证据正文都会被核对。

For a consecutive real-project cycle, also record all four counters. Every
counter must be zero for the cycle to count:

连续真实项目闭环还必须记录以下四项，并且全部为零：

```json
{
  "outside_wakeups": 0,
  "duplicate_sends": 0,
  "cross_chat_reads": 0,
  "replacement_tasks": 0
}
```

Record an observed file with:

```text
python -B scripts/record_beta_evidence.py --gate <exact-gate-name> --evidence evidence/beta/<file>.json
```

Then run `python -B scripts/validate_beta_evidence.py`. A blocked result is
expected until every required real-device gate is complete.

记录后运行 `python -B scripts/validate_beta_evidence.py`。在所有真实设备门槛完成
以前，显示尚未达到 Beta 属于正常结果。
