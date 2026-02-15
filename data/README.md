# Knot and Link Data Compression Notice

The database files in this directory have been compressed to `.gz` format to minimize the repository size.

## Files:
- `knotinfo_data_complete.csv.gz` (Compressed from ~84 MB)
- `linkinfo_data_complete.csv.gz` (Compressed from ~15 MB)

## Usage:

### Automatic Handling
Most updated KSAU scripts (e.g., in `v6.0/code/` and `v7.0/code/`) are designed to look for the `.csv.gz` version if the raw `.csv` is missing.

### Manual Decompression
If you need the raw `.csv` files for legacy scripts or external tools:

**PowerShell:**
```powershell
gzip -d data/*.gz
```

**Linux/macOS:**
```bash
gunzip data/*.gz
```

### Python (Direct Reading)
You can read the compressed CSV directly using `pandas`:
```python
import pandas as pd
df = pd.read_csv('data/knotinfo_data_complete.csv.gz', compression='gzip', sep='|')
```
