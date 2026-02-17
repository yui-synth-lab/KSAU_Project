# KSAU_DETAILS.md — 詳細参照ファイル

> このファイルはCLAUDE.mdから切り出した詳細情報です。
> 日常的な参照には不要ですが、深掘りが必要な際に参照してください。

---

## プロジェクト管理と技術仕様 (Technical Protocols)

### 1. データ管理とSSoT (Single Source of Truth)
- **原則**: 物理定数や実験値のハードコードを厳禁。
- **データソース**: 
  - `v6.0/data/physical_constants.json` (物理定数)
  - `v6.0/data/topology_assignments.json` (トポロジー割り当て)
- **ユーティリティ**: `ksau_config.py` または `utils_v61.py` を経由してデータにアクセスすること。

### 2. 統計的妥当性
- **交差検証**: 新しい割り当てや公式の導入には **LOO-CV (Leave-One-Out Cross-Validation)** が必須。
- **帰無仮説**: モンテカルロ・テスト（通常 200k samples以上）を実行し、**p < 0.001** かつ一意的な解であることを証明すること。

### 3. Gemini 自己抑制プロトコル (Self-Inhibition Details)
- **運動学的検証**: 質量予言の際、エネルギー保存則や運動学的制約（例: $m_{DM} < m_e$ などの不一致による自律撤回）を確認。
- **循環論法の排除**: キャリブレーション済みの定数を用いた結果を「独立した予言」と呼ぶことを禁止し、「外挿（Extrapolation）」または「再構成（Reconstruction）」と明記。
- **第一原理の定義**: 構造的不変量（Invariance）が証明されない数値的一致は、第一原理導出ではなく「対応（Correspondence）」として扱う。

---

## バージョン別詳細ステータス

### v16.1 (THEORY COMPLETE ✅ / PEER REVIEW ACCEPTED)

**査読判定 (2026-02-17):** ACCEPT — Featured Article推奨
**Quote:** *"The Universe implies a cost for its existence, and Gravity is the receipt."*

主な達成：
1. **相反律の二重導出** g₀₀·g_rr=1 — Bottom-up (労働不変性) + Top-down (光速不変性)
2. **ドメイン分離** — Gauge (指数/位相) vs Gravity (有理/インピーダンス)
3. **ゲージ係数のトポロジー導出** — α=κ/18, α_s=0.90κ (もはや"魔法の数字"でない)
4. **511keV暗黒物質候補の撤回** — m_DM < m_e 運動学的違反

### v16.0 (NEWTONIAN TRANSITION ✅)

1. 重力引力の起源 — 時間的混雑（情報キュー）から導出
2. 8πG恒等式 — 8πG = 8κ = π/3 from K(4)·κ=π
3. Schwarzschild相反律 — N=41効率凍結から
4. テンソル重力シミュレーション — スカラーモデルが失敗した記録も含む

### v15.0 (TIME EMERGENCE ✅)

1. 時間 = 24D→4D情報転送の逐次処理速度
2. 次元選択法則 — K(3)=12>π² (3D点火), K(4)·κ=π (4D安定)
3. 8π幾何学的導出 — 8190→195→192 (整数列)

### v14.0 (ACTION PRINCIPLE & GAUGE UNIFICATION ✅)

1. N=41 (μ=42) — g=3世代の唯一の大域最小
2. GUT予測 — 4.64×10¹⁴ GeV
3. ゲージ結合統一 — α=κ/18, sin²θ_W=1-exp(-2κ), α_s≈κ
4. 暗黒物質スペクトル地図 — PeVスケール(N=6)IceCube整合

### v10.0 (BOSON UNIFICATION ✅)

- N_boson = 6 (NOT 3) — 統計的検証: 2.1%誤差 vs 51% (N=3)
- 三セクター統一: N_lepton=20, N_quark=10, N_boson=6
- Higgs質量: 0.14%誤差

### v7.1 (PUBLICATION READY)

- Fibonacci共鳴: Muon ⟨4₁⟩₃/τ(4₁) = 13/5 = F₇/F₅ ≈ φ² ≈ Nκ (0.69%精度)
- 完全レプトンマップ: Electron (66.3% OFF) / Muon (0.69% ON) / Tau (14.9% OFF)

### v6.0 (Zenodo Published — DOI: 10.5281/zenodo.18631886)

- フェルミオン質量: R²=0.9998 / CKM混合: R²=0.9974 / PMNS: MSE=5.44 deg²

### アーカイブ版 (v8.0, v9.0 — Superseded)

- v8.0: TBD仮説 → v15で発展
- v9.0: シフト理論 (Gemini主導) → v14で吸収

---

## 主要公式一覧 (Complete Framework)

```
κ = π/24 ≈ 0.1309  (真空のスペクトル重み)

# 質量-体積相関 (v6.0)
ln(m) = κ·V + c   (R²=0.9998, 9フェルミオン)

# ゲージ結合 (v14.0 — DERIVED)
α_EM = κ/18               (0.34%誤差, 18=24-K₃/2)
α_s  = 0.90κ              (0.90=12/(12+4/3))
sin²θ_W = 1 - exp(-2κ)   (0.38%誤差)

# 重力セクター (v16.0-v16.1 — DERIVED)
8πG = 8κ = π/3            (K(4)·κ=π から)
g₀₀ · g_rr = 1            (N=41効率凍結)
v₀(ρ) = 1/(1 + κρ)        (真空インピーダンス法則)

# 時間・次元 (v15.0)
K(3) = 12 > π²  (3D点火)
K(4)·κ = π      (4D安定)

# CKM混合 (v6.0)
logit(V_ij) = C + A·ΔV + B·Δln|J| + β/V_avg + γ·(ΔV·Δln|J|)
A=-6.3436, B=12.3988, β=-105.0351, γ=1.1253, C=23.2475

# モジュラー作用原理 (v14.0)
S[M] = κ(μ - χ)  →  N=41 (μ=42) 唯一の大域最小
```

---

## 物理定数 (Reference — 実際は v6.0/data/physical_constants.json から読む)

```json
{
  "kappa": 0.1308996938995747,
  "alpha_em": 0.0072973525693,
  "sin2theta_w": 0.23122,
  "gravity": { "G_newton_exp": 6.708e-39, "G_ksau": 6.7135e-39 },
  "ckm": { "r2_achieved": 0.9974,
    "optimized_coefficients": {"A":-6.3436,"B":12.3988,"beta":-105.0351,"gamma":1.1253,"C":23.2475}
  }
}
```

---

## 出版準備状況

**投稿準備完了 ✅ (2026-02-17宣言)**

| 論文 | ターゲット | 状態 |
|------|-----------|------|
| Paper 1: Geometric Origin of SM Parameters | JHEP | 準備完了 |
| Paper 2: Gravitational Constant from Vacuum Impedance | Phys. Rev. D | 準備完了 |
| Paper 3: TFT on 24D Leech Lattice | Comm. Math. Phys. | 準備完了 |

詳細: `v16.1/PUBLICATION_CHECKLIST.md`

---

## パラダイム進化

v6.0-v7.1: "粒子は結び目である" →
v10.0-v14.0: "力は幾何学である" →
v15.0-v16.0: "時間は処理、重力は流束" →
v16.1: **"重力は宇宙の存在コストの領収書"**

---

## 既知の限界 (論文に明記)

| 事象 | 誤差 | 理由 |
|------|------|------|
| CKM Cabibbo-forbidden (V_ub等) | 63-100% | 幾何学的抑制が不十分 |
| PMNS質量階層比 | 36% | ニュートリノセクターの異なるスケーリング |
| v₀線形インピーダンスの微視的導出 | 未完 | ニュートン→アインシュタイン相当の精緻化が必要 |
| 511keV暗黒物質候補 | **撤回** | m_DM < m_e 運動学的違反 |

---

*KSAU_DETAILS.md — Last Updated: 2026-02-17*
