"""
##########################################################################
*
*   Copyright © 2019-2021 Akashdeep Dhar <t0xic0der@fedoraproject.org>
*
*   This program is free software: you can redistribute it and/or modify
*   it under the terms of the GNU General Public License as published by
*   the Free Software Foundation, either version 3 of the License, or
*   (at your option) any later version.
*
*   This program is distributed in the hope that it will be useful,
*   but WITHOUT ANY WARRANTY; without even the implied warranty of
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*   GNU General Public License for more details.
*
*   You should have received a copy of the GNU General Public License
*   along with this program.  If not, see <https://www.gnu.org/licenses/>.
*
##########################################################################
"""

from urllib3 import PoolManager
import click
import threading
from time import time
from tqdm import tqdm
from sys import exit
from os.path import basename
from hashlib import sha256


"""
Notification Slugs

WARNING
FAILURE
SUCCESS
DETAILS
PROPERTY
RECEIVED
PATIENCE
COMPLETE
STARTING
"""


class Textface:
    def warnmesg(self, precursr, textmesg):
        return \
            click.style(precursr, fg="yellow", bold=True) + " " + \
            click.style(textmesg)

    def failmesg(self, precursr, textmesg):
        return \
            click.style(precursr, fg="red", bold=True) + " " + \
            click.style(textmesg)

    def succmesg(self, precursr, textmesg):
        return \
            click.style(precursr, fg="green", bold=True) + " " + \
            click.style(textmesg)

    def infomesg(self, precursr, textmesg):
        return \
            click.style(precursr, fg="blue", bold=True) + " " + \
            click.style(textmesg)

    def specmesg(self, precursr):
        return \
            click.style(precursr, fg="magenta", bold=True)

    def genrmesg(self, precursr, textmesg):
        return \
            click.style(precursr, bold=True) + " " + \
            click.style(textmesg)


class Singload:
    def __init__(self, fileloca, strmsize):
        self.httpobjc = PoolManager(num_pools=128)
        self.respdata = b""
        self.duraform = "0.00"
        self.rqstobjc = self.httpobjc.request("GET", fileloca, preload_content=False)
        self.strmsize = strmsize
        self.filename = basename(fileloca)
        # self.filename = self.rqstobjc.headers.get("Content-Disposition")
        self.filesize = self.rqstobjc.headers.get("Content-Length")
        if self.filesize is None or self.filename is None:
            click.echo(
                Textface().warnmesg(
                    "EXEMPLAR",
                    "Resource name and/or size could not be retrieved"
                )
            )
            exit()
        else:
            if (self.strmsize > int(self.filesize)):
                click.echo(
                    Textface().warnmesg(
                        "EXEMPLAR",
                        "Stream size is greater than the file size"
                    )
                )
                exit()
            else:
                click.echo(
                    Textface().infomesg(
                        "SINGLOAD",
                        self.filename + " [" + str(self.filesize) + "B/" + str(self.strmsize) + "S/1T]"
                    )
                )
                self.begindld()

    def begindld(self):
        strttime = time()
        progelem = tqdm(
            self.rqstobjc.stream(self.strmsize),
            desc=click.style("STARTING", fg="yellow", bold=True),
            colour="#008080",
            total=int(self.filesize),
            leave=False
        )
        for filepeic in progelem:
            self.respdata += filepeic
            progelem.set_description(
                Textface().specmesg(
                    "RECEIVED",
                )
            )
            progelem.update(len(filepeic))
        progelem.close()
        stoptime = time()
        duration = str(stoptime - strttime)
        self.duraform = duration
        self.savetest()

    def savetest(self):
        writstrg = "1," + str(self.duraform) + "," + sha256(self.respdata).hexdigest()
        with open(str(self.strmsize) + ".csv", "a") as fileobjc:
            fileobjc.write(writstrg + "\n")


class Multload:
    def __init__(self, fileloca, strmsize, thrdqant):
        self.httpobjc = PoolManager(num_pools=128)
        self.buffdict = {}
        self.duraform = "0.00"
        self.rqstobjc = self.httpobjc.request("GET", fileloca, preload_content=False)
        self.strmsize = strmsize
        self.fileloca = fileloca
        self.filename = basename(fileloca)
        self.thrdqant = thrdqant
        # self.filename = self.rqstobjc.headers.get("Content-Disposition")
        self.filesize = self.rqstobjc.headers.get("Content-Length")
        if self.filesize is None or self.filename is None:
            click.echo(
                Textface().warnmesg(
                    "EXEMPLAR",
                    "Resource name and/or size could not be retrieved"
                )
            )
            exit()
        else:
            if (self.thrdqant > int(self.filesize)):
                click.echo(
                    Textface().warnmesg(
                        "EXEMPLAR",
                        "Thread count is greater than the file size"
                    )
                )
                exit()
            else:
                if (self.strmsize > int(self.filesize)):
                    click.echo(
                        Textface().warnmesg(
                            "EXEMPLAR",
                            "Stream size is greater than the file size"
                        )
                    )
                    exit()
                else:
                    click.echo(
                        Textface().infomesg(
                            "MULTLOAD",
                            self.filename + " [" + str(self.filesize) + "B/" + str(self.strmsize) + "S/" + str(self.thrdqant) + "T]"
                        )
                    )
                    self.begindld()

    def thrdpull(self, qantindx, byternge):
        partsize = byternge[1] - byternge[0]
        thrdrqst = self.httpobjc.request(
            "GET",
            self.fileloca,
            preload_content=False,
            headers={"range": "bytes=" + str(byternge[0]) + "-" + str(byternge[1]) + ""}
        )
        progelem = tqdm(
            thrdrqst.stream(self.strmsize),
            desc=click.style("STARTING", fg="yellow", bold=True),
            colour="#008080",
            total=partsize,
            leave=False
        )
        partresp = b""
        for filepeic in progelem:
            partresp += filepeic
            progelem.set_description(
                Textface().specmesg(
                    "RECEIVED"
                )
            )
            progelem.update(len(filepeic))
        progelem.close()
        thrdrqst.release_conn()
        self.buffdict[qantindx] = partresp

    def calcptsz(self, fullsize, thrdqant):
        leftsize = fullsize % thrdqant
        dividend = (fullsize - leftsize) // thrdqant
        sizelist, partindx, chekpnts = [], [], []
        for indx in range(thrdqant):
            if indx == 0:
                sizelist.append(dividend + leftsize)
            else:
                sizelist.append(dividend)
        for indx in range(0, thrdqant+1, 1):
            partindx.append(sum(sizelist[0:indx]))
        for indx in range(1, len(partindx), 1):
            if indx == 1:
                chekpnts.append((partindx[indx - 1], partindx[indx]))
            else:
                chekpnts.append((partindx[indx - 1] + 1, partindx[indx]))
        return chekpnts

    def begindld(self):
        ptszlist = self.calcptsz(int(self.filesize), self.thrdqant)
        thrdlist = []
        for thrdindx in range(self.thrdqant):
            thrdobjc = threading.Thread(target=self.thrdpull, args=(thrdindx, ptszlist[thrdindx]))
            thrdlist.append(thrdobjc)
        strttime = time()
        for thrdindx in thrdlist:
            thrdindx.start()
        for thrdindx in thrdlist:
            thrdindx.join()
        stoptime = time()
        duration = str(stoptime - strttime)
        self.duraform = duration
        self.savetest()

    def savetest(self):
        filebuff = b""
        for indx in sorted(self.buffdict.keys()):
            filebuff += self.buffdict[indx]
        writstrg = str(self.thrdqant) + "," + str(self.duraform) + "," + sha256(filebuff).hexdigest()
        with open(str(self.strmsize) + ".csv", "a") as fileobjc:
            fileobjc.write(writstrg + "\n")

@click.command()
@click.option("-s", "--strmsize", "strmsize", help="Set the stream size in bytes.", required=True)
def mainfunc(strmsize):
    """
    A conveniently fast multithreaded downloader in command-line
    [65536, 131072, 196608, 262144, 327680, 393216, 458752, 524288, 589824, 655360, 720896, 786432, 851968, 917504, 983040, 1048576, 1114112, 1179648, 1245184, 1310720, 1376256, 1441792, 1507328, 1572864, 1638400, 1703936, 1769472, 1835008, 1900544, 1966080, 2031616, 2097152]
    SCHEMA {strmsize}.csv > {thrdqant}, {duration}, {sha256hx}
    """
    fileloca = "https://speed.hetzner.de/100MB.bin"
    with open(str(strmsize)+".csv", "w") as fileobjc:
        fileobjc.write("")
    for thrdqant in range(1, 513, 1):
        if thrdqant == 1:
            downobjc = Singload(fileloca, strmsize)
        elif 512 >= thrdqant > 1:
            downobjc = Multload(fileloca, strmsize, thrdqant)


if __name__ == "__main__":
    mainfunc()
