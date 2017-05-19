import os
import shutil
import subprocess
import datetime
import time
from threading import Thread
from threading import Lock

cur_path = os.path.abspath(os.curdir)
path = 'deploy\\tomcat'
rm_list = ['shared\\lib', 'webapps\\app', 'webapps\\app-core',
           'webapps\\app-mobile', 'webapps\\app-portal']
lock = Lock()

context_path = os.path.join(cur_path, path, 'webapps\\app-core\\META-INF\\context.xml')
context_path_temp = os.path.join(cur_path, path, 'context.xml')
shutil.copy(context_path, context_path_temp)


def context_replacer():
    while True:
        try:
            time.sleep(2)
            os.remove(context_path)
            shutil.copy(os.path.join(cur_path, path, 'context.xml'), context_path)
            break
        except FileNotFoundError:
            pass


def gradle_update():
    global lock
    lock.acquire(blocking=False)
    subprocess.call(['cmd.exe', '/C', 'gradle clean restart'])
    time = datetime.datetime.today()
    print('Updated at {0}'.format(time.ctime()))


for directory in rm_list:
    full_path = os.path.join(cur_path, path, directory)
    loop_checker = True
    while loop_checker:
        try:
            shutil.rmtree(full_path)
            loop_checker = False
        except FileNotFoundError:
            loop_checker = False
        except OSError:
            pass
checker = subprocess.call(['cmd.exe', '/C', 'git pull'])
if checker != 0:
    subprocess.call(['cmd.exe', '/C', 'svn update'])

t1 = Thread(target=context_replacer)
t2 = Thread(target=gradle_update)

t2.start()
t1.start()
t1.join()
t2.join()

os.remove(context_path_temp)
