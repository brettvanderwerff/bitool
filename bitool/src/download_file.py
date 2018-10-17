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
        for piece in range(torrent_file.piece_count):
            for factor, block in enumerate(range(self.blocks_per_piece)):
                self.template['peice_{}_block_{}'.format(piece, block)] = self.block_size + factor * self.block_size

    DOWNLOADED = 0
    UPLOADED = 0

if __name__ == "__main__":
    torrent_file = TorrentFile("test.torrent")
    torrent_file.read_file()
    download_file = DownloadFile(torrent_file)
    print(download_file.template)
