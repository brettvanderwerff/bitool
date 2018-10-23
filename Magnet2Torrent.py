#!/usr/bin/env python3
"""convert magnet link to torrent file.

Created on Apr 19, 2012 @author: dan, Faless
    GNU GENERAL PUBLIC LICENSE - Version 3

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    http://www.gnu.org/licenses/gpl-3.0.txt

"""
import shutil
import sys
import tempfile
from time import sleep
try:
    from urllib.parse import unquote_plus
except ImportError:
    from urllib import unquote_plus
import libtorrent as lt


class Magnet2Torrent(object):
    """class for converter from magnet link to torrent."""

    def __init__(self, magnet):
        """init function.

        check for validity of the input.

        Raises:
            ValueError: if input is not valid this error will be raise
        """

        self.tempdir = tempfile.mkdtemp()
        self.ses = lt.session()

        params = {
            'url': magnet,
            'save_path': self.tempdir,
            'storage_mode': lt.storage_mode_t(2),
            'paused': False,
            'auto_managed': True,
            'duplicate_is_error': False
        }
        self.handle = self.ses.add_torrent(params)

    def run(self):
        """run the converter.

        using the class attribute initiated at init function.

        Returns:
            Filename of created torrent.

        Raises:
            KeyboardInterrupt: This error caused by user to stop this.
            When downloading metadata from magnet link,
            it requires an additional step before the error reraised again.
        """
        print("Downloading Metadata (this may take a while)")

        # used to control "Maybe..." and "or the" msgs after sleep(1)
        wait_time = 1
        soft_limit = 120
        while not self.handle.has_metadata():
            try:
                sleep(1)
                if wait_time > soft_limit:
                    print("Downloading is taking a while, maybe there is an "
                          "issue with the magnet link or your network connection")
                    soft_limit += 30
                wait_time += 1
            except KeyboardInterrupt:
                print("\nAborting...")
                self.ses.pause()
                print("Cleanup dir " + self.tempdir)
                shutil.rmtree(self.tempdir)
                raise
        self.ses.pause()
        print("Done")

        torinfo = self.handle.get_torrent_info()
        torfile = lt.create_torrent(torinfo)
        self.ses.remove_torrent(self.handle)
        shutil.rmtree(self.tempdir)

        return torfile.generate()




def open_default_app(filepath):
    """open filepath with default application for each operating system."""
    import os
    import subprocess

    if sys.platform.startswith('darwin'):
        subprocess.call(('open', filepath))
    elif os.name == 'nt':
        os.startfile(filepath)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', filepath))

def main(magnet):
    """main function."""

    # encode magnet link if it's url decoded.
    if magnet != unquote_plus(magnet):
        magnet = unquote_plus(magnet)

    conv = Magnet2Torrent(magnet)
    return conv.run()
