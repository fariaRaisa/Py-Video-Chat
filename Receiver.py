import numpy as np
import cv2
import time
import threading
from socket import *
import queue
import pyaudio
import Sender

# Set the socket parameters
#host = "192.168.0.100"
host = ""
UDP_PORT_A = 9991
UDP_PORT_V = 9990
buf = 4096
audio_buf = 10000
addr_a = (host, UDP_PORT_A )
addr_v = (host, UDP_PORT_V)
frame_queue = queue.Queue()
prepared_frames = queue.Queue()
frame_queue_lock = threading.Lock()
last_time = time.clock()
frame_time = 0 #ms
# Create socket and bind to address
UDPSock_V = socket(AF_INET,SOCK_DGRAM)
UDPSock_V.bind(addr_v)
UDPSock_A = socket(AF_INET,SOCK_DGRAM)
UDPSock_A.bind(addr_a)
WIDTH = 2
CHANNELS = 1
RATE = 44100
p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(WIDTH),
            channels=CHANNELS,
            rate=RATE,
            output = True)

def get_packet_v():
    global frame_queue
    global frame_queue_lock
    global last_time
    global in_call

    # Receive messages
    while True:
        data,address = UDPSock_V.recvfrom(buf)
        frame_queue.put(data)


def get_packet_a():
    global stream
    # Receive messages
    while True:
        data,address = UDPSock_A.recvfrom(audio_buf)
        stream.write(data)

def prepare_frame(cur_frame_parts):
    cur_frame_parts = sorted(cur_frame_parts, key = lambda part : int( part[0:3]) )
    cur_frame = bytes()
    for part in cur_frame_parts:
        cur_frame += part[3:len(part)]

    if len(cur_frame)>0 :
        de_stringed = np.fromstring(cur_frame, np.uint8)
        decimg = cv2.imdecode(de_stringed, 1)
        return decimg
    return None

def main():
    global frame_queue
    global prepared_frames
    global frame_queue_lock
    global last_time
    global stream
    global p


    stream.start_stream()
    
    print("before")
    # start receiving
    v_receiver_thread = threading.Thread( target = get_packet_v )
    v_receiver_thread.daemon = True
    v_receiver_thread.start()

    a_receiver_thread = threading.Thread( target = get_packet_a )
    a_receiver_thread.daemon = True
    a_receiver_thread.start()

    print("after")
    
    # process data in queue
    is_running = True
    current_frame_no = 0
    current_part_no = 0
    cur_frame = bytes()
    cur_frame_parts = list()

    while(is_running):
        if not frame_queue.empty():
            frame_queue_lock.acquire()
            part = frame_queue.get()
            frame_queue_lock.release()
            
            if int( part[0:4]) >= current_frame_no :
                if int( part[0:4] ) > current_frame_no :
                    # new frame received so...
                    prepared_frames.put( prepare_frame(cur_frame_parts))
                    current_frame_no = int(part[0:4])
                    cur_frame_parts.clear()
                cur_frame_parts.append( part[4: len(part)] )

        # is it time to construct the frame?
        cur_time = time.clock()
        if  cur_time - last_time >= frame_time:
            last_time = cur_time
            if not prepared_frames.empty():
                cv2.imshow('Remote',prepared_frames.get())
                
        if cv2.waitKey(1) & 0xFF == ord('q'):
            is_running = False

    stream.stop_stream()
    stream.close()
    cv2.destroyAllWindows()

#main()
if __name__=="__main__":
    main()
