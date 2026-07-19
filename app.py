from flask import Flask, render_template
import os

app = Flask(__name__)


def detect_platform():
    if os.environ.get("RENDER"):
        return "Render"
    if os.environ.get("HEROKU"):
        return "Heroku"
    if os.environ.get("KOYEB"):
        return "Koyeb"
    if os.path.exists("/app/.dockerenv"):
        return "Docker"
    return "VPS"


@app.route("/")
def home():
    return render_template("welcome.html", platform=detect_platform())


@app.route("/health")
def health():
    return "OK"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
