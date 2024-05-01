import io, base64
import matplotlib.pyplot as plt
from flask_bootstrap import Bootstrap4
from flask import Flask, render_template,redirect, url_for, request, session, flash

from datetime import timedelta
import client

app = Flask(__name__)
bootstrap = Bootstrap4(app)
app.secret_key = "hello"

app.permanent_session_lifetime = timedelta(minutes=5)


@app.route('/')
def home():
    return redirect(url_for("login_user"))

@app.route("/login", methods=["POST", "GET"])
def login_user():
    if request.method == "POST":
        session.permanent = True
        user = request.form["username"]
        password = request.form["password"]

        user_id= client.login(user, password)
        if user_id:
            session["user"]=user_id
            return redirect(url_for("user"))
        else:
            flash ("Login Error")
            return redirect(url_for("login_user"))

    else:
        if "user" in session:
            return redirect(url_for("user"))

        return render_template("login.html")

@app.route("/user", methods=['GET', 'POST'])
def user():
    if "user" in session:
        if request.method == "POST":
            node = request.form["sub_button"]   

            vbat=client.plot_sensor_data(client.get_sensor_data(session["user"], node, 7))

            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()

            plot_encoded = base64.b64encode(image_png).decode('utf-8')
            return render_template("graphics.html", plot_encoded=plot_encoded, value=vbat)
        else: 
            return render_template("nodes.html")
    else:
        return redirect(url_for("login_user"))

@app.route("/logout")
def logout():
	session.pop("user", None)
	return redirect(url_for("login"))

@app.route("/register", methods=["POST", "GET"])
def register_u():
    if request.method == "POST":
        session.permanent = True
        user = request.form["username"]
        password = request.form["password"]

        user_id= client.register_user(user, password)
        if user_id:
            session["user"]=user_id
            return redirect(url_for("user"))
        else:
            flash ("Registration Error")
            return redirect(url_for("register_u"))

    else:
        if "user" in session:
            return redirect(url_for("user"))

        return render_template("register.html")

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5001)
