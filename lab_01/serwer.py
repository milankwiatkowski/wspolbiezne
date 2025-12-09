import os
import time
import errno
def funkcja(x):
    return x**2
while True:
    try:
        fd = os.open("plikDane.txt", os.O_RDONLY|os.O_EXCL)
        data = os.read(fd,10).decode().strip()
        os.close(fd)
        if not data:
            time.sleep(0.5)
            continue
        try:
            fd2 = os.open("plikWynik.txt", os.O_CREAT | os.O_RDWR | os.O_TRUNC)
            liczba = int(data)
            os.write(fd2, str(funkcja(liczba)).encode("utf-8"))
            os.close(fd2)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    except FileNotFoundError:
        time.sleep(0.01)
    time.sleep(0.5)
