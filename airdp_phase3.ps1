# airdp_phase3.ps1 - Phase 3: Execute (Researcher <-> Reviewer Auto Iteration)
#
# Usage:
#   .\airdp_phase3.ps1 -ProjectDir . -CycleId 01

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

# --- Auto Resume Logic ---
$iteration = 1
if (Test-Path $p.CycleCompletePath) {
    Write-Host "[SKIP] Cycle $CycleId is already complete (cycle_complete.md found)." -ForegroundColor Cyan
    exit 0
}

if (Test-Path $p.IterationsDir) {
    $existingIters = Get-ChildItem (Join-Path $p.IterationsDir "iter_*") | Where-Object { $_.Attributes -match "Directory" } | Sort-Object Name
    if ($existingIters.Count -gt 0) {
        $lastIterFolder = $existingIters[-1]
        if ($lastIterFolder.Name -match "iter_(\d+)") {
            $lastIterNum = [int]$matches[1]
            $reviewPath = Join-Path $lastIterFolder.FullName "review.md"

            if (Test-Path $reviewPath) {
                $iteration = $lastIterNum + 1
                Write-Host "[RESUME] Iteration $lastIterNum is complete. Starting from Iteration $iteration." -ForegroundColor Cyan
            } else {
                $iteration = $lastIterNum
                Write-Host "[RESUME] Iteration $iteration is incomplete. Resuming from here." -ForegroundColor Cyan
            }
        }
    }
}

# --- Session ID Initialization ---
$ResearcherSessionFile = Join-Path $p.SessionDir "researcher_session_id.txt"
$ReviewerSessionFile   = Join-Path $p.SessionDir "reviewer_session_id.txt"

$researcherSession   = Get-OrCreateSessionId -AIName $Researcher -SessionFile $ResearcherSessionFile
$reviewerSession     = Get-OrCreateSessionId -AIName $Reviewer   -SessionFile $ReviewerSessionFile
$ResearcherSessionId = $researcherSession.Id
$ReviewerSessionId   = $reviewerSession.Id
$isFirstResearcher   = $researcherSession.IsFirst
$isFirstReviewer     = $reviewerSession.IsFirst

Write-Host "`n=== Phase 3: Execute (Researcher: $Researcher / Reviewer: $Reviewer) ===" -ForegroundColor Yellow
Write-Host "  RoadmapPath : $($p.RoadmapPath)" -ForegroundColor Gray
Write-Host "  WorkDir     : $($p.CycleDir)"    -ForegroundColor Gray
Write-Host "  SsotDir     : $($p.SsotDir)"     -ForegroundColor Gray

$finished  = $false

while (-not $finished) {
    Write-Host "`n--- Iteration $iteration ---" -ForegroundColor Yellow

    $iterDir = Join-Path $p.IterationsDir ("iter_{0:D2}" -f $iteration)
    $null = New-Item -ItemType Directory -Force -Path (Join-Path $iterDir "code")

    # --- 1. Researcher ---
    $skipResearcher = $false
    if (Test-Path $p.LogPath) {
        $logContent = Get-Content $p.LogPath -Raw
        if ($logContent -match "Output Log - Iteration $iteration") {
            if (Test-Path (Join-Path $iterDir "researcher_report.md")) {
                $skipResearcher = $true
            }
        }
    }

    if ($skipResearcher) {
        Write-Host "[RESUME] Researcher outputs found. Skipping to Reviewer." -ForegroundColor Gray
    } else {
        Write-Host "Researcher ($Researcher) working..." -ForegroundColor Green

        $researcherVars = @{
            ROADMAP_PATH = $p.RoadmapPath
            NG_PATH      = $p.NgPath
            GO_PATH      = $p.GoPath
            WORK_DIR     = $p.CycleDir
            LOG_PATH     = $p.LogPath
            ITER_DIR     = $iterDir
            SSOT_DIR     = $p.SsotDir
            PROJECT_SSOT_LOADER = $p.ProjectSsotLoader
            PROJECT_SSOT_MODULE = $p.ProjectSsotModule
        }
        $promptResearcher = Expand-PromptTemplate (Join-Path $PromptsDir "researcher.md") $researcherVars

        Invoke-AI -AIName $Researcher -Prompt $promptResearcher `
            -SessionIdRef ([ref]$ResearcherSessionId) -SessionFile $ResearcherSessionFile `
            -IsFirst $isFirstResearcher
        $isFirstResearcher = $false

        if (Test-Path $p.GoPath) { Remove-Item $p.GoPath }
        if (Test-Path $p.NgPath) { Remove-Item $p.NgPath }
    }

    if (-not (Test-Path $p.LogPath)) {
        Write-Host "[ERROR] Researcher did not generate output_log.md. Skipping." -ForegroundColor Red
        $iteration++
        if ($iteration -gt $MaxIterations) { $finished = $true }
        continue
    }

    # --- 2. Reviewer ---
    Write-Host "Reviewer ($Reviewer) reviewing..." -ForegroundColor Magenta

    $reviewerVars = @{
        LOG_PATH              = $p.LogPath
        NG_PATH               = $p.NgPath
        GO_PATH               = $p.GoPath
        ROADMAP_PATH          = $p.RoadmapPath
        ITER_DIR              = $iterDir
        SSOT_DIR              = $p.SsotDir
        CYCLE_COMPLETE_PATH   = $p.CycleCompletePath
    }
    $promptReviewer = Expand-PromptTemplate (Join-Path $PromptsDir "reviewer.md") $reviewerVars

    Invoke-AI -AIName $Reviewer -Prompt $promptReviewer `
        -SessionIdRef ([ref]$ReviewerSessionId) -SessionFile $ReviewerSessionFile `
        -IsFirst $isFirstReviewer
    $isFirstReviewer = $false

    # --- 3. Decision ---
    if (Test-Path $p.GoPath) {
        Write-Host "[APPROVED] $($p.GoPath)" -ForegroundColor Green
        if (Test-Path $p.LogPath) { Remove-Item $p.LogPath }

        if (Test-Path $p.CycleCompletePath) {
            Write-Host "[Phase 3] All iterations complete (cycle_complete.md found)." -ForegroundColor Cyan
            $finished = $true
        } else {
            Write-Host "[Phase 3] Iteration approved. Continuing to next." -ForegroundColor Green
            $iteration++
        }
    } elseif (Test-Path $p.NgPath) {
        if (Test-Path p.CycleCompletePath) {
            Write-Host "[Phase 3] All iterations complete (cycle_complete.md found)." -ForegroundColor Cyan
            $finished = $true
        } else {
            Write-Host "[REJECTED] Addressing issues in next iteration." -ForegroundColor Red
            $iteration++
        }
    } else {
        Write-Host "[ERROR] No go.md or ng.md generated." -ForegroundColor DarkYellow
        $finished = $true
    }

    if ($iteration -gt $MaxIterations) {
        Write-Host "[LIMIT] Max iterations reached ($MaxIterations)." -ForegroundColor DarkYellow
        $finished = $true
    }
}

Write-Host "`n[Phase 3] Done. Next step:" -ForegroundColor Cyan
Write-Host "  .\airdp_phase4.ps1 -ProjectDir $ProjectDir -CycleId $CycleId" -ForegroundColor DarkGray
