
import sys
import os
import art
from src import jsonHelper
# Copyright (c) Twisted Matrix Laboratories. See LICENSE for details.
from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol
import threading

# \033 is the "escape code." when printed to a terminal, the terminal processes the characters following it as commands for formatting, cursor control, and other terminal controls.
redwhite = "\033[25;37;41m"
homecursor = "\033[H"
clearscreen = "\033[J"
screenf = redwhite + homecursor + clearscreen
bold = "\033[1m"
unbold = "\033[22m"
end = '\033[0m'
def center(s, width=30):
    text_length = len(s)
    padding = max(0, (width - text_length) // 2)

    return str(" " * padding + s + " " * padding)
dir = "/opt/MMRK-v2/"  # This is where files will be stored on the pi.
firstboot = False

clisplash = redwhite + \
    art.text2art("MMRK", font="rounded", sep="\r\n") + \
    "\nMILL Machine Room Kiosk V2\n\n"



class Echo(Protocol):
    inProcessString = ""
    keypress = False  # if waiting for a keypress instead of processing commands
    latestkey = ""
    inputEvent = threading.Event()
    keycmd = ""
    def keyflag(self,cmd=None):
        '''Shorthand for interfacing with key commands'''
        if cmd is None:
            self.keypress = False
        else:
            self.keypress = True
            self.keycmd = cmd
            self.transport.write("\033[?25l".encode())
    def connectionMade(self):
        # the escape codes here take care of setting formatting to the red + white background, and you can unset this by printing '\x1b[J'
        self.transport.write(screenf.encode())
        self.transport.write((clisplash + "Welcome to the MMRK shell.").encode())
        if firstboot:
            self.transport.write((bold + "\r\n\033[101m" + "Welcome." + unbold + "\n PINs and credentials need setting up. Press " + bold + "Space" + unbold + " to continue setup, or " + bold + "+" + unbold + " to reinstall an archive file.").encode())
            self.keyflag("setup|archive") 
        else:
            self.transport.write((" Please authenticate, or type " + bold + "/exit" + end + redwhite + " to disconnect.\n\r").encode())
            
    def dataReceived(self, data):
        if self.keypress:
            print(data.decode())
            self.inputEvent.set()
            self.latestkey = data.decode().strip("\n")
            if self.keycmd == "setup|archive":
                if " " in self.latestkey:
                    install(self.transport.write)
        else:
            if data.decode() == "\b":
                self.inProcessString = self.inProcessString[:-1]
                self.transport.write('\033[0C\x08 \x08'.encode())
            else:
                self.inProcessString += data.decode()
                if "\n" in self.inProcessString:
                    self.inProcessString.strip().strip("\n")
                    if "/exit" in self.inProcessString:
                        self.transport.write((end + clearscreen + homecursor + bold + clearscreen +"\rDisconnected. Press enter to return to shell.\n" + redwhite + "MMRK v2 by mae.red (2023)\b" + end + redwhite).encode())

                        self.transport.loseConnection()
                    else:
                        self.command(self.inProcessString)

    def command(self, cmd):
        print("Command parsed: " + cmd)

        self.inProcessString = ""


def main():
    f = Factory()
    f.protocol = Echo
    reactor.listenTCP(8000, f)
    reactor.run()

def isinstalled(dir):
    try:
        if os.path.exists(dir):
            return True
    except:
        return False
def install(out):
    
    out(("\n Installing directory at: " + dir + "\n").encode())
    try:
        os.mkdir(dir)
    except Exception as e:
        out(str("Failed to create storage directory. \n" + str(e)).encode())

    try:
        out(str("Creating log JSON: " + jsonHelper.createJSON(dir + "log.json") + "\n").encode())
    except Exception as e:
        out(str("Failed to create log JSON. \n" + str(e)).encode())
    out(str("Success!").encode())


if __name__ == "__main__":
    # Change this before debugging, unless you run the program with the --debug flag.
    debug = True


    if debug or "--debug" in sys.argv:
        import os
        dir = "./kioskDebugStorage/"
        os.system("wt.exe telnet 127.0.0.1 8000")
    if isinstalled(dir):
        pass
    else:
        firstboot = True
    main()
