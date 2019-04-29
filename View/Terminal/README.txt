Currently only a kanban board

Non case sensitive comands:
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
	QUIT : Exits the kanaban loop 

COMMANDS NOT YET IMPLEMENTED:
PING: Send an email to a user
	PING haddockcl This is a ping
	PING <recipient> <message>
	http://purpletall.cs.longwood.edu:5000/ping?user=2&rcvr={haddockcl}&msg={This%20is%20a%20ping}
LOG: Log has been modified to also return a log of movements done to an item. View for info needs to be updated to display log