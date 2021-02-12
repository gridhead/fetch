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

from os.path import basename
from sys import exit
from time import time

import click
from magic import from_buffer
from urllib3 import PoolManager

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
"""


class Textface:
    def warnmesg(self, precursr, textmesg):
        click.echo(
            click.style(precursr, fg="yellow", bold=True) + " " +
            click.style(textmesg)
        )

    def failmesg(self, precursr, textmesg):
        click.echo(
            click.style(precursr, fg="red", bold=True) + " " +
            click.style(textmesg)
        )

    def succmesg(self, precursr, textmesg):
        click.echo(
            click.style(precursr, fg="green", bold=True) + " " +
            click.style(textmesg)
        )

    def infomesg(self, precursr, textmesg):
        click.echo(
            click.style(precursr, fg="blue", bold=True) + " " +
            click.style(textmesg)
        )


class Download(object):
    def __init__(self, fileloca, strmsize):
        try:
            self.httpobjc = PoolManager(num_pools=128)
            self.respdata = b""
            self.duraform = "0.00"
            self.rqstobjc = self.httpobjc.request("GET", fileloca, preload_content=False)
            self.strmsize = strmsize
            self.filename = basename(fileloca)
            #self.filename = self.rqstobjc.headers.get("Content-Disposition")
            self.filesize = self.rqstobjc.headers.get("Content-Length")
            if self.filesize is None or self.filename is None:
                Textface().warnmesg("WARNING", "Resource name and/or size could not be retrieved")
                exit()
            else:
                Textface().infomesg("PROPERTY", self.filename + " (" + str(self.filesize) + " bytes" + ")")
        except Exception as expt:
            Textface().failmesg("FAILURE", str(expt))
            exit()

    def begindld(self):
        try:
            strttime = time()
            with click.progressbar(
                    self.rqstobjc.stream(self.strmsize),
                    length=int(self.filesize),
                    fill_char="#",
                    label="RECEIVED 0/0 bytes",
                    bar_template="%(label)s [%(bar)s] %(info)s"
                ) as progelem:
                for filepeic in progelem:
                    self.respdata += filepeic
                    progelem.update(len(filepeic))
                    progelem.label = click.style("RECEIVED", fg="magenta", bold=True) + " " + \
                                     click.style(str(len(self.respdata)) + "/" + str(self.filesize) + " bytes")
            stoptime = time()
            duration = str(stoptime - strttime)
            self.duraform = duration.split(".")[0] + "." + duration.split(".")[1][0:2]
        except Exception as expt:
            Textface().failmesg("FAILURE", str(expt))
            exit()

    def savefile(self):
        try:
            with open(self.filename, "wb") as fileobjc:
                fileobjc.write(self.respdata)
            click.echo(
                click.style("MIMETYPE", bold=True) + " " +
                click.style(from_buffer(self.respdata) + " " + "(" + from_buffer(self.respdata, mime=True) + ")")
            )
            click.echo(
                click.style("COMPLETE", fg="green", bold=True) + " " +
                click.style("Transferred in " + str(self.duraform) + " seconds")
            )
            self.rqstobjc.release_conn()
            exit()
        except Exception as expt:
            Textface().failmesg("FAILURE", str(expt))
            exit()


@click.command()
@click.option("-l", "--fileloca", "fileloca", help="Set the remote file location.", required=True)
@click.option("-s", "--strmsize", "strmsize", help="Set the stream size in bytes.", required=True, default=65536)
@click.version_option(version="0.1.0-alpha", prog_name=click.style("Fetch", fg="magenta", bold=True))
def mainfunc(fileloca, strmsize):
    """
    A conveniently fast downloader in command-line
    """
    try:
        downobjc = Download(fileloca, strmsize)
        downobjc.begindld()
        downobjc.savefile()
    except Exception as expt:
        Textface().failmesg("FAILURE", str(expt))


if __name__ == "__main__":
    mainfunc()
