# app.py
import streamlit as st
from PIL import Image, ImageOps
from io import BytesIO

st.set_page_config(page_title="crop1080", page_icon="✂️")
st.title("✂️ crop1080 - 左右34pxトリミング & 横1080pxリサイズ")

left = st.number_input("左トリミング(px)", 0, 200, 34)
right = st.number_input("右トリミング(px)", 0, 200, 34)
top = st.number_input("上トリミング(px)", 0, 200, 0)
bottom = st.number_input("下トリミング(px)", 0, 200, 0)
target_width = st.number_input("リサイズ後の横幅(px)", 100, 5000, 1080)

uploaded = st.file_uploader("画像を選択", type=["jpg","jpeg","png","webp","bmp","tiff"])
if uploaded:
    im = Image.open(uploaded)
    im = ImageOps.exif_transpose(im)
    w, h = im.size
    st.write(f"元サイズ: {w}×{h}")
    if w <= left+right or h <= top+bottom:
        st.error("トリミング幅が画像サイズを超えています。値を下げてください。")
    else:
        box = (left, top, w-right, h-bottom)
        cropped = im.crop(box)
        cw, ch = cropped.size
        new_h = round(ch * (target_width / cw))
        resized = cropped.resize((target_width, new_h), Image.LANCZOS)
        st.image(resized, caption="処理後プレビュー", use_column_width=True)
        buf = BytesIO()
        resized.save(buf, format="JPEG", quality=95)
        st.download_button("📥 ダウンロード", buf.getvalue(), "cropped_1080.jpg", "image/jpeg")
