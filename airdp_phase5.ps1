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
    [Parameter(Mandatory=$false)] [string]$PromptsDir   = "",
    [Parameter(Mandatory=$false)] [switch]$SkipNextSeed
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptDir "airdp_common.ps1")

if ($PromptsDir -eq "") { $PromptsDir = Join-Path $ScriptDir "airdp_prompts" }
if (-not (Test-Path $PromptsDir)) { throw "Prompts directory not found: $PromptsDir" }

$p = Resolve-AirdpPaths -ProjectDir $ProjectDir -CycleId $CycleId

$OrchestratorSessionFile = Join-Path $p.SessionDir "orchestrator_phase5_session_id.txt"
$session               = Get-OrCreateSessionId -AIName $Orchestrator -SessionFile $OrchestratorSessionFile
$orchestratorSessionId = $session.Id
$isFirst               = $session.IsFirst

Write-Host "`n━━━ Phase 5: Report（Orchestrator: $Orchestrator）━━━" -ForegroundColor Yellow

# 次サイクル番号を計算して seed パスを決める
$nextCycleId   = "{0:D2}" -f ([int]$CycleId + 1)
$nextCycleDir  = Join-Path $p.CyclesDir "cycle_$nextCycleId"
$nextSeedPath  = Join-Path $nextCycleDir "seed.md"

$vars = @{
    VERDICT_PATH      = $p.VerdictPath
    NEG_RESULTS_PATH  = $p.NegResultsPath
    CONSTANTS_PATH    = $p.ConstantsPath
    SSOT_CHANGELOG    = $p.SsotChangelog
    IDEA_QUEUE_PATH   = $p.IdeaQueuePath
    CYCLE_REPORT_PATH = $p.CycleReportPath
    NEXT_SEED_PATH    = $nextSeedPath
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

# ── 次サイクル seed.md の生成 ──────────────────────────────
if (-not $SkipNextSeed) {
    Write-Host "`n[Phase 5] 次サイクル (cycle_$nextCycleId) の seed.md 候補を生成中..." -ForegroundColor Yellow
    if (-not (Test-Path $nextCycleDir)) {
        New-Item -ItemType Directory -Path $nextCycleDir | Out-Null
    }
    # cycle_report.md が生成済みの場合のみ実行（入力として使うため）
    if (Test-Path $p.CycleReportPath) {
        Invoke-AI -AIName $Orchestrator -Prompt $prompt `
            -SessionIdRef ([ref]$orchestratorSessionId) -SessionFile $OrchestratorSessionFile `
            -IsFirst $false
        if (Test-Path $nextSeedPath) {
            Write-Host "[Phase 5] seed.md 候補生成完了: $nextSeedPath" -ForegroundColor Green
            Write-Host "  ※ DRAFT です。人間による精査・承認後に Cycle $nextCycleId を開始してください。" -ForegroundColor DarkYellow
        } else {
            Write-Host "[WARNING] seed.md 候補が生成されませんでした。手動で作成してください。" -ForegroundColor DarkYellow
        }
    } else {
        Write-Host "[WARNING] cycle_report.md がないため seed.md 候補の生成をスキップしました。" -ForegroundColor DarkYellow
    }
}

Write-Host "`n══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  AIRDP Cycle $CycleId 完了" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  サイクルレポート : $($p.CycleReportPath)" -ForegroundColor White
Write-Host "  Judge 判定       : $($p.VerdictPath)"     -ForegroundColor White
Write-Host "  否定的結果       : $($p.NegResultsPath)"  -ForegroundColor White
if (-not $SkipNextSeed) {
    Write-Host "  次サイクル seed  : $nextSeedPath (DRAFT)" -ForegroundColor White
}
