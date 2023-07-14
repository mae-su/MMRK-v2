#!/bin/sh
killall python
python KioskMain.py &
python KioskHardwareAgent.py &
chromium-browser http://localhost:8080/ui/ &
