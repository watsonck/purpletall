Currently only a kanban board

Non case sensitive comands:
ADD : followed by your task 
	ADD This new task
	ADD <Task>
MOVE : followed by the task number then destination
	MOVE 0 todo comp
	MOVE <task_id> <from> <to>
REMV : Removes task
	REMV 0 comp
	REMV <task_id> <area>
SPLT : Splits task into 2 tasks
	SPLT 0 comp Task1 Task2
	SPLT <task_id> <Task1> <Task2>
QUIT : Exits the kanaban loop 