import bencoder
import math
import pprint

class TorrentFile():
    '''
    class for representing torrent files.
    '''

    def __init__(self, torrent_file):
        self.announce = None
        self.announce_list = None
        self.info = None
        self.length = None
        self.meta_info = None
        self.name = None
        self.torrent_file = torrent_file
        self.pieces = None
        self.piece_length = None
        self.piece_count = None

    def read_file(self):
        '''
        Reads the torrent file with bencoder and updates class attributes with the relevant values
        '''
        with open(self.torrent_file, 'rb') as read_obj:
            self.meta_info = bencoder.decode(read_obj.read())
        self.announce = self.meta_info[b'announce']
        self.announce_list = self.meta_info[b'announce-list']
        self.info = self.meta_info[b'info']
        try:
            self.length = self.info[b'length']
        except KeyError as e:
            self.length = self.info[b'files'][1][b'length'] #may have something to do with multiple files

        self.name = self.info[b'name']
        self.write_name = self.name.decode('utf-8').replace(' ', '_')
        self.pieces = self.info[b'pieces']
        self.piece_length = self.info[b'piece length']
        self.piece_count = math.ceil(self.length / self.piece_length)


if __name__ == "__main__":
    torrent_file = TorrentFile("test.torrent")
    torrent_file.read_file()
    print(torrent_file.piece_count)
    print(torrent_file.piece_length)
    print(torrent_file.length)



