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
        parent_name = data['results'][0].get('parent_name', None)
        name_ru = data['results'][0].get('name_ru', None)
        name_en = data['results'][0].get('name_en', None)
        name = parent_name if parent_name else name_ru if name_ru else name_en
        return name
    else:
        return None
