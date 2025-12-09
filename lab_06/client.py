import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Twój klient działa. Wpisz papier/kamień/nożyce lub koniec.")

    while True:
        wybor = input("Twój ruch: ").strip().lower()

        client.sendto(wybor.encode(), (SERVER_IP, SERVER_PORT))

        if wybor == "koniec":
            print("Kończysz grę.")
            break

        # czekamy na odpowiedź
        msg, _ = client.recvfrom(1024)
        msg = msg.decode()

        if msg == "koniec":
            print("Gra zakończona przez jednego z graczy.")
            break

        print("Wynik rundy:", msg)

    client.close()


if __name__ == "__main__":
    main()
