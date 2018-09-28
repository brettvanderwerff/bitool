from bitool.src.torrent_file import TorrentFile
import bencoder
import hashlib
import random
import socket
import struct


class ConnectReq():
    '''
    Class representing the connection request to the tracker
    '''
    def __init__(self):
        self.transaction_id = random.randrange(1, 1000)
        self.sock = None
        self.connection_id = None

    TRACKER_URL = 'tracker.coppersurfer.tk'
    TRACKER_PORT = 6969

    def send_request(self):
        '''
        Send request to tracker for a connection ID
        '''
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sock.connect((ConnectReq.TRACKER_URL, ConnectReq.TRACKER_PORT))
        protocol_id = 0x41727101980
        action = 0
        packet = struct.pack(">qii", protocol_id, action, self.transaction_id)
        self.sock.send(packet)

    def recv_connec_id(self):
        '''
        Recieve connection ID from tracker
        '''
        response = self.sock.recv(4096)
        unpacked_response = struct.unpack(">iiq", response)
        self.connection_id = unpacked_response[2]
        self.sock.close()

    def connect(self):
        self.send_request()
        self.recv_connec_id()

class AnnounceReq():
    def __init__(self, torrent_file):
        self.torrent_file = TorrentFile(torrent_file)

    def hash(self):
        '''
        Generates SHA1 hash of the torrent info value.
        :return: hash
        '''
        info = self.torrent_file.info
        encoded_info = bencoder.encode(info)
        hash = hashlib.sha1(encoded_info)
        return hash

    def peer_id(self):
        '''
        Generates a 20 byte peer ID as per bit torrent protocol: http://www.bittorrent.org/beps/bep_0020.html
        :return:
        '''
        peer_id = ['-AZ2060-']
        for i in range(12):
            peer_id.append(str(random.randrange(1, 9)))
        return bytearray(''.join(peer_id), 'utf-8')


if __name__ == "__main__":
    connec_req = ConnectReq()
    connec_req.connect()
    print(connec_req.connection_id)

