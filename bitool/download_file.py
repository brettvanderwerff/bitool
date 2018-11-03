import math

class DownloadFile():
    '''
    Class represents the file being downloaded via the bit torrent network. Attributes represent what has and has not
    been downloaded.
    '''
    def __init__(self, magnet):
        self.blocks_per_piece = int(math.ceil(magnet.piece_length / 2 ** 14))
        self.block_size = int(magnet.piece_length / self.blocks_per_piece)
        self.last_piece = magnet.length % magnet.piece_length
        self.bytes = b''
        self.have = []
        self.done = False
        self.requests = []
        self.cur_index = None
        self.cur_block = None


        if self.last_piece == 0:
            adj = 0
        else:
            adj = 1


        '''
        Build request list
        
        '''

        for piece in range(magnet.piece_count - adj):
            piece_list = []
            for counter, block in enumerate(range(self.blocks_per_piece)):
                block_list = []
                block_list.append(counter * self.block_size)
                block_list.append(2 ** 14)
                piece_list.append(block_list)
            self.requests.append(piece_list)

        if self.last_piece <= 2 ** 14:
            self.requests.insert(len(self.requests), [[0,self.last_piece]])

        else:
            block_len = int(self.last_piece / 2 ** 14)
            self.last_piece = self.last_piece % 2 ** 14
            last_piece = []
            for counter in range(block_len):
                block_list = []
                block_list.append(counter * 2 ** 14)
                block_list.append(2 ** 14)
                last_piece.append(block_list)
            block_list = []
            block_list.append((counter + 1) * 2 ** 14)
            block_list.append(self.last_piece)
            last_piece.append(block_list)
            self.requests.insert(len(self.requests), last_piece)

        self.last_piece = magnet.length % magnet.piece_length # Reset last piece for building have list

        '''
        Build have list

        '''

        for piece in range(magnet.piece_count - adj):
            piece_list = []
            for x in range(self.blocks_per_piece):
                block_list = False
                piece_list.append(block_list)
            self.have.append(piece_list)

        if self.last_piece <= 2 ** 14:
            self.have.insert(len(self.have), [False])

        else:
            block_len = int(self.last_piece / 2 ** 14)
            self.last_piece = self.last_piece % 2 ** 14
            last_piece = []
            for counter in range(block_len):
                block_list = False
                last_piece.append(block_list)
            block_list = False
            last_piece.append(block_list)
            self.have.insert(len(self.have), last_piece)





