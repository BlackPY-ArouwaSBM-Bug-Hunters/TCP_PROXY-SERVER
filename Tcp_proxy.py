

import sys
import socket
import threading


hex_fulter=''.join([(len(repr(chr(i)))==3) and chr(i) or '.' for i in range(256)])
def hexdump(src,length=16,show=True):
    if isinstance(src,bytes):
        src=src.decode()

    lis=[]
    for i in range(0,len(src),length):
        word=str(src[i:i+length])
        printa=word.translate(hex_fulter)

        hexa=' '.join([f'{ord(c):02X}' for c in word])
        hex_width=length*3

        lis.append(f'{i:04x}  {hexa:<{hex_width}} {printa}')
    if show:
        for line in lis:
            print(line)
    else:
        return lis
    
def received_from(connection):
    buffer=b''
    connection.settimeout(5)

    try:
        while True:
            data=connection.recv(4096)
            if not data:
                break
            buffer+=data
    except Exception as e:
        pass
    return buffer

def request_handler(buffer):
    # modified
    return buffer 
def response_handler(buffer):
    # modified
    return buffer

def proxy_hadler(client_socket,remote_host,remote_port,receive_first):
    remote_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    remote_socket.connect((remote_host,remote_port))

    if receive_first:
        remote_buffer=received_from(remote_socket)
        hexdump(remote_buffer)
    remote_buffer=response_handler(remote_buffer)
    if len(remote_buffer):
        print('[<==] sending %d bytes to local_host'%len(remote_buffer))
        client_socket.send(remote_buffer)

    while True:
        local_buffer=received_from(client_socket)
        if len(local_buffer):
            print('[==>] receiced %d bytes from local_host'%len(local_buffer))
            hexdump(local_buffer)
            local_buffer=request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print('[==>] Send to remote')

        remote_buffer=received_from(remote_socket)
        if len(remote_buffer):
            print('[<==] Received %d bytes from rmeote'%len(remote_buffer))
            hexdump(remote_buffer)
            remote_buffer=response_handler(remote_buffer)
            
            client_socket.send(remote_buffer)
            print('[<==] send to local host')
            
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print('[*] No more data Closing connection...')
            break


def server_loop(local_host,local_port,remote_host,remote_port,receive_first):
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    try:
        server.bind((local_host,local_port))
    except Exception as e:
        print('[!!] Problem on Bind %r'%e)
        print('[!!] Failed to listen %s:%d'%(local_host,local_port))
        print('[!!] Check other connection or permission')
        sys.exit(0)

    print('[*] listening on %s:%d'%(local_host,local_port))
    server.listen(5)
    while True:
        client_socket,user=server.accept()
        print('Received incomming connection from %s:%d'%(user[0],user[1]))
        proxy_thread=threading.Thread(target=proxy_hadler,args=(client_socket,remote_host,remote_port,receive_first))
        proxy_thread.start()


def main():
    if len(sys.argv[1:])!=5:
        print('User : ./proxy.py [localHost] [localPort]',end='')
        print('[rmote_host] [remote_port] [receive_first]')
        print('Exaple: ./proxy.py 127.0.0.1 9000 0.0.0.0 90000 True')
        sys.exit(0)

    local_host=sys.argv[1]
    local_port=int(sys.argv[2])
    remote_host=sys.argv[3]
    remote_port=int(sys.argv[4])
    receive_first=sys.argv[5]

    if "True" in receive_first:
        receive_first=True
    else:
        receive_first=False

    server_loop(local_host,local_port,remote_host,remote_port,receive_first)

if __name__=="__main__":
    main()