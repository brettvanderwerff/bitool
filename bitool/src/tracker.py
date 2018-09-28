from bitool.src.torrent_file import TorrentFile
import random
import socket
import struct

class ConnectRequest():
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
        self.sock.connect((ConnectRequest.TRACKER_URL, ConnectRequest.TRACKER_PORT))
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

if __name__ == "__main__":
    connec_req = ConnectRequest()
    connec_req.connect()
    print(connec_req.connection_id)

