The [[User Interface (UI)]] and [[Admin Interface]] are both Web Apps. This basically means a website that acts as an app.

The web interfaces keep in touch with the [[KioskMain.py]] by sending HTTP requests. An HTTP request is basically a call and response function, where the client requests something, and awaits a response from the server.

In the JavaScript code of both is a function called `sendData()`. Let's break down one of the most common requests that happens between the web interfaces and the server: a routine [[ping]]

`sendData('Ping,')` will send an HTTP request to the server, with the string "`Ping,`"

In python, it 