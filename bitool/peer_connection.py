import socket
import struct
import bencoder
import random
from bitool import magnet_link, download_file
from bitstring import BitArray
import os
import hashlib
import binascii
import sys

magnet = magnet_link.MagnetLink(sys.argv[1])
torrent = download_file.DownloadFile(magnet)

def parse_trackers():
    '''
    Parses trackers from the magnet link, extracts the url and port number for each tracker.
    '''
    tracker_list = []
    for tracker in magnet.trackers:
        tracker = tracker.decode('utf-8').split('/')[-1]
        tracker_url = tracker.split(":")[0]
        tracker_port = int(tracker.split(":")[1])
        tracker_list.append((tracker_url, tracker_port))
    tracker_list.append(('tracker.coppersurfer.tk', 6969)) # Fall back on known to work tracker
    return tracker_list

def build_request():
    '''
    Builds a request to connnect to tracker.
    '''
    protocol_id = 0x41727101980
    action = 0
    transaction_id = random.randrange(1, 1000)
    request = struct.pack(">qii", protocol_id, action, transaction_id)
    return request

def gen_hash():
    '''
    Generated SHA1 hash based on the 'info' section of the magnet link data.
    '''
    info = magnet.info
    encoded_info = bencoder.encode(info)
    return hashlib.sha1(encoded_info)

def gen_peer_id():
    '''
    Generates peer ID according to conventions at: http://www.bittorrent.org/beps/bep_0020.html
    '''
    peer_id = ['-AZ2060-']
    for i in range(12):
        peer_id.append(str(random.randrange(1, 9)))
    return bytearray(''.join(peer_id), 'utf-8')

def build_announce_req(connection_id, hash, peer_id):
    '''
    Builds an announce request to get a peer list from the tracker.
    '''
    binary_hash = binascii.a2b_hex(hash.hexdigest())
    action = 1
    transaction_id = random.randrange(1, 1000)
    downloaded = 0
    uploaded = 0
    event = 0
    ip = 0
    left = magnet.length
    key = random.randrange(1, 1000)
    num_want = -1
    port = 6681
    request = struct.pack(">qii20s20sqqqiiiih",
                         connection_id,
                         action,
                         transaction_id,
                         binary_hash,
                         peer_id,
                         downloaded,
                         left,
                         uploaded,
                         event,
                         ip,
                         key,
                         num_want,
                         port)
    return request


def communicate_DGRAM(target, message):
    '''
    Primary function for sending and receiving information with tracker via DGRAM.
    '''
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.settimeout(15)
    sock.connect(target)
    sock.send(message)
    response = sock.recv(4096)
    sock.close()
    return response

def connect_tracker(tracker_list, request, hash, peer_id):
    for tracker in tracker_list:
        try:
            print('Connecting to trackers...')
            response = communicate_DGRAM(tracker, request)
            unpacked_response = struct.unpack(">iiq", response)
            connection_id = unpacked_response[2]
            print('Connection to tracker formed')
            announce_req = build_announce_req(connection_id, hash, peer_id)
            print('Receiving list of peers..')
            response = communicate_DGRAM(tracker, announce_req)
            return response
        except (ConnectionRefusedError, socket.timeout) as e:
            continue

def parse_ips(response):
    ips_ports = []
    for offset in range(20, len(response), 6):
        raw_ip = struct.unpack_from(">BBBB", response, offset)
        ip = '.'.join([str(i) for i in raw_ip])
        port = struct.unpack_from(">H", response, offset + 4)[0]
        ips_ports.append((ip, port))
    print("Peer list received")
    return ips_ports


def gen_ips():
    tracker_list = parse_trackers()
    request = build_request()
    hash = gen_hash()
    peer_id = gen_peer_id()
    response = connect_tracker(tracker_list, request, hash, peer_id)
    return parse_ips(response)


def build_handshake(hash):
    pstrlen = bytes([19])
    pstr = b'BitTorrent protocol'
    reserved = (bytes([0]) * 8)
    hash = hash.digest()
    peer_id = gen_peer_id()

    return pstrlen + pstr + reserved + hash + peer_id


def build_interested():
    message_len = bytes([0, 0, 0, 1])
    id = bytes([2])

    return message_len + id


def validate_handshake(response, hash):
    '''
    Checks if a handshake response from a peer contains the pstr b'BitTorrent protocol' and contains the
    same SHA1 hash our bitorrent client sent in the original handshake message.

    :param response: A byte stream response from a peer that has received a handshake message.
    '''

    is_pstr = False

    if response[1:20] == b'BitTorrent protocol':
        is_pstr = True
    is_hash = False

    if response[28:48] == hash.digest():
        is_hash = True

    return is_pstr and is_hash


def recv_unchoked(sock):

    for index_number, piece in enumerate(torrent.requests):
        for block_number, block in enumerate(piece):

            torrent.cur_index = index_number
            torrent.cur_block = block_number

            if not torrent.have[index_number][block_number]:
                offset = block[0]
                length = block[1]
                request = send_request(index_number, offset, length)
                sock.send(request)
                parse_response(sock)


def parse_response(sock):
    payload_length = struct.unpack(">I", sock.recv(4))[0]
    id = ord(sock.recv(1))
    if id == 0:
        print('Message type: choked, peer stopped sharing.')
        raise TimeoutError

    elif id == 1:
        print('Message type: unchoked, peer will allow sharing')
        recv_unchoked(sock)


    elif id == 5:
        # Message type: bitfield
        do_download = eval_bitfield(payload_length, sock)
        if do_download:
            interested = build_interested()
            sock.send(interested)
            parse_response(sock)

        else:
            raise TimeoutError

    elif id == 7:
        # Message type: piece
        recv_piece(payload_length, sock)

    else:
        print('Error communicating with peer, dropping connection.')
        raise TimeoutError


def eval_bitfield(payload_length, sock):
    bitfield = sock.recv(4096)
    if len(bitfield) == payload_length - 1:
        bit_array = BitArray(bitfield)
        counter = 0
        for item in bit_array:
            if item == True:
                counter += 1
        return True if counter == magnet.piece_count else False


def write_binary():
    os.mkdir(magnet.name)
    offset = 0
    for file in magnet.write_data:
        file_name = file[0]
        file_length = file[1]
        write_path = os.path.join(os.getcwd(), os.path.basename(magnet.name), os.path.basename(file_name))
        with open(write_path, 'wb') as file_obj:
            file_obj.write(torrent.bytes[offset:offset + file_length])
        offset += file_length


def recv_piece(payload_length, sock):
    if (payload_length == torrent.block_size + 9) or (payload_length == torrent.last_piece + 9):
        piece_count = struct.unpack(">I", sock.recv(4))[0]
        print('receiving piece number ' + str(piece_count))
        offset = struct.unpack(">I", sock.recv(4))[0]
        print('with offset ' + str(offset))
        piece = b''
        while len(piece) < payload_length - 9:
            piece += sock.recv(4096)
        print('bytes added')
        torrent.bytes += piece
        print(len(torrent.bytes))
        torrent.have[torrent.cur_index][torrent.cur_block] = True
        progress = str(round((sum([sum(piece) for piece in torrent.have]) / sum([len(piece) for piece in torrent.have]) * 100), 2))
        print("receiving data from peer... " + progress + " % complete")




def send_request(index, offset, length):
    message_len = bytes([0, 0, 0, 13])
    id = bytes([6])
    index = index.to_bytes(4, 'big')
    offset = offset.to_bytes(4, 'big')
    length = length.to_bytes(4, 'big')
    request = message_len + id + index + offset + length

    return request


def connect_peers(ips, hash):
    for peer in ips:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.5)

        try:
            print("Attempting to receive from peer at IP address: " + str(peer[0] + ", port " + str(peer[1])))
            sock.connect(peer)
            handshake = build_handshake(hash)
            sock.send(handshake)
            response = sock.recv(68)

            if validate_handshake(response, hash):
                parse_response(sock)
                torrent.done = True
                write_binary()
                exit()

        except (TimeoutError, OSError, BrokenPipeError, struct.error) as e:
            sock.close()



def run():
    while torrent.done == False:
        ips = gen_ips()
        hash = gen_hash()
        connect_peers(ips, hash)




