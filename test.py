import streamlit as st
st.set_page_config(page_title="Handwritten OCR with TrOCR", layout="centered")

from PIL import Image
import numpy as np
import cv2
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import torch

# Load model only once
@st.cache_resource
def load_model():
    processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
    model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")
    return processor, model

processor, model = load_model()
def preprocess_image(image: Image.Image):
    img = np.array(image.convert("L"))  # Grayscale
    img = cv2.resize(img, (800, 800), interpolation=cv2.INTER_LINEAR)
    _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return Image.fromarray(img).convert("RGB")  # 🔥 Convert back to RGB


st.title("📝 Handwritten OCR with TrOCR")
st.write("Upload a handwritten image — we'll clean it up and read it using TrOCR.")

uploaded_file = st.file_uploader("📤 Upload Handwritten Code Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Original Image", use_column_width=True)

    with st.spinner("🧼 Preprocessing image..."):
        clean_image = preprocess_image(image)
        st.image(clean_image, caption="Preprocessed Image", use_column_width=True)

    with st.spinner("🤖 Reading handwriting with TrOCR..."):
        pixel_values = processor(images=clean_image, return_tensors="pt").pixel_values
        generated_ids = model.generate(pixel_values)
        extracted_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        st.success("✅ Handwriting Extracted!")
        st.code(extracted_text, language="python")
