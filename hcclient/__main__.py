# No copyright, licenses or whatever
# Edit 'target_websocket' within the Client class to access personal servers

import json
import threading
import websocket
import tkinter as tk
from tkinter import *
from os import system, name
from datetime import datetime
from time import sleep



class Client:


    def __init__(self, root, nick, password, channel="programming", target_websocket="wss://hack.chat/chat-ws"):
        self.main_window = tk.Frame(root, height=50, width=100)
        self.main_window.pack(fill=Y, expand=True)
        self.scrollbar = Scrollbar(self.main_window)
        self.output_box = tk.Text(self.main_window, height=30, width=100, yscrollcommand=self.scrollbar.set, bg='black', fg='white')
        self.output_box.config(state='disabled')
        self.output_box.bind("<Button>", lambda event: self.output_box.focus_set())
        self.input_box = tk.Text(self.main_window, height=1, width=102, bg='white', fg='black')
        self.input_box.config(wrap='none')
        self.input_box.pack(side='bottom')
        self.scrollbar.config(command=self.output_box.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.output_box.pack(side='top')
        self.nick = nick
        self.channel = channel
        self.online_users = []
        self.full_nick = "{}#{}".format(nick, password)
        self.ws = websocket.create_connection(target_websocket)
        self.ws.send(json.dumps({"cmd": "join", "channel": channel, "nick": self.full_nick}))
        self.refresh_display(text="You are now connected to the channel: {}\nType '/help' for a list of commands you can use with this client\n\n".format(channel))
        self.thread_ping = threading.Thread(target=self.ping_thread, daemon=True)
        self.thread_input = threading.Thread(target=self.input_thread, daemon=True)
        self.thread_main = threading.Thread(target=self.main_thread, daemon=True)

    
    def main_thread(self):        
        
        while True:            
            received = json.loads(self.ws.recv())
            packet_receive_time = datetime.now().strftime("%H:%M")
            
            if received["cmd"] == "chat":

                if len(received.get("trip", "")) < 6:
                    tripcode = "NOTRIP"

                else:
                    tripcode = received.get("trip", "")
                text_to_print = "{}|{}|[{}] {}".format(packet_receive_time,
                                                       tripcode,
                                                       received["nick"],
                                                       received["text"])
                self.refresh_display(text=text_to_print)

            elif received["cmd"] == "onlineAdd":

                if len(received.get("trip", "")) < 6:
                    tripcode = "NOTRIP"

                else:
                    tripcode = received.get("trip", "")
                
                self.online_users.append(received["nick"])
                text_to_print = "{}|{}|{} joined".format(packet_receive_time,
                                                         tripcode,
                                                         received["nick"])
                self.refresh_display(text=text_to_print)
                    
            elif received["cmd"] == "onlineRemove":                

                if len(received.get("trip", "")) < 6:
                    tripcode = "NOTRIP"

                else:
                    tripcode = received.get("trip", "")
                
                self.online_users.remove(received["nick"])
                text_to_print = "{}|{}|{} left".format(packet_receive_time,
                                                       tripcode,
                                                       received["nick"])
                self.refresh_display(text=text_to_print)
            
            elif received["cmd"] == "onlineSet":                

                for nick in received["nicks"]:                    
                    self.online_users.append(nick)
            
            elif received["cmd"] == "emote":

                if len(received.get("trip", "")) < 6:
                    tripcode = "NOTRIP"

                else:
                    tripcode = received.get("trip", "")

                text_to_print = "{}|{}|{}".format(packet_receive_time,
                                                  tripcode,
                                                  received["text"])
                self.refresh_display(text=text_to_print)
                    
            elif received["cmd"] == "info" and received.get("type") is not None and received.get("type") == "whisper": 

                if len(received.get("trip", "")) < 6:
                    tripcode = "NOTRIP"

                else:
                    tripcode = received.get("trip", "")
                    
                text_to_print = "{}|{}|{}".format(packet_receive_time,
                                                  tripcode,
                                                  received["text"])
                self.refresh_display(text=text_to_print)

            
            elif received["cmd"] == "info":
 
                text_to_print = "{}|{}|{}".format(packet_receive_time,
                                                  "SYSTEM",
                                                  received["text"])
                self.refresh_display(text=text_to_print)
 
            elif received["cmd"] == "warn":

                text_to_print = "{}|{}|{}".format(packet_receive_time,
                                                     "!WARN!",
                                                     received["text"])
                self.refresh_display(text=text_to_print)

                   
    def ping_thread(self):        

        while self.ws.connected:            
            self.ws.send(json.dumps({"cmd": "ping"}))
            sleep(60)


    def input_thread(self):        
         self.input_box.bind('<Return>', lambda _: self.send_input())

        
    def refresh_display(self, text):
        self.output_box.config(state='normal')
        self.output_box.insert('end', text+"\n")
        self.output_box.config(state='disabled')
        self.output_box.yview_moveto( 1 ) 

                    
    def send_input(self):
        message = self.input_box.get("1.0", "end-1c")
        listed = message.split()
        message = ' '.join(listed)
        message = message.replace("/n/", "\n")
        check = ''.join(listed)

        if message.split()[0] == "/raw":
            split_message = message.split()
            split_message.pop(0)
            to_send = ' '.join(split_message)
            self.input_box.delete("1.0", END)

            try:
                json_to_send = json.loads(to_send)
                self.ws.send(json.dumps(json_to_send))

            except:
                self.refresh_display(text="\nError sending json")
        
        elif message == "/list":
            user_list = "\n\nChannel: {}\nOnline users:\n{}\n\n".format(channel, "\n".join(map(str, self.online_users)))
            self.input_box.delete("1.0", END)
            self.refresh_display(text=user_list)

        else:
            self.input_box.delete("1.0", END)
            self.ws.send(json.dumps({"cmd": "chat", "text": message}))     

            if message == "/help":
                extra_text = "\n\nAll '/n/' will be converted into linebreaks\n\nRaw json packets can be sent with '/raw'\nUsage: /raw <json>\n\nUser list can be viewed with '/list'\nUsage: /list\n\n"
                self.refresh_display(text=extra_text)
        
   
if __name__ == "__main__":
    channel = input("Channel: ")
    nick = input("Nick: ")
    password = input("Password(optional): ")
    root = tk.Tk()
    root.title("hcclient")
    client = Client(root=root,
                    nick=nick,
                    password=password,
                    channel=channel,
                    target_websocket="wss://hack.chat/chat-ws")
    root.resizable(False, False)
    client.thread_main.start()
    client.thread_ping.start()
    client.thread_input.start()
    root.mainloop()
