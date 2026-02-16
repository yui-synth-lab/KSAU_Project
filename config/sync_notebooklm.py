import os
import json
import shutil

def sync_notebooklm():
    config_path = 'config/notebooklm_sync_list.json'
    target_dir = 'NotebookLM_Upload'
    if not os.path.exists(config_path): raise FileNotFoundError(config_path)
    if not os.path.exists(target_dir): os.mdirs(target_dir)
    with open(config_path, 'r', encoding='utf-8') as f: config = json.load(f)
    print(f"Synchronizing {target_dir}...")
    for f in os.listdir(target_dir): os.remove(os.path.join(target_dir, f))
    for item in config['sync_list']: 
        src = item['source']
        dst = os.path.join(target_dir, item['target'])
        if os.path.exists(src): 
            shutil.copy2(src, dst)
            print(f"  Copied: { src} -> {dst}")
        else: print(f"  WARNING: Source not found: {src}")

if __name__ == "__main__": sync_notebooklm()
