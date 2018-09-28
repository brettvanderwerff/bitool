from bitool import TorrentFile
import binascii
import bencoder
import hashlib
import random
import socket
import struct

class ConnectReq():
    '''
    Class representing the connection request to the tracker.
    '''
    def __init__(self):
        self.transaction_id = random.randrange(1, 1000)
        self.sock = None
        self.connection_id = None

    TRACKER_URL = 'tracker.coppersurfer.tk'
    TRACKER_PORT = 6969

    def send_request(self):
        '''
        Send request to tracker for a connection ID.
        '''
        protocol_id = 0x41727101980
        action = 0
        packet = struct.pack(">qii", protocol_id, action, self.transaction_id)
        self.sock.send(packet)

    def recv_connec_id(self):
        '''
        Receives connection ID from tracker.
        '''
        response = self.sock.recv(4096)
        unpacked_response = struct.unpack(">iiq", response)
        self.connection_id = unpacked_response[2]

    def connect(self):
        '''
        Master connection method for ConnectReq
        '''
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sock.connect((ConnectReq.TRACKER_URL, ConnectReq.TRACKER_PORT))
        self.send_request()
        self.recv_connec_id()
        self.sock.close()

class AnnounceReq():
    def __init__(self, torrent_file):
        self.connect_req = ConnectReq()
        self.connect_req.connect()
        self.interval = None
        self.ips_ports = None
        self.leechers = None
        self.sock = None
        self.seeders = None
        self.torrent_file = TorrentFile(torrent_file)
        self.torrent_file.read_file()
        self.transaction_id = random.randrange(1, 1000)

    TRACKER_URL = 'tracker.coppersurfer.tk'
    TRACKER_PORT = 6969

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

    def send_request(self):
        '''
        Send announce request to tracker.
        '''
        connection_id = self.connect_req.connection_id
        bin_hash = binascii.a2b_hex(self.hash().hexdigest())
        peer_id = self.peer_id()
        action = 1
        downloaded = 0
        left = self.torrent_file.length
        uploaded = 0
        event = 0
        ip = 0
        key = random.randrange(1, 1000)
        num_want = -1
        port = 6681
        packet = struct.pack(">qii20s20sqqqiiiih",
                             connection_id,
                             action,
                             self.transaction_id,
                             bin_hash,
                             peer_id,
                             downloaded,
                             left,
                             uploaded,
                             event,
                             ip,
                             key,
                             num_want,
                             port)
        self.sock.send(packet)

    def parse_ip_ports(self, response):
        '''
        Parses response for IP addresses and corresponding ports
        :return: a list of tuples of IP addresses and ports
        '''
        ips_ports = []
        for offset in range(20, len(response), 6):
            raw_ip = struct.unpack_from(">BBBB", response, offset)
            ip = '.'.join([str(i) for i in raw_ip])
            port = struct.unpack_from(">H", response, offset + 4)[0]
            ips_ports.append((ip, port))
        return ips_ports

    def recv_connec_id(self):
        '''
        Receives announce request from tracker.
        '''
        response = self.sock.recv(4096)
        self.interval = struct.unpack_from(">I", response, 8)
        self.leechers = struct.unpack_from(">I", response, 12)
        self.seeders = struct.unpack_from(">I", response, 16)
        self.ips_ports = self.parse_ip_ports(response)

    def connect(self):
        '''
        Master connection method for AnnounceReq
        '''
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sock.connect((AnnounceReq.TRACKER_URL, AnnounceReq.TRACKER_PORT))
        self.send_request()
        self.recv_connec_id()
        self.sock.close()

if __name__ == "__main__":
    announce_req = AnnounceReq("test.torrent")
    announce_req.connect()
    print(announce_req.ips_ports)



