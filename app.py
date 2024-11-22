from flask import Flask, request
import requests
from dotenv import load_dotenv
import datetime

load_dotenv()

app = Flask(__name__)

API_KEY = "2e572d843c252f03f711e312401ad7b8"  # Replace with your actual API key


@app.route("/", methods=["GET", "POST"])
def home():
    weather_results = []
    error_message = None

    if request.method == "POST":
        cities = request.form.get("cities")
        unit = request.form.get("unit", "metric")  # Default to metric (Celsius)
        unit_symbol = "°C" if unit == "metric" else "°F"

        if cities:
            city_list = [city.strip().capitalize() for city in cities.split(",")]
            for city in city_list:
                if not city.isalpha():
                    weather_results.append({"city": city, "error": f"Invalid city name '{city}'. Only alphabets allowed."})
                    continue
                url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={unit}"
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()

                    # Calculate local time based on the city's timezone
                    timezone_offset = data["timezone"]  # Offset in seconds
                    utc_now = datetime.datetime.utcnow()
                    local_time = utc_now + datetime.timedelta(seconds=timezone_offset)
                    local_time_str = local_time.strftime("%Y-%m-%d %H:%M:%S")

                    sunrise = datetime.datetime.utcfromtimestamp(data["sys"]["sunrise"] + timezone_offset).strftime("%H:%M:%S")
                    sunset = datetime.datetime.utcfromtimestamp(data["sys"]["sunset"] + timezone_offset).strftime("%H:%M:%S")

                    weather_results.append({
                        "city": data["name"],
                        "temperature": data["main"]["temp"],
                        "description": data["weather"][0]["description"].capitalize(),
                        "humidity": data["main"]["humidity"],
                        "pressure": data["main"]["pressure"],
                        "wind_speed": data["wind"]["speed"],
                        "visibility": data["visibility"] / 1000,
                        "local_time": local_time_str,
                        "sunrise": sunrise,
                        "sunset": sunset,
                        "icon": f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png",
                    })
                else:
                    weather_results.append({"city": city, "error": f"City '{city}' not found. Please try again."})
        else:
            error_message = "Please enter at least one city name."

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Weather Bot</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
            body {{
                font-family: 'Poppins', Arial, sans-serif;
                background: linear-gradient(120deg, #f7d1ba, #f8e7db); /* Soft single gradient */
                color: #333;
                text-align: center;
                margin: 0;
                padding: 0;
            }}
            header {{
                background: #f08080; /* Coral header for warmth */
                color: white;
                padding: 20px;
                font-size: 2rem;
                font-weight: bold;
                text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.3);
                border-bottom: 3px solid #eea47f;
            }}
            form {{
                margin: 20px auto;
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            input, select {{
                padding: 10px;
                margin: 10px;
                border-radius: 8px;
                border: 1px solid #ddd;
                width: 300px;
                font-size: 1rem;
            }}
            button {{
                background: #eea47f; /* Orange for button */
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 1rem;
                cursor: pointer;
            }}
            button:hover {{
                background: #d98a6a; /* Slightly darker orange on hover */
            }}
            .weather-info {{
                margin: 20px auto;
                padding: 20px;
                border-radius: 15px;
                width: 400px;
                text-align: left;
                background: linear-gradient(135deg, #ffe5d9, #fad4c0); /* Light pastel gradient */
                border: 1px solid #ddd;
                box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2);
            }}
            .weather-info h2 {{
                text-align: center;
                color: #f08080; /* Match header coral */
            }}
            .error {{
                background: #f8d7da;
                color: #721c24;
                margin: 20px auto;
                padding: 10px;
                border-radius: 5px;
                width: fit-content;
                text-align: left;
                border: 1px solid #f5c6cb;
            }}
        </style>
    </head>
    <body>
        <header>Welcome to the Weather Bot</header>
        <form method="POST">
            <input type="text" name="cities" placeholder="Enter cities (e.g., London, Paris)">
            <select name="unit">
                <option value="metric">Celsius</option>
                <option value="imperial">Fahrenheit</option>
            </select>
            <button type="submit">Get Weather</button>
        </form>
        {''.join([
            f'''
            <div class="weather-info">
                <h2>Weather in {result['city']}</h2>
                <img src="{result['icon']}" alt="Weather Icon" style="display: block; margin: 0 auto;">
                <p><strong>Temperature:</strong> {result['temperature']}{unit_symbol}</p>
                <p><strong>Description:</strong> {result['description']}</p>
                <p><strong>Local Time:</strong> {result['local_time']}</p>
                <p><strong>Humidity:</strong> {result['humidity']}%</p>
                <p><strong>Pressure:</strong> {result['pressure']} hPa</p>
                <p><strong>Wind Speed:</strong> {result['wind_speed']} m/s</p>
                <p><strong>Visibility:</strong> {result['visibility']} km</p>
                <p><strong>Sunrise:</strong> {result['sunrise']}</p>
                <p><strong>Sunset:</strong> {result['sunset']}</p>
            </div>
            ''' if 'error' not in result else f'''
            <div class="error">{result['error']}</div>
            '''
            for result in weather_results
        ]) if weather_results else ""}
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True)