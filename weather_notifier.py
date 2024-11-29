
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
from datetime import datetime

API_KEY = ''  
EMAIL_ADDRESS = ''
  
EMAIL_PASSWORD = ''  
RECIPIENT_EMAIL = ''  

def fetch_weather(api_key, location):
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    response = requests.get(base_url)
    return response.json()

def compose_email(weather_data, location):
    weather = weather_data['weather'][0]['main']
    temp = weather_data['main']['temp']
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data['wind']['speed']
    advice = "Have a great day."

    message = f"""Here's today's weather Report in {location}:
    Weather: {weather}
    Temperature: {temp}°C
    Humidity: {humidity}%
    Wind Speed: {wind_speed} m/s

    {advice}
    """
    
    return message

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  
            server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())  
        print("Weather update sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_weather_update():
    global LOCATION  
    weather_data = fetch_weather(API_KEY, LOCATION)
    if weather_data.get("cod") != 200:  
        print(f"Failed to fetch weather data for {LOCATION}: {weather_data.get('message', 'Unknown error')}")
        return
    email_body = compose_email(weather_data, LOCATION)
    send_email("Today's Weather Alert", email_body)

def convert_to_24_hour_format(time_str):
    return datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M")

if __name__ == "__main__":
    try:
        LOCATION = input("Enter your location (e.g., 'Chennai'): ")
        weather_data = fetch_weather(API_KEY, LOCATION)
        if weather_data.get("cod") != 200: 
            print(f"Invalid location '{LOCATION}'. Please enter a valid location.")
            exit()

        user_time = input("Enter the time for the weather update (e.g., '07:00 AM' or '06:00 PM'): ")
        SCHEDULED_TIME = convert_to_24_hour_format(user_time)
        print(f"Weather update notifier scheduled daily at {user_time} ({SCHEDULED_TIME} in 24-hour format) for {LOCATION}.")

        schedule.every().day.at(SCHEDULED_TIME).do(send_weather_update)

        while True:
            schedule.run_pending()
            time.sleep(1)  
    except ValueError:
        print("Invalid input. Please check your location or time format and try again.")

