var ID = ""
var signInUnlock = false
var entryDenied = false
var errorState = false
var logScreen = false
var managerOpen = false
var closed = false
var selected = []
var displaytimer = 0
var searchquery = ""

function getElement(s){
  return document.getElementById(s)
}
function setDocProperty(p,v){
  document.documentElement.style.setProperty(p,v)
}
function rmBodyClass(c){
  if(typeof c === 'string' || c instanceof String){
    document.body.classList.remove(c)
  }
  else{
    for (const i in c) {
      document.body.classList.remove(c[i])
    }
  }
}

function addBodyClass(c){
  if(typeof c === 'string' || c instanceof String){
    document.body.classList.add(c)
  }
  else{
    for (const i in c) {
      document.body.classList.add(c[i])
    }
  }
}

setDocProperty("--bordercolor", "hsla(54, 0%, 60%,80%)");
var teleporturl = ""
if(window.location.href.includes(":5500")){
  teleporturl = window.location.href.split(":5500")[0] + ":8080/teleport"; //automatically reconstructs the server URL if the admin url is through a Five Server environment
} else{
  teleporturl = window.location.href.split("/admin")[0] + "/teleport";
}
setInterval(function() {
  sendData("Ping,");
}, 500);

document.addEventListener("keypress", function onPress(event) {
  if (!signInUnlock) {
    if (!isNaN(event.key)){
      key(parseInt(event.key)); 
    }  
  } else if(logScreen){
    setTimeout(function () {
    sendData('DumpJSON;' + getElement('searchBar').value);
  },50)
}
});

document.addEventListener('keydown', function(event) {
  if (event.key === 'Escape' && document.documentElement.classList != "_default _defaultInteractable") {
    if(logScreen){
      logScreen = false;
      rmBodyClass('logScreen');
      addBodyClass('home');
    }
    
  }else if(logScreen && searchquery != getElement('searchBar').value && event.key ==='Backspace'){
    searchquery = getElement('searchBar').value;
      sendData('DumpJSON;' + searchquery);
  }
});

function borderStep(step){
  switch (step){
  case -1:
    getElement("buttonDecorator").style.clipPath = "polygon(0 100%, 0 100%, 100% 100%, 0% 100%)";
    break;
  case 0:
    getElement("buttonDecorator").style.clipPath = "polygon(0 100%, 0 0%, 0% 0%, 0% 100%)";
    break
  case 1:
    setDocProperty("--bordercolor", "#f4e136");
    rmBodyClass('welcome');
    addBodyClass('idscreen');
    getElement("buttonDecorator").style.clipPath = "polygon(0 0, 0 0, 22% 100%, 0% 100%)";
    break;
  case 2:
    getElement("buttonDecorator").style.clipPath = "polygon(0 0, 20% 0, 20% 100%, 0% 100%)";
    break
  case 3:
  getElement("buttonDecorator").style.clipPath = "polygon(0 0, 44% 0, 44% 100%, 0% 100%)";
    break
  case 4:
    getElement("buttonDecorator").style.clipPath = "polygon(0 0, 66% 0, 66% 100%, 0% 100%)";
    break
  case 5:
    getElement("buttonDecorator").style.clipPath = "polygon(0 0, 100% 0, 100% 100%, 0% 100%)";
    break
  }
}

function updateDots(first=false){
  var s = "";
  if(ID.length == 0){
    s = "_ _ _ _ _"
  } else{
    borderStep(ID.length)
  }
    if(first){
      borderStep(-1)
    }
  if(ID.length == 1){
        s = "* _ _ _ _"
    }
    if(ID.length == 2){
        s = "* * _ _ _"
    }
    if(ID.length == 3){
      s = "* * * _ _"
    }
    if(ID.length == 4){
        s = "* * * * _"
    }
    if(ID.length == 5){
      s = "* * * * *"
    }
    getElement("subtext").innerText = s
}
function del(){
    ID = ID.slice(0,ID.length - 1)
    updateDots()
}

function key(k){

    if(ID.length < 6){
        ID = ID + k
        updateDots()
    }
    if(ID.length == 5){
      sendData("SignInReq;" + ID)
    }
}

function lockdownbutton(){
  sendData("ToggleEntry;")
  sendData("Ping,");
}

function manualunlockbutton(){
  sendData("Manual;");
  setDocProperty("--shadowmult", "0.1");
  getElement("manualUnlock").style.opacity = "0.5";
  setTimeout(function () {
    // setDocProperty("--shadowmult", "1");
    setTimeout(function () {
      setDocProperty("--shadowmult", "1");
      
    }, 150);
    getElement("manualUnlock").style.opacity = "1";
  }, 400);
}

function resetScreen(){
  setDocProperty("--bordercolor", "hsl(54, 0%, 65%)");
  rmBodyClass(['idscreen','screen2',"closed","home"]);
  addBodyClass('welcome');
  getElement("latest").style.opacity = 0;
  getElement("signInText").innerText = "sign in";
  getElement("text").innerText = "welcome back."
  getElement("subtext").innerText = "please sign in.";
  signInUnlock=false;
  ID = ""
  // entryDenied = false;
}
function signInButton(){
  if(!errorState){
      sendData("Ping,");
      setDocProperty("--bordercolor", "#f4e136");
      rmBodyClass('welcome');addBodyClass('idscreen');
      updateDots(true)
    
  }
}

function signedIn(){
  setInterval(function() {
    sendData("Latest;");
  }, 1000);
}

function userManager(){
  managerOpen = true
  sendData("UIDManager;");
  addBodyClass('managerOpen')
  window.open(teleporturl.split(":8080")[0] + ":4196/upload/", '_blank');
}

function parsejson(){
  logScreen = true;
  fetch('data.json')
  .then(response => response.json())
  .then(data => {
    // Get the 'entries' div element
    console.log(data)
    const entriesDiv = getElement('log');
    entriesDiv.innerHTML = ""
    var i = 0
    // Iterate over each entry in the JSON data
    for (const timestamp in data) {
      const entry = data[timestamp];
      i = i + 1
      // Create an HTML element to display the entry
      const entryElement = document.createElement('div');
      entryElement.className = 'logEntry';

      // Create a heading element for the timestamp
      const timestampHeading = document.createElement('span');
      timestampHeading.textContent = ((new Date(parseFloat(timestamp) * 1000).toLocaleString("en-US",{weekday: "short", month: "long", day: "numeric", year: "numeric"})).split(", 20")[0]) + " at " + (new Date(parseFloat(timestamp) * 1000).toLocaleTimeString("en-US"));
      entryElement.appendChild(timestampHeading);
      
      const machines = entry.machines.join(', ')
      const whoSignedIn = document.createElement('p');
      if(machines.length == 0){
        whoSignedIn.textContent = entry.name + " signed in without selecting any machines.";
      } else{
        whoSignedIn.textContent = entry.name + " signed in and used: " + entry.machines.join(', ');
      }
      entryElement.appendChild(whoSignedIn);

      // entryElement.appendChild(machinesParagraph);

      // Append the entry element to the 'entries' div
      if(entry.include != "false"){
        entriesDiv.appendChild(entryElement);
      }
    }
  console.log("Rendered " + String(i) + " entries.")
  rmBodyClass('home');
  addBodyClass('logScreen');
  
})
  .catch(error => console.error(error));
}

function sendData(data) {
  data = "%" + data //adds the necessary modifier to all commands before sending
    var xhr = new XMLHttpRequest();
    xhr.open('POST', teleporturl, true); // Modify the URL as per your server configuration
    
    // Set the appropriate headers if you need to send data other than plain text
    // xhr.setRequestHeader('Content-Type', 'application/json');
    // xhr.setRequestHeader('Authorization', 'Bearer myToken');

    xhr.onreadystatechange = function() {
      if (xhr.readyState === XMLHttpRequest.DONE) {
        if (xhr.status === 200) {
          
          resp = String(xhr.responseText.trim()) //removes the request header.
          if(String(resp).includes('%')){
            resp = resp.replace('%','')
           
            console.log('Received POST data: ' + resp); //process received responses here
            
            if(resp.includes("Authorize")){
              var set = resp.split(";")
              getElement("signInText").innerText = "signing in..."
              addBodyClass('screen2');
              rmBodyClass('idscreen');
              signInUnlock = true;
              setDocProperty("--bordercolor", "#00BB00");
              setTimeout(function () {
                addBodyClass('home');
                signedIn()
              }, 1000);
            }
            if(resp.includes("Latest;")){
              displaytimer = 6
              var latest = resp.split(";")[1];
              getElement("latest").style.opacity = 0;
              setTimeout(function () {
                getElement("latest").innerText = latest;
              }, 400);
              setTimeout(function () {
                getElement("latest").style.opacity = 0.85;
              }, 800);
            } 
            else if(resp.includes("Latest")){
              if(displaytimer == 0){
                displaytimer = -1;
                getElement("latest").style.opacity = 0;
                setTimeout(function () {
                  if(entryDenied){
                    getElement("latest").innerText = "Machine room closed.";
                  } else{
                    getElement("latest").innerText = "Kiosk is running.";
                  }
                }, 500);
                setTimeout(function () {
                  getElement("latest").style.opacity = 0.85;
                }, 1000);
              } else if(displaytimer>0){
                displaytimer = displaytimer - 1
              }
            }
            
            if(resp == "Incorrect"){
              setDocProperty("--bordercolor", "red");
              setTimeout(function () {
                setDocProperty("--bordercolor", "#f4e136")
              }, 250);
              ID = ""
              updateDots()
            }
            if(resp.includes("DumpedJSON;")){
              parsejson()
            }
            if(resp.includes("entryDenied")){
              if(errorState){
                location.reload()
              }
              if(!entryDenied){
                entryDenied = true;
                
                addBodyClass("closed");
                displaytimer = 0;
                // setDocProperty("--bordercolor", "red");
              }
            }
            if(resp.includes("entryAllowed")){
              if(errorState){
                location.reload()
              }
              if(entryDenied){
                
                rmBodyClass("closed");
                entryDenied = false;
                displaytimer = 0;
              }
              
            }
            // if(resp.includes("ping")){
            //   if(entryDenied){
            //     entryDenied = false;
            //     resetScreen();
            //   }
              
            // }

        } 
        }
        else {
          if(!errorState){
            errorState = true;
            resetScreen();
            // getElement("signInText").innerText = "the backend is offline. please restart.";
            setDocProperty("--bordercolor", "darkred");
            getElement("text").innerText = "the kiosk backend did not serve a proper response.";
            getElement("subtext").innerText = "please restart the kiosk, verify its wifi connection, or debug the backend: kill all python scripts and execute from terminal."
            getElement("signInText").innerText = ""
            
          }
          console.error('Error:', xhr.status);
        }
      }
    };
    xhr.send(data);
  }