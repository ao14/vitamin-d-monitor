# VITAMIN D MONITOR
#### Video Demo:  https://www.youtube.com/watch?v=IKLQqEthMQI

#### Description:
Disclaimer: This project is still an alpha version. No liability is taken for the recommendations of the software.
Furthermore, they are without guarantee. They are NOT reliable health advice.

This web application helps people to monitor their individual needs for Vitamin D based on location data, user input, historical weather data
and weather forecasts. Vitamin D is known to be an essential nutrient  that the body cannot synthesize by itself without being exposed to
UV-B radiation. This radiation occurs year-round only in regions inbetween 35 degrees latitude north and south. The modern lifestyle of spending a lot of time inside
and the lack of the radiation in many regions during winter causes a Vitamin D shortage in the body. This project should assist individuals to
recognize a potential lack in time and react by spending more time outside and supplement Vitamin D if necessary.

#### Design of the project
The project is based on the CS50 Finance distribution code and its design choices. The application is written in Python on the server-side using the Flask
framework. HTML Pages for the client-side are dynamically rendered. Jinja is used for templating and thus simplifing the pages rendering. The HTML
pages are styled using CSS. The pages contain scripts written in JavaScript to facilitate client-side computations. The server-side Database used is
SQLite.


#### Overview of functionality
It is required for the users to create a user account so that they are able to access historical data related to their person.
Once an account is created, users can log in an are directed to /index.html where their current location is determined using the HTML Geolocation API.
Once the location is successful, the users can provide input via a form on how much time they have approximately spent outside in the past week.
Submitting the form hands over not only the user input, but also the user's location data to the server. The server then uses the location data
to call the OpenWeather API. The API hands back the weather data of the past 5 days and the upcoming 7 days to the server. The server then determines
an individual Vitamin D report for the user based on their location, the location's weather and the datetime. If for example the user input that
they spent little time outside and/or there were few sun hours at their location recently, the report will acknowledge this and recommend to spend
more time outside (if the weather forecast anticipates sun hours) or will suggest the usage of Vitamin D supplements.
On the contrary, if the user spend a lot of time outside and the matching weather data showed a lot  of cloudless sun hours, the report will diagnose
that no action needs to be taken.

The report is saved in /history.html so that the user can get an overview over longer time periods. As the location is determined again at every login,
the application can be used worldwide and for users whose location may change frequently.

#### Project files, folders and their functionality

/static
Contains images, icons and the css stylesheet that contains the styling for the HTML pages

/templates
Various templates to render all routes the webapp is providing.
'layout.html' is the base template on which all other templates extend
'apology.html' is for error handling,
'index.html' is the main page of the app providing Vitamin D request and display functionality.
'history.html' provides the user an overview on past reports they have requested.
'login.html' provides a simple login page for users that have already registered.
'register.html' provides a simple webform to create an account providing username and a password.

app.db
User data such as the username, their password hash, their reports etc are persistently saved here. If the user is requesting an new report the report is also
written to the database, if they request their past reports, they also have reading access to this database.

application.py
The main engine or controller of the application. All routes are here, rendering of the html pages, important function calls etc are done here.

helpers.py
Here is where all the heavy lifiting is done, such as doing multiple API calls, parsing data, and compiling the actual report.

README.md
Recursive function :)

#### How to run the application
1. Get an API key by making a free account at https://openweathermap.org/api
2. Go into the project root folder
3. In terminal, execute 'export API_KEY=<your api key>'
4. In terminal, execute 'flask run'


