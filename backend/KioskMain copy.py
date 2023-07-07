
import sys
import os
import art
from src import jsonHelper
from twisted.internet import reactor# Copyright (c) Twisted Matrix Laboratories. See LICENSE for details.
from twisted.internet.protocol import Factory, Protocol
from rich import print
# \033 is the "escape code." when printed to a terminal, the terminal processes the characters following it as commands for formatting, cursor control, and other terminal controls. 
redwhite = "\033[25;37;41m"
homecursor = "\033[H"
clearscreen = "\033[J"
screenf= redwhite + homecursor + clearscreen
bold = "\033[1m"
unbold = "\033[22m"
end = '\033[0m'
firstboot = False

clisplash = redwhite + art.text2art("MMRK", font="rounded", sep="\r\n") + "\nMILL Machine Room Kiosk V2\n\n"
art.tprint("MMRK", font="rounded")

class Echo(Protocol):
    inProcessString = ""
    def __init__(self):
        self.console =

    def connectionMade(self):
        
    def dataReceived(self, data):
        if data.decode() == "\b": 
            self.inProcessString = self.inProcessString[:-1]
            self.transport.write('\033[0C\x08 \x08'.encode())
        
        else:
            self.inProcessString += data.decode()
            if "\n" in self.inProcessString:
                i = i + 1
                self.inProcessString.strip().strip("\n")
                if "/exit" in self.inProcessString: 
                    self.transport.write(( end + clearscreen + homecursor + bold + clearscreen + "\rDisconnected. Press enter to return to shell.\n" + redwhite + "MMRK v2 by mae.red (2023)\b" + end + redwhite).encode())

                    self.transport.loseConnection()

                else:
                    self.command(self.inProcessString)
    def command(self,cmd):
        print("Command parsed: " + cmd)
        
        self.inProcessString=""

def main():
    f = Factory()
    f.protocol = Echo
    reactor.listenTCP(8000, f)
    reactor.run()

def installed(dir):
    try: 
        if os.path.exists(dir):
            return True
    except:
        pass
    print("No install files were found. Creating directory at: " + dir)
    try: 
        os.mkdir(dir)
    except Exception as e:
        print("Failed to create storage directory. Exiting!\n" + str(e))
        exit()
    
    try: 
        print("Creating log JSON: " + jsonHelper.createJSON(dir + "log.json"))
    except Exception as e:
        print("Failed to create log JSON. Exiting!\n" + str(e))
        exit()
    
    return False
        
        


if __name__ == "__main__":
    debug=True # Change this before debugging, unless you run the program with the --debug flag.
    dir = "/opt/MMRK-v2/" # This is where files will be stored on the pi.

    if debug or "--debug" in sys.argv:
        import os
        dir="./kioskDebugStorage/"
        os.system("wt.exe telnet 127.0.0.1 8000")
    if installed(dir):
        pass
    else:
        firstboot = True
    main()
