import datetime
import time
from astral import Astral

city_name = 'Baltimore'
a = Astral()
a.solar_depression = 'civil'
city = a[city_name]

def dawn():
    sun = city.sun(date=datetime.date.today(),local=True)
    return int(utc_mktime(sun['dawn'].timetuple()))

def dusk():
    sun = city.sun(date=datetime.date.today(),local=True)
    return int(utc_mktime(sun['dusk'].timetuple()))

def is_night():
    now = time.time()
    next_dawn = dawn()
    next_dusk = dusk()
    if now < next_dawn or now > next_dusk:
        return True
    else:
        return False

def utc_mktime(utc_tuple):
    if len(utc_tuple) == 6:
        utc_tuple += (0, 0, 0)
    return time.mktime(utc_tuple) - time.mktime((1970, 1, 1, 0, 0, 0, 0, 0, 0))

def datetime_to_timestamp(dt):
    return int(utc_mktime(dt.timetuple()))


