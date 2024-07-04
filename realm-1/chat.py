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
- get all user
- get all group
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
	def __init__(self, REALM_IP, REALM_PORT):
		self.sessions={}
		self.sessions['server'] = {'username': 'server', 'userdetail': {}} # special session for server
		self.users = {}
		self.groups = {}
		self.realm = { 'ip': REALM_IP, 'port': REALM_PORT}
		self.known_realms = [('127.0.0.1', 1112)]

		self.temp_outgoing={}


		# initialize users
		self.users['messi']={ 'nama': 'Lionel Messi', 'negara': 'Argentina', 'password': 'surabaya', 'incoming' : {}, 'outgoing': {}, 'group': [], 'realm': self.realm}
		self.users['dev']={ 'nama': 'dev', 'negara': 'dev', 'password': 'dev', 'incoming' : {}, 'outgoing': {}, 'group': []}
		self.users['henderson']={ 'nama': 'Jordan Henderson', 'negara': 'Inggris', 'password': 'surabaya', 'incoming': {}, 'outgoing': {}, 'group': ['group1'], 'realm': self.realm}
		self.users['lineker']={ 'nama': 'Gary Lineker', 'negara': 'Inggris', 'password': 'surabaya','incoming': {}, 'outgoing':{}, 'group': ['group1'], 'realm': self.realm}

		self.groups['group1'] = { 'nama': 'grup inggris', 'incoming': {}, 'outgoing': {}, 'users': ['henderson','lineker'], 'realm': self.realm}
	def proses(self,data):
		is_different_realm = False
		j=data.split(" ")
		print("splitted data ",j)
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

				if "server" not in sessionid:
					usernamefrom = self.sessions[sessionid]['username']
				else :
					usernamefrom = sessionid.split('=')[1]
				logging.warning("SEND: session {} send message from {} to {}" . format(sessionid, usernamefrom,usernameto))
				return self.send_message(sessionid,usernamefrom,usernameto,message)
			
			elif (command=='get_all_users'):
				sessionid = j[1].strip()
				logging.warning("GET ALL USERS: {}" . format(sessionid))
				return self.get_all_users(sessionid)
			
			elif (command=='get_all_groups'):
				sessionid = j[1].strip()
				logging.warning("GET ALL GROUPS: {}" . format(sessionid))
				return self.get_all_groups(sessionid)
			
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
				groupname = j[2].strip()

				if "server" not in sessionid:
					usernamefrom = self.sessions[sessionid]['username']
				else :
					usernamefrom = sessionid.split('=')[1]
				
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
		
	def pop_temp(self, username):
		message = self.temp_incoming[username]
		user_obj = self.get_user(message['msg_from'])
		message['msg_from'] = user_obj['nama']

		final_msg = message

		outqueue_sender = user_obj['outgoing']
		try:	
			outqueue_sender[username].put(final_msg)
		except KeyError:
			outqueue_sender[username]=Queue()
			outqueue_sender[username].put(final_msg)

		del self.temp_outgoing[username]
		return {'status': 'OK', 'message': '*Popped temp'}
			
		
		
		
		
	def autentikasi_user(self,username,password):
		if (username not in self.users):
			return { 'status': 'ERROR', 'message': 'User Tidak Ada' }
		if (self.users[username]['password']!= password):
			return { 'status': 'ERROR', 'message': 'Password Salah' }
		tokenid = str(uuid.uuid4()) 
		self.sessions[tokenid]={ 'username': username, 'userdetail':self.users[username]}
		return { 'status': 'OK', 'tokenid': tokenid }
	
	# realm related functions
	def check_realm(self, obj):
		if (obj['realm']['ip'] != self.realm['ip'] or obj['realm']['port'] != self.realm['port']):
			return False
		return True
	
	# called by the server to add realm
	def add_realm(self, ip, port):
		self.known_realms.append({'ip': ip, 'port': port})
	
	def logout_user(self,sessionid):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		del self.sessions[sessionid]
		return {'status': 'OK', 'message': 'Logout Berhasil'}

	def get_user(self,username):
		if (username not in self.users):
			return False
		return self.users[username]
	
	def get_all_users(self, sessionid):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		# make sure that this session belongs to dev
		if (self.sessions[sessionid]['username'] != 'dev'):
			return {'status': 'ERROR', 'message': 'Forbidden Access'}
		return {'status': 'OK', 'users': self.users}
	
	def get_all_groups(self, sessionid):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		# make sure that this session belongs to dev
		if (self.sessions[sessionid]['username'] != 'dev'):
			return {'status': 'ERROR', 'message': 'Forbidden Access'}
		return {'status': 'OK', 'groups': self.groups}
	
	def get_group(self,groupname):
		if (groupname not in self.groups):
			return False
		return self.groups[groupname]
	def send_message(self,sessionid,username_from,username_dest,message):
		print("session id ", sessionid)
		if (sessionid not in self.sessions and 'server' not in sessionid):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		
		if 'server' in sessionid:
			s_fr = username_from # just the username
		else:	
			s_fr = self.get_user(username_from)
			if s_fr==False:
				return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}
			
		self.temp_outgoing[username_from] = { 'msg_from': username_from, 'msg_to': username_dest, 'msg': message }
		s_to = self.get_user(username_dest)
		
		if ((s_to==False) and 'server' not in sessionid):
			# try to find the user in another realm
			
			for realm in self.known_realms:
				# as realm is a tuple, index 0 is ip and index 1 is port
				# check if the realm is the same as the current realm
				if (realm[0] == self.realm['ip'] and realm[1] == self.realm['port']):
					continue

				# remove the last two characters of the message
				message = message[:-2]
				string="send {} {} \r\n" . format(username_dest,message)

				json_for_communicator = {'status': 'NAV',
						'ip': realm[0], 'port': realm[1], 
						'username_fr': username_from}


				# give a sign to server to handle
				return json_for_communicator
			
		elif(s_to==False):
			return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

		if "server" not in sessionid:
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

			del self.temp_outgoing[username_from]
			return {'status': 'OK', 'message': 'Message Sent'}
		
		else : 
			# mengasumsikan temp_incoming insertion implemented (belum)
			message = { 'msg_from': s_fr, 'msg_to': s_to['nama'], 'msg': message }
			inqueue_receiver = s_to['incoming']
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
		
		s_gr = self.get_group(groupname)

		if s_gr==False and 'server' not in sessionid:
			for realm in self.known_realms:
				# as realm is a tuple, index 0 is ip and index 1 is port
				# check if the realm is the same as the current realm
				if (realm[0] == self.realm['ip'] and realm[1] == self.realm['port']):
					continue

				# remove the last two characters of the message
				string="join_group {}\r\n" . format(groupname)

				json_for_communicator = {'status': 'NAV',
						'ip': realm[0], 'port': realm[1], 
						'username_fr': username}

				# give a sign to server to handle
				return json_for_communicator
			
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

		if s_gr==False and 'server' not in sessionid:
			for realm in self.known_realms:
				# as realm is a tuple, index 0 is ip and index 1 is port
				# check if the realm is the same as the current realm
				if (realm[0] == self.realm['ip'] and realm[1] == self.realm['port']):
					continue

				# remove the last two characters of the message
				message = message[:-2]
				string="leave_group {}\r\n" . format(groupname)

				json_for_communicator = {'status': 'NAV',
						'ip': realm[0], 'port': realm[1], 
						'username_fr': username}

				# give a sign to server to handle
				return json_for_communicator
			
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

		if s_gr==False and 'server' not in sessionid:
			for realm in self.known_realms:
				# as realm is a tuple, index 0 is ip and index 1 is port
				# check if the realm is the same as the current realm
				if (realm[0] == self.realm['ip'] and realm[1] == self.realm['port']):
					continue

				# remove the last two characters of the message
				message = message[:-2]
				string="delete_group {}\r\n" . format(groupname)

				json_for_communicator = {'status': 'NAV',
						'ip': realm[0], 'port': realm[1], 
						'username_fr': username}

				# give a sign to server to handle
				return json_for_communicator
			
		if (username not in s_gr['users']):
			return {'status': 'ERROR', 'message': 'User Tidak Ada di Group'}

		# remove groups from users
		for user in s_gr['users']:
			self.users[user]['group'].remove(groupname)

		
		del self.groups[groupname]
		return {'status': 'OK', 'message': 'Group Deleted'}
	
	def send_message_group(self,sessionid,username_from,groupname,message):
		if (sessionid not in self.sessions and 'server' not in sessionid):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}

		if 'server' in sessionid:
			s_fr = username_from
		else :
			s_fr = self.get_user(username_from)

		g_to = self.get_group(groupname)
		if (g_to==False and 'server' not in sessionid):
			# try to find the group in another realm
			for realm in self.known_realms:
				# as realm is a tuple, index 0 is ip and index 1 is port
				# check if the realm is the same as the current realm
				if (realm[0] == self.realm['ip'] and realm[1] == self.realm['port']):
					continue

				# remove the last two characters of the message
				message = message[:-2]
				string="send_group {} {} \r\n" . format(groupname,message)

				json_for_communicator = {'status': 'NAV',
						'ip': realm[0], 'port': realm[1], 
						'username_fr': username_from}

				# give a sign to server to handle
				return json_for_communicator
			
		elif(g_to==False):
			return {'status': 'ERROR', 'message': 'Group Tidak Ditemukan'}
		
		# check if user is in the group
		if (username_from not in g_to['users']):
			return {'status': 'ERROR', 'message': 'User Tidak Ada di Group'}
		
		if "server" not in sessionid:
			message = { 'msg_from': s_fr['nama'], 'msg_to': g_to['nama'], 'msg': message }
			outqueue_sender = s_fr['outgoing']
			inqueue_receiver = g_to['incoming']
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
			# del self.temp_outgoing[username_from]
			return {'status': 'OK', 'message': 'Message Sent to group'}
		
		else:
			message = { 'msg_from': s_fr, 'msg_to': g_to['nama'], 'msg': message }
			inqueue_receiver = g_to['incoming']
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
















