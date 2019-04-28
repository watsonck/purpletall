Currently only a kanban board

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
DCOL: Delete column on kanban board
	DCOL Crap
	DCOL <col_name>
PROJ: Changes projects
	PROJ
INFO: Displays more info about Task
	INFO 1
	INFO <task_id>
QUIT : Exits the kanaban loop 
