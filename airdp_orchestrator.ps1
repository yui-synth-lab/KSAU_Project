# airdp_orchestrator.ps1 — AIRDP 全フェーズ連続実行
# 各フェーズを個別に実行したい場合は airdp_phase2/3/4/5.ps1 を直接呼ぶこと
#
# Usage:
#   .\airdp_orchestrator.ps1 -ProjectDir . -CycleId 01 -SeedPath .\cycles\cycle_01\seed.md
#   .\airdp_orchestrator.ps1 -ProjectDir . -CycleId auto -Orchestrator gemini -Researcher gemini -Reviewer claude -Judge claude
#   .\airdp_orchestrator.ps1 -ProjectDir . -CycleId 02 -SkipApproval   # CI 用
#
# フェーズ個別実行:
#   .\airdp_phase2.ps1 -ProjectDir . -CycleId 01 -SeedPath .\cycles\cycle_01\seed.md
#   .\airdp_phase3.ps1 -ProjectDir . -CycleId 01 -Researcher gemini -Reviewer claude
#   .\airdp_phase4.ps1 -ProjectDir . -CycleId 01 -Judge claude
#   .\airdp_phase5.ps1 -ProjectDir . -CycleId 01 -Orchestrator gemini

param (
    [Parameter(Mandatory=$false)] [string]$ProjectDir   = ".",
    [Parameter(Mandatory=$false)] [string]$CycleId      = "auto",
    [Parameter(Mandatory=$false)] [string]$SeedPath     = "",
    [Parameter(Mandatory=$false)]
    [ValidateSet("gemini","codex","claude","copilot")]
    [string]$Orchestrator = "gemini",
    [Parameter(Mandatory=$false)]
    [ValidateSet("gemini","codex","claude","copilot")]
    [string]$Researcher   = "gemini",
    [Parameter(Mandatory=$false)]
    [ValidateSet("gemini","codex","claude","copilot")]
    [string]$Reviewer     = "claude",
    [Parameter(Mandatory=$false)]
    [ValidateSet("gemini","codex","claude","copilot")]
    [string]$Judge        = "claude",
    [Parameter(Mandatory=$false)] [int]$MaxIterations   = 10,
    [Parameter(Mandatory=$false)] [switch]$SkipApproval,
    [Parameter(Mandatory=$false)] [string]$PromptsDir   = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptDir "airdp_common.ps1")

# ── CycleId の自動採番 ───────────────────────
$ProjectDir = (Resolve-Path $ProjectDir).Path
$CyclesDir  = Join-Path $ProjectDir "cycles"
$null = New-Item -ItemType Directory -Force -Path $CyclesDir

if ($CycleId -eq "auto") {
    $existing = Get-ChildItem $CyclesDir -Directory -Filter "cycle_*" -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -match "^cycle_\d+$" } | Sort-Object Name
    $CycleId = if ($existing.Count -eq 0) { "01" } else {
        "{0:D2}" -f ([int]($existing[-1].Name -replace "cycle_", "") + 1)
    }
}

Write-Host "`n══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  AIRDP Pipeline 起動 — Cycle $CycleId"  -ForegroundColor Cyan
Write-Host "══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Orchestrator: $Orchestrator" -ForegroundColor Yellow
Write-Host "  Researcher  : $Researcher"  -ForegroundColor Green
Write-Host "  Reviewer    : $Reviewer"    -ForegroundColor Magenta
Write-Host "  Judge       : $Judge"       -ForegroundColor Blue

$commonArgs = @("-ProjectDir", $ProjectDir, "-CycleId", $CycleId)
if ($PromptsDir -ne "") { $commonArgs += @("-PromptsDir", $PromptsDir) }

# ── Phase 2 ─────────────────────────────────
$phase2Args = $commonArgs + @("-Orchestrator", $Orchestrator)
if ($SeedPath -ne "") { $phase2Args += @("-SeedPath", $SeedPath) }
if ($SkipApproval)    { $phase2Args += "-SkipApproval" }
& (Join-Path $ScriptDir "airdp_phase2.ps1") @phase2Args

# ── Phase 3 ─────────────────────────────────
$EmergencyStopPath = Join-Path $ProjectDir "audit" "emergency_stops" "emergency_stop_cycle${CycleId}.md"
$null = New-Item -ItemType Directory -Force -Path (Split-Path $EmergencyStopPath)
$phase3Aborted = $false

try {
    $phase3Args = $commonArgs + @("-Researcher", $Researcher, "-Reviewer", $Reviewer, "-MaxIterations", $MaxIterations)
    & (Join-Path $ScriptDir "airdp_phase3.ps1") @phase3Args
} catch {
    if ($_.Exception -is [System.Management.Automation.PipelineStoppedException]) {
        $stopReason = Read-Host "`n[緊急停止] 停止理由を入力してください"
        @"
# Emergency Stop — Cycle $CycleId
**停止日時:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**停止理由:** $stopReason
Phase 4 (Judge) に直接移行します。
"@ | Out-File -FilePath $EmergencyStopPath -Encoding utf8
        Write-Host "  emergency_stop.md: $EmergencyStopPath" -ForegroundColor Yellow
    } else { throw }
}

# ── Phase 4 ─────────────────────────────────
$phase4Args = $commonArgs + @("-Judge", $Judge)
& (Join-Path $ScriptDir "airdp_phase4.ps1") @phase4Args

# ── Phase 5 ─────────────────────────────────
$phase5Args = $commonArgs + @("-Orchestrator", $Orchestrator)
& (Join-Path $ScriptDir "airdp_phase5.ps1") @phase5Args
