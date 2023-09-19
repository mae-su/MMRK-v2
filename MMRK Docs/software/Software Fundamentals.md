First of all, let's run through the basic functions of the kiosk software.

[[User Interface (UI)]]
- Students enter a 5-digit code of their own
- If the 5-digit code matches a student in the system, continue to a machine selection screen
- Once machines are selected, unlock the machine room. This is handed off to the **Hardware Agent.**

Admin Interface
- Allows Mr. Seibert to:
	- Manage who has access to the machine room
		- Manage which machines students have access to
	- Close down the machine room, denying access to all.
	- View logs of who entered when and what machines they used
	- Manually unlock the machine room from his laptop.

Python Server (`KioskMain.py`)
- Manage users in JSON files
- Process requests for when a web resource is requested
	- Prevent unauthorized access to files that aren't in allowed directories
	- For example:
		- If `/ui/index.html` is requested by a browser, return that file
		- If `/backend/logs.json` is requested by a browser, don't return the file
			- ~~Instead, rickroll them in the process~~
- Respond to routine pings from the admin interface and user interface, checking if the machine room has been closed or for status updates

Hardware Agent (`KioskHardwareAgent.py`)
- Manage the unlocker servo
	- When the machine room needs to be unlocked:
		- Swipe the card out
		- Wait a predefined delay
		- Retract the card
		- Turn off the servo (otherwise, the servo **will overheat!**)
- Respond to requests on a WebSocket to start the unlocking routine above
- Monitor temperatures and adjust the fan speed accordingly