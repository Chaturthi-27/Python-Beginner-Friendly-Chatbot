from flask import Flask, render_template, request, jsonify
import sqlite3
import json
import re
import requests
from datetime import datetime


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)


# =========================================================
# SETTINGS
# =========================================================

DB_NAME = "db.sqlite"
DATA_FILE = "data.json"

# Ollama local API
OLLAMA_URL = "http://localhost:11434/api/chat"

# Your installed Ollama model
MODEL_NAME = "llama3.2:latest"


# =========================================================
# DATABASE
# =========================================================

def init_db():
    """
    Create the SQLite database and chat history table.
    """

    connection = sqlite3.connect(DB_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    connection.commit()

    connection.close()


def save_message(user_message, bot_response):
    """
    Save a conversation in SQLite.
    """

    connection = sqlite3.connect(DB_NAME)

    cursor = connection.cursor()

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        INSERT INTO chat_history
        (user_message, bot_response, timestamp)
        VALUES (?, ?, ?)
    """, (
        user_message,
        bot_response,
        timestamp
    ))

    connection.commit()

    connection.close()


def get_chat_history(limit=10):
    """
    Get recent conversations from SQLite.
    """

    connection = sqlite3.connect(DB_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT user_message, bot_response
        FROM chat_history
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()

    connection.close()

    return list(reversed(rows))


# =========================================================
# JSON DATA
# =========================================================

def load_chat_data():
    """
    Load basic chatbot information from data.json.
    """

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as error:

        print("Could not load data.json:", error)

        return {}


chat_data = load_chat_data()


# =========================================================
# BASIC RULE-BASED RESPONSES
# =========================================================

def get_basic_response(user_message):
    """
    Check data.json for simple predefined responses.

    Returns:
        response if a match is found
        None if no match is found
    """

    message = user_message.lower().strip()

    best_response = None

    best_score = 0


    for category, details in chat_data.items():

        if category == "fallback":
            continue


        keywords = details.get(
            "keywords",
            []
        )


        for keyword in keywords:

            keyword = keyword.lower().strip()


            # Phrase
            if " " in keyword:

                if keyword in message:

                    score = len(keyword)

                    if score > best_score:

                        responses = details.get(
                            "responses",
                            []
                        )

                        if responses:

                            best_response = responses[0]

                            best_score = score


            # Single word
            else:

                words = re.findall(
                    r"\b\w+\b",
                    message
                )

                if keyword in words:

                    score = len(keyword)

                    if score > best_score:

                        responses = details.get(
                            "responses",
                            []
                        )

                        if responses:

                            best_response = responses[0]

                            best_score = score


    return best_response


# =========================================================
# DETECT USER'S NAME
# =========================================================

def find_name(message):
    """
    Detect a name from messages such as:

    My name is Rahul
    I am Rahul
    I'm Rahul
    """

    patterns = [

        r"\bmy name is ([a-zA-Z]+)\b",

        r"\bi am ([a-zA-Z]+)\b",

        r"\bi'm ([a-zA-Z]+)\b"

    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            message,
            re.IGNORECASE
        )

        if match:

            return match.group(1).capitalize()


    return None


def get_saved_name():
    """
    Search SQLite for a previously provided name.
    """

    history = get_chat_history(50)


    patterns = [

        r"\bmy name is ([a-zA-Z]+)\b",

        r"\bi am ([a-zA-Z]+)\b",

        r"\bi'm ([a-zA-Z]+)\b"

    ]


    for user_message, bot_response in reversed(history):

        for pattern in patterns:

            match = re.search(
                pattern,
                user_message,
                re.IGNORECASE
            )

            if match:

                return match.group(1).capitalize()


    return None


# =========================================================
# CALL LLAMA THROUGH OLLAMA
# =========================================================

def ask_llama(user_message):
    """
    Send the user's question to the local
    Llama 3.2 model through Ollama.
    """

    # Get previous conversations
    history = get_chat_history(8)


    # System instruction for the AI
    system_prompt = """
You are ChatBuddy, a beginner-friendly AI programming assistant.

Your main purpose is to help students learn programming.

You can:

1. Explain programming concepts.
2. Generate code.
3. Debug code.
4. Fix code.
5. Explain code line by line.
6. Suggest improvements.
7. Convert code between programming languages.
8. Help with Python, Java, C, C++, HTML, CSS,
   JavaScript, SQL, Flask and basic programming.
9. Answer normal questions when appropriate.

IMPORTANT RULES:

- Give clear and beginner-friendly explanations.
- When generating code, provide complete working code.
- When debugging code, explain what the error is,
  why it happens, and then provide corrected code.
- Do not invent errors that are not present.
- If the user provides code, analyze the actual code.
- Keep explanations simple.
- Use Markdown formatting for code.
- Put programming code inside code blocks.
- Do not claim that code was executed unless it actually was.
- If the question is unrelated to programming,
  answer briefly and politely.
"""


    # Create messages for Llama
    messages = [

        {
            "role": "system",
            "content": system_prompt
        }

    ]


    # Add previous conversation memory
    for old_user_message, old_bot_response in history:

        messages.append({

            "role": "user",

            "content": old_user_message

        })


        messages.append({

            "role": "assistant",

            "content": old_bot_response

        })


    # Add current question
    messages.append({

        "role": "user",

        "content": user_message

    })


    # Send request to Ollama
    response = requests.post(

        OLLAMA_URL,

        json={

            "model": MODEL_NAME,

            "messages": messages,

            "stream": False

        },

        timeout=120

    )


    # Check HTTP status
    response.raise_for_status()


    # Convert response to JSON
    result = response.json()


    # Extract Llama response
    bot_response = result.get(
        "message",
        {}
    ).get(
        "content",
        ""
    )


    if not bot_response:

        return (
            "I received an empty response from "
            "Llama. Please try again."
        )


    return bot_response.strip()


# =========================================================
# MAIN CHATBOT FUNCTION
# =========================================================

def get_bot_response(user_message):
    """
    Decide whether to use:

    1. Memory
    2. Basic JSON responses
    3. Llama AI
    """


    # -----------------------------------------------------
    # NAME MEMORY
    # -----------------------------------------------------

    name = find_name(user_message)


    if name:

        return (
            f"Nice to meet you, {name}! "
            "I will remember your name."
        )


    # -----------------------------------------------------
    # ASK REMEMBERED NAME
    # -----------------------------------------------------

    name_questions = [

        "what is my name",

        "do you know my name",

        "remember my name",

        "tell me my name"

    ]


    message_lower = user_message.lower()


    for question in name_questions:

        if question in message_lower:

            saved_name = get_saved_name()


            if saved_name:

                return (
                    f"Your name is {saved_name}. "
                    "I remember it from our previous conversation."
                )


            return (
                "You haven't told me your name yet. "
                "You can say: My name is Rahul."
            )


    # -----------------------------------------------------
    # BASIC JSON RESPONSE
    # -----------------------------------------------------

    basic_response = get_basic_response(
        user_message
    )


    if basic_response:

        return basic_response


    # -----------------------------------------------------
    # LLAMA AI
    # -----------------------------------------------------

    return ask_llama(
        user_message
    )


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# CHAT ROUTE
# =========================================================

@app.route(
    "/chat",
    methods=["POST"]
)
def chat():

    try:

        data = request.get_json()


        if not data:

            return jsonify({

                "response":
                "No message was received."

            }), 400


        user_message = data.get(
            "message",
            ""
        ).strip()


        print("\n================================")

        print(
            "User:",
            user_message
        )


        if not user_message:

            return jsonify({

                "response":
                "Please type a message."

            })


        # Generate response
        bot_response = get_bot_response(
            user_message
        )


        print(
            "Bot:",
            bot_response
        )


        # Save conversation
        save_message(
            user_message,
            bot_response
        )


        print("Conversation saved.")

        print("================================\n")


        return jsonify({

            "response":
            bot_response

        })


    except requests.exceptions.ConnectionError:

        print(
            "ERROR: Ollama is not running."
        )


        return jsonify({

            "response":
            "I cannot connect to Ollama. "
            "Please make sure Ollama is running "
            "and that llama3.2:latest is installed."

        }), 500


    except requests.exceptions.Timeout:

        print(
            "ERROR: Ollama took too long to respond."
        )


        return jsonify({

            "response":
            "Llama took too long to respond. "
            "Please try again."

        }), 500


    except Exception as error:

        print("\n========== ERROR ==========")

        print(error)

        print("===========================\n")


        return jsonify({

            "response":
            "Something went wrong. "
            "Please check the Flask terminal."

        }), 500


# =========================================================
# CHAT HISTORY
# =========================================================

@app.route(
    "/history",
    methods=["GET"]
)
def history():

    rows = get_chat_history(20)


    history_data = []


    for row in rows:

        history_data.append({

            "user_message":
            row[0],

            "bot_response":
            row[1]

        })


    return jsonify(
        history_data
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    init_db()


    print(
        "======================================="
    )

    print(
        "     Python AI Programming Chatbot"
    )

    print(
        "======================================="
    )

    print(
        "Model:",
        MODEL_NAME
    )

    print(
        "Ollama:",
        OLLAMA_URL
    )

    print(
        "Website:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print(
        "======================================="
    )


    app.run(
        debug=True
    )