var ID = "";
var signInUnlock = false;
var entryDenied = false;
var errorState = false;
var selected = [];
var teleporturl = "";

function idleTimeout() {
  const timeoutDuration = 15000;
  let timeout;

  const resetTimer = () => {
    clearTimeout(timeout);
    timeout = setTimeout(resetScreen, timeoutDuration);
  };

  window.onload = window.onmousemove = window.onmousedown = window.ontouchstart = window.ontouchmove = window.onclick = window.onkeydown = window.addEventListener('scroll', resetTimer, true);

  function yourFunction() {
    resetScreen();
  }

  resetTimer();
}

idleTimeout();

if (window.location.href.includes(":5500")) {
  teleporturl = window.location.href.split(":5500")[0] + ":8080/teleport";
} else {
  teleporturl = window.location.href.split("/ui")[0] + "/teleport";
}

document.documentElement.style.setProperty("--bordercolor", "hsla(54, 0%, 60%, 80%)");

setInterval(function () {
  sendData("Ping,");
}, 1000);

function borderStep(step) {
  const buttonDecorator = document.getElementById("buttonDecorator");
  const steps = [
    "0 100%, 22 0%, 0% 0%, 0% 100%",
    "0 0, 0 0, 22% 100%, 0% 100%",
    "0 0, 20% 0, 20% 100%, 0% 100%",
    "0 0, 44% 0, 44% 100%, 0% 100%",
    "0 0, 66% 0, 66% 100%, 0% 100%",
    "0 0, 100% 0, 100% 100%, 0% 100%"
  ];
  console.log(step)
  buttonDecorator.style.clipPath = `polygon(${steps[step]})`;
}

function updateDots(first = false) {
  const dotCount = Math.min(ID.length, 5);
  borderStep(dotCount);
  const dots = Array(5).fill("*").fill("_", dotCount);
  document.getElementById("subtext").innerText = dots.join(" ");
}

function del() {
  ID = ID.slice(0, ID.length - 1);
  updateDots();
}

function signInButton() {
  if (!entryDenied && !errorState) {
    if (signInUnlock) {
      if (selected.length == 0) {
        document.documentElement.style.setProperty("--bordercolor", "red");
        setTimeout(function () {
          document.documentElement.style.setProperty("--bordercolor", "darkgrey");
        }, 250);
      } else {
        sendData("Unlock;" + ID + ";" + selected.toString());
        selected = [];
        resetScreen();
      }
    } else {
      sendData("Ping");
      document.documentElement.style.setProperty("--bordercolor", "#f4e136");
      document.body.classList.remove('welcome');
      document.body.classList.add('idscreen');
      updateDots(true);
    }
  }
}

function key(k) {
  if (ID.length < 6) {
    ID += k;
    updateDots();
  }
  if (ID.length === 5) {
    sendData("SignInReq;" + ID);
  }
}

function machineButton(i, d) {
  const buttonElement = document.getElementById(i);
  const backgroundColor = buttonElement.style.backgroundColor;
  const selectedColor = "#f4e136";
  const deselectedColor = "#00000060";
  
  if (backgroundColor === selectedColor || backgroundColor === "" || backgroundColor === "rgba(0, 0, 0, 0.376)") {
    buttonElement.style.backgroundColor = selectedColor;
    selected.push(d);
    document.documentElement.style.setProperty("--bordercolor", "#00FF00");
    console.log(selected);
  } else {
    selected = selected.filter(machine => machine !== d);
    console.log(selected);
    
    if (selected.length === 0) {
      document.documentElement.style.setProperty("--bordercolor", "darkgrey");
    }
    
    buttonElement.style.backgroundColor = deselectedColor;
  }
}

function resetScreen() {
  const bodyClassList = document.body.classList;
  const signInTextElement = document.getElementById("signInText");
  const textElement = document.getElementById("text");
  const subtextElement = document.getElementById("subtext");

  document.documentElement.style.setProperty("--bordercolor", "hsl(54, 0%, 65%)");
  bodyClassList.remove('idscreen', 'screen2');
  bodyClassList.add('welcome');

  signInTextElement.innerText = "sign in";
  textElement.innerText = "welcome back.";
  subtextElement.innerText = "please sign in.";

  signInUnlock = false;
  ID = "";
}

function sendData(data) {
  data = "+" + data;
  var xhr = new XMLHttpRequest();
  xhr.open('POST', teleporturl, true);
  xhr.onreadystatechange = function () {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      if (xhr.status === 200) {
        var resp = xhr.responseText.trim();
        if (resp.includes('+')) {
          resp = resp.replace('+', '');
          console.log('Server --> Self: ' + resp);
          if (resp.includes("Authorize")) {
            var set = resp.split(";");
            var name = set[1];
            var machines = set.slice(2);
            document.getElementById("machineList").innerHTML = "";
            for (const element of machines) {
              var identifier = element.replace(" ", "");
              document.getElementById("machineList").innerHTML +=
                '<span class="mListItem" id="' +
                identifier +
                'Button" onclick="machineButton(\'' +
                identifier +
                'Button\',\'' +
                element +
                '\')">' +
                element +
                '</span> ';
            }
            document.getElementById("text").innerText = "welcome, " + name.toLowerCase() + ".";
            document.getElementById("subtext").innerText = "please select your machines.";
            document.getElementById("signInText").innerText = "unlock";
            document.body.classList.add('screen2');
            document.body.classList.remove('idscreen');
            document.documentElement.style.setProperty("--bordercolor", "darkgrey");
            signInUnlock = true;
          }

          if (resp == "Incorrect") {
            document.documentElement.style.setProperty("--bordercolor", "red");
            setTimeout(function () {
              document.documentElement.style.setProperty("--bordercolor", "#f4e136");
            }, 250);
            ID = "";
            updateDots();
          }
          if (resp.includes("Ipaddr;")) {
            var old = document.getElementById("signInText").innerText;
            document.getElementById("signInText").innerText = "http://" + resp.split(";")[1] + ":8080/admin/";
            setTimeout(function () {
              document.getElementById("signInText").style.fontStyle = "";
              document.getElementById("signInText").style.fontWeight = 400;
              document.getElementById("signInText").innerText = old;
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
      } else {
        if (!errorState) {
          errorState = true;
          resetScreen();
          document.documentElement.style.setProperty("--bordercolor", "darkred");
          document.getElementById("text").innerText = "internal error :(";
          document.getElementById("subtext").innerText = "the backend is not running.\nplease restart.";
        }
        console.error('Error:', xhr.status);
      }
    }
  };
  xhr.send(data);
}

