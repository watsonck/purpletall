import curses, time, requests, json

win_list = []
screen = -1
username = ""
password = ""

#kanban varriables
cur_proj = 1
kanban_start = 0
tasks = {}
in_prog = {}
complete = {}
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

def send_recv(proj, cmd, args):
    url = "http://purpletall.cs.longwood.edu:5000/" + str(proj) +'/'
    if cmd == 'add' and len(args) >= 4:
        url = url + 'add?name={'+ args[0].decode() + '}&desc={' + args[1].decode() + '}&time={' + args[2].decode()  + '}&bug={' + args[3].decode() + '}'
    elif cmd == 'move' and len(args) >= 2:
        url = url + 'move?id=' + args[0].decode() +'&stage={'+args[1].decode()+'}'
    elif cmd == 'splt' and len(args) >= 1:
        url = url + 'split?id=' +args[0].decode()
    elif cmd == 'remv' and len(args) >= 1:
        url = url + 'remove?id=' + args[0].decode()
    elif cmd == 'modi':
        return
    elif cmd == 'info' and len(args) >= 1:
        url = url + 'info?id=' +args[0].decode()
    test = requests.get('http://purpletall.cs.longwood.edu:5000/1/add?name={Bug1}&desc={This%20bug%20is%20in%20controller}&time={2019-05-1}&bug={true}').text#.json() #requests.get(url).json()
    print(test)
    screen.addstr(2, 2, test, curses.A_REVERSE)
    return 0

def proc_resp(task):
    for i in range(len(task['stages'])):
        for j in range(len(task['stages'][str(i)])):
            if i == 0:
                boards['todo'][task['stages']['0'][j]['id']] = task['stages']['0'][j]['name']
            elif i == 1:
                boards['inpr'][task['stages']['1'][j]['id']] = task['stages']['1'][j]['name']
            elif i == 2:
                boards['comp'][task['stages']['2'][j]['id']] = task['stages']['2'][j]['name']


#Function for printing the kanban sections
def kanban_print(split, max_tasks, limit):
    global kanban_print
    global boards

    cur_tasks = 0
    cur_board = 0
    for board in boards:
        for task in boards[board]:
            screen.addstr(str(task) + ' ', curses.A_REVERSE)
            break
            if cur_tasks == max_tasks:
                break
            else:
                str1 = str(task) + ": " + boards[board][str(task)]['name']
                screen.addstr(2+(cur_tasks*2), 2+(split*cur_board), str1, curses.A_REVERSE)
                screen.addstr(3+(cur_tasks*2), 3+(split*cur_board), boards[board][task]['user'], curses.A_REVERSE)
                cur_tasks = cur_tasks + 1
        cur_board = cur_board + 1


def draw_kanban(max_x,max_y,split):
    for x in range(max_x):
        screen.addstr(max_y-2, x, " ", curses.A_REVERSE)
        screen.addstr(0,x, " ", curses.A_REVERSE)

    for y in range(max_y-1):
        screen.addstr(y,0+split, " ", curses.A_REVERSE)
        screen.addstr(y,0+split+split, " ", curses.A_REVERSE)
        if y < max_y-2:
            screen.addstr(y,0, " ", curses.A_REVERSE)
            screen.addstr(y,max_x-1, " ", curses.A_REVERSE)
        
    screen.addstr(1,int(split/2)-5, "TO DO", curses.A_REVERSE)
    screen.addstr(1,int((split/2)*3)-5, "IN PROGRESS", curses.A_REVERSE)
    screen.addstr(1,int((split/2)*5)-5, "COMPLETE", curses.A_REVERSE)


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


    curses.echo()
    username = screen.getstr(splity+2,splitx+12,15)
    curses.noecho()
    screen.clear()

    

    


##Cannot write to bottom right corner
def kanban():
    global screen
    size = screen.getmaxyx()
    max_tasks = int((size[0]-5)/2)+1
    split = int(size[1]/3)
    #task = json.loads(requests.get('http://purpletall.cs.longwood.edu:5000/1/ADD/').text)
    added = json.loads(requests.get('http://purpletall.cs.longwood.edu:5000/1/add?name={Bug1}&desc={This%20bug%20is%20in%20controller}&time={2019-05-1}&bug={true}').text)

    string = added['metadata']['stagecount']

    #proc_resp(task)
    draw_kanban(size[1],size[0],split)
    kanban_print(split, max_tasks, split-1)
    screen.addstr(0,0,str(string), curses.A_REVERSE)


    while True:
        global boards
        global cur_proj

        str1 = get_text(split-1)
        if len(str1) < 1:
            continue
        parsed = parse_cmd(str1)
        
        #For when typing in input
        if parsed[0].decode() == "QUIT":
            break
        elif parsed[0].decode() == "ADD":#EX: ADD Do this thing
            task = send_recv(cur_proj, 'add', parsed[1:])
            str1 = get_text(split-1)

            break
            proc_resp(task)
        elif parsed[0].decode() == "MOVE":#EX: MOVE 0 from dest 
            task = send_recv(cur_proj, 'move', parsed[1:])
            proc_resp(task)
        elif parsed[0].decode() == "REMV":#EX: REMV 0 COMP,  Once we have a model this will be REMV 0 
            task = send_recv(cur_proj, 'remv', parsed[1:])
            proc_resp(task)
        elif parsed[0].decode() == "SPLT":#EX: SPLT 0 COMP Task1 Task2,   Once we have a model this will be SPLT 0 Task1 Task2
            task = send_recv(cur_proj, 'splt', parsed[1:])
            proc_resp(task)

        screen.clear()
        draw_kanban(size[1],size[0],split)
        kanban_print(split, max_tasks, split-1)
        refresh_screen()


def main():
    login()
    kanban()
    refresh_screen()
    screen.clear()

init_curses()
main()
close_curses()
