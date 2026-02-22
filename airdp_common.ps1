# airdp_common.ps1 — AIRDP 共通ユーティリティ
# 各フェーズスクリプトから . .\airdp_common.ps1 でドットソースして使用する
#
# 提供する関数:
#   Resolve-AirdpPaths   : ProjectDir / CycleId からパス群を返す
#   Read-SessionId       : セッションIDファイルの読み込み
#   Save-SessionId       : セッションIDファイルへの書き込み
#   Expand-PromptTemplate: プロンプトテンプレートのプレースホルダー展開
#   Invoke-AI            : AI バックエンド共通呼び出しラッパー

# ──────────────────────────────────────────
# パス解決
# ──────────────────────────────────────────
function Resolve-AirdpPaths {
    param(
        [string]$ProjectDir,
        [string]$CycleId
    )
    $ProjectDir  = (Resolve-Path $ProjectDir).Path
    $CyclesDir   = Join-Path $ProjectDir "cycles"
    $CycleDir    = Join-Path $CyclesDir  "cycle_$CycleId"
    $SsotDir     = Join-Path $ProjectDir "ssot"

    return @{
        ProjectDir       = $ProjectDir
        CyclesDir        = $CyclesDir
        CycleDir         = $CycleDir
        SsotDir          = $SsotDir
        IterationsDir    = Join-Path $CycleDir "iterations"
        SessionDir       = Join-Path $CycleDir ".airdp_sessions"
        RoadmapPath      = Join-Path $CycleDir "roadmap.md"
        VerdictPath      = Join-Path $CycleDir "verdict.md"
        CycleReportPath  = Join-Path $CycleDir "cycle_report.md"
        LogPath          = Join-Path $CycleDir "output_log.md"
        GoPath           = Join-Path $CycleDir "go.md"
        NgPath           = Join-Path $CycleDir "ng.md"
        ConstantsPath    = Join-Path $SsotDir  "constants.json"
        SsotChangelog    = Join-Path $SsotDir  "changelog.json"
        NegResultsPath   = Join-Path $ProjectDir "NEGATIVE_RESULTS_INDEX.md"
        IdeaQueuePath    = Join-Path $ProjectDir "idea_queue.md"
    }
}

# ──────────────────────────────────────────
# セッション ID 管理
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

# セッションIDを取得し、IsFirst フラグも返す
# 戻り値: @{ Id = <string or null>; IsFirst = <bool> }
function Get-OrCreateSessionId {
    param(
        [string]$AIName,
        [string]$SessionFile
    )
    $existing = Read-SessionId $SessionFile
    # Gemini/Codex は毎回新規セッション（セッション管理が異なるため）
    if ($AIName -in @("gemini", "codex")) {
        return @{ Id = $existing; IsFirst = $true }
    }
    # Claude/Copilot: ファイルがあれば resume、なければ新規UUID を生成して保存
    if ($null -ne $existing) {
        return @{ Id = $existing; IsFirst = $false }
    } else {
        $newId = [System.Guid]::NewGuid().ToString()
        Save-SessionId $SessionFile $newId
        return @{ Id = $newId; IsFirst = $true }
    }
}

# ──────────────────────────────────────────
# プロンプトテンプレート展開
# ──────────────────────────────────────────
function Expand-PromptTemplate([string]$TemplatePath, [hashtable]$Vars) {
    if (-not (Test-Path $TemplatePath)) { throw "Template not found: $TemplatePath" }
    $text = Get-Content $TemplatePath -Raw -Encoding utf8
    foreach ($key in $Vars.Keys) {
        $text = $text -replace [regex]::Escape("{$key}"), $Vars[$key]
    }
    return $text
}

# ──────────────────────────────────────────
# AI 呼び出し: Gemini
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
# AI 呼び出し: Codex
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
# AI 呼び出し: Claude
# ──────────────────────────────────────────
function Invoke-Claude([string]$Prompt, [ref]$SessionIdRef, [string]$SessionFile, [bool]$IsFirst) {
    # ネスト検出を防ぐため Claude 関連環境変数を完全に削除する
    $backupVars = @{}
    foreach ($key in @("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_VERSION")) {
        if (Test-Path "Env:$key") {
            $backupVars[$key] = (Get-Item "Env:$key").Value
            Remove-Item "Env:$key" -ErrorAction SilentlyContinue
        }
    }
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
        foreach ($key in $backupVars.Keys) {
            Set-Item "Env:$key" $backupVars[$key]
        }
    }
}

# ──────────────────────────────────────────
# AI 呼び出し: Copilot
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
        default   { throw "Unknown AI backend: $AIName" }
    }
}
