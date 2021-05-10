import socket
import sys
import threading
import time
from datetime import datetime

def connect(conn):
    user =False
    pass_ = False
    authenticated = False
    floods = {}
    while True:
        if authenticated == False:
            received = conn.recv(1024)
            if received == ' ':
                pass
            else:
                if "USER bilkentstu" in received.decode():
                    user = True
            
                if "PASS cs421s2021" in received.decode() and user:
                    #print("HELLLOOO")
                    pass_ = True
                    authenticated = True
                # print(received.decode())
                    conn.sendall(b'OK\r\n')
                    #print("Basarili")

                if user == False and pass_ == False:
                    conn.sendall(b'INVALID CRED\r\n')
                    print("refused")
            
        else:
            received = conn.recv(17)
            if received == ' ':
                pass
            else:
                msg = received.decode()
                if msg not in floods:
                    #floods += msg
                    floods[msg] = 1
                   
                    thread = threading.Thread(target=send_msg, args=([msg]))
                    thread.start()
                    #print("Thread msg is joined")
                    thread.join()
                   
                else:
                    floods[msg] += 1

                if len(floods) == 7 * nPeers:
                    print("flood is ")
                    print(floods)
                    print_table(floods)
                    exit(0)
        
        
           
                

def print_table(list_f):
    print("Printing table")
    print ("{:<14} {:<10} {:<10}".format('Source Node ID','Timestamp','# of messages received'))
    for key, value in list_f.items():
        rand = key.find(" ")
        flood_id = key[rand:rand + 1]
        timestamp = key[rand+1:rand + 11]
        print ("{:<14} {:<10} {:<10}".format(flood_id, timestamp, value))

def send_msg(msg):
    #print("Send message is here")
    global destinations
    for port in destinations:
        #print("Port is " + str(port))
        s_o = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s_o.connect((ADDRESS, port))
            #print("connected peers are " + str(s_o.getpeername()))
            s_out.sendall(msg.encode())
        except Exception as e:
            #print(e)
            pass

            
            
def handleClient(s, port_number):
    peer_id = port_number - 60000
    print("TCP connection established with peer " + str(peer_id))
    s.sendall(b'USER bilkentstu\r\n')
    s.sendall(b'PASS cs421s2021\r\n')
    timesup = False
    data  = s.recv(1024)
    if "OK" in data.decode():
        print("Authenticated to peer " + str(peer_id))
        while timesup == False:
            now = datetime.now()
            hour = now.strftime("%H:%M:%S")
            if hour[-2:] == "00":
                timesup = True
                counter = 0
                now = datetime.now()
                s.sendall(b'FLOD '+ str(PEER_ID).encode() + b' ' + now.strftime("%H:%M:%S").encode() + b'\r\n')
                counter +=1
                while counter < 7:
                    time.sleep(5)
                    now = datetime.now()
                    s.sendall(b'FLOD '+ str(PEER_ID).encode() + b' ' + now.strftime("%H:%M:%S").encode() + b'\r\n')
                    counter += 1
               
    else:
        s.shutdown(s.SHUT_RDWR)
        s.close()



arg = sys.argv
ADDRESS = arg[1]
PEER_ID = int(arg[2])
PORT_IN = 60000 + PEER_ID
USERNAME = "bilkentstu"
PASSWORD = "cs421s2021"

all_connected = False
topologyFile = open('topology.txt', 'r')
lines = topologyFile.readlines()
#print(lines)

# extract number of pairs of information
nPeers = int(lines[0][0])
#print(nPeers)
lines = lines[1:]
#print(lines)
destinations = []
sources = []

threads = []

for link in lines:
    client = int(link[0])
    host = int(link[3])
    if client == PEER_ID:
        destinations.append(host + 60000)
    elif host == PEER_ID:
        sources.append(client + 60000)

# tamam

s_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_in.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s_in.bind((ADDRESS, PORT_IN))
print('listening on', (ADDRESS, PORT_IN))

#print(PORT_IN)
s_in.listen()

while len(threads) < len(destinations):
    for port in destinations:
        s_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s_out.connect((ADDRESS, port))
            print(s_out.getpeername())
            thread1 = threading.Thread(target=handleClient, args=([s_out, port]))
            threads.append(thread1)
            thread1.start()
        except Exception as ex:
            # print(ex)
            pass

conn, addr = s_in.accept()
thread_conn = threading.Thread(target=connect, args=([conn]))
thread_conn.start()

for t in threads:
    print("joining threads")
    t.join()
thread_conn.join()