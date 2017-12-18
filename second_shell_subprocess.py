import os
import signal
import time
import sys

pid = os.getpid()
received = False


def signal_usr1(signum, frame):
    "Callback invoked when a signal is received %d" % signum
    global received
    received = True
    if signum == signal.SIGUSR1:
    	print('CHILD {:>6}: Received USR1'.format(pid))
    	sys.stdout.flush()
    else:
    	print('CHILD {:>6}: Im not concerned with this signal'.format(pid))
    	sys.stdout.flush()
    	signal.pause()


print('CHILD {:>6}: Setting up signal handler'.format(pid))
sys.stdout.flush()
signal.signal(signal.SIGUSR1, signal_usr1)
print('CHILD {:>6}: Pausing to wait for signal'.format(pid))
sys.stdout.flush()
signal.pause()
#time.sleep(15)

#if not received:
#    print('CHILD {:>6}: Never received signal'.format(pid))

print('CHILD {:>6}: End of subprocess ...'.format(pid))
sys.stdout.flush()