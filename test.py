"""
Proof of concept for Threaded Downloads
"""

from urllib3 import PoolManager
import click
import threading
from time import time
from tqdm import tqdm
from sys import exit


buffdict = {}


"""
def thrdpull(qantindx, httpobjc, urllocat, srcebyte, destbyte, strmsize):
    print("Execution of thread #" + str(qantindx) + " is in progress...")
    thrdrqst = httpobjc.request("GET", urllocat, preload_content=False, headers={"range":"bytes=" + str(srcebyte) + "-" + str(destbyte) + ""})
    partsize = destbyte - srcebyte
    respdata = b""
    with click.progressbar(
        thrdrqst.stream(strmsize),
        length=partsize,
        fill_char="#",
        label="RECEIVED 0/0 bytes",
        bar_template="%(label)s [%(bar)s] %(info)s"
    ) as progelem:
        for filepeic in progelem:
            respdata += filepeic
            progelem.update(len(filepeic))
            progelem.label = click.style("RECEIVED", fg="magenta", bold=True) + " " + \
                             click.style(str(len(respdata)) + "/" + str(partsize) + " bytes")
    buffdict[qantindx] = respdata
"""


def thrdpull(qantindx, httpobjc, urllocat, srcebyte, destbyte, strmsize):
    thrdrqst = httpobjc.request("GET", urllocat, preload_content=False, headers={"range":"bytes=" + str(srcebyte) + "-" + str(destbyte) + ""})
    partsize = destbyte - srcebyte
    respdata = b""
    progelem = tqdm(thrdrqst.stream(strmsize), desc=click.style("STARTING", fg="yellow", bold=True), leave=False)
    for filepeic in progelem:
        respdata += filepeic
        progelem.set_description(
            click.style("RECEIVED", fg="magenta", bold=True) + " " +
            click.style(str(len(respdata)) + "/" + str(partsize) + " bytes")
        )
    progelem.close()
    buffdict[qantindx] = respdata


if __name__ == "__main__":
    httpobjc = PoolManager(num_pools=128)
    strmsize = 1048576
    """
    urllocat = "https://chromium.arnoldthebat.co.uk/weekly//CARMOS-20210124200101.img.7z"
    dividend = 10
    """
    urllocat = "https://speed.hetzner.de/100MB.bin"
    rqstobjc = httpobjc.request("GET", urllocat, preload_content=False)
    filesize = int(rqstobjc.headers.get("Content-Length"))
    filebuff = b""
    print("File size is " + str(filesize) + " bytes\nMaking 100 threads for equal-sized transfers...")
    indxlist, dividend = [], filesize // 100
    print("Calculating download checkpoints for each thread...")
    for indx in range(0, filesize, dividend):
        indxlist.append((indx, indx + dividend))
    thrdlist = []
    print("Populating threads in a list...")
    for indx in range(len(indxlist)):
        thrdobjc = threading.Thread(target=thrdpull, args=(indx, httpobjc, urllocat, indxlist[indx][0], indxlist[indx][1], strmsize))
        thrdlist.append(thrdobjc)
    print("Starting execution now...")
    strttime = time()
    for indx in thrdlist:
        indx.start()
    print("Concluding execution now...")
    for indx in thrdlist:
        indx.join()
    stoptime = time()
    duration = stoptime - strttime
    for indx in buffdict.keys():
        filebuff += buffdict[indx]
    print("\r\r", end="")
    print(len(filebuff))
    #rqstobjc = httpobjc.request("GET", "https://github.com/cdr/code-server/releases/download/v3.9.0/code-server-3.9.0-amd64.rpm", preload_content=False, headers={"range":"bytes=30-1000"})
    #print(dir(rqstobjc))
    print("Finished in", duration)
