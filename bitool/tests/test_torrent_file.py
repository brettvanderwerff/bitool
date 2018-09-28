import unittest
from bitool import TorrentFile

class TestTorrentFile(unittest.TestCase):

    def setUp(self):
        '''
        Instantiates the test object for the TorrentFile class
        '''

        self.test = TorrentFile("test.torrent")


#ToDo Make tests!


if __name__ == "__main__":
    unittest.main()