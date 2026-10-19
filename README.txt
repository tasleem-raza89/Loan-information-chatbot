LOANWISE CHATBOT - HTML, CSS, JAVASCRIPT + PYTHON BACKEND

1. Extract this ZIP into a folder.
2. Open Command Prompt / VS Code terminal in that folder.
3. Install dependencies:
   pip install -r requirements.txt
4. Make sure Ollama is installed and running, and the llama3.2 model is available:
   ollama pull llama3.2
5. Start the website:
   python app.py
6. Open this address in your browser:
   http://127.0.0.1:5000

FILES:
- app.py                 Python Flask backend and loan response logic
- templates/index.html   Website structure
- static/style.css       Website design and responsive layout
- static/script.js       Chat interaction and API request
- requirements.txt       Python packages

NOTE:
The website uses Ollama at http://localhost:11434 with model llama3.2.
If Ollama is unavailable, the backend falls back to basic knowledge-base answers.
The old Streamlit app is replaced by this Flask version so HTML/CSS/JavaScript can control the full design.
Do not put API keys or passwords into frontend HTML/JavaScript.
