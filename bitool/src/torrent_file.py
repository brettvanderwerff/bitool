import bencoder

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

    def read_file(self):
        '''
        Reads the torrent file with bencoder and updates class attributes with the relevant values
        '''
        with open(self.torrent_file, 'rb') as read_obj:
            self.meta_info = bencoder.decode(read_obj.read())
        self.announce = self.meta_info[b'announce']
        self.announce_list = self.meta_info[b'announce-list']
        self.info = self.meta_info[b'info']
        self.length = self.info[b'length']
        self.name = self.info[b'name']

if __name__ == "__main__":
    torrent_file = TorrentFile("test.torrent")
    torrent_file.read_file()
    print(torrent_file.length)


