import hashlib
import socket
import struct
import bencoder
import random
import binascii


def parse_trackers(magnet):
    tracker_list = []
    for tracker in magnet.trackers:
        tracker = tracker.decode('utf-8').split('/')[-1]
        tracker_url = tracker.split(":")[0]
        tracker_port = int(tracker.split(":")[1])
        tracker_list.append((tracker_url, tracker_port))
    tracker_list.append(('tracker.coppersurfer.tk', 6969)) # Fall back on known to work tracker
    return tracker_list

def build_request():
    protocol_id = 0x41727101980
    action = 0
    transaction_id = random.randrange(1, 1000)
    request = struct.pack(">qii", protocol_id, action, transaction_id)
    return request

def gen_hash(magnet):
    info = magnet.info
    encoded_info = bencoder.encode(info)
    return hashlib.sha1(encoded_info)

def gen_peer_id():
    peer_id = ['-AZ2060-']
    for i in range(12):
        peer_id.append(str(random.randrange(1, 9)))
    return bytearray(''.join(peer_id), 'utf-8')

def build_announce_req(connection_id, hash, peer_id, magnet):
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
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.settimeout(15)
    sock.connect(target)
    sock.send(message)
    response = sock.recv(4096)
    sock.close()
    return response

def connect_tracker(tracker_list, request, hash, peer_id, magnet):
    for tracker in tracker_list:
        try:
            print('Connecting to trackers...')
            response = communicate_DGRAM(tracker, request)
            unpacked_response = struct.unpack(">iiq", response)
            connection_id = unpacked_response[2]
            print('Connection to tracker formed')
            announce_req = build_announce_req(connection_id, hash, peer_id, magnet)
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


def gen_ips(magnet):
    tracker_list = parse_trackers(magnet=magnet)
    request = build_request()
    hash = gen_hash(magnet)
    peer_id = gen_peer_id()
    response = connect_tracker(tracker_list, request, hash, peer_id, magnet)
    return parse_ips(response)



