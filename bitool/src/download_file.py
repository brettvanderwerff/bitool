from bitool import TorrentFile
import math

class DownloadFile():
    '''
    Class represents the file being downloaded via the bit torrent network
    '''
    def __init__(self, torrent_file):
        self.left = torrent_file.length
        self.blocks_per_piece = int(math.ceil(torrent_file.piece_length / 2 ** 14))
        self.block_size = int(torrent_file.piece_length / self.blocks_per_piece)
        self.last_piece = torrent_file.length % torrent_file.piece_length

        self.template = {}
        for piece_count, piece in enumerate(range(torrent_file.piece_count)):
            self.template['piece_{}'.format(piece_count)] = {}
            for factor, block in enumerate(range(self.blocks_per_piece)):
                self.template['piece_{}'.format(piece_count)]['block_{}'.format(block)] = self.block_size + factor * self.block_size


        if self.last_piece <= 2 ** 14:
            self.template['peice_{}'.format(piece_count + 1)] = {'block_0' : self.last_piece}











        #ToDo add logic for if last piece is larger than 2 ** 14 bytes

    DOWNLOADED = 0
    UPLOADED = 0

if __name__ == "__main__":
    torrent_file = TorrentFile("test.torrent")
    torrent_file.read_file()
    download_file = DownloadFile(torrent_file)
    print(download_file.template)
