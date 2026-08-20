# Python AI Programming Chatbot 🤖

A beginner-friendly AI programming chatbot built using **Python, Flask, SQLite, Ollama, and Llama 3.2**. It helps users learn programming, generate code, understand errors, debug programs, and maintain conversation history.

## ✨ Features

- 💬 Interactive chatbot interface
- 🐍 Python programming assistance
- 💻 Code generation
- 🐛 Code debugging and error explanation
- 📖 Code explanation
- 🔧 Code improvement suggestions
- 🧠 SQLite-based conversation memory
- 🤖 Local AI responses using Llama 3.2 through Ollama
- 📚 Basic predefined responses using `data.json`
- 🎨 Responsive Bootstrap interface
- 🚀 Beginner-friendly project structure

## 🛠️ Technologies Used

- Python
- Flask
- SQLite
- HTML
- Bootstrap
- JavaScript
- JSON
- Ollama
- Llama 3.2

## 📁 Project Structure

```text
session3/
├── app.py
├── data.json
├── db.sqlite
├── requirements.txt
├── README.md
└── templates/
    └── index.html
```

## ⚙️ Requirements

- Python 3.x
- Flask
- Requests
- Ollama
- Llama 3.2 model

## 🚀 Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd session3
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up Ollama

Check your installed models:

```bash
ollama list
```

Make sure `llama3.2:latest` is available.

If it is not installed:

```bash
ollama pull llama3.2
```

Test the model:

```bash
ollama run llama3.2
```

### 4. Run the Flask application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## 💡 Example Questions

```text
What is Python?

Write a Python program to add two numbers.

Create a Python calculator.

Explain this Python code.

Find the error in this code.

Convert this Python program to Java.

How can I improve this code?
```

## 🧠 How It Works

```text
User
  ↓
Bootstrap Chat Interface
  ↓
Flask /chat API
  ↓
Chatbot Logic
  ├── data.json for basic responses
  └── Ollama + Llama 3.2 for AI responses
  ↓
SQLite
  ↓
Chat History
```

The chatbot stores conversations in `db.sqlite` and can use recent chat history as basic memory.

## 🎯 Project Objective

The objective of this project is to create a simple AI-powered programming assistant that helps beginners understand programming concepts and practice writing, explaining, and debugging code.

## 🔮 Future Improvements

- Secure Python code execution
- Support for additional programming languages
- User accounts and separate chat histories
- Code syntax highlighting
- Chat export functionality
- Improved long-term memory
- Voice input and output

## 📌 Note

This project uses a **local Llama model through Ollama**, so Ollama must be installed and running on the computer where the application is executed.

Generated code should always be reviewed and tested before being used in real applications.

## 👩‍💻 Author

**Chaturthi Fagare**

A beginner-friendly college project for learning Python, Flask, databases, and local AI integration.
