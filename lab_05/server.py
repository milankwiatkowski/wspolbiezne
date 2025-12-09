from ipcqueue import sysvmq
import time

KEY_IN  = 0x1234
KEY_OUT = 0x5678

mq_in  = sysvmq.Queue(KEY_IN,  create=True)
mq_out = sysvmq.Queue(KEY_OUT, create=True)

capitals = {
    "Polska": "Warszawa",
    "Niemcy": "Berlin",
    "Francja": "Paryż",
    "Hiszpania": "Madryt"
}

print("Serwer działa...")

while True:
    mtype, raw = mq_in.get()
    text = raw.decode()

    print(f"[SERWER] PID={mtype}, pytanie: {text}")

    if text == "stop":
        print("Usuwam kolejki i kończę...")
        mq_in.remove()
        mq_out.remove()
        break

    time.sleep(2)

    answer = capitals.get(text, "Nie wiem")
    mq_out.put(mtype, answer.encode())

    print(f"[SERWER] Odpowiedź dla PID={mtype}: {answer}")
