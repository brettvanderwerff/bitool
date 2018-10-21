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
        self.bytes = b''


        self.template = {}
        for piece_count, piece in enumerate(range(torrent_file.piece_count)):
            self.template['piece_{}'.format(piece_count)] = {}
            for factor, block in enumerate(range(self.blocks_per_piece)):
                self.template['piece_{}'.format(piece_count)]['block_{}'.format(block)] = factor * self.block_size


        if self.last_piece <= 2 ** 14:
            self.template['peice_{}'.format(piece_count + 1)] = {'block_0' : self.last_piece} # need to adjust length not offset

        if self.last_piece == 0:
            adj = 0
        else:
            adj = 1
        self.requests = []
        for piece in range(torrent_file.piece_count - adj):
            piece_list = []
            for counter, block in enumerate(range(self.blocks_per_piece)):
                block_list = []
                block_list.append(counter)
                block_list.append(counter * self.block_size)
                block_list.append(2 ** 14)
                piece_list.append(block_list)
            self.requests.append(piece_list)

        if self.last_piece <= 2 ** 14:
            self.requests.insert(len(self.requests), [[0,0,self.last_piece]])


        #ToDo add logic for if last piece is larger than 2 ** 14 bytes

    DOWNLOADED = 0
    UPLOADED = 0

if __name__ == "__main__":
    torrent_file = TorrentFile("test.torrent")
    torrent_file.read_file()
    download_file = DownloadFile(torrent_file)
    print(torrent_file.piece_count)
    print(download_file.requests)
    for piece_number, piece in enumerate(download_file.requests):
        for block in piece:
            offset = block[1]
            length = block[2]
            print(piece_number, offset, length)


