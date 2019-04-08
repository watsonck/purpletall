import curses, time, requests, json, signal
from sys import exit

win_list = []
screen = -1
username = ""
user_id = 0

#kanban varriables
cur_proj = 1
kanban_start = 0
boards = {}
sect_names = []

#prevents CTRL+C from breaking the terminal
#Lines 16-19 and Line 257 Helped by :https://stackoverflow.com/questions/1112343/how-do-i-capture-sigint-in-python
def signal_handler(sig, frame):
    close_curses()
    exit()

#Put init stuff here
def init_curses(): 
    global screen
    screen = curses.initscr()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_RED)
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

def proj_change(proj_num = 1):
    global boards
    task = json.loads(requests.get('http://purpletall.cs.longwood.edu:5000/'+str(proj_num)+'/LIST').text)
    for stage in task['metadata']['stages']:
        boards[task['metadata']['stages'][stage].upper()] = {}
        sect_names.append([str(stage),task['metadata']['stages'][stage].upper()])
    proc_resp(task)

def more_info(url):
    global screen
    size = screen.getmaxyx()
    splity = int(size[0]/3)
    splitx = int(size[1]/3)
    for y in range(splity,splity+splity):
        if y == splity :
            for x in range(splitx, splitx+splitx):
                screen.addstr(y,x," ", curses.color_pair(1))
        elif y == splity+splity-1:
            for x in range(splitx, splitx+splitx):
                screen.addstr(y,x," ", curses.color_pair(1))
        screen.addstr(y,splitx," ", curses.color_pair(1))
        screen.addstr(y,splitx+splitx," ", curses.color_pair(1))
    
    task = json.loads(requests.get(url).text)
    y = splity+2
    for key1, val1 in task.items():
        str1 = str(key1) + ": " + str(val1) + " "
        screen.addstr(y,splitx+1, str1, curses.A_REVERSE)
        y = y+1
    screen.refresh()
    screen.addstr(splity+splity-1, splitx+1, "Press Enter To Contiune", curses.color_pair(1))
    get_text(splitx+splitx)


def send_recv(proj, cmd, args):
    global user_id
    url = "http://purpletall.cs.longwood.edu:5000/" + str(proj) +'/'
    if cmd == 'add' and len(args) >= 4:
        url = url + 'add?name={'+ args[0].decode() + '}&desc={'
        for words in args[3:]:
            url = url + words.decode() + "_"
        url = url[:len(url)-2] +'}&time={' + args[1].decode()  + '}&bug={' + args[2].decode() + '}'+'&user='+str(user_id)
    elif cmd == 'move' and len(args) >= 2:
        url = url + 'move?id=' + args[0].decode() +'&stage={'+args[1].decode()+'}'+'&user='+str(user_id)
    elif cmd == 'splt' and len(args) >= 1:
        url = url + 'split?id=' +args[0].decode()+'&user='+str(user_id)
    elif cmd == 'remv' and len(args) >= 1:
        url = url + 'remove?id=' + args[0].decode()
    elif cmd == 'modi':
        return
    elif cmd == 'info' and len(args) >= 1:
        url = url + 'info?id=' +args[0].decode()
        more_info(url)
        url = 'http://purpletall.cs.longwood.edu:5000/'+str(proj)+'/LIST'
    elif cmd == 'proj' and len(args) >= 1:
        proj_change(args[0].decode)
        return
    return json.loads(requests.get(url).text)

def proc_resp(task):
    global boards
    for key1, board in boards.items():
        board.clear()
    for key1, stage in task['stages'].items():
        for task in stage:
            boards[str(key1).upper()][str(task['id'])] = [task['name'], task['user'], task['is_bug']]




#Function for printing the kanban sections
def kanban_print(split, max_tasks, limit, start = 0):
    global kanban_print
    global boards
    global sect_names

    first = -1
    f_name = ""
    second = -1
    s_name = ""
    last = -1
    l_name = ""
    while True:
        for i in range(len(sect_names)):
            if int(sect_names[i][0]) == start:
                first = int(sect_names[i][0])
                f_name = sect_names[i][1]
            elif int(sect_names[i][0]) == start+1:
                second = int(sect_names[i][0])
                s_name = sect_names[i][1]
            elif int(sect_names[i][0]) == start+2:
                last = int(sect_names[i][0])
                l_name = sect_names[i][1]
        if first != -1 and second != -1 and last != -1:
            break

    cur_tasks = 0
    cur_board = 0
    for key1, board in boards.items():
        for key2, task in board.items():
            if cur_tasks == max_tasks:
                cur_tasks = 0
                break
            else:
                if key1 == f_name:
                    cur_board = first
                elif key1 == s_name:
                    cur_board = second
                else:
                    cur_board = last
                str1 = ""
                if task[2] == True: #Unicode emoji copied from https://www.compart.com/en/unicode/U+1F41B
                    str1 = str(key2) + ": " + task[0]
                    screen.addstr(2+(cur_tasks*2), 2+(split*cur_board), str1, curses.color_pair(1))
                    screen.addstr(3+(cur_tasks*2), 3+(split*cur_board), str(task[1]), curses.color_pair(1))
                else:
                    str1 = str(key2) + ": " + task[0]
                    screen.addstr(2+(cur_tasks*2), 2+(split*cur_board), str1, curses.A_REVERSE)
                    screen.addstr(3+(cur_tasks*2), 3+(split*cur_board), str(task[1]), curses.A_REVERSE)

                cur_tasks = cur_tasks + 1
        cur_tasks = 0
        cur_board = cur_board + 1



def draw_kanban(max_x,max_y,split,start = 0):
    for x in range(max_x):
        screen.addstr(max_y-2, x, " ", curses.A_REVERSE)
        screen.addstr(0,x, " ", curses.A_REVERSE)

    for y in range(max_y-1):
        screen.addstr(y,0+split, " ", curses.A_REVERSE)
        screen.addstr(y,0+split+split, " ", curses.A_REVERSE)
        if y < max_y-2:
            screen.addstr(y,0, " ", curses.A_REVERSE)
            screen.addstr(y,max_x-1, " ", curses.A_REVERSE)
    
    global sect_names
    first = -1
    second = -1
    last = -1
    while True:
        for i in range(len(sect_names)):
            if int(sect_names[i][0]) == start:
                first = sect_names[i][1]
            elif int(sect_names[i][0]) == start+1:
                second = sect_names[i][1]
            elif int(sect_names[i][0]) == start+2:
                last = sect_names[i][1]
        if first != -1 and second != -1 and last != -1:
            break
    
    screen.addstr(1,int((split/2))-5, first, curses.A_REVERSE)
    screen.addstr(1,int((split/2)*3)-5, second, curses.A_REVERSE)
    screen.addstr(1,int((split/2)*5)-5, last, curses.A_REVERSE)




def login():
    global username
    global user_id
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


    curses.echo()
    username = screen.getstr(splity+2,splitx+12,15)
    user_id = requests.get('http://purpletall.cs.longwood.edu:5000/login?user={'+username.decode()+'}').text
    curses.noecho()
    screen.clear()

    

    


##Cannot write to bottom right corner
def kanban():
    global screen
    size = screen.getmaxyx()
    max_tasks = int((size[0]-5)/2)+1
    split = int(size[1]/3)
    
    proj_change()
    draw_kanban(size[1],size[0],split)
    kanban_print(split, max_tasks, split-1)

    while True:
        global boards
        global cur_proj

        str1 = get_text(split+split)
        if len(str1) < 1:
            continue
        parsed = parse_cmd(str1)
        
        #For when typing in input
        if parsed[0].decode() == "QUIT":
            break
        elif parsed[0].decode() == "ADD":#EX: ADD <name> <expected comp> <is_bug> <desc>
            task = send_recv(cur_proj, 'add', parsed[1:])
            proc_resp(task)
        elif parsed[0].decode() == "MOVE":#EX: MOVE <task_id> <dest> 
            task = send_recv(cur_proj, 'move', parsed[1:])
            proc_resp(task)
        elif parsed[0].decode() == "REMV":#EX: REMV <task_id>
            task = send_recv(cur_proj, 'remv', parsed[1:])
            proc_resp(task)
        elif parsed[0].decode() == "SPLT":#EX: SPLT <task_id>
            task = send_recv(cur_proj, 'splt', parsed[1:])
            proc_resp(task)
        elif parsed[0].decode() == "INFO":#EX: INFO <task_id>
            task = send_recv(cur_proj, 'info', parsed[1:])
            proc_resp(task)

        screen.clear()
        draw_kanban(size[1],size[0],split)
        kanban_print(split, max_tasks, split-1)
        refresh_screen()


def main():
    signal.signal(signal.SIGINT, signal_handler)
    login()
    kanban()
    refresh_screen()
    screen.clear()

init_curses()
main()
close_curses()
