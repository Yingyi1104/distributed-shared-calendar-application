from datetime import *
def parse_time(time_string):
    #split hour, minutes, and merediem from string
    hour_minutes = time_string.split(":")
    hour = int(hour_minutes[0])
    minutes = int(hour_minutes[1])

    #return time object
    timeobj = time(hour, minutes)
    return timeobj


def parse_date(date_string):
    #split month, day, year from string
    date_string = date_string.split("/")
    month = int(date_string[0])
    day = int(date_string[1])
    year = int(date_string[2])
    
    dateobj = datetime.datetime(year, month, day)
    return dateobj