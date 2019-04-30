# purpletall
A project management system

Contributors to Controller: 
  Cameron Haddock

Contributors to View (Terminal and Web): 
  Ryan White(Terminal)
  Alex Sedgwick(Web)
  Michael Montgomery(Web)
  Shyheim Williams(Web)

Unit Testing: 
  Shyheim Williams
  Colin Watson
  Brendan Speed

Contributers to Model:
  Colin Watson


Setup Server:
1) Copy server to host computer
2) Have a postgres database in place
3) Run: psql -h (host) -U username -f sql.input
	Log in with password
4) Edit config file to direct towards postgres database


Setup Client:
1) Copy client to client computer
2) Edit config to direct towards host computer
	Also supports changing how often server refreshes

How to use:
1) Start the controller:
	python3 controller.py
----Using the terminal----
2) Open another Terminal.
3) Start the view:
	python3 curses_console.py
----Using the web----
2)Using the website:
    open your browser (in the lab)
	Enter the host url where the server is located 


Here are the view controls:

ALL CMDS NON CASE SENSISTIVE
While in Login screen:
	create : Go to Create user screen

While in Kanban board:
	ADD: followed by your task 
		ADD Task1  2019 false This thing is broken
		ADD <name> <expected comp> <is_bug> <desc>
	MOVE : followed by the task number then destination
		MOVE 0 comp
		MOVE <task_id> <to>
	RNAM: Rename a tasl
		RNAM 8 Bug2
		RNAM <task_id> <task_name>
	REMV: Removes task
		REMV 0
		REMV <task_id> 
	SPLT: Splits task into 2 tasks
		SPLT 0 
		SPLT <task_id>
	LOG: Gives you the log of all actions applied to a task
		LOG 19
		LOG <task_id>
	SCRL: Scroll either columns or tasks
		For Tasks:
			SCRL T U
			SCRL <T> <U or D>
		For Columns:
			SCRL S R
			SCRL <S> <L or R>
	PLS: Brings up list of all projects
		PLS 
	ACOL: Add column to kanban board
		ACOL Crap
		ACOL <col_name>
	DCOL: Delete column on kanban board
		DCOL Crap
		DCOL <col_name>
	SCOL: Swap column positions
		SCOL Todo Done
		SCOL <col_1> <col_2>
	PROJ: Changes projects
		PROJ
			While In proj screen:
				CPROJ: Create Project
				DPROJ: Delete Project
					DPROJ 5
					DPROJ <proj_id>
	INFO: Displays more info about Task
		INFO 1
		INFO <task_id>
	PING: Ping a user with an email
		PING whitery Hello i fixed the bug
		PING <username> <msg>
	QUIT : Exits the kanaban loop 

Git Flags:
	To perform actions, place this flags in your git commits

	Add a new task to a project:
		<ADD (Project ID) (Task Name) (Expected Completion Date) (Is Bug Boolean) (Message)>
		Ex: <ADD 1 Task5 5-5-2019 false This task is to test stuff>

	Remove a task from a project:
		<REMV (Project ID) (Task ID)
		Ex: <REMV 1 9>
	
	Move a task to a different stage
		<MOVE (Project ID) (Task ID) (Destination Stage Name)>
		Ex: <MOVE 1 22 done>
	
	Ping a user with a message:
		<PING (Recipient Username) (Message)>
		<PING haddockcl You're a nerd>
