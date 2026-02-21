# KSAU Monitoring Protocol (v38.0)

**作成日:** 2026-02-21
**ステータス:** ACTIVE (Passive Monitoring Phase)
**目的:** Euclid/LSST などの次世代サーベイによる $S_8$ 測定結果を監視し、KSAU の予測と照合するための手順書。

---

## 1. 監視対象と頻度

### 1.1 監視ソース
以下のキーワードで arXiv (astro-ph.CO) および NASA ADS を定期的にチェックする。

- **キーワード:** "Euclid weak lensing S8", "LSST cosmic shear", "S8 tension", "KiDS-1000", "DES Y3", "HSC-SSP"
- **推奨ツール:** arXiv RSS フィード, Google Scholar Alerts

### 1.2 監視頻度
- **通常時:** 週次 (Weekly)
- **主要リリース時 (Data Release):** 即時 (Daily)

---

## 2. 照合手順 (Verification Workflow)

新しい $S_8$ 測定値が報告された場合、以下の手順で KSAU の予測と照合する。

### 2.1 予測値の確認 (SSoT)
`v36.0/task_a_s8_verification_design.md` に記載された以下の範囲を参照する。

| Survey | Target Redshift ($z_{eff}$) | Predicted $S_8$ (KSAU) |
|--------|-----------------------------|------------------------|
| Euclid | $0.9 - 1.2$                 | **0.724 – 0.761**      |
| LSST   | $0.6 - 0.9$                 | **0.739 – 0.783**      |

### 2.2 判定基準
報告された測定値 $S_{8,obs} \pm \sigma_{obs}$ と比較し、以下のいずれかに分類する。

1. **CONSISTENT (一致):** $|S_{8,obs} - S_{8,pred}| \le 1\sigma$
   - KSAU の予測範囲内に収まっている。
2. **TENSION (緊張):** $1\sigma < |S_{8,obs} - S_{8,pred}| \le 3\sigma$
   - わずかなずれがあるが、統計的変動の範囲内。
3. **EXCLUDED (棄却):** $|S_{8,obs} - S_{8,pred}| > 3\sigma$
   - KSAU の予測と明確に矛盾する。

---

## 3. ログの更新 (`s8_monitoring_log.md`)

`v37.0/s8_monitoring_log.md` (または最新のログファイル) に以下のフォーマットで追記する。

```markdown
### [YYYY-MM-DD] {Survey Name} (arXiv:{ID})
- **Title:** {Paper Title}
- **Measured S8:** {Value} ± {Error}
- **Redshift:** z = {Redshift}
- **Verdict:** {CONSISTENT / TENSION / EXCLUDED}
- **Notes:** {Brief comment on methodology or specific cuts used}
```

---

## 4. 重大な結果への対応 (Action Plan)

### 4.1 支持 (Strong Support)
- **条件:** Euclid/LSST の $S_8$ が $0.74 \pm 0.01$ 付近で確定し、かつ $\Lambda$CDM ($S_8 \approx 0.83$) を $5\sigma$ 以上で排除した場合。
- **アクション:** プロジェクトを再起動し、v39.0 として「KSAU 宇宙論モデルの確立」フェーズを開始する。

### 4.2 棄却 (Refutation)
- **条件:** $S_8 > 0.80$ (Planck 整合) または $S_8 < 0.70$ (極端な抑制) が確定した場合。
- **アクション:** KSAU の宇宙論セクターを「棄却済み」としてマークし、プロジェクトを完全終了 (Final Shutdown) する。

### 4.3 モデル修正 (Modification)
- **条件:** $S_8$ のズレが $3\sigma$ 程度で、かつ $z$ 依存性が KSAU の予測と異なる傾向を示す場合。
- **アクション:** v39.0 として「モデル修正フェーズ」を開始し、スケール依存性のパラメータ ($\kappa$ など) を再検討する。

---

*This protocol is maintained by Gemini SSoT Auditor.*
