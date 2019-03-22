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

#Function for printing the kanban sections
def kanban_print(sect, sect_n, split):
    for i in range(len(sect)):
        str2 = str(i) + ":" + sect[i]
        screen.addstr(2+(i*2), 2+(split*sect_n), str2[:len(str2)], curses.A_REVERSE)

#Function to clear the screen where a task you are moving was 
def clear_task(task, sect, sect_n,split):
    start = 0
    end = 0
    if sect_n == 0:
        return
    elif sect_n == 1:
        start = 2
        end = split-3
    elif sect_n == 2:
        start = split+2
        end = split+split-2        
    for x in range(start, end):
        screen.addstr(2+(task*2), x, " ")
        screen.addstr(2+len(sect)*2, x, " ")    

##Cannot write to bottom right corner
def kanban():
    global screen
    size = screen.getmaxyx()
    max_tasks = int((size[0]-5)/2)+1
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

        str1 = get_text(split-1)
        if len(str1) < 1:
            continue
        parsed = parse_cmd(str1)
        

        #For when typing in input
        if parsed[0].decode() == "QUIT":
            break
        elif parsed[0].decode() == "TODO":
            task = ""
            if len(tasks) == max_tasks :#temporary untill i do scrolling of the tasks
                continue
            for word in parsed[1:]:
                task = task + word.decode() + " "
            resp = requests.get("http://127.0.0.1:5000/TODO/" + task).text
            if len(resp) > split:#temporary until i do popups for more info on tasks
                continue
            resp = parse_cmd(resp)
            resp = remake_resp(resp)
            tasks.append(resp)
        elif parsed[0].decode() == "INPR":
            task = requests.get("http://127.0.0.1:5000/INPR/" + str(parsed[1].decode())).text
            if len(in_prog) == max_tasks:#temporary untill i do scrolling of the tasks
                continue
            elif len(task) > split:#temporary until i do popups for more info on tasks
                continue
            task = parse_cmd(task)
            if int(task[1]) <= len(tasks)-1 :
                in_prog.append(tasks[int(task[1])])
                tasks.pop(int(task[1]))
                clear_task(int(task[1]), tasks, 1, split)
        elif parsed[0].decode() == "COMP":
            task = requests.get("http://127.0.0.1:5000/COMP/" + str(parsed[1].decode())).text
            if len(complete) == max_tasks:#temporary untill i do scrolling of the tasks
                continue
            elif len(task) > split:#temporary until i do popups for more info on tasks
                continue
            task = parse_cmd(task)
            if int(task[1]) <= len(in_prog)-1:
                complete.append(in_prog[int(task[1])])
                in_prog.pop(int(task[1]))
                clear_task(int(task[1]), in_prog, 2, split)
        elif parsed[0].decode() == "SPLT":
            task = requests.get("http://127.0.0.1:5000/SPLT/" + str(parsed[1].decode())).text
            if len(tasks) == max_tasks:#temporary untill i do scrolling of the tasks
                continue
            elif len(task) > split:#temporary until i do popups for more info on tasks
                continue
            task = parse_cmd(task)

        kanban_print(tasks,0,split)
        kanban_print(in_prog,1,split)
        kanban_print(complete,2,split)
            
        refresh_screen()


def main():
    kanban()
    refresh_screen()
    screen.clear()

init_curses()
main()
close_curses()
