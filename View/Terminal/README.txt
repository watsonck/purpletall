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


COMMANDS NOT YET IMPLEMENTED:
SCOL: Swap 2 column positions on board
	SCOL todo done
	SCOL <col_name1> <col_name2>
	http://purpletall.cs.longwood.edu:5000/1/swap?stage1={todo}&stage2={Done}
PING: Send an email to a user
	PING haddockcl This is a ping
	PING <recipient> <message>
	http://purpletall.cs.longwood.edu:5000/ping?user=2&rcvr={haddockcl}&msg={This%20is%20a%20ping}
LOG: Log has been modified to also return a log of movements done to an item. View for info needs to be updated to display log
CREATE USER: Create a new user using this request format
	http://purpletall.cs.longwood.edu:5000/user?fname={Student}&lname={McStudentpants}&uname={imastudent}&email={student.mcstudentpants%40live.longwood.edu}
	Ensure that in the email address the @ symbol is replaced with %40
ADD PROJECT:
	http://purpletall.cs.longwood.edu:5000/newproj?name={Project%20Manager}&desc={This%20is%20a%20project%20management%20system}
DELETE PROJECT:
	http://purpletall.cs.longwood.edu:5000/delproj?id=3
