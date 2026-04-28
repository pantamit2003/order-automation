import requests
import json

session = requests.Session()

# 🔐 LOGIN API
login_url = "https://edge-service.emizainc.com/identity-service/user/login"

login_payload = {
    "cred": "billdesk@swissmilitaryindia.com",  # 🔥 MUST
    "password": "Emiza@123",
    "user_type": "SELLERS",
    "is_otp_login": False
}

headers = {
    "content-type": "application/json",
    "x-device-id": "armaze-web"
}

login_res = session.post(login_url, json=login_payload, headers=headers)

# ✅ STATUS CHECK
print("STATUS CODE:", login_res.status_code)

# ✅ BODY PRINT
print("\n===== LOGIN RESPONSE BODY =====")
try:
    print(json.dumps(login_res.json(), indent=2))
except:
    print(login_res.text)

# ✅ HEADERS PRINT
print("\n===== LOGIN RESPONSE HEADERS =====")
for key, value in login_res.headers.items():
    print(f"{key}: {value}")

# 🔥 PIM-SID EXTRACT
pim_sid = login_res.headers.get("pim-sid")

print("\n🔥 PIM SID:", pim_sid)

# ❗ SAFETY CHECK
if not pim_sid:
    print("❌ ERROR: PIM SID nahi mila → login issue")
else:
    print("✅ READY FOR ORDER API")
