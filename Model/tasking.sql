


CREATE TABLE Task  (id			SERIAL PRIMARY KEY,
    		    name		VARCHAR(20),
		    description		TEXT,
		    stage		VARCHAR(4),
		    startTime		TEXT,
		    exptCompTime	TEXT,
		    actCompTime		TEXT
    );

CREATE TABLE Users (userId		SERIAL PRIMARY KEY,
  		    fname		VARCHAR(10),
		    lname		VARCHAR(10),
		    email		VARCHAR(30),
		    gitname		VARCHAR(20)
    );

CREATE TABLE Logs  (taskId		SERIAL,
  		    contributor		SERIAL REFERENCES Users (userId),
		    action		TEXT,
		    time		TEXT,
		    comments		TEXT,
		    PRIMARY KEY(taskId, time)
    );

CREATE TABLE Projects (projId		SERIAL PRIMARY KEY,
    		       name		VARCHAR(30),
		       description	TEXT
    );

CREATE TABLE Stages (projId		SERIAL,
    		     stageName		VARCHAR,
		     stageOrder		INTEGER,
		     PRIMARY KEY(projId, stageName)
    );

ALTER TABLE Logs ADD FOREIGN KEY (taskId) REFERENCES Task(id);
ALTER TABLE Stages ADD FOREIGN KEY (projId) REFERENCES Projects(projId);

INSERT INTO Users (fname, lname, email, gitname) VALUES ('Colin', 'Watson', 'colin.watson777@yahoo.com', 'watsonck');
INSERT INTO Users (fname, lname, email, gitname) VALUES ('Cameron', 'Haddock', 'cameron.haddock@live.longwood.edu', 'TheBiggerFish');
INSERT INTO Users (fname, lname, email, gitname) VALUES ('Ryan'. 'White', 'ryan.white@live.longwood.edu','whitebryan');
INSERT INTO Users (fname, lname, email, gitname) VALUES ('Micheal', 'Montgomery', 'soul4hdwn@gmail', 'soul4hdwn');
INSERT INTO Users (fname, lname, email, gitname) VALUES ('Brendan', 'Speed', 'bredan.speed@live.longwood.edu','Iridium12');
INSERT INTO Users (fname, lname, email, gitname) VALUES ('Shyheim', 'Williams', 'shyheim.williams@live.longwood.edu', 'steelairship');

INSERT INTO Projects(name, description) VALUES ('Testing Project','a project made to test program');

INSERT INTO Stages(projId, stageName, stageOrder) VALUES(1,'start',0);
INSERT INTO Stages(projId, stageName, stageOrder) VALUES(1, 'todo',1);
INSERT INTO Stages(projId, stageName, stageOrder) VALUES(1, 'Done',2);
