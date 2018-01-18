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
    def sunrise(self):
        current_datetime = datetime.now(tz=pytz.utc)
        sun = self.city.sun(date=current_datetime.date(),local=False)
        return sun['sunrise']
    def dusk(self):
        current_datetime = datetime.now(tz=pytz.utc)
        sun = self.city.sun(date=current_datetime.date(),local=False)
        return sun['dusk']
    def is_night(self):
        current_datetime = datetime.now(tz=pytz.utc)
        sun = self.city.sun(date=current_datetime.date(),local=False)
        sunrise = sun['sunrise']
        dusk = sun['dusk']
        if current_datetime < sunrise or current_datetime > dusk:
            return True
        else:
            return False


