Currently only a kanban board

Non case sensitive comands:
ADD : followed by your task 
	ADD Task1  2019 false This thing is broken
	ADD <name> <expected comp> <is_bug> <desc>
MOVE : followed by the task number then destination
	MOVE 0 comp
	MOVE <task_id> <to>
REMV : Removes task
	REMV 0 comp
	REMV <task_id> 
SPLT : Splits task into 2 tasks
	SPLT 0 
	SPLT <task_id> 
PROJ: Changes projects
	PROJ 1
	PROJ <proj_id>
INFO: Displays more info about Task
	INFO 1
	INFO <task_id>
QUIT : Exits the kanaban loop 
