#!/usr/bin/python3
# Coding: utf-8
# Author: Rogen
# Description: 主選單功能介面


from Planting_water import Water_management
from Planting_fertilizer import Fertilizer_management
from Quick_Test import QuickTest
from ExpertSystem_Functions import ExpertSystemFunctions as esf
from tkinter import messagebox
from os import walk
from GUI_language import *
import tkinter as tk
import ExpertSystem_GUI as es
import SiteEva_login as sl
import os, subprocess, sys


class optionlist(object):
	def __init__(self, ver):
		self.sheet = 'SiteEvaluation'
		self.language = ver
		self.photo_temp = './Photo/TempFile'
		self.internal_code = self.initiated_setting()
		self.report_flag = 0

		# 介面語言選擇
		if self.language == 1:
			ch = Chinese()
			self.interface = ch.option_panel()
		else:
			en = English()
			self.interface = en.option_panel()


	# 讀取CropVISTMapInfo.txt檔案
	def initiated_setting(self):
		if os.path.exists('CropVISTMapInfo.txt'):
			with open('CropVISTMapInfo.txt','r',encoding='utf-8') as o:
				lines = o.readlines()
				sp_lines = lines[-1].split(' = ')
				internal_code = sp_lines[1].replace('\n','')
				return(internal_code)
		else:
			messagebox.showinfo('INFO','Please choose a tea field first!')
			sys.exit()


	# 啟動專家系統
	def expertsystem(self):
		self.option.destroy()
		ES_GUI = es.ExpertSystemInterface(self.language, self.sheet, self.internal_code)
		ES_GUI.gui()


	#開立診斷報告書
	def report(self):
		p = subprocess.call('ReportMaker.exe', shell=True)
		self.report_flag = 1


	# 執行土壤感應器速測
	def quicktest(self):
		self.option.destroy()
		qt = QuickTest(self.language, self.internal_code)
		qt.main()


	# 執行灌溉紀錄
	def waterusage(self):
		self.option.destroy()
		wm = Water_management(self.language, self.internal_code)
		wm.main()


	# 執行施肥紀錄
	def fertilizerusage(self):
		self.option.destroy()
		fm = Fertilizer_management(self.language, self.internal_code)
		fm.main()


	# 執行茶園座標定點校正
	def coordinate_adjust(self):
		p = subprocess.run('CropPlantationLocation.exe', shell=True)


	# 返回茶園登入
	def back(self):
		self.option.destroy()
		with open('TeaRegionLoading.txt','r',encoding='utf-8') as r:
			lines = r.readlines()

		login = sl.SiteEvaLogin(self.language)
		login.main(update={'country':lines[0].split(' = ')[1].replace('\n',''),'region':lines[1].split(' = ')[1]})


	# 視窗關閉返回主選單
	def wm_delete_window(self):
		if self.report_flag == 0:
			Msgbox = messagebox.askyesno('WARNING','You do not execeed ReportMaker function!!\nDo you sure to exit?',icon = 'warning')
		else:
			Msgbox = True

		if Msgbox:
			ESF = esf(self.language, self.sheet, self.internal_code).GuiClose()
			for file in ['TeaRegionLoading.txt','CropVISTMapInfo.txt','SuppliedInfo.txt']:
				if os.path.exists(file):
					os.remove(file)
			self.option.destroy()
		else:
			pass


	# 主程式介面
	def main(self):
		self.option = tk.Tk()
		self.option.resizable(width=False,height=False)
		self.option.title(self.interface['option']['title'])
		self.option.geometry('250x270')
		self.option.protocol('WM_DELETE_WINDOW',self.wm_delete_window)

		frame = tk.LabelFrame(self.option,text=self.interface['option']['main_function'],fg='blue')
		frame.place(x=10,y=150,width=230,height=70)

		es_button = tk.Button(frame,text=self.interface['option']['expert_system'],width=12,command=self.expertsystem).grid(row=0,column=0,padx=10,pady=10)
		report_button = tk.Button(frame,text=self.interface['option']['report_output'],width=12,command=self.report).grid(row=0,column=1,padx=10,pady=10)

		frame = tk.LabelFrame(self.option,text=self.interface['option']['database'],fg='blue')
		frame.place(x=10,y=5,width=230,height=130)

		coordinate_adjust_button = tk.Button(frame,text=self.interface['option']['coordinate'],width=12,command=self.coordinate_adjust).grid(row=0,column=0,padx=10,pady=10,sticky=tk.W)
		water_button = tk.Button(frame,text=self.interface['option']['water_usage'],width=12,command=self.waterusage).grid(row=1,column=1,padx=10,pady=10,sticky=tk.W)
		fertilizer_button = tk.Button(frame,text=self.interface['option']['fert_usage'],width=12,command=self.fertilizerusage).grid(row=0,column=1,padx=10,pady=10,sticky=tk.W)
		quicktest_button = tk.Button(frame,text=self.interface['option']['quick_test'],width=12,command=self.quicktest).grid(row=1,column=0,padx=10,pady=10,sticky=tk.W)

		back_button = tk.Button(self.option,text=self.interface['option']['back'],width=12,command=self.back).place(x=75,y=230)
		
		self.option.mainloop()


# if __name__ == '__main__':
# 	a = optionlist(1).main()