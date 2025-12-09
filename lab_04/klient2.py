import os
import time
import errno
FIFO = "/tmp/fifo_klient2"
FIFO_SERWER = "/tmp/fifo_serwer"
try:
    os.mkfifo(FIFO)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise
fifo_out = os.open(FIFO_SERWER, os.O_WRONLY)
dane = input("Podaj id do sprawdzenia: ")
dane = dane + " " + FIFO
os.write(fifo_out, dane.encode())
os.close(fifo_out)
print("Wyslano dane do serwera, czekam na odpowiedz...")
try:
    fifo_in = os.open(FIFO, os.O_RDONLY)
    odpowiedz = os.read(fifo_in, 1024).decode()
    os.close(fifo_in)
    print("Odpowiedz serwera: ", odpowiedz)
except Exception as e:
    print("Blad podczas odczytu odpowiedzi serwera, ponawiam proba...")
    if e.errno != errno.EEXIST:
        raise