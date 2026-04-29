from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ✅ HOME
@app.route("/")
def home():
    return "Server Running 🚀"


# 🔐 GET PIM (REAL)
@app.route("/get-pim", methods=["GET"])
def get_pim():
    login_url = "https://edge-service.emizainc.com/identity-service/user/login"

    payload = {
        "cred": "billdesk@swissmilitaryindia.com",
        "password": "Emiza@123",
        "user_type": "SELLERS",
        "is_otp_login": False
    }

    headers = {
        "content-type": "application/json",
        "x-device-id": "armaze-web"
    }

    res = requests.post(login_url, json=payload, headers=headers)

    pim_sid = res.headers.get("pim-sid")

    return jsonify({
        "pim_sid": pim_sid
    })


# 🔥 CREATE ORDER (TEST VERSION)
@app.route("/create-order", methods=["POST"])
def create_order():
    data = request.json

    return jsonify({
        "status": "SUCCESS",
        "received_data": data
    })


# 🔥 RUN
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
