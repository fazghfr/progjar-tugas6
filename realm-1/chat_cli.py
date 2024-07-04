import socket
import os
import json

# i want to use this ChatClient class in other python file, how?


TARGET_IP = "127.0.0.1"
TARGET_PORT = 1111

'''
implemented function:
- proses : memproses given command dari user input, entah itu auth, send, atau inbox
- sendstring : mengirimkan string ke server dan menerima balasan dari server, ini di implement di dalem login,`sendmessage`, dan `inbox`
- login : buat login
- sendmessage : buat send message ke user lain (for now masih gaada antar realm)
- inbox : ngambil inbox punya sendiri, harus login dulu
- logout : buat logout
- create_group : buat create group
- join_group : buat join group
- leave_group : buat leave group
- delete_group : buat delete group
- send_message_group : buat send message ke group
- inbox_group : ngambil inbox group, harus join group dulu


'''
glob_data = "{'status': 'OK', 'message': 'Message Sent'}"

class ChatClient:
    def __init__(self, target_ip=TARGET_IP, target_port=TARGET_PORT, is_server=False, real_username=""):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (target_ip,target_port)
        self.sock.connect(self.server_address)
        self.data = glob_data
        
        self.is_server = is_server
        self.real_username_fr = ""

        if self.is_server:
            self.real_username_fr = real_username
        self.tokenid=""

    def reconnect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.server_address)
        self.tokenid=""
        return True
    def proses(self,cmdline):
        j=cmdline.split(" ")
        print("j ",j)
        try:
            command=j[0].strip()
            if (command=='auth'):
                username=j[1].strip()
                password=j[2].strip()
                return self.login(username,password)
            
            elif (command=='logout'):
                return self.logout()
            elif (command=='send'):
                usernameto = j[1].strip()
                message=""
                for w in j[2:]:
                   message="{} {}" . format(message,w)
                return self.sendmessage(usernameto,message)
            elif (command=='inbox'):
                return self.inbox()
            
            elif (command=='get_all_users'):
                return self.get_all_users()
            
            elif (command=='get_all_groups'):
                return self.get_all_groups()
            
            elif (command=='create_group'):
                groupname=j[1].strip()
                return self.create_group(groupname)
            
            elif (command=='join_group'):
                groupname=j[1].strip()
                return self.join_group(groupname)
            
            elif (command=='leave_group'):
                groupname=j[1].strip()
                return self.leave_group(groupname)
            
            elif (command=='delete_group'):
                groupname=j[1].strip()
                return self.delete_group(groupname)
            
            elif (command=='send_group'):
                groupname=j[1].strip()
                message=""
                for w in j[2:]:
                   message="{} {}" . format(message,w)
                return self.send_message_group(groupname,message)
            
            elif (command=='inbox_group'):
                groupname=j[1].strip()
                return self.inbox_group(groupname)
            
            elif(command=='exit' or command=='quit'):
                self.sock.close()
                return True

            else:
                return "*Maaf, command tidak benar"
        except IndexError:
                return "-Maaf, command tidak benar"
    def sendstring(self,string):
        try:
            self.sock.sendall(string.encode())
            receivemsg = ""
            while True:
                data = self.sock.recv(64)
                print("diterima dari server",data)
                if (data):  
                    glob_data = data
                    receivemsg = "{}{}" . format(receivemsg,data.decode())  #data harus didecode agar dapat di operasikan dalam bentuk string
                    if receivemsg[-4:]=='\r\n\r\n':
                        print("end of string")
                        return json.loads(receivemsg)
        except:
            print("ada error")
            # self.sock.close()
            # self.reconnect()
            return { 'status' : 'ERROR', 'message' : 'Gagal'}
    
    # TODO
    # implement this, refer to Tugas 4 code
    def send_file(self, filename):
        return False    
    def login(self,username,password):
        string="auth {} {} \r\n" . format(username,password)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.tokenid=result['tokenid']
            return "username {} logged in, token {} " .format(username,self.tokenid)
        else:
            return "Error, {}" . format(result['message'])
    def logout(self):
        string="logout {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            # clear tokenid
            self.tokenid=""
            return "user logged out"
        else:
            return "Error, {}" . format(result['message'])
    def sendmessage(self,usernameto="xxx",message="xxx"):
        if (self.tokenid=="" and not self.is_server):
            return "Error, not authorized"
        
        if self.tokenid=="":
            self.tokenid="server="+self.real_username_fr+"="
        string="send {} {} {} \r\n" . format(self.tokenid,usernameto,message)
        print(string)
        result = self.sendstring(string)

        if type(result) != dict and not self.is_server:
            # convert to dict
            result = json.loads(result)
        if result['status']=='OK' and not self.is_server:
            return "message sent to {}" . format(usernameto)
        elif self.is_server:
            return "{}" . format(json.dumps(result))
        else:
            return "Error, {}" . format(result['message'])
    def inbox(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inbox {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['messages']))
        else:
            return "Error, {}" . format(result['message'])
        
    def get_all_users(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="get_all_users {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['users']))
        else:
            return "Error, {}" . format(result['message'])
        
    def get_all_groups(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="get_all_groups {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['groups']))
        else:
            return "Error, {}" . format(result['message'])
        
    def create_group(self, groupname):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="create_group {} {} \r\n" . format(self.tokenid, groupname)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "group {} created : groups {}" . format(groupname)
        else:
            return "Error, {}" . format(result['message'])
        
    def join_group(self, groupname):
        if (self.tokenid=="" and not self.is_server):
            return "Error, not authorized"
        
        if self.tokenid=="":
            self.tokenid="server="+self.real_username_fr+"="
        string="join_group {} {} \r\n" . format(self.tokenid, groupname)
        result = self.sendstring(string)
        if type(result) != dict and not self.is_server:
            # convert to dict
            result = json.loads(result)
        if result['status']=='OK' and not self.is_server:
            return "group {} joined : groups {}" . format(groupname)
        elif self.is_server:
            return "{}" . format(json.dumps(result))
        else:
            return "Error, {}" . format(result['message'])
        
    def leave_group(self, groupname):
        if (self.tokenid=="" and not self.is_server):
            return "Error, not authorized"
        
        if self.tokenid=="":
            self.tokenid="server="+self.real_username_fr+"="
        string="leave_group {} {} \r\n" . format(self.tokenid, groupname)
        result = self.sendstring(string)
        if type(result) != dict and not self.is_server:
            # convert to dict
            result = json.loads(result)
        if result['status']=='OK' and not self.is_server:
            return "group {} left : groups {}" . format(groupname)
        elif self.is_server:
            return "{}" . format(json.dumps(result))
        else:
            return "Error, {}" . format(result['message'])
        
    def delete_group(self, groupname):
        if (self.tokenid=="" and not self.is_server):
            return "Error, not authorized"
        
        if self.tokenid=="":
            self.tokenid="server="+self.real_username_fr+"="
        string="delete_group {} {} \r\n" . format(self.tokenid, groupname)
        result = self.sendstring(string)
        if type(result) != dict and not self.is_server:
            # convert to dict
            result = json.loads(result)
        if result['status']=='OK' and not self.is_server:
            return "group {} deleted : groups {}" . format(groupname)
        elif self.is_server:
            return "{}" . format(json.dumps(result))
        else:
            return "Error, {}" . format(result['message'])
        
    def send_message_group(self, groupname, message):
        if (self.tokenid=="" and not self.is_server):
            return "Error, not authorized"
        
        if self.tokenid=="":
            self.tokenid="server="+self.real_username_fr+"="
        string="send_group {} {} {} \r\n" . format(self.tokenid, groupname, message)
        print(string)
        result = self.sendstring(string)
        if type(result) != dict and not self.is_server:
            # convert to dict
            result = json.loads(result)
        if result['status']=='OK' and not self.is_server:
            return "message sent to group {}" . format(groupname)
        elif self.is_server:
            return "{}" . format(json.dumps(result))
        else:
            return "Error, {}" . format(result['message'])
        
    def inbox_group(self, groupname):
        if (self.tokenid=="" and not self.is_server):
            return "Error, not authorized"
        
        if self.tokenid=="":
            self.tokenid="server="+self.real_username_fr+"="
        string="inbox_group {} {} \r\n" . format(self.tokenid, groupname)
        result = self.sendstring(string)

        if type(result) != dict and not self.is_server:
            # convert to dict
            result = json.loads(result)
        if result['status']=='OK' and not self.is_server:
            return "{}" . format(json.dumps(result['messages']))
        elif self.is_server:
            return "{}" . format(json.dumps(result))
        else:
            return "Error, {}" . format(result['message'])
        
        
    



if __name__=="__main__":
    cc = ChatClient()
    while True:
        cmdline = input("Command {}:" . format(cc.tokenid))
        str_response=cc.proses(cmdline)
        if (str_response==True):
            print("good bye")
            break
        print(str_response)

