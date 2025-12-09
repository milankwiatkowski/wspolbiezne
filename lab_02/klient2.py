import os
import time
import errno
while True:
    try:
        fd = os.open("lockfile", os.O_CREAT|os.O_EXCL|os.O_RDWR)
        os.close(fd)
        print("Utworzono lockfile")
        try:
            fd2 = os.open("bufor_serwera.txt", os.O_WRONLY | os.O_TRUNC)
            writefile = "klient2_answer.txt"
            os.write(fd2,writefile.encode("utf-8"))
            while True:
                n = input("Podaj dane: ")
                if(n=="ESC"):
                    os.write(fd2,"\n".encode("utf-8"))
                    os.write(fd2,str(n).encode("utf-8"))
                    break
                os.write(fd2,"\n".encode("utf-8"))
                os.write(fd2,str(n).encode("utf-8"))
            print("Zapisano dane do bufora serwera")
            os.close(fd2)
            break
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Error")
        print("Lockfile istnieje, czekam...")
        time.sleep(1)