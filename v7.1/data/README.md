# Data Compression Notice

The large\text files in this directory (`CJTwist.*.txt`) have been compressed to `.gz` format to reduce the repository size.

## How to use these files:

If you need to run legacy scripts that expect raw `.txt` files, you must decompress them first:

### On Windows (PowerShell):
```powershell
# Decompress all files
Get-ChildItem *.gz | ForEach-Object { gzip -d $_.FullName }
```

### On Linux/macOS:
```bash
# Decompress all files
gunzip *.gz
```

Alternatively, you can modify your Python scripts to read the compressed files directly using the `gzip` module:

```python
import gzip
with gzip.open('data/CJTwist.9.txt.gz', 'rt') as f:
    content = f.read()
```
