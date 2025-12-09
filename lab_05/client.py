from ipcqueue import sysvmq
import os
import time

KEY_IN  = 0x1234
KEY_OUT = 0x5678

mq_in  = sysvmq.Queue(KEY_IN)
mq_out = sysvmq.Queue(KEY_OUT)

PID = os.getpid()
question = "Polska"

print(f"[KLIENT {PID}] Start")

for i in range(10):
    mq_in.put(PID, question.encode())
    print(f"[KLIENT {PID}] Wysłałem zapytanie {i+1}")
    time.sleep(1)

print(f"[KLIENT {PID}] Oczekuję na odpowiedzi...")

answers = []
for i in range(10):
    mtype, msg = mq_out.get(type=PID)
    answers.append(msg.decode())

print("Odpowiedzi klienta", PID)
for a in answers:
    print(" →", a)
