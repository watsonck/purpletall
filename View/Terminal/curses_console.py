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
    global cur_proj
    url = "http://purpletall.cs.longwood.edu:5000/" + str(proj) +'/'
    if cmd == 'add':
        if len(args) < 5:
            return -3
        url = url + 'add?name={'+ args[1] + '}&desc={'
        for words in args[4:]:
            url = url + words + " "
        url = url[:len(url)-1] +'}&time={' + args[2]  + '}&bug=' + args[3] +'&user='+str(user_id)
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


def get_s_names():
    global sect_names
    global sect_start
    result = []
    first = -1
    fname = ""
    second = -1
    sname = ""
    last = -1
    lname = ""

    s_start = -1
    s_start_found = False
    for i in range(len(sect_names)):
        if sect_start == sect_names[i][1]:
            s_start_found = True
            break
        elif int(sect_names[i][0]) < s_start or s_start == -1:
            s_start = int(sect_names[i][0]) 
    if s_start_found == False:
        sect_start = s_start
    for i in range(len(sect_names)):
        if int(sect_names[i][0]) == sect_start:
            first = sect_names[i][0]
            fname = sect_names[i][1]
        elif int(sect_names[i][0]) == sect_start+1:
            second = sect_names[i][0]
            sname = sect_names[i][1]
        elif int(sect_names[i][0]) == sect_start+2:
            last = sect_names[i][0]
            lname = sect_names[i][1]
    if second == -1:
        for i in range(len(sect_names)):
            if int(sect_names[i][0]) > int(first) and second == -1 and int(sect_names[i][0]) != last:
                second = int(sect_names[i][0])             
                sname = sect_names[i][1]
            elif int(sect_names[i][0]) > int(first) and int(sect_names[i][0]) != last :
                second = int(sect_names[i][0])
                sname = sect_names[i][1]
    if last == -1:
        for i in range(len(sect_names)):
            if int(sect_names[i][0]) > int(second) and int(sect_names[i][0]) != second and last == -1:
                last = int(sect_names[i][0])
                lname = sect_names[i][1]
            elif int(sect_names[i][0]) > int(second) and int(sect_names[i][0]) != second:
                last = int(sect_names[i][0])
                lname = sect_names[i][1]

    result.append([first,fname])
    result.append([second,sname])
    result.append([last,lname])
    return result


#Function for printing the kanban sections
def kanban_print(split, max_tasks, limit):
    global kanban_start
    global boards
    global sect_names
    global sect_start

    sects = get_s_names()
    f_name = -1
    s_name = -1
    l_name = -1
    for i in range(len(sects)):
        if i == 0:
            f_name = sects[i][1]
        elif i == 1:
            s_name = sects[i][1]
        elif i == 2:
            l_name = sects[i][1]
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


    sects = get_s_names()
    first = -1
    fname = " "
    second = -1
    sname = " "
    last = -1
    lname = " "
    if len(sects) >= 3:
        first = sects[0][0]
        fname = sects[0][1]
        second = sects[1][0]
        sname = sects[1][1]
        last = sects[2][0]
        lname = sects[2][1]
    elif len(sects) == 2:
        first = sects[0][0]
        fname = sects[0][1]
        second = sects[1][0]
        sname = sects[1][1]
    elif len(sects) == 1:
        first = sects[0][0]
        fname = sects[0][1]


    screen.addstr(1,int((split/2))-5, fname, curses.A_REVERSE)
    screen.addstr(1,int((split/2)*3)-5, sname, curses.A_REVERSE)
    screen.addstr(1,int((split/2)*5)-5, lname, curses.A_REVERSE)

    max_p = 0
    if len(sect_names)%3 == 0:
        max_p = int(len(sect_names)/3)
    else:
        max_p = int(len(sect_names)/3+1)
    pages = 'Sect PGS: ' + str(sect_start+1) + '/' + str(max_p)
    screen.addstr(max_y-3,max_x-len(pages)-1, pages, curses.A_REVERSE)

def blank(start_x, end_x, max_y):
    for y in range(1,max_y-2):
        for x in range(start_x+1, end_x+1):
            screen.addstr(y,x," ",curses.A_REVERSE)

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
        elif username.decode().upper() == 'CREATE':
            create_user()
            user_id = requests.get('http://purpletall.cs.longwood.edu:5000/login?user={'+username.decode()+'}').text
            break
        else:
            screen.addstr(splity-2, splitx, "INVALID USERNAME", curses.color_pair(1))
    curses.noecho()
    screen.clear()

#user creation screen for once thats in the controller
def create_user():
    global screen
    size = screen.getmaxyx()
    splity = int(size[0]/3)
    splitx = int(size[1]/3)
    screen.addstr(splity-2, splitx, "                 ")
    for y in range(splity,splity+splity):
        for x in range(splitx,splitx+splitx):
            screen.addstr(y,x," ", curses.A_REVERSE)
            if y == splity or y == splity+splity-1:
                screen.addstr(y,x, " ", curses.color_pair(2))
            elif x == splitx or x == splitx+splitx-1:
                screen.addstr(y,x, " ", curses.color_pair(2))
    
    screen.addstr(splity, splitx+(int(splitx*.3)), "Purple Tall User Creation", curses.A_REVERSE)
    screen.addstr(splity+2, splitx+1, "Please enter your information", curses.A_REVERSE)
    screen.addstr(splity+4, splitx+1, "First Name:", curses.A_REVERSE)
    screen.addstr(splity+4, splitx+12, "                ")
    screen.addstr(splity+6, splitx+1, "Last Name:", curses.A_REVERSE)
    screen.addstr(splity+6, splitx+12, "                ")
    screen.addstr(splity+8, splitx+1, "Username:", curses.A_REVERSE)
    screen.addstr(splity+8, splitx+10, "                ")
    screen.addstr(splity+10, splitx+1, "Email:", curses.A_REVERSE)
    screen.addstr(splity+10, splitx+7, "                                  ")


    
    curses.echo()
    fname = screen.getstr(splity+4,splitx+12,15)
    lname = screen.getstr(splity+6,splitx+12,15)
    username = screen.getstr(splity+8,splitx+10,15)
    email = screen.getstr(splity+10,splitx+7,34)
    requests.get("http://purpletall.cs.longwood.edu:5000/user?fname={"+fname.decode()+"}&lname={"+lname.decode()+"}&uname={"+username.decode()+"}&email={"+email.decode()+"}")
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

def create_proj():
    global screen
    size = screen.getmaxyx()
    splity = int(size[0]/3)
    splitx = int(size[1]/3)
    screen.addstr(splity-2, splitx, "                 ")
    for y in range(splity,splity+splity):
        for x in range(splitx,splitx+splitx):
            screen.addstr(y,x," ", curses.A_REVERSE)
            if y == splity or y == splity+splity-1:
                screen.addstr(y,x, " ", curses.color_pair(2))
            elif x == splitx or x == splitx+splitx-1:
                screen.addstr(y,x, " ", curses.color_pair(2))

    screen.addstr(splity, splitx+(int(splitx*.3)), "Purple Tall User Creation", curses.A_REVERSE)
    screen.addstr(splity+2, splitx+1, "Please enter the project information.")
    screen.addstr(splity+4, splitx+1, "Proj Name:",curses.A_REVERSE)    
    screen.addstr(splity+4, splitx+11, "                    ",curses.A_REVERSE)
    screen.addstr(splity+6, splitx+1, "Proj Desc:",curses.A_REVERSE)
    screen.addstr(splity+6, splitx+11, "                    ",curses.A_REVERSE)
    
    curses.echo()
    pname = screen.getstr(splity+4,splitx+11,15)
    desc = screen.getstr(splity+6,splitx+11,15)
    requests.get("http://purpletall.cs.longwood.edu:5000/newproj?name={"+pname.decode()+"}&desc={"+desc.decode()+"}")
    curses.noecho()
    screen.clear()


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
        elif choice.decode().upper() == 'CPROJ':
            create_proj()
            return
        elif choice.decode().upper() == 'DPROJ':
            parse = choice.decode().split()
            screen.addstr(20,2,parse[1], curses.A_REVERSE)
            get_text(15)
            if len(parse) >= 2:
                requests.get("http://purpletall.cs.longwood.edu:5000/delproj?id="+parse[1])
                curses.noecho()
                screen.clear()
                return
        elif choice.decode() in p_list:
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
        elif parsed[0].upper() == 'ACOL' or parsed[0].upper() == 'DCOL':
            if len(parsed) < 2:
                screen.addstr(size[0]-2, 1, "                                  ", curses.color_pair(2))
                screen.addstr(size[0]-2, 1, "ERROR: NOT ENOUGH ARGS FOR COMMAND", curses.color_pair(1))
            else:
                url = "http://purpletall.cs.longwood.edu:5000/" + str(cur_proj) +'/'
                if parsed[0].upper() == 'ACOL':
                    url = url + 'addcol?name={' + parsed[1] +'}'
                elif parsed[0].upper() == 'DCOL': 
                    url = url + 'delcol?name={' + parsed[1] +'}'
                requests.get(url).text
                proj_change(int(cur_proj))
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
                elif parsed[2].upper() == 'R' and len(sect_names) > 3 and sect_start+1 < len(sect_names):
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
