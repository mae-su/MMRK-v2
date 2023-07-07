var ID = ""
var signInUnlock = false
var entryDenied = false
var errorState = false
var closed = false
var selected = []
var displaytimer = 0
document.documentElement.style.setProperty("--bordercolor", "hsla(54, 0%, 60%,80%)");
setInterval(function() {
  sendData("Ping,");
}, 500);



document.addEventListener("keypress", function onPress(event) {
  if (!signInUnlock) {
    if (!isNaN(event.key)){
      key(parseInt(event.key)); 
    } else{
      del()
    }
  }
});
function borderStep(step){
  if (step==-1){
    document.getElementById("buttonDecorator").style.clipPath = "polygon(0 100%, 0 100%, 100% 100%, 0% 100%)";
  }
  if(step==0){
    document.getElementById("buttonDecorator").style.clipPath = "polygon(0 100%, 0 0%, 0% 0%, 0% 100%)";
  }
  if(step==1){
    document.documentElement.style.setProperty("--bordercolor", "#f4e136");
    document.body.classList.remove('welcome');
    document.body.classList.add('idscreen');
    document.getElementById("buttonDecorator").style.clipPath = "polygon(0 0, 0 0, 22% 100%, 0% 100%)";
  }
  if(step==2){
    document.getElementById("buttonDecorator").style.clipPath = "polygon(0 0, 20% 0, 20% 100%, 0% 100%)";
  }
  if(step==3){
    document.getElementById("buttonDecorator").style.clipPath = "polygon(0 0, 44% 0, 44% 100%, 0% 100%)";
    }
    if(step==4){
      document.getElementById("buttonDecorator").style.clipPath = "polygon(0 0, 66% 0, 66% 100%, 0% 100%)";
    }
    if(step==5){
      document.getElementById("buttonDecorator").style.clipPath = "polygon(0 0, 100% 0, 100% 100%, 0% 100%)";
    }
}

function updateDots(first=false){
  var s = "";
    if(first){
      borderStep(-1)
    }
    if(ID.length == 0){
        s = "_ _ _ _ _"
    }
    if(ID.length == 1){
      borderStep(1)
        s = "* _ _ _ _"
    }
    if(ID.length == 2){
      borderStep(2)
        s = "* * _ _ _"
    }
    if(ID.length == 3){
      borderStep(3)
      s = "* * * _ _"
    }
    if(ID.length == 4){
      borderStep(4)
        s = "* * * * _"
    }
    if(ID.length == 5){
      borderStep(5)
      s = "* * * * *"
    }
    document.getElementById("subtext").innerText = s
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

function resetScreen(){
  document.documentElement.style.setProperty("--bordercolor", "hsl(54, 0%, 65%)");
  document.body.classList.remove('idscreen');
  document.body.classList.remove('screen2');
  document.body.classList.remove("closed");
  document.body.classList.add('welcome');
  document.getElementById("signInText").innerText = "sign in";
  document.getElementById("text").innerText = "welcome back."
  document.getElementById("subtext").innerText = "please sign in.";
  signInUnlock=false;
  ID = ""
  // entryDenied = false;
}
function signInButton(){
  if(!errorState){
      sendData("Ping,");
      document.documentElement.style.setProperty("--bordercolor", "#f4e136");
      document.body.classList.remove('welcome');document.body.classList.add('idscreen');
      updateDots(true)
    
  }
}

function signedIn(){
  setInterval(function() {
    sendData("Latest;");
  }, 1000);
}

function sendData(data) {
  data = "%" + data //adds the necessary modifier to all commands before sending
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://192.168.0.30:8080/teleport', true); // Modify the URL as per your server configuration
    
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
              document.getElementById("signInText").innerText = "signing in..."
              document.body.classList.add('screen2');
              document.body.classList.remove('idscreen');
              signInUnlock = true;
              document.documentElement.style.setProperty("--bordercolor", "#00BB00");
              setTimeout(function () {
                document.body.classList.add('home');
                signedIn()
              }, 1000);
            }
            if(resp.includes("Latest;")){
              displaytimer = 6
              var latest = resp.split(";")[1];
              document.getElementById("latest").style.opacity = 0;
              setTimeout(function () {
                document.getElementById("latest").innerText = latest;
              }, 500);
              setTimeout(function () {
                document.getElementById("latest").style.opacity = 0.85;
              }, 1000);
            } 
            else if(resp.includes("Latest")){
              if(displaytimer == 0){
                displaytimer = -1;
                document.getElementById("latest").style.opacity = 0;
                setTimeout(function () {
                  if(entryDenied){
                    document.getElementById("latest").innerText = "Machine room closed.";
                  } else{
                    document.getElementById("latest").innerText = "Kiosk is running.";
                  }
                }, 500);
                setTimeout(function () {
                  document.getElementById("latest").style.opacity = 0.85;
                }, 1000);
              } else if(displaytimer>0){
                displaytimer = displaytimer - 1
              }
            }
            
            if(resp == "Incorrect"){
              document.documentElement.style.setProperty("--bordercolor", "red");
              setTimeout(function () {
                document.documentElement.style.setProperty("--bordercolor", "#f4e136")
              }, 250);
              ID = ""
              updateDots()
            }

            if(resp.includes("entryDenied")){
              if(errorState){
                resetScreen();
                errorState = false;
              }
              if(!entryDenied){
                entryDenied = true;
                
                document.body.classList.add("closed");
                displaytimer = 0;
                // document.documentElement.style.setProperty("--bordercolor", "red");
              }
            }
            if(resp.includes("entryAllowed")){
              if(errorState){
                resetScreen();
                errorState = false;
              }
              if(entryDenied){
                
                document.body.classList.remove("closed");
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
            // document.getElementById("signInText").innerText = "the backend is offline. please restart.";
            document.documentElement.style.setProperty("--bordercolor", "darkred");
            document.getElementById("text").innerText = "the kiosk backend did not serve a proper response.";
            document.getElementById("subtext").innerText = "please restart the kiosk, verify its wifi connection, or debug the backend: kill all python scripts and execute from terminal."
            document.getElementById("signInText").innerText = ""
            
          }
          console.error('Error:', xhr.status);
        }
      }
    };
    xhr.send(data);
  }