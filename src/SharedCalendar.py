import pickle
from Event import *

# recover after site broken, get information from 3 TXT file
def recover(my_store):
    original_data = {}
    with open('log.txt', 'rb') as file1:
        original_data["log"] =  pickle.load(file1)
    with open('dictionary.txt', 'rb') as file2:
        original_data["dictionary"] =  pickle.load(file2)
    with open('timetable.txt', 'rb') as file3:
        original_data["timetable"] =  pickle.load(file3)
    if len(original_data) > 0:
        my_store.import_data(original_data)

class SharedCalendar(object):

    def __init__(self, sites, site_id):
        self.dictionary = []
        self.log = []
        self.allsites = sites
        num_of_site = len(sites)
        self.time_table = [[0] * num_of_site for _ in range(num_of_site)]
        self.site_id_to_index = {site_id:site_info["index"]  for site_id, site_info in sites.items()}
        self.site_timestamp = 0
        self.site_id = site_id
    #if insert successfully, return True, else return False
    def insert(self, information_from_order):
        meeting_name = information_from_order[0]
        if self.find_meeting_in_dictionary(meeting_name):
            print("Can't schedule! Has same name!")
            return False


        day = information_from_order[1]
        start_time =information_from_order[2]
        end_time = information_from_order[3]
 
        participants = information_from_order[4].strip().split(",")
        participants.sort()

        current_meeting = Meeting(meeting_name, day, start_time, end_time, participants)
        for meeting in self.dictionary:
            if meeting.is_conflict(current_meeting,self.site_id):
                print("Unable to schedule meeting ", meeting_name)
                return False
        self.dictionary.append(current_meeting)
        self.site_timestamp += 1
        current_event = Event("create", current_meeting,self.site_timestamp,self.site_id)
        self.log.append(current_event)
        self.time_table[self.site_id_to_index[self.site_id]][self.site_id_to_index[self.site_id]] = self.site_timestamp
        self.record()
        print("Meeting ",meeting_name," scheduled.")
        return True


    #if delete successfully, return True, else return False
    def delete(self, information_from_order):
        meeting_name = information_from_order[0]
        target_meeting = self.find_meeting_in_dictionary(meeting_name)
        if target_meeting is None:
            return False
        if self.site_id not in target_meeting.participants:
            return False
        self.site_timestamp += 1
        current_event = Event("cancel", target_meeting,self.site_timestamp,self.site_id)
        self.log.append(current_event)
        self.dictionary.remove(target_meeting)
        self.time_table[self.site_id_to_index[self.site_id]][self.site_id_to_index[self.site_id]] = self.site_timestamp
        self.record()
        print("Meeting ",meeting_name," cancelled.")
        return True
        
        
    def update(self, info_got,other_node_name):
        records = info_got[0]
        other_timetable = info_got[1]
        NE = []
        for record in records:
            if not self.hasRec(record, self.site_id):
                NE.append(record)
        sides_involved_in_canceled_meetings = []
        # print("**********Record***********")
        # for event in records:
        #     print(event.operating_type +" "+ event.meeting.name +" "+event.meeting.start + " "+event.meeting.end +" "+ ",".join(event.meeting.participants)+" ", event.site_id, event.site_timestamp)
        # print("***********************")
        for index in range(len(other_timetable)):
            self.time_table[self.site_id_to_index[self.site_id]][index] = max(self.time_table[self.site_id_to_index[self.site_id]][index], other_timetable[self.site_id_to_index[other_node_name]][index])

        for index1 in range(len(other_timetable)):
            for index2 in range(len(other_timetable)):
                self.time_table[index1][index2] = max(self.time_table[index1][index2], other_timetable[index1][index2])
        for record in NE:
            self.log.append(record)
            if record.operating_type == "cancel":
                for meeting in self.dictionary:
                    if record.meeting == meeting:
                        self.dictionary.remove(record.meeting)
                        break
            elif record.operating_type == "create":
                is_delete = False
                for record2 in NE:
                    if record2.operating_type == "cancel" and record2.meeting == record.meeting:
                        is_delete = True
                if is_delete:
                    continue
                conflicts_meeting = []
                for meeting in self.dictionary:
                    if meeting.is_conflict(record.meeting,self.site_id):
                        flag = True
                        for record2 in NE:
                            if record2.operating_type == "cancel" and record2.meeting == meeting:
                                flag = False
                        if flag:
                            conflicts_meeting.append(meeting)
                conflicts_meeting.append(record.meeting)
                conflicts_meeting.sort()
                if len(conflicts_meeting) == 1:
                    self.dictionary.append(record.meeting)
                elif len(conflicts_meeting) > 2 or conflicts_meeting[1] == record.meeting:
                    if self.site_id not in record.meeting.participants:
                        print("Cannot cancel the meeting",record.meeting.name , ", I do not participant it!")
                        continue
                    self.site_timestamp += 1
                    current_event = Event("cancel", record.meeting,self.site_timestamp,self.site_id)
                    self.log.append(current_event)
                    self.time_table[self.site_id_to_index[self.site_id]][self.site_id_to_index[self.site_id]] = self.site_timestamp
                    sides_involved_in_canceled_meetings.extend(record.meeting.participants)
                    print("Meeting ",record.meeting.name," cancelled.")
                else:
                    if self.site_id not in conflicts_meeting[1].participants:
                        print("Cannot cancel the meeting",conflicts_meeting[1].name , ", I do not participant it!")
                        continue
                    self.site_timestamp += 1
                    current_event = Event("cancel", conflicts_meeting[1],self.site_timestamp,self.site_id)
                    self.log.append(current_event)
                    self.time_table[self.site_id_to_index[self.site_id]][self.site_id_to_index[self.site_id]] = self.site_timestamp
                    self.dictionary.remove(conflicts_meeting[1])
                    self.dictionary.append(record.meeting)
                    sides_involved_in_canceled_meetings.extend(conflicts_meeting[1].participants)
                    print("Meeting ",conflicts_meeting[1].name," cancelled.")
        self.dictionary.sort()

        #Truncate logs and reduce message sizes
        new_log = []
        for event in self.log:
            flag = False
            for current_site in self.allsites:
                if not self.hasRec(event, current_site):
                    flag = True
                    break
            if flag:
                new_log.append(event)
        self.log = new_log

        self.record()
        return list(set(sides_involved_in_canceled_meetings))



    def hasRec(self, the_event, target_site_id):
        site_where_event_happend = the_event.site_id
        index_of_event_site = self.site_id_to_index[site_where_event_happend]
        index_of_target_site = self.site_id_to_index[target_site_id]
        return self.time_table[index_of_target_site][index_of_event_site] >= the_event.site_timestamp

    def print_view(self):
        self.print_view_helper(self.dictionary)
        

    def print_myview(self):
        target_meetings = []
        for meeting in self.dictionary:
            if self.site_id in meeting.participants:
                target_meetings.append(meeting)
        self.print_view_helper(target_meetings)

    #order by day, start, name
    def print_view_helper(self, meetings):
        sorted_meetings = sorted(meetings)
        for meeting in sorted_meetings:
            print(meeting.name +" "+ meeting.date +" "+meeting.start + " "+meeting.end +" "+ ",".join(meeting.participants))

    def print_log(self):
        for event in self.log:
            if event.operating_type == "create":
                print(event.operating_type +" "+ event.meeting.name +" "+event.meeting.start +" "+ event.meeting.date +" "+event.meeting.start + " "+event.meeting.end +" "+ ",".join(event.meeting.participants))
            else:
                print(event.operating_type +" "+ event.meeting.name)

    def print_time(self):
        print(self.time_table)
        print(self.site_timestamp)

    def get_info_to_send(self, target_site_id):
        info_to_send = []
        for record in self.log:
            if not self.hasRec(record, target_site_id):
                info_to_send.append(record)
        return [info_to_send, self.time_table]
        

    def sites_involved_in_meeting(self,current_meeting_name):
        target_meeting = None
        for meeting in self.dictionary:
            if current_meeting_name == meeting.name:
                target_meeting = meeting
        if not target_meeting:
            return []
        return target_meeting.participants

    def import_data(self, original_data):
        self.dictionary = original_data["dictionary"]
        self.time_table = original_data["timetable"]
        self.log = original_data["log"]
        self.site_timestamp = self.time_table[self.site_id_to_index[self.site_id]][self.site_id_to_index[self.site_id]]

    #If exist return meeting, if not return None
    def find_meeting_in_dictionary(self, current_meeting_name):
        for meeting in self.dictionary:
            if current_meeting_name == meeting.name:
                return meeting
        return None


    def record(self):
        with open('log.txt', 'wb') as file1:
            pickle.dump(self.log,file1)
        with open('dictionary.txt', 'wb') as file2:
            pickle.dump(self.dictionary,file2)
        with open('timetable.txt', 'wb') as file3:
            pickle.dump(self.time_table,file3)