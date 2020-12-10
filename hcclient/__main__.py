# No copyright, licenses or whatever
# Edit 'target_websocket' within the Client class to access personal servers



import json
import threading
import websocket
import colorama
from os import system, name
from datetime import datetime
from time import sleep



colorama.init()



class Client:
     
        
    def __init__(self, nick, password, channel="programming", target_websocket="wss://hack.chat/chat-ws"):  
        self.nick = nick
        self.channel = channel
        self.online_users = []
        self.full_nick = "{}#{}".format(nick, password)
        self.ws = websocket.create_connection(target_websocket)
        self.ws.send(json.dumps({"cmd": "join", "channel": channel, "nick": self.full_nick}))

        system('cls' if name == 'nt' else 'clear')

        print("You are now connected to the channel: {}".format(color_list.RED +
                                                                    channel +
                                                                    color_list.END))
        print("Type '/list' to see who's online.\n\n".format(self.online_users))

        self.thread_ping = threading.Thread(target=self.ping_thread)
        self.thread_input = threading.Thread(target=self.input_thread)
        self.thread_main = threading.Thread(target=self.main_thread)


    def main_thread(self):        
        
        while True:            
            received = json.loads(self.ws.recv())
            packet_receive_time = datetime.now().strftime("%H:%M")
            
            if received["cmd"] == "chat":

                if len(received.get("trip", "")) < 6:
                    tripcode = "NOTRIP"

                else:
                    tripcode = received.get("trip", "")

                colored_trip = color_list.WHITE + tripcode + color_list.END

                if received["nick"] != self.nick:
                    colored_nick = color_list.CYAN + received["nick"] + color_list.END
                    print("{}|{}|[{}] {}".format(packet_receive_time,
                                                 colored_trip,
                                                 colored_nick,
                                                 received["text"]))

                else:                   
                    colored_nick = color_list.RED + received["nick"] + color_list.END
                    print("{}|{}|[{}] {}".format(packet_receive_time,
                                                 colored_trip,
                                                 colored_nick,
                                                 received["text"]))

            elif received["cmd"] == "onlineAdd":

                if len(received.get("trip", "")) < 6:
                    tripcode = "NOTRIP"

                else:
                    tripcode = received.get("trip", "")
                
                colored_trip = color_list.WHITE + tripcode + color_list.END
                self.online_users.append(received["nick"])
                print("{}|{}|".format(packet_receive_time, colored_trip) +
                      color_list.GREEN +
                      "{} joined".format(received["nick"]) + 
                      color_list.END)
                    
            elif received["cmd"] == "onlineRemove":                

                if len(received.get("trip", "")) < 6:
                    tripcode = "NOTRIP"

                else:
                    tripcode = received.get("trip", "")
                
                colored_trip = color_list.WHITE + tripcode + color_list.END
                self.online_users.remove(received["nick"])
                print("{}|{}|".format(packet_receive_time, colored_trip) +
                      color_list.GREEN +
                      "{} left".format(received["nick"]) +
                      color_list.END)
            
            elif received["cmd"] == "onlineSet":                

                for nick in received["nicks"]:                    
                    self.online_users.append(nick)
            
            elif received["cmd"] == "emote":

                if len(received.get("trip", "")) < 6:
                    tripcode = "NOTRIP"

                else:
                    tripcode = received.get("trip", "")

                colored_emote = color_list.GREEN + received["text"] + color_list.END
                colored_trip = color_list.WHITE + tripcode + color_list.END

                print("{}|{}|{}".format(packet_receive_time,
                                        colored_trip,
                                        colored_emote))                    
                    
            elif received["cmd"] == "info" and received.get("type") is not None and received.get("type") == "whisper": 

                if len(received.get("trip", "")) < 6:
                    tripcode = "NOTRIP"

                else:
                    tripcode = received.get("trip", "")
                    
                colored_whisper = color_list.YELLOW + received["text"] + color_list.END
                colored_trip = color_list.WHITE + tripcode + color_list.END
                print("{}|{}|{}".format(packet_receive_time,
                                        colored_trip,
                                        colored_whisper))
            
            elif received["cmd"] == "info":
                if len(received.get("trip", "")) < 6:
                    tripcode = "NOTRIP"

                else:
                    tripcode = received.get("trip", "")
                colored_info = color_list.YELLOW + received["text"] + color_list.END
                colored_trip = color_list.WHITE + "SYSTEM" + color_list.END
                print("{}|{}|{}".format(packet_receive_time,
                                        colored_trip,
                                        colored_info))
            
            elif received["cmd"] == "warn":
                colored_warn = color_list.YELLOW + received["text"] + color_list.END
                colored_trip = color_list.WHITE + "!WARN!" + color_list.END
                print("{}|{}|{}".format(packet_receive_time,
                                        colored_trip,
                                        colored_warn))
                   
                                
    def ping_thread(self):        

        while self.ws.connected:            
            self.ws.send(json.dumps({"cmd": "ping"}))
            sleep(60)


    def input_thread(self):        
        
        while self.ws.connected:
                        
            message = str(input())

            if message == "/list":
                print("\n\nOnline users:\n{}\n\n".format("\n".join(map(str, self.online_users))))
             
            else:
                self.ws.send(json.dumps({"cmd": "chat", "text": message}))                       




class color_list:

    CYAN = '\033[1;36;48m'
    GREEN = '\033[1;32;48m'
    YELLOW = '\033[1;33;48m'
    RED = '\033[1;31;48m'
    WHITE = '\33[37m'
    END = '\033[1;37;0m'
   

                
if __name__ == "__main__":
    channel_to_join = input("Channel: ")
    nick_to_use = input("Nick: ")
    password = input("Password(optional): ")
    client = Client(nick=nick_to_use,
                    password=password,
                    channel=channel_to_join,
                    target_websocket="wss://hack.chat/chat-ws")
    client.thread_main.start()
    client.thread_ping.start()
    client.thread_input.start()
