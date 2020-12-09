# No copyright, licenses or whatever
# Edit 'target_websocket' within the Client class to access personal servers



import json
import threading
import websocket
import colorama
from time import sleep
from termcolor import colored





class Client:
     
 
       
    def __init__(self, nick, channel="programming", target_websocket="wss://hack.chat/chat-ws"):  
        self.nick = nick
        self.channel = channel
        self.online_users = []
        self.ws = websocket.create_connection(target_websocket)
        self.ws.send(json.dumps({"cmd": "join", "channel": channel, "nick": nick}))

        print("\n\nYou are now connected to the channel: {}".format(channel))
        print("Type '/list' to see who's online.\n\n".format(self.online_users))

        self.thread_ping = threading.Thread(target=self.ping_thread)
        self.thread_input = threading.Thread(target=self.input_thread)
        self.thread_main = threading.Thread(target=self.main_thread)



    def main_thread(self):        

        while True:            
            received = json.loads(self.ws.recv())
            
            if received["cmd"] == "chat":
                if received["nick"] != self.nick:
                    print("{}|[{}] {}".format(colored(received.get("trip", ""), 'white'), colored(received["nick"], "cyan"), received["text"]))
                else:
                    print("{}{}|[{}] {}".format(colored("you:","red", attrs=["bold"]),colored(received.get("trip", ""), 'white'), colored(received["nick"], "cyan"), received["text"]))

            elif received["cmd"] == "onlineAdd":
                self.online_users.append(received["nick"])
                print("|{} joined (Trip: {})".format(colored(received["nick"], 'cyan'), colored(received.get("trip", ""), 'white')))
                    
            elif received["cmd"] == "onlineRemove":                
                self.online_users.remove(received["nick"])
                print("|{} left".format(colored(received["nick"], 'cyan')))
            
            elif received["cmd"] == "onlineSet":                
                for nick in received["nicks"]:                    
                    self.online_users.append(nick)
            
            elif received["cmd"] == "emote":
                if received["nick"] != self.nick:
                    print("{}| {}".format(colored(received.get("trip", ""), 'white'), received["text"]))                    
                else:
                    print("{}{}| {}".format(colored("you:","red", attrs=["bold"]),colored(received.get("trip", ""), 'white'), received["text"]))
                    
            elif received["cmd"] == "info" and received.get("type") is not None and received.get("type") == "whisper": 
                print("{}| {}".format(colored(received.get("trip", ""),'white'), received["text"]))
                
                   
                                
    def ping_thread(self):        

        while self.ws.connected:            
            self.ws.send(json.dumps({"cmd": "ping"}))
            sleep(60)



    def input_thread(self):        
        
        while self.ws.connected:
            message = str(input())
            self.ws.send(json.dumps({"cmd": "chat", "text": message}))                       

            if message == "/list":
                print("\n\nOnline users:\n{}\n\n".format("\n".join(map(str, self.online_users))))


                
if __name__ == "__main__":
    channel_to_join = input("Channel:")
    nick_to_use = input("Nick:")
    client = Client(nick=nick_to_use,
                    channel=channel_to_join,
                    target_websocket="wss://hack.chat/chat-ws")
    colorama.init()
    client.thread_main.start()
    client.thread_ping.start()
    client.thread_input.start()

