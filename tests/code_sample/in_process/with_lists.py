import uuid


def calculate_expected_time(rate, product_quantity):
    hours = product_quantity[1]/rate[0]
    return {'id': uuid.uuid4().hex, 'days': 0, 'hours': hours}


def calculate_expected_time_with_list(rate, product_quantity):
    hours = product_quantity[1]/rate[0]
    return hours * 24
