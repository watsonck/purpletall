# purpletall
A project management system

Contributors to Controller: 
  Cameron Haddock

Contributors to View (Terminal and Web): 
  Ryan White
  Alex Sedgwick
  Michael Montgomery
  Shyheim Williams

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
Non case sensitive comands:
ADD: followed by your task 
	ADD Task1  2019 false This thing is broken
	ADD <name> <expected comp> <is_bug> <desc>
MOVE : followed by the task number then destination
	MOVE 0 comp
	MOVE <task_id> <to>
REMV: Removes task
	REMV 0 comp
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
