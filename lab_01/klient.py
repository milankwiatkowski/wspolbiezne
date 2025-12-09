import os
import time
import errno
while True:
    try:
        fd = os.open("plikDane.txt", os.O_CREAT|os.O_EXCL|os.O_RDWR)
        print("Utworzono plik z danymi od użytkownika")
        n = int(input())
        os.write(fd,str(n).encode("utf-8"))
        print("Zapisano dane od użytkownika")
        break
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
        else:
            os.unlink("plikDane.txt")
        time.sleep(0.05)
while True:
    try:
        time.sleep(0.5)
        fd = os.open("plikWynik.txt", os.O_RDONLY)
        data = os.read(fd, 10).decode().strip()
        print(data)
        break
    except FileNotFoundError:
        time.sleep(0.01)
os.close(fd)