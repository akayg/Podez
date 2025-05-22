import streamlit as st
import requests
import re

st.title("Python Code Compiler (Piston API)")

default_code = """
a = int(input())
b = int(input())
print("Sum:", a + b)
print("Difference:", a - b)
print("Product:", a * b)
print("Quotient:", a / b if b != 0 else "undefined")
"""

user_code = st.text_area("Paste your Python code here:", value=default_code, height=180)

# Count how many input() calls are in the code
input_count = len(re.findall(r'input\s*\(', user_code))

inputs = []
if input_count > 0:
    st.info(f"Your code requires {input_count} input value(s). Please provide them below (in order):")
    for i in range(input_count):
        user_val = st.text_input(f"Input value #{i+1}:")
        inputs.append(user_val)

if st.button("Run Code"):
    # Join all user inputs with newlines for stdin
    stdin = "\n".join(inputs) + ("\n" if inputs else "")
    response = requests.post(
        "https://emkc.org/api/v2/piston/execute",
        json={
            "language": "python3",
            "version": "3.10.0",
            "files": [
                {"name": "main.py", "content": user_code}
            ],
            "stdin": stdin
        }
    )
    st.subheader("Output:")
    st.code(response.json()["run"]["stdout"])
    if response.json()["run"]["stderr"]:
        st.subheader("Errors:")
        st.code(response.json()["run"]["stderr"])