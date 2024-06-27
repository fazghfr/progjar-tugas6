import sys
import os
import json
import uuid
import logging
from queue import  Queue

'''
The following functions are implemented in the `Chat` class:

1. `__init__(self)`: Initializes the `Chat` class with empty dictionaries for sessions, users, and groups, and initializes some default users and groups.
2. `proses(self, data)`: Processes the input data and performs different actions based on the command provided.
3. `autentikasi_user(self, username, password)`: Authenticates the user by checking if the provided username and password match the stored user information.
4. `get_user(self, username)`: Retrieves user information based on the provided username.
5. `get_group(self, groupname)`: Retrieves group information based on the provided groupname.
6. `send_message(self, sessionid, username_from, username_dest, message)`: Sends a message from one user to another user.
7. `create_group(self, sessionid, username, groupname)`: Creates a new group with the provided groupname and adds the creator as a member.
8. `join_group(self, sessionid, username, groupname)`: Adds a user to an existing group.
9. `leave_group(self, sessionid, username, groupname)`: Removes a user from a group.
10. `delete_group(self, sessionid, username, groupname)`: Deletes a group.
11. `send_message_group(self, sessionid, username_from, groupname, message)`: Sends a message from a user to a group.
12. `get_inbox_group(self, sessionId, username, groupname)`: Retrieves the inbox messages for a user in a specific group.
13. `get_inbox(self, username)`: Retrieves the inbox messages for a user.

TODO
- implement multirealms
'''

class Chat:
	def __init__(self):
		self.sessions={}
		self.users = {}
		self.groups = {}

		# initialize users
		self.users['messi']={ 'nama': 'Lionel Messi', 'negara': 'Argentina', 'password': 'surabaya', 'incoming' : {}, 'outgoing': {}, 'group': []}
		self.users['henderson']={ 'nama': 'Jordan Henderson', 'negara': 'Inggris', 'password': 'surabaya', 'incoming': {}, 'outgoing': {}, 'group': ['group1']}
		self.users['lineker']={ 'nama': 'Gary Lineker', 'negara': 'Inggris', 'password': 'surabaya','incoming': {}, 'outgoing':{}, 'group': ['group1']}

		self.groups['group1'] = { 'nama': 'grup inggris', 'incoming': {}, 'outgoing': {}, 'users': ['henderson','lineker']}
	def proses(self,data):
		j=data.split(" ")
		try:
			command=j[0].strip()
			if (command=='auth'):
				username=j[1].strip()
				password=j[2].strip()
				logging.warning("AUTH: auth {} {}" . format(username,password))
				return self.autentikasi_user(username,password)
			elif (command=='logout'):
				sessionid = j[1].strip()
				logging.warning("LOGOUT: {}" . format(sessionid))
				return self.logout_user(sessionid)
			elif (command=='send'):
				sessionid = j[1].strip()
				usernameto = j[2].strip()
				message=""
				for w in j[3:]:
					message="{} {}" . format(message,w)
				usernamefrom = self.sessions[sessionid]['username']
				logging.warning("SEND: session {} send message from {} to {}" . format(sessionid, usernamefrom,usernameto))
				return self.send_message(sessionid,usernamefrom,usernameto,message)
			elif (command=='inbox'):
				sessionid = j[1].strip()
				username = self.sessions[sessionid]['username']
				logging.warning("INBOX: {}" . format(sessionid))
				return self.get_inbox(username)
			
			elif (command=='create_group'):
				sessionid = j[1].strip()
				username = self.sessions[sessionid]['username']
				groupname = j[2].strip()
				logging.warning("CREATE GROUP: {}" . format(groupname))
				return self.create_group(sessionid,username,groupname)
			
			elif (command=='join_group'):
				sessionid = j[1].strip()
				username = self.sessions[sessionid]['username']
				groupname = j[2].strip()
				logging.warning("JOIN GROUP: {}" . format(groupname))
				return self.join_group(sessionid,username,groupname)
			
			elif (command=='leave_group'):
				sessionid = j[1].strip()
				username = self.sessions[sessionid]['username']
				groupname = j[2].strip()
				logging.warning("LEAVE GROUP: {}" . format(groupname))
				return self.leave_group(sessionid,username,groupname)
			
			elif (command=='delete_group'):
				sessionid = j[1].strip()
				username = self.sessions[sessionid]['username']
				groupname = j[2].strip()
				logging.warning("DELETE GROUP: {}" . format(groupname))
				return self.delete_group(sessionid,username,groupname)
			
			elif (command=='send_group'):
				sessionid = j[1].strip()
				usernamefrom = self.sessions[sessionid]['username']
				groupname = j[2].strip()
				message=""
				for w in j[3:]:
					message="{} {}" . format(message,w)
				logging.warning("SEND GROUP: session {} send message from {} to {}" . format(sessionid, usernamefrom,groupname))
				return self.send_message_group(sessionid,usernamefrom,groupname,message)
			
			elif (command=='inbox_group'):
				sessionid = j[1].strip()
				username = self.sessions[sessionid]['username']
				groupname = j[2].strip()
				logging.warning("INBOX GROUP: {}" . format(groupname))
				return self.get_inbox_group(sessionid,username,groupname)
			

			else:
				return {'status': 'ERROR', 'message': '**Protocol Tidak Benar'}
		except KeyError:
			return { 'status': 'ERROR', 'message' : 'Informasi tidak ditemukan'}
		except IndexError:
			return {'status': 'ERROR', 'message': '--Protocol Tidak Benar'}
	def autentikasi_user(self,username,password):
		if (username not in self.users):
			return { 'status': 'ERROR', 'message': 'User Tidak Ada' }
		if (self.users[username]['password']!= password):
			return { 'status': 'ERROR', 'message': 'Password Salah' }
		tokenid = str(uuid.uuid4()) 
		self.sessions[tokenid]={ 'username': username, 'userdetail':self.users[username]}
		return { 'status': 'OK', 'tokenid': tokenid }
	
	def logout_user(self,sessionid):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		del self.sessions[sessionid]
		return {'status': 'OK', 'message': 'Logout Berhasil'}

	def get_user(self,username):
		if (username not in self.users):
			return False
		return self.users[username]
	
	def get_group(self,groupname):
		if (groupname not in self.groups):
			return False
		return self.groups[groupname]
	def send_message(self,sessionid,username_from,username_dest,message):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		s_fr = self.get_user(username_from)
		s_to = self.get_user(username_dest)
		
		if (s_fr==False or s_to==False):
			return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

		message = { 'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': message }
		outqueue_sender = s_fr['outgoing']
		inqueue_receiver = s_to['incoming']
		try:	
			outqueue_sender[username_from].put(message)
		except KeyError:
			outqueue_sender[username_from]=Queue()
			outqueue_sender[username_from].put(message)
		try:
			inqueue_receiver[username_from].put(message)
		except KeyError:
			inqueue_receiver[username_from]=Queue()
			inqueue_receiver[username_from].put(message)
		return {'status': 'OK', 'message': 'Message Sent'}
	
	def create_group(self,sessionid,username,groupname):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		s_fr = self.sessions[sessionid]
		if (groupname in self.groups):
			return {'status': 'ERROR', 'message': 'Group Sudah Ada'}
		
		self.groups[groupname] = { 'nama': groupname, 'incoming': {}, 'outgoing': {}, 'users': [] }
		self.groups[groupname]['users'].append(username)

		# append group to username
		self.users[username]['group'].append(groupname)

		# list all groups created in server
		print(self.groups)
		print(self.users[username])
		return {'status': 'OK', 'message': 'Group Created'}
	
	def join_group(self,sessionid,username,groupname):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		if (groupname not in self.groups):
			return {'status': 'ERROR', 'message': 'Group Tidak Ditemukan'}
		
		s_gr = self.groups[groupname]
		if (username in s_gr['users']):
			return {'status': 'ERROR', 'message': 'User Sudah Ada di Group'}
		s_gr['users'].append(username)
		return {'status': 'OK', 'message': 'User Joined Group'}
	
	def leave_group(self,sessionid,username,groupname):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		if (groupname not in self.groups):
			return {'status': 'ERROR', 'message': 'Group Tidak Ditemukan'}
		
		s_gr = self.groups[groupname]
		if (username not in s_gr['users']):
			return {'status': 'ERROR', 'message': 'User Tidak Ada di Group'}
		
		if len(s_gr['users'])==1:
			return {'status': 'ERROR', 'message': 'Cannot Leave Group, Last User in Group, use delete group instead'}	
		s_gr['users'].remove(username)
		return {'status': 'OK', 'message': 'User Left Group'}
	
	def delete_group(self,sessionid,username,groupname):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		if (groupname not in self.groups):
			return {'status': 'ERROR', 'message': 'Group Tidak Ditemukan'}
		
		s_gr = self.groups[groupname]
		if (username not in s_gr['users']):
			return {'status': 'ERROR', 'message': 'User Tidak Ada di Group'}

		# remove groups from users
		for user in s_gr['users']:
			self.users[user]['group'].remove(groupname)

		
		del self.groups[groupname]
		return {'status': 'OK', 'message': 'Group Deleted'}
	
	def send_message_group(self,sessionid,username_from,groupname,message):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		s_fr = self.get_user(username_from)
		s_gr = self.groups[groupname]
		if (s_fr==False or s_gr==False):
			return {'status': 'ERROR', 'message': 'User atau Group Tidak Ditemukan'}
		
		# check if user is in the group
		if (username_from not in s_gr['users']):
			return {'status': 'ERROR', 'message': 'User Tidak Ada di Group'}
		message = { 'msg_from': s_fr['nama'], 'msg_to': s_gr['nama'], 'msg': message }
		outqueue_sender = s_fr['outgoing']
		inqueue_receiver = s_gr['incoming']
		try:
			outqueue_sender[username_from].put(message)
		except KeyError:
			outqueue_sender[username_from]=Queue()
			outqueue_sender[username_from].put(message)
		try:
			inqueue_receiver[username_from].put(message)
		except KeyError:
			inqueue_receiver[username_from]=Queue()
			inqueue_receiver[username_from].put(message)
		return {'status': 'OK', 'message': 'Message Sent to group'}
	
	def get_inbox_group(self,sessionId,username,groupname):
		if sessionId not in self.sessions:
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}

		if groupname not in self.groups:
			return {'status': 'ERROR', 'message': 'Group Tidak Ditemukan'}

		if username not in self.groups[groupname]['users']:
			return {'status': 'ERROR', 'message': 'User Tidak Ada di Group'}
		
		s_fr = self.get_group(groupname)
		incoming = s_fr['incoming']
		msgs = {}
		for users in incoming:
			msgs[users] = []
			while not incoming[users].empty():
				msgs[users].append(s_fr['incoming'][users].get_nowait()) 

		return {'status': 'OK', 'messages': msgs}

	def get_inbox(self,username):
		s_fr = self.get_user(username)
		incoming = s_fr['incoming']
		msgs={}
		for users in incoming:
			msgs[users]=[]
			while not incoming[users].empty():
				msgs[users].append(s_fr['incoming'][users].get_nowait())
			
		return {'status': 'OK', 'messages': msgs}


if __name__=="__main__":
	j = Chat()
	sesi = j.proses("auth messi surabaya")
	print(sesi)
	#sesi = j.autentikasi_user('messi','surabaya')
	#print sesi
	tokenid = sesi['tokenid']
	print(j.proses("send {} henderson hello gimana kabarnya son " . format(tokenid)))
	print(j.proses("send {} messi hello gimana kabarnya mess " . format(tokenid)))

	#print j.send_message(tokenid,'messi','henderson','hello son')
	#print j.send_message(tokenid,'henderson','messi','hello si')
	#print j.send_message(tokenid,'lineker','messi','hello si dari lineker')


	print("isi mailbox dari messi")
	print(j.get_inbox('messi'))
	print("isi mailbox dari henderson")
	print(j.get_inbox('henderson'))
















