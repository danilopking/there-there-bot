import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def send_message(chat_id, text):
    requests.post(f"{URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data and "text" in data["message"]:
        user_message = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]

        if user_message.lower() == "/start":
            welcome_text = (
                "Hello. I know things might be tough right now.\n"
                "I’m here, and I’m listening — if you feel like talking.\n"
                "What’s been happening? What are you feeling?\n"
                "You can share as much or as little as you want."
            )
            send_message(chat_id, welcome_text)
        else:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }, json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a warm, emotionally intelligent companion. Your job is to gently support the user. Don't give advice, don't solve problems, just be present and emotionally safe."
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            })

            reply = response.json()["choices"][0]["message"]["content"]
            send_message(chat_id, reply + "\n\nI'm here if you want to talk again.")

    return {"ok": True}
