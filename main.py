from tempfile import tempdir
import reverse_geocoder as rg
import numpy as np  
from requests import get
import time

BASE = 'https://api.openweathermap.org/data/2.5/weather'
API_KEY = '00dbce25503eebf0535dd18a1dfb2ba7'
UNITS = 'metric'
LAT = 63.595
LON = 118.892

def random_coordinates():
    return (np.random.rand() * 180 - 90, np.random.rand() * 360 - 180)

def antipodal_point(point):
    # antipod_point = lambda x, y: -np.sign(x - np.finfo(float).eps)*abs(y - x)
    antipod_point = lambda x, y: -np.sign(x - np.finfo(float).eps)*((-abs(x))%y)
    lat = -point[0]
    lon = antipod_point(point[1], 180.0)
    #return list(map(lambda x: -np.sign(x - np.finfo(float).eps)*abs(180.0 - x), point))
    return (lat, lon)

def distance_between_coordinates(point1, point2):
    R = 6371e3
    lat1, lon1 = point1
    lat2, lon2 = point2

    x1 = lat1 * np.pi/180
    x2 = lat2 * np.pi/180
    d1 = (lat2-lat1) * np.pi/180
    d2 = (lon2-lon1) * np.pi/180

    a = np.sin(d1/2) * np.sin(d1/2) + np.cos(x1) * np.cos(x2) * np.sin(d2/2) * np.sin(d2/2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))

    return R*c

def temperature_on_coordinates(point):
    data_temp = get(f'{BASE}?lat={point[0]}&lon={point[1]}&units={UNITS}&appid={API_KEY}').json()
    return data_temp['main']['temp']

def next_point(point, val):
    diff1 = np.sign(np.random.rand()-.5) * np.random.rand()*val
    diff2 = np.sign(np.random.rand()-.5) * (val - abs(diff1))
    return (point[0] + diff1, point[1] + diff2)

def nearest_city(point):
    return rg.search(point)[0]

def find_Borsuk_Ulam(threshold = .1):
    point = random_coordinates()
    while True:
        anti_point = antipodal_point(point)
        temp_diff = abs(temperature_on_coordinates(point) - temperature_on_coordinates(anti_point))
        print(f'Temp diff = {temp_diff:.2f} \'C')
        if temp_diff < threshold:
            city = nearest_city(point)
            #city_point = (city['lat'], city['lon'])
            city_anti = nearest_city(anti_point)
            #city_anti_point = (city_anti['lat'], city_anti['lon'])
            city_distance = distance_between_coordinates(point, (float(city['lat']), float(city['lon'])))//10/100
            city_anti_distance = distance_between_coordinates(anti_point, (float(city_anti['lat']), float(city_anti['lon'])))//10/100
            print(f"Borsuk-Ulam found!\nPoint:           {point} - {city_distance}km from {city['name']}\n"
            f"Antipodal point: {anti_point} - {city_anti_distance}km from {city_anti['name']}\nTemperature: {temperature_on_coordinates(point)}")
            break
        point = next_point(point, temp_diff)
        point = (point[0] if abs(point[0]) < 90 else point[0] + -np.sign(point[0])*180,
                point[1] if abs(point[1]) < 180 else point[1] + -np.sign(point[1])*360)
        print(point, '\n')

if __name__ == '__main__':
    find_Borsuk_Ulam(.1)