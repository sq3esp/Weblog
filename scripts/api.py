import requests
import json
import ipaddress
from flask import request

def get_json_from_api(url):  # get json from api
    r = requests.get(url)  # get json from url
    if r.status_code == 200:  # if status code is 200 (OK)
        j = json.loads(r.text)  # load json
    else:
        j = None  # if status code is not 200 (OK) return None
    return j


def get_ip():  # get ip from request (used for location)
    if ipaddress.ip_address(request.remote_addr):  # if testing locally
        j = get_json_from_api(
            "https://api.ipify.org?format=json")  # get ip from api
        if j:
            return j["ip"]  # return ip
        else:
            return "8.8.8.8"  # if api is not working return ip of google
    else:
        reqIp = request.remote_addr  # get ip address from request
    return reqIp


def get_location():  # get location from ip
    ip = get_ip()  # get ip from request
    url = 'https://api.ip2loc.com/qUk2hHrOjfg40QdmmB8wtOfeHENmMTN2/{}?include=location_latitude,location_longitude'.format(
        ip)  # url to get location from ip
    j = get_json_from_api(url)  # get location from ip
    if j:  # if location is found
        # return location
        return (j["location_latitude"], j["location_longitude"])
    else:
        return (0, 0)  # if location is not found return 0,0 coordinates


def get_weather(lat, lon):  # get weather from lat and lon
    url = 'https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid=b21a2633ddaac750a77524f91fe104e7&lang=pl&units=metric'.format(
        lat, lon)  # url to get weather from lat and lon
    j = get_json_from_api(url)  # get weather from lat and lon
    if j:  # if weather is found
        # return weather
        return (j["name"], j["weather"][0]["icon"], int(j["main"]["temp"]), str(j["weather"][0]["description"]).capitalize())
    else:
        # if weather is not found return "Brak"
        return ("Brak", "04d", 0, "Brak")


def get_random_quote():  # get random quote
    url = 'https://zenquotes.io/api/random'  # url to get random quote
    j = get_json_from_api(url)  # get random quote
    if j:
        return (j[0]["q"], j[0]["a"])  # return quote and author
    else:
        # if quote is not found return "Bez Internetu nie mamy Internetu" because it is a quote from the internet
        return ("Bez Internetu nie mamy Internetu", "ja")


class Location:
    def __init__(self, lat=None, lon=None):
        if lat is None and lon is None:
            location = get_location()
            self.__lat = location[0]
            self.__lon = location[1]
        else:
            self.__lat = lat
            self.__lon = lon

    @property
    def lat(self):  # getter for the latitude
        return self.__lat

    @property
    def lon(self):  # getter for the longitude
        return self.__lon

    @lat.setter
    def lat(self, lat):  # setter for the latitude
        self.__lat = lat

    @lon.setter
    def lon(self, lon):  # setter for the longitude
        self.__lon = lon


print(Location)

class Weather:  # class for the weather
    def __init__(self, city = None, icon = None, temperature = None, description = None):
        if city is None and icon is None and temperature is None and description is None:
            location = get_location()
            weather = get_weather(location[0], location[1])
            self.__city = weather[0]
            self.__icon = weather[1]
            self.__temperature = weather[2]
            self.__description = weather[3]
        else:
            self.__city = city
            self.__icon = icon
            self.__temperature = temperature
            self.__description = description

    @property
    def city(self):  # getter for the city
        return self.__city

    @property
    def icon(self):
        return self.__icon

    @property
    def temperature(self):
        return self.__temperature

    @property
    def description(self):
        return self.__description

    @city.setter
    def city(self, city):  # setter for the city
        self.__city = city

    @icon.setter
    def icon(self, icon):  # setter for the icon
        self.__icon = icon

    @temperature.setter
    def temperature(self, temperature):  # setter for the temperature
        self.__temperature = temperature

    @description.setter
    def description(self, description):  # setter for the description
        self.__description = description



class Api:  # class for the api
    def __init__(self, location = None, weather = None, quote = None):
        if location is None and weather is None and quote is None:
            self.__location = Location()
            self.__weather = Weather()
            randomQuote =  get_random_quote()
            self.__quote = randomQuote[0]
            self.__author = randomQuote[1]
        else:
            self.__location = location
            self.__weather = weather
            self.__quote = quote

    @property
    def lat(self):  # getter for the latitude
        return self.__location.lat

    @property
    def lon(self):  # getter for the longitude
        return self.__location.lon

    @property
    def city(self):  # getter for the city
        return self.__weather.city

    @property
    def icon(self):  # getter for the icon
        return self.__weather.icon

    @property
    def temperature(self):  # getter for the temperature
        return self.__weather.temperature

    @property
    def description(self):  # getter for the description
        return self.__weather.description

    @property
    def quote(self):  # getter for the quote
        return self.__quote

    @property
    def author(self):  # getter for the author
        return self.__author




