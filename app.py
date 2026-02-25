import requests
from flask import Flask, render_template
from datetime import datetime
import config

app = Flask(__name__)

def get_token():
    r = requests.post(config.TOKEN_URL, data={
        "grant_type": "client_credentials",
        "client_id": config.CLIENT_ID,
        "client_secret": config.CLIENT_SECRET
    })
    r.raise_for_status()
    return r.json()["access_token"]

def get_orders():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(config.API_URL, headers=headers)
    r.raise_for_status()
    return r.json()

@app.route("/")
def home():
    data = get_orders()
    orders = []

    for item in data:
        status = item.get("status", "Unknown")
        completed = item.get("completed_at")

        if completed:
            completed = datetime.fromisoformat(
                completed.replace("Z","")
            ).strftime("%d/%m %H:%M")
        else:
            completed = "-"

        orders.append({
            "fb": item.get("delivery_instructions",""),
            "order": item.get("order_number"),
            "status": status,
            "completed": completed,
            "color": "green" if status == "Dispatched" else "red"
        })

    orders.sort(key=lambda x: x["completed"], reverse=True)

    return render_template("index.html", orders=orders)

app.run(host="0.0.0.0", port=8080)