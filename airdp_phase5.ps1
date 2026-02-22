# airdp_phase5.ps1 — Phase 5: Report（cycle_report.md 生成）
#
# Usage:
#   .\airdp_phase5.ps1 -ProjectDir . -CycleId 01
#   .\airdp_phase5.ps1 -ProjectDir . -CycleId 01 -Orchestrator gemini

param (
    [Parameter(Mandatory=$false)] [string]$ProjectDir   = ".",
    [Parameter(Mandatory=$true)]  [string]$CycleId,
    [Parameter(Mandatory=$false)]
    [ValidateSet("gemini","codex","claude","copilot")]
    [string]$Orchestrator = "gemini",
    [Parameter(Mandatory=$false)] [string]$PromptsDir   = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptDir "airdp_common.ps1")

if ($PromptsDir -eq "") { $PromptsDir = Join-Path $ScriptDir "airdp_prompts" }
if (-not (Test-Path $PromptsDir)) { throw "Prompts directory not found: $PromptsDir" }

$p = Resolve-AirdpPaths -ProjectDir $ProjectDir -CycleId $CycleId

$OrchestratorSessionFile = Join-Path $p.SessionDir "orchestrator_session_id.txt"
$session               = Get-OrCreateSessionId -AIName $Orchestrator -SessionFile $OrchestratorSessionFile
$orchestratorSessionId = $session.Id
$isFirst               = $session.IsFirst

Write-Host "`n━━━ Phase 5: Report（Orchestrator: $Orchestrator）━━━" -ForegroundColor Yellow

$vars = @{
    VERDICT_PATH      = $p.VerdictPath
    NEG_RESULTS_PATH  = $p.NegResultsPath
    SSOT_CHANGELOG    = $p.SsotChangelog
    IDEA_QUEUE_PATH   = $p.IdeaQueuePath
    CYCLE_REPORT_PATH = $p.CycleReportPath
}
$prompt = Expand-PromptTemplate (Join-Path $PromptsDir "orchestrator_phase5.md") $vars

Write-Host "[Phase 5] Orchestrator が cycle_report.md を生成中..." -ForegroundColor Yellow
Invoke-AI -AIName $Orchestrator -Prompt $prompt `
    -SessionIdRef ([ref]$orchestratorSessionId) -SessionFile $OrchestratorSessionFile `
    -IsFirst $isFirst

if (Test-Path $p.CycleReportPath) {
    Write-Host "[Phase 5] cycle_report.md 生成完了: $($p.CycleReportPath)" -ForegroundColor Green
} else {
    Write-Host "[WARNING] cycle_report.md が生成されませんでした。" -ForegroundColor DarkYellow
}

Write-Host "`n══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  AIRDP Cycle $CycleId 完了" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  サイクルレポート : $($p.CycleReportPath)" -ForegroundColor White
Write-Host "  Judge 判定       : $($p.VerdictPath)"     -ForegroundColor White
Write-Host "  否定的結果       : $($p.NegResultsPath)"  -ForegroundColor White
