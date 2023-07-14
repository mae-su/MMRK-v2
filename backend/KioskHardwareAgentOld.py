import asyncio
from websocket_server import WebsocketServer

import sys

gpio = True
threadedserver=True
try: 
     from drivers import fan
     from drivers import card
except ModuleNotFoundError:
     print("[OS] Pi imports failed. Assuming a Windows platform, GPIO calls will be disabled.")
     gpio = False
     threadedserver=False

unlockEvent = asyncio.Event()
latestWebRQ = ""
debug=False

if "--debug" in sys.argv:
    debug = True
if "--threadedserver" in sys.argv:
    threadedserver = True
servoParkPosition = 4
servoEjectPosition = 7

# Called for every client connecting (after handshake)
def new_client(client, server):
	print("[Websocket] New client connected and was given id %d" % client['id'])
	server.send_message_to_all("Client connected.")


# Called for every client disconnecting
def client_left(client, server):
	print("[Websocket] Client(%d) disconnected" % client['id'])


# Called when a client sends a message
def message_received(client, server, message):
	if len(message) > 200:
		message = message[:200]+'..'
	print("[Websocket] Client(%d) said: %s" % (client['id'], message))
	if message == "Unlock":
		unlockEvent.set()
		print("[CARD] Unlocking")

if True:
    async def servoDebug():
        while True:
            print("[DEBUG] Enter servo test value:")
            asyncio.create_task(card.setServo(int(input())))
            await asyncio.sleep(1)
    
    async def unlock(s):
        print("[CARD] Retracting card.")
        asyncio.create_task(card.setServo(servoParkPosition))
        await asyncio.sleep(1)
        print("[CARD] Confirming position...")
        asyncio.create_task(card.setServo(servoParkPosition))
        await asyncio.sleep(1)
        print("[CARD] Ready.")
        
        while True:
            print("[Websocket/Card] Waiting for unlock request.")
            await unlockEvent.wait()
            print("[Card]-- Beginning unlock sequence --")
            asyncio.create_task(card.setServo(servoEjectPosition))
            await asyncio.sleep(s/1000)
            asyncio.create_task(card.setServo(servoParkPosition))
            await asyncio.sleep(1)
            print("[CARD] Confirming position...")
            asyncio.create_task(card.setServo(servoParkPosition))
                
            unlockEvent.clear()
    
    async def startupSound():
        pass
    
    async def server():
        PORT=9001
        server = WebsocketServer(port = PORT, host = "0.0.0.0")
        server.set_fn_new_client(new_client)
        server.set_fn_client_left(client_left)
        server.set_fn_message_received(message_received)
        print("[Websocket] Server running.")
        if gpio and threadedserver:
             server.run_forever(threaded=True)
        else: 
            print("[OS] Running websocket server in the main thread. To run the threaded server regardless of the operating system, run with flag --threadedserver. Please be aware that this may result in the websocket unintentionally running in the background, even after stopping the program.")
            server.run_forever()

    
async def main():
    try:
        if debug:
            tasks = [asyncio.create_task(servoDebug())]
        elif not gpio:
            tasks = [asyncio.create_task(server())]
        else:
             tasks = [asyncio.create_task(card.setServo(4)), asyncio.create_task(fan.monitor()), asyncio.create_task(server()),asyncio.create_task(unlock(1000))]
        
        done, pending = await asyncio.wait(tasks)
    
    except KeyboardInterrupt:
        print("Keyboardinterrupted! Remember to kill all python scripts before debugging, as background processes may still be running.")
        if gpio:
            import RPi.GPIO as GPIO
            GPIO.cleanup()
        
# Create the event loop
loop = asyncio.get_event_loop()

# Run the main function within the event loop using loop.run_until_complete()
loop.run_until_complete(main())

# Close the event loop
loop.close()