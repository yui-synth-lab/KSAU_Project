# airdp_paper.ps1 — AIRDP 論文執筆パイプライン（Writer ↔ Reviewer ループ）
#
# Usage:
#   .\airdp_paper.ps1 -PaperDir papers\paper_01 -Title "KSAU Framework: Topological Mass Prediction"
#   .\airdp_paper.ps1 -PaperDir papers\paper_01 -Writer gemini -Reviewer claude -MaxRevisions 5
#
# ディレクトリ構造（自動生成）:
#   {PaperDir}/
#     brief.md          ← 人間が事前に作成する執筆依頼書（必須）
#     draft_v01.md      ← Writer が生成する論文 draft
#     draft_v02.md      ← 改訂版（revisions が進むごとに連番）
#     review_v01.md     ← Reviewer の査読コメント
#     review_v02.md
#     paper_final.md    ← 人間が最終承認後にリネーム（スクリプトは生成しない）
#     .sessions/
#       writer_session_id.txt
#       reviewer_session_id.txt

param (
    [Parameter(Mandatory=$true)]  [string]$PaperDir,
    [Parameter(Mandatory=$false)] [string]$ProjectDir  = ".",
    [Parameter(Mandatory=$false)]
    [ValidateSet("gemini","codex","claude","copilot")]
    [string]$Writer      = "gemini",
    [Parameter(Mandatory=$false)]
    [ValidateSet("gemini","codex","claude","copilot")]
    [string]$Reviewer    = "claude",
    [Parameter(Mandatory=$false)] [int]$MaxRevisions   = 5,
    [Parameter(Mandatory=$false)] [string]$PromptsDir  = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptDir "airdp_common.ps1")

if ($PromptsDir -eq "") { $PromptsDir = Join-Path $ScriptDir "airdp_prompts" }
if (-not (Test-Path $PromptsDir)) { throw "Prompts directory not found: $PromptsDir" }

$ProjectDir = (Resolve-Path $ProjectDir).Path
$PaperDir   = Join-Path $ProjectDir $PaperDir
$SessionDir = Join-Path $PaperDir ".sessions"
$BriefPath  = Join-Path $PaperDir "brief.md"
$SsotDir    = Join-Path $ProjectDir "ssot"
$NegPath    = Join-Path $ProjectDir "NEGATIVE_RESULTS_INDEX.md"

# ── 事前チェック ──────────────────────────────────────
if (-not (Test-Path $BriefPath)) {
    throw "brief.md が見つかりません: $BriefPath`n執筆依頼書を先に作成してください。"
}

$null = New-Item -ItemType Directory -Force -Path $PaperDir
$null = New-Item -ItemType Directory -Force -Path $SessionDir

# ── セッション ID ──────────────────────────────────────
$WriterSessionFile   = Join-Path $SessionDir "writer_session_id.txt"
$ReviewerSessionFile = Join-Path $SessionDir "reviewer_session_id.txt"

$writerSession   = Get-OrCreateSessionId -AIName $Writer   -SessionFile $WriterSessionFile
$reviewerSession = Get-OrCreateSessionId -AIName $Reviewer -SessionFile $ReviewerSessionFile
$WriterSessionId   = $writerSession.Id
$ReviewerSessionId = $reviewerSession.Id
$isFirstWriter     = $writerSession.IsFirst
$isFirstReviewer   = $reviewerSession.IsFirst

Write-Host "`n━━━ AIRDP Paper Pipeline（Writer: $Writer / Reviewer: $Reviewer）━━━" -ForegroundColor Yellow
Write-Host "  PaperDir : $PaperDir"  -ForegroundColor Gray
Write-Host "  Brief    : $BriefPath" -ForegroundColor Gray

$revision  = 1
$finished  = $false

while (-not $finished) {
    $draftPath  = Join-Path $PaperDir ("draft_v{0:D2}.md"  -f $revision)
    $reviewPath = Join-Path $PaperDir ("review_v{0:D2}.md" -f $revision)
    $prevDraft  = if ($revision -gt 1) { Join-Path $PaperDir ("draft_v{0:D2}.md" -f ($revision - 1)) } else { "" }
    $prevReview = if ($revision -gt 1) { Join-Path $PaperDir ("review_v{0:D2}.md" -f ($revision - 1)) } else { "" }

    Write-Host "`n━━━ Revision $revision ━━━" -ForegroundColor Yellow

    # ── 1. Writer ─────────────────────────────────────
    Write-Host "[Writer: $Writer] 執筆中..." -ForegroundColor Green

    $figuresDir = Join-Path $PaperDir "figures"
    $null = New-Item -ItemType Directory -Force -Path $figuresDir
    $writerVars = @{
        BRIEF_PATH    = $BriefPath
        DRAFT_PATH    = $draftPath
        PREV_DRAFT    = $prevDraft
        PREV_REVIEW   = $prevReview
        SSOT_DIR      = $SsotDir
        NEG_PATH      = $NegPath
        REVISION      = "$revision"
        PAPER_DIR     = $PaperDir
        FIGURES_DIR   = $figuresDir
    }
    $promptWriter = Expand-PromptTemplate (Join-Path $PromptsDir "paper_writer.md") $writerVars

    Invoke-AI -AIName $Writer -Prompt $promptWriter `
        -SessionIdRef ([ref]$WriterSessionId) -SessionFile $WriterSessionFile `
        -IsFirst $isFirstWriter
    $isFirstWriter = $false

    if (-not (Test-Path $draftPath)) {
        Write-Host "[ERROR] Writer が $draftPath を生成しませんでした。中断。" -ForegroundColor Red
        $finished = $true
        continue
    }

    # ── 2. Reviewer ───────────────────────────────────
    Write-Host "`n[Reviewer: $Reviewer] 査読中..." -ForegroundColor Magenta

    $reviewerVars = @{
        BRIEF_PATH    = $BriefPath
        DRAFT_PATH    = $draftPath
        REVIEW_PATH   = $reviewPath
        SSOT_DIR      = $SsotDir
        NEG_PATH      = $NegPath
        REVISION      = "$revision"
    }
    $promptReviewer = Expand-PromptTemplate (Join-Path $PromptsDir "paper_reviewer.md") $reviewerVars

    Invoke-AI -AIName $Reviewer -Prompt $promptReviewer `
        -SessionIdRef ([ref]$ReviewerSessionId) -SessionFile $ReviewerSessionFile `
        -IsFirst $isFirstReviewer
    $isFirstReviewer = $false

    if (-not (Test-Path $reviewPath)) {
        Write-Host "[ERROR] Reviewer が $reviewPath を生成しませんでした。中断。" -ForegroundColor Red
        $finished = $true
        continue
    }

    # ── 3. 判定（review.md の VERDICT を読む）────────
    $reviewContent = Get-Content $reviewPath -Raw -Encoding utf8
    # VERDICT 行は "VERDICT: ACCEPT" または "**VERDICT:** ACCEPT" 等の形式を許容する
    if ($reviewContent -match "VERDICT\W+ACCEPT") {
        Write-Host "`n[ACCEPTED] Revision $revision が承認されました。" -ForegroundColor Cyan
        Write-Host "  最終 draft: $draftPath" -ForegroundColor White
        Write-Host "  確認後、paper_final.md にリネームしてください。" -ForegroundColor DarkYellow
        $finished = $true
    } elseif ($reviewContent -match "VERDICT\W+REVISE") {
        Write-Host "`n[REVISE] 修正要求。Revision $($revision + 1) に進みます。" -ForegroundColor Yellow
        $revision++
    } else {
        Write-Host "`n[ERROR] review.md に VERDICT フィールドが見つかりません。" -ForegroundColor Red
        Write-Host "  検索パターン: 'VERDICT\W+ACCEPT' または 'VERDICT\W+REVISE'" -ForegroundColor DarkGray
        Write-Host "  review.md の先頭5行:" -ForegroundColor DarkGray
        Get-Content $reviewPath -TotalCount 5 -Encoding utf8 | ForEach-Object { Write-Host "    $_" -ForegroundColor DarkGray }
        $finished = $true
    }

    if ($revision -gt $MaxRevisions) {
        Write-Host "`n[LIMIT] 最大改訂数 ($MaxRevisions) に到達。人間による判断が必要です。" -ForegroundColor DarkYellow
        $finished = $true
    }
}

Write-Host "`n══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  論文パイプライン完了" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  PaperDir   : $PaperDir"  -ForegroundColor White
Write-Host "  最終Revision: $revision" -ForegroundColor White
