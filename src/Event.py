from Utils import *
class Meeting(object):
    def __init__(self, name, date, start, end, participants):
        self.name = name
        self.date = date
        self.start = start
        self.end = end
        self.participants = participants


    def is_conflict(self, new_meeting,site_id):
        if self.date != new_meeting.date:
            return False
        if not site_id in self.participants or not site_id in new_meeting.participants:
            return False
        time_list = []
        time_list.append(parse_time(self.start))
        time_list.append(parse_time(self.end))
        time_list.append(parse_time(new_meeting.start))
        time_list.append(parse_time(new_meeting.end))
        time_list.sort()
        if time_list[1] == parse_time(new_meeting.start) or \
            time_list[1] == parse_time(self.start):
            if time_list[1] == time_list[2]:
                return False
            return True
        return False

    # 重定义小于比较
    def __lt__(self, other):
        return self.date < other.date \
            or (self.date == other.date and self.start < other.start) \
            or (self.date == other.date and self.start == other.start \
                and self.name < other.name)
  
  # 重定义等于比较
    def __eq__(self, other):
        return self.date == other.date and self.start == other.start \
                and self.name == other.name


class Event(object):
    def __init__(self, operating_type, current_meeting, site_timestamp, site_id):
        self.operating_type = operating_type
        self.meeting = current_meeting
        self.site_timestamp = site_timestamp
        self.site_id = site_id

        