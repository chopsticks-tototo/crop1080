import streamlit as st
from PIL import Image, ImageOps
from io import BytesIO
import zipfile
import os

st.set_page_config(page_title="crop1080", page_icon="✂️", layout="wide")
st.title("✂️ crop1080 – 複数画像を左右トリミングして横1080pxにリサイズ")

# ---- サイドバー設定 ----
with st.sidebar:
    st.header("設定")
    left = st.number_input("左トリミング(px)", 0, 2000, 34)
    right = st.number_input("右トリミング(px)", 0, 2000, 34)
    target_width = st.number_input("リサイズ後の横幅(px)", 100, 10000, 1080)
    keep_format = st.checkbox("入力と同じ拡張子で保存（透過保持）", value=True)
    show_preview = st.checkbox("処理後プレビューを表示", value=True)

# ---- ファイルアップロード ----
uploaded_files = st.file_uploader(
    "画像を選択（複数OK）",
    type=["jpg", "jpeg", "png", "webp", "bmp", "tiff"],
    accept_multiple_files=True
)

# ---- 画像処理関数 ----
def process_one(file, left, right, target_width, keep_format):
    im = Image.open(file)
    im = ImageOps.exif_transpose(im)
    w, h = im.size

    if w <= left + right:
        raise ValueError(f"トリミング幅が大きすぎます（{w}x{h}）。")

    # 左右だけトリミング
    box = (left, 0, w - right, h)
    im = im.crop(box)
    cw, ch = im.size

    # 横1080にリサイズ（縦は比率維持）
    if cw != target_width:
        new_h = round(ch * (target_width / cw))
        im = im.resize((target_width, new_h), Image.LANCZOS)

    # 出力形式を決定
    buf = BytesIO()
    default_fmt = "PNG" if keep_format else "JPEG"
    name = getattr(file, "name", "image")
    ext = os.path.splitext(name)[1].lower()
    fmt_map = {
        ".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG",
        ".webp": "WEBP", ".bmp": "BMP", ".tiff": "TIFF"
    }
    out_fmt = fmt_map.get(ext, default_fmt) if keep_format else default_fmt

    save_kwargs = {}
    if out_fmt == "JPEG":
        im = im.convert("RGB")
        save_kwargs.update(dict(quality=95, optimize=True))
    im.save(buf, format=out_fmt, **save_kwargs)
    return im, buf.getvalue(), out_fmt

# ---- メイン処理 ----
if uploaded_files:
    run = st.button("🚀 まとめて処理する")
    if run:
        zip_buf = BytesIO()
        zf = zipfile.ZipFile(zip_buf, "w", compression=zipfile.ZIP_DEFLATED)

        col1, col2 = st.columns(2)
        ok = 0
        errors = []

        for i, uf in enumerate(uploaded_files, 1):
            try:
                img, data, out_fmt = process_one(uf, left, right, target_width, keep_format)
                base, ext = os.path.splitext(getattr(uf, "name", f"image_{i}"))
                ext_out = {
                    "JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp",
                    "BMP": ".bmp", "TIFF": ".tiff"
                }.get(out_fmt, ".jpg")
                out_name = f"{base}{ext_out}"

                zf.writestr(out_name, data)
                ok += 1
                if show_preview:
                    (col1 if i % 2 else col2).image(img, caption=out_name, use_column_width=True)
            except Exception as e:
                errors.append(f"{getattr(uf, 'name', f'image_{i}')} : {e}")

        zf.close()
        zip_bytes = zip_buf.getvalue()

        st.success(f"✅ 完了：{ok}枚処理 / 失敗 {len(errors)}")
        if errors:
            with st.expander("エラーの詳細"):
                for line in errors:
                    st.write("• " + line)

        st.download_button(
            "📦 処理済み画像をZIPでダウンロード",
            data=zip_bytes,
            file_name="crop1080_batch.zip",
            mime="application/zip"
        )
else:
    st.info("左上の「Browse files」またはドラッグ＆ドロップで画像を選んでください。")
