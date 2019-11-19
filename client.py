#!/usr/bin/env python
# -*- coding:utf8 -*-
import sys
import threading
import socket
import json
import time

class NetClient(object):
	def __init__(self):
		self.login=False
		#是否开启了接受线程
		self.Recv=False
		#self.mutex = threading.Lock()
		self.client=[]
		self.port=-1
		self.host=""
		#主线程进入控制台
		self.sendCharts()
		#尝试连接服务器
		#self.loginServer(False,False,True,False)
		#开启获取聊天信息的线程循环，并且主线程进入等待输入命令主循环
		#self.start()
		#退出应用
		#print("正在从服务器注销。。。")
		#self.loginServer(False,False,False,True)
	def start(self):
		#开启接受进程
		recv_th=threading.Thread(target = self.recvCharts)
		recv_th.start()
		#开启发送进程
		#self.sendCharts()
	#进入接受chart子线程
	def recvCharts(self):
		if self.port==-1:
				return None;
		#需要过滤掉不在连接里的消息，并且每失败一次就更新一次client列表
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind((self.host, self.port))		# 接受port为发送注册请求的port
		sock.settimeout(5)		  # Set timeout period
		while self.login:
			self.Recv=True
			#print("Recive charts: in [%s:%d]"%(self.host,self.port))
			try:
				revcData, (remoteHost, remotePort) = sock.recvfrom(1024)
			except socket.timeout:
				continue
			'''#ack Data format:{Name,Chart,Data}
			print("[%s:%s] connect" % (remoteHost, remotePort))		# 接收客户端的ip, port
			localtime = time.asctime( time.localtime(time.time()) )
			sendData={"Error":0,"Chart":"Reccieved!","Data":{"Name":self.name,"Time":localtime}}
			sendData=json.dumps(sendData).encode()
			sendDataLen = sock.sendto(sendData, (remoteHost, remotePort))
			#print("revcData: ", revcData)
			#print("sendDataLen: ", sendDataLen)
			#chart Data format:{Error,Chart,Data}
			'''
			recvData=json.loads(revcData.decode())
			if(recvData["Error"]==0):
				name=recvData["Data"]["Name"]
				chart=recvData["Chart"]
				times=recvData["Data"]["Time"]
				self.showChart(name,remoteHost,remotePort,times,chart)
			else:
				print("Error:%s"%(recvData["Data"]))
				if(recvData["Error"]==-2):
					print("Error: 重复登陆，请退出！")
					self.name=""
					self.pwd=""
					self.login=False
					self.port=-1
					break;
		self.Recv=False
		sock.close()
	#输入控制命令
	#Quit：退出
	#Update： 重新获取联系人列表
	#Login：登陆
	#logout: 登出
	#Register: 注册
	#UpdatePwd: 更新密码
	#进入发送chart主线程
	def sendCharts(self):
		#发送socket
		help='''
		Commend List: 
		#Quit：退出
		#Update： 重新获取联系人列表
		#Login：登陆
		#logout: 登出
		#Register: 注册
		#UpdatePwd: 更新密码
		#Name: 获取当前用户名 
		#\">\" to set dstination user, using \"space\" split.
		'''
		print(help)
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		while(True):
			inp=input(">>")
			if(inp=="Quit"):
				if(not self.login):
					return False
				self.logout()
				return False
			if(inp=="Update"):
				if(not self.login):
					print("未登陆用户，请先登陆！")
					continue
				self.updateClientList()
				continue
			if(inp=="Login"):
				if(self.login or self.Recv):
					print("你已登陆用户名%s的账户，请先注销该登陆！"%(self.name))
					continue
				name=input("用户名：")
				pwd=input("密码：")
				if(self.login_(name,pwd)):
					#开启收消息线程
					self.start()
				continue
			if(inp=="Logout"):
				if(not self.login):
					print("未登陆用户，请先登陆！")
					continue
				if(self.logout()):
					print("用户%s已注销登陆"%(self.name))
				else:
					print("用户%s注销失败"%(self.name))
				continue
			if(inp=="Register"):
				if(self.login or self.Recv):
					print("你已登陆用户名%s的账户，请先注销该登陆！"%(self.name))
					continue
				name=input("用户名：")
				pwd=input("密码：")
				self.register(name,pwd)
				continue
			if(inp=="UpdatePwd"):
				if(not self.login):
					print("未登陆用户，请先登陆！")
					continue
				pwd=input("新的密码：")
				self.updatePwd(pwd)
				continue
			if(inp=="Name"):
				if(not self.login):
					print("未登陆用户，请先登陆！")
				else:
					print("Your Name is: ", self.name)
				continue
			if(not self.login):
				print("未登陆用户，请先登陆！")
				print(help)
			inp=inp.split(">")
			chart=inp[0]
			if(len(inp)<2):
				print("Input Error: please select one user to send using \">\" after your charts!")
				continue
			dstname=inp[1].split()
			localtime = time.asctime( time.localtime(time.time()) )
			sendData={"Error":0,"Chart":chart,"Data":{"Name":self.name,"Time":localtime}}
			sendData=json.dumps(sendData).encode()
			for dst in dstname:
				if(not dst in self.client.keys()):
					print("Error: no user name is %s"%(dst))
					continue
				host=self.client[dst]["Host"]
				port=self.client[dst]["Port"]
				print("Send to [%s:%d]"%(host,port))
				sock.sendto(sendData, (host, port))
				#sock.recv(1024)
		sock.close()
	def exit():
		sys.exit() 
	def showChart(self,name,host,port,time,chart):
		print("From: %s [%s:%d] at %s"%(name,host,port,time))
		print("Chart: %s"%(chart))
	def updateClientList(self):
		return self.loginServer(False,False,False,False,True)
	def register(self,name,pwd):
		self.name=name
		self.pwd=pwd
		return self.loginServer(True,False,False,False,False)
	def updatePwd(self,pwd):
		self.pwd=pwd
		return self.loginServer(False,True,False,False,False)
	def login_(self,name,pwd):
		self.name=name
		self.pwd=pwd
		return self.loginServer(False,False,True,False,False)
	def logout(self):
		if(self.loginServer(False,False,False,True,False)):
			self.name=""
			self.pwd=""
			return True
		return False
	def loginServer(self,register=False,updatepwd=False,login=True,logout=False,update=False):
		clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		clientSock.connect(('localhost', 9527))
		clientSock.settimeout(5)
		localtime = time.asctime( time.localtime(time.time()) )
		sendData={"Name":self.name,"Pwd":self.pwd,"Operator":{"Register":register,"UpdatePwd":updatepwd,"Login":login,"Logout":logout,"Update":update},"Data":{"Time":localtime}}
		#print(sendData)
		sendData=json.dumps(sendData).encode()
		sendDataLen = clientSock.send(sendData)
		temp = clientSock.recv(4096)
		recvData = b""
		while temp:
			recvData+=temp
			temp = clientSock.recv(4096)
		recvData=recvData.decode("utf8","ignore")
		recvData=json.loads(recvData)
		if(not recvData["Error"]==0):
			print("Error: %s"%(recvData["Data"]))
			clientSock.close()
			return False
		if(register or updatepwd):
			print("==========%s=========="%(recvData["Data"]))
			clientSock.close()
			return True
		#print("sendDataLen: ", sendDataLen)
		print("Client List: ", recvData["Data"].keys())
		print("Your Name is: ", self.name)
		self.client=recvData["Data"]
		if(login):
			print("==========Login Success!==========")
			self.login=True
			clientSock.close()
			self.port=self.client[self.name]["Port"]
			self.host=self.client[self.name]["Host"]
			return True
		elif(logout):
			print("==========Logout Success!==========")
			self.login=False
			clientSock.close()
			self.port=-1
			return True
		elif(update):
			print("==========Update Success!==========")
			#self.login=True
			clientSock.close()
			#self.port=self.client[self.name]["Port"]
			#self.host=self.client[self.name]["Host"]
			return True
		return False
		
if __name__ == "__main__":
	netClient = NetClient()
	#netClient.loginServer("GongCheng")
	#netClient.loginServer("FengJIaQi",True,False)
	#netClient.loginServer("GongCheng",False,True)
