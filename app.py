from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ✅ HOME CHECK
@app.route("/")
def home():
    return "Server Running 🚀"


# 🔥 CREATE ORDER (MULTI SKU SUPPORT)
@app.route("/create-order", methods=["POST"])
def create_order():
    try:
        data = request.json

        # -----------------------
        # 🔐 STEP 1: LOGIN API
        # -----------------------
        login_url = "https://edge-service.emizainc.com/identity-service/user/login"

        login_payload = {
            "cred": "billdesk@swissmilitaryindia.com",
            "password": "Emiza@123",
            "user_type": "SELLERS",
            "is_otp_login": False
        }

        login_headers = {
            "content-type": "application/json",
            "x-device-id": "armaze-web"
        }

        login_res = requests.post(login_url, json=login_payload, headers=login_headers)

        pim_sid = login_res.headers.get("pim-sid")

        print("LOGIN RESPONSE:", login_res.text)
        print("PIM SID:", pim_sid)

        if not pim_sid:
            return jsonify({
                "status": "FAILED",
                "message": "Login failed (no pim-sid)"
            })


        # -----------------------
        # 📦 STEP 2: PREPARE LINE ITEMS (MULTI SKU)
        # -----------------------
        line_items = data.get("line_items", [])

        if not line_items or len(line_items) == 0:
            return jsonify({
                "status": "FAILED",
                "message": "No line_items received"
            })

        # 🔥 fix required fields
        for item in line_items:
            item["shelf_life"] = 0
            if not item.get("lineitem_price"):
                item["lineitem_price"] = 1


        # -----------------------
        # 📦 STEP 3: ORDER API
        # -----------------------
        order_url = "https://edge-service.emizainc.com/aggregator/api/ve1/oms/manual"

        order_headers = {
            "pim-sid": pim_sid,
            "x-device-id": "armaze-web",
            "x-seller-id": "80000493",
            "x-tenant-id": "1",
            "x-user-id": "300000000850",
            "x-warehouse-id": "600071",
            "content-type": "application/json"
        }

        order_payload = {
            "name": data.get("name"),
            "phone": data.get("phone"),
            "same_as_billing": data.get("same_as_billing"),
            "shipping_name": data.get("shipping_name"),
            "shipping_phone": data.get("shipping_phone"),

            # 🔥 MULTI SKU
            "line_items": line_items,

            "billing_address1": data.get("billing_address1"),
            "billing_state": data.get("billing_state"),
            "billing_city": data.get("billing_city"),
            "billing_pincode": data.get("billing_pincode"),
            "shipping_address1": data.get("shipping_address1"),
            "shipping_state": data.get("shipping_state"),
            "shipping_city": data.get("shipping_city"),
            "shipping_pincode": data.get("shipping_pincode"),
            "business_type": data.get("business_type"),
            "source": data.get("source"),
            "uploaded_by": data.get("uploaded_by")
        }

        order_res = requests.post(order_url, json=order_payload, headers=order_headers)

        print("ORDER RESPONSE:", order_res.text)

        order_result = order_res.json()

        # 🔥 ORDER ID EXTRACT
        order_id = None
        if "callbacks" in order_result and order_result["callbacks"]:
            order_id = list(order_result["callbacks"].keys())[0]


        # -----------------------
        # ✅ SUCCESS / FAIL CHECK
        # -----------------------
        if order_res.status_code == 200 and order_result.get("id"):
            return jsonify({
                "status": "SUCCESS",
                "message": "Order Created Successfully",
                "order_id": order_id,
                "emiza_response": order_result
            })
        else:
            return jsonify({
                "status": "FAILED",
                "message": order_result
            })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({
            "status": "ERROR",
            "message": str(e)
        })


# 🔥 RUN SERVER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
