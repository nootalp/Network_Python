import socket

target_ip = "www.google.com"
target_port = 80

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((target_ip, target_port))
client.send("GET / HTTP/1.1\r\nHost: google.com\r\n\r\n".encode())

response = client.recv(4096)
print(response)
