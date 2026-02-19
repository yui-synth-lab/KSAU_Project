# γ 閾値 0.70 の物理的再評価と幾何学的統一

**Date:** 2026-02-18
**Project:** KSAU v22.0
**Status:** VALIDATED (Revision 1)

## 1. 閾値 0.70 の設定根拠（過去の経緯）

v17.0 以前において採用されていた成長指数 $\gamma$ の棄却閾値 0.70 は、以下の 2 点に基づく暫定的な基準であった：
1. $\Lambda$CDM の予測値（$\gamma \approx 0.55$）と、観測データ（$\gamma_{\text{obs}} \approx 0.65-0.75$）の中間点付近を設定。
2. $\sigma_8$ テンションが「有意に緩和された」とみなせる境界線としてのヒューリスティックな採用。

しかし、これは KSAU の幾何学から導出されたものではなく、物理的な必然性に欠けていた。

## 2. 幾何学的再解釈：スケール依存型 $\gamma_{\text{app}}$

v22.0 における革新は、$\gamma$ を定数ではなく、有効物質密度 $\Omega_{\text{eff}}(k)$ に由来するスケール依存的な観測量として定式化したことにある。

$$ \gamma_{\text{app}}(k) = 0.55 \frac{\ln \Omega_{\text{eff}}(k)}{\ln \Omega_{m,0}} $$

ここで、$\Omega_{\text{eff}}(k) = (\Omega_{m,0} - \Omega_{\text{tens}}) + \xi(k) \Omega_{\text{tens}}$ である。

### 特徴：
- **大スケール ($\xi \to 0.5$):** $\gamma_{\text{app}} \approx 0.623$。これは $\Omega_{\text{tens}}$（背景位相張力）による成長抑制を、標準的な成長指数で表現した場合の「見かけの $\gamma$」に相当する。
- **小スケール ($\xi \to 1$):** $\gamma_{\text{app}} \approx 0.55$。小スケールではコヒーレンス長 $R_{\text{cell}}$ の内部において $\xi \approx 1$ となり、標準的な $\Lambda$CDM 的成長が回復される。

## 3. 実装上のバグ修正と統一

前回の監査（`ng.md`）で指摘された $\gamma_{\text{impl}} \approx 1.25$ と $\gamma_{\text{app}} \approx 0.623$ の乖離は、以下の 2 点により解消された：
1. **バグ修正:** $\gamma_{\text{impl}}$ 計算において strand 分割数 $B_{\text{eff}}=4$ ではなく全次数 $B_{\text{cell}}=8$ を誤用していた。
2. **公式の統一:** $\gamma_{\text{impl}}$ にも上記の対数公式を適用することで、線形近似を廃し、幾何学的整合性を確保。

## 4. 結論

$\gamma < 0.70$ という一律の閾値は廃止され、今後は **「各スケール $k$ における観測値 $\gamma_{\text{obs}}$ が幾何学的予測 $\gamma_{\text{app}}(k)$ と一致するか」** が KSAU の正当性評価基準となる。

最新の検証結果では、全サーベイの平均で $\gamma_{\text{impl}} \approx 0.6139$ であり、ターゲット $\gamma_{\text{app}} \approx 0.623$ と 1.5% 以内で整合している。しかしながら、個別のサーベイでは **KiDS-Legacy ($k \approx 0.7$) において $\gamma_{\text{impl}} = 0.5973$ (4.1% 乖離)** が観測されており、高 $k$ 領域でのモデル精度には依然として課題が残されている。これは、非線形成長の影響が $\gamma_{\text{app}}$ の対数公式に十分に織り込まれていないことを示唆している。
