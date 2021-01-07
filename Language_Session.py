#!usr/bin/python3
# Coding: utf-8
# Author: Rogen
# Description: 語言選擇控制介面


from tkinter import messagebox
import tkinter as tk
import SiteEva_login as sl
import os, sys
import subprocess
import psutil


class Language_Session(object):
	#中文按鈕功能
	def press_ch(self):
		self.main_windows.destroy()
		Login = sl.SiteEvaLogin(1)
		Login.main()

	#英文按鈕功能
	def press_en(self):
		self.main_windows.destroy()
		Login = sl.SiteEvaLogin(2)
		Login.main()


	#主程式介面
	def main(self):
		self.main_windows = tk.Tk()
		self.main_windows.resizable(width=False, height=False)
		self.main_windows.title("Expert System of Tea Soil-Problem Diagnosis")
		self.main_windows.geometry('460x400')
		tk.Label(master=self.main_windows, text='請選擇系統介面呈現語言：', font=('Arial',14)).place(x=70,y=50)
		tk.Label(master=self.main_windows, text='Copyright © 2020 NCHU', font=('Arial',10)).place(x=300,y=370)
		button_ch = tk.Button(master=self.main_windows, text='English', height=3, width=40, font=('Arial',12), command=self.press_en).place(x=50,y=100)
		button_en = tk.Button(master=self.main_windows, text='繁體中文', height=3, width=40, font=('Arial',12), command=self.press_ch).place(x=50,y=200)
		self.main_windows.mainloop()


if __name__ == '__main__':
	Language_Session().main()
