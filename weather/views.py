from django.shortcuts import render
import requests
import pytz
from django.shortcuts import render
from datetime import datetime, timedelta
from django.utils import timezone

def convert_utc_to_local(utc_datetime):
    local_timezone = pytz.timezone('Europe/Istanbul')
    local_datetime = utc_datetime.replace(tzinfo=pytz.utc).astimezone(local_timezone)
    return local_datetime

def get_basic_weather(city):
   api_key = '5dc22f5d5a37b0ee97c135fe954fb37f'
   url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}&lang=tr'

   response = requests.get(url)
   data = response.json()

   basic_weather_data = {
       'city': data['name'],
       'temperature': data['main']['temp'],
       'icon_url': f'http://openweathermap.org/img/w/{data["weather"][0]["icon"]}.png'
   }

   return basic_weather_data

def get_detailed_weather(city):
    api_key = '5dc22f5d5a37b0ee97c135fe954fb37f'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}&lang=tr'

    response = requests.get(url)
    data = response.json()

    detailed_weather_data = {
        'city': data['name'],
        'temperature': data['main']['temp'],
        'humidity': data['main']['humidity'],
        'pressure': data['main']['pressure'],
        'visibility': data['visibility'],
        'description': data['weather'][0]['description'],
        'icon_url': f'http://openweathermap.org/img/w/{data["weather"][0]["icon"]}.png',
        'feels_like': data['main']['feels_like'],
        'wind_speed': data['wind']['speed'],
        'wind_deg': data['wind']['deg'],
    }

    if 'sunset' in data['sys']:
        utc_sunset = datetime.utcfromtimestamp(data['sys']['sunset'])
        local_sunset = convert_utc_to_local(utc_sunset)
        detailed_weather_data['sunset'] = local_sunset.strftime('%H:%M')

    request_time = datetime.now().replace(second=0, microsecond=0)
    detailed_weather_data['request_time'] = request_time.strftime('%H:%M')

    return detailed_weather_data

def get_forecast(city):
    api_key = '5dc22f5d5a37b0ee97c135fe954fb37f'
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&appid={api_key}&lang=tr'

    response = requests.get(url)
    data = response.json()

    forecast_data = []

    today = datetime.now().date()
    end_date = today + timedelta(days=4) 

    for item in data['list']:
        dt_txt = item['dt_txt']
        date_obj = datetime.strptime(dt_txt, '%Y-%m-%d %H:%M:%S').date()

        if today <= date_obj <= end_date and item['dt_txt'].split()[1] == '12:00:00':
            forecast_day = {
                'date': date_obj,
                'temperature': item['main']['temp'],
                'description': item['weather'][0]['description'],
                'icon_url': f'http://openweathermap.org/img/w/{item["weather"][0]["icon"]}.png'
            }
            forecast_data.append(forecast_day)

    return forecast_data
    
def get_hourly_forecast_from_request_time(city):
    api_key = '5dc22f5d5a37b0ee97c135fe954fb37f'
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&appid={api_key}&lang=tr'

    response = requests.get(url)
    data = response.json()

    request_time = datetime.now().replace(second=0, microsecond=0)
    request_date = request_time.date()

    hourly_forecast_data = []

    for item in data['list']:
        dt = datetime.fromtimestamp(item['dt'])
        forecast_date = dt.date()

        if request_date == forecast_date and dt.minute == 0:
            forecast_hour = {
                'time': dt.strftime('%H:%M'),
                'temperature': item['main']['temp'],
                'description': item['weather'][0]['description'],
                'icon_url': f'http://openweathermap.org/img/w/{item["weather"][0]["icon"]}.png'
            }
            hourly_forecast_data.append(forecast_hour)

        if forecast_date == request_date + timedelta(days=1) and dt.hour == 0:
            forecast_hour = {
                'time': dt.strftime('%H:%M'),
                'temperature': item['main']['temp'],
                'description': item['weather'][0]['description'],
                'icon_url': f'http://openweathermap.org/img/w/{item["weather"][0]["icon"]}.png'
            }
            hourly_forecast_data.append(forecast_hour)

    return hourly_forecast_data

def index(request):
    if request.method == 'POST':
        city = request.POST.get('city')
        data = get_detailed_weather(city)
        forecast_data = get_forecast(city)
        
        return render(request, 'main.html', {'data': data, 'forecast_data': forecast_data})

    cities = ['Istanbul', 'Ankara', 'Izmir', 'Bursa', 'Adana', 'Gaziantep', 'Konya', 'Antalya', 'Mersin', 'Kayseri']
    weather_data = []

    for city in cities:
        data = get_basic_weather(city)
        weather_data.append(data)

    return render(request, 'index.html', {'weather_data': weather_data})

def main(request):
    if request.method == 'POST':
        city = request.POST.get('city')
        data = get_detailed_weather(city)
        forecast_data = get_forecast(city)
        hourly_forecast_data = get_hourly_forecast_from_request_time(city) 
       
        return render(request, 'main.html', {'data': data, 'forecast_data': forecast_data, 'hourly_forecast_data': hourly_forecast_data})

    return render(request, 'main.html')

