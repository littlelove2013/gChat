#!/usr/bin/env python
# -*- coding:utf8 -*-
import sys
import threading
import socket
import json
import os

class NetServer(object):
	def __init__(self):
		self.client={}
		#self.user={}#记录注册的用户列表，并且实时写到文本中去json字符串
		self.userdocname="./GCUserbackup.txt"
		self.loadUserFromFile()
		self.mutex = threading.Lock()
		self.writemutex= threading.Lock()
	def tcpServer(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind(('', 9527))		#
		sock.listen(5)
		print("================Start Server================")
		while True:
			clientSock, (remoteHost, remotePort) = sock.accept()
			#print("[%s:%s] connect" % (remoteHost, remotePort))		#
			#新线程回复
			worker_th=threading.Thread(target = self.solverClient,args=(clientSock,remoteHost, remotePort))
			worker_th.start()
			#solverClient(clientSocket,remoteHost, remotePort)
	#solver
	def solverClient(self,clientSock,remoteHost, remotePort):
		revcData = clientSock.recv(1024)
		try:
			revcData=json.loads(revcData.decode())
		except Exception as e:
			print ("error %s"%e)
			return None
		#print(revcData)
		name=revcData["Name"]
		pwd=revcData["Pwd"]
		operator=revcData["Operator"]
		data=revcData["Data"]
		#需要先注册
		if("Register" in operator.keys() and operator["Register"]):
			if(not name in self.user.keys()):
				if(self.register(name,pwd)):
					sendData=json.dumps({"Error":0,"Data":"注册成功！"}).encode()
					print("%s [%s:%d] Registered at [%s]."%(name,remoteHost, remotePort,data["Time"]))
				else:
					sendData=json.dumps({"Error":-1,"Data":"注册失败，请重试！"}).encode()
					print("%s [%s:%d] Register error at [%s]."%(name,remoteHost, remotePort,data["Time"]))
				sendDataLen = clientSock.send(sendData)
				clientSock.close()
				return None
			else:
				sendData=json.dumps({"Error":-1,"Data":"用户不允许重复注册！"}).encode()
				print("%s [%s:%d] repeate registration at [%s]."%(name,remoteHost, remotePort,data["Time"]))
				sendDataLen = clientSock.send(sendData)
				clientSock.close()
				return None
		if("UpdatePwd" in operator.keys() and operator["UpdatePwd"]):
			if(not name in self.user.keys()):
				sendData=json.dumps({"Error":-1,"Data":"不存在用户名，请先注册！"}).encode()
				print("Unknown user %s [%s:%d] request at [%s]."%(name,remoteHost, remotePort,data["Time"]))
				sendDataLen = clientSock.send(sendData)
				clientSock.close()
				return None
			else:
				if(self.register(name,pwd,True)):
					sendData=json.dumps({"Error":0,"Data":"密码更新成功！"}).encode()
					print("%s [%s:%d] Update password at [%s]."%(name,remoteHost, remotePort,data["Time"]))
				else:
					sendData=json.dumps({"Error":-1,"Data":"密码更新失败，请重试！"}).encode()
				sendDataLen = clientSock.send(sendData)
				clientSock.close()
				return None
		#只获取更新信息
		if("Update" in operator.keys() and operator["Update"]):
			if(name in self.client.keys()):
				sendData=json.dumps({"Error":0,"Data":self.client}).encode()
				sendDataLen = clientSock.send(sendData)
				clientSock.close()
				print("%s [%s] request client list!"%(name,remoteHost))
				return None
			else:
				sendData=json.dumps({"Error":-1,"Data":"Please Login First!"}).encode()
				sendDataLen = clientSock.send(sendData)
				clientSock.close()
				print("Warning: Non-registered user %s [%s] attempt request client list!"%(name,remoteHost))
				return None
		elif("Login" in operator.keys() and operator["Login"]):
			if(not name in self.user.keys()):
				#未注册用户
				sendData=json.dumps({"Error":-1,"Data":"未注册用户，请先注册！"}).encode()
				sendDataLen = clientSock.send(sendData)
				#print("未注册用户，请先注册！")
				clientSock.close()
				return None
			#密码错误
			if(not pwd == self.user[name]["Pwd"]):
				#密码错误
				sendData=json.dumps({"Error":-1,"Data":"用户账户名和密码不匹配！"}).encode()
				sendDataLen = clientSock.send(sendData)
				clientSock.close()
				return None
			if(name in self.client.keys()):
				print("%s repeat login"%(name))
				#-2为强制下线
				sendData=json.dumps({"Error":-2,"Data":"Your account \"%s\" is logging in from a differen location [%s:%d] at time [%s]. The current login will be logged out. Please log in again."%(name,remoteHost, remotePort,data["Time"])}).encode()
				#通过udp发送给重复登陆的用户
				sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				sock.sendto(sendData, (self.client[name]["Host"], self.client[name]["Port"]))
				sock.close()
				#sendDataLen = clientSock.send(sendData)
				#clientSock.close()
				#print("%s attemp to request client list!"%(name))
				#return None
			self.writeClientList(name,data,remoteHost, remotePort,flag=True)
			sendData=json.dumps({"Error":0,"Data":self.client}).encode()
			sendDataLen = clientSock.send(sendData)
			print("%s [%s:%d] Login at [%s]."%(name,remoteHost, remotePort,data["Time"]))
			clientSock.close()
			return True
		elif("Logout" in operator.keys() and operator["Logout"]):
			self.writeClientList(name,data,remoteHost, remotePort,flag=False)
			sendData=json.dumps({"Error":0,"Data":self.client}).encode()
			sendDataLen = clientSock.send(sendData)
			print("%s [%s:%d] Logout at [%s]."%(name,remoteHost, remotePort,data["Time"]))
			clientSock.close()
			return True
	def writeClientList(self,clientName,clientData,remoteHost, remotePort,flag=True):#
		info={"Name":clientName,"Host":remoteHost,"Port":remotePort,"Time":clientData["Time"]}
		if(not flag and not clientName in self.client.keys()):
			return None
		if(flag and clientName in self.client.keys()):
			print("Forced offline %s [%s:%d]"%(self.client[clientName]["Name"],self.client[clientName]["Host"],self.client[clientName]["Port"]))
		if self.mutex.acquire(1):  
			if(flag):
				self.client[clientName]=info
			else:
				del self.client[clientName]
			self.mutex.release()
	
	def saveUserToFile(self):
		if(len(self.user)==0):
			return False
		tmpj=json.dumps(self.user)
		#加锁
		if self.mutex.acquire(1): 
			with open(self.userdocname,'w') as f:
				f.write(tmpj)
			self.mutex.release()
		return True
	def loadUserFromFile(self):
		if(not os.path.exists(self.userdocname)):
			self.user={}
		else:
			with open(self.userdocname,'r') as f:
				tmpj=f.read()
				try:
					self.user=json.loads(tmpj)
				except Exception as e:
					self.user={}
	def register(self,username,pwd,updatepwd=False):
		if(not updatepwd and not username in self.user.keys()):
			self.user[username]={}
			self.user[username]["Username"]=username
			self.user[username]["Pwd"]=pwd
			#写入文本
			return self.saveUserToFile()
		elif(updatepwd and username in self.user.keys()):
			self.user[username]["Pwd"]=pwd
			#写入文本
			return self.saveUserToFile()
		return False
if __name__ == "__main__":
	netServer = NetServer()
	netServer.tcpServer()
