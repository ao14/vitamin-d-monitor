import os
import requests
from datetime import datetime
import time


from flask import redirect, render_template, request, session
from functools import wraps

#'global variables'
forecast_range = 5
api_key = os.environ.get("API_KEY")
exclude = "minutely,hourly,alerts"
day_unix = 86400


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup_future(lat, lon):
    """recieve current, future weather"""

    # Contact API
    try:
        url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={exclude}&appid={api_key}"
        response = requests.get(url)
        # raise_for_status checks http status and if 200, no exception will be raised
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        data = response.json()
        api_response = []
        # needs to be calculated as api does not provide accurate historical uv index data
        user_midday = ((data['current']['sunrise'] + data['current']['sunset']) / 2)

        for i in range(forecast_range):
            api_response.append({
                "date": time_convert(data['daily'][i]['dt']),
                "uvi": data['daily'][i]['uvi'],
                "clouds": data['daily'][i]['clouds'],
            })

        return api_response, user_midday

    except (KeyError, TypeError, ValueError):
        return None


def lookup_history(lat, lon, user_midday):
    """recieve historical weather"""

    api_response = []
    # unix time format in seconds, subtract 5 days from now
    timestamp = (user_midday - (day_unix * forecast_range))
    # initiate list to call api for the five days before - api design required
    date_list = [timestamp]
    # create list cointaining all unix dates of the past five days
    for i in range(4):
        timestamp = timestamp + day_unix
        date_list.append(timestamp)

    # loop through past 5 days
    for day in date_list:
        # Contact API
        try:
            url = f"https://api.openweathermap.org/data/2.5/onecall/timemachine?lat={lat}&lon={lon}&dt={day}&appid={api_key}"
            response = requests.get(url)
            # raise_for_status checks http status and if 200, no exception will be raised
            response.raise_for_status()
        except requests.RequestException:
            return None

        # Parse response
        try:
            data = response.json()

            api_response.append({
                "date": time_convert(data['current']['dt']),
                "uvi": data['current']['uvi'],
            })

        except (KeyError, TypeError, ValueError):
            return None

    return api_response


def make_report(api_history, user_input):

    # calculate average uv index for the past five days
    uvi_average = 0
    for i in api_history:
        uvi_average += i['uvi']
    uvi_average = uvi_average/len(api_history)

    # determine uvi level
    if uvi_average < 3:
        uvi_level = "low"
    elif 3 <= uvi_average < 6:
        uvi_level = "moderate"
    elif 6 <= uvi_average < 8:
        uvi_level = "high"
    else:
        uvi_level = "very high to extreme"

    # match the average index with user's input on time spent outside
    if 2 < uvi_average < 6 and user_input >= 1:
        recommendation = "You have had some opportunities to fill up your Vitamin D recently. You might want to spend some more time outside the next week and/or think about supplementing Vitamin D. \n"
    elif 2 < uvi_average < 6 and user_input == 2:
        recommendation = "You had opportunities to fill up your Vitamin D recently. You are on a good streak, continue to spend time outside in the coming days. \n"
    elif uvi_average >= 6 and user_input > 0:
        recommendation = "You had plenty of opportunities to fill up your Vitamin D recently. No need to act as of now. Check in back soon. \n"
    elif uvi_average >= 6 and user_input == 0:
        recommendation = "You had plenty of opportunities to fill up your Vitamin D at your location recently, but did not spend enough time outside. You might want to use the next days for getting a sunbath. \n"
    elif uvi_average <= 2 or 2 < uvi_average < 6 and user_input < 1:
        recommendation = "You only had a few opportunities to fill up your Vitamin D recently. You might want to spend more time outside the next week and/or think about supplementing Vitamin D. \n"
    else:
        recommendation = " \n"

    report = (
        "Hello " + session["user_name"] + "\n \n"
        + "Disclaimer: This application is still in pre-alpha. This is NO medical advice. \n \n"
        + "The average UV Index at your location in the past five days was " + str(round(uvi_average, 1)) + ". \n"
        + "That is a " + uvi_level + " index value based on the UV Index scale of 0 - 11. \n"
        + recommendation
    )

    return report


def time_convert(date):
    """change between UNIX and standard time/date"""
    return datetime.utcfromtimestamp(date).strftime('%Y-%m-%d')