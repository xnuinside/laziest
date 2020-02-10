import uuid


def calculate_expected_time(rate, product_quantity):
    hours = product_quantity['value']/rate['value']
    return {'id': uuid.uuid4().hex, 'days': 0, 'hours': hours}


async def calculateExpectedMaintanceTime(vehichle, station):
    return {'id': uuid.uuid4().hex, 'hours': 12}
