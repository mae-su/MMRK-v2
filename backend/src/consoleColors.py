## This file contains special terminal formatting codes. 
# When you print one of these strings to the console, the terminal handles it as something called an escape code, and any text printed after the escape code will have different formatting.
# You can learn more about escape codes and find more formatting options here: https://learn.microsoft.com/en-us/windows/console/console-virtual-terminal-sequences
# There's even ways to make flashing text in the terminal. You can use escape sequences to beautify a program's console output, calling attention to the important details.

end = "\033[0m"#resets formatting
homecursor = "\033[H" #brings the cursor back to the first character in a line (iirc)
clearscreen = "\033[J" #flushes the console
bold = "\033[1m" #adds bold
unbold = "\033[22m" #removes bold
ul = "\033[4m" #adds underline
unul = "\033[24m" #removes underline
boldul = bold + ul #adds bold and underline
unboldul = unbold + unul #undoes bold and underline
redwhite = "\033[25;33;49m" # red text with white background
screenf = redwhite + homecursor + clearscreen # sets the whole console to a red background/white text environment