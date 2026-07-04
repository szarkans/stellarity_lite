#!/usr/bin/env python3
"""Send commands to the running test server. Usage: rcon.py 'cmd1' 'cmd2' ..."""
import socket
import struct
import sys

PORT, PW = 25601, "stellarity-test"

def send_cmd(s, t, payload, rid=1):
    data = struct.pack("<ii", rid, t) + payload.encode() + b"\x00\x00"
    s.sendall(struct.pack("<i", len(data)) + data)
    ln = struct.unpack("<i", s.recv(4))[0]
    buf = b""
    while len(buf) < ln:
        buf += s.recv(ln - len(buf))
    rid = struct.unpack("<i", buf[:4])[0]
    return rid, buf[8:-2].decode(errors="replace")

s = socket.create_connection(("127.0.0.1", PORT), timeout=10)
if send_cmd(s, 3, PW)[0] == -1:
    sys.exit("auth failed")
for c in sys.argv[1:]:
    print(">", c)
    print(send_cmd(s, 2, c)[1])
