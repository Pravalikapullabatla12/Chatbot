from flask import Flask, render_template, request, jsonify, session
import json
import random
from textblob import TextBlob

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# === Load dataset ===
with open("AiData.json", "r", encoding="utf-8") as f:
    data = json.load(f)

faq_entries = data.get("mental_health_qa", [])

chatbot_features = {
    "friendly_greeting": [
        "Hi there! I'm really glad you're here. How can I help you today?",
        "Hey! You're not alone. How can I support you today?",
        "Welcome! I'm here for you. What would you like to talk about?"
    ],
    "story_invitation": [
        "Absolutely. I'm listening. Tell me everything you want to share 💬",
        "Of course, go ahead. I'm here to hear you out without judgment 🫂"
    ],
    "story_complete_response": [
        "Thank you so much for sharing. You're incredibly brave. 🫂",
        "That must have been tough. You're not alone. 💙",
        "I’m really grateful you opened up. You deserve support. ❤"
    ],
    "support_suggestions": [
        "- Try deep breathing or mindfulness.",
        "- Talk to a trusted friend or family member.",
        "- Keep a journal to express your emotions.",
        "- Seek help from a licensed counselor or therapist.",
        "- Remember, you're not alone. Support is available."
    ],
    "guided_exercises": [
        {
            "type": "breathing",
            "name": "Box Breathing",
            "steps": [
                "Inhale through your nose for 4 seconds.",
                "Hold your breath for 4 seconds.",
                "Exhale through your mouth for 4 seconds.",
                "Hold your breath again for 4 seconds.",
                "Repeat for 4 cycles."
            ]
        }
    ]
}

def find_best_match(user_input):
    user_words = user_input.lower().split()
    best_match = None
    max_overlap = 0

    for entry in faq_entries:
        question_words = entry["question"].lower().split()
        overlap = len(set(user_words) & set(question_words))
        if overlap > max_overlap:
            best_match = entry
            max_overlap = overlap

    return best_match if max_overlap > 0 else None

def analyze_sentiment(user_input):
    analysis = TextBlob(user_input)
    return analysis.sentiment.polarity

def get_bot_response(user_input):
    user_input = user_input.lower().strip()

    # === Exit ===
    if user_input in ["quit", "bye", "exit", "thank you", "thankyou"]:
        session.pop("story_mode", None)
        session.pop("story_parts", None)
        return "I'm always here if you need to talk again. Take care 💚"

    # === End Story Mode ===
    if user_input in ["done", "that's it", "finished"]:
        story_log = session.pop("story_parts", [])
        session.pop("story_mode", None)
        return random.choice(chatbot_features["story_complete_response"])

    # === If user is currently storytelling ===
    if session.get("story_mode"):
        story = session.get("story_parts", [])
        story.append(user_input)
        session["story_parts"] = story
        return "I'm listening... 📝"

    # === Trigger storytelling mode ===
    if any(phrase in user_input for phrase in ["i want to talk", "i need help", "can i share", "i want to tell my story"]):
        session["story_mode"] = True
        session["story_parts"] = []
        return random.choice(chatbot_features["story_invitation"])

    # === Greetings ===
    if any(word in user_input for word in ["hi", "hello", "hey", "hii"]):
        return random.choice(chatbot_features["friendly_greeting"])

    # === Guided Exercise ===
    if any(word in user_input for word in ["exercise", "calm", "breathe"]):
        ex = random.choice(chatbot_features["guided_exercises"])
        steps = "\n".join(ex["steps"])
        return f"🧘 Let's try the '{ex['name']}' ({ex['type']}):\n{steps}"

    # === Try FAQ Matching ===
    match = find_best_match(user_input)
    if match:
        return match["answer"]

    # === Fallback: Sentiment check ===
    sentiment = analyze_sentiment(user_input)
    if sentiment < -0.3:
        return "I sense you're feeling low. Want to talk or try an exercise?"
    elif sentiment > 0.3:
        return "I'm glad you're feeling okay! 😊"
    else:
        return "I'm here for you. Would you like to talk more or try a calming activity?"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    bot_response = get_bot_response(user_input)
    return jsonify({"response": bot_response})

'''if __name__ == "__main__":
    app.run(debug=True)'''
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)

