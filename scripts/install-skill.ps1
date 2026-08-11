$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$sourceDir = Join-Path $repoRoot "skills\luna-chatgpt-review-loop"
$codexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$targetRoot = Join-Path $codexRoot "skills"
$targetDir = Join-Path $targetRoot "luna-chatgpt-review-loop"

New-Item -ItemType Directory -Path $targetRoot -Force | Out-Null
if (Test-Path -LiteralPath $targetDir) {
    throw "Refusing to overwrite existing Skill: $targetDir"
}

Copy-Item -LiteralPath $sourceDir -Destination $targetDir -Recurse
Get-ChildItem -LiteralPath $targetDir -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -LiteralPath $targetDir -Recurse -File -Filter "*.pyc" | Remove-Item -Force
python -B (Join-Path $targetDir "scripts\lcrl.py") selftest
Write-Host "Installed: $targetDir"
Write-Host "Start a new Codex task to load the updated Skill."
