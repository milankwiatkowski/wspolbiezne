#!/usr/bin/env python3
import sys
import time
import sysv_ipc

KEY_ROLE_SEM     = 0x1000  # semafor do "wyścigu" o bycie Graczem 1
KEY_SHM_PW1      = 0x2001  # pamięć współdzielona na wybór Gracza 1
KEY_SHM_PW2      = 0x2002  # pamięć współdzielona na wybór Gracza 2
KEY_SEM_PW1_WR   = 0x3001  # "PW1 gotowe" (Gracz 1 -> Gracz 2)
KEY_SEM_PW2_WR   = 0x3002  # "PW2 gotowe" (Gracz 2 -> Gracz 1)
KEY_SEM_AFTER_R1 = 0x3003  # "G1 przeczytał PW2" (Gracz 1 -> Gracz 2)
KEY_SEM_AFTER_R2 = 0x3004  # "G2 przeczytał PW1" (Gracz 2 -> Gracz 1)

SHM_SIZE = 16  # spokojnie wystarczy na zapis liczby jako tekstu


def ask_choice(prompt: str) -> int:
    while True:
        try:
            val = int(input(prompt))
            if val in (1, 2, 3):
                return val
            print("Wpisz liczbę 1, 2 albo 3.")
        except ValueError:
            print("To nie jest poprawna liczba. Spróbuj jeszcze raz.")


def shm_write_int(shm: sysv_ipc.SharedMemory, value: int):
    data = str(value).encode("utf-8").ljust(SHM_SIZE, b"\x00")
    shm.write(data)


def shm_read_int(shm: sysv_ipc.SharedMemory) -> int:
    data = shm.read(SHM_SIZE)
    text = data.decode("utf-8").strip("\x00").strip()
    return int(text)


def attach_shm(key):
    while True:
        try:
            return sysv_ipc.SharedMemory(key)
        except sysv_ipc.ExistentialError:
            time.sleep(0.1)


def attach_sem(key):
    while True:
        try:
            return sysv_ipc.Semaphore(key)
        except sysv_ipc.ExistentialError:
            time.sleep(0.1)


def main():
    print("Uruchamianie gry w trzy karty (IPC: pamięć współdzielona + semafory)...")

    try:
        # Jeśli uda się utworzyć semafor z IPC_CREX, jesteśmy pierwsi => Gracz 1
        role_sem = sysv_ipc.Semaphore(
            KEY_ROLE_SEM,
            sysv_ipc.IPC_CREX,
            initial_value=1
        )
        is_player1 = True
        print(">>> Jesteś Graczem 1 (utworzyłeś semafor wyścigu).")
    except sysv_ipc.ExistentialError:
        # Semafor już istnieje -> ktoś był pierwszy
        role_sem = sysv_ipc.Semaphore(KEY_ROLE_SEM)
        is_player1 = False
        print(">>> Jesteś Graczem 2 (Gracz 1 już wystartował).")

    # ----------------- TWORZENIE / DOŁĄCZANIE do IPC -----------------
    if is_player1:
        # Gracz 1 tworzy pamięci współdzielone i semafory
        shm_pw1 = sysv_ipc.SharedMemory(KEY_SHM_PW1, sysv_ipc.IPC_CREX, size=SHM_SIZE)
        shm_pw2 = sysv_ipc.SharedMemory(KEY_SHM_PW2, sysv_ipc.IPC_CREX, size=SHM_SIZE)

        sem_pw1_written = sysv_ipc.Semaphore(KEY_SEM_PW1_WR, sysv_ipc.IPC_CREX, initial_value=0)
        sem_pw2_written = sysv_ipc.Semaphore(KEY_SEM_PW2_WR, sysv_ipc.IPC_CREX, initial_value=0)
        sem_after_read1 = sysv_ipc.Semaphore(KEY_SEM_AFTER_R1, sysv_ipc.IPC_CREX, initial_value=0)
        sem_after_read2 = sysv_ipc.Semaphore(KEY_SEM_AFTER_R2, sysv_ipc.IPC_CREX, initial_value=0)

    else:
        # Gracz 2 czeka aż G1 stworzy wszystko i się dołącza
        print("Czekam, aż Gracz 1 stworzy pamięci i semafory...")
        shm_pw1 = attach_shm(KEY_SHM_PW1)
        shm_pw2 = attach_shm(KEY_SHM_PW2)

        sem_pw1_written = attach_sem(KEY_SEM_PW1_WR)
        sem_pw2_written = attach_sem(KEY_SEM_PW2_WR)
        sem_after_read1 = attach_sem(KEY_SEM_AFTER_R1)
        sem_after_read2 = attach_sem(KEY_SEM_AFTER_R2)

    print("IPC gotowe, można zaczynać grę.")
    print("Zasady: jeśli obaj wybierzecie tę samą pozycję, wygrywa Gracz 2, inaczej wygrywa Gracz 1.\n")

    # ----------------- LOGIKA GRY -----------------
    rounds = 3
    score_p1 = 0
    score_p2 = 0

    for tura in range(1, rounds + 1):
        print(f"\n=========== TURA {tura} ===========")

        if is_player1:
            # --- Krok 1: Gracz 1 wybiera i zapisuje do PW1 ---
            my_choice = ask_choice("Gracz 1: wybierz pozycję wygrywającej karty (1, 2 lub 3): ")
            shm_write_int(shm_pw1, my_choice)
            # powiadom Gracza 2, że PW1 jest gotowe
            sem_pw1_written.release()

            # --- Krok 3: czekaj aż Gracz 2 zapisze PW2 i odczytaj ---
            sem_pw2_written.acquire()
            g2_choice = shm_read_int(shm_pw2)

            # Oblicz wynik tury
            if my_choice == g2_choice:
                # Gracz 2 trafił
                score_p2 += 1
                result = "Przegrałeś tę turę (Gracz 2 trafił)."
            else:
                score_p1 += 1
                result = "Wygrałeś tę turę (Gracz 2 nie trafił)."

            # Informacja dla Gracza 1
            print(f"[G1] Twój wybór: {my_choice}, wybór Gracza 2: {g2_choice}")
            print(f"[G1] {result}")
            print(f"[G1] Wynik sumaryczny: Gracz 1 = {score_p1}, Gracz 2 = {score_p2}")

            # sygnalizuj G2, że G1 już przeczytał PW2
            sem_after_read1.release()
            # poczekaj aż G2 przeczyta PW1
            sem_after_read2.acquire()

        else:
            # --- Krok 2: Gracz 2 czeka, aż PW1 będzie gotowe, wybiera i zapisuje do PW2 ---
            sem_pw1_written.acquire()
            my_choice = ask_choice("Gracz 2: spróbuj odgadnąć pozycję (1, 2 lub 3): ")
            shm_write_int(shm_pw2, my_choice)
            # powiadom Gracza 1, że PW2 jest gotowe
            sem_pw2_written.release()

            # --- Krok 4: poczekaj aż Gracz 1 przeczyta PW2, potem odczytaj PW1 ---
            sem_after_read1.acquire()
            g1_choice = shm_read_int(shm_pw1)

            # Oblicz wynik tury
            if g1_choice == my_choice:
                score_p2 += 1
                result = "Wygrałeś tę turę (trafiłeś!)."
            else:
                score_p1 += 1
                result = "Przegrałeś tę turę (nie trafiłeś)."

            # Informacja dla Gracza 2
            print(f"[G2] Wybór Gracza 1: {g1_choice}, Twój wybór: {my_choice}")
            print(f"[G2] {result}")
            print(f"[G2] Wynik sumaryczny: Gracz 1 = {score_p1}, Gracz 2 = {score_p2}")

            # sygnalizuj G1, że G2 przeczytał PW1 i można zacząć następną turę
            sem_after_read2.release()

    # ----------------- KONIEC GRY -----------------
    print("\n=========== KONIEC GRY ===========")
    print(f"Końcowy wynik: Gracz 1 = {score_p1}, Gracz 2 = {score_p2}")
    if is_player1:
        if score_p1 > score_p2:
            print("Wygrywa Gracz 1!")
        elif score_p2 > score_p1:
            print("Wygrywa Gracz 2!")
        else:
            print("Remis!")

    # Sprzątanie IPC – robi to tylko Gracz 1
    if is_player1:
        print("\nSprzątanie zasobów IPC (pamięci i semaforów)...")
        try:
            shm_pw1.remove()
        except Exception:
            pass
        try:
            shm_pw2.remove()
        except Exception:
            pass

        for sem in (sem_pw1_written, sem_pw2_written, sem_after_read1, sem_after_read2, role_sem):
            try:
                sem.remove()
            except Exception:
                pass

        print("Zasoby IPC zostały usunięte.")

    print("Zamykanie programu.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrzerwano klawiszem Ctrl+C.")
        sys.exit(0)
