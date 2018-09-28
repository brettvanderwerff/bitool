# bitool
A set of tools for working with torrent files and implementing the bit torrent protocol in Python

==Work in Progress==

Warning: A work in progress hobby project to learn low level network tools, use at your own risk.

## Usage Cases

##### Parse a torrent file

```python
from bitool import TorrentFile

torrent_file = TorrentFile("file.torrent")

if __name__ == "__main__":
# Read the torrent file with the read_file method
    torrent_file.read_file()

# Then access components of the torrent file via object attributes
    print(torrent_file.meta_info)
    print(torrent_file.info)
    print(torrent_file.announce)
    print(torrent_file.announce_list)
    print(torrent_file.name)
```

##### Make an announce request to a tracker

```python
from bitool import AnnounceReq

announce_req = AnnounceReq("file.torrent")

if __name__ == "__main__":
# Connect to the tracker using the connect method
    announce_req.connect()

# Then access response information via object attributes
    print(announce_req.seeders)
    print(announce_req.leechers)
    print(announce_req.interval)
    print(announce_req.ips_ports) # a list of peer IPs and ports
```

