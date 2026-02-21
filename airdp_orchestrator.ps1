# AIRDP Orchestrator Script — Phase 1/2/4/5 管理
# AIRDPフレームワーク (AIRDP_Framework_Design.md) の全5フェーズを管理する
# Phase 3 は airdp_research_loop.ps1 に委譲する
#
# Usage:
#   .\airdp_orchestrator.ps1 -ProjectDir "." -SeedPath "my_seed.md"
#   .\airdp_orchestrator.ps1 -ProjectDir "." -CycleId "02" -Orchestrator gemini -Researcher codex -Reviewer claude -Judge copilot
#   .\airdp_orchestrator.ps1 -ProjectDir "." -SkipApproval  # CI / 自動実行用
#
# ロール → AI の対応（全4種から自由に選択）:
#   Orchestrator : Phase 2 (roadmap生成) / Phase 5 (報告書生成)
#   Researcher   : Phase 3 (airdp_research_loop.ps1 に渡す)
#   Reviewer     : Phase 3 (airdp_research_loop.ps1 に渡す)
#   Judge        : Phase 4 (verdict.md 生成)
#
# 人間の介入ポイント:
#   Phase 2 完了後 → roadmap.md の承認（"go" / "edit" / "stop"）
#   Phase 3 中     → Ctrl+C で緊急停止（emergency_stop.md を記録して Phase 4 へ）

param (
    [Parameter(Mandatory=$false)]
    [string]$ProjectDir = ".",

    # "auto" で cycle_01, cycle_02 ... と自動採番
    [Parameter(Mandatory=$false)]
    [string]$CycleId = "auto",

    # 空の場合は cycles/cycle_NN/seed.md を探す
    [Parameter(Mandatory=$false)]
    [string]$SeedPath = "",

    [Parameter(Mandatory=$false)]
    [ValidateSet("gemini","codex","claude","copilot")]
    [string]$Orchestrator = "gemini",

    [Parameter(Mandatory=$false)]
    [ValidateSet("gemini","codex","claude","copilot")]
    [string]$Researcher = "gemini",

    [Parameter(Mandatory=$false)]
    [ValidateSet("gemini","codex","claude","copilot")]
    [string]$Reviewer = "claude",

    [Parameter(Mandatory=$false)]
    [ValidateSet("gemini","codex","claude","copilot")]
    [string]$Judge = "claude",

    [Parameter(Mandatory=$false)]
    [int]$MaxIterations = 10,

    # Phase 2 の人間承認をスキップ（CI / 全自動実行用）
    [Parameter(Mandatory=$false)]
    [switch]$SkipApproval,

    # プロンプトテンプレートのディレクトリ
    [Parameter(Mandatory=$false)]
    [string]$PromptsDir = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# ──────────────────────────────────────────
# プロンプトディレクトリの解決
# ──────────────────────────────────────────
if ($PromptsDir -eq "") {
    $PromptsDir = Join-Path $ScriptDir "airdp_prompts"
}
if (-not (Test-Path $PromptsDir)) {
    throw "Prompts directory not found: $PromptsDir"
}

# ──────────────────────────────────────────
# プロジェクトディレクトリの解決（絶対パスに変換）
# ──────────────────────────────────────────
$ProjectDir = (Resolve-Path $ProjectDir).Path

# ──────────────────────────────────────────
# ユーティリティ関数
# ──────────────────────────────────────────
function Read-SessionId([string]$Path) {
    if (Test-Path $Path) {
        $id = (Get-Content $Path -Raw).Trim()
        if ($id -ne "") { return $id }
    }
    return $null
}

function Save-SessionId([string]$Path, [string]$Id) {
    $Id | Out-File -FilePath $Path -Encoding utf8 -NoNewline
}

function Expand-PromptTemplate([string]$TemplatePath, [hashtable]$Vars) {
    if (-not (Test-Path $TemplatePath)) { throw "Template not found: $TemplatePath" }
    $text = Get-Content $TemplatePath -Raw -Encoding utf8
    foreach ($key in $Vars.Keys) {
        $text = $text -replace [regex]::Escape("{$key}"), $Vars[$key]
    }
    return $text
}

# ──────────────────────────────────────────
# AI 呼び出し関数（research_loop と共通の実装）
# ──────────────────────────────────────────
function Get-LatestGeminiSessionId {
    $sessions = gemini --list-sessions 2>$null
    foreach ($line in $sessions) {
        if ($line -match "\[([a-f0-9\-]{36})\]") { return $matches[1] }
    }
    return $null
}

function Invoke-Gemini([string]$Prompt, [ref]$SessionIdRef, [string]$SessionFile, [string]$GeminiMdSrc = "") {
    if ($GeminiMdSrc -ne "" -and (Test-Path $GeminiMdSrc)) {
        Copy-Item $GeminiMdSrc "GEMINI.md" -Force
    }
    if ($null -eq $SessionIdRef.Value) {
        gemini -p $Prompt -y
        $newId = Get-LatestGeminiSessionId
        if ($newId) {
            $SessionIdRef.Value = $newId
            Save-SessionId $SessionFile $newId
            Write-Host "  Gemini session (new): $newId" -ForegroundColor DarkGray
        }
    } else {
        Write-Host "  Gemini session (resume): $($SessionIdRef.Value)" -ForegroundColor DarkGray
        gemini -r $SessionIdRef.Value -p $Prompt -y
    }
}

function Invoke-Codex([string]$Prompt, [ref]$SessionIdRef, [string]$SessionFile) {
    if ($null -eq $SessionIdRef.Value) {
        $lines = codex exec --json --dangerously-bypass-approvals-and-sandbox $Prompt 2>&1
        foreach ($line in $lines) {
            Write-Host $line
            try {
                $obj = $line | ConvertFrom-Json -ErrorAction SilentlyContinue
                if ($obj -and $obj.type -eq "thread.started" -and $obj.thread_id) {
                    $SessionIdRef.Value = $obj.thread_id
                    Save-SessionId $SessionFile $obj.thread_id
                    Write-Host "  Codex session (new): $($obj.thread_id)" -ForegroundColor DarkGray
                }
            } catch { }
        }
    } else {
        Write-Host "  Codex session (resume): $($SessionIdRef.Value)" -ForegroundColor DarkGray
        codex exec resume --json --dangerously-bypass-approvals-and-sandbox $SessionIdRef.Value $Prompt 2>&1 |
            ForEach-Object { Write-Host $_ }
    }
}

function Invoke-Claude([string]$Prompt, [ref]$SessionIdRef, [string]$SessionFile, [bool]$IsFirst) {
    $envBackup = $env:CLAUDECODE
    $env:CLAUDECODE = $null
    try {
        if ($IsFirst) {
            Write-Host "  Claude session (new): $($SessionIdRef.Value)" -ForegroundColor DarkGray
            claude --session-id $SessionIdRef.Value -p $Prompt --verbose `
                --allowedTools "Read,Write,Edit,Bash,Glob,Grep" `
                --permission-mode bypassPermissions
        } else {
            Write-Host "  Claude session (resume): $($SessionIdRef.Value)" -ForegroundColor DarkGray
            claude --resume $SessionIdRef.Value -p $Prompt --verbose `
                --allowedTools "Read,Write,Edit,Bash,Glob,Grep" `
                --permission-mode bypassPermissions
        }
    } finally {
        $env:CLAUDECODE = $envBackup
    }
}

function Invoke-Copilot([string]$Prompt, [ref]$SessionIdRef) {
    Write-Host "  Copilot session: $($SessionIdRef.Value)" -ForegroundColor DarkGray
    copilot --resume $SessionIdRef.Value -p $Prompt --yolo
}

function Invoke-AI {
    param(
        [string]$AIName,
        [string]$Prompt,
        [ref]$SessionIdRef,
        [string]$SessionFile,
        [bool]$IsFirst = $false,
        [string]$GeminiMdSrc = ""
    )
    switch ($AIName) {
        "gemini"  { Invoke-Gemini  -Prompt $Prompt -SessionIdRef $SessionIdRef -SessionFile $SessionFile -GeminiMdSrc $GeminiMdSrc }
        "codex"   { Invoke-Codex   -Prompt $Prompt -SessionIdRef $SessionIdRef -SessionFile $SessionFile }
        "claude"  { Invoke-Claude  -Prompt $Prompt -SessionIdRef $SessionIdRef -SessionFile $SessionFile -IsFirst $IsFirst }
        "copilot" { Invoke-Copilot -Prompt $Prompt -SessionIdRef $SessionIdRef }
    }
}

# ──────────────────────────────────────────
# Phase 1: サイクルディレクトリとファイルパスの確定
# ──────────────────────────────────────────
Write-Host "`n══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  AIRDP Pipeline 起動" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ProjectDir  : $ProjectDir"  -ForegroundColor Gray
Write-Host "  Orchestrator: $Orchestrator" -ForegroundColor Yellow
Write-Host "  Researcher  : $Researcher"  -ForegroundColor Green
Write-Host "  Reviewer    : $Reviewer"    -ForegroundColor Magenta
Write-Host "  Judge       : $Judge"       -ForegroundColor Blue

# サイクル番号の自動採番
$CyclesDir = Join-Path $ProjectDir "cycles"
$null = New-Item -ItemType Directory -Force -Path $CyclesDir

if ($CycleId -eq "auto") {
    $existing = Get-ChildItem $CyclesDir -Directory -Filter "cycle_*" -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -match "^cycle_\d+$" } |
                Sort-Object Name
    if ($existing.Count -eq 0) {
        $CycleId = "01"
    } else {
        $lastNum = [int]($existing[-1].Name -replace "cycle_", "")
        $CycleId = "{0:D2}" -f ($lastNum + 1)
    }
}

$CycleDir = Join-Path $CyclesDir "cycle_$CycleId"

# ディレクトリ構造を作成
$null = New-Item -ItemType Directory -Force -Path $CycleDir
$null = New-Item -ItemType Directory -Force -Path (Join-Path $CycleDir "iterations")
$SsotDir = Join-Path $ProjectDir "ssot"
$null = New-Item -ItemType Directory -Force -Path (Join-Path $SsotDir "data\raw")
$null = New-Item -ItemType Directory -Force -Path (Join-Path $SsotDir "data\processed")
$null = New-Item -ItemType Directory -Force -Path (Join-Path $SsotDir "hypotheses")
$null = New-Item -ItemType Directory -Force -Path (Join-Path $ProjectDir "audit\communication")
$null = New-Item -ItemType Directory -Force -Path (Join-Path $ProjectDir "audit\ssot_checks")
$null = New-Item -ItemType Directory -Force -Path (Join-Path $ProjectDir "audit\emergency_stops")
$null = New-Item -ItemType Directory -Force -Path (Join-Path $ProjectDir "archive")

# ファイルパスの定義
$SeedPath_resolved = if ($SeedPath -ne "" -and (Test-Path $SeedPath)) {
    (Resolve-Path $SeedPath).Path
} else {
    Join-Path $CycleDir "seed.md"
}
$RoadmapPath      = Join-Path $CycleDir "roadmap.md"
$VerdictPath      = Join-Path $CycleDir "verdict.md"
$CycleReportPath  = Join-Path $CycleDir "cycle_report.md"
$NegResultsPath   = Join-Path $ProjectDir "NEGATIVE_RESULTS_INDEX.md"
$IdeaQueuePath    = Join-Path $ProjectDir "idea_queue.md"
$SsotChangelog    = Join-Path $SsotDir "changelog.json"
$ConstantsPath    = Join-Path $SsotDir "constants.json"

Write-Host "`n  Cycle: cycle_$CycleId → $CycleDir" -ForegroundColor Gray

# セッション ID 永続化ディレクトリ（サイクルまたいで継続可能）
$SessionDir = Join-Path $CycleDir ".airdp_sessions"
$null = New-Item -ItemType Directory -Force -Path $SessionDir
$OrchestratorSessionFile = Join-Path $SessionDir "orchestrator_session_id.txt"
$JudgeSessionFile        = Join-Path $SessionDir "judge_session_id.txt"

$OrchestratorSessionId = Read-SessionId $OrchestratorSessionFile
$JudgeSessionId        = Read-SessionId $JudgeSessionFile

if ($Orchestrator -in @("claude","copilot") -and $null -eq $OrchestratorSessionId) {
    $OrchestratorSessionId = [System.Guid]::NewGuid().ToString()
    Save-SessionId $OrchestratorSessionFile $OrchestratorSessionId
}
if ($Judge -in @("claude","copilot") -and $null -eq $JudgeSessionId) {
    $JudgeSessionId = [System.Guid]::NewGuid().ToString()
    Save-SessionId $JudgeSessionFile $JudgeSessionId
}

# SSoT の初期化（constants.json が存在しなければ雛形を作成）
if (-not (Test-Path $ConstantsPath)) {
    $defaultConstants = @{
        "_meta" = @{
            "created"     = (Get-Date -Format "yyyy-MM-dd")
            "description" = "AIRDP Single Source of Truth"
            "version"     = 1
        }
        "statistical_thresholds" = @{
            "bonferroni_base_alpha"    = 0.05
            "fpr_rejection_threshold"  = 0.50
            "monte_carlo_n_trials"     = 10000
        }
        "pipeline_limits" = @{
            "max_hypotheses_per_seed"      = 3
            "max_iterations_per_hypothesis" = 5
            "max_modify_count"             = 2
            "consecutive_stop_limit"       = 2
        }
    } | ConvertTo-Json -Depth 5
    $defaultConstants | Out-File -FilePath $ConstantsPath -Encoding utf8
    Write-Host "  SSoT初期化: $ConstantsPath を作成しました。" -ForegroundColor DarkGray
}

# idea_queue.md が存在しなければ作成
if (-not (Test-Path $IdeaQueuePath)) {
    "# AIRDP Idea Queue`n`nPhase 3 実行中に思いついたアイデアをここに追記してください。`n現在のサイクルには影響しません。次のサイクルの seed.md の候補になります。`n`n---`n" |
        Out-File -FilePath $IdeaQueuePath -Encoding utf8
}

# ──────────────────────────────────────────
# seed.md のバリデーション
# ──────────────────────────────────────────
Write-Host "`n━━━ Phase 1: Seed ━━━" -ForegroundColor Yellow

if (-not (Test-Path $SeedPath_resolved)) {
    Write-Host "[Phase 1] seed.md が見つかりません: $SeedPath_resolved" -ForegroundColor Red
    Write-Host "以下のフォーマットで seed.md を作成してください:`n" -ForegroundColor Yellow
    Write-Host "# Seed: [タイトル]`n`n## What`n[何を調べたいか]`n`n## Why`n[なぜ面白いか]`n`n## Boundary`n[何が出たら失敗と認めるか]`n" -ForegroundColor Gray
    $createSeed = Read-Host "seed.md を今すぐ作成しますか？ [y/n]"
    if ($createSeed -eq "y") {
        $seedTitle    = Read-Host "タイトル (What)"
        $seedWhy      = Read-Host "動機 (Why)"
        $seedBoundary = Read-Host "撤退条件 (Boundary)"
        $seedContent = @"
# Seed: $seedTitle

## What
$seedTitle

## Why
$seedWhy

## Boundary
$seedBoundary
"@
        $seedContent | Out-File -FilePath $SeedPath_resolved -Encoding utf8
        Write-Host "seed.md を作成しました: $SeedPath_resolved" -ForegroundColor Green
    } else {
        Write-Host "中断します。seed.md を作成してから再実行してください。" -ForegroundColor Red
        exit 1
    }
}

# seed.md の3要素チェック
$seedContent = Get-Content $SeedPath_resolved -Raw -Encoding utf8
$hasWhat     = $seedContent -match "## What"
$hasWhy      = $seedContent -match "## Why"
$hasBoundary = $seedContent -match "## Boundary"

Write-Host "[Phase 1] seed.md バリデーション:" -ForegroundColor Cyan
Write-Host "  What    : $(if ($hasWhat) { '✓' } else { '✗ 不足' })"
Write-Host "  Why     : $(if ($hasWhy)  { '✓' } else { '✗ 不足' })"
Write-Host "  Boundary: $(if ($hasBoundary) { '✓' } else { '△ 不足 → Orchestratorが補完します' })"

# ──────────────────────────────────────────
# Phase 2: Orchestrator → roadmap.md 生成
# ──────────────────────────────────────────
Write-Host "`n━━━ Phase 2: Plan（Orchestrator: $Orchestrator）━━━" -ForegroundColor Yellow

$isFirstOrchestrator = $true
$approved = $false

while (-not $approved) {
    $phase2Vars = @{
        SEED_PATH      = $SeedPath_resolved
        ROADMAP_PATH   = $RoadmapPath
        SSOT_DIR       = $SsotDir
        NEG_RESULTS_PATH = $NegResultsPath
        CONSTANTS_PATH = $ConstantsPath
    }
    $promptPhase2 = Expand-PromptTemplate (Join-Path $PromptsDir "orchestrator_phase2.md") $phase2Vars

    Write-Host "[Phase 2] Orchestrator が roadmap.md を生成中..." -ForegroundColor Green
    Invoke-AI -AIName $Orchestrator -Prompt $promptPhase2 `
        -SessionIdRef ([ref]$OrchestratorSessionId) -SessionFile $OrchestratorSessionFile `
        -IsFirst $isFirstOrchestrator -GeminiMdSrc "GEMINI-orchestrator.md"
    $isFirstOrchestrator = $false

    if (-not (Test-Path $RoadmapPath)) {
        Write-Host "[ERROR] Orchestrator が roadmap.md を生成しませんでした。" -ForegroundColor Red
        $retry = Read-Host "再試行しますか？ [y/n]"
        if ($retry -ne "y") { exit 1 }
        continue
    }

    # 人間の承認フェーズ
    if ($SkipApproval) {
        Write-Host "[Phase 2] -SkipApproval が指定されているため、承認をスキップします。" -ForegroundColor DarkYellow
        $approved = $true
    } else {
        Write-Host "`n[Phase 2] roadmap.md が生成されました。" -ForegroundColor Cyan
        Write-Host "  ファイル: $RoadmapPath" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  以下のコマンドを入力してください:" -ForegroundColor White
        Write-Host "  [go]   → Phase 3（Execute）に進む" -ForegroundColor Green
        Write-Host "  [edit] → Orchestrator に修正を依頼して再生成" -ForegroundColor Yellow
        Write-Host "  [stop] → パイプラインを中断" -ForegroundColor Red
        Write-Host ""

        $decision = Read-Host "判断"
        switch ($decision.Trim().ToLower()) {
            "go" {
                $approved = $true
                Write-Host "[Phase 2] 承認されました。Phase 3 に進みます。" -ForegroundColor Green
            }
            "edit" {
                $editRequest = Read-Host "修正内容を入力してください"
                $editPrompt = "以下の修正を行い、roadmap.md を再生成してください:`n$editRequest`n`n現在の roadmap.md: $RoadmapPath"
                Invoke-AI -AIName $Orchestrator -Prompt $editPrompt `
                    -SessionIdRef ([ref]$OrchestratorSessionId) -SessionFile $OrchestratorSessionFile `
                    -IsFirst $false
            }
            "stop" {
                Write-Host "パイプラインを中断しました。" -ForegroundColor Red
                exit 0
            }
            default {
                Write-Host "無効な入力です。'go', 'edit', 'stop' のいずれかを入力してください。" -ForegroundColor Yellow
            }
        }
    }
}

# ──────────────────────────────────────────
# Phase 3: Execute（airdp_research_loop.ps1 に委譲）
# Ctrl+C をトラップして緊急停止プロトコルを実行
# ──────────────────────────────────────────
Write-Host "`n━━━ Phase 3: Execute（Researcher: $Researcher / Reviewer: $Reviewer）━━━" -ForegroundColor Yellow
Write-Host "[Phase 3] airdp_research_loop.ps1 を起動します..." -ForegroundColor Green
Write-Host "  Ctrl+C で緊急停止できます（emergency_stop.md を記録して Phase 4 へ進みます）" -ForegroundColor DarkYellow

$EmergencyStopPath = Join-Path $ProjectDir "audit\emergency_stops" "emergency_stop_cycle${CycleId}.md"
$phase3Aborted = $false

try {
    $loopScript = Join-Path $ScriptDir "airdp_research_loop.ps1"
    & $loopScript `
        -RoadmapPath $RoadmapPath `
        -WorkDir $CycleDir `
        -Researcher $Researcher `
        -Reviewer $Reviewer `
        -MaxIterations $MaxIterations `
        -PromptsDir $PromptsDir
} catch {
    if ($_.Exception -is [System.Management.Automation.PipelineStoppedException]) {
        # Ctrl+C による緊急停止
        $phase3Aborted = $true
        $stopReason = Read-Host "`n[緊急停止] 停止理由を入力してください"
        $emergencyContent = @"
# Emergency Stop — Cycle $CycleId

**停止日時:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**停止理由:** $stopReason

## 対応
現在のイテレーションを中断し、Phase 4 (Judge) に直接移行します。
"@
        $emergencyContent | Out-File -FilePath $EmergencyStopPath -Encoding utf8
        Write-Host "  emergency_stop.md を記録しました: $EmergencyStopPath" -ForegroundColor Yellow
    } else {
        throw
    }
}

Write-Host "[Phase 3] 完了$(if ($phase3Aborted) { '（緊急停止）' })。" -ForegroundColor Green

# ──────────────────────────────────────────
# Phase 4: Judge → verdict.md 生成
# ──────────────────────────────────────────
Write-Host "`n━━━ Phase 4: Judge（$Judge）━━━" -ForegroundColor Yellow

$phase4Vars = @{
    ITERATIONS_DIR   = Join-Path $CycleDir "iterations"
    ROADMAP_PATH     = $RoadmapPath
    NEG_RESULTS_PATH = $NegResultsPath
    VERDICT_PATH     = $VerdictPath
}
$promptPhase4 = Expand-PromptTemplate (Join-Path $PromptsDir "judge_phase4.md") $phase4Vars

Write-Host "[Phase 4] Judge が verdict.md を生成中..." -ForegroundColor Blue
$isFirstJudge = ($null -eq (Read-SessionId $JudgeSessionFile)) -or ($Judge -in @("gemini","codex"))
Invoke-AI -AIName $Judge -Prompt $promptPhase4 `
    -SessionIdRef ([ref]$JudgeSessionId) -SessionFile $JudgeSessionFile `
    -IsFirst $isFirstJudge -GeminiMdSrc "GEMINI-judge.md"

if (-not (Test-Path $VerdictPath)) {
    Write-Host "[WARNING] Judge が verdict.md を生成しませんでした。Phase 5 を継続しますが、内容が不完全な可能性があります。" -ForegroundColor DarkYellow
} else {
    Write-Host "[Phase 4] verdict.md が生成されました: $VerdictPath" -ForegroundColor Green

    # REJECT 判定があれば NEGATIVE_RESULTS_INDEX.md に追記
    $verdictContent = Get-Content $VerdictPath -Raw -Encoding utf8
    if ($verdictContent -match "REJECT") {
        Write-Host "  REJECT 判定が含まれています。NEGATIVE_RESULTS_INDEX.md に記録してください。" -ForegroundColor Yellow
        Write-Host "  詳細は $VerdictPath の「NEGATIVE_RESULTS_INDEX への記載案」セクションを参照。" -ForegroundColor Gray
    }
}

# ──────────────────────────────────────────
# Phase 5: Orchestrator → cycle_report.md 生成
# ──────────────────────────────────────────
Write-Host "`n━━━ Phase 5: Report（Orchestrator: $Orchestrator）━━━" -ForegroundColor Yellow

$phase5Vars = @{
    VERDICT_PATH     = $VerdictPath
    NEG_RESULTS_PATH = $NegResultsPath
    SSOT_CHANGELOG   = $SsotChangelog
    IDEA_QUEUE_PATH  = $IdeaQueuePath
    CYCLE_REPORT_PATH = $CycleReportPath
}
$promptPhase5 = Expand-PromptTemplate (Join-Path $PromptsDir "orchestrator_phase5.md") $phase5Vars

Write-Host "[Phase 5] Orchestrator が cycle_report.md を生成中..." -ForegroundColor Yellow
Invoke-AI -AIName $Orchestrator -Prompt $promptPhase5 `
    -SessionIdRef ([ref]$OrchestratorSessionId) -SessionFile $OrchestratorSessionFile `
    -IsFirst $false

# ──────────────────────────────────────────
# 完了
# ──────────────────────────────────────────
Write-Host "`n══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  AIRDP Pipeline 完了 — Cycle $CycleId" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "  サイクルレポート  : $CycleReportPath"  -ForegroundColor White
Write-Host "  Judge 判定        : $VerdictPath"       -ForegroundColor White
Write-Host "  否定的結果        : $NegResultsPath"    -ForegroundColor White
Write-Host "  アイデアキュー    : $IdeaQueuePath"     -ForegroundColor White
if ($phase3Aborted) {
    Write-Host "  緊急停止ログ      : $EmergencyStopPath"  -ForegroundColor Yellow
}
Write-Host ""
Write-Host "次のサイクルを開始するには:" -ForegroundColor Gray
Write-Host "  .\airdp_orchestrator.ps1 -ProjectDir `"$ProjectDir`" -SeedPath `"[新しいseed.md]`"" -ForegroundColor DarkGray
