import requests
import json
import ipaddress
from flask import request


class Location:
    def __init__(self, lat, lon):
        self.__lat = lat
        self.__lon = lon

    def get_lat(self):
        return self.__lat

    def get_lon(self):
        return self.__lon

    def set_lat(self, lat):
        self.__lat = lat


def get_json_from_api(url):
    r = requests.get(url)  # get json from url
    if r.status_code == 200:
        j = json.loads(r.text)
    else:
        j = None
    return j


def get_ip():
    if ipaddress.ip_address(request.remote_addr):  # if testing locally
        j = get_json_from_api("https://api.ipify.org?format=json")
        if j:
            return j["ip"]
        else:
            return "8.8.8.8"
    else:
        reqIp = request.remote_addr  # get ip address from request
    return reqIp


def get_location():
    ip = get_ip()
    # url to get location from ip
    url = 'https://api.ip2loc.com/qUk2hHrOjfg40QdmmB8wtOfeHENmMTN2/{}?include=location_latitude,location_longitude'.format(
        ip)
    j = get_json_from_api(url)  # get location from ip
    if j:
        return (j["location_latitude"], j["location_longitude"])
    else:
        return (0, 0)


def get_weather(lat, lon):
    # url to get weather from lat and lon
    url = 'https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid=b21a2633ddaac750a77524f91fe104e7&lang=pl&units=metric'.format(
        lat, lon)
    j = get_json_from_api(url)  # get weather from lat and lon
    if j:
        return (j["name"], j["weather"][0]["icon"], int(j["main"]["temp"]), str(j["weather"][0]["description"]).capitalize())
    else:
        return ("Brak", "04d", 0, "Brak")


def get_random_quote():
    url = 'https://zenquotes.io/api/random'  # url to get random quote
    print(url)
    j = get_json_from_api(url)  # get random quote
    print(j)
    if j:
        return (j[0]["q"], j[0]["a"])
    else:
        return ("Bez Internetu nie mamy Internetu", "ja")
