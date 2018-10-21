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

import logging
import os.path as pt
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

    def __init__(self, magnet, output_name=None):
        """init function.

        check for validity of the input.

        Raises:
            ValueError: if input is not valid this error will be raise
        """
        if (output_name and not pt.isdir(output_name) and
                not pt.isdir(pt.dirname(pt.abspath(output_name)))):
            raise ValueError("Invalid output folder: " + pt.dirname(pt.abspath(output_name)))
        self.output_name = output_name

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

        output = pt.abspath(torinfo.name() + ".torrent")

        if self.output_name:
            if pt.isdir(self.output_name):
                output = pt.abspath(pt.join(self.output_name,
                                            torinfo.name() + ".torrent"))
            elif pt.isdir(pt.dirname(pt.abspath(self.output_name))):
                output = pt.abspath(self.output_name)
        else:
            output = pt.abspath(torinfo.name() + ".torrent")

        print("Saving torrent file here : " + output + " ...")
        with open(output, "wb") as outfile:
            torcontent = lt.bencode(torfile.generate())
            outfile.write(torcontent)

        print("Saved! Cleaning up dir: " + self.tempdir)
        self.ses.remove_torrent(self.handle)
        shutil.rmtree(self.tempdir)

        return output


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




def main(magnet, output_name):
    """main function."""


    # guess the name if output name is not given.
    # in a magnet link it is between '&dn' and '&tr'
    try:
        if output_name is None:
            output_name = magnet.split('&dn=')[1].split('&tr')[0]
            output_name = unquote_plus(output_name)
            output_name += '.torrent'
    except IndexError:
        logging.error('magnet: {}'.format(magnet))

    # return if user wants to skip existing file.
    if output_name is not None and pt.isfile(output_name):
        print('File [{}] already exists.'.format(output_name))
        # still open file if file already exists.
        return

    # create fullname if file exists.
    if output_name is not None and pt.isfile(output_name):
        new_output_name = output_name
        counter = 1
        while pt.isfile(new_output_name):
            non_basename, non_ext = pt.splitext(new_output_name)
            if counter - 1 != 0:
                non_basename = non_basename.rsplit('_{}'.format(counter - 1), 1)[0]
            non_basename += '_{}'.format(counter)
            new_output_name = '{}{}'.format(non_basename, non_ext)
            counter += 1
        output_name = new_output_name

    # encode magnet link if it's url decoded.
    if magnet != unquote_plus(magnet):
        magnet = unquote_plus(magnet)

    conv = Magnet2Torrent(magnet, output_name)
    conv.run()




if __name__ == "__main__":
    sys.exit(main(magnet="magnet:?xt=urn:btih:15daaf668b57b3e9160bbc62ce9a310bfa38a93b&dn=200+Ways+to+Revive+a+Hard+Drive+pdf&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969&tr=udp%3A%2F%2Fzer0day.ch%3A1337&tr=udp%3A%2F%2Fopen.demonii.com%3A1337&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969&tr=udp%3A%2F%2Fexodus.desync.com%3A6969",
                  output_name="hd.torrent"))
