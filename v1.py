import streamlit as st
import requests
from PIL import Image, ImageOps
import io
import google.generativeai as genai
import toml
import sys
import re
import pytesseract
import builtins

@st.cache_resource(show_spinner=False)
def load_gemini_api_key():
    try:
        secrets = toml.load("secrets.toml")
        return secrets.get("GEMINI_API_KEY")
    except Exception as e:
        st.error(f"Error loading AI API key: {e}")
        return None

def preprocess_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    image = ImageOps.exif_transpose(image)
    image = image.convert("RGB")
    image.thumbnail((1024, 1024))
    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()

@st.cache_data(show_spinner=False)
def ocr_space_extract(image_bytes):
    url = "https://api.ocr.space/parse/image"
    payload = {
        'apikey': 'helloworld',
        'language': 'eng',
        'isOverlayRequired': False
    }
    files = {
        'file': ('image.png', image_bytes, 'image/png')
    }
    try:
        response = requests.post(url, data=payload, files=files, timeout=15)
        result = response.json()
    except Exception:
        return "", "⚠️ OCR.space API failed or exceeded limit."
    if result.get("IsErroredOnProcessing") or not result.get("ParsedResults"):
        return "", "⚠️ OCR did not return enough valid code to process."
    return result["ParsedResults"][0].get("ParsedText", "").strip(), None

@st.cache_data(show_spinner=False)
def tesseract_extract(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image, lang="eng")
        return text.strip(), None
    except Exception as e:
        return "", f"⚠️ Tesseract OCR failed: {e}"

def extract_text_from_image(image_bytes, engine="OCR.space"):
    if engine == "OCR.space":
        return ocr_space_extract(image_bytes)
    else:
        return tesseract_extract(image_bytes)

def execute_python_code(code: str, user_inputs: list):
    output = io.StringIO()
    error = None
    try:
        sys.stdout = output
        input_iter = iter(user_inputs)
        def patched_input(prompt=""):
            st.write(f"Prompt: {prompt}")
            return next(input_iter)
        original_input = builtins.input
        builtins.input = patched_input
        exec(code, {"__builtins__": builtins.__dict__})
        builtins.input = original_input
    except Exception as e:
        error = str(e)
    finally:
        sys.stdout = sys.__stdout__
    return output.getvalue(), error

def extract_input_prompts(code):
    if not code:
        return []
    return re.findall(r'input\((.*?)\)', code)

def refine_code_with_gemini(model, extracted_text):
    prompt = f"""
    Refine this Python code. Only correct syntax and structure errors.
    DO NOT explain anything. DO NOT change logic or language. Just return valid Python code:
    {extracted_text}
    """
    response = model.generate_content(prompt)
    corrected_code = response.text or ""
    code_blocks = re.findall(r"```(?:python)?\s*([\s\S]*?)```", corrected_code)
    if code_blocks:
        corrected_code = code_blocks[0].strip()
    return corrected_code.strip()

def main():
    st.set_page_config(page_title="DexRun Ai", layout="centered")
    st.title("✍️ DexRun Ai")

    GEMINI_API_KEY = load_gemini_api_key()
    if not GEMINI_API_KEY:
        st.stop()

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")

    if "refined_code" not in st.session_state:
        st.session_state.refined_code = None
    if "user_code" not in st.session_state:
        st.session_state.user_code = None
    if "last_uploaded_filename" not in st.session_state:
        st.session_state.last_uploaded_filename = None
    if "ocr_engine" not in st.session_state:
        st.session_state.ocr_engine = "OCR.space"

    st.session_state.ocr_engine = st.radio(
        "Choose OCR Engine:",
        options=["OCR.space(API)", "Tesseract(Model)"],
        index=0,
        horizontal=True,
        key="ocr_engine_radio"
    )

    uploaded_file = st.file_uploader("📤 Upload a code image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        if uploaded_file.name != st.session_state.last_uploaded_filename or st.session_state.ocr_engine != st.session_state.get("last_ocr_engine"):
            st.session_state.last_uploaded_filename = uploaded_file.name
            st.session_state.last_ocr_engine = st.session_state.ocr_engine
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
            image_bytes = uploaded_file.read()
            extracted_text, ocr_error = extract_text_from_image(image_bytes, st.session_state.ocr_engine)
            if ocr_error:
                st.warning(ocr_error)
                st.stop()
            if not extracted_text:
                st.warning("OCR result is empty.")
                st.stop()
            st.write("### 🧾 OCR Extracted Code:")
            st.code(extracted_text, language="python")
            with st.spinner("Refining code with Ai..."):
                corrected_code = refine_code_with_gemini(model, extracted_text)
                st.session_state.refined_code = corrected_code
                st.session_state.user_code = corrected_code
        else:
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    if st.session_state.refined_code:
        st.write("### ✅ Refined Code:")
        editable_code = st.text_area(
            "✏️ Editable Python Code:",
            st.session_state.user_code or st.session_state.refined_code,
            height=300,
            key="editable_code"
        )
        if editable_code != st.session_state.user_code:
            st.session_state.user_code = editable_code

        input_prompts = extract_input_prompts(st.session_state.user_code)
        user_inputs = []
        if input_prompts:
            st.warning("⚠️ Code has input() statements. Provide values below.")
            for idx, prompt in enumerate(input_prompts):
                safe_prompt = prompt.strip("'\"")
                value = st.text_input(f"Input {idx + 1} - {safe_prompt}", key=f"input_{idx}")
                user_inputs.append(value)

        if st.button("🚀 Run Code"):
            if st.session_state.user_code:
                output, error = execute_python_code(st.session_state.user_code, user_inputs)
                st.write("### 🖥️ Output:")
                if error:
                    st.error(f"Error: {error}")
                else:
                    st.code(output or "No output.")
            else:
                st.warning("No code to execute.")

if __name__ == "__main__":
    main()
