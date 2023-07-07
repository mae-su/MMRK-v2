from websocket import create_connection
import time

def main(IP = "192.168.86.80"):
    w = create_connection("ws://" + IP + ":9001")
    w.send("Unlock")
    w.close()
if __name__ == "__main__":
    main()