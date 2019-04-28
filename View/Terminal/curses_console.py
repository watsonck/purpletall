import curses, time, requests, json, signal
from sys import exit

win_list = []
screen = -1
username = ""
user_id = 0

#kanban varriables
cur_proj = 1
kanban_start = 0 #where to start displaying tasks from
sect_start = 0 # where to start displaying sections from
boards = {}
sect_names = []
most_tasks = -1 # the most tasks in any column, used to prevent scrolling down super far

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
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_CYAN)
    if curses.can_change_color():
        curses.init_color(5, 540, 170, 870)
    curses.noecho()
    curses.cbreak()
    screen.keypad(True)

def close_curses():
    curses.nocbreak()
    global screen
    screen.keypad(False)
    curses.echo()
    curses.endwin()

def get_text(limit):
    curses.echo()
    global screen
    size = screen.getmaxyx()
    str1 = screen.getstr(size[0]-1,0,limit)
    for i in range(limit):
        screen.addstr(size[0]-1, i, " ")
    return str1

def proj_change(proj_num = 1):
    global boards
    global sect_names
    global kanban_start
    global sect_start
    global cur_proj
    sect_names.clear()
    boards.clear()
    kanban_start = 0
    sect_start = 0
    task = requests.get('http://purpletall.cs.longwood.edu:5000/'+str(proj_num)+'/list').text
    if task == 'ERROR':
        return
    task = json.loads(task)
    cur_proj = proj_num
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
    if cmd == 'add':
        if len(args) < 5:
            return -3
        url = url + 'add?name={'+ args[1] + '}&desc={'
        for words in args[4:]:
            url = url + words + "_"
        url = url[:len(url)-1] +'}&time={' + args[2]  + '}&bug={' + args[3] + '}'+'&user='+str(user_id)
    elif cmd == 'move':
        if len(args) < 3:
            return -3
        url = url + 'move?id=' + args[1] +'&stage={'+args[2]+'}'+'&user='+str(user_id)
    elif cmd == 'splt':
        if len(args) < 2:
            return -3
        url = url + 'split?id=' +args[1]+'&user='+str(user_id)
    elif cmd == 'remv':
        if len(args) < 2:
            return -3
        url = url + 'remove?id=' + args[1]
    elif cmd == 'modi':
        return
    elif cmd == 'info':
        if len(args) < 2:
            return -3
        url = url + 'info?id=' +args[1]
        more_info(url)
        url = 'http://purpletall.cs.longwood.edu:5000/'+str(proj)+'/list'
    elif cmd == 'proj':
        if len(args) < 2:
            return -3
        proj_change(args[1])
        return
    elif cmd == 'acol':
        if len(args) < 2:
            return -3
        url = url + 'addcol?name={' + args[1] +'}' 
    elif cmd == 'dcol':
        if len(args) < 2:
            return -3
        url = url + 'delcol?name={' + args[1] +'}'
    else:
        return -1
    result = requests.get(url).text
    if result == 'ERROR':
        return -2#return -2 since server doesnt give error info
    else:
        return json.loads(result)

def proc_resp(task):
    global boards
    global most_tasks
    most_tasks = 0
    if task == -1:
        return
    for key1, board in boards.items():
        board.clear()
    for key1, stage in task['stages'].items():
        for task in stage:
            boards[str(key1).upper()][str(task['id'])] = [task['name'], task['user'], task['is_bug']]
    for key1, board in boards.items():
        if len(board) > most_tasks:
            most_tasks = len(boards) 




#Function for printing the kanban sections
def kanban_print(split, max_tasks, limit):
    global kanban_start
    global boards
    global sect_names
    global sect_start

    first = -1
    f_name = ""
    second = -1
    s_name = ""
    last = -1
    l_name = ""
    while True:
        for i in range(len(sect_names)):
            if int(sect_names[i][0]) == sect_start:
                first = int(sect_names[i][0])
                f_name = sect_names[i][1]
            elif int(sect_names[i][0]) == sect_start+1:
                second = int(sect_names[i][0])
                s_name = sect_names[i][1]
            elif int(sect_names[i][0]) == sect_start+2:
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
            elif int(key2) >= kanban_start:
                if key1 == f_name:
                    cur_board = 0
                elif key1 == s_name:
                    cur_board = 1
                else:
                    cur_board = 2
                str1 = ""
                if task[2] == True: 
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
        screen.addstr(max_y-2, x, " ", curses.color_pair(2))
        screen.addstr(0,x, " ", curses.color_pair(2))
    for y in range(max_y-1):
        screen.addstr(y,0+split, " ", curses.color_pair(2))
        screen.addstr(y,0+split+split, " ", curses.color_pair(2))
        if y < max_y-2:
            screen.addstr(y,0, " ", curses.color_pair(2))
            screen.addstr(y,max_x-1, " ", curses.color_pair(2))
    global sect_names
    global sect_start
    first = -1
    second = -1
    last = -1

    for i in range(len(sect_names)):
        if int(sect_names[i][0]) == sect_start:
            first = sect_names[i][1]
        elif int(sect_names[i][0]) == sect_start+1:
            second = sect_names[i][1]
        elif int(sect_names[i][0]) == sect_start+2:
            last = sect_names[i][1]

    
    screen.addstr(1,int((split/2))-5, first, curses.A_REVERSE)
    #page =  str(kanban_start/max_t) + "/" + str(total_t/max_t) Ill comeback to these if i have time to show which page you are on
    #screen.addstr(max_y-1, int((split/2))-5, page, curses.A_REVERSE)

    screen.addstr(1,int((split/2)*3)-5, second, curses.A_REVERSE)
    #page =  str(kanban_start/max_t) + "/" + str(total_t/max_t)
    #screen.addstr(max_y-1, int((split/2)*3)-5, page, curses.A_REVERSE)

    screen.addstr(1,int((split/2)*5)-5, last, curses.A_REVERSE)    
    #page =  str(kanban_start/max_t) + "/" + str(total_t/max_t)
    #screen.addstr(max_y-1, int((split/2)*5)-5, page, curses.A_REVERSE)
    max_p = 0
    if len(sect_names)%3 == 0:
        max_p = int(len(sect_names)/3)
    else:
        max_p = int(len(sect_names)/3+1)
    pages = 'Sect PGS: ' + str(sect_start+1) + '/' + str(max_p)
    screen.addstr(max_y-3,max_x-len(pages)-1, pages, curses.A_REVERSE)



def login():
    global username
    global user_id
    global screen
    size = screen.getmaxyx()
    splity = int(size[0]/3)
    splitx = int(size[1]/3)
    curses.echo()
    while True:
        for y in range(splity,splity+5):
            for x in range(splitx,splitx+splitx):
                screen.addstr(y,x," ", curses.A_REVERSE)
                if y == splity or y == splity+4:
                    screen.addstr(y,x," ", curses.color_pair(2))
                elif x == splitx or x == splitx+splitx-1:
                    screen.addstr(y,x," ", curses.color_pair(2))
    
        screen.addstr(splity+1, splitx + int(splitx*.38), "Purple Tall Login", curses.A_REVERSE)
        screen.addstr(splity+3, splitx + int(splitx*.33), "Username:", curses.A_REVERSE)
        screen.addstr(splity+3, splitx + int(splitx*.33) + 12, "               ")

        username = screen.getstr(splity+3,splitx + int(splitx*.33)+12,15)
        user_id = requests.get('http://purpletall.cs.longwood.edu:5000/login?user={'+username.decode()+'}').text
        if str(user_id) != '0':
            break
        elif username.decode().upper() == 'QUIT':
            close_curses()
            exit()
    curses.noecho()
    screen.clear()

#user creation screen for once thats in the controller
def create_user():
    global screen
    size = screen.getmaxyx()
    splity = int(size[0]/3)
    splitx = int(size[1]/3)
    for y in range(splity,splity+splity):
        for x in range(splitx,splitx+splitx):
            screen.addstr(y,x," ", curses.A_REVERSE)
    
    screen.addstr(splity, splitx+(int(splitx/2)), "Purple Tall Usercreation", curses.A_REVERSE)
    screen.addstr(splity+2, splitx+1, "Please enter your desired username", curses.A_REVERSE)
    screen.addstr(splity+4, splitx+1, "Username:", curses.A_REVERSE)
    screen.addstr(splity+4, splitx+12, "                ")
    
    curses.echo()
    username = screen.getstr(splity+4,splitx+12,15)
    #user_id = requests.get('http://purpletall.cs.longwood.edu:5000/login?user={'+username.decode()+'}').text
    curses.noecho()
    screen.clear()

def proj_list(called_from = 0):
    global screen
    size = screen.getmaxyx()
    splity = int(size[0]/3)
    splitx = int(size[1]/3)

    projs = json.loads(requests.get('http://purpletall.cs.longwood.edu:5000/projlist').text)
    max_y = splity+1 + 2*projs['count']
    for y in range(splity,max_y+1):
        for x in range(splitx,splitx+splitx):
            screen.addstr(y,x," ", curses.A_REVERSE)
            if called_from == 0:
                if y == splity or y == max_y:
                    screen.addstr(y,x," ", curses.color_pair(1))
                elif x == splitx or x == splitx+splitx-1:
                    screen.addstr(y,x," ", curses.color_pair(1))
            else:
                if y == splity or y == max_y:
                    screen.addstr(y,x," ", curses.color_pair(2))
                elif x == splitx or x == splitx+splitx-1:
                    screen.addstr(y,x," ", curses.color_pair(2))
    
    for x in range(size[1]):
        screen.addstr(size[0]-2,x, " ", curses.color_pair(2))
    cur_y = splity+1
    p_list = []
    for proj in projs['projects']:
        p_list.append(str(proj['projid']))
        str1 = str(proj['projid']) + ': ' + proj['name'] + ': ' + proj['description'] 
        screen.addstr(cur_y,splitx+1,str1, curses.A_REVERSE)
        cur_y = cur_y + 2
    if called_from == 0:
        screen.addstr(size[0]-3,1,'Press enter or enter anything to contiune', curses.A_REVERSE)
        wait = get_text(splitx*3-2)
    elif called_from == 1:
        return p_list

def proj_choice():
    global screen
    size = screen.getmaxyx()
    splitx = int(size[1]/3)

    p_list = proj_list(1)
    global cur_proj
    curses.echo()
    screen.addstr(size[0]-3,1,'Please Type the ID of the Proj you would like:', curses.A_REVERSE)
    while True:
        choice = get_text(splitx*3-2)
        if choice.decode().upper() == 'QUIT':
            close_curses()
            exit()
        if choice.decode() in p_list:
            cur_proj = str(choice.decode())
            break
    curses.noecho()
    screen.clear()
    proj_change(cur_proj)
        

##Cannot write to bottom right corner
def kanban():
    global boards
    global cur_proj
    global kanban_start
    global most_tasks
    global sect_start
    global screen
    size = screen.getmaxyx()
    max_tasks = int((size[0]-5)/2)+1
    split = int(size[1]/3)
    
    proj_change(cur_proj)
    draw_kanban(size[1],size[0],split)
    kanban_print(split, max_tasks, split-1)
    screen.addstr(size[0]-3, 1, "Please enter a command:", curses.A_REVERSE)
    while True:
        size = screen.getmaxyx()
        max_tasks = int((size[0]-5)/2)+1
        split = int(size[1]/3)
        str1 = get_text(split+split)
        if len(str1) < 1:
            continue
        parsed = str1.decode().split()
        
        #CMD templates
        #EX: ADD <name> <expected comp> <is_bug> <desc>
        #EX: MOVE <task_id> <dest> 
        #EX: REMV <task_id>
        #EX: SPLT <task_id>
        #EX: INFO <task_id>
        #EX: DCOL <col_name>
        #EX: ACOL <col_name>
        #EX: PROJ <proj_id>
        #EX: SCRL <T> <U or D> #To scroll tasks
        #EX: SCRL <S> <L or R> #To scroll sections
        if parsed[0].upper() == "QUIT":
            break
        elif parsed[0].upper() == "PROJ":
            proj_choice()
            #task = send_recv(cur_proj, 'proj', parsed)
        elif parsed[0].upper() == "SCRL":
            if len(parsed) < 3:
                continue
            if parsed[1].upper() == "T":
                if parsed[2].upper() == "U" and kanban_start != 0:
                    kanban_start = kanban_start-max_tasks
                elif parsed[2].upper() == 'D' and kanban_start < most_tasks:
                    kanban_start = kanban_start+max_tasks
            elif parsed[1].upper() == "S":
                if parsed[2].upper() == 'L' and sect_start != 0:
                    sect_start = sect_start - 1
                elif parsed[2].upper() == 'R' and len(sect_names) > 3:
                    if sect_start+3 < len(sect_names):
                        sect_start = sect_start+1
        elif parsed[0].upper() == 'PLS':
            proj_list()
        else:
            task = send_recv(cur_proj, parsed[0].lower(), parsed)
            if task == -1:
                screen.addstr(size[0]-2, 1, "                                  ", curses.color_pair(2))
                screen.addstr(size[0]-2, 1, "ERROR: NOT A VALID COMMAND", curses.color_pair(1))
                continue
            elif task == -2:
                screen.addstr(size[0]-2, 1, "                                  ", curses.color_pair(2))
                screen.addstr(size[0]-2, 1, "ERROR: ERROR RECEIVED FROM SERVER", curses.color_pair(1))
                continue
            elif task == -3:
                screen.addstr(size[0]-2, 1, "                                  ", curses.color_pair(2))
                screen.addstr(size[0]-2, 1, "ERROR: NOT ENOUGH ARGS FOR COMMAND", curses.color_pair(1))
                continue
            proc_resp(task)

        screen.clear()
        draw_kanban(size[1],size[0],split)
        kanban_print(split, max_tasks, split-1)
        screen.addstr(size[0]-3, 1, "Please enter a command:", curses.A_REVERSE)
        screen.refresh()


def main():
    global screen
    signal.signal(signal.SIGINT, signal_handler)
    login()
    proj_choice()
    kanban()
    screen.refresh()
    screen.clear()

init_curses()
main()
close_curses()
