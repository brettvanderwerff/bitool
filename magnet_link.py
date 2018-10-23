import Magnet2Torrent
import math

class MagnetLink():
    def __init__(self, magnet_link):
        meta_info = Magnet2Torrent.main(magnet_link)

        self.trackers = meta_info[b'announce-list'][0]
        self.info = meta_info[b'info']
        self.name = self.info[b'name'].decode('utf-8')


        try:
            self.length = sum([item[b'length'] for item in meta_info[b'info'][b'files']])

        except:
            self.length = self.info[b'length']

        try:
            write_names = [item[b'path'][-1].decode('utf-8') for item in meta_info[b'info'][b'files']]

        except:
            write_names = [self.info[b'name'].decode('utf-8').replace(' ', '_')]

        try:
            write_lengths = [item[b'length'] for item in meta_info[b'info'][b'files']]

        except:
            write_lengths = [self.info[b'length']]


        self.write_data = zip(write_names, write_lengths)


        self.pieces = self.info[b'pieces']
        self.piece_length = self.info[b'piece length']
        self.piece_count = math.ceil(self.length / self.piece_length)

