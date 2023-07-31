var ID = ""
var signInUnlock = false
var entryDenied = false
var errorState = false
var selected = []
var teleporturl = ""

if (window.location.href.includes(":5500")) {
  teleporturl = window.location.href.split(":5500")[0] + ":8080/teleport"; //automatically reconstructs the server URL if the admin url is through a Five Server environment
} else {

  teleporturl = window.location.href.split("/ui")[0] + "/teleport";
}
document.documentElement.style.setProperty("--bordercolor", "hsla(54, 0%, 60%,80%)");
setInterval(function () {
  sendData("Ping,");
}, 1000);

function borderStep(step) {
  if (step == -1) {
    document.getElementById("buttonDecorator").style.clipPath = "polygon(0 100%, 0 100%, 100% 100%, 0% 100%)";
  }
  if (step == 0) {
    document.getElementById("buttonDecorator").style.clipPath = "polygon(0 100%, 0 0%, 0% 0%, 0% 100%)";
  }
  if (step == 1) {
    document.getElementById("buttonDecorator").style.clipPath = "polygon(0 0, 0 0, 22% 100%, 0% 100%)";
  }
  if (step == 2) {
    document.getElementById("buttonDecorator").style.clipPath = "polygon(0 0, 20% 0, 20% 100%, 0% 100%)";
  }
  if (step == 3) {
    document.getElementById("buttonDecorator").style.clipPath = "polygon(0 0, 44% 0, 44% 100%, 0% 100%)";
  }
  if (step == 4) {
    document.getElementById("buttonDecorator").style.clipPath = "polygon(0 0, 66% 0, 66% 100%, 0% 100%)";
  }
  if (step == 5) {
    document.getElementById("buttonDecorator").style.clipPath = "polygon(0 0, 100% 0, 100% 100%, 0% 100%)";
  }
}

function updateDots(first = false) {
  var s = "";
  switch (ID.length) {
    case 0:
      s = "_ _ _ _ _";
      break;
    case 1:
      borderStep(1);
      s = "* _ _ _ _";
      break;
    case 2:
      borderStep(2);
      s = "* * _ _ _";
      break;
    case 3:
      borderStep(3);
      s = "* * * _ _";
      break;
    case 4:
      borderStep(4);
      s = "* * * * _";
      break;
    case 5:
      borderStep(5);
      s = "* * * * *";
      break;
  }
  document.getElementById("subtext").innerText = s
}
function del() {
  ID = ID.slice(0, ID.length - 1)
  updateDots()
}

function key(k) {
  if (ID.length < 6) {
    ID = ID + k
    updateDots()
  }
  if (ID.length == 5) {
    sendData("SignInReq;" + ID)
  }
}



function resetScreen() {
  document.documentElement.style.setProperty("--bordercolor", "hsl(54, 0%, 65%)");
  document.body.classList.remove('idscreen');
  document.body.classList.remove('screen2');
  document.body.classList.add('welcome');
  document.getElementById("signInText").innerText = "sign in";
  document.getElementById("text").innerText = "welcome back."
  document.getElementById("subtext").innerText = "please sign in.";
  signInUnlock = false;
  ID = ""
}
function signInButton() {
  if (!entryDenied && !errorState) {
    if (signInUnlock) {
      sendData("Unlock;" + ID + ";" + selected.toString());
      selected = [];
      resetScreen()

    } else {
      sendData("Ping");
      document.documentElement.style.setProperty("--bordercolor", "#f4e136");
      document.body.classList.remove('welcome'); document.body.classList.add('idscreen');
      updateDots(true)
    }
  }
}

function machineButton(i, d) {
  if (document.getElementById(i).style.backgroundColor == "#00000060" || document.getElementById(i).style.backgroundColor == "" || document.getElementById(i).style.backgroundColor == "rgba(0, 0, 0, 0.376)") {
    document.getElementById(i).style.backgroundColor = "#f4e136";
    selected.push(d);
    console.log(selected);
  } else {
    selected = selected.filter(function (machine) {
      return machine !== d;
    });

    console.log(selected);
    document.getElementById(i).style.backgroundColor = "#00000060"
  }
}

function sendData(data) {
  data = "+" + data //adds the necessary modifier to all commands before sending 
  var xhr = new XMLHttpRequest();   //** XMLHttpRequests are from stackoverflow!
  xhr.open('POST', teleporturl, true); // Set the appropriate headers if you need to send data other than plain text  xhr.setRequestHeader('Content-Type', 'application/json'); xhr.setRequestHeader('Authorization', 'Bearer myToken');
  xhr.onreadystatechange = function () {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      if (xhr.status === 200) {
        resp = String(xhr.responseText.trim()) //removes the request header. --end complete stackoverflow copypaste
        if (String(resp).includes('+')) {
          resp = resp.replace('+', '')
          console.log('Server --> Self: ' + resp); //process received responses here
          if (resp.includes("Authorize")) {
            var set = resp.split(";")
            var name = String(set[1])
            var machines = set.slice(2)
            document.getElementById("machineList").innerHTML = "";
            for (const element of machines) {
              identifier = String(element).replace(" ", "")
              document.getElementById("machineList").innerHTML = document.getElementById("machineList").innerHTML + '<span class="mListItem" id=\'' + identifier + 'Button\' onclick="machineButton(\'' + identifier + 'Button\',\'' + element + '\')">' + element + '</span> '
            }
            document.getElementById("text").innerText = "welcome, " + name.toLowerCase() + "."
            document.getElementById("subtext").innerText = "please select your machines.";
            document.getElementById("signInText").innerText = "unlock";
            document.body.classList.add('screen2'); document.body.classList.remove('idscreen');
            signInUnlock = true;
          }

          if (resp == "Incorrect") {
            document.documentElement.style.setProperty("--bordercolor", "red");
            setTimeout(function () {
              document.documentElement.style.setProperty("--bordercolor", "#f4e136")
            }, 250);
            ID = ""
            updateDots()
          }
          if (resp.includes("Ipaddr;")) {
            var old = document.getElementById("signInText").innerText
            document.getElementById("signInText").innerText = "http://" + resp.split(";")[1] + ":8080/admin/"
            setTimeout(function () {
              document.getElementById("signInText").style.fontStyle = ""
              document.getElementById("signInText").style.fontWeight = 400
              document.getElementById("signInText").innerText = old
            }, 7000);
          }

          if (resp.includes("entryDenied")) {
            if (errorState) {
              resetScreen();
              errorState = false;
            }
            if (!entryDenied) {
              resetScreen();
              entryDenied = true;
              document.documentElement.style.setProperty("--bordercolor", "red");
              document.getElementById("signInText").innerText = "machine room closed.";
              document.getElementById("text").innerText = "";
              document.getElementById("subtext").innerText = "";
            }
          }
          if (resp.includes("entryAllowed")) {
            if (errorState) {
              resetScreen();
              errorState = false;
            }
            if (entryDenied) {
              entryDenied = false;
              resetScreen();
            }
          }
        }
      }
      else {
        if (!errorState) {
          errorState = true;
          resetScreen();
          document.documentElement.style.setProperty("--bordercolor", "darkred");
          document.getElementById("text").innerText = "internal error :(";
          document.getElementById("subtext").innerText = "the backend is not running.\nplease restart."
        }
        console.error('Error:', xhr.status);
      }
    }
  };
  xhr.send(data);
}