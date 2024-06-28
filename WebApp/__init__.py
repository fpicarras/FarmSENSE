import io, base64
import matplotlib.pyplot as plt
from flask_bootstrap import Bootstrap4
from flask import Flask, render_template,redirect, url_for, request, session, flash
import datetime
import json
from datetime import datetime, date

from datetime import timedelta
import client

app = Flask(__name__)
bootstrap = Bootstrap4(app)
app.secret_key = "hello"

app.permanent_session_lifetime = timedelta(minutes=60)


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
            session["username"]=user
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
            if "sub_button" in request.form:
                node = request.form["sub_button"]
                session["node"] = node
                days = 1

            if "submit_button" in request.form:
                batata = request.form["submit_button"]
                node = session["node"]

                selected_option = request.form.get("humidity")

                if selected_option == "today":
                    days = 1
                elif selected_option == "week":
                    days = 7
                elif selected_option == "month":
                    days = 28 
                elif selected_option == "year":
                    days = 365 

            if "data_button" in request.form:
                start_date = request.form["trip-start"]
                client.setData(session["user"], "startDate", start_date)

                username = session["username"] 

                # Get status messages
                status_messages = client.get_status(session["user"])

                # Get images
                disease_image = client.get_disease(session["user"], "static/disease_image.png")
                status_image = client.get_image(session["user"], "static/image.png")
                client.get_prevision(session["user"], "static/prevision.png")

                # Get Dates
                start_date = client.getData(session["user"], "startDate")
                expected_harvest = client.getData(session["user"], "expectedHarvest")
                today_date = date.today().isoformat()

                # Get number of days
                start_date_obj = datetime.fromisoformat(start_date).date()
                expected_harvest_obj = datetime.fromisoformat(expected_harvest).date()
                today_date_obj = date.fromisoformat(today_date)
                cycle_duration = (expected_harvest_obj - start_date_obj).days
                days_left = (expected_harvest_obj - today_date_obj).days
                date_obj = datetime.strptime(expected_harvest, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d / %m / %Y')

                # Get nodes
                node_list = client.get_current_status(session["user"])

                return render_template("nodes.html", username=username, node_list=node_list, status_messages=status_messages, status_image=status_image, disease_image=disease_image, expected_harvest=formatted_date, start_date=start_date, cycle_duration=cycle_duration, days_left=days_left)

            else:
                # Get status messages
                status_messages = client.get_status(session["user"])

                vbat = client.plot_sensor_data(client.get_sensor_data(session["user"], node, days))
                    
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                image_png = buffer.getvalue()
                buffer.close()

                plot_encoded = base64.b64encode(image_png).decode('utf-8')
                username = session["username"] 

                # Get node list
                node_list = client.get_node_list(session["user"])

                # Data to be plotted
                data = client.get_sensor_data(session["user"], node, days)

                timestamps = [datetime.strptime(measurement[4], '%Y-%m-%d %H:%M:%S') for measurement in data]
                air_temp = [measurement[0] for measurement in data]
                air_humidity = [measurement[1] for measurement in data]
                soil_humidity = [measurement[2] for measurement in data]
                luminosity = [measurement[3] for measurement in data]

                timestamps_iso = [dt.isoformat() for dt in timestamps]

                timestamps_json = json.dumps(timestamps_iso)
                air_humidity_json = json.dumps(air_humidity)
                soil_humidity_json = json.dumps(soil_humidity)
                air_temperature_json= json.dumps(air_temp)
                luminosity_json = json.dumps(luminosity)

                return render_template("graphics.html", value=vbat, username=username, node_list=node_list, timestamps=timestamps_json, air_humidity=air_humidity_json, soil_humidity=soil_humidity_json, air_temperature=air_temperature_json, luminosity=luminosity_json, plot_encoded=plot_encoded)
            
        else: 

            username = session["username"] 

            # Get status messages
            status_messages = client.get_status(session["user"])

            # Get images
            disease_image = client.get_disease(session["user"], "static/disease_image.png")
            status_image = client.get_image(session["user"], "static/image.png")
            client.get_prevision(session["user"], "static/prevision.png")

            # Get Dates
            start_date = client.getData(session["user"], "startDate")
            expected_harvest = client.getData(session["user"], "expectedHarvest")
            today_date = date.today().isoformat()

            # Get number of days
            start_date_obj = datetime.fromisoformat(start_date).date()
            expected_harvest_obj = datetime.fromisoformat(expected_harvest).date()
            today_date_obj = date.fromisoformat(today_date)
            cycle_duration = (expected_harvest_obj - start_date_obj).days
            days_left = (expected_harvest_obj - today_date_obj).days
            date_obj = datetime.strptime(expected_harvest, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d / %m / %Y')

            # Get nodes
            node_list = client.get_current_status(session["user"])

            return render_template("nodes.html", username=username, node_list=node_list, status_messages=status_messages, status_image=status_image, disease_image=disease_image, expected_harvest=formatted_date, start_date=start_date, cycle_duration=cycle_duration, days_left=days_left)
    else:
        return redirect(url_for("login_user"))

@app.route("/logout")
def logout():
	session.pop("user", None)
	return redirect(url_for("login_user"))

@app.route("/register", methods=["POST", "GET"])
def register_u():
    if request.method == "POST":
        session.permanent = True
        user = request.form["username"]
        password = request.form["password"]

        user_id= client.register_user(user, password)
        if user_id:
            session["user"]=user_id
            session["username"]=user
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
