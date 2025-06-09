```markdown
# Podez

Podez is an advanced AI-powered platform designed to bridge the gap between handwritten code and executable, refined Python programs. Leveraging state-of-the-art OCR (Optical Character Recognition) and generative AI models, Podez enables users to upload images of handwritten or printed Python code, extract and correct the code, and execute it—all within a secure, interactive web interface.

---

## 🚀 Features

- **Handwritten Code Recognition:**  
    Upload images of handwritten or printed Python code and extract text using OCR (Tesseract or OCR.Space API).

- **AI-Powered Code Refinement:**  
    Automatically corrects syntax and structure errors in extracted code using Google Gemini generative AI.

- **Interactive Code Editing:**  
    Edit the refined code directly in the browser before execution.

- **Safe Code Execution:**  
    Run Python code securely with support for user input prompts.

- **Downloadable Results:**  
    Download the corrected Python code for further use.

- **Multiple OCR Engines:**  
    Choose between local (Tesseract) and cloud (OCR.Space) OCR engines for flexibility and accuracy.

---

## 🛠️ Installation

1. **Clone the Repository**
     ```sh
     git clone https://github.com/akayg/podez.git
     cd podez
     ```

2. **Create and Activate a Virtual Environment**
     ```sh
     python3 -m venv venv
     source venv/bin/activate  # On Windows: venv\Scripts\activate
     ```

3. **Install Dependencies**
     ```sh
     pip install -r requirements.txt
     ```

     *Required libraries include:*  
     `streamlit`, `pytesseract`, `Pillow`, `requests`, `google-generativeai`, `toml`

4. **Install Tesseract OCR**  
     - [Tesseract Installation Guide](https://tesseract-ocr.github.io/tessdoc/Installation.html)

5. **Configure API Keys**  
     - Create a `secrets.toml` file in the project root:
         ```toml
         GEMINI_API_KEY = "your-gemini-api-key"
         ```

---

## 💻 Usage

1. **Start the Streamlit App**
     ```sh
     streamlit run v2.py
     ```
     *(You can also run app.py, v1.py, or test.py for different interfaces and experiments.)*

2. **Upload an Image**
     - Upload a `.jpg`, `.jpeg`, or `.png` image containing handwritten or printed Python code.

3. **Extract, Refine, and Run**
     - The app will extract code, refine it using Gemini AI, and allow you to edit and execute it interactively.

---

## 📦 Project Structure

- `app.py` — Main Streamlit app (simple workflow)
- `v1.py`, `v2.py`, `test.py` — Advanced and experimental interfaces
- `ocr.py` — LLaVA + Ollama-based OCR demo
- `api.py` — API and alternative OCR/compilation demos
- `secrets.toml` — API key configuration (not included in repo)
- `notes.txt` — Setup and development notes

---

## 🧠 Technologies Used

- **Streamlit** — Interactive web app framework
- **Tesseract OCR** — Local optical character recognition
- **OCR.Space API** — Cloud-based OCR
- **Google Gemini** — Generative AI for code correction
- **Pillow** — Image processing
- **Python** — Core language

---

## ⚠️ Disclaimer

- **Security:**  
    Executing arbitrary code can be dangerous. Podez includes basic input handling, but always review and sandbox code before running in production environments.

- **API Limits:**  
    Free OCR.Space API keys have usage limits. For production, obtain a paid API key.

---

## 📄 License

This project is licensed under the MIT License. See LICENSE for details.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Please open an issue or submit a pull request.

---

## 📬 Contact

For questions or support, please contact [email@abhishekgore.com](mailto:email@abhishekgore.com).

---

*Podez — AI meets code, from paper to execution.*
```
