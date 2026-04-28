from flask import Flask, request, jsonify
import requests

app = Flask(__name__)   # 🔥 YE LINE MUST HAI

@app.route("/")
def home():
    return "Server Running 🚀"

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


# 🔥 LOCAL RUN (IMPORTANT)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
