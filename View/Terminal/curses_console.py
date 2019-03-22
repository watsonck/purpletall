import curses
import time
import requests

win_list = []
screen = -1

#kanban varriables
tasks = []
in_prog = []
complete = []

#Put init stuff here
def init_curses(): 
    global screen
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    screen.keypad(True)

def close_curses():
    curses.nocbreak()
    global screen
    screen.keypad(False)
    curses.echo()
    curses.endwin()

def refresh_screen():
    screen.refresh()
    for win in win_list:
        win.refresh()


def get_text(limit):
    curses.echo()
    global screen
    size = screen.getmaxyx()
    str1 = screen.getstr(size[0]-1,0,limit)
    for i in range(limit):
        screen.addstr(size[0]-1, i, " ")
    return str1

def parse_cmd(cmd):
    return cmd.upper().split() 


#Just remakes the rest of the cmd without the leading four letter identifier 
def remake_cmd(cmd):
    result = ""
    for word in resp[1:]:
        result = result + " " + word.decode()
    return result

#same as above but for server responses so it doesnt need to be decoded 
def remake_resp(resp):
    result = ""
    for word in resp[1:]:
        result = result + " " + word
    return result



##Cannot write to bottom right corner
def kanban():
    global screen
    size = screen.getmaxyx()
    for x in range(size[1]):
        screen.addstr(size[0]-2, x, " ", curses.A_REVERSE)
        screen.addstr(0,x, " ", curses.A_REVERSE)

    split = int(size[1]/3)
    for y in range(size[0]-1):
        screen.addstr(y,0+split, " ", curses.A_REVERSE)
        screen.addstr(y,0+split+split, " ", curses.A_REVERSE)
        if y < size[0]-2:
            screen.addstr(y,0, " ", curses.A_REVERSE)
            screen.addstr(y,size[1]-1, " ", curses.A_REVERSE)
        
    screen.addstr(1,int(split/2)-5, "TO DO", curses.A_REVERSE)
    screen.addstr(1,int((split/2)*3)-5, "IN PROGRESS", curses.A_REVERSE)
    screen.addstr(1,int((split/2)*5)-5, "COMPLETE", curses.A_REVERSE)

    while True:
        global tasks
        global in_prog
        global complete

        str1 = get_text(split-2)
        parsed = parse_cmd(str1)
        

        #For when typing in input
        if parsed[0].decode() == "QUIT":
            break
        elif parsed[0].decode() == "TODO":
            task = ""
            for word in parsed[1:]:
                task = task + word.decode() + " "
            resp = requests.get("http://127.0.0.1:5000/TODO/" + task).text
            resp = parse_cmd(resp)
            resp = remake_resp(resp)
            tasks.append(resp)
        elif parsed[0].decode() == "INPR":
            task = requests.get("http://127.0.0.1:5000/INPR/" + str(parsed[1].decode())).text
            task = parse_cmd(task)
            if int(task[1]) <= len(tasks)-1 :
                in_prog.append(tasks[int(task[1])])
                tasks.pop(int(task[1]))
                for x in range(2, split-2):
                    screen.addstr(2+(int(int(task[1])*2)), x, " ")
        elif parsed[0].decode() == "COMP":
            task = requests.get("http://127.0.0.1:5000/COMP/" + str(parsed[1].decode())).text
            task = parse_cmd(task)
            if int(task[1]) <= len(in_prog)-1:
                complete.append(in_prog[int(task[1])])
                in_prog.pop(int(task[1]))
                for x in range(split+2, split+split-2):
                    screen.addstr(2+(int(int(task[1])*2)), x, " ")

 
        for i in range(len(tasks)):
            str2 = str(i) + ": " + tasks[i]
            screen.addstr(2+(i*2), 2, str2[:len(str2)], curses.A_REVERSE)
            
        for i in range(len(in_prog)):
            str2 = str(i) + ": " + in_prog[i]
            screen.addstr(2+(i*2), split+2 , str2[:len(str2)], curses.A_REVERSE)
                      
        for i in range(len(complete)):
            str2 = str(i) + ": " + complete[i]
            screen.addstr(2+(i*2), split+split+2 , str2[:len(str2)], curses.A_REVERSE)
            
        refresh_screen()


def main():
    kanban()
    refresh_screen()
    time.sleep(3)
    screen.clear()

init_curses()
main()
close_curses()
