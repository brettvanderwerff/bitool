from bitool import AnnounceReq, TorrentFile, ConnectReq

class PeerConnections():
    def __init__(self, announce_req):
        self.announce_req = announce_req


# ToDo method to make the handshake

# ToDo method for iterating through peer_id, port

# ToDo master method for connection





if __name__ == '__main__':
    connect_req = ConnectReq()
    connect_req.connect()
    torrent_file = TorrentFile("test.torrent")
    torrent_file.read_file()
    announce_req = AnnounceReq(connect_req, torrent_file)
    announce_req.connect()
    peer_connection = PeerConnections(announce_req)
