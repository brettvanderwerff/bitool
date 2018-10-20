from bitool import AnnounceReq, TorrentFile, ConnectReq, DownloadFile
import socket
import struct
from bitstring import BitArray


'''
~~~~~~~~~~
LOOK AWAY THIS IS NOT DONE :)
~~~~~~~~~~

'''

class PeerConnections():
    def __init__(self, announce_req, download_file):
        self.announce_req = announce_req
        self.download_file = download_file
        self.sock = None

    def gen_handshake(self):
        '''
        Generates a handshake to send to peers.

        :return: a handshake that is the concatenation of pstrlen, pstr, reserved, hash and peer_id
        '''
        pstrlen = bytes([19])
        pstr = b'BitTorrent protocol'
        reserved = (bytes([0]) * 8)
        hash = announce_req.hash.digest()
        peer_id = announce_req.peer_id
        return pstrlen + pstr + reserved + hash + peer_id


    def gen_interested(self):
        '''
        Generates and "interested message to send to each peer, which attempt to receive and unchokced message
        from the peer.

        :return: message length in 4 byte values and single byte message ID
        '''
        message_len = bytes([0, 0, 0, 1]) # 4 byte value indicating message length
        id = bytes([2]) # single decimal byte message ID
        return message_len + id


    def send_handshakes(self, peer):
        '''
        Iterates though list of peers gotten from the tracker, sends each one a handshake message.
        '''
        handshake = self.gen_handshake()

        print("Attempting to connect to peer at IP address: " + str(peer[0] + ", port " + str(peer[1])))
        self.sock.connect(peer)
        self.sock.send(handshake)
        response = self.sock.recv(68)# hopefully burn though all of bitfield stream before attempting to send interested message, reset to 68 for no bitfield
        if self.validate_handshake(response):
            self.parse_response()



    def send_interested(self):
        '''
        Sends "interested"message to peer.
        :return:
        '''
        self.sock.send(self.gen_interested())

    def parse_bitfield(self, payload_length):
        bitfeild = self.sock.recv(10 ** 6)  # burn bitfeild stream, may be issue with losing connection
        if len(bitfeild) == payload_length - 1:
            self.decode_bifield(bitfeild)
            self.send_interested()
            if self.parse_response() == 1:
                for index, (key, offset) in enumerate(
                        download_file.template.items()):  # logic needs to be outside this function
                    for offset in offset.values():
                        self.send_request(index, offset) # never enters second loop
                        self.parse_response()
        else:
            print('bitfeild does not match length, dropping peer')


    def parse_response(self):
        #https://wiki.theory.org/index.php/BitTorrentSpecification
        payload_length = struct.unpack(">I", self.sock.recv(4))[0]
        id = ord(self.sock.recv(1))
        print("ID of response is " + str(id) + ": ")
        if id == 0:
            print('choked')
        elif id == 1:
            print('unchoked')
        elif id == 2:
            print('interested')
        elif id == 3:
            print('uninterested')
        elif id == 4:
            print('have')
        elif id == 5:
            print('bitfield')
            self.parse_bitfield(payload_length)
        elif id == 6:
            print('request')
        elif id == 7:
            print('piece')
            print(payload_length)
            piece = b''
            while len(piece) <= payload_length:
                piece += self.sock.recv(4096)
                print(piece)
                print(len(piece))
            print(piece)
            print('len of piece is ' + str(len(piece))) # never prints for some reason
        elif id == 8:
            print('cancel')
        return id

    def decode_bifield(self, bitfield):
        bit_array = BitArray(bitfield)
        counter = 0 # explains trailing zeros https://stackoverflow.com/questions/44308457/confusion-around-bitfield-torrent
        for item in bit_array:
            if item == True:
                counter += 1
        if counter == torrent_file.piece_count:
            print('Has all pieces')


    def validate_handshake(self, response):
        '''
        Checks if a handshake response from a peer contains the pstr b'BitTorrent protocol' and contains the
        same SHA1 hash our bitorrent client sent in the original handshake message.

        :param response: A byte stream response from a peer that has received a handshake message.
        '''
        is_pstr = False
        if response[1:20] == b'BitTorrent protocol':
            is_pstr = True
        is_hash = False
        if response[28:48] == announce_req.hash.digest():
            is_hash = True
        return is_pstr and is_hash


    def send_request(self, index, offset):
        message_len = bytes([0, 0, 0, 13])  # 4 byte value indicating message length
        id = bytes([6])  # single decimal byte message ID
        index = index.to_bytes(4, 'big')  # four byte zero index for first piece
        offset = offset.to_bytes(4, 'big') # four byte block offset
        n = 2 ** 14
        length = n.to_bytes(4, 'big')  # standardized block length for 2 **14 bytes
        request = message_len + id + index + offset + length
        self.sock.send(request)

    def connect(self):
        '''
        Master connection method for PeerConnection
        '''

        for peer in announce_req.ips_ports:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)
            try:
                self.send_handshakes(peer)
            except (TimeoutError, OSError) as e:
                self.sock.close()
                continue
            self.send_interested()
            self.sock.close()


# ToDo master method for connection


if __name__ == '__main__':
    connect_req = ConnectReq()
    connect_req.connect()
    torrent_file = TorrentFile("test.torrent")
    torrent_file.read_file()
    download_file = DownloadFile(torrent_file)
    announce_req = AnnounceReq(connect_req, torrent_file, download_file)
    announce_req.connect()
    peer_connection = PeerConnections(announce_req, download_file)
    peer_connection.connect()
