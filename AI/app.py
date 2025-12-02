
from flask import Flask, render_template, request, session, redirect, url_for, send_file
import requests
import os
import io
app = Flask(__name__)
app.secret_key = os.urandom(24)
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = "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"
WEATHER_API = "a1b4ea281df09d4e4ad532a0b3516686"

def chat_with_groq(message, history=None):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    } 
    system_prompt = {
        "role": "system",
        "content": (
            "You are AgroBot — an expert agricultural assistant. "
            "You provide accurate, clear, and practical answers about farming, "
            "agriculture, crop management, soil health, irrigation, fertilizers, "
            "weather effects, pest control, and sustainable practices. "
            "If a user asks about topics unrelated to agriculture, politely say: "
            "'I'm designed to help only with agriculture-related topics.'"
        )
    }

    messages = [system_prompt]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": message})

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.7
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data)
        print("Status Code:", response.status_code)
        print("Response Body:", response.text)
        response.raise_for_status()
    except Exception as e:
        print("Error:", e)
        return "Error contacting Groq API.", history or []

    try:
        reply = response.json()["choices"][0]["message"]["content"]
        # Save conversation history
        history = history or []
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": reply})
        return reply, history
    except Exception as e:
        print("Parse Error:", e)
        return "Couldn't parse the response.", history or []


@app.route("/", methods=["GET", "POST"])
def index():
    if "username" in session:
        return redirect(url_for("chat"))

    if request.method == "POST":
        session["username"] = request.form["username"]
        session["history"] = []
        return redirect(url_for("chat"))

    return render_template("login.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "username" not in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        user_message = request.form["message"]
        history = session.get("history", [])
        bot_reply, updated_history = chat_with_groq(user_message, history)
        session["history"] = updated_history
    return render_template("chat.html", messages=session.get("history", []), username=session["username"])
@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))
@app.route("/download")
def download_chat():
    chat_log = session.get("history", [])
    content = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_log])
    return send_file(
        io.BytesIO(content.encode()),
        mimetype="text/plain",
        as_attachment=True,
        download_name="chat_log.txt"
    )
import base64
def get_weather(city="Delhi"):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API}&units=metric"
        res = requests.get(url).json()
        weather_text = (
            f"Temperature: {res['main']['temp']}°C, "
            f"Humidity: {res['main']['humidity']}%, "
            f"Condition: {res['weather'][0]['description']}"
        )
        return weather_text
    except:
        return "Weather data unavailable"

@app.route("/soil_detect", methods=["POST"])
def soil_detect():
    if "image" not in request.files:
        return {"error": "No image uploaded"}

    file = request.files["image"]
    img_bytes = file.read()
    img_base64 = base64.b64encode(img_bytes).decode()

    # Weather data
    weather_data = get_weather("Delhi")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # SOIL + WEATHER request
    prompt_text = (
        "Analyze this soil image and weather data.\n"
        "Provide:\n"
        "- Soil type\n"
        "- Moisture level\n"
        "- Fertility\n"
        "- Weather impact\n"
        "- Best crops to grow\n\n"
        f"Weather Data: {weather_data}"
    )

    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt_text
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_base64}"
                        }
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        print("RAW RESPONSE:", response.text)

        data = response.json()

        # If Groq returns an error
        if "error" in data:
            return {"error": data["error"]["message"]}

        # Extract model response
        result = data["choices"][0]["message"]["content"]

        return {
            "result": result,
            "weather": weather_data
        }

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    app.run(debug=True)
