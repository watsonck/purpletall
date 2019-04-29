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


How to use:
1) Start the controller:
	cd Controller
	python3 Controller.py
2) Open another Terminal.
3) Start the view:
	cd View/Terminal
	python3 curses_console.py
	
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

COMMANDS NOT YET IMPLEMENTED:
LOG: Log has been modified to also return a log of movements done to an item. View for info needs to be updated to display log