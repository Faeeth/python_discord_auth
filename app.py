import os
from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)  # RANDOM AND SAFE SECRET KEY

@app.route("/", methods=["POST", "GET"])
def index():
    if check_session():
        return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("discord_login"))

@app.route("/discord_login", methods=["POST", "GET"])
def discord_login():
    return render_template("discord_login.html")

@app.route("/process_auth", methods=["POST", "GET"])
def process_auth():
    code = request.args.get('code')
    if code:
        data = {
            "code": code,
            "client_id" : "CHANGEME",
            "client_secret" : "CHANGEME",
            "grant_type" : "authorization_code",
            "scope": "identify%20guids",
            "redirect_uri" : "http://127.0.0.1/process_auth" # CHANGE IP AND ADD THIS URL IN OAUTH2 DISCORD REDIRECTS IN YOUR DISCORD APPLICATION SETTINGS
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        r = requests.post(url="https://discordapp.com/api/oauth2/token",data=data, headers=headers)
        result = r.json()
        if "access_token" in result:
            #print("access_token",result["access_token"],sep="-->")
            headers = {
                "Authorization": f"Bearer {result['access_token']}",
                "Content-Type" : "application/x-www-form-urlencoded"
            }
            r = requests.get(url="https://discordapp.com/api/users/@me", headers=headers)
            result = r.json()
            for item in ("id","username","avatar","discriminator","locale"):
                session[item] = result[item] if item in result else None
            if session["avatar"] and session["id"]:
                session["avatar"] = f"https://cdn.discordapp.com/avatars/{session['id']}/{session['avatar']}.png"
        return redirect(url_for("dashboard"))
    else:
        session.clear() # LOGIN ERROR -- CLEAR (YOU CAN LOG IT)
        return redirect("/")

@app.route("/dashboard", methods=["POST", "GET"])
def dashboard():
    if check_session():
        return render_template("dashboard.html")
    else:
        return redirect("/")

@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.clear()
    return redirect("/")


def check_session():
    return True if "id" in session else False

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=80)
