import os

def child():
    print('\n new child ', os.getpid())
    os._exit(0)

def parent():
    parentread,childwrite = os.pipe()
    parentwrite,childread = os.pipe()
    pid = os.fork()
    if pid == 0:
        child()
    else:
        print('parent ', os.getpid())
        print('child ', pid)
        os._exit(0)

parent()

#https://www.python-course.eu/pipes.php
#https://www.python-course.eu/forking.php
#https://www.google.com/search?client=firefox-b-1-d&q=set+up+socket+between+python+and+c%2B%2B
