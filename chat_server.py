import socket
import json
import sys
import select

client_socks = set()
buffers = {}
nicks = {}

def get_next_packet(s):
    global buffers
    if s not in buffers.keys():
        buffers[s] = b''
    print("getting next")
    while True:
        buffer = buffers[s]
        print(buffer)
        if len(buffer) >= 2:
            l = int.from_bytes(buffer[:2], "big")
            if len(buffer[2:]) >= l:
                # Read packet
                message = buffer[2:2+l]
                buffers[s] = buffer[2+l:]
                return message
        new_data = s.recv(4096)
        if len(new_data) == 0:
            return None
        buffers[s] = buffer + new_data

def packet_to_object(p):
    s = p.decode()
    json_data = json.loads(s)
    return json_data

def object_to_packet(o):
    data = json.dumps(o).encode()
    l = len(data).to_bytes(2, "big")
    return l + data

def make_join_packet(nick):
    join_object = {
            "type": "join",
            "nick": nick
    }
    return object_to_packet(join_object)

def make_leave_packet(nick):
    leave_object = {
            "type": "leave",
            "nick": nick
    }
    return object_to_packet(leave_object)

def make_message_packet(nick, message):
    message_object = {
            "type": "chat",
            "nick": nick,
            "message": message
    }
    return object_to_packet(message_object)

def send_all(packet):
    global buffers
    socks = buffers.keys()

    for sock in socks:
        sock.sendall(packet)

def usage():
    print("usage: chat_server.py port", file=sys.stderr)

def main(argv):
    try: 
        port = int(argv[1])
    except:
        usage()
        return 1

    global client_socks
    global buffers
    global nicks

    listener = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(('', port))
    listener.listen()
    client_socks.add(listener)

    while True:
        socks, _, _ = select.select(client_socks, {}, {})
        for sock in socks:
            if sock == listener:
                new_conn = sock.accept()
                new_sock = new_conn[0]
                print("conn accepted")
                client_socks.add(new_sock)
            else:
                pack = get_next_packet(sock)
                print("pack ", pack)
                if pack == None:
                    client_socks.remove(sock)
                    buffers.pop(sock)
                    nick = nicks[sock]
                    nicks.pop(sock)
                    to_send = make_leave_packet(nick)
                    send_all(to_send)
                    continue
                
                message = packet_to_object(pack)
                t = message["type"]
                print("ahhhh")
                print(message)
                print(t)
                if t == "hello":
                    print("got hello")
                    nick = message["nick"]
                    buffers[sock] = b''
                    nicks[sock] = nick
                    to_send = make_join_packet(nick)
                    send_all(to_send)
                elif t == "chat":
                    print("got chat")
                    nick = nicks[sock]
                    m = message["message"]
                    to_send = make_message_packet(nick, m)
                    send_all(to_send)


if __name__ == "__main__":
    main(sys.argv)
