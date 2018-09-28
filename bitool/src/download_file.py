
class DownloadFile(): #ToDO put this in its own module, solve circular import issue
    '''
    Class represents the file being downloaded via the bit torrent network
    '''
    def __init__(self, torrent_file):
        self.left = torrent_file.length

    DOWNLOADED = 0
    UPLOADED = 0