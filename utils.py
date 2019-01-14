# -*- coding: utf-8 -*-
import json

from messages import no_results_message, too_many_results_message


def validate_request(query):
    """
    Check that request query is ok.
    """
    query_length = len(query.split())
    if query_length <= 3 and query_length >= 1:
        return True
    return False


def parse_search_answer(data, request_name):
    """
    Method check returned data from request.
    Return is amount of answers _, result _.
    """
    if isinstance(data, bytes):
        data = data.decode('utf8').replace("'", '"')
        data = json.loads(data)

    if isinstance(data, list):
        return 0, "Неверный формат запроса."
    elif isinstance(data, dict):
        count = data['count']
        if count == 0:
            return count, no_results_message % request_name
        elif count == 1:
            result = data['results'][0]['id']
            return count, result
        elif count <= 25:
            result = [{'text': get_office_position(person), 'id': person.get(
                'id')} for person in data['results']]
            return count, result
        else:
            return count, too_many_results_message % request_name
    else:
        return 0, "Что-то пошло не так."


def get_office_position(person):
    information = person.get('sections', [])
    if information:
        last_information = information[0]
        return "%s / %s" % (last_information.get('position'), last_information.get('office'))
    return None


def get_templated_string(field_name, obj, template):
    if field_name == 'Транспортные средства':
        if template == '%s':
            return template % (obj['type']['name'])
        else:
            name = obj.get('brand').get('name') if obj.get(
                'brand') else obj.get('type').get('name')
            return template % (obj.get('type', {}).get('name'), obj.get('brand_name'), name)
    elif field_name == 'Недвижимое имущество':
        return template % (obj['type']['name'], obj['square'], obj.get('own_type', {}).get('name', ''))
    elif field_name == 'Доход':
        return template % (obj['size'], obj['comment'])
    return


def create_part_of_answer(field_name, data, template):
    from network import make_request_for_car
    result = "\n*%s*\n" % field_name
    for obj in data:
        if field_name == 'Транспортные средства':
            field_dict = obj.get('brand') or obj.get('type')
            if field_dict:
                name = make_request_for_car(field_dict.get('id'))
                if name:
                    obj['brand_name'] = name
                    template = "%s %s %s"
        if obj['relative'] is None:
            result += "%s\n" % get_templated_string(
                field_name, obj, template)
        else:
            result += "%s: %s\n" % (obj['relative']['name'],
                                    get_templated_string(field_name, obj, template))
    return result


def parse_person_answer(data):
    # if isinstance(data, bytes):
    #     data = data.decode('utf8').replace("'", '"')
    #     data = json.loads(data)

    all_years = data['results']
    result = []
    if all_years:
        # all_years = sorted(all_years, key=lambda last_year: last_year.get(
        #     'main', {}).get('year', 0), reverse=True)
        last_year = all_years[-1]
        year = last_year.get('main', {}).get('year', 0)
        name = last_year.get('main', {}).get('person', {}).get('name', None)
        result.append("%s\n%s\n" % (last_year['main']['office']
                                    ['post'], last_year['main']['office']['name']))

        incomes = last_year['incomes']
        if incomes:
            # maybe no comment
            result.append(create_part_of_answer(
                "Доход", incomes, "%s руб. (%s)").replace(' ()', ''))

        real_estates = last_year['real_estates']
        if real_estates:
            result.append(create_part_of_answer("Недвижимое имущество",
                                                real_estates, "%s, %s кв. м. (%s)").replace(' ()', ''))

        vehicles = last_year['vehicles']
        if vehicles:
            result.append(create_part_of_answer(
                "Транспортные средства", vehicles, "%s"))

        savings = last_year['savings']
        if savings:
            savings = "\n*Счета*\n"
            for saving in savings:
                savings += "%s\n" % saving
            result.append(savings)

        # spendings
        # stocks

    return result, name, year


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    return [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
