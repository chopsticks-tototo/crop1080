# crop1080

左右34pxずつトリミングして横1080pxにリサイズするツール。  
ファイル名はそのままで保存します。

## 使い方

```bash
python -m venv .venv
source .venv/bin/activate  # Windowsは .venv\Scripts\activate
pip install -e .
crop1080 input.jpg
