import socket
from datetime import datetime
 
address = ('localhost',1138)
max_size = 1024

print("Start the client at {}".format(datetime.now()))

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect(address)

while(1):
	client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	client.connect(address)
	str=input("message：")
	client.sendall(bytes(str,encoding='utf-8'))
	data = client.recv(max_size)
	print("AT",datetime.now(),"some reply" , data)
	client.close()


