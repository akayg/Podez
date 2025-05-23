# import streamlit as st
# import requests
# import re

# st.title("Python Code Compiler (Piston API)")

# default_code = """
# a = int(input())
# b = int(input())
# print("Sum:", a + b)
# print("Difference:", a - b)
# print("Product:", a * b)
# print("Quotient:", a / b if b != 0 else "undefined")
# """

# user_code = st.text_area("Paste your Python code here:", value=default_code, height=180)

# # Count how many input() calls are in the code
# input_count = len(re.findall(r'input\s*\(', user_code))

# inputs = []
# if input_count > 0:
#     st.info(f"Your code requires {input_count} input value(s). Please provide them below (in order):")
#     for i in range(input_count):
#         user_val = st.text_input(f"Input value #{i+1}:")
#         inputs.append(user_val)

# if st.button("Run Code"):
#     # Join all user inputs with newlines for stdin
#     stdin = "\n".join(inputs) + ("\n" if inputs else "")
#     response = requests.post(
#         "https://emkc.org/api/v2/piston/execute",
#         json={
#             "language": "python3",
#             "version": "3.10.0",
#             "files": [
#                 {"name": "main.py", "content": user_code}
#             ],
#             "stdin": stdin
#         }
#     )
#     st.subheader("Output:")
#     st.code(response.json()["run"]["stdout"])
#     if response.json()["run"]["stderr"]:
#         st.subheader("Errors:")
#         st.code(response.json()["run"]["stderr"])



import streamlit as st
import requests
import tempfile

st.set_page_config(page_title="🧠 OCR Extractor", layout="centered")
st.title("📝 OCR Extractor using OCR.Space API")
st.write("Upload an image with handwritten or printed text, and we'll extract it using OCR.Space API!")

uploaded_file = st.file_uploader("📤 Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name

    st.info("⏳ Sending image to OCR.Space...")

    with open(temp_file_path, 'rb') as image_file:
        url_api = "https://api.ocr.space/parse/image"
        payload = {
            'apikey': 'helloworld',
            'language': 'eng',
            'OCREngine': 2
        }
        response = requests.post(
            url_api,
            files={temp_file_path: image_file},
            data=payload
        )

    result = response.json()

    try:
        extracted_text = result['ParsedResults'][0]['ParsedText']
        st.success("✅ Text Extracted!")
        st.code(extracted_text, language='text')
    except Exception as e:
        st.error("❌ Failed to extract text.")
        st.error(f"Error: {e}")
