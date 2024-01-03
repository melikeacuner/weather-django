# views.py
import requests
import pytz
from django.shortcuts import render
from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import render
from itertools import groupby
from operator import itemgetter

def convert_utc_to_local(utc_datetime):
    local_timezone = pytz.timezone('Europe/Istanbul')
    local_datetime = utc_datetime.replace(tzinfo=pytz.utc).astimezone(local_timezone)
    return local_datetime

def convert_unix_timestamp_to_turkey_time(unix_timestamp):
    utc_time = datetime.utcfromtimestamp(unix_timestamp)
    turkey_time = utc_time + timedelta(hours=3)
    formatted_time = turkey_time.strftime('%H:%M')
    return formatted_time

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

def get_detailed_weather(city, forecast_days=6, first_day_only=False):
    api_key = '5dc22f5d5a37b0ee97c135fe954fb37f'
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&appid={api_key}&lang=tr'

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        detailed_weather_data = {
            'city': data['city']['name'],
            'forecast': []
        }

        today = datetime.now().date()
        end_date = today + timedelta(days=forecast_days)

        for item in data['list']:
            dt_txt = item['dt_txt']
            date_obj = datetime.strptime(dt_txt, '%Y-%m-%d %H:%M:%S').date()

            if today <= date_obj < end_date and dt_txt.split()[1] == '12:00:00':
                forecast_day = {
                    'date': date_obj.strftime('%d.%m.%Y'),
                    'temperature': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'pressure': item['main']['pressure'],
                    'visibility': item['visibility'],
                    'description': item['weather'][0]['description'],
                    'icon_url': f'http://openweathermap.org/img/w/{item["weather"][0]["icon"]}.png',
                    'feels_like': item['main']['feels_like'],
                    'wind_speed': item['wind']['speed'],
                    'wind_deg': item['wind']['deg'],
                    'sunset': convert_unix_timestamp_to_turkey_time(data['city']['sunset'])
                }

                detailed_weather_data['forecast'].append(forecast_day)

                if first_day_only:
                    break

        request_time = datetime.now().replace(second=0, microsecond=0)
        detailed_weather_data['request_time'] = request_time.strftime('%H:%M')

        return detailed_weather_data
    else:
        print(f"API isteği başarısız! HTTP Hatası: {response.status_code}")
        print(response.json()) 
        return None

def get_forecast(city):
    api_key = '5dc22f5d5a37b0ee97c135fe954fb37f'
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&appid={api_key}&lang=tr'

    response = requests.get(url)
    
    # Ek kontrol: API'den gelen cevabı kontrol et
    if response.status_code != 200:
        print(f"API isteği başarısız! HTTP Hatası: {response.status_code}")
        return None

    data = response.json()

    forecast_data = []

    today = datetime.now().date()
    end_date = today + timedelta(days=5)

    for item in data['list']:
        dt_txt = item['dt_txt']
        date_obj = datetime.strptime(dt_txt, '%Y-%m-%d %H:%M:%S').date()

        if today <= date_obj <= end_date and dt_txt.split()[1] == '12:00:00':
            forecast_day = {
                'date': date_obj.strftime('%d.%m.%Y'),
                'temperature': item['main']['temp'],
                'description': item['weather'][0]['description'],
                'icon_url': f'http://openweathermap.org/img/w/{item["weather"][0]["icon"]}.png'
            }
            forecast_data.append(forecast_day)

    return forecast_data

def get_4_day_hourly_forecast(city, forecast_days):
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

        if forecast_days == 1 and request_date == forecast_date and dt.minute == 0:
            forecast_hour = {
                'date': dt.strftime('%d.%m.%Y'),
                'time': dt.strftime('%H:%M'),
                'temperature': item['main']['temp'],
                'description': item['weather'][0]['description'],
                'icon_url': f'http://openweathermap.org/img/w/{item["weather"][0]["icon"]}.png'
            }
            hourly_forecast_data.append(forecast_hour)

        elif forecast_days == 4 and request_date <= forecast_date <= request_date + timedelta(days=4) and dt.minute == 0:
            forecast_hour = {
                'date': dt.strftime('%d.%m.%Y'),
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
        request.session['city'] = city 
        data = get_detailed_weather(city)
        forecast_data = get_forecast(city)
        
        return render(request, 'main.html', {'data': data, 'forecast_data': forecast_data , 'city': city})

    cities = ['Istanbul', 'Ankara', 'Izmir', 'Bursa', 'Adana', 'Gaziantep', 'Konya', 'Antalya', 'Mersin', 'Kayseri']
    weather_data = []

    for city in cities:
        data = get_basic_weather(city)
        weather_data.append(data)

    return render(request, 'index.html', {'weather_data': weather_data})

def main(request):
    city = None

    if request.method == 'POST':
        city = request.POST.get('city')
        if city:
            request.session['city'] = city 

    city = request.session.get('city')

    if city:
        data = get_detailed_weather(city, first_day_only=True)
        forecast_data = get_forecast(city)
        hourly_forecast_data = get_4_day_hourly_forecast(city, forecast_days=1) 

        return render(request, 'main.html', {'data': data, 'forecast_data': forecast_data, 'hourly_forecast_data': hourly_forecast_data, 'city': city})

    return render(request, 'main.html', {'city': city})

def hourly_view(request):
    city = request.session.get('city') 
    forecast_days = 4 
    hourly_forecast_data = get_4_day_hourly_forecast(city, forecast_days)

    # Saatlik verileri tarihe göre grupla
    hourly_forecast_data.sort(key=lambda x: datetime.strptime(x['date'], '%d.%m.%Y'))
    grouped_hourly_data = {date: list(group) for date, group in groupby(hourly_forecast_data, key=itemgetter('date'))}

    context = {'grouped_hourly_data': grouped_hourly_data,
               'city': city}
    return render(request, 'hourly.html', context)

def daily(request):
    city = request.session.get('city') 
    detailed_weather_data = None

    detailed_weather_data = get_detailed_weather(city, forecast_days=6, first_day_only=False)

    return render(request, 'daily.html', {'detailed_weather_data': detailed_weather_data, 'city': city})

