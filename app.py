# app.py
import streamlit as st
from PIL import Image
import pytesseract
import google.generativeai as genai
import toml
import io
import sys

# Configure Tesseract path (update if needed)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def load_gemini_api_key():
    try:
        secrets = toml.load("secrets.toml")
        return secrets.get("GEMINI_API_KEY")
    except FileNotFoundError:
        st.error("Error: secrets.toml file not found. Please create this file with your GEMINI_API_KEY.")
    except toml.TomlDecodeError:
        st.error("Error: Could not decode secrets.toml. Please check formatting.")
    return None

def execute_python_code(code: str):
    output = io.StringIO()
    error = None
    try:
        sys.stdout = output
        exec(code, {})
    except Exception as e:
        error = str(e)
    finally:
        sys.stdout = sys.__stdout__
    return output.getvalue(), error

def main():
    st.set_page_config(page_title="Handwritten Code Analyzer with Gemini", layout="centered")
    st.title("✍️ Handwritten Code Analyzer with Gemini ✨")
    st.write("Upload an image of handwritten Python code. We'll extract it, refine it with Gemini, then execute it!")

    GEMINI_API_KEY = load_gemini_api_key()
    .
    if not GEMINI_API_KEY:
        st.stop()

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")

    uploaded_file = st.file_uploader("📤 Choose an image...", type=["jpg", "jpeg", "png"])
    if not uploaded_file:
        return

    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image",  use_container_width=True)

    try:
        extracted_text = pytesseract.image_to_string(image).strip()
    except pytesseract.TesseractNotFoundError:
        st.error("Tesseract OCR not found. Please install it: https://tesseract-ocr.github.io/tessdoc/Installation.html")
        return
    except Exception as e:
        st.error(f"OCR error: {e}")
        return

    if not extracted_text:
        st.warning("No text found in the image.")
        return

    st.write("## Extracted Code (OCR):")
    st.code(extracted_text, language="python")

    with st.spinner("✨ Refining code with Gemini..."):
                prompt = f"""
         Ensure the corrected code is valid Python code and maintains the original intent as much as possible.
         Preserve comments. Output only the corrected Python code and provide only compilable code without any additional explanation.
          as your provided code will be pushed directly to the compiler. Exclude comments, 
          explanations, or anything that is not compilable, and provide neat code only.

{extracted_text}

"""

                import re
                response = model.generate_content(prompt)
                corrected_code = getattr(response, "text", None)
                if corrected_code is None:
                    # Try to extract from candidates if .text is not present
                    candidates = getattr(response, "candidates", [])
                    if candidates and hasattr(candidates[0], "content") and hasattr(candidates[0].content, "parts"):
                        corrected_code = candidates[0].content.parts[0].text
                    elif candidates and isinstance(candidates[0], dict):
                        corrected_code = candidates[0].get("content", None)
                if not corrected_code:
                    st.error("Gemini API did not return any corrected code.")
                    return
                # Extract code block if present
                code_blocks = re.findall(r"```(?:python)?\s*([\s\S]*?)```", corrected_code)
                if code_blocks:
                    corrected_code = code_blocks[0].strip()
                else:
                    corrected_code = corrected_code.strip()

    st.write("## Refined Code (Gemini):")
    st.code(corrected_code, language="python")

    st.write("## Execution Output:")
    output, error = execute_python_code(corrected_code)
    if error:
        st.error(f"Error during execution:\n{error}")
    else:
        st.text(output or "No output.")

    st.markdown("---")
    st.info("💡 Note: Gemini's corrections depend on the clarity of the OCR output and code complexity.")

if __name__ == "__main__":
    main()