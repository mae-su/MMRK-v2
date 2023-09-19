end = "\033[0m" 
homecursor = "\033[H"
clearscreen = "\033[J"
screenf = redwhite + homecursor + clearscreen
bold = "\033[1m"
unbold = "\033[22m"
ul = "\033[4m"
unul = "\033[24m"
boldul = bold + ul
unboldul = unbold + unul #undoes bold and underline

redwhite = "\033[25;33;49m" # red text with white background