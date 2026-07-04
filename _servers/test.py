#!/usr/bin/env python3
"""Datapack load test harness.

Usage: python3 _servers/test.py <1.21.11|26.1.2> [--keep-world]

Builds the datapack zip, wipes the server world, boots the Paper server via
Windows java.exe, waits for startup, forceloads an End chunk over RCON,
stops the server, and prints a DEDUPLICATED error summary (full log stays in
_servers/<ver>/server.log for targeted grepping).
"""
import re
import subprocess
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
def java_for(ver):
    if ver.startswith("26."):  # MC 26.1+ requires Java 25
        return str(next((ROOT / "_servers").glob("jdk-25*")) / "bin" / "java.exe")
    return "/mnt/c/Program Files/Java/jdk-24/bin/java.exe"
PACK_PARTS = ["pack.mcmeta", "pack.png", "data", "1_21_9", "1_21_11", "26_2"]
RCON_PORT = 25601
RCON_PW = "stellarity-test"
BOOT_TIMEOUT = 420

# --- tiny RCON client ---------------------------------------------------
def rcon(cmds):
    import socket, struct
    s = socket.create_connection(("127.0.0.1", RCON_PORT), timeout=10)
    def send(t, payload, rid=1):
        data = struct.pack("<ii", rid, t) + payload.encode() + b"\x00\x00"
        s.sendall(struct.pack("<i", len(data)) + data)
        ln = struct.unpack("<i", s.recv(4))[0]
        buf = b""
        while len(buf) < ln:
            buf += s.recv(ln - len(buf))
        return struct.unpack("<i", buf[:4])[0]
    if send(3, RCON_PW) == -1:
        raise RuntimeError("rcon auth failed")
    for c in cmds:
        send(2, c)
        time.sleep(0.3)
    s.close()

# --- zip build ----------------------------------------------------------
def build_zip(dest):
    dest.unlink(missing_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for part in PACK_PARTS:
            p = ROOT / part
            if p.is_file():
                z.write(p, part)
            else:
                for f in sorted(p.rglob("*")):
                    if f.is_file():
                        z.write(f, f.relative_to(ROOT).as_posix())

# --- log filtering ------------------------------------------------------
NOISE = re.compile(r"^\s+at |^\s*\.\.\. \d+ more|^\s*$")
INTEREST = re.compile(r"ERROR|FATAL|Exception|Failed|Couldn't|failed to|Invalid|Errors? in|Caused by")
def summarize(log_path):
    counts = {}
    order = []
    for line in log_path.read_text(errors="replace").splitlines():
        if NOISE.search(line) or not INTEREST.search(line):
            continue
        # strip timestamp/thread prefix so identical errors dedupe
        msg = re.sub(r"^(\[[^\]]*\] ?)+:? ?", "", line).strip()
        if msg not in counts:
            counts[msg] = 0
            order.append(msg)
        counts[msg] += 1
    return [(counts[m], m) for m in order]

def main():
    ver = sys.argv[1]
    keep_world = "--keep-world" in sys.argv
    srv = ROOT / "_servers" / ver
    jar = next(srv.glob("paper-*.jar"), None) or next(srv.glob("server*.jar"))
    jar = jar.name
    log = srv / "server.log"

    (srv / "eula.txt").write_text("eula=true\n")
    props = srv / "server.properties"
    want = {"server-port": "25599", "enable-rcon": "true", "rcon.port": str(RCON_PORT),
            "rcon.password": RCON_PW, "online-mode": "false", "view-distance": "3",
            "simulation-distance": "3", "max-players": "1"}
    lines = props.read_text().splitlines() if props.exists() else []
    lines = [l for l in lines if l.split("=")[0] not in want]
    lines += ["%s=%s" % kv for kv in want.items()]
    props.write_text("\n".join(lines) + "\n")
    if not keep_world:
        subprocess.run(["rm", "-rf", str(srv / "world"), str(srv / "world_nether"), str(srv / "world_the_end")])
    (srv / "world" / "datapacks").mkdir(parents=True, exist_ok=True)
    build_zip(srv / "world" / "datapacks" / "stellarity_lite.zip")
    print("zip built, booting %s ..." % jar, flush=True)

    with open(log, "w") as lf:
        proc = subprocess.Popen([java_for(ver), "-Xms512M", "-Xmx2G", "-jar", jar, "nogui"],
                                cwd=srv, stdout=lf, stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL)
        status = "TIMEOUT"
        for _ in range(BOOT_TIMEOUT):
            time.sleep(1)
            if proc.poll() is not None:
                status = "CRASHED (exit %s)" % proc.returncode
                break
            tail = log.read_text(errors="replace")
            if "Done (" in tail:
                status = "STARTED"
                break
            if "You can either fix your datapacks" in tail or "Failed to load datapacks" in tail:
                status = "DATAPACK REFUSED"
                break
        if status == "STARTED":
            try:
                rcon(["execute in minecraft:the_end run forceload add 0 0"])
                time.sleep(8)  # let the End chunk generate
                rcon(["execute in minecraft:the_end run forceload remove all", "stop"])
            except Exception as e:
                print("rcon failed: %s" % e, flush=True)
                proc.kill()
        else:
            try:
                rcon(["stop"])
            except Exception:
                proc.kill()
        try:
            proc.wait(timeout=90)
        except subprocess.TimeoutExpired:
            proc.kill()

    print("RESULT:", status)
    errors = summarize(log)
    print("UNIQUE ERROR LINES: %d (full log: %s)" % (len(errors), log))
    for n, msg in errors[:80]:
        print("%4dx %s" % (n, msg[:300]))
    if len(errors) > 80:
        print("... %d more unique lines, grep the log" % (len(errors) - 80))

if __name__ == "__main__":
    main()
