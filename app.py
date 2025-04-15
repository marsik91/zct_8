from flask import Flask, request, jsonify
from flask_cors import CORS
import requests  # to send HTTP requests
from supabase import create_client, Client  # Supabase client

app = Flask(__name__)
CORS(app)

# Supabase configuration
NEURAL_API_URL = "https://diagnosis-api-dobm.onrender.com/predict"
SUPABASE_URL = "https://ycxfujroaqzqtkhvnlan.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InljeGZ1anJvYXF6cXRraHZubGFuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ2MzgwOTcsImV4cCI6MjA2MDIxNDA5N30.egu_7Ve0X6dxFTEapU_QYGNOefQm9aiOHUgh-DKJ-mY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Known symptoms list
all_symptoms = [
    'cough', 'fever', 'headache', 'rash', 'shortness_of_breath',
    'muscle_pain', 'joint_pain', 'fatigue', 'weight_loss', 'stiff_neck',
    'dehydration', 'heart_attack', 'meningitis', 'pneumonia',
    'dengue_fever', 'tuberculosis', 'cancer'
]

@app.route("/api/message", methods=["POST"])
def handle_message():
    data = request.json
    user_message = data.get("message", "").lower()

    # Detect symptoms mentioned in the user's message
    detected_symptoms = [symptom for symptom in all_symptoms if symptom in user_message]

    # Default bot reply
    bot_reply = "Hello! I can help you with health-related questions. Please describe your symptoms."

    # If symptoms were found, send them to the neural API
    if detected_symptoms:
        try:
            nn_response = requests.post(NEURAL_API_URL, json={"symptoms": detected_symptoms})

            if nn_response.status_code == 200:
                diagnosis_data = nn_response.json()
                diagnosis = diagnosis_data.get("diagnosis", "no diagnosis found")
                bot_reply = f"My team and I believe you may have: {diagnosis}."
            else:
                bot_reply = "Sorry, I couldn't get a diagnosis at the moment. Please try again later."

        except Exception as e:
            bot_reply = "There was an error while contacting the diagnosis service."

    # Save the message, symptoms, and reply to Supabase
    try:
        supabase.table("messages").insert({
            "user_message": user_message,
            "symptoms": detected_symptoms,
            "bot_reply": bot_reply
        }).execute()
    except Exception as e:
        print("❌ Failed to insert into Supabase:", e)

    return jsonify({"reply": bot_reply})


if __name__ == "__main__":
    app.run(debug=True)
