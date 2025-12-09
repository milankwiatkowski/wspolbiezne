from ipcqueue import sysvmq
import os

KEY_IN = 0x1234
mq_in = sysvmq.Queue(KEY_IN)

PID = os.getpid()
mq_in.put(PID, b"stop")

print("STOP wysłany.")
