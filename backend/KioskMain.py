import json
import os
import subprocess
import sys
from collections import OrderedDict
from datetime import datetime
#from selenium import webdriver
from src import cardswipe, jsonHelper
from src.consoleColors import * # useful console formatting variables here!
from twisted.internet import endpoints, reactor
from twisted.internet.protocol import Factory, Protocol
from twisted.protocols.basic import LineReceiver
from twisted.web import resource, server, static
logJSONData = {}
permissionsJSONData = {}
latestSignIns = []

dir = "./data/"  # This is where files will be stored on the pi.
firstboot = False
kioskIP = "127.0.0.1"

def entry(b=None):
  if b is None:
    j = jsonHelper.getJson(dir + "secrets.json")["entryDenied"]
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

class Simple(resource.Resource):
    '''Simple webserver'''
    isLeaf = True
    def getChild(self, path, request):
        if path == b"":
            return self
        return resource.Resource.getChild(self, path, request)
    
    def render_GET(self, request):
        '''When a browser requests a file, the URL is passed in here.'''
        file_path = "none"
        if request.path == b"./" or request.path == b"/" or request.path == b"." or request.path == b"":
            file_path = b"./ui/index.html"
        elif request.path == b"/ui/":
          file_path = b"./ui/index.html"
        elif b"/ui/" in request.path:
          file_path = b"./ui/" + str(request.path.decode()).replace("/ui/","").encode()
        elif request.path == b"/logjam.json":
            file_path = b"./data/log.json"
        
        #this next part is literally just rickroll resources
        elif b"secrets" in request.path:
            file_path = b"./fse/dne.html" 
        elif b"tryharder" in request.path:
            file_path = b"./fse/rick.mp4"
        elif b"yadonegoofed" in request.path:
            file_path = b"./fse/styles.min.css"
        
        elif request.path == b"/admin/":
            file_path = b"./admin/index.html"
        elif b"/admin/" in request.path:
          file_path = b"./admin/" + str(request.path.decode()).replace("/admin/","").encode()
        elif b"favicon.ico" in request.path:
            file_path = b"./admin/favicon.ico"
        elif file_path == "none":
            file_path = b"./fse/dne.html"
        print("\x1b[3m\x1b[90m" + str(request.path).replace("b","") + " served as " + str(file_path).replace("b","") + end)
        return static.File(file_path).getContent()
        


    def render_POST(self, request):
        request.setHeader(b"Access-Control-Allow-Origin", b"*")
        content = str(request.content.read().decode("utf-8"))
        
        
        if content.startswith("%"):
            resp = self.adminPostHandler(content.strip("%"))
            if True:
                print("[Admin] " + content.strip("%") + " --> " + str(resp))
            return str("%" + str(resp)).encode()
        elif content.startswith("+"):
            resp = self.UIPostHandler(content.strip("+"))
            if True:
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
            return "Incorrect"
          else:
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
            return str("Ipaddr;" + subprocess.getoutput("hostname -I"))  # send IP address
        else:
            return "OK"  # Return a response to the client
    
    def adminPostHandler(self, content):
        global logJSONData
        global permissionsJSONData
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
        if "Manual;" in content:
            try:
                if debug:
                    print("[DEBUG] Card swipe called.")
                    return "Latest;Manually unlocked."
                else:
                    cardswipe.main(IP=kioskIP)
                    return "Latest;Manually unlocked."
            except:
                return "Latest;A hardware agent error occured."
        if "ToggleEntry;" in content:
          if entry():
            entry(False)
            return "Machine room closed."
          else:
            entry(True)
            return "Machine room open."
        if "LogData;Dump;" in content:
            returnall = "LogData;Dump;" == content
            if not returnall:
                query = content.split(";")[2].lower()
                
            else:
                logJSONData = OrderedDict(reversed(list(jsonHelper.getJson(dir + "log.json").items())))
                permissionsJSONData = jsonHelper.getJson(dir + "permissions.json")
                print("[MMRKV2] Data reloaded.")
            startTime = datetime.now()
            
            

            for key, value in logJSONData.items():
                try:
                    permissions = permissionsJSONData.get(value["ID"])
                    if permissions:
                        name = permissions['firstname'] + " " + permissions['lastname']
                        value["name"] = name
                        
                        if not returnall:
                            if query.isNumeric(): 
                                if query in str(value["machines"]):
                                    value["include"] = "true"
                            else:
                                if query.lower() in name.lower():
                                    value["include"] = "true"
                                else: value["include"] = "false"
                        else:
                            value["include"] = "true"
                    else:
                        value["include"] = "false"
                except:
                    value["include"] = "false"

            endTime = datetime.now()
            execTime = endTime - startTime
            jsonHelper.setJson(dir + "../admin/buffer.json", logJSONData)
            print("[MMRKV2] Log data dumped to admin buffer in " + str(execTime.total_seconds()*1000) + " milliseconds.")
            return "DumpedLogJSON;"
        
        if "PermissionsManager;Dump" in content:
            jsonHelper.setJson(dir + "../admin/buffer.json", jsonHelper.getJson(dir + "permissions.json"))
            print("[MMRKV2] Permissions data dumped to admin buffer.")
            return "Latest;Downloading..."
        if "PermissionsManager;Scrub" in content:
            jsonHelper.setJson(dir + "../admin/buffer.json", {})
            print("[MMRKV2] Permissions data scrubbed from admin buffer.")
            return "Latest;Opening VSCode..."
        if "SetSecret;" in content:
            secrets = jsonHelper.getJson(dir + "secrets.json")
            key = content.split(";")[1]
            value = content.split(";")[2]
            secrets[key] = value
            return "Latest;" + key + " has been set."
        if "PermissionsManager;Open," in content:
            return "VSCode;" + jsonHelper.getJson(dir + "secrets.json")["downloadPath"] + content.split(",")[1]
        if "PermissionsManager;Inject;" in content:
            try: data = json.loads(content.split(";")[2])
            except json.JSONDecodeError: return "Error: "
            print(data)
            if not data:
                return "Latest;Error: Empty JSON was refused."
            for key, value in data.items():
                if not key.isdigit():
                    return "Latest;Error: One or more IDs were not numeric:\n" + key
                if not len(key) == 5:
                    return "Latest;Error: This ID is not five digits long:\n" + key
                if not isinstance(value, dict):
                    return "Latest;Error in ID " + key + ": Fields are incorrectly formatted."
                
                required_fields = {"firstname", "lastname", "machines"}
                if not set(value.keys()) == required_fields:
                    return "Latest;Error in ID " + key + ": This ID does not contain the right fields.\n(\"firstname\",\"lastname\",\"machines\")"
                if not isinstance(value["machines"], list):
                    return "Latest;Error in ID " + key + ": This ID does not contain a list of machines.\n(square brackets - the list can be left empty)"
            print("[MMRKV2] Permissions data injected from admin app.")
            try:
                jsonHelper.setJson(dir + "permissions.json",data)
            except:
                return "Latest;Permissions were received successfully,\nbut an error occured writing to storage."
            return "Latest;Permissions have been updated."    
def main():
    try:
        if not os.path.exists(dir):
            install(print)
    except:
        install(print)
    print("[MMRKV2] Kiosk is starting...")
    f = Factory()
    site = server.Site(Simple())
    endpoint = endpoints.TCP4ServerEndpoint(reactor, 8080)
    endpoint.listen(site)
    reactor.listenTCP(8000, f)
    print("[MMRKV2] Kiosk UI is running at: http://localhost:8080/ui/")
    print("[MMRKV2] Admin UI is running at: http://localhost:8080/admin/")
    try:
        command = "chromium-browser http://localhost:8080/ui/ --kiosk"
        subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[MMRKV2] Kiosk UI opened successfully.")
    except:
        print("[MMRKV2] An error occurred while opening the UI on the kiosk. Please open the UI manually.")
    try:
        subprocess.Popen(['python', '/home/pi/MMRK-V2/backend/KioskHardwareAgent.py'])
    except:
      print("[MMRKV2] An error occurred while launching the hardware agent on the kiosk. Please launch it manually.")
    reactor.run()


def install(out):
    def selfout(s):
        out("[MMRKV2 Installer] " + s)
    selfout("Installing directory at: " + dir)
    try:
        os.mkdir(dir)
    except Exception as e:
        selfout("Failed to create storage directory. \n" + str(e))

    try:
        selfout("Creating JSONs: ")
        jsonHelper.createJSON(dir + "log.json")
        jsonHelper.createJSON(dir + "permissions.json")
        jsonHelper.createJSON(dir + "secrets.json")
        selfout("Done.")
        selfout("Writing format to secrets.json with defaults:")
        j = jsonHelper.getJson(dir + "secrets.json")
        j["entryDenied"] = str(False)
        selfout("'entryDenied' : 'False'  |  Kiosk is currently accepting entry.")
        j["authcode"] = "00000"
        selfout("'authcode':'00000'  |  Admin PIN is currently 00000.")
        j["downloadPath"] = ""
        selfout("'downloadPath':''  |  Download path is currently unset.")
        jsonHelper.setJson(dir + "secrets.json",j)
        

    except Exception as e:
        selfout("Failed to create JSONs. \n" + str(e))
    selfout("Success! Please set a five digit admin PIN and downloadPath in secrets.json.")

def log(ID, machines):
    logdata = jsonHelper.getJson(dir + "log.json")
    logdata [datetime.now().timestamp()] = {
        "ID":ID,
        "machines":machines
    }
    jsonHelper.setJson(dir + "log.json",logdata)

def getName(data,ID):
    if ID in data:
      
      return data[ID]['firstname'] + " " + data[ID]['lastname']
def checkID(ID):
    permissions = jsonHelper.getJson(dir + "permissions.json")
    if ID in permissions:
      
      return [permissions[ID]['firstname'],permissions[ID]['machines']]
    else:
      return ["Incorrect"]

if __name__ == "__main__":
    # Change this before debugging, unless you run the program with the --debug flag.
    debug = False

    if debug or "--debug" in sys.argv:
        import os
        dir = "./data/"
        kioskIP = "192.168.86.80"
    main()
