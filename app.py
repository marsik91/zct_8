from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # дозволяє запити з фронтенду

@app.route("/api/message", methods=["POST"])
def handle_message():
    data = request.json
    user_message = data.get("message", "").lower()

    if "привіт" in user_message:
        response = "Привіт! Як справи?"
    else:
        response = "Я поки розумію тільки привітання 😊"

    return jsonify({"reply": response})

if __name__ == "__main__":
    app.run(debug=True)