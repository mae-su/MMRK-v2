from websocket import create_connection
import time
ws = create_connection("ws://192.168.86.52:9001")

ws.send("Unlock")
time.sleep(2.5)