import streamlit as st
import requests
import base64

def extract_text_from_image(image_bytes):
    image_base64 = base64.b64encode(image_bytes).decode()

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "llava",
        "prompt": "Extract all visible text from this image. the text in image is python code and just reply with code that is visible no other text",
        "images": [image_base64],
        "stream": False
    })

    if response.ok:
        return response.json().get("response", "No text found.")
    else:
        return f"Error: {response.text}"

st.title("🖼️ OCR using LLaVA + Ollama")

uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    with st.spinner("Extracting text..."):
        result = extract_text_from_image(uploaded_file.read())
        st.subheader("📄 Extracted Text:")
        st.code(result)
