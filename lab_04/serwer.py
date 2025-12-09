import os
import time
import errno
data = []
data.append({"id": 1, "name": "Kwiatkowski"})
data.append({"id": 2, "name": "Nowak"})
data.append({"id": 3, "name": "Bukalska"})
data.append({"id": 4, "name": "Głodnicki"})
data.append({"id": 5, "name": "Wiktorowicz"})
data.append({"id": 6, "name": "Zieliński"})
data.append({"id": 7, "name": "Adamska"})
data.append({"id": 8, "name": "Kowalski"})

FIFO = "/tmp/fifo_serwer"
FIFO1 = ""
FIFO2 = ""
try:
    os.mkfifo(FIFO)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise
fifo_in = os.open(FIFO, os.O_RDONLY| os.O_NONBLOCK)
print("Serwer uruchomiony, oczekiwanie na dane...")
fifo_dummy = os.open(FIFO, os.O_WRONLY | os.O_NONBLOCK)
while True:
    try:
        dane = os.read(fifo_in, 1024).decode().strip()
        print("Otrzymano dane od klienta: ", dane)
        dane = dane.split(" ")
        FIFO1 = dane[1]
        if_found=False
        for elems in data:
            if str(elems["id"])==dane[0]:
                if_found=True
                fifo_out = os.open(FIFO1, os.O_WRONLY)
                os.write(fifo_out, elems["name"].encode())
                os.close(fifo_out)
                break
        if not if_found:
            fifo_out = os.open(FIFO1, os.O_WRONLY)
            os.write(fifo_out, "Nie ma".encode())
            os.close(fifo_out)
    except Exception as e:
        continue
os.close(fifo_in)