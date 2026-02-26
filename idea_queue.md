# AIRDP Idea Queue — KSAU Project

Phase 3 実行中に思いついたアイデアをここに追記してください。
現在のサイクルには影響しません。次のサイクルの seed.md の候補になります。

---

## 優先度：高

### [COMPLETED in Cycle 17 (H43)] H24 再挑戦 — 崩壊幅 Γ とトポロジー不変量の相関
- **結果:** TSI の正則化により R²=0.7246 を達成し ACCEPT。SSoT に統合済み。

### H23 再設計 — ST 不変量による質量残差補正
- **アイデア:** Cycle_10 では「レプトン 3 点 × 3 パラメータ」で自由度ゼロの過学習に陥った。全フェルミオン 9 点の残差に対する**線形** ST 補正に限定することで自由度問題を回避する
- **根拠:** 線形モデルならパラメータ数 ≤ 2、df ≥ 7 が確保できる
- **設計上の注意:** 非線形モデルへの拡張は df ≥ 3 が担保される場合のみ許可すること。roadmap にその旨を明記すること
- **引き継ぎ元:** Cycle_10 H23 MODIFY（過学習棄却）
- **ステータス:** Cycle 18 Seed に採用済み。

---

## 優先度：中

### κ = π/24 の再検証 — 循環論法を排した設計
- **アイデア:** Cycle_10 で Judge が「SSoT の κ=π/24 を使って κ=π/24 を確認した」として循環論法を疑い棄却した。次回は SSoT の κ 値を入力に使わず、フェルミオン質量の生データのみから κ を回帰推定し、その結果を π/24 と比較する設計にする
- **根拠:** Cycle_08 H16（FPR=0.00078）で独立検証済みなので核心的成果は保護されているが、検証設計の改善として有意義
- **設計上の注意:** 「SSoT の κ を定数として読み込む」ことは禁止。回帰の入力は質量データのみとすること
- **引き継ぎ元:** Cycle_10 H22（Judge による循環論法疑惑）

### π/24 の「24」の理論的導出
- **アイデア:** なぜ 24 なのか。プランクスケールでの位相離散化、24 セル体（24-cell）の幾何学、Pachner move の共鳴条件から 24 が必然的に導出できるかを検証する
- **根拠:** 現状 κ=π/24 は数値フィット後に発見された値。理論的必然として導出できれば理論の強度が根本的に変わる
- **引き継ぎ元:** idea_queue.md 初期メモ「π/24 はなぜ 24 なのか」

### カラビ＝ヤウ多様体との接続
- **アイデア:** 重力補正項 k_c / δ の幾何学的根拠が確立された後の候補。10 次元バルクのコンパクト化と重力定数 G のさらなる精密化を検討する
- **引き継ぎ元:** idea_queue.md 初期メモ

---

## 優先度：低（理論探索）

### スピン・電荷のトポロジー対応
- **アイデア:** フェルミオン（スピン 1/2）とボソン（スピン 1）の違いを向きのある結び目と向きのない結び目の違いとして記述できるか。電荷との対応も探索する
- **引き継ぎ元:** idea_queue.md 初期メモ

### 時間の波モデル（理論的基盤）
- **アイデア:** 時間がプランクスケールで離散化された波であり、その位相のランダム性が量子揺らぎとして現れるという理論的枠組みを数式化する。質量＝空間の粘性への抵抗、という解釈を定量化できるか
- **引き継ぎ元:** idea_queue.md 初期メモ「時間の波、周波数はプランクスケールで固定、位相はランダム、世界は離散的」

---

## 凍結中（条件付き再開）

### CKM Cabibbo-forbidden 要素の改善
- **状態:** 57–97% の誤差が残存。高次不変量の導入を検討したが未着手
- **再開条件:** 基本フェルミオン MAE が 0.5% 未満で安定してから

### PMNS ニュートリノ混合の幾何学的導出
- **状態:** v7.0 スコープ外として保留
- **再開条件:** 混合角の導出精度向上のための理論的枠組みが整ってから


## Priority: Critical (Major Revision対応必須)
### H44: Novel Quantitative Predictions from KSAU
**Description:**  
現在は既知データへの後ろ向きフィットのみ。  
κ = π/24 + V_effモデルから、**実験未確認の新規予測**を最低2個導出する。  
候補:
- アクシオン質量精密予測 (m_a = 12.4 ± 0.3 μeV など、実験検出可能レンジ)
- Newton定数Gの理論偏差予測 (ΔG/G ≈ 10^{-5} レベル、MICROSCOPEやSTEP実験で検証可能)
- トップクォーク崩壊幅の微小異常予測 (Γ_t の 0.1% レベル修正)
**Success Criteria:** R² > 0.99 + FPR < 0.01 + 実験提案付き  
**Test Method:** Monte Carlo + 既存実験誤差との比較  
**Priority:** Critical / Suggested Cycle: 18 (Seed直後)

### H45: First-Principles Topology Assignment Rule
**Description:**  
現行の粒子↔結び目割り当てがpost-hocに見える問題を解消。  
24-cell対称性・Pachner Move安定性・署名/行列式の表現論から**事前ルール**を定義し、  
全12粒子のトポロジーを**予測として固定**する。  
例: 「安定粒子はDet ≡ 0 mod 24」「レプトンは3成分リンク必須」など。  
**Success Criteria:** 割り当て成功率100% + 恣意性ゼロ証明  
**Priority:** Critical / Suggested Cycle: 18

### H46: TQFT Embedding into SM Gauge Group
**Description:**  
KSAU TQFT (24-cell + Pachner) が **SU(3)×SU(2)×U(1)** を自然に導出する埋め込みスキームを構築。  
候補: 24-cellの対称群 → SU(2)_L × U(1)_Y の表現分解、またはBorromean ringsをカラー荷電として扱う。  
**Success Criteria:** ゲージ群の次元・破れパターンがSMと一致 + Witten条件拡張  
**Priority:** High / Suggested Cycle: 18-19

### H47: Compactification Scheme via 24-cell
**Description:**  
24-cellを**コンパクト化多様体**として扱い、  
余剰次元を7次元コンパクト (D_compact=7) と整合させる弦/M理論的埋め込み。  
V_effモデルと弦理論の体積モジュライを接続。  
**Success Criteria:** Gの導出と矛盾なし + Planckスケール再現  
**Priority:** High / Suggested Cycle: 19

## Priority: Medium (将来拡張)
（必要に応じて後で追加）

**Next Action Recommendation:**  
Cycle 18 Seedでは **H44 + H45** を最優先で回す。  
これで「Major Revision → Minor Revision → Accept」への道が開ける。

---
**Note for Orchestrator:**  
このidea_queueは査読者レビュー（2026-02-26）の**直接対応版**です。  
全仮説はSSoT/constants.json の新セクション "prediction_targets" と "assignment_rules" を参照必須。