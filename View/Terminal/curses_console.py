import curses
import time
import requests

win_list = []
screen = -1
username = ""
password = ""

#kanban varriables
tasks = []
in_prog = []
complete = []
boards = {'todo':tasks, 'inpr':in_prog, 'comp':complete}


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
    for word in cmd:
        result = result + " " + word.decode()
    return result

#same as above but for server responses so it doesnt need to be decoded 
def remake_resp(resp):
    result = ""
    for word in resp[1:]:
        result = result + " " + word
    return result

def send_recv(cmd):
    task = requests.get("http://purpletall.cs.longwood.edu:5000/TASK/" + cmd).text
    return parse_cmd(task)    

#Function for printing the kanban sections
def kanban_print(sect, sect_n, split):
    global username
    for i in range(len(sect)):
        str2 = str(i) + ":" + sect[i]
        screen.addstr(2+(i*2), 2+(split*sect_n), str2[:len(str2)], curses.A_REVERSE)
        screen.addstr(3+(i*2), 2+(split*sect_n), username, curses.A_REVERSE)

#Function to clear the screen where a task you are moving was 
def clear_task(task, sect, sect_n,split):
    start = 0
    end = 0
    if sect_n == 'todo':#todo
        start = 2
        end = split-3
    elif sect_n == 'inpr':#inpr
        start = split+2
        end = split+split-2
    elif sect_n == 'comp':#comp
        start = split+split+2
        end = split+split+split-2        
    for x in range(start, end):
        screen.addstr(2+(task*2), x, " ")
        screen.addstr(2+len(sect)*2, x, " ")    

def login():
    global username
    global password
    global screen
    size = screen.getmaxyx()
    splity = int(size[0]/3)
    splitx = int(size[1]/3)
    for y in range(splity,splity+splity):
        for x in range(splitx,splitx+splitx):
            screen.addstr(y,x," ", curses.A_REVERSE)
    
    screen.addstr(splity, splitx+(int(splitx/2)), "Purple Tall Login", curses.A_REVERSE)
    screen.addstr(splity+2, splitx+1, "Username:", curses.A_REVERSE)
    screen.addstr(splity+2, splitx+12, "                ")
    screen.addstr(splity+4, splitx+1, "Password:", curses.A_REVERSE)
    screen.addstr(splity+4, splitx+12, "                ")

    curses.echo()
    username = screen.getstr(splity+2,splitx+12,16)
    password = screen.getstr(splity+4,splitx+12,16)
    curses.noecho()
    screen.clear()

    

    


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
        global boards

        str1 = get_text(split-1)
        if len(str1) < 1:
            continue
        parsed = parse_cmd(str1)
        
        #For when typing in input
        if parsed[0].decode() == "QUIT":
            break
        elif parsed[0].decode() == "ADD":#EX: ADD Do this thing
            task = send_recv(str1.decode())
            if len(boards['todo']) == max_tasks or len(task) < 2:#temporary untill i do scrolling of the tasks
                continue
            if len(remake_resp(task)) > split:#temporary until i do popups for more info on tasks
                continue
            boards['todo'].append(remake_resp(task))
        elif parsed[0].decode() == "MOVE":#EX: MOVE 0 from dest 
            task = send_recv(str1.decode())
            if len(task) < 3:
                continue
            c_board = task[2].lower()
            t_board = task[3].lower()
            if len(task) < 3:
                continue
            if len(boards[t_board]) < max_tasks and int(task[1]) <= len(boards[c_board])-1:
                if len(remake_resp(task)) > split-2:
                    continue
                boards[t_board].append(boards[c_board][int(task[1])])
                boards[c_board].pop(int(task[1]))
                clear_task(int(task[1]), boards[c_board], c_board, split)
        elif parsed[0].decode() == "REMV":#EX: REMV 0 COMP,  Once we have a model this will be REMV 0 
            task = send_recv(str1.decode())
            if len(task) < 3 : 
                continue
            c_board = task[2].lower()
            if int(task[1]) <= len(boards[c_board])-1:
                boards[c_board].pop(int(task[1]))
                clear_task(int(task[1]), boards[c_board], c_board, split)
        elif parsed[0].decode() == "SPLT":#EX: SPLT 0 COMP Task1 Task2,   Once we have a model this will be SPLT 0 Task1 Task2
            task = send_recv(str1.decode())
            if len(task) < 5:
                continue
            c_board = task[2].lower()
            if len(boards[c_board]) <= max_tasks-2 and int(task[1]) <= len(boards[c_board])-1:#temporary untill i do scrolling of the tasks
                boards[c_board].pop(int(task[1]))
                boards[c_board].append(task[3])
                boards[c_board].append(task[4])
            clear_task(int(task[1]), boards[c_board], c_board, split)

        kanban_print(tasks,0,split)
        kanban_print(in_prog,1,split)
        kanban_print(complete,2,split)
            
        refresh_screen()


def main():
    login()
    kanban()
    refresh_screen()
    screen.clear()

init_curses()
main()
close_curses()
