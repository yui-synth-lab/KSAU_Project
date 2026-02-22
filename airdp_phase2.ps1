# airdp_phase2.ps1 — Phase 2: Plan（Orchestrator が roadmap.md を生成）
#
# Usage:
#   .\airdp_phase2.ps1 -ProjectDir . -CycleId 01 -SeedPath .\cycles\cycle_01\seed.md
#   .\airdp_phase2.ps1 -ProjectDir . -CycleId 02 -Orchestrator gemini -SkipApproval

param (
    [Parameter(Mandatory=$false)] [string]$ProjectDir  = ".",
    [Parameter(Mandatory=$true)]  [string]$CycleId,
    [Parameter(Mandatory=$false)] [string]$SeedPath    = "",
    [Parameter(Mandatory=$false)]
    [ValidateSet("gemini","codex","claude","copilot")]
    [string]$Orchestrator = "gemini",
    [Parameter(Mandatory=$false)] [switch]$SkipApproval,
    [Parameter(Mandatory=$false)] [string]$PromptsDir  = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptDir "airdp_common.ps1")

if ($PromptsDir -eq "") { $PromptsDir = Join-Path $ScriptDir "airdp_prompts" }
if (-not (Test-Path $PromptsDir)) { throw "Prompts directory not found: $PromptsDir" }

$p = Resolve-AirdpPaths -ProjectDir $ProjectDir -CycleId $CycleId
$null = New-Item -ItemType Directory -Force -Path $p.CycleDir
$null = New-Item -ItemType Directory -Force -Path $p.SessionDir

$SeedPath_resolved = if ($SeedPath -ne "" -and (Test-Path $SeedPath)) {
    (Resolve-Path $SeedPath).Path
} else {
    Join-Path $p.CycleDir "seed.md"
}
if (-not (Test-Path $SeedPath_resolved)) { throw "seed.md not found: $SeedPath_resolved" }

$OrchestratorSessionFile = Join-Path $p.SessionDir "orchestrator_phase2_session_id.txt"
$session   = Get-OrCreateSessionId -AIName $Orchestrator -SessionFile $OrchestratorSessionFile
$sessionId = $session.Id
$isFirst   = $session.IsFirst

Write-Host "`n━━━ Phase 2: Plan（Orchestrator: $Orchestrator）━━━" -ForegroundColor Yellow

$approved = $false

while (-not $approved) {
    $vars = @{
        SEED_PATH        = $SeedPath_resolved
        ROADMAP_PATH     = $p.RoadmapPath
        SSOT_DIR         = $p.SsotDir
        NEG_RESULTS_PATH = $p.NegResultsPath
        CONSTANTS_PATH   = $p.ConstantsPath
    }
    $prompt = Expand-PromptTemplate (Join-Path $PromptsDir "orchestrator_phase2.md") $vars

    Write-Host "[Phase 2] Orchestrator が roadmap.md を生成中..." -ForegroundColor Green
    Invoke-AI -AIName $Orchestrator -Prompt $prompt `
        -SessionIdRef ([ref]$sessionId) -SessionFile $OrchestratorSessionFile `
        -IsFirst $isFirst
    $isFirst = $false

    if (-not (Test-Path $p.RoadmapPath)) {
        Write-Host "[ERROR] roadmap.md が生成されませんでした。" -ForegroundColor Red
        $retry = Read-Host "再試行しますか？ [y/n]"
        if ($retry -ne "y") { exit 1 }
        continue
    }

    if ($SkipApproval) {
        Write-Host "[Phase 2] SkipApproval: 承認をスキップします。" -ForegroundColor DarkYellow
        $approved = $true
    } else {
        Write-Host "`n[Phase 2] roadmap.md が生成されました: $($p.RoadmapPath)" -ForegroundColor Cyan
        Write-Host "  [go]   → Phase 3 に進む" -ForegroundColor Green
        Write-Host "  [edit] → 修正を依頼して再生成" -ForegroundColor Yellow
        Write-Host "  [stop] → 中断" -ForegroundColor Red

        $decision = Read-Host "判断"
        switch ($decision.Trim().ToLower()) {
            "go" {
                $approved = $true
                Write-Host "[Phase 2] 承認。Phase 3 に進んでください:" -ForegroundColor Green
                Write-Host "  .\airdp_phase3.ps1 -ProjectDir `"$ProjectDir`" -CycleId $CycleId" -ForegroundColor DarkGray
            }
            "edit" {
                $editRequest = Read-Host "修正内容を入力してください"
                $editPrompt  = "以下の修正を行い、roadmap.md を再生成してください:`n$editRequest`n`n現在の roadmap.md: $($p.RoadmapPath)"
                Invoke-AI -AIName $Orchestrator -Prompt $editPrompt `
                    -SessionIdRef ([ref]$sessionId) -SessionFile $OrchestratorSessionFile -IsFirst $false
            }
            "stop" { Write-Host "中断しました。" -ForegroundColor Red; exit 1 }
            default { Write-Host "go / edit / stop を入力してください。" -ForegroundColor Yellow }
        }
    }
}
