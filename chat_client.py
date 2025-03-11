import threading
import sys
import json
import socket

from chatui import init_windows, read_command, print_message, end_windows

buffer = b''

def get_next_packet(s):
    global buffer
    while True:
        if len(buffer) >= 2:
            l = int.from_bytes(buffer[:2], "big")
            if len(buffer[2:]) >= l:
                # read packet
                message = buffer[2:2+l]
                buffer = buffer[2+l:]
                return message
        new_data = s.recv(4096)
        if len(new_data) == 0:
            return None
        buffer += new_data

def packet_to_object(p):
    s = p.decode();
    json_data = json.loads(s)
    return json_data

def object_to_packet(o):
    data = json.dumps(o).encode()
    l = len(data).to_bytes(2, "big")
    return l + data
        

def receiving_function(s):
    while True:
        message_packet = get_next_packet(s)
        if message_packet == None:
            break
        message = packet_to_object(message_packet)
        nick = message["nick"]
        t = message["type"]
        if t == "chat":
            m = message["message"]
            print_message(f"{nick}: {m}")
        else:
            verb = "joined" if t == "join" else "left"
            print_message(f"*** {nick} has {verb} the chat")

def send_message(s, nick, t, message=""):
    message_object = {
            "type": t,
            "nick": nick
    }
    if message:
        message_object["message"] = message

    packet = object_to_packet(message_object)
    s.sendall(packet)
    print_message("message sent: " + message)

def usage():
    print("usage: chat_client.py nickname server port", file=sys.stderr)

def main(argv):
    try:
        nick = argv[1]
        server = argv[2]
        port = int(argv[3])
    except:
        usage()
        return 1

    init_windows()

    s = socket.socket()
    s.connect((server, port))

    send_message(s, nick, "hello")

    read_thread = threading.Thread(target = receiving_function, daemon=True, args=(s,))
    read_thread.start()

    while True:
        try:
            command = read_command(">> ")
        except:
            break

        #TODO send to server
        if command[:1] == "/":
            if command[1:2] == "q":
                break;
        send_message(s, nick, "chat", command)

    end_windows()

if __name__ == "__main__":
    main(sys.argv)
    
