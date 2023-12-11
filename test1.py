import datetime 

def roundTimeToTimestamp(dt=None, roundTo=60):
   """Round a datetime object to any time lapse in seconds and return Unix timestamp
   dt : datetime.datetime object, default now.
   roundTo : Closest number of seconds to round to, default 1 minute.
   """
   if dt == None: 
       dt = datetime.datetime.now()
   seconds = (dt.replace(tzinfo=None) - dt.min).seconds
   rounding = (seconds + roundTo / 2) // roundTo * roundTo
   rounded_dt = dt + datetime.timedelta(0, rounding - seconds, -dt.microsecond)
   return rounded_dt.timestamp()

# Sample with the current time rounded to the nearest minute and converted to Unix timestamp:
print(int(roundTimeToTimestamp()))
