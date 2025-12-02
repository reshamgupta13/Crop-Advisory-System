from flask import Flask, render_template, request
from mandi_api import fetch_mandi_price


app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    data = None

    if request.method == "POST":
        crop = request.form["crop"]
        state = request.form["state"]

        data = fetch_mandi_price(crop, state)

    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)
