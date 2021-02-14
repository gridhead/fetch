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
from magic import from_buffer
from sys import exit
from os.path import basename

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

    def specmesg(self, precursr, textmesg):
        return \
            click.style(precursr, fg="magenta", bold=True) + " " + \
            click.style(textmesg)

    def genrmesg(self, precursr, textmesg):
        return \
            click.style(precursr, bold=True) + " " + \
            click.style(textmesg)


class Singload:
    def __init__(self, fileloca, strmsize):
        try:
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
        except Exception as expt:
            click.echo(Textface().failmesg("COLLAPSE", str(expt)))
            exit()

    def begindld(self):
        try:
            strttime = time()
            progelem = tqdm(
                self.rqstobjc.stream(self.strmsize),
                desc=click.style("STARTING", fg="yellow", bold=True),
                leave=False
            )
            for filepeic in progelem:
                self.respdata += filepeic
                progelem.set_description(
                    Textface().specmesg(
                        "RECEIVED",
                        click.style(str(len(self.respdata)) + "/" + str(self.filesize) + "B")
                    )
                )
            progelem.close()
            stoptime = time()
            duration = str(stoptime - strttime)
            self.duraform = duration.split(".")[0] + "." + duration.split(".")[1][0:2]
            self.savefile()
        except Exception as expt:
            Textface().failmesg("FAILURE", str(expt))
            exit()

    def savefile(self):
        try:
            with open(self.filename, "wb") as fileobjc:
                fileobjc.write(self.respdata)
            click.echo(
                Textface().genrmesg(
                    "MIMETYPE",
                    click.style(from_buffer(self.respdata) + " " + "(" + from_buffer(self.respdata, mime=True) + ")")
                )
            )
            click.echo(
                Textface().succmesg(
                    "COMPLETE",
                    click.style("Transferred in " + str(self.duraform) + " seconds")
                )
            )
            self.rqstobjc.release_conn()
            exit()
        except Exception as expt:
            Textface().failmesg("FAILURE", str(expt))
            exit()


class Multload:
    def __init__(self, fileloca, strmsize, thrdqant):
        try:
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
        except Exception as expt:
            click.echo(Textface().failmesg("COLLAPSE", str(expt)))
            exit()

    def thrdpull(self, qantindx, byternge):
        try:
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
                leave=False
            )
            partresp = b""
            for filepeic in progelem:
                partresp += filepeic
                progelem.set_description(
                    Textface().specmesg(
                        "RECEIVED",
                        click.style("T#" + str(qantindx) + " " + str(len(partresp)) + "/" + str(partsize) + "B")
                    )
                )
            progelem.close()
            self.buffdict[qantindx] = partresp
        except Exception as expt:
            Textface().failmesg("FAILURE", str(expt))
            exit()

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
            chekpnts.append((partindx[indx-1], partindx[indx]))
        return chekpnts

    def begindld(self):
        try:
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
            self.duraform = duration.split(".")[0] + "." + duration.split(".")[1][0:2]
            self.savefile()
        except Exception as expt:
            click.echo(Textface().failmesg("COLLAPSE", str(expt)))
            exit()

    def savefile(self):
        try:
            filebuff = b""
            for indx in self.buffdict.keys():
                filebuff += self.buffdict[indx]
            with open(self.filename, "wb") as fileobjc:
                fileobjc.write(filebuff)
            print("\r\r", end="")
            click.echo(
                Textface().genrmesg(
                    "MIMETYPE",
                    click.style(from_buffer(filebuff) + " " + "(" + from_buffer(filebuff, mime=True) + ")")
                )
            )
            click.echo(
                Textface().succmesg(
                    "COMPLETE",
                    click.style("Transferred in " + str(self.duraform) + " seconds")
                )
            )
            self.rqstobjc.release_conn()
            exit()
        except Exception as expt:
            click.echo(Textface().failmesg("COLLAPSE", str(expt)))
            exit()


@click.command()
@click.option("-l", "--fileloca", "fileloca", help="Set the remote file location.", required=True)
@click.option("-s", "--strmsize", "strmsize", help="Set the stream size in bytes.", required=True, default=65536)
@click.option("-t", "--thrdqant", "thrdqant", help="Set the number of threads.", required=True, default=1)
@click.version_option(version="0.2.0-alpha", prog_name=click.style("Fetch", fg="magenta", bold=True))
def mainfunc(fileloca, strmsize, thrdqant):
    """
    A conveniently fast multithreaded downloader in command-line
    """
    try:
        if strmsize >= 1:
            if thrdqant == 1:
                downobjc = Singload(fileloca, strmsize)
            elif thrdqant > 1:
                downobjc = Multload(fileloca, strmsize, thrdqant)
            else:
                click.echo(Textface().failmesg("COLLAPSE", "Invalid thread count entered"))
        else:
            click.echo(Textface().failmesg("COLLAPSE", "Invalid stream size entered"))
    except Exception as expt:
        click.echo(Textface().failmesg("FAILURE", str(expt)))


if __name__ == "__main__":
    mainfunc()
