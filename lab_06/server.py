import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000

# Wyniki gry
def wynik(a, b):
    if a == b:
        return 0
    if (a == "papier" and b == "kamień") or \
       (a == "kamień" and b == "nożyce") or \
       (a == "nożyce" and b == "papier"):
        return 1
    return -1


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((SERVER_IP, SERVER_PORT))

    print("Serwer uruchomiony na 127.0.0.1:5000, oczekiwanie na 2 graczy...")

    players = []
    choices = {}
    points = {}

    while True:
        msg, addr = server.recvfrom(1024)
        msg = msg.decode()

        # Jeśli dołącza nowy gracz
        if addr not in players:
            players.append(addr)
            points[addr] = 0
            print(f"Dołączył nowy gracz: {addr}")

        # Jeśli mamy dwóch graczy, zbieramy wybory
        choices[addr] = msg

        # Sprawdzamy, czy obaj już odpowiedzieli
        if len(players) == 2 and len(choices) == 2:
            p1, p2 = players[0], players[1]
            c1, c2 = choices[p1], choices[p2]

            print(f"Runda: {p1} -> {c1}, {p2} -> {c2}")

            # przypadki zakończenia gry
            if c1 == "koniec" and c2 == "koniec":
                print("Obaj gracze zakończyli grę.")
                server.sendto("koniec".encode(), p1)
                server.sendto("koniec".encode(), p2)

                # reset
                players.clear()
                choices.clear()
                points.clear()
                print("\nOczekiwanie na nową parę graczy...\n")
                continue

            if c1 == "koniec":
                print("Gracz 1 zakończył grę.")
                server.sendto("koniec".encode(), p1)
                server.sendto("koniec".encode(), p2)

                players.clear()
                choices.clear()
                points.clear()
                continue

            if c2 == "koniec":
                print("Gracz 2 zakończył grę.")
                server.sendto("koniec".encode(), p1)
                server.sendto("koniec".encode(), p2)

                players.clear()
                choices.clear()
                points.clear()
                continue

            # normalna runda
            w = wynik(c1, c2)
            if w == 1:
                points[p1] += 1
                result1 = f"Wygrałeś! ({c1} vs {c2}) | Punkty: {points[p1]}"
                result2 = f"Przegrałeś! ({c2} vs {c1}) | Punkty: {points[p2]}"
            elif w == -1:
                points[p2] += 1
                result1 = f"Przegrałeś! ({c1} vs {c2}) | Punkty: {points[p1]}"
                result2 = f"Wygrałeś! ({c2} vs {c1}) | Punkty: {points[p2]}"
            else:
                result1 = result2 = f"Remis! ({c1} vs {c2}) | Punkty: {points[p1]} : {points[p2]}"

            print(f"Punkty: {p1} = {points[p1]}, {p2} = {points[p2]}")

            # odesłanie wyników
            server.sendto(result1.encode(), p1)
            server.sendto(result2.encode(), p2)

            # Czyścimy wybory na kolejną rundę
            choices.clear()


if __name__ == "__main__":
    main()
