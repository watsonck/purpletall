CREATE TABLE Task  (id      	 SERIAL PRIMARY KEY,
    		    name	 VARCHAR(20)
		    description	 TEXT,
		    stage	 VARCHAR(4),
		    startTime    TIMESTAMP
		    exptCompTime 
		    actCompTime
    );



CREATE TABLE Users (userId  SERIAL PRIMARY KEY,
  		    fname   VARCHAR(10),
		    lname   VARCHAR(10),
		    email   VARCHAR(30),
		    gitname VARCHAR(20)
  );


CREATE TABLE Logs  (taskId
  		    contributor
		    action
		    time
		    comments
