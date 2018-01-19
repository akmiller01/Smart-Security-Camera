from datetime import datetime
import pytz
from astral import Astral

class LocalTime(object):
    def __init__(self,city_name):
        a = Astral()
        a.solar_depression = 'civil'
        self.city = a[city_name]
    def utcnow(self):
        return datetime.now(tz=pytz.utc)
    def now(self):
        return datetime.now(tz=self.city.tz)
    def dawn(self):
        current_datetime = datetime.now(tz=pytz.utc)
        sun = self.city.sun(date=current_datetime.date(),local=False)
        return sun['dawn']
    def dusk(self):
        current_datetime = datetime.now(tz=pytz.utc)
        sun = self.city.sun(date=current_datetime.date(),local=False)
        return sun['dusk']
    def is_night(self):
        current_datetime = datetime.now(tz=pytz.utc)
        sun = self.city.sun(date=current_datetime.date(),local=False)
        dawn = sun['dawn']
        dusk = sun['dusk']
        if current_datetime < dawn or current_datetime > dusk:
            return True
        else:
            return False
    def current_state(self):
        current_datetime = datetime.now(tz=pytz.utc)
        sun = self.city.sun(date=current_datetime.date(),local=False)
        dawn = sun['dawn']
        dusk = sun['dusk']
        if current_datetime < dawn or current_datetime > dusk:
            return "day"
        else:
            return "night"


