import os
plik = os.open("plikA.txt",os.O_RDONLY)
opened = os.open("output.txt",os.O_CREAT|os.O_RDONLY|os.O_TRUNC)
data = os.read(plik,os.path.getsize("plikA.txt")).decode().strip().split()
os.close(plik)
for i in range(len(data)):
    if data[i].startswith("\\"):
        data[i] = data[i][7:len(data[i])-1]
def loopcheck(dane):
    for i in range(len(dane)):
        if dane[i].startswith("\\"):
            dane[i] = dane[i][7:len(dane[i])-1]
    for elems in dane:
        if elems.startswith("plik"):
            elems = elems.strip("}")
            pid = os.fork()
            if(pid>0):
                os.wait()
            else:
                plik2 = os.open(elems,os.O_RDONLY)
                data2 = os.read(plik2,os.path.getsize(elems)).decode().strip().split()
                os.close(plik2)
                loopcheck(data2)
                os._exit(0)
        else:
            plik_z_danymi=os.open("output.txt",os.O_CREAT|os.O_RDWR|os.O_APPEND)
            os.write(plik_z_danymi,(elems+" ").encode("utf-8"))
            os.close(plik_z_danymi)
loopcheck(data)
output = os.read(opened,os.path.getsize("output.txt"))
output = output.decode().strip()
print(output)
os.unlink("output.txt")