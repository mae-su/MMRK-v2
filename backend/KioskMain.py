import sys
import os
import art
from src import jsonHelper
from src import cardswipe
from twisted.internet import reactor, endpoints
from twisted.internet.protocol import Factory, Protocol
from twisted.web import server, resource, static
from twisted.protocols.basic import LineReceiver
import threading
import socket
import datetime

# \033 is the "escape code." when printed to a terminal, the terminal processes the characters following it as commands for formatting, cursor control, and other terminal controls.
redwhite = "\033[25;33;49m"
homecursor = "\033[H"
clearscreen = "\033[J"
screenf = redwhite + homecursor + clearscreen
bold = "\033[1m"
unbold = "\033[22m"
ul = "\033[4m"
unul = "\033[24m"
boldul = bold + ul
unboldul = unbold + unul
end = "\033[0m"
latestSignIns = []

dir = "/opt/MMRK-v2/"  # This is where files will be stored on the pi.
firstboot = False
kioskIP = "127.0.0.1"
clisplash = (
    redwhite
    + art.text2art("MMRK", font="rounded", sep="\r\n")
    + "MILL Machine Room Kiosk V2\n"
)

def entry(b=None):
  if b is None:
    j = jsonHelper.getJson(dir + "secrets.json")["entryDenied"]
    # print(jsonHelper.getJson(dir + "secrets.json")["entryDenied"])
    if j == "False":
      return False
    if j == "True":
      return True
    
  else:
    j = jsonHelper.getJson(dir + "secrets.json")
    j["entryDenied"] = str(b)
    jsonHelper.setJson(dir + "secrets.json",j)

def isinstalled(dir):
    try:
        if os.path.exists(dir):
            return True
    except:
        print(dir + " not found.")
        return False


class Echo(Protocol):
    inProcessString = ""
    keypress = False  # if waiting for a keypress instead of processing commands
    latestkey = ""
    inputEvent = threading.Event()
    keycmd = ""
    authenticated = False

    def out(self, s, nl="\r", end="\n"):
        self.transport.write((nl + str(s) + end).encode())

    def keyflag(self, cmd=None):
        """Shorthand for interfacing with key commands"""
        if cmd is None:
            self.keypress = False
        else:
            self.keypress = True
            self.keycmd = cmd
            self.transport.write("\033[25l".encode())

    def connectionMade(self):
        self.teleport_protocol = TeleportProtocol(self)
        self.authenticated = False
        self.out(screenf)
        self.out(clisplash)
        self.out("Welcome to the kiosk shell.")
        if not isinstalled(dir + "secrets.json"):
            self.authenticated = True
            self.out(
                "No admin password is set. Please set one using /adminpass <password>"
            )
        if firstboot:
            self.out(
                bold + "\033[101m" + "PINs and credentials need setting up. Press " + boldul + "Space" + unboldul + " to continue setup, or " + boldul + "+" + unboldul + " to reinstall an archive file."
            )
            self.out("\033[25l")
            self.keyflag("setup|archive")
        elif not self.authenticated:
            self.out(
                "Please authenticate with " + bold + "/unlock <password>" + unbold + ", or type " + bold + "/exit" + unbold + " to disconnect.\r\n"
            )

    def dataReceived(self, data):
        if self.keypress:
            print(data.decode())
            self.inputEvent.set()
            self.latestkey = data.decode().strip("\n")
            self.keypress = False
            # KEY COMMANDS
            if self.keycmd == "setup|archive":
                if " " in self.latestkey:
                    install(self.out)
            self.keycmd = ""
        else:
            if data.decode() == "\b":
                self.inProcessString = self.inProcessString[:-1]
                self.transport.write("\033[0C\x08 \x08".encode())
            else:
                self.inProcessString += data.decode()
                if "\n" in self.inProcessString:
                    self.inProcessString.strip().strip("\n")
                    if "/exit" in self.inProcessString:
                        self.transport.write((end + clearscreen + homecursor + bold + clearscreen + "\rDisconnected. Press enter to return to shell.\n" + redwhite + "MMRK v2 by mae.red (2023)\b" + end + redwhite).encode())
                        self.transport.loseConnection()
                    else:
                        self.shellcommand(self.inProcessString)
    
    def shellcommand(self, cmd):
        cmd = cmd.strip()
        self.transport.write((redwhite + unbold).encode)
        print("Command parsed: " + cmd)
        self.inProcessString = ""
        if "/adminpass" in cmd and self.authenticated:
            print("authcode = " + str(cmd).split(" ")[1])
            self.out("Admin password has been set to " + cmd.split(" ")[1])
            self.out("Writing secrets.json to " + dir)
            jsonHelper.createJSON(dir + "secrets.json")
            jsonHelper.setJson(
                dir + "secrets.json", {"authcode": cmd.split(" ")[1].strip()}
            )

        if "/unlock" in cmd:
            if self.authenticated:
                self.out("Already authenticated.")
            else:
                try:
                    if jsonHelper.getJson(dir + "secrets.json")[
                        "authcode"
                    ] in cmd.split(" ")[1].strip("\n"):
                        self.out("Authenticated! Admin commands now enabled.")
                        self.authenticated = True
                    else:
                        self.out("Incorrect password.")
                except:
                    self.out("An error occured.")
                    
        if "/getlog" in cmd and self.authenticated:
            self.out()

        if "/help" in cmd:
            self.out("")
            self.out(boldul + "/help" + unboldul + ": The command you're using right now. Wowzers.")
            self.out(boldul + "/id-add" + unboldul + ":")
            self.out("  Adds an ID to the system.")
            self.out("  Format: /id-add <#ID> <firstname> <lastname> <machine> <machine> <...>")
            self.out("  Ex: /id-add 12345 Jane Doe bandsaw sanding_belt drill_press")
            self.out("  All arguments should be separated by spaces. To add a space inside an argument, use an underscore:")
            self.out("  \'Sanding Belt\' --> sanding_belt")
            self.out("")
            
            self.out(boldul + "/id-remove" + unboldul + ": <#ID>")
            self.out("  Removes an ID from the system.")
            

        if "/id-add" in cmd and self.authenticated:
            number = cmd.split(" ")[1]
            firstname = cmd.split(" ")[2]
            lastname = cmd.split(" ")[3]
            machines = cmd.split(" ")[4:(len(cmd.strip().split(" ")))]
            print(machines)
            for i in machines:
                i = i.replace(" ", "_")
            UIDdata = jsonHelper.getJson(dir + "UIDs.json")
            UIDdata[number] = {
                "firstname":firstname,
                "lastname":lastname,
                "machines":machines
            }
            jsonHelper.setJson(dir + "UIDs.json",UIDdata)
        
        if "/id-remove" in cmd and self.authenticated:
            number = cmd.split(" ")[1]
            UIDdata = jsonHelper.getJson(dir + "UIDs.json")
            del UIDdata[number]
            jsonHelper.setJson(dir + "UIDs.json",UIDdata)
        
        if "/id-get" in cmd and self.authenticated:
            
            ID = cmd.split(" ")[1]
            
            print(machines)
            for i in machines:
                i = i.replace(" ", "_")
            UIDdata = jsonHelper.getJson(dir + "UIDs.json")
            UIDdata[number] = {
                "firstname":firstname,
                "lastname":lastname,
                "machines":machines
            }
            jsonHelper.setJson(dir + "UIDs.json",UIDdata)

        
        if "/manual" in cmd and self.authenticated:
            self.out("Unlock request sent to hardware socket.")
            try:
                if debug:
                    print("[DEBUG] Card swipe called.")
                else:
                    cardswipe.main(IP=kioskIP)
            except:
                self.out
        self.out("",end="bold")
        
class TeleportProtocol(LineReceiver):
    def __init__(self, echo_protocol):
        self.echo_protocol = echo_protocol

    def lineReceived(self, line):
        print("Received:", line)
        self.echo_protocol.sendLine(line)

class Simple(resource.Resource):
    isLeaf = True
    
    def getChild(self, path, request):
        if path == b"":
            return self
        return resource.Resource.getChild(self, path, request)

    def render_GET(self, request):
        print(str(request.path))
        if request.path == b"./":
            file_path = b"./ui/index.html"
            return static.File(file_path).getContent()
        
        if request.path == b"/ui/":
          file_path = b"./ui/index.html"
          return static.File(file_path).getContent()
        elif b"/ui/" in request.path:
          file_path = b"./ui/" + str(request.path.decode()).replace("/ui/","").encode()
          return static.File(file_path).getContent()
            
        if request.path == b"/admin/":
            file_path = b"./admin/index.html"
            return static.File(file_path).getContent()
        elif b"/admin/" in request.path:
          file_path = b"./admin/" + str(request.path.decode()).replace("/admin/","").encode()
          return static.File(file_path).getContent()
        


    def render_POST(self, request):
        request.setHeader(b"Access-Control-Allow-Origin", b"*")
        content = str(request.content.read().decode("utf-8"))
        
        
        if content.startswith("%"):
            resp = self.adminPostHandler(content.strip("%"))
            print("[Admin] " + content.strip("%") + " --> " + str(resp))
            return str("%" + str(resp)).encode()
        elif content.startswith("+"):
            resp = self.UIPostHandler(content.strip("+"))
            print("[UI] " + content.strip("+") + " --> " + resp)
            return str("+" + str(resp)).encode()
        
    def UIPostHandler(self, content):
        
        if "Ping" in content:
          if entry():
            return str("entryDenied")
          else:
            return str("entryAllowed")
        ##process web POSTS here
        if "SignInReq;" in content:
          try:
            result = checkID(content.split(";")[1])
          except Exception as e:
            print(e)
          if result[0] == "Incorrect":
            latestSignIns.append("Incorrect sign in attempted.")
            # print("append " + latestSignIns[len(latestSignIns)-1])
            return "Incorrect"
          else:
            # print(str("Authorize;" + result[0] + ";" + ";".join(result[1])))
            latestSignIns.append(result[0] + " is signing in...")
            return str("Authorize;" + result[0] + ";" + ";".join(result[1]))
        if "Unlock;" in content:
          ID = content.split(";")[1]
          latestSignIns.append(checkID(ID)[0] + " has signed in.")
          machines = content.split(";")[2].split(",")
          log(ID,machines)
          if debug:
              print("[DEBUG] Card swipe called.")
          else:
              cardswipe.main(IP=kioskIP)
              return "Log Success;"
        if content == "Ipaddr":
            return str("Ipaddr;" + socket.gethostbyname(socket.gethostname()))  # send IP address
        else:
            return "OK"  # Return a response to the client
    def adminPostHandler(self, content):
  
        if "Ping" in content:
          if entry():
            return str("entryDenied;")
          else:
            return str("entryAllowed;")
        if "SignInReq;" in content:
          print(jsonHelper.getJson(dir + "secrets.json")["authcode"])
          if content.split(";")[1] in jsonHelper.getJson(dir + "secrets.json")["authcode"]:
            latestSignIns.clear()
            return "Authorize"
          else:
            return "Incorrect"
        if "Latest;" in content:
          if len(latestSignIns)>0:
            resp = latestSignIns[0]
            
            latestSignIns.remove(resp)
            return "Latest;" + str(resp)
          else:
            return "Latest"
            
        if "ToggleEntry;" in content:
          if entry():
            entry(False)
            return "Machine room closed."
          else:
            entry(True)
            return "Machine room open."
          

def main():
    f = Factory()
    f.protocol = Echo
    site = server.Site(Simple())
    endpoint = endpoints.TCP4ServerEndpoint(reactor, 8080)
    endpoint.listen(site)
    reactor.listenTCP(8000, f)
    reactor.run()


def install(out):
    out(("\n Installing directory at: " + dir + "\n").encode())
    try:
        os.mkdir(dir)
    except Exception as e:
        out(str("Failed to create storage directory. \n" + str(e)).encode())

    try:
        out(str("Creating JSONs: " + dir + "\n").encode())
        jsonHelper.createJSON(dir + "log.json")
        jsonHelper.createJSON(dir + "UIDs.json")

    except Exception as e:
        out(str("Failed to create JSONs. \n" + str(e)).encode())
    out(str("Success! Please set a password with /adminpass <password>").encode())

def log(ID, machines):
    logdata = jsonHelper.getJson(dir + "log.json")
    logdata [datetime.datetime.now().timestamp()] = {
        "ID":ID,
        "machines":machines
    }
    jsonHelper.setJson(dir + "log.json",logdata)


def checkID(ID):
    UIDs = jsonHelper.getJson(dir + "UIDs.json")
    if ID in UIDs:
      
      return [UIDs[ID]['firstname'],UIDs[ID]['machines']]
    else:
      return ["Incorrect"]

if __name__ == "__main__":
    # Change this before debugging, unless you run the program with the --debug flag.
    debug = True

    if debug or "--debug" in sys.argv:
        import os

        dir = "./data/"
        # os.system("wt.exe telnet 127.0.0.1 8000")
        kioskIP = "192.168.86.80"

    if isinstalled(dir):
        pass
    else:
        firstboot = True
    main()
