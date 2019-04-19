DROP TABLE IF EXISTS Projects CASCADE;
DROP TABLE IF EXISTS Task CASCADE;
DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS Logs CASCADE;
DROP TABLE IF EXISTS Stages;


CREATE TABLE Task  (id			SERIAL,
    		    projId		INTEGER,
    		    name		TEXT,
		    description		TEXT,
		    stage		TEXT,
		    startTime		TEXT,
		    exptCompTime	TEXT,
		    actCompTime		TEXT,
		    contributor		INTEGER,
		    bugged		BOOLEAN,
		    PRIMARY KEY(id, projId)
    );

CREATE TABLE Users (userId		SERIAL PRIMARY KEY,
  		    fname		TEXT,
		    lname		TEXT,
		    email		TEXT,
		    gitname		TEXT
    );

CREATE TABLE Logs  (taskId		INTEGER,
    		    projId		INTEGER,
  		    contributor		INTEGER REFERENCES Users (userId),
		    action		TEXT,
		    time		TEXT,
		    comments		TEXT,
		    PRIMARY KEY(taskId, time)
    );

CREATE TABLE Projects (projId		SERIAL PRIMARY KEY,
    		       name		TEXT,
		       description	TEXT
    );

CREATE TABLE Stages (projId		INTEGER,
    		     stageName		TEXT,
		     stageOrder		INTEGER,
		     PRIMARY KEY(projId, stageName)
    );

ALTER TABLE Logs ADD FOREIGN KEY (taskId, projId) REFERENCES Task(id, projId);
ALTER TABLE Stages ADD FOREIGN KEY (projId) REFERENCES Projects(projId);
ALTER TABLE Task ADD FOREIGN KEY (projId) REFERENCES Projects(projId);
ALTER TABLE Task ADD FOREIGN KEY (contributor) REFERENCES Users(userId);

INSERT INTO Users (fname, lname, email, gitname) VALUES ('Colin', 'Watson', 'colin.watson777@yahoo.com', 'watsonck');
INSERT INTO Users (fname, lname, email, gitname) VALUES ('Cameron', 'Haddock', 'cameron.haddock@live.longwood.edu', 'TheBiggerFish');
INSERT INTO Users (fname, lname, email, gitname) VALUES ('Ryan', 'White', 'ryan.white@live.longwood.edu','whitebryan');
INSERT INTO Users (fname, lname, email, gitname) VALUES ('Micheal', 'Montgomery', 'soul4hdwn@gmail', 'soul4hdwn');
INSERT INTO Users (fname, lname, email, gitname) VALUES ('Brendan', 'Speed', 'brendan.speed@live.longwood.edu','Iridium12');
INSERT INTO Users (fname, lname, email, gitname) VALUES ('Shyheim', 'Williams', 'shyheim.williams@live.longwood.edu', 'steelairship');

INSERT INTO Projects(name, description) VALUES ('Testing Project','a project made to test program');

INSERT INTO Stages(projId, stageName, stageOrder) VALUES(1,'start',0);
INSERT INTO Stages(projId, stageName, stageOrder) VALUES(1, 'todo',1);
INSERT INTO Stages(projId, stageName, stageOrder) VALUES(1, 'Done',2);

INSERT INTO Task(projId, name, description, stage, contributor) VALUES (1, 'TesterOne', 'Need to start this thing','todo',2);
INSERT INTO Task(projId, name, description, stage, contributor) VALUES (1, 'TestTwo', 'Heres somethiong else','start',2);
INSERT INTO Task(projId, name, description, stage, contributor) VALUES (1, 'TestThree','Last one','todo',2);

INSERT INTO Projects(name, description) VALUES ('Switching Project','a project made to test switching');

INSERT INTO Stages(projId, stageName, stageOrder) VALUES(2,'start',0);
INSERT INTO Stages(projId, stageName, stageOrder) VALUES(2, 'todo',1);
INSERT INTO Stages(projId, stageName, stageOrder) VALUES(2, 'Bugs',2);
INSERT INTO Stages(projId, stageName, stageOrder) VALUES(2, 'Done',3);

INSERT INTO Task(projId, name, description, stage, contributor) VALUES (2, 'TesterOne', 'Need to start this thing','todo',2);
INSERT INTO Task(projId, name, description, stage, contributor) VALUES (2, 'TestTwo', 'Heres somethiong else','start',2);
INSERT INTO Task(projId, name, description, stage, contributor) VALUES (2, 'TestThree','Last one','todo',2);
