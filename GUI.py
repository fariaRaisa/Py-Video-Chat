from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
import threading
import Sender
import Receiver
from socket import *

udp_socket = socket(AF_INET,SOCK_DGRAM)
udp_socket.bind(("",9992))

# Tniker code
class VideoChat(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent        
        self.initUI()
        
    def initUI(self):
        self.parent.title("Quit button")
        self.style = Style()    
        self.style.theme_use("default")

        label = Label(self, text="IP address to call!")
        label.place(x=35, y=30)
        
        ip_entry = Entry(self)
        ip_entry.place(x=20, y=50)

        startButton = Button(self, text="Call",
            command= lambda : make_call(ip_entry.get()))
        startButton.place(x=160, y=50)
        self.pack(fill=BOTH, expand=1)



def start_conversation(address):
    Sender.UDP_IP = address
    sender_thread = threading.Thread( target = Sender.main )
    sender_thread.daemon = True
    sender_thread.start()

    receiver_thread = threading.Thread( target = Receiver.main )
    receiver_thread.daemon = True
    receiver_thread.start()
    
def make_call(address):
    parts = address.split('.')
    if len(parts) == 4:
        udp_socket.sendto( bytes("CALL","utf-8"), (address,9992))
        print("sent request")
        
        
def receive_call():
    while  True:
        data,address = udp_socket.recvfrom(1024)
        
        if data.decode("utf-8")== "CALL":
            if messagebox.askokcancel("Receive", "Incoming Call..."):
                udp_socket.sendto( bytes("RECV","utf-8"), (address[0],9992))
                start_conversation(address[0])
                print(address)
                break
        elif data.decode("utf-8") == "RECV":
            start_conversation(address[0])
            

root = Tk()
def on_closing():
    global root

    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()

def main():
    global root

    # start receiver module in a separate thread
    call_receiver_thread = threading.Thread( target = receive_call)
    call_receiver_thread.daemon = True
    call_receiver_thread.start()
    
    root.geometry("250x150+300+300")
    app = VideoChat(root)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__=='__main__':
    main()
