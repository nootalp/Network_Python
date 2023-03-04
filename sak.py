import sys
import socket
import getopt
import threading
import subprocess
import random
from termcolor import colored

listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

'''
def signal_handler():
    print("Received signal. Closing server...")
    sys.exit(0)


# Espera pelo sinal de fechamento;
signal.signal(signal.SIGINT, signal_handler())
'''


def usage():
    phrase = "\nSwiss Army Knife\n\tPython Network Tool\n"
    colors = ["cyan", "green", "light_blue"]

    colored_string = ""
    prev_color_index = None

    for char in phrase:
        color_index = prev_color_index

        while color_index == prev_color_index:
            color_index = random.randint(0, len(colors) - 1)
        prev_color_index = color_index

        colored_char = colored(char, colors[color_index])
        colored_string += colored_char
    print(colored_string)

    print("Usage: sak.py -t target_host -p port")
    print("\t-l --listen - listen on [host]:[port] for incoming connections")
    print("\t-e --execute=file_to_run - execute the given file upon receiving a connection")
    print("\t-c --command - initialize a command shell")
    print("\t-u --upload=destination - upon receiving connection upload a file and write to [destination]")
    print("\nExamples:")
    print("\tsak.py -t 192.168.0.1 -p 5555 -l -c")
    print("\tsak.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print("\tsak.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print("\techo 'ABCDEFGHI' | ./sak.py -t 192.168.11.12 -p 135\n")

    note = colored("Note: This tool is for educational purposes only.\n", "green")
    print(note)
    sys.exit(0)


def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((target, port))
        if len(buffer):
            client.send(buffer)

        while True:
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break
            print(response)

            buffer = input("")
            buffer += "\n"

            client.send(buffer.encode())
    except OSError as e:
        print(f"Error connecting to {target}:{port}: {e}")
        client.close()
    except Exception as e:
        print(f"Error: {e}")
        client.close()


def client_handler(client_socket):
    global upload
    global execute
    global command

    if len(upload_destination):
        file_buffer = ""
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer.encode())
            file_descriptor.close()
            client_socket.send("Successfully saved file to %s\n" % upload_destination)
        except OSError as err:
            client_socket.send("Failed to save file to %s\n: %s" % (upload_destination, err))

    if len(execute):
        output = run_command(execute)
        client_socket.send(output)

    if command:
        while True:
            client_socket.send("<SAK:#> ".encode())
            cmd_buffer = ""

            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024).decode()

            response = run_command(cmd_buffer)
            client_socket.send(response)


def server_loop():
    global target
    # if no target is defined, we listen on all interfaces
    if not len(target):
        target = "0.0.0.0"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()


def run_command(command_line):
    command_line = command_line.rstrip()
    try:
        output = subprocess.check_output(command_line, stderr=subprocess.STDOUT, shell=True)
    except Exception as err:
        output = "Failed to execute command.\n\t%s" % err
    return output


def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target
    opts = []

    if not len(sys.argv[1:]):
        usage()

    try:
        opts, args = getopt.getopt(
                sys.argv[1:], "hle:t:p:cu:",
                ["help", "listen", "execute", "target", "port", "command", "upload"]
        )
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

    if not listen and len(target) and port > 0:
        buffer = sys.stdin.read()
        client_sender(buffer)

    if listen:
        server_loop()


main()
