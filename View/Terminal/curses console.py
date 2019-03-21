import curses
import time


win_list = []
screen = -1

#Put init stuff here
def init_curses(): 
    global screen
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()


def refresh_screen():
    screen.refresh()
    for win in win_list:
        win.refresh()


def get_text():
    str1 = ""
    while True:
        char = screen.getkey()
        if char == 'q':
            break
        else:
            str1 = str1 + char
    return str1



#Verry simple main, just makes a small box in the middle then waits for you to type a string
#ended with a q, then waits 5 seconds and closes 
def main():
    #split a window into multiple
    #win = curses.newwin(height,width,start_y,start_x)
    window1 = curses.newwin(20,20, 0, 100)
    win_list.append(window1)
    window1.addstr("===================",curses.A_BLINK)
    for i in range(18):
        window1.addstr(i+1,0,"|",curses.A_BLINK)
        for i in range(18):
            window1.addstr(" ")
        window1.addstr("|",curses.A_BLINK)
    window1.addstr("===================",curses.A_BLINK)

    refresh_screen()

    #add text to screen where cursor is
    #screen.addstr(str)
    str1 = get_text()
    if len(str1) > 15 :
        str1 = str1[0:15]
    window1.addstr(10,3,str1)
    refresh_screen()

    #Keeps the console open while im on windows
    time.sleep(5)
    screen.clear()

init_curses()
main()
