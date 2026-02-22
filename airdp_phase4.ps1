# airdp_phase4.ps1 — Phase 4: Judge（verdict.md 生成）
#
# Usage:
#   .\airdp_phase4.ps1 -ProjectDir . -CycleId 01
#   .\airdp_phase4.ps1 -ProjectDir . -CycleId 01 -Judge claude

param (
    [Parameter(Mandatory=$false)] [string]$ProjectDir = ".",
    [Parameter(Mandatory=$true)]  [string]$CycleId,
    [Parameter(Mandatory=$false)]
    [ValidateSet("gemini","codex","claude","copilot")]
    [string]$Judge       = "claude",
    [Parameter(Mandatory=$false)] [string]$PromptsDir = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptDir "airdp_common.ps1")

if ($PromptsDir -eq "") { $PromptsDir = Join-Path $ScriptDir "airdp_prompts" }
if (-not (Test-Path $PromptsDir)) { throw "Prompts directory not found: $PromptsDir" }

$p = Resolve-AirdpPaths -ProjectDir $ProjectDir -CycleId $CycleId

if (-not (Test-Path $p.IterationsDir)) { throw "iterations/ not found: $($p.IterationsDir). Run Phase 3 first." }

$null = New-Item -ItemType Directory -Force -Path $p.SessionDir

$JudgeSessionFile = Join-Path $p.SessionDir "judge_session_id.txt"
$session          = Get-OrCreateSessionId -AIName $Judge -SessionFile $JudgeSessionFile
$judgeSessionId   = $session.Id
$isFirst          = $session.IsFirst

Write-Host "`n━━━ Phase 4: Judge（$Judge）━━━" -ForegroundColor Yellow

$vars = @{
    ITERATIONS_DIR   = $p.IterationsDir
    ROADMAP_PATH     = $p.RoadmapPath
    NEG_RESULTS_PATH = $p.NegResultsPath
    VERDICT_PATH     = $p.VerdictPath
}
$prompt = Expand-PromptTemplate (Join-Path $PromptsDir "judge_phase4.md") $vars

Write-Host "[Phase 4] Judge が verdict.md を生成中..." -ForegroundColor Blue
Invoke-AI -AIName $Judge -Prompt $prompt `
    -SessionIdRef ([ref]$judgeSessionId) -SessionFile $JudgeSessionFile `
    -IsFirst $isFirst

if (-not (Test-Path $p.VerdictPath)) {
    Write-Host "[WARNING] verdict.md が生成されませんでした。" -ForegroundColor DarkYellow
} else {
    Write-Host "[Phase 4] verdict.md 生成完了: $($p.VerdictPath)" -ForegroundColor Green

    $verdictContent = Get-Content $p.VerdictPath -Raw -Encoding utf8
    if ($verdictContent -match "REJECT") {
        Write-Host "  REJECT 判定あり → $($p.NegResultsPath) への記録を忘れずに。" -ForegroundColor Yellow
    }
}

Write-Host "`n[Phase 4] 完了。次のステップ:" -ForegroundColor Cyan
Write-Host "  .\airdp_phase5.ps1 -ProjectDir `"$ProjectDir`" -CycleId $CycleId" -ForegroundColor DarkGray
