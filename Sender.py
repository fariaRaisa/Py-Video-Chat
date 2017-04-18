import numpy as np
import cv2
import time
import socket
import pyaudio
import wave
import sys
import pyaudio
import time

WIDTH = 2
CHANNELS = 1
RATE = 44100

buf = 4096
UDP_IP = "undefined"
UDP_PORT_V = 9990
UDP_PORT_A = 9991
sock_v = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock_a = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

def send_message(sock, MESSAGE, ip, port) :
    sock.sendto(MESSAGE, (ip, port))

def get_split_frame(frame):
    step = buf-7 # 7 byte meta, buf byte data
    return [ frame[ i : i+step ] for i in range(0, len(frame), step) ] 

def callback(in_data, frame_count, time_info, status):
    #message = bytes(str(in_data), "utf-8")
    #split_audio = get_split_frame(message)
    #for x in split_audio:
    message = in_data
    send_message( sock_a, in_data, UDP_IP,UDP_PORT_A)
    return (in_data, pyaudio.paContinue)


def main():
    p = pyaudio.PyAudio()
    cap = cv2.VideoCapture(0)#('sample.mp4')
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 25]
    frame_count = -1
    
    stream = p.open(format=p.get_format_from_width(WIDTH),
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    #output = True,
                    stream_callback=callback)
    stream.start_stream()
    
    while(cap.isOpened()):
        # get a frame and resize
        ret, frame = cap.read()
        #frame = cv2.imread("loop.jpg")
        if ret:
            frame = cv2.resize(frame, (640,480), interpolation = cv2.INTER_LINEAR)
        else:
            continue
        
        # compress it to jpg
        result, encimg = cv2.imencode('.jpg', frame, encode_param)
        # turn it into a bytes obj
        stringed = encimg.tostring()
        #split the frame 
        split_frames = get_split_frame(stringed)
        
        frame_count = (frame_count+1) % 10000
        part_count = 0
        for f in split_frames:
            frame_to_send =  bytes( str(frame_count).zfill(4) + str(part_count).zfill(3) ,"utf-8") + f
            send_message(sock_v, frame_to_send, UDP_IP, UDP_PORT_V)
            part_count += 1

        #if stream.is_active():
        #    time.sleep(0.1)

        cv2.imshow("Self", frame)
        if cv2.waitKey(50) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    
    stream.stop_stream()
    stream.close()
    p.terminate()


    
#main()
if __name__ == "__main__":
     main()
