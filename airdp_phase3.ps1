# airdp_phase3.ps1 — Phase 3: Execute（Researcher ↔ Reviewer 自動イテレーション）
#
# Usage:
#   .\airdp_phase3.ps1 -ProjectDir . -CycleId 01
#   .\airdp_phase3.ps1 -ProjectDir . -CycleId 01 -Researcher gemini -Reviewer claude -MaxIterations 5

param (
    [Parameter(Mandatory=$false)] [string]$ProjectDir    = ".",
    [Parameter(Mandatory=$true)]  [string]$CycleId,
    [Parameter(Mandatory=$false)]
    [ValidateSet("gemini","codex","claude","copilot")]
    [string]$Researcher    = "gemini",
    [Parameter(Mandatory=$false)]
    [ValidateSet("gemini","codex","claude","copilot")]
    [string]$Reviewer      = "claude",
    [Parameter(Mandatory=$false)] [int]$MaxIterations    = 10,
    [Parameter(Mandatory=$false)] [string]$PromptsDir    = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptDir "airdp_common.ps1")

if ($PromptsDir -eq "") { $PromptsDir = Join-Path $ScriptDir "airdp_prompts" }
if (-not (Test-Path $PromptsDir)) { throw "Prompts directory not found: $PromptsDir" }

$p = Resolve-AirdpPaths -ProjectDir $ProjectDir -CycleId $CycleId

if (-not (Test-Path $p.RoadmapPath)) { throw "roadmap.md not found: $($p.RoadmapPath). Run Phase 2 first." }
if (-not (Test-Path $p.SsotDir))    { throw "SSoT directory not found: $($p.SsotDir). Run ssot initialization first." }

$null = New-Item -ItemType Directory -Force -Path $p.IterationsDir
$null = New-Item -ItemType Directory -Force -Path $p.SessionDir

# ── セッション ID の取得・初期化 ──────────────
$ResearcherSessionFile = Join-Path $p.SessionDir "researcher_session_id.txt"
$ReviewerSessionFile   = Join-Path $p.SessionDir "reviewer_session_id.txt"

$researcherSession   = Get-OrCreateSessionId -AIName $Researcher -SessionFile $ResearcherSessionFile
$reviewerSession     = Get-OrCreateSessionId -AIName $Reviewer   -SessionFile $ReviewerSessionFile
$ResearcherSessionId = $researcherSession.Id
$ReviewerSessionId   = $reviewerSession.Id
$isFirstResearcher   = $researcherSession.IsFirst
$isFirstReviewer     = $reviewerSession.IsFirst

Write-Host "`n━━━ Phase 3: Execute（Researcher: $Researcher / Reviewer: $Reviewer）━━━" -ForegroundColor Yellow
Write-Host "  RoadmapPath : $($p.RoadmapPath)" -ForegroundColor Gray
Write-Host "  WorkDir     : $($p.CycleDir)"    -ForegroundColor Gray
Write-Host "  SsotDir     : $($p.SsotDir)"     -ForegroundColor Gray

$finished  = $false
$iteration = 1

while (-not $finished) {
    Write-Host "`n━━━ Iteration $iteration ━━━" -ForegroundColor Yellow

    $iterDir = Join-Path $p.IterationsDir ("iter_{0:D2}" -f $iteration)
    $null = New-Item -ItemType Directory -Force -Path (Join-Path $iterDir "code")

    # ── 1. Researcher ────────────────────────
    Write-Host "[Researcher: $Researcher] 作業中..." -ForegroundColor Green

    $researcherVars = @{
        ROADMAP_PATH = $p.RoadmapPath
        NG_PATH      = $p.NgPath
        GO_PATH      = $p.GoPath
        WORK_DIR     = $p.CycleDir
        LOG_PATH     = $p.LogPath
        ITER_DIR     = $iterDir
        SSOT_DIR     = $p.SsotDir
    }
    $promptResearcher = Expand-PromptTemplate (Join-Path $PromptsDir "researcher.md") $researcherVars

    Invoke-AI -AIName $Researcher -Prompt $promptResearcher `
        -SessionIdRef ([ref]$ResearcherSessionId) -SessionFile $ResearcherSessionFile `
        -IsFirst $isFirstResearcher
    $isFirstResearcher = $false

    # go.md / ng.md をクリア（Reviewer 実行前に）
    if (Test-Path $p.GoPath) { Remove-Item $p.GoPath }
    if (Test-Path $p.NgPath) { Remove-Item $p.NgPath }

    if (-not (Test-Path $p.LogPath)) {
        Write-Host "[ERROR] Researcher が output_log.md を生成しませんでした。スキップ。" -ForegroundColor Red
        $iteration++
        if ($iteration -gt $MaxIterations) { $finished = $true }
        continue
    }

    # ── 2. Reviewer ──────────────────────────
    Write-Host "`n[Reviewer: $Reviewer] 査読中..." -ForegroundColor Magenta

    $reviewerVars = @{
        LOG_PATH     = $p.LogPath
        NG_PATH      = $p.NgPath
        GO_PATH      = $p.GoPath
        ROADMAP_PATH = $p.RoadmapPath
        ITER_DIR     = $iterDir
        SSOT_DIR     = $p.SsotDir
    }
    $promptReviewer = Expand-PromptTemplate (Join-Path $PromptsDir "reviewer.md") $reviewerVars

    Invoke-AI -AIName $Reviewer -Prompt $promptReviewer `
        -SessionIdRef ([ref]$ReviewerSessionId) -SessionFile $ReviewerSessionFile `
        -IsFirst $isFirstReviewer
    $isFirstReviewer = $false

    # ── 3. 判定 ──────────────────────────────
    if (Test-Path $p.GoPath) {
        Write-Host "`n[APPROVED] $($p.GoPath)" -ForegroundColor Green
        $finished = $true
        if (Test-Path $p.LogPath) { Remove-Item $p.LogPath }
    } elseif (Test-Path $p.NgPath) {
        Write-Host "`n[REJECTED] 次イテレーションで対応します。" -ForegroundColor Red
        $iteration++
    } else {
        Write-Host "`n[ERROR] go.md も ng.md も生成されませんでした。" -ForegroundColor DarkYellow
        $finished = $true
    }

    if ($iteration -gt $MaxIterations) {
        Write-Host "`n[LIMIT] 最大イテレーション数 ($MaxIterations) に到達。" -ForegroundColor DarkYellow
        $finished = $true
    }
}

Write-Host "`n[Phase 3] 完了。次のステップ:" -ForegroundColor Cyan
Write-Host "  .\airdp_phase4.ps1 -ProjectDir `"$ProjectDir`" -CycleId $CycleId" -ForegroundColor DarkGray
