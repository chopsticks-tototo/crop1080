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

uploaded_file = st.file_uploader("画像を選択してください", type=["jpg", "jpeg", "png", "webp", "bmp", "tiff"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    image = ImageOps.exif_transpose(image)
    w, h = image.size
    st.write(f"元サイズ: {w}×{h}")

    if st.button("トリミング＆リサイズ実行"):
        if w <= left + right or h <= top + bottom:
            st.error("指定されたトリミング幅が画像サイズを超えています。")
        else:
            box = (left, top, w - right, h - bottom)
            cropped = image.crop(box)
            cw, ch = cropped.size
            new_h = round(ch * (target_width / cw))
            resized = cropped.resize((target_width, new_h), Image.LANCZOS)

            st.image(resized, caption="処理後の画像", use_column_width=True)

            # ダウンロード用
            buf = BytesIO()
            resized.save(buf, format="JPEG", quality=95)
            byte_im = buf.getvalue()

            st.download_button(
                label="📥 処理済み画像をダウンロード",
                data=byte_im,
                file_name="cropped_1080.jpg",
                mime="image/jpeg"
            )
