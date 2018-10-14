#TODO run.sh & build.sh

from socket import *
import threading
import os
from SharedCalendar import *
from Event import *
import pickle
import sys

def send_msg_to_participants(my_store, participants, this_site_id, sock, nodes):
    for participant in participants:
        if participant == this_site_id:
            continue
        # print("Need to send:",participant)
        msg = my_store.get_info_to_send(participant)
        msg = pickle.dumps(msg)
        sock.sendto(msg,(nodes[participant]["ip"],nodes[participant]["port"]))

#Listen to other sites in child thread
def listen_to_other_sites(sock, nodes, this_site_id):
    while True:
        data, address = sock.recvfrom(4096)
        # print("received info from address!",address)
        data = pickle.loads(data)
        for node_name in nodes:
            if nodes[node_name]["ip"] == address[0]:
                address = node_name
        participants = my_store.update(data,address)
        if len(participants) <= 1:
            continue
        send_msg_to_participants(my_store, participants, this_site_id, sock, nodes)


#get all sites information from knownhosts_udp.txt
nodes = {}
with open('knownhosts_udp.txt', 'r') as udp_sites_file:
    all_sites_data = udp_sites_file.readlines() 
    for index, line in enumerate(all_sites_data):
        current_site = {}
        host_name_and_port  = line.strip().split(" ")
        current_site["port"] = int(host_name_and_port[1])
        current_site["ip"] = gethostbyname(host_name_and_port[0])
        current_site["index"] = index
        nodes[host_name_and_port[0]] = current_site

#get ID of this site
this_site_id = sys.argv[1]


#create store of this site, class SharedCalendar is in SharedCalendar.py
my_store = SharedCalendar(nodes, this_site_id)
# if file is existed, recover this site
if os.path.exists("log.txt")\
     and os.path.exists('dictionary.txt')\
      and os.path.exists('timetable.txt'):
    recover(my_store)


# Create a UDP socket
sock = socket(AF_INET, SOCK_DGRAM)

# Bind the socket to the port
server_address = (nodes[this_site_id]["ip"], nodes[this_site_id]["port"])
sock.bind(server_address)






    
#create a child thread to listen to message from other sites
listening_thread = threading.Thread(target=listen_to_other_sites, args =(sock,nodes,this_site_id))
listening_thread.start()



#Say your order!
while True:
    #print("What do you want to do, ",this_site_id," ?")
    get_order = input("")
    information_from_order = get_order.strip().split(" ")
    if information_from_order[0] == "schedule":
        if not my_store.insert(information_from_order[1:]):
            continue
        participants = my_store.sites_involved_in_meeting(information_from_order[1])
        if len(participants) <= 1:
            # print("Only one participants:",participants)
            continue
        send_msg_to_participants(my_store, participants, this_site_id, sock, nodes)

    elif information_from_order[0] == "cancel":
        participants = my_store.sites_involved_in_meeting(information_from_order[1])
        if len(participants) == 0:
            print("Can't cancel! Not found in dictionary")
            continue        
        if not my_store.delete(information_from_order[1:]):
            print("Cannot cancel! this site not involved the meeting!")
            continue
        if len(participants) == 1:
            continue
        send_msg_to_participants(my_store, participants, this_site_id, sock, nodes)
    elif information_from_order[0] == "view":
        my_store.print_view()
    elif information_from_order[0] == "myview":
        my_store.print_myview()
    elif information_from_order[0] == "log":
        my_store.print_log()
    elif information_from_order[0] == "time":
        my_store.print_time()
    else:
        print("WRONG ORDER! TRY AGAIN!")



