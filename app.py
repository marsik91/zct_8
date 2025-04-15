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
    'itching', 'skin_rash', 'nodal_skin_eruptions', 'continuous_sneezing',
    'shivering', 'chills', 'joint_pain', 'stomach_pain', 'acidity',
    'ulcers_on_tongue', 'muscle_wasting', 'vomiting', 'burning_micturition',
    'spotting_ urination', 'fatigue', 'weight_gain', 'anxiety',
    'cold_hands_and_feets', 'mood_swings', 'weight_loss', 'restlessness',
    'lethargy', 'patches_in_throat', 'irregular_sugar_level',
    'cough', 'high_fever', 'sunken_eyes', 'breathlessness', 'sweating',
    'dehydration', 'indigestion', 'headache', 'yellowish_skin',
    'dark_urine', 'nausea', 'loss_of_appetite', 'pain_behind_the_eyes',
    'back_pain', 'constipation', 'abdominal_pain', 'diarrhoea', 'mild_fever',
    'yellow_urine', 'yellowing_of_eyes', 'acute_liver_failure',
    'fluid_overload', 'swelling_of_stomach', 'swelled_lymph_nodes',
    'malaise', 'blurred_and_distorted_vision', 'phlegm',
    'throat_irritation', 'redness_of_eyes', 'sinus_pressure',
    'runny_nose', 'congestion', 'chest_pain', 'weakness_in_limbs',
    'fast_heart_rate', 'pain_during_bowel_movements', 'pain_in_anal_region',
    'bloody_stool', 'irritation_in_anus', 'neck_pain', 'dizziness',
    'cramps', 'bruising', 'obesity', 'swollen_legs', 'swollen_blood_vessels',
    'puffy_face_and_eyes', 'enlarged_thyroid', 'brittle_nails',
    'swollen_extremeties', 'excessive_hunger', 'extra_marital_contacts',
    'drying_and_tingling_lips', 'slurred_speech', 'knee_pain',
    'hip_joint_pain', 'muscle_weakness', 'stiff_neck', 'swelling_joints',
    'movement_stiffness', 'spinning_movements', 'loss_of_balance',
    'unsteadiness', 'weakness_of_one_body_side', 'loss_of_smell',
    'bladder_discomfort', 'foul_smell_of urine', 'continuous_feel_of_urine',
    'passage_of_gases', 'internal_itching', 'toxic_look_(typhos)',
    'depression', 'irritability', 'muscle_pain', 'altered_sensorium',
    'red_spots_over_body', 'belly_pain', 'abnormal_menstruation',
    'dischromic _patches', 'watering_from_eyes', 'increased_appetite',
    'polyuria', 'family_history', 'mucoid_sputum', 'rusty_sputum',
    'lack_of_concentration', 'visual_disturbances', 'receiving_blood_transfusion',
    'receiving_unsterile_injections', 'coma', 'stomach_bleeding',
    'distention_of_abdomen', 'history_of_alcohol_consumption',
    'fluid_overload.1', 'blood_in_sputum', 'prominent_veins_on_calf',
    'palpitations', 'painful_walking', 'pus_filled_pimples', 'blackheads',
    'scurring', 'skin_peeling', 'silver_like_dusting', 'small_dents_in_nails',
    'inflammatory_nails', 'blister', 'red_sore_around_nose',
    'yellow_crust_ooze'
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
