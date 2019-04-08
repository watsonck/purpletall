Currently only a kanban board

Non case sensitive comands:
ADD : followed by your task 
	ADD This new task
	ADD <Task> <Desc> <Expected completion> <Is_Bug>
MOVE : followed by the task number then destination
	MOVE 0 todo comp
	MOVE <task_id> <to>
REMV : Removes task
	REMV 0 comp
	REMV <task_id> 
SPLT : Splits task into 2 tasks
	SPLT 0 comp Task1 Task2
	SPLT <task_id> 
PROJ: Changes projects
	PROJ 1
	PROJ <proj_id>
INFO: Displays more info about Task
	INFO 1
	INFO <task_id>
QUIT : Exits the kanaban loop 
