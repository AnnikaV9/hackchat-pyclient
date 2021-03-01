"""
Copyright (c) 2020 AnnikaV9

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""


import json
import threading
import websocket
import sys
import re
import tkinter as tk
from tkinter import *
from datetime import datetime
from time import sleep


# The main client class
class Client:

    # Window properties setting, websocket connection, thread defining
    def __init__(self,
                 root,
                 nick,
                 password,
                 channel="programming",
                 target_websocket="wss://hack.chat/chat-ws"):

        self.main_window = tk.Frame(root,
                                    height=50,
                                    width=100)
        self.main_window.pack(fill=Y,
                              expand=True)
        self.scrollbar = Scrollbar(self.main_window)
        self.output_box = tk.Text(self.main_window,
                                  height=30,
                                  width=100,
                                  yscrollcommand=self.scrollbar.set,
                                  background="black",
                                  foreground="white")
        self.output_box.config(state="disabled")
        self.output_box.bind("<Button>",
                             lambda event: self.output_box.focus_set())
        self.input_box = tk.Text(self.main_window,
                                 height=1,
                                 width=102,
                                 background="white",
                                 foreground="black")
        self.input_box.config(wrap="none")
        self.input_box.pack(side="bottom")
        self.scrollbar.config(command=self.output_box.yview)
        self.scrollbar.pack(side=RIGHT,
                            fill=Y)
        self.output_box.pack(side="top")
        self.output_box.tag_config("LimeOnBlack",
                                   background="black",
                                   foreground="lime")
        self.output_box.tag_config("YellowOnBlack",
                                   background="black",
                                   foreground="yellow")
        self.output_box.tag_config("WhiteOnBlack",
                                   background="black",
                                   foreground="white")
        self.output_box.tag_config("CyanOnBlack",
                                   background="black",
                                   foreground="cyan")
        self.nick = nick
        self.root = root
        self.online_users = []
        self.full_nick = "{}#{}".format(nick,
                                        password)
        self.ws = websocket.create_connection(target_websocket)
        self.ws.send(json.dumps({"cmd": "join",
                                 "channel": channel,
                                 "nick": self.full_nick}))
        self.thread_ping = threading.Thread(target=self.ping_thread,
                                            daemon=True)
        self.thread_input = threading.Thread(target=self.input_thread,
                                             daemon=True)
        self.thread_main = threading.Thread(target=self.main_thread,
                                            daemon=True)

    # Main thread where received packets are parsed
    def main_thread(self):

        while True:
            received = json.loads(self.ws.recv())
            packet_receive_time = datetime.now().strftime("%H:%M")

            # Checking if --no-parse parameter was given
            try:
                if sys.argv[1] == "--no-parse":
                    text_to_print = "\n{}|{}".format(packet_receive_time,
                                                     received)
                    self.refresh_display(text=text_to_print, tag="WhiteOnBlack")

                else:
                    self.refresh_display(text="\n\nUnknown parameter: {}".format(sys.argv[1]), tag="whisper")

            # An IndexError is given if no parameters are entered, enabling parsing
            except IndexError:
                if received["cmd"] == "onlineSet":

                    for nick in received["nicks"]:
                        if self.nick in self.online_users:
                            self.online_users.remove(self.nick)
                        self.online_users.append(nick)                        
                        self.channel = received["users"][0]["channel"]
                    self.refresh_display(text="You are now connected to channel: {}\nType '/help' for a list of commands you can use with this client\n\n".format(self.channel),
                    tag="normal")
                    self.root.title("hack.chat - ?{}".format(self.channel))

                elif received["cmd"] == "chat":

                    if len(received.get("trip", "")) < 6:
                        tripcode = "NOTRIP"

                    else:
                        tripcode = received.get("trip", "")
                    text_to_print = "{}|{}|[{}] {}".format(packet_receive_time,
                                                           tripcode,
                                                           received["nick"],
                                                           received["text"])
                    self.refresh_display(text=text_to_print,
                                         tag="WhiteOnBlack")

                elif received["cmd"] == "onlineAdd":

                    if len(received.get("trip", "")) < 6:
                        tripcode = "NOTRIP"

                    else:
                        tripcode = received.get("trip", "")

                    self.online_users.append(received["nick"])
                    text_to_print = "{}|{}|{} joined".format(packet_receive_time,
                                                             tripcode,
                                                             received["nick"])
                    self.refresh_display(text=text_to_print,
                                         tag="CyanOnBlack")

                elif received["cmd"] == "onlineRemove":

                    if len(received.get("trip", "")) < 6:
                        tripcode = "NOTRIP"

                    else:
                        tripcode = received.get("trip", "")

                    self.online_users.remove(received["nick"])
                    text_to_print = "{}|{}|{} left".format(packet_receive_time,
                                                           tripcode,
                                                           received["nick"])
                    self.refresh_display(text=text_to_print,
                                         tag="CyanOnBlack")

                elif received["cmd"] == "emote":

                    if len(received.get("trip", "")) < 6:
                        tripcode = "NOTRIP"

                    else:
                        tripcode = received.get("trip", "")

                    text_to_print = "{}|{}|{}".format(packet_receive_time,
                                                      tripcode,
                                                      received["text"])
                    self.refresh_display(text=text_to_print,
                                         tag="LimeOnBlack")

                elif received["cmd"] == "info" and received.get("type") is not None and received.get("type") == "whisper":

                    if len(received.get("trip", "")) < 6:
                        tripcode = "NOTRIP"

                    else:
                        tripcode = received.get("trip", "")

                    text_to_print = "{}|{}|{}".format(packet_receive_time,
                                                      tripcode,
                                                      received["text"])
                    self.refresh_display(text=text_to_print,
                                         tag="YellowOnBlack")

                elif received["cmd"] == "info":

                    text_to_print = "{}|{}|{}".format(packet_receive_time,
                                                      "SYSTEM",
                                                      received["text"])
                    self.refresh_display(text=text_to_print,
                                         tag="LimeOnBlack")

                elif received["cmd"] == "warn":

                    text_to_print = "{}|{}|{}".format(packet_receive_time,
                                                      "!WARN!",
                                                      received["text"])
                    self.refresh_display(text=text_to_print,
                                         tag="YellowOnBlack")

    # Ping thread to keep the websocket connection alive
    def ping_thread(self):

        while self.ws.connected:
            self.ws.send(json.dumps({"cmd": "ping"}))
            sleep(60)

    # Input thread that captures user input within the input box and sends it to send_input()
    def input_thread(self):
        self.input_box.bind('<Return>',
                            lambda _: self.send_input())

    # Allows editing in the output box, inserts given text, disables editing again, and moves
    # the display down when it's filled
    def refresh_display(self,
                        text,
                        tag):
        self.output_box.config(state="normal")
        self.output_box.insert("end",
                               text+"\n", tag)
        self.output_box.config(state="disabled")
        self.output_box.yview_moveto(1)

    # Parses user input, and sends the appropriate json to server
    def send_input(self):
        message = self.input_box.get("1.0",
                                     "end-1c")
        listed = message.split()
        message = ' '.join(listed)
        message = message.replace("/n/",
                                  "\n")

        if message.split()[0] == "/raw":
            split_message = message.split()
            split_message.pop(0)
            to_send = ' '.join(split_message)
            self.input_box.delete("1.0",
                                  END)

            try:
                json_to_send = json.loads(to_send)
                self.ws.send(json.dumps(json_to_send))

            except:
                self.refresh_display(text="\nError sending json",
                                     tag="YellowOnBlack")

        elif message == "/list":
            user_list = "\n\nChannel: {}\nOnline users:\n{}\n\n".format(self.channel,
                                                                        "\n".join(map(str,
                                                                                      self.online_users)))
            self.input_box.delete("1.0",
                                  END)
            self.refresh_display(text=user_list,
                                 tag="LimeOnBlack")

        elif message == "/clear":
            self.input_box.delete("1.0",
                                  END)
            self.output_box.config(state="WhiteOnBlack")
            self.output_box.delete("1.0",
                                   END)
            self.output_box.config(state="disabled")

        elif message.split()[0] == "/move":
            split_message = message.split()
            split_message.pop(0)
            channel_to_join = ' '.join(split_message)
            self.input_box.delete("1.0",
                                  END)
            self.ws.send(json.dumps({"cmd": "move",
                                     "channel": channel_to_join}))

        elif message.split()[0] == "/nick":
            split_message = message.split()
            split_message.pop(0)
            nick_to_change = ''.join(split_message)
            self.input_box.delete("1.0",
                                  END)
            if re.match("^[A-Za-z0-9_]*$",
                        nick_to_change):
                self.ws.send(json.dumps({"cmd": "changenick",
                                         "nick": nick_to_change}))
                self.nick = nick_to_change
            else:
                self.ws.send(json.dumps({"cmd": "changenick",
                                         "nick": nick_to_change}))

        elif message.split()[0] == "/me":
            split_message = message.split()
            split_message.pop(0)
            message_to_send = ' '.join(split_message)
            self.input_box.delete("1.0",
                                  END)
            self.ws.send(json.dumps({"cmd": "emote",
                                     "text": message_to_send}))

        else:
            self.input_box.delete("1.0",
                                  END)
            self.ws.send(json.dumps({"cmd": "chat",
                                     "text": message}))

            if message == "/help":
                extra_text = "\n\nAll '/n/' will be converted into linebreaks\n\nRaw json packets can be sent with '/raw'\nUsage: /raw <json>\n\nUser list can be viewed with '/list'\nUsage: /list\n\nDisplay can be cleared with '/clear'\nUsage: /clear\n\nChannel can be changed with '/move'\nUsage: /move <newchannel>\n\nNickname can be changed with '/nick'\nUsage: /nick <newnick>\n\nAction messages can be sent with '/me'\nUsage: /me <message>\n\nWhispers can be sent with '/whisper'\nUsage: /whisper <user> <message> or /w <user> <message>\n\nUse '/reply' no reply to the user who last whispered to you\nUsage: /reply <message> or /r <message>\n\n"
                self.refresh_display(text=extra_text,
                                     tag="LimeOnBlack")


if __name__ == "__main__":
    channel = input("Channel: ")
    nick = input("Nick: ")
    password = input("Password(optional): ")
    root = tk.Tk()
    root.iconphoto(False, tk.PhotoImage(file='icon.png'))
    root.title("hack.chat")
    client = Client(root=root,
                    nick=nick,
                    password=password,
                    channel=channel,
                    # Change to connect to personal servers
                    target_websocket="wss://hack.chat/chat-ws")
    root.resizable(False,
                   False)
    # Starting all threads as daemons and window mainloop
    client.thread_main.start()
    client.thread_ping.start()
    client.thread_input.start()
    root.mainloop()
