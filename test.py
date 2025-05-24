import streamlit as st
import requests
from PIL import Image
import io
import google.generativeai as genai
import toml
import sys
import re

# Load Gemini API key from secrets.toml
def load_gemini_api_key():
    try:
        secrets = toml.load("secrets.toml")
        return secrets.get("GEMINI_API_KEY")
    except Exception as e:
        st.error(f"Error loading Gemini API key: {e}")
        return None

# Execute Python code and capture output
def execute_python_code(code: str, user_inputs: list):
    output = io.StringIO()
    error = None
    try:
        sys.stdout = output
        input_iter = iter(user_inputs)

        def patched_input(prompt=""):
            st.write(f"Prompt: {prompt}")
            return next(input_iter)

        builtins_backup = __import__("builtins")
        original_input = builtins_backup.input
        builtins_backup.input = patched_input

        exec(code, {"__builtins__": builtins_backup.__dict__})
        builtins_backup.input = original_input
    except Exception as e:
        error = str(e)
    finally:
        sys.stdout = sys.__stdout__
    return output.getvalue(), error

# Extract all input() prompts from code
def extract_input_prompts(code):
    if not code:
        return []
    return re.findall(r'input\((.*?)\)', code)

# OCR.space
def extract_text_from_image(image_bytes):
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
        response = requests.post(url, data=payload, files=files)
        result = response.json()
    except Exception:
        st.warning("⚠️ OCR.space API failed or exceeded limit.")
        return ""

    if result.get("IsErroredOnProcessing") or not result.get("ParsedResults"):
        st.warning("⚠️ OCR did not return enough valid code to process.")
        return ""

    return result["ParsedResults"][0].get("ParsedText", "").strip()

# Streamlit main app
def main():
    st.set_page_config(page_title="Handwritten Code Analyzer", layout="centered")
    st.title("✍️ Handwritten Code Analyzer with Gemini")

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

    uploaded_file = st.file_uploader("📤 Upload a code image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        # Only process new uploads
        if uploaded_file.name != st.session_state.last_uploaded_filename:
            st.session_state.last_uploaded_filename = uploaded_file.name
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
            image_bytes = uploaded_file.read()
            extracted_text = extract_text_from_image(image_bytes)

            if not extracted_text:
                st.stop()

            st.write("### 🧾 OCR Extracted Code:")
            st.code(extracted_text, language="python")

            if extracted_text.strip():
                with st.spinner("Refining code with Gemini..."):
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

                    st.session_state.refined_code = corrected_code.strip()
                    st.session_state.user_code = corrected_code.strip()
            else:
                st.warning("OCR result is empty.")
        else:
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    if st.session_state.refined_code:
        st.write("### ✅ Refined Code:")
        # Use user_code for editing, only update it when user edits
        editable_code = st.text_area(
            "✏️ Editable Python Code:",
            st.session_state.user_code or st.session_state.refined_code,
            height=300,
            key="editable_code"
        )
        if editable_code != st.session_state.user_code:
            st.session_state.user_code = editable_code  # Only update if user changed it

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
