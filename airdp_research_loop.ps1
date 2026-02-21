# AIRDP Research Loop Script — Phase 3: 自動イテレーション
# AIRDPフレームワーク (AIRDP_Framework_Design.md) の Researcher ↔ Reviewer ループ実装
#
# Usage:
#   .\airdp_research_loop.ps1 -RoadmapPath "cycles\cycle_01\roadmap.md" -WorkDir "cycles\cycle_01"
#   .\airdp_research_loop.ps1 -RoadmapPath "cycles\cycle_01\roadmap.md" -WorkDir "cycles\cycle_01" -Researcher codex  -Reviewer claude
#   .\airdp_research_loop.ps1 -RoadmapPath "cycles\cycle_01\roadmap.md" -WorkDir "cycles\cycle_01" -Researcher claude -Reviewer copilot
#
# 対応 AI（Researcher / Reviewer 両方で全4種から選択可能）:
#   gemini  : gemini CLI (-p / -r)
#   codex   : codex exec (--json / exec resume)
#   claude  : claude CLI (-p / --session-id / --resume)
#   copilot : copilot CLI (-p / --resume)
#
# プロンプトテンプレート: airdp_prompts/researcher.md / reviewer.md
# プレースホルダー {KEY} はスクリプト内で実パスに展開される
#
# セッション継続:
#   Gemini  : gemini -r <id>            (--list-sessions で最新 ID を取得)
#   Codex   : codex exec resume <id>    (--json の thread_id で ID を取得)
#   Claude  : claude --session-id <uuid> / --resume <uuid>
#   Copilot : copilot --resume <uuid>   (同じ UUID を使い続ける)

param (
    [Parameter(Mandatory=$false)]
    [string]$RoadmapPath = "cycles\cycle_01\roadmap.md",

    [Parameter(Mandatory=$false)]
    [string]$WorkDir = "cycles\cycle_01",

    [Parameter(Mandatory=$false)]
    [ValidateSet("gemini","codex","claude","copilot")]
    [string]$Researcher = "gemini",

    [Parameter(Mandatory=$false)]
    [ValidateSet("gemini","codex","claude","copilot")]
    [string]$Reviewer = "claude",

    [Parameter(Mandatory=$false)]
    [int]$MaxIterations = 10,

    # プロンプトテンプレートのディレクトリ（デフォルトはスクリプトと同じ場所の airdp_prompts/）
    [Parameter(Mandatory=$false)]
    [string]$PromptsDir = ""
)

$ErrorActionPreference = "Stop"

# ──────────────────────────────────────────
# プロンプトディレクトリの解決
# ──────────────────────────────────────────
if ($PromptsDir -eq "") {
    $PromptsDir = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "airdp_prompts"
}
if (-not (Test-Path $PromptsDir)) {
    throw "Prompts directory not found: $PromptsDir`nRun from the directory containing airdp_prompts/"
}

# ──────────────────────────────────────────
# 前提チェック
# ──────────────────────────────────────────
if (-not (Test-Path $RoadmapPath)) { throw "Roadmap not found: $RoadmapPath" }
if (-not (Test-Path $WorkDir))     { throw "WorkDir not found: $WorkDir" }

# ──────────────────────────────────────────
# ファイルパス定義
# ──────────────────────────────────────────
$LogPath      = Join-Path $WorkDir "output_log.md"
$GoPath       = Join-Path $WorkDir "go.md"
$NgPath       = Join-Path $WorkDir "ng.md"
$IterationsDir = Join-Path $WorkDir "iterations"
$null = New-Item -ItemType Directory -Force -Path $IterationsDir

# セッション ID を永続化するディレクトリ
$SessionDir            = Join-Path $WorkDir ".airdp_sessions"
$null = New-Item -ItemType Directory -Force -Path $SessionDir
$ResearcherSessionFile = Join-Path $SessionDir "researcher_session_id.txt"
$ReviewerSessionFile   = Join-Path $SessionDir "reviewer_session_id.txt"

# SSoTディレクトリ（WorkDir の親を探す）
$SsotDir = Join-Path (Split-Path -Parent $WorkDir) "ssot"
if (-not (Test-Path $SsotDir)) { $SsotDir = Join-Path $WorkDir "ssot" }

Write-Host "AIRDP Phase 3: 自動イテレーション起動" -ForegroundColor Cyan
Write-Host "  Roadmap   : $RoadmapPath" -ForegroundColor Gray
Write-Host "  WorkDir   : $WorkDir"     -ForegroundColor Gray
Write-Host "  Researcher: $Researcher"  -ForegroundColor Green
Write-Host "  Reviewer  : $Reviewer"    -ForegroundColor Magenta
Write-Host "  PromptsDir: $PromptsDir"  -ForegroundColor Gray

# ──────────────────────────────────────────
# ユーティリティ
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

# プロンプトテンプレートを読み込み、プレースホルダーを展開する
function Expand-PromptTemplate([string]$TemplatePath, [hashtable]$Vars) {
    if (-not (Test-Path $TemplatePath)) {
        throw "Prompt template not found: $TemplatePath"
    }
    $text = Get-Content $TemplatePath -Raw -Encoding utf8
    foreach ($key in $Vars.Keys) {
        $text = $text -replace [regex]::Escape("{$key}"), $Vars[$key]
    }
    return $text
}

# ──────────────────────────────────────────
# AI 呼び出し関数：Gemini
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

# ──────────────────────────────────────────
# AI 呼び出し関数：Codex
# ──────────────────────────────────────────
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

# ──────────────────────────────────────────
# AI 呼び出し関数：Claude
# --session-id で初回 UUID を固定、--resume で継続。
# CLAUDECODE 環境変数を一時クリアしてネストを回避。
# ──────────────────────────────────────────
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

# ──────────────────────────────────────────
# AI 呼び出し関数：Copilot
# --resume <uuid> で UUID を固定。初回でも既存 UUID を渡せば新規セッションとして開始。
# ──────────────────────────────────────────
function Invoke-Copilot([string]$Prompt, [ref]$SessionIdRef) {
    Write-Host "  Copilot session: $($SessionIdRef.Value)" -ForegroundColor DarkGray
    copilot --resume $SessionIdRef.Value -p $Prompt --yolo
}

# ──────────────────────────────────────────
# 汎用 AI 呼び出しラッパー
# ──────────────────────────────────────────
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
# セッション ID の初期化
# ──────────────────────────────────────────
$ResearcherSessionId = Read-SessionId $ResearcherSessionFile
$ReviewerSessionId   = Read-SessionId $ReviewerSessionFile

# Claude / Copilot は UUID を起動時に生成・固定
if ($Researcher -in @("claude","copilot") -and $null -eq $ResearcherSessionId) {
    $ResearcherSessionId = [System.Guid]::NewGuid().ToString()
    Save-SessionId $ResearcherSessionFile $ResearcherSessionId
}
if ($Reviewer -in @("claude","copilot") -and $null -eq $ReviewerSessionId) {
    $ReviewerSessionId = [System.Guid]::NewGuid().ToString()
    Save-SessionId $ReviewerSessionFile $ReviewerSessionId
}

# ──────────────────────────────────────────
# メインループ
# ──────────────────────────────────────────
$finished  = $false
$iteration = 1
$isFirstResearcher = ($null -eq (Read-SessionId $ResearcherSessionFile)) -or ($Researcher -in @("gemini","codex"))
$isFirstReviewer   = $true

while (-not $finished) {
    Write-Host "`n━━━ Iteration $iteration ━━━" -ForegroundColor Yellow

    # イテレーションディレクトリを作成
    $iterDir = Join-Path $IterationsDir ("iter_{0:D2}" -f $iteration)
    $null = New-Item -ItemType Directory -Force -Path (Join-Path $iterDir "code")

    # ── 1. Researcher Phase ──────────────────
    Write-Host "[Researcher: $Researcher] 作業中..." -ForegroundColor Green

    $researcherVars = @{
        ROADMAP_PATH = $RoadmapPath
        NG_PATH      = $NgPath
        GO_PATH      = $GoPath
        WORK_DIR     = $WorkDir
        LOG_PATH     = $LogPath
        ITER_DIR     = $iterDir
    }
    $promptResearcher = Expand-PromptTemplate (Join-Path $PromptsDir "researcher.md") $researcherVars

    Invoke-AI -AIName $Researcher -Prompt $promptResearcher `
        -SessionIdRef ([ref]$ResearcherSessionId) -SessionFile $ResearcherSessionFile `
        -IsFirst $isFirstResearcher -GeminiMdSrc "GEMINI-writer.md"
    $isFirstResearcher = $false

    # go.md / ng.md をクリア（次の査読前に）
    if (Test-Path $GoPath) { Remove-Item $GoPath }
    if (Test-Path $NgPath) { Remove-Item $NgPath }

    # output_log.md が生成されているか確認
    if (-not (Test-Path $LogPath)) {
        Write-Host "[ERROR] Researcher が $LogPath を生成しませんでした。イテレーションをスキップ。" -ForegroundColor Red
        $iteration++
        if ($iteration -gt $MaxIterations) { $finished = $true }
        continue
    }

    # ── 2. Reviewer Phase ───────────────────
    Write-Host "`n[Reviewer: $Reviewer] 査読中..." -ForegroundColor Magenta

    $reviewerVars = @{
        LOG_PATH     = $LogPath
        NG_PATH      = $NgPath
        GO_PATH      = $GoPath
        ROADMAP_PATH = $RoadmapPath
        ITER_DIR     = $iterDir
        SSOT_DIR     = $SsotDir
    }
    $promptReviewer = Expand-PromptTemplate (Join-Path $PromptsDir "reviewer.md") $reviewerVars

    Invoke-AI -AIName $Reviewer -Prompt $promptReviewer `
        -SessionIdRef ([ref]$ReviewerSessionId) -SessionFile $ReviewerSessionFile `
        -IsFirst $isFirstReviewer -GeminiMdSrc "GEMINI-reviewer.md"
    $isFirstReviewer = $false

    # ── 3. Decision ─────────────────────────
    if (Test-Path $GoPath) {
        Write-Host "`n[APPROVED] ロードマップ更新済み。$GoPath を確認してください。" -ForegroundColor Green
        $finished = $true
        if (Test-Path $LogPath) { Remove-Item $LogPath }
    } elseif (Test-Path $NgPath) {
        Write-Host "`n[REJECTED] $NgPath が生成されました。次のイテレーションで対応します。" -ForegroundColor Red
        $iteration++
    } else {
        Write-Host "`n[ERROR] go.md も ng.md も生成されませんでした。Reviewer が判定できませんでした。" -ForegroundColor DarkYellow
        $finished = $true
    }

    if ($iteration -gt $MaxIterations) {
        Write-Host "`n[LIMIT] 最大イテレーション数 ($MaxIterations) に到達。ループを終了します。" -ForegroundColor DarkYellow
        $finished = $true
    }
}

Write-Host "`nAIRDP Phase 3 ループ終了。" -ForegroundColor Cyan
