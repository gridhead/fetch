from os import system
from time import time

if __name__ == "__main__":
    strttime = time()
    system("wget https://speed.hetzner.de/100MB.bin")
    stoptime = time()
    duration = stoptime - strttime
    print(duration)
