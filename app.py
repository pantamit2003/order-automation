from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 🔥 MULTI WAREHOUSE CONFIG
ACCOUNTS = {
    "RATAN": {
        "cred": "billdesk@swissmilitaryindia.com",
        "password": "Emiza@123",
        "seller_id": "80000493",
        "warehouse_id": "600071"
    },
    "ACT B2B": {
        "cred": "act@swissmilitaryindia.com",
        "password": "Swiss@123",
        "seller_id": "80000332",
        "warehouse_id": "600040"
    },

    #Retail WARHOUSE
    "RETAIL": {
        "cred": "billdesk@swissmilitaryindia.com",
        "password": "Emiza@123",
        "seller_id": "80000333",
        "warehouse_id": "600040"
    }
}

# ✅ HOME
@app.route("/")
def home():
    return "Server Running 🚀"


# 🔥 CREATE ORDER
@app.route("/create-order", methods=["POST"])
def create_order():
    try:
        data = request.json

        # -----------------------
        # 🧠 STEP 0: GET WAREHOUSE
        # -----------------------
        warehouse = data.get("warehouse")
        account = ACCOUNTS.get(warehouse)

        if not account:
            return jsonify({
                "status": "FAILED",
                "message": "Invalid warehouse"
            })

        # -----------------------
        # 🔐 STEP 1: LOGIN
        # -----------------------
        login_url = "https://edge-service.emizainc.com/identity-service/user/login"

        login_payload = {
            "cred": account["cred"],
            "password": account["password"],
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
                "message": "Login failed"
            })

        # -----------------------
        # 📦 STEP 2: LINE ITEMS
        # -----------------------
        line_items = data.get("line_items", [])

        if not line_items:
            return jsonify({
                "status": "FAILED",
                "message": "No line_items received"
            })

        for item in line_items:
                # ✅ MRP ALWAYS 0
                item["lineitem_price"] = 0
            
                # ✅ Selling price MUST come from sheet
                if "selling_price_new" not in item or item["selling_price_new"] in [None, "", 0]:
                    return jsonify({
                        "status": "FAILED",
                        "message": f"Missing or invalid price for SKU: {item.get('lineitem_sku')}"
                    })
            
                # ✅ force numeric
                item["selling_price_new"] = float(item["selling_price_new"])
            
                # ✅ required fields
                item["shelf_life"] = 0
                item["zone"] = None
                item["id"] = None
                        
        # -----------------------
        # 📦 STEP 3: ORDER API
        # -----------------------
        order_url = "https://edge-service.emizainc.com/aggregator/api/ve1/oms/manual"

        order_headers = {
            "pim-sid": pim_sid,
            "x-device-id": "armaze-web",
            "x-seller-id": account["seller_id"],
            "x-tenant-id": "1",
            "x-user-id": "300000000850",
            "x-warehouse-id": account["warehouse_id"],
            "content-type": "application/json"
        }

        order_payload = {
                "name": data.get("name"),
                "phone": data.get("phone"),
                "same_as_billing": data.get("same_as_billing"),
                "shipping_name": data.get("shipping_name"),
                "shipping_phone": data.get("shipping_phone"),
            
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
            
                # 🔥 IMPORTANT CHANGE
                "source": "seller-dashboard",
            
                "uploaded_by": data.get("uploaded_by"),
            
                # 🔥 NEW FIELD
                "remarks": data.get("remarks")
            }

        order_res = requests.post(order_url, json=order_payload, headers=order_headers)

        print("ORDER RESPONSE:", order_res.text)

        order_result = order_res.json()

        # 🔥 ORDER ID
        order_id = None
        if "callbacks" in order_result and order_result["callbacks"]:
            order_id = list(order_result["callbacks"].keys())[0]

        # -----------------------
        # ✅ RESPONSE
        # -----------------------
        if order_res.status_code == 200 and order_result.get("id"):
            return jsonify({
                "status": "SUCCESS",
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

# 🔥 GET ORDER STATUS
@app.route("/get-order-status/<order_id>", methods=["GET"])
def get_order_status(order_id):

    try:

        # 🔥 GET WAREHOUSE FROM URL
        warehouse = request.args.get("warehouse")

        account = ACCOUNTS.get(warehouse)

        if not account:
            return jsonify({
                "status": "FAILED",
                "message": "Invalid warehouse"
            })

        # 🔐 LOGIN FIRST
        login_url = "https://edge-service.emizainc.com/identity-service/user/login"

        login_payload = {
            "cred": account["cred"],
            "password": account["password"],
            "user_type": "SELLERS",
            "is_otp_login": False
        }

        login_headers = {
            "content-type": "application/json",
            "x-device-id": "armaze-web"
        }

        login_res = requests.post(
            login_url,
            json=login_payload,
            headers=login_headers
        )

        pim_sid = login_res.headers.get("pim-sid")

        if not pim_sid:
            return jsonify({
                "status": "FAILED",
                "message": "Login failed"
            })

        # 🔥 ORDER STATUS API
        status_url = f"https://edge-service.emizainc.com/warehouse-order-processing-service/api/v1/warehouse/order/{order_id}"

        status_headers = {
            "pim-sid": pim_sid,
            "x-device-id": "armaze-web",
            "x-seller-id": account["seller_id"],
            "x-tenant-id": "1",
            "x-user-id": "300000000850",
            "x-warehouse-id": account["warehouse_id"],
            "content-type": "application/json"
        }

        status_res = requests.get(
            status_url,
            headers=status_headers
        )

        print("STATUS CODE:", status_res.status_code)
        print("STATUS RESPONSE:", status_res.text)

        result = status_res.json()

        # 🔥 TRY MULTIPLE FIELDS
        live_status = (
            result.get("result", {}).get("status")
            or "NOT FOUND"
        )

        return jsonify({
            "success": True,
            "order_id": order_id,
            "warehouse": warehouse,
            "status": live_status,
            "raw": result
        })

    except Exception as e:

        print("STATUS ERROR:", str(e))

        return jsonify({
            "success": False,
            "message": str(e)
        })

# 🔥 RUN
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
