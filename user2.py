import socket

# client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #AF_INET（IPV4使用） SOCK_STREAM（TCP模式）

client.connect(('localhost', 8080))         #连接本地回环地址127.0.0.1 端口号8080 以元组作为参数

print(client.recv(1024).decode('utf-8'))

while True:
    sendbuf = input()                      # 输入
    client.send(sendbuf.encode('utf-8'))   # UTF-8编码
    if not sendbuf or sendbuf == 'exit':   #退出条件判断
        break
    recvbuf = client.recv(1024)
    print(recvbuf.decode('utf-8'))        # 解码
client.close()                            # 断开连接
print('Connection was closed...')
