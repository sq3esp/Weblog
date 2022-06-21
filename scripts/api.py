import requests
import json
import ipaddress
from flask import request


class Location:  # class for the location
    def __init__(self, lat, lon):  # constructor for the class
        self.__lat = lat
        self.__lon = lon

    def get_lat(self):  # getter for the latitude
        return self.__lat

    def get_lon(self):  # getter for the longitude
        return self.__lon

    def set_lat(self, lat):  # setter for the latitude
        self.__lat = lat

    def set_lon(self, lon):  # setter for the longitude
        self.__lon = lon


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
