import os
import time
import errno
def funkcja(x):
    time.sleep(2)
    d = ""
    for elems in x:
        d += str(elems)
    return d
try:
    fd = os.open("bufor_serwera.txt", os.O_CREAT | os.O_RDWR)
    os.close(fd)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise
while True:
    try:
        fd = os.open("bufor_serwera.txt", os.O_RDONLY|os.O_EXCL)
        dlugosc = os.path.getsize("bufor_serwera.txt")
        data = os.read(fd,dlugosc).decode().strip()
        data = data.split("\n")
        os.close(fd)
        if not data:
            time.sleep(0.5)
            continue
        if(data[len(data)-1]=="ESC"):
            try:
                fd2 = os.open(data[0], os.O_CREAT | os.O_RDWR | os.O_TRUNC)
                wartosc = data[1:len(data)-1]
                os.write(fd2, str(funkcja(wartosc)).encode("utf-8"))
                print(str(funkcja(wartosc)))
                os.close(fd2)
                os.unlink("lockfile")
                fd3 = os.open("bufor_serwera.txt", os.O_WRONLY | os.O_TRUNC)
                os.close(fd3)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        else:
            time.sleep(0.3)
    except FileNotFoundError:
        time.sleep(0.01)
    time.sleep(0.5)
