import socket
import json
import base64
import logging

server_address=('0.0.0.0',7777)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning(f"sending message ")
        sock.sendall(command_str.encode())
        # Look for the response, waiting until socket is done (no more data)
        data_received="" #empty string
        while True:
            #socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
            data = sock.recv(16)
            if data:
                #data is not empty, concat with previous content
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                # no more data, stop the process by break
                break
        # at this point, data_received (string) will contain all data coming from the socket
        # to be able to use the data_received as a dict, need to load it using json.loads()
        hasil = json.loads(data_received)
        logging.warning("data received from server:")
        return hasil
    except:
        logging.warning("error during data receiving")
        return False
    
def remote_list():
    command_str=f"LIST"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        print("daftar file : ")
        for nmfile in hasil['data']:
            print(f"- {nmfile}")
        return True
    else:
        print("Gagal")
        return False

def remote_get(filename=""):
    command_str=f"GET {filename}"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        #proses file dalam bentuk base64 ke bentuk bytes
        namafile= hasil['data_namafile']
        isifile = base64.b64decode(hasil['data_file'])
        fp = open(namafile,'wb+')
        fp.write(isifile)
        fp.close()
        return True
    else:
        print("Gagal")
        return False

def remote_upload(filename=""):
    try:
        fp = open(filename,'rb') 
        isifile = base64.b64encode(fp.read())
        # print(isifile)
        # return False
        fp.close()

        # if this is a large file, it is better to send the file in chunks
        # server accepts max 32 bytes, so we need to split the file into 32 bytes, jadi datanya sisa 16  
        # max total is 32
        
        chunk_data_size = 32
        isifile = [isifile[i:i+chunk_data_size] for i in range(0,len(isifile),chunk_data_size)]
        # print(isifile)
        # return False
        for i in range(len(isifile)):
            isifile[i] = isifile[i].decode()
            command_str=f"DATA {filename} {i} {isifile[i]}"
            hasil = send_command(command_str)
            if (hasil['status']=='ERROR'):
                print(command_str)
                print(f"Gagal chunk ke-{i}")
                remote_delete(filename)
                return False

        print("upload berhasil")
        return True 
    except:
        print("Gagal")
        remote_delete(filename)
        return False
    
def remote_delete(filename=""):
    command_str=f"DELETE {filename}"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        print("delete berhasil")
        return True
    else:
        print("Gagal")
        return False

if __name__=='__main__':
    server_address=('172.16.16.101',6666)
    print("Anda akan terhubung ke server dengan ip address: 172.16.16.101 dan port 6666")

    # user input if GET, DELETE, UPLOAD, and LIST
    while(True):
        input_command = input("Masukkan perintah: ")
        if (input_command.lower() == "list"):
            remote_list()
        elif (input_command.lower() == "get"):
            filename = input("Masukkan nama file: ")
            remote_get(filename)
        elif (input_command.lower() == "upload"):
            filename = input("Masukkan nama file: ")
            remote_upload(filename)
        elif (input_command.lower() == "delete"):
            filename = input("Masukkan nama file: ")
            remote_delete(filename)
        elif (input_command.lower() == "exit"):
            break
        else:
            print("Perintah tidak dikenali")
            

