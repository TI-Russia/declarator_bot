# -*- coding: utf-8 -*-
import requests
import json


from utils import parse_search_answer, parse_person_answer

BASE_URL = 'https://declarator.org/api/'


def make_request_for_search(query):
    method_url = 'v1/search/person-sections/?name=%s'
    response = requests.get(BASE_URL + method_url % query)
    if response.status_code == 200:
        data = response.content
        amount, result = parse_search_answer(data, query)
        if amount == 1:
            amount, data, name, year = make_request_for_person(result)
            return amount, data, name, year, result
        else:
            return amount, result, None, None, None
    elif response.status_code == 400:
        return 0, "Неверный формат запроса.", None, None, None


def make_request_for_person(person_id):
    method_url = 'v1/search/sections/?person=%d'
    response = requests.get(BASE_URL + method_url % person_id)
    if response.status_code == 200:
        data = response.content
        if isinstance(data, bytes):
            data = data.decode('utf8').replace("'", '"')
            data = json.loads(data)
        while data.get('next'):
            response = requests.get(data.get('next'))
            if response.status_code == 200:
                data = response.content
                if isinstance(data, bytes):
                    data = data.decode('utf8').replace("'", '"')
                    data = json.loads(data)
        result, name, year = parse_person_answer(data)
        return 1, result, name, year
    elif response.status_code == 400:
        return 0, "Неверный формат запроса.", None, None


def make_request_for_car(car_id):
    method_url = 'carbrand/?id=%d'
    response = requests.get(BASE_URL + method_url % car_id)
    if response.status_code == 200:
        data = response.content
        if isinstance(data, bytes):
            data = data.decode('utf8').replace("'", '"')
            data = json.loads(data)
        name = data['results'][0]['parent_name'] or data['results'][0]['name_en'] or data['results'][0]['name_ru']
        return name
    else:
        return None
