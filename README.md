# hackchat-pyclient
A python client for connecting to hack.chat servers.


## Requirements
Python3


## Setup and Usage
```
pip3 uninstall websocket
pip3 install websocket-client
pip3 install colorama

git clone https://github.com/AnnikaV9/hackchat-pyclient.git
cd hackchat-pyclient
python3 hcclient
```


## Expected colors
```
message: terminal default
timestamp: terminal default
nick(you): red
nick(others): cyan
whisper: yellow
join/leave: green
emote: green
tripcode: white
warn: yellow
system: yellow 
```
Color compatibility may vary on different terminals.
