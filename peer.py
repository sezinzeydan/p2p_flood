import socket
import sys
import threading
import time

def connect(conn):
    user =False
    pass_ = False
    authenticated = False
    while True:
        received = conn.recv(1024)
        if received == ' ':
            pass
        else:
            print(received.decode())
            #time.sleep(3)
            if authenticated == False:
                if "USER bilkentstu" in received.decode():
                    user = True
            
                if "PASS cs421s2021" in received.decode() and user:
                    print("HELLLOOO")
                    pass_ = True
                    authenticated = True
                # print(received.decode())
                    conn.sendall(b'OK\r\n')
                    print("Basarili")

                if user == False and pass_ == False:
                    conn.sendall(b'INVALID CRED\r\n')
                    print("refused")
                    #exit(0)
            


def handleClient(s, port_number):
    print("TCP connection established with peer" + str(port_number))
    s.sendall(b'USER bilkentstu\r\n')
    s.sendall(b'PASS cs421s2021\r\n')
    conn = s.accept()
    data  = conn.recv(1024)
    if "OK" in data.decode():
        while True:
            now = datetime.now()
            hour = now.strftime("%H:%M:%S")
            if hour[-2:] == "00":
                peer_id = port_number - 60000
                counter = 0
                while counter < 7:
                    s.sendall()
    else:
        s.shutdown(s.SHUT_RDWR)
        s.close()



arg = sys.argv
ADDRESS = arg[1]
PEER_ID = int(arg[2])

PORT_IN = 60000 + PEER_ID
# PORT_OUT = 50000 + PEER_ID
USERNAME = "bilkentstu"
PASSWORD = "cs421s2021"

all_connected = False
topologyFile = open('topology.txt', 'r')
lines = topologyFile.readlines()
print(lines)

# extract number of pairs of information
nPeers = int(lines[0][0])
print(nPeers)
lines = lines[1:]
print(lines)
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

print(PORT_IN)
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
    t.join()
thread_conn.join()