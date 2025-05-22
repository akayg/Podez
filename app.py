# app.py
import streamlit as st
from PIL import Image
import pytesseract
import google.generativeai as genai
import toml



# Point to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# Load secrets from the toml file
try:
    secrets = toml.load("secrets.toml")
    GEMINI_API_KEY = secrets.get("GEMINI_API_KEY")
except FileNotFoundError:
    GEMINI_API_KEY = None
    st.error("Error: secrets.toml file not found. Please create this file in the same directory and add your GEMINI_API_KEY.")
except toml.TomlDecodeError:
    GEMINI_API_KEY = None
    st.error("Error: Could not decode secrets.toml. Please ensure the file is correctly formatted.")

if GEMINI_API_KEY is None:
    st.stop()
else:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")

    st.set_page_config(page_title="Handwritten Code Analyzer with Gemini", layout="centered")

    st.title("✍️ Handwritten Code Analyzer with Gemini ✨")
    st.write("Upload an image of your handwritten code, we'll extract it using OCR and then refine it with Gemini!")

    uploaded_file = st.file_uploader("📤 Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_column_width=True)

        st.write("## Extracted Code (OCR):")
        try:
            extracted_text = pytesseract.image_to_string(image)
            st.code(extracted_text, language="python")

            if extracted_text:
                with st.spinner("✨ Refining code with Gemini..."):
                    prompt = f"""Please review and correct the following potentially misrecognized code. Ensure the corrected code is valid and maintains the original intent as much as possible. If there are comments, preserve them. Output only the corrected code.

                    ```
                    {extracted_text}
                    ```
                    """
                    response = model.generate_content(prompt)
                    corrected_code = response.text

                    st.write("## Refined Code (Gemini):")
                    st.code(corrected_code, language="python")

        except pytesseract.TesseractNotFoundError:
            st.error("Tesseract is not installed or not in your PATH. Please install it to use this feature.")
            st.info("You can find installation instructions here: https://tesseract-ocr.github.io/tessdoc/Installation.html")
        except Exception as e:
            st.error(f"An error occurred during OCR: {e}")

    st.markdown("---")
    st.info("💡 **Note:** Gemini's ability to correct the code depends on the complexity and clarity of the initial OCR output.")
    