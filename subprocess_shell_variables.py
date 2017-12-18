import os
import signal
import subprocess
import time
import sys

proc = subprocess.Popen(['python3', 'second_shell_subprocess.py'])
print('PARENT      : Pausing before sending signal...')
sys.stdout.flush()
time.sleep(10)
print('PARENT      : Signaling child 1')
sys.stdout.flush()
os.kill(proc.pid, signal.SIGTERM)
time.sleep(10)
print('PARENT      : Signaling child 2')
sys.stdout.flush()
os.kill(proc.pid, signal.SIGUSR1)
print('End of parent process')
sys.stdout.flush()