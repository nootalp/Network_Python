import socket
import threading

bind_ip = "0.0.0.0"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Associa o IP com a porta.
server.bind((bind_ip, bind_port))
server.listen(5)

print("[*] Listening on %s:%d" % (bind_ip, bind_port))


def handle_client(client_socket):
    # Recebe os dados enviados pelo cliente.
    request = client_socket.recv(1024)
    print("[*] Received: %s" % request)
    # Envia RECONHECIMENTO para o cliente.
    client_socket.send("ACK!".encode())
    # A conexão com o cliente é terminada.
    client_socket.close()


# Loop de escuta para novas conexões.
while True:
    # Retorna uma tupla contendo o objeto socket e o endereço do cliente.
    client, addr = server.accept()
    print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))
    # Cria nova thread para lidar com a conexão.
    # Ela é configurada para chamar a função "handle_client",
    # Passando como parâmetro o objeto socket.
    client_handler = threading.Thread(target=handle_client, args=(client,))
    # A nova thread é criada, aguardando novas conexões.
    client_handler.start()
