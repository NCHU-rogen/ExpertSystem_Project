#!usr/bin/python3
# Coding: utf-8
# Author: Rogen
# Description: 土壤感應器速測紀錄


from tkinter import messagebox
from GUI_language import *
import tkinter as tk
import csv, re, os
import subprocess
import pandas as pd


class QuickTest(object):
	def __init__(self, ver, code):
		super(QuickTest, self).__init__()
		self.object_vehical = {}
		self.language = ver
		self.internal_code = code
		self.NodeAnswer = 'NodeAnswer.exe'
		self.SaveCSV = './Dataset/Soils_Test.csv'
		self.title_list = {'T_Texture':'T','B_Texture':'B','T_BD_min':'表土BD','T_BD_max':'表土BD','B_BD_min':'底土BD','B_BD_max':'底土BD',
							'SDepth_min':'土壤深度','SDepth_max':'土壤深度','CDepth_min':'壓實深度','CDepth_max':'壓實深度','MDepth_min':'鏽斑深度','MDepth_max':'鏽斑深度',
							'pH_min':'pH','pH_max':'pH','EC_min':'EC','EC_max':'EC','OM_min':'OM','OM_max':'OM','NO3_min':'NO3','NO3_max':'NO3',
							'PO4_min':'PO4','PO4_max':'PO4','K_min':'K','K_max':'K','Ca_min':'Ca','Ca_max':'Ca'}

		if self.language == 1:
			ch = Chinese()
			self.interface = ch.Plating_Management()
		else:
			en = English()
			self.interface = en.Plating_Management()


	# 速測紀錄儲存
	def submit(self):
		tag = self.checkempty()
		if tag == 0:
			tk.messagebox.showerror('ERROR','Please input values!')
		else:
			content = []
			title_tag = 1 if os.path.exists(self.SaveCSV) else 0
			with open(self.SaveCSV, 'a', encoding='utf_8_sig', newline='') as f:
				title = ['T_Texture','B_Texture','T_BD_min','T_BD_max','B_BD_min','B_BD_max','SDepth_min','SDepth_max','CDepth_min','CDepth_max','MDepth_min','MDepth_max',
						'pH_min','pH_max','EC_min','EC_max','OM_min','OM_max','NO3_min','NO3_max','PO4_min','PO4_max','K_min','K_max','Ca_min','Ca_max']
				
				content.append(self.internal_code)

				for t in title:
					if re.search('max',t):
						flag = 1
					else:
						flag = 0
					value = self.object_vehical[self.title_list[t]][flag].get()
					value = 0 if value == '' else value
					content.append(value)

				writer = csv.writer(f, quoting=csv.QUOTE_NONE)
				if title_tag == 0:
					writer.writerow(['Internal_Code']+title)
				writer.writerow(content)

			self.hidden_node_answer()
			self.qt_delete_window()


	# 呼叫"NodeAnswer.exe"程式 (利用土壤速測紀錄來回答專家系統問題)
	def hidden_node_answer(self):
		p = subprocess.run(self.NodeAnswer, shell=True)


	# 檢查欄位空值
	def checkempty(self):
		tag = 0
		for val in self.object_vehical.values():
			for element in val:
				if element.get() != '' and element.get() != 'None':
					tag = 1
		return(tag)


	# 所有欄位清空
	def reset(self):
		for key in self.object_vehical.keys():
			clear = None if re.match(r'[T|B]',key) else ''
			for ob in self.object_vehical[key]:
				ob.set(clear)


	# 視窗關閉返回主選單
	def qt_delete_window(self):
		from Option_List import optionlist
		self.qt_win.destroy()
		manu = optionlist(self.language)
		manu.main()


	# 當min欄位輸入值時，max欄位被激活
	def bindkey(self, event, entry):
		if event.keysym == "BackSpace" and event.widget.get() == '':
			entry.config(state=tk.DISABLED)
		else:
			entry.config(state=tk.NORMAL)


	# 速測紀錄修改
	def quicktest_edit(self):
		if os.path.exists(self.SaveCSV):
			qt_df = pd.read_csv(self.SaveCSV,encoding='utf_8_sig',delimiter=',')
			title = qt_df.columns.tolist()

			try:
				index = qt_df.index[qt_df['Internal_Code'] == self.internal_code].tolist()[-1]
				for t in title[1:]:		# Remove internal_code
					key = self.title_list[t]
					flag = 1 if re.search('max',t) else 0
					ob = self.object_vehical[key][flag]
					ob.set(qt_df[t].tolist()[index])
			except IndexError as e:
				tk.messagebox.showerror('ERROR','You do not recode any infomation!')
		else:
			tk.messagebox.showerror('ERROR','You do not recode any infomation!')


	# 主程式介面
	def main(self):
		self.qt_win = tk.Tk()
		self.qt_win.geometry('550x370')
		self.qt_win.resizable(width=False, height=False)
		self.qt_win.title(self.interface['quicktest']['title'])
		self.qt_win.protocol("WM_DELETE_WINDOW",self.qt_delete_window)

		# Parameter of tkinter
		grid_padx = 2
		grid_pady = 2
		frame_bd = 2
		frame_padx = 3
		frame_pady = 3
		counter = 0
		counter4chemistry = 0
		counter4soildepth = 0
		counter4soiltexture = 0

		# Design a framework of detected values of soils chemistry
		chemistry_list = ['pH','EC','OM','NO3','PO4','K','Ca']
		chemistry_lf = tk.LabelFrame(self.qt_win,bd=frame_bd,relief='groove',padx=frame_padx,pady=frame_pady)
		chemistry_lf.place(x=10,y=20,width=520)

		for i in chemistry_list:
			locals()['%s_Min' % i] = tk.StringVar()
			locals()['%s_Max' % i] = tk.StringVar()
			tk.Label(chemistry_lf, text=i).grid(row=0,column=counter4chemistry+1,padx=grid_padx,pady=grid_pady)
			chemistry_min_entry = tk.Entry(chemistry_lf, textvariable=locals()['%s_Min' % i], width=7)
			chemistry_min_entry.grid(row=1,column=counter4chemistry+1,padx=grid_padx,pady=grid_pady)
			chemistry_max_entry = tk.Entry(chemistry_lf, textvariable=locals()['%s_Max' % i], width=7, state=tk.DISABLED)
			chemistry_max_entry.grid(row=2,column=counter4chemistry+1,padx=grid_padx,pady=grid_pady)

			chemistry_min_entry.bind("<KeyRelease>",lambda event, x=chemistry_max_entry: self.bindkey(event,x))
			counter4chemistry = counter4chemistry+1

			# Storage the variable of chemistry's table into the dictionary
			self.object_vehical[i] = [locals()['%s_Min' % i],locals()['%s_Max' % i]]

		tk.Label(chemistry_lf, text='Min').grid(row=1,column=0,padx=grid_padx,pady=grid_pady)
		tk.Label(chemistry_lf, text='Max').grid(row=2,column=0,padx=grid_padx,pady=grid_pady)


		# Design a framework of derected values of soils physiology
		physiology_list = [self.interface['quicktest']['soils'],
							self.interface['quicktest']['compact'],
							self.interface['quicktest']['rust'],
							self.interface['quicktest']['top_BD'],
							self.interface['quicktest']['bottom_BD']]

		physiology_lf = tk.LabelFrame(self.qt_win,bd=frame_bd,relief='groove',padx=frame_padx,pady=frame_pady)
		soildepth_lf = tk.LabelFrame(physiology_lf,bd=0)
		soiltexture_lf = tk.LabelFrame(physiology_lf,bd=0)
		physiology_lf.place(x=10,y=120,width=520)
		soildepth_lf.grid(row=0,column=0)
		soiltexture_lf.grid(row=0,column=1,padx=15)

		# Design a framework of soils depth
		for j in physiology_list:
			tk.Label(soildepth_lf, text=j).grid(row=0,column=counter4soildepth+1,padx=grid_padx,pady=grid_pady)

			j = j.replace('\n','')
			locals()['%s_Min' % j] = tk.StringVar()
			locals()['%s_Max' % j] = tk.StringVar()

			physiology_min_entry = tk.Entry(soildepth_lf, textvariable=locals()['%s_Min' % j], width=7)
			physiology_min_entry.grid(row=1,column=counter4soildepth+1,padx=grid_padx,pady=grid_pady)
			physiology_max_entry = tk.Entry(soildepth_lf, textvariable=locals()['%s_Max' % j], width=7, state=tk.DISABLED)
			physiology_max_entry.grid(row=2,column=counter4soildepth+1,padx=grid_padx,pady=grid_pady)

			physiology_min_entry.bind("<KeyRelease>",lambda event, x=physiology_max_entry: self.bindkey(event,x))
			counter4soildepth = counter4soildepth+1

			# Storage the variable of physiology's table into the dictionary
			self.object_vehical[j] = [locals()['%s_Min' % j],locals()['%s_Max' % j]]

		tk.Label(soildepth_lf, text='Min').grid(row=1,column=0,padx=grid_padx,pady=grid_pady)
		tk.Label(soildepth_lf, text='Max').grid(row=2,column=0,padx=grid_padx,pady=grid_pady)

		# Design a framework of soils depth
		soildepth_list = [self.interface['quicktest']['texture'],
							self.interface['quicktest']['top_soils'],
							self.interface['quicktest']['buttom_soils']]

		soiltexture_list = [self.interface['quicktest']['gravel'],self.interface['quicktest']['sand'],
							self.interface['quicktest']['loam'],self.interface['quicktest']['clay']]

		topsoils = tk.StringVar()
		bottomsoils = tk.StringVar()
		topsoils.set(None)
		bottomsoils.set(None)

		for k in soildepth_list:
			tk.Label(soiltexture_lf,text=k).grid(row=counter,column=0,padx=1,pady=1)
			counter = counter+1

		for l in range(4):
			tk.Label(soiltexture_lf,text=soiltexture_list[l]).grid(row=0,column=counter4soiltexture+1,padx=1,pady=1)
			r1 = tk.Radiobutton(soiltexture_lf,variable=topsoils,value=l).grid(row=1,column=counter4soiltexture+1,padx=1,pady=1)
			if l != 0:
				r2 = tk.Radiobutton(soiltexture_lf,variable=bottomsoils,value=l).grid(row=2,column=counter4soiltexture+1,padx=1,pady=1)
			counter4soiltexture = counter4soiltexture+1

		self.object_vehical['T'] = [topsoils]
		self.object_vehical['B'] = [bottomsoils]

		tk.Button(self.qt_win,text=self.interface['quicktest']['edit'],width=7,command=self.quicktest_edit).place(x=310,y=250)
		tk.Button(self.qt_win,text=self.interface['quicktest']['reset'],width=7,command=self.reset).place(x=380,y=250)
		tk.Button(self.qt_win,text=self.interface['quicktest']['submit'],width=7,command=self.submit).place(x=450,y=250)

		self.qt_win.mainloop()


# if __name__ == '__main__':
# 	QuickTest(2,'001-0002').main()


