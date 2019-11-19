# coding: utf-8
'''
实现简易的Web浏览器程序
1.基于HTTP 1.1规范完成，不可用现成的浏览器软件及API,实现图形用户界面
2.可输入HTTP命令（GET与HEAD）与URL地址，输出返回的HHTP响应与HTML文档，解析并显示与文本相关的标记
3.在Windows平台上实现；.提交内容：程序源码、可执行文件与说明文档,编程语言不限制
'''
import _tkinter
import tkinter as Tkinter
from tkinter import filedialog
import tkinter.messagebox
import threading
import time
import client
import os
import sys
import socket
import json

DEBUG = False
l1 = []
class TkGUI:
	def __init__(self, root):
		self.root = root
		root.title("GongCheng-2120160392")
		self.__gui_init()
		self.chart_init()
		#self.__pcap_init()
		self.offlinestate()

	def __gui_init(self):
		self.root.geometry('1200x800')
		#创建OutputFrame
		self.outputFrame=Tkinter.LabelFrame(self.root,text="Output",padx=10,pady=1)
		self.outputFrame.place(x=20,y=10)
		#chart
		self.label_charts = Tkinter.Label(self.outputFrame, text="Charts Window")
		self.label_charts.grid(row=0, column=2, sticky=Tkinter.E)
		self.chartsPanel = Tkinter.Text(self.outputFrame, height=30, width=116) 
		self.chartsPanel.grid(row=1, column=0,columnspan=3, rowspan=5)
		self.chartsS=Tkinter.Scrollbar(self.root)
		self.chartsS.pack(side=Tkinter.LEFT, fill=Tkinter.Y)
		self.chartsS.config(command=self.chartsPanel.yview)
		self.chartsPanel.config(yscrollcommand=self.chartsS.set)
		#client list
		self.label_client = Tkinter.Label(self.outputFrame, text="Client List")
		self.label_client.grid(row=0, column=3, sticky=Tkinter.E)
		self.clientPanel = Tkinter.Listbox(self.outputFrame, height=22, width=45) 
		self.clientPanel.grid(row=1, column=3,columnspan=1,rowspan=5)
		self.clientS=Tkinter.Scrollbar(self.root)
		self.clientS.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
		self.clientS.config(command=self.clientPanel.yview)
		self.clientPanel.config(yscrollcommand=self.clientS.set)
		header = "%+5s %+15s %+30s" % ("Name","Host:Port", "Time")
		self.clientPanel.insert(Tkinter.END, header)
		#self.clientPanel.insert(Tkinter.END, header)
		#self.clientPanel.insert(Tkinter.END, header)
		#设置listbox绑定的回调函数
		self.clientPanel.bind('<Button-1>',self.setClientSelection)
		#创建inputFrame
		self.inputFrame=Tkinter.LabelFrame(self.root,text="Input",padx=10,pady=10)
		self.inputFrame.place(x=20,y=460)
		#创建输入框
		self.File_input = Tkinter.Entry(self.inputFrame,width=100)
		self.File_input.grid(row=0, column=0,columnspan=30)
		self.file_btn = Tkinter.Button(self.inputFrame, text="选择文件", 
		command=self.file_callback, height=1, width=12)
		self.file_btn.grid(row=0, column=30)
		#url input
		self.label_input = Tkinter.Label(self.inputFrame, text="输入文本框")
		#self.label_time.config(font=('Courier New', '14'))
		self.label_input.grid(row=1, column=29, sticky=Tkinter.E)
		self.Text_input = Tkinter.Text(self.inputFrame,width=100,height=6)
		self.Text_input.grid(row=2, column=0,columnspan=30,rowspan=10)
		#schema default
		#群发用户名设置
		self.label_mass = Tkinter.Label(self.inputFrame, text="群发用户名设置")
		#self.label_time.config(font=('Courier New', '14'))
		self.label_mass.grid(row=1, column=30, sticky=Tkinter.E)
		self.mass_client = Tkinter.Text(self.inputFrame,width=14,height=6)
		self.mass_client.grid(row=2, column=30)
		#self.clear_btn.config(state = "disabled")
		
		#创建controlFrame
		self.controlFrame=Tkinter.LabelFrame(self.root,text="Control",padx=10,pady=6)
		self.controlFrame.place(x=850,y=460)
		
		#登陆
		self.label_name = Tkinter.Label(self.controlFrame, text="Name")
		self.label_name.grid(row=0, column=0, sticky=Tkinter.E)
		self.name_text = Tkinter.Entry(self.controlFrame, width=15) 
		self.name_text.grid(row=0, column=1,columnspan=1)
		self.label_pwd = Tkinter.Label(self.controlFrame, text="Password")
		self.label_pwd.grid(row=1, column=0, sticky=Tkinter.E)
		self.pwd_text = Tkinter.Entry(self.controlFrame, width=15) 
		self.pwd_text.grid(row=1, column=1,columnspan=1)
		self.login_btn = Tkinter.Button(self.controlFrame, text="登陆", 
		command=self.login_callback, height=1, width=12)
		self.login_btn.grid(row=2, column=0)
		self.register_btn = Tkinter.Button(self.controlFrame, text="注册", 
		command=self.register_callback, height=1, width=12)
		self.register_btn.grid(row=2, column=1)
		self.updatepwd_btn = Tkinter.Button(self.controlFrame, text="更改密码", 
		command=self.updatepwd_callback, height=1, width=12)
		self.updatepwd_btn.grid(row=3, column=0)
		self.logout_btn = Tkinter.Button(self.controlFrame, text="退出登陆", 
		command=self.logout_callback, height=1, width=12)
		self.logout_btn.grid(row=3, column=1)
		
		#打开控制台
		self.dos_btn = Tkinter.Button(self.controlFrame, text="打开控制台", 
		command=self.enter_dos, height=1, width=15)
		self.dos_btn.grid(row=0, column=2)
		#刷新客户端列表
		self.update_btn = Tkinter.Button(self.controlFrame, text="刷新客户端列表", 
		command=self.update_callback, height=1, width=15)
		self.update_btn.grid(row=1, column=2)
		#发送
		self.send_btn = Tkinter.Button(self.controlFrame, text="发送", 
		command=self.send_callback, height=1, width=15)
		self.send_btn.grid(row=2, column=2)
		#群发
		self.mass_btn = Tkinter.Button(self.controlFrame, text="群发", 
		command=self.mass_callback, height=1, width=15)
		self.mass_btn.grid(row=3, column=2)
		
	def file_callback(self):
		file_path = filedialog.askopenfilename()
		self.File_input.delete(0,Tkinter.END)
		self.File_input.insert(Tkinter.END,file_path)
		pass
	def chart_init(self):
		self.login=False
		#是否开启了接受线程
		self.Recv=False
		#self.mutex = threading.Lock()
		self.client=[]
		self.port=-1
		self.host=""
		self.chartslist={}#聊天记录，显示当前收到的聊天信息列表，为一个长的数组，可以写入到文本保存
		self.chartslistdocname=""
		self.curid=-1
		#主线程进入控制台
		#self.sendCharts()
	#存取聊天记录，为了方便观察，存为文本文件
	def saveChartsToFile(self):
		if(len(self.chartslist)==0):
			return False
		tmpj=json.dumps(self.chartslist)
		with open(self.chartslistdocname,'w') as f:
			f.write(tmpj)
		return True
	def loadChartsFromFile(self):
		if(not self.chartslistdocname=="" and not os.path.exists(self.chartslistdocname)):
			self.chartslist={}
		else:
			with open(self.chartslistdocname,'r') as f:
				tmpj=f.read()
				try:
					self.chartslist=json.loads(tmpj)
				except Exception as e:
					self.chartslist={}
	def enter_dos(self):
		#self.instance=client.NetClient()
		os.system("start client.exe")
	
	def setClientSelection(self,event):
		id=self.clientPanel.curselection()
		if(len(id)>0):
			self.curid=id[0]
			self.showChart()
	def login_callback(self):
		if(self.login or self.Recv):
			self.errorProcess("你已登陆用户名%s的账户，请先注销该登陆！"%(self.name))
			return None
		#从用户名和密码框获取值
		self.name=self.name_text.get()
		self.pwd=self.pwd_text.get()
		if(len(self.name.split())==0 or len(self.pwd.split())==0):
			self.errorProcess("用户名或密码不能为空")
			return None
		if(self.loginServer(False,False,True,False,False)):
			#开启收消息线程
			recv_th=threading.Thread(target = self.recvCharts)
			recv_th.start()
			#设置聊天记录保存路径，按用户名保存，并读取聊天记录
			if(not os.path.exists("./%s"%(self.name))):
				os.mkdir(self.name)
			self.chartslistdocname="./%s/charts_backup.txt"%(self.name)
			self.loadChartsFromFile()
			self.onlinestate()
		pass
	def logout_callback(self):
		if(not self.login):
			self.errorProcess("未登陆用户，请先登陆！")
			return None
		if(self.loginServer(False,False,False,True,False)):
			self.name=""
			self.pwd=""
			#保存聊天记录
			self.saveChartsToFile()
			self.offlinestate()
			return True
		self.errorProcess("退出失败！")
		return False
		pass
	def register_callback(self):
		if(self.login or self.Recv):
			self.errorProcess("你已登陆用户名%s的账户，请先注销该登陆！"%(self.name))
			return None
		#从用户名和密码框获取值
		self.name=self.name_text.get()
		self.pwd=self.pwd_text.get()
		if(len(self.name.split())==0 or len(self.pwd.split())==0):
			self.errorProcess("用户名或密码不能为空")
			return None
		#print(self.name,self.pwd)
		return self.loginServer(True,False,False,False,False)
		#pass
	def updatepwd_callback(self):
		if(not self.login):
			self.errorProcess("未登陆用户，请先登陆！")
			return None
		#self.name=self.name_text.get()
		self.pwd=self.pwd_text.get()
		if(len(self.pwd.split())==0):
			self.errorProcess("密码不能为空")
			return None
		#print(self.name,self.pwd)
		return self.loginServer(False,True,False,False,False)
		pass
	def update_callback(self):
		#清空统计数据
		if(not self.login):
			self.errorProcess("未登陆用户，请先登陆！")
			return None
		#更新列表
		if(self.loginServer(False,False,False,False,True)):
			self.clientPanel.delete(1, Tkinter.END)
			for index in self.client.keys():
				item=self.client[index]
				tmp="%+5s %+15s %+30s" % (item["Name"],"%s:%d"%(item["Host"],item["Port"]), item["Time"])
				self.clientPanel.insert(Tkinter.END, tmp)
		else:
			self.errorProcess("更新列表失败！")
		pass
		
	def check_ip(self,ip):
		tmp=ip.split('.')
		if(not len(tmp)==4):
			return False
		for i in range(4):
			v=int(tmp[i])
			if(v>255 or v<0):
				return False
		return True
	def send_callback(self,mass=False):
		#
		if(not self.login):
			self.errorProcess("未登陆用户，请先登陆！")
			return None
		#获取聊天信息和选中用户
		dstname=[]
		#如果是群发，则从群发列表中选择用户进行发送
		if(mass):
			clientmass=self.mass_client.get("0.0",Tkinter.END)
			dstname=clientmass.split()
			if(len(dstname)==0):
				self.errorProcess("请输入群发的用户名")
				return None
		else:
			if(self.curid==-1):
				self.errorProcess("请在用户列表中选择一个用户进行聊天！")
				return None
			name=self.clientPanel.get(self.curid).split()[0]
			dstname=[name]
		
		chart=self.Text_input.get('0.0',Tkinter.END)
		filepath=self.File_input.get()
		if(len(chart.split())==0 and len(filepath.split())==0):
			self.errorProcess("不能发送空消息！")
			return None
		#print(chart)
		localtime = time.asctime( time.localtime(time.time()) )
		frominfo="%s [%s:%d] at %s \r\n"%(self.name,self.host,self.port,localtime)
		#path="./GongCheng_charts_backup.txt"
		sendData={"Error":0,"Data":{"Name":self.name,"Time":localtime}}
		if(len(chart.split())>0):
			sendData["Chart"]=chart
			frominfo+="%s\r\n"%chart
		if(len(filepath.split())>0):
			filename=filepath.split("/")[-1]
			if(filename==""):
				self.errorProcess("选择文件格式错误，请重新选择")
				return None
			filecontent=self.get_file(filepath)
			if(not filecontent):
				self.errorProcess("%s文件错误或者不存在!"%filename)
				return None
			sendData["File"]={"Name":filename,"Content":filecontent}
			frominfo+="send file \"%s\" to %s \r\n\r\n"%(filename,str(dstname))
		sendData=json.dumps(sendData).encode()
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		for dst in dstname:
			if(not dst in self.client.keys()):
				self.errorProcess("选中用户[%s]不存在或者并未在线，本软件没有聊天缓存功能，请选择在线用户！"%(dst))
				continue
			host=self.client[dst]["Host"]
			port=self.client[dst]["Port"]
			#print("Send to [%s:%d]"%(host,port))
			sock.sendto(sendData, (host, port))
			#写入发送列表
			if(not dst in self.chartslist.keys()):
				self.chartslist[dst]=[]
			self.chartslist[dst].append(frominfo)
			self.showChart(dst,frominfo)
		self.Text_input.delete('0.0',Tkinter.END)
		sock.close()
		pass
	
	def mass_callback(self):
		self.send_callback(mass=True)
		pass
	 
	def request(self):
		#进入接受chart子线程
		pass
	def save_file(self,filename,filecontent):
		if(self.name==""):
			return None
		with open("./%s/%s"%(self.name,filename),'w') as f:
			f.write(filecontent)
		return True
	def get_file(self,filename):
		if(self.name==""):
			return None
		if(not os.path.exists(filename) or not os.path.isfile(filename)):
			return None
		with open("%s"%(filename),'r') as f:
			filecontent=f.read()
		return filecontent
	def recvCharts(self):
		if self.port==-1:
				return None;
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind((self.host, self.port))		# 接受port为发送注册请求的port
		sock.settimeout(5)		  # Set timeout period
		while self.login:
			self.Recv=True
			revcData=b''
			#print("Recive charts: in [%s:%d]"%(self.host,self.port))
			try:
				revcData, (remoteHost, remotePort) = sock.recvfrom(4096)
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
				times=recvData["Data"]["Time"]
				#将消息写入聊天队列，检测是不是当前选中行，如果是则刷新
				frominfo="%s [%s:%d] at %s \r\n"%(name,remoteHost,remotePort,times)
				if("Chart" in recvData.keys()):
					chart=recvData["Chart"]
					frominfo+="%s\r\n"%(chart)
				if("File" in recvData.keys()):
					files=recvData["File"]
					filename=files["Name"]
					filecontent=files["Content"]
					self.save_file(filename,filecontent)
					frominfo+="save file \"%s\" to \"%s/%s\" \r\n\r\n"%(filename,self.name,filename)
				if(not name in self.chartslist.keys()):
					self.chartslist[name]=[]
				self.chartslist[name].append(frominfo)
				self.showChart(name,frominfo)
				
			else:
				self.errorProcess("Error:%s"%(recvData["Data"]))
				if(recvData["Error"]==-2):
					#退出登陆
					self.errorProcess("Error: 重复登陆，已退出！")
					self.name=""
					self.pwd=""
					self.login=False
					self.port=-1
					self.offlinestate()
					break;
		self.Recv=False
		sock.close()
	#刷新信息显示区域，如果当前选中和name一致且name不为None，则显示
	def showChart(self,name=None,frominfo=""):
		if(self.curid==-1):
			return None
		curclient=self.clientPanel.get(self.curid).split()
		#print(curclient[0])
		if(name==None):
			self.chartsPanel.delete('0.0', Tkinter.END)
			#显示curclient[0]的所有信息
			if(curclient[0] in self.chartslist.keys()):
				infos=self.chartslist[curclient[0]]
				for item in infos:
					self.chartsPanel.insert(Tkinter.END,item)
		elif(curclient[0]==name and not frominfo==""):
			self.chartsPanel.insert(Tkinter.END,frominfo)
		#在聊天窗显示信息列表
		#print("From: %s [%s:%d] at %s"%(name,host,port,time))
		#print("Chart: %s"%(chart))
		pass
	#切换在线状态
	def onlinestate(self):
		#设置按键状态
		self.login_btn.config(state = "disabled")
		self.name_text.config(state = "disabled")
		self.register_btn.config(state = "disabled")
		self.updatepwd_btn.config(state = "normal")
		self.logout_btn.config(state = "normal")
		self.send_btn.config(state = "normal")
		self.mass_btn.config(state = "normal")
		self.update_btn.config(state = "normal")
		#装填在线用户列表
		self.clientPanel.delete(1, Tkinter.END)
		for index in self.client.keys():
			item=self.client[index]
			tmp="%+5s %+15s %+30s" % (item["Name"],"%s:%d"%(item["Host"],item["Port"]), item["Time"])
			self.clientPanel.insert(Tkinter.END, tmp)
		pass
	#切换离线状态
	def offlinestate(self):
		#设置按键状态
		self.login_btn.config(state = "normal")
		self.name_text.config(state = "normal")
		self.register_btn.config(state = "normal")
		self.updatepwd_btn.config(state = "disabled")
		self.logout_btn.config(state = "disabled")
		self.send_btn.config(state = "disabled")
		self.mass_btn.config(state = "disabled")
		self.update_btn.config(state = "disabled")
		#清空在线用户列表
		self.clientPanel.delete(1,Tkinter.END)
		#清空聊天框
		self.chartsPanel.delete('0.0',Tkinter.END)
		pass
	def errorProcess(self,error_str):
		Tkinter.messagebox.showerror(title='Error', message = error_str)
	def infoProcess(self,info_str):
		Tkinter.messagebox.showinfo(title='INOF', message = info_str)
	def setName(self,name):
		return None
	def loginServer(self,register=False,updatepwd=False,login=True,logout=False,update=False):
		clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			clientSock.connect(('localhost', 9527))
		except Exception:
			self.errorProcess("连接超时！请检查网路状态或者服务器状态！")
			return None
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
			self.errorProcess("Error: %s"%(recvData["Data"]))
			clientSock.close()
			return False
		if(register or updatepwd):
			self.infoProcess("==========%s=========="%(recvData["Data"]))
			clientSock.close()
			return True
		#print("sendDataLen: ", sendDataLen)
		#print("Client List: ", recvData["Data"].keys())
		#print("Your Name is: ", self.name)
		self.client=recvData["Data"]
		if(login):
			self.infoProcess("==========Login Success!==========")
			self.login=True
			clientSock.close()
			self.port=self.client[self.name]["Port"]
			self.host=self.client[self.name]["Host"]
			return True
		elif(logout):
			self.infoProcess("==========Logout Success!==========")
			self.login=False
			clientSock.close()
			self.port=-1
			return True
		elif(update):
			#self.infoProcess("==========Update Success!==========")
			#self.login=True
			clientSock.close()
			#self.port=self.client[self.name]["Port"]
			#self.host=self.client[self.name]["Host"]
			return True
		return False
		
def main():
	root = Tkinter.Tk()
	window = TkGUI(root)
	root.mainloop()
	

if __name__=="__main__":
	main()


