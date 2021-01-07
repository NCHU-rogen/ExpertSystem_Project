#!/bin/usr/python3
# Coding: utf-8
# Author: Rogen
# Description: 植株灌溉紀錄


from tkinter import ttk, messagebox
from GUI_language import *
import subprocess
import csv, os
import pandas as pd
import tkinter as tk


class Water_management(object):
	def __init__(self,ver,code):
		self.language = ver
		self.internal_code = code
		self.NodeAnswer = 'NodeAnswer.exe'
		self.SaveCSV = './Dataset/Planting_Water.csv'

		if self.language == 1:
			ch = Chinese()
			self.interface = ch.Plating_Management()
		else:
			en = English()
			self.interface = en.Plating_Management()


	# 灌溉紀錄儲存
	def submit(self):
		situation = self.check()
		tag = 0
		
		if situation == 1:
			mylist = []
			# Add tea site in the name
			tag = 1 if os.path.exists(self.SaveCSV) else 0

			with open(self.SaveCSV, 'a', encoding='utf_8_sig') as f:
				if tag == 0:
					f.write('Internal_Code,Sprinkler_Density_W,Sprinkler_Density_H,Frequence,Amount,Electric_Bill_Year,Water_Bill_Year,Water_Bill_Degreed\n')
				mylist.append(self.internal_code)

				for z in range(7):
					mylist.append(self.water_info[z].get())
				f.write(','.join(mylist)+'\n')
			mylist.clear()

			self.hidden_node_answer()
			self.pw_delete_window()


	# 確認表格是否有填寫
	def check(self):
		self.validation_box.delete(1.0,tk.END)
		empty = []; situation = 1
		for i in range(len(self.water_info)):
			if self.water_info[i].get() == '':
				if i == 0 or i == 1:
					empty.append(self.interface['water']['sprinkler_density'])
				elif i == 2:
					empty.append(self.interface['water']['frequence'])
				'''	
				# 以下不強制要求使用者輸入
				elif i == 3:
					empty.append(self.interface['water']['amount'])
				elif i == 4:
					empty.append(self.interface['water']['electric_bill_year'])
				elif i == 5:
					empty.append(self.interface['water']['bill_year'])
				elif i == 6:
					empty.append(self.interface['water']['bill_degree'])
				'''
		if len(empty):
			situation = 0
			for e in empty:
				if self.language == 1:
					self.validation_box.insert(1.0,'%s 未填寫...\n' % e)
				elif self.language == 2:
					self.validation_box.insert(1.0,'%s is empty...\n' % e.replace('\n',''))

		return(situation)


	# 視窗關閉返回主選單
	def pw_delete_window(self):
		from Option_List import optionlist
		self.water.destroy()
		manu = optionlist(self.language)
		manu.main()


	# 呼叫"NodeAnswer.exe"程式 (利用灌溉紀錄來回答專家系統問題)
	def hidden_node_answer(self):
		p = subprocess.run(self.NodeAnswer, shell=True)


	# 茶園灌溉紀錄修改
	def watering_edit(self):
		x = 1		# Escape the colunm of Internal_Code

		if os.path.exists(self.SaveCSV):
			pw_df = pd.read_csv(self.SaveCSV,encoding='utf_8_sig',delimiter=',')
			try:
				index = pw_df.index[pw_df['Internal_Code'] == self.internal_code].tolist()[-1]
				for ob in self.water_info:
					if str(pw_df.iloc[index,x]) == 'nan':
						pw_df.iloc[index,x] = ''
					ob.set(pw_df.iloc[index,x])
					x = x+1
			except IndexError as e:
				tk.messagebox.showerror('ERROR','You do not recode any infomation!')
		else:
			tk.messagebox.showerror('ERROR','You do not recode any infomation!')


	# 主程式介面
	def main(self):
		self.water = tk.Tk()
		self.water.geometry('620x415')
		self.water.resizable(width=False,height=False)
		self.water.title(self.interface['water']['title'])
		self.water.protocol("WM_DELETE_WINDOW",self.pw_delete_window)

		sprinkler_density_width = tk.StringVar()
		sprinkler_density_heigh = tk.StringVar()
		watering_frequence = tk.StringVar()
		watering_volume = tk.StringVar()
		electric_bill_year  = tk.StringVar()
		water_bill_year = tk.StringVar()
		water_bill = tk.StringVar()

		self.water_info = [sprinkler_density_width,sprinkler_density_heigh,watering_frequence,watering_volume,electric_bill_year,water_bill_year,water_bill]
		self.watering_list = ['3-5天一次','每周一次','每旬一次','每兩週一次','每月一次','表土乾即灌溉']

		water_frame = tk.Frame(self.water,highlightbackground='blue',highlightcolor='black',highlightthickness=1,bd=5)
		water_frame.place(x=10,y=20,width=600,height=100)
		tk.Label(water_frame,text=self.interface['water']['sprinkler_density']).grid(row=0,column=0)
		tk.Label(water_frame,text=self.interface['water']['frequence']).grid(row=0,column=1)
		tk.Label(water_frame,text=self.interface['water']['amount']).grid(row=0,column=2)
		tk.Label(water_frame,text=self.interface['water']['electric_bill_year']).grid(row=0,column=3)
		tk.Label(water_frame,text=self.interface['water']['bill_year']).grid(row=0,column=4)
		tk.Label(water_frame,text=self.interface['water']['bill_degree']).grid(row=0,column=5)

		sprinkler_frame = tk.Frame(water_frame)
		sprinkler_frame.grid(row=1,column=0,padx=3,pady=5)

		for k in range(7):
			if k == 0:
				tk.Entry(sprinkler_frame,textvariable=self.water_info[k],width=4).grid(row=0,column=k,padx=2,pady=5)
				tk.Label(sprinkler_frame,text='mx').grid(row=0,column=k+1,padx=2,pady=5)
			elif k == 1:
				tk.Entry(sprinkler_frame,textvariable=self.water_info[k],width=4).grid(row=0,column=k+2,padx=2,pady=5)
				tk.Label(sprinkler_frame,text='m').grid(row=0,column=k+3,padx=2,pady=5)
			elif k == 2:
				watering_combox = ttk.Combobox(water_frame,textvariable=self.water_info[k],values=self.watering_list,width=11,state='readonly')
				watering_combox.grid(row=1,column=k-1,padx=2,pady=5)
			else:
				tk.Entry(water_frame,textvariable=self.water_info[k],width=11).grid(row=1,column=k-1,padx=2,pady=5)

		tk.Button(self.water,text=self.interface['button']['button']['submit'],width=7,command=self.submit).place(x=530,y=140)
		tk.Button(self.water,text='Edit',width=7,command=self.watering_edit).place(x=450,y=140)

		self.validation_box = tk.Text(self.water, bg='lightgray', width=85, height=10)
		self.validation_box.place(x=10,y=190)

		self.water.mainloop()


# if __name__ == '__main__':
# 	w = Water_management(1,'000-0001')
# 	w.main()
