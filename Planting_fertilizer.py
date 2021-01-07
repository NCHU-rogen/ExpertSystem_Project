#!/usr/bin/python3
# Coding: utf-8
# Author: Rogen
# Description: 植株施肥紀錄


from tkinter import ttk, messagebox
from PIL import ImageTk, Image
from functools import partial
from GUI_language import *
import pandas as pd
import tkinter as tk
import os, re
import subprocess


# 全域變數宣告 (跨class可共用)
global ShowVehicle, StorageVehicle, CaculateVehicle
ShowVehicle = []
StorageVehicle = []
CaculateVehicle = {}


class AutocompleteCombobox(ttk.Combobox):
	# 初始設定
	def primary_setting(self, completion_list, recepter, ligand=None, df=None, order=None, target_object=None, width=15):
		#---------- Use our completion list as our drop down selection menu, arrows move through menu. ----------#
		self._completion_list = sorted(completion_list, key=str.lower) if order == 1 or order == 2 else completion_list # Work with a sorted list
		self._hits = []
		self._hit_index = 0
		self.position = 0
		self.recepter = recepter								# the object of recepter is stored the value of combobox selected. (ex:登機証字號)
		self.ligand = ligand									# the object of recepter is stored the value of correspond combobox selected. (ex:肥料品名)
		self.df = df											# the dataframe of fertilizer list
		self.order = order										# the sequence of columns in GUI
		self.object = target_object
		self['width'] = width
		self['textvariable'] = self.recepter
		self['values'] = self._completion_list  				# Setup our popup menu
		self.bind('<KeyRelease>', self.handle_keyrelease)
		# self.bind('<KeyPress>', self.handle_keyrelease)
		self.bind('<<ComboboxSelected>>',self.ComboboxSelected)	# For selection
		self.bind('<FocusOut>',self.ComboboxSelected)			# For keyin


	# 欄位輸入關鍵字自動完成
	def autocomplete(self, delta=0):
		#---------- autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits ----------#
		if delta: # need to delete selection otherwise we would fix the current position
				self.delete(self.position, tk.END)
		else: # set position to end so selection starts where textentry ended
				self.position = len(self.get())
		# collect hits
		_hits = []
		for element in self._completion_list:
				if element.lower().startswith(self.get().lower()): # Match case insensitively
						_hits.append(element)
		# if  we have a newhit list, keep this in mind
		if _hits != self._hits:
				self._hit_index = 0
				self._hits=_hits
		# only allow cycling if we are in a known hit list
		if _hits == self._hits and self._hits:
				# print(self._hit_index,len(self._hits))
				self._hit_index = (self._hit_index + delta) % len(self._hits)
		# now finally perform the auto completion
		if self._hits:
				self.delete(0,tk.END)
				self.insert(0,self._hits[self._hit_index])
				self.select_range(self.position,tk.END)


	# 表格關鍵字自動填補控制鍵
	def handle_keyrelease(self, event):
		#---------- event handler for the keyrelease event on this widget ----------#
		# self.flag = 1
		if event.keysym == "BackSpace":
			# self.flag = 0								# When keypress BackSpace, the text autocomplete don't work.
			self.delete(self.index(tk.INSERT), tk.END)
			self.position = self.index(tk.END)
			# self.l = len(event.widget.get())

		if event.keysym == "Left":
			# self.flag = 0								# When keypress BackSpace, the text autocomplete don't work.
			if self.position < self.index(tk.END): 		# delete the selection
					self.delete(self.position, tk.END)
			else:
					self.position = self.position-1 	# delete one character
					self.delete(self.position, tk.END)
			# self.l = len(event.widget.get())

		if event.keysym == "Right":
			self.position = self.index(tk.END) # go to end (no selection)
		

		if event.keysym == 'Return':
			self.autocomplete()

		# No need for up/down, we'll jump to the popup
		# list at the position of the autocompletion


	# 表格選單控制
	def ComboboxSelected(self, event=None):
		def show_ingredient():
			#Retaining the ID, product name and components of fertilizer
			choice_list = self.df.iloc[choice_index,:].tolist()
			choice_list = choice_list[1:2] + choice_list[4:]

			# Showing the current ingredient of fertilizer which is chose
			for i in range(len(choice_list)):
				if str(choice_list[i]) == 'nan':
					choice_list[i] = 0
				ShowVehicle[i].set(choice_list[i])
			
			# Storing the component of fertilizer which is chose in a dictionary
			CaculateVehicle[choice_list[0]] = choice_list[2:]

		if self.ligand != None:
			try:
				if self.order == 1:
					# choice_index = self.df.index[self.df.登記證字號 == event.widget.get()].tolist()[0]
					choice_index = self.df.index[self.df.登記證字號 == self.recepter.get()].tolist()[0]
					self.ligand.set(self.df.廠牌商品名稱[choice_index])
					show_ingredient()

				elif self.order == 2:
					# choice_index = self.df.index[self.df.廠牌商品名稱 == event.widget.get()].tolist()[0]
					choice_index = self.df.index[self.df.廠牌商品名稱 == self.recepter.get()].tolist()[0]
					self.ligand.set(self.df.登記證字號[choice_index])
					show_ingredient()

				elif self.order == 3:
					if not re.match(self.recepter.get(),'葉面施肥'):
						self.ligand.set(self.df[0])
						self.object.configure(state=tk.DISABLED)
					else:
						self.object.configure(state=tk.ACTIVE)

			except IndexError as error:
				# clear the ligand column
				self.ligand.set('')


class Fertilizer_management(object):

	def __init__(self,ver,code):
		self.language = ver
		self.internal_code = code
		self.NodeAnswer = 'NodeAnswer.exe'
		self.fertilizer_fig = './Photo/Fertilizer/'
		self.NoPicture = './Photo/Interface/ProductNotFind.png'
		self.SaveCSV = './Dataset/Planting_Fertilizer_%s.csv' % code
		self.fert_dict = pd.read_excel('CropBasedInfo.xlsx',sheet_name='Fertilizer_items')
		self.row_num = 9
		self.ot_row_num = 5
		self.TEA = []

		if self.language == 1:
			ch = Chinese()
			self.interface = ch.Plating_Management()
		else:
			en = English()
			self.interface = en.Plating_Management()


	# 施肥次數轉數字
	def frequency2numeric(self, row_num, from_database=None):
		freq2num = {'':0,'每年一次':1,'每季一次':4,'雙月一次':6,'每月一次':12,'雙週一次':26,'每週一次':52}
		df = self.fert_value if from_database == True else self.other_fert_value
		frequency = freq2num[df[4][row_num].get()]
		return(frequency)


	# 數字轉施肥次數
	def numeric2frequency(self,num):
		num2freq = {1:'每年一次',4:'每季一次',6:'雙月一次',12:'每月一次',26:'雙週一次',52:'每週一次'}
		freq = num2freq[num]
		return(freq)


	# 施肥紀錄儲存
	def submit(self):
		mylist = []	
		# Plus internal code of site in name
		with open(self.SaveCSV, 'w', encoding='utf_8_sig') as f:
			f.write('Internal_Code,ID,Item,Product,Amount,Aim,Frequency,N,P2O5,K2O,CaO,MgO,OM\n')

			# Recoding the fertilized usage from database obtainedm and appending values into an array by row number
			for x in range(self.row_num):		
				mylist.clear()
				# Check the next value is empty or not
				if self.fert_value[0][x].get() == '':
					continue

				# Trans frequency to numeric
				frequency = self.frequency2numeric(x,True)
				self.fert_value[4][x].set(frequency)

				# Appending values into an array by column number, 
				# the values contained ID, Product, Amount, Aim, Frequency by sequencing.
				for y in range(5):
					mylist.append(self.fert_value[y][x].get())

				# Inserting product's item into array
				item = self.fert_dict.品目[self.fert_dict.登記證字號 == self.fert_value[0][x].get()].tolist()[0]
				mylist.insert(1,item)
				mylist.insert(0,self.internal_code)

				# Appending component of N, P2O5, K2O, CaO, MgO, OM into array
				mylist = mylist+list(map(str,CaculateVehicle[self.fert_value[0][x].get()]))

				f.write(','.join(mylist)+'\n')

			# Recodeing the fertilized usage from user filled and appending values into an array by row number
			for w in range(self.ot_row_num):
				mylist.clear()

				# check the next value is empty or not
				if self.other_fert_value[0][w].get() == '':
					continue

				# Trans frequency to numeric
				frequency = self.frequency2numeric(w,False)
				self.other_fert_value[4][w].set(frequency)

				# Appending values into an array by column number
				for z in range(5):
					mylist.append(self.other_fert_value[z][w].get())

				# Inserting empty product's item into array because the fertiliz don't stroage in database
				mylist.insert(1,'')
				mylist.insert(0,self.internal_code)

				f.write(','.join(mylist)+'\n')

		self.hidden_node_answer()
		self.pf_delete_window()


	# 多種肥料施肥各成分計算
	def calculate(self):
		fer_amount = {}
		total = []
		temp = 0

		# Saving fertilizer amount to dictionary
		for x in range(self.row_num):
			if self.fert_value[0][x].get() == '':
				continue

			frequency = self.frequency2numeric(x,True)
			if self.fert_value[2][x].get() != '' and frequency != 0:
				fer_amount[self.fert_value[0][x].get()] = float(self.fert_value[2][x].get())*frequency

		# Deleting empty keys, and showing warning when value is empty 
		if len(fer_amount) == 0:
			messagebox.showwarning('WARNING','Please input fertilizers!')
			return(0)
		else:
			# Calculating components of each fertilizer multiply by (times) amount of usage
			for key in fer_amount.keys():
				component = CaculateVehicle[key]
				total.append([c*fer_amount[key] for c in component]) 
			
			# Showing the amount of fertitlizer's component
			for c in range(6):					# each component
				for r in range(len(total)):		# kinds of fertilizers application
					temp = temp + total[r][c]
				StorageVehicle[c].set(round(temp/100,2))
				temp = 0
			return(1)


	# 施肥紀錄修改
	def fertitlizer_edit(self):
		lines = -1
		ot_lines = -1
		choice_list = []

		if os.path.exists(self.SaveCSV):
			pf_df = pd.read_csv(self.SaveCSV,encoding='utf_8_sig',delimiter=',')
			pf_df = pf_df.drop(['Internal_Code','Item'], axis=1)

			for r in range(len(pf_df.axes[0])):
				for c in range(len(self.fert_value)):
					if c == 0:
						try:		# The ID have be match of database. 
							choice_index = self.fert_dict.index[self.fert_dict.登記證字號 == pf_df.iloc[r,c]].tolist()[0]
							choice_list = self.fert_dict.iloc[choice_index,:].tolist()
							choice_list = choice_list[1:2] + choice_list[4:]		# Including ID, product's name and chemical compounds

							for z in range(len(choice_list)):
								if str(choice_list[z]) == 'nan':
									choice_list[z] = 0

							# For calculating totally chemical compounds in types of fertilizers
							CaculateVehicle[choice_list[0]] = choice_list[2:]
							# To decide which host can be load
							host = self.fert_value
							# To count which lines the data should be loaded
							lines += 1
							pointer = lines

						except:
							# Manually input ID in list because the data is not in database
							choice_list.append(pf_df.iloc[r,c])
							# To decide which host can be load
							host = self.other_fert_value
							# To count which lines the data should be loaded
							ot_lines += 1
							pointer = ot_lines

						string = choice_list[0]

					elif c == 4:
						string = self.numeric2frequency(int(pf_df.iloc[r,c]))
						
					else:
						string = pf_df.iloc[r,c]

					host[c][pointer].set(string)

		else:
			tk.messagebox.showerror('ERROR','You do not recode any infomation!')


	# 圖片尺寸調整
	def image_resize(self, image):
		w, h = image.size
		f1 = 220/w
		f2 = 220/h
		factor = min([f1, f2])
		width = int(w*factor)
		height = int(h*factor)
		return image.resize((width, height), Image.ANTIALIAS)


	# 肥料登錄檔查詢欄位清除
	def clear(self):
		self.combo_goods.set('')
		self.combo_categorize.set('')
		self.id_search.set('')
		self.pre_button.config(state=tk.DISABLED)
		self.next_button.config(state=tk.DISABLED)
		try:
			self.canvas.itemconfig(self.image_on_canvas, image='')
		except AttributeError as e:
			pass


	# 肥料登錄檔查詢
	def search(self):
		def image_show():
			self.product_figures_counter = 0
			photo_list = os.listdir(self.fertilizer_fig)
			target_list = [_ for _ in photo_list if re.match(self.id_search.get(),_)]
			self.product_figures = [os.path.join(self.fertilizer_fig,_) for _ in target_list]

			if len(self.product_figures):
				fig = Image.open(self.product_figures[0])
			else:
				fig = Image.open(self.NoPicture)

			self.canvas.image = ImageTk.PhotoImage(self.image_resize(fig))
			self.image_on_canvas = self.canvas.create_image(100,110,image=self.canvas.image, anchor=tk.CENTER)

			# When images are shown, the next/back button will be activated
			self.pre_button.config(state=tk.ACTIVE)
			self.next_button.config(state=tk.ACTIVE)

		if self.combo_categorize.get() and self.combo_goods.get():
			# Set id column value
			ID = self.fert_dict.登記證字號[self.fert_dict.廠牌商品名稱 == self.combo_goods.get()].tolist()[0]
			self.id_search.set(ID)
			# Get image from option
			image_show()

		elif self.id_search.get():
			# Get image from option
			image_show()

		else:
			messagebox.showerror('ERROR','No any option is chose!')
			return 0


	# 匯入登錄檔
	def importID(self):
		if self.id_search.get() == '':
			messagebox.showwarning('WARNING','尚未查詢')
		else:
			n = self.fert_value[0]
			for i in range(self.row_num):
				if n[i].get() == '':
					n[i].set(self.id_search.get())
					ID = self.fertilizer[0][i]
					ID.ComboboxSelected()
					break


	# 施肥用量比照
	def review(self):
		def recommend():
			sheet = '公斤_分' if types.get() == '公斤/分' else '每次_分'
			df = pd.read_excel('肥料建議成份.xlsx',sheet_name=sheet)
			df_dict = df.set_index('樹齡').T.to_dict('dict')

			if age_var.get() != 0:
				age = 8 if age_var.get() > 8 else age_var.get()
				p = df_dict[age]
				items = tree.get_children()
				tree.delete(items[-1])
				tree.insert('','end',values=['','','建議用量']+[p['N'],p['P'],p['K']],tags='recommend')
				self.TEA = ['建議用量',p['N'],p['P'],p['K']]
			else:
				messagebox.showerror('ERROR','樹齡不能為0，必須>=1')

		component = []
		res = self.calculate()
		if res:
			rv = tk.Toplevel(self.CM)
			rv.geometry('920x450')

			age_var = tk.IntVar()
			types = tk.StringVar()
			table_types = ['公斤/分','次/分']

			tea_age = tk.LabelFrame(rv,text='茶樹年齡')
			tea_age.place(x=10, y=10, width=350,height=50)

			tk.Label(tea_age,text='請輸入茶樹年齡：').grid(row=0,column=0,padx=2)
			tk.Entry(tea_age,textvariable=age_var,width=10).grid(row=0,column=1,padx=2)
			style = ttk.Style()
			style.configure('TMenubutton', foreground="black", width=7, relief="raised")
			optionmenu = ttk.OptionMenu(tea_age, types, 0, *table_types).grid(row=0,column=2,padx=2)

			tk.Button(tea_age,text='送出',command=recommend).grid(row=0,column=3,padx=2)

			cols = ['c'+str(i) for i in range(1,10)]
			tree = ttk.Treeview(rv, height=15, columns=cols, show="headings")
			for op in cols:
				tree.column(op, width=100, anchor=tk.CENTER)

			tableheads = {'c1':'登入檔','c2':'名稱','c3':'施用量','c4':'N','c5':'P2O5','c6':'K2O','c7':'CaO','c8':'MgO','c9':'OM'}

			for header,name in tableheads.items():
				tree.heading(header, text=name)

			tree.place(x=10,y=100)
			tree.tag_configure('main',background='light gray')
			tree.tag_configure('second',background='white')
			tree.tag_configure('total',background='light sky blue')
			tree.tag_configure('recommend',background='yellow')

			for i in range(self.row_num):
				component = []
				if self.fert_value[0][i].get() != '':
					for j in [0,1,2]:
						component.append(self.fert_value[j][i].get())

					component.extend(list(map(str,CaculateVehicle[self.fert_value[0][i].get()])))
					tag = 'main' if i % 2 == 0 else 'second'
					tree.insert('','end',values=component,tag=tag)
				else:
					break

			tree.insert('','end',values=['']*9)
			tree.insert('','end',values=['','','總量']+[s.get() for s in StorageVehicle],tags='total')
			tree.insert('','end',values=['','','建議用量'],tags='recommend')


	# 上一張肥料袋圖片
	def previous_image_on_canvas(self):
		if self.product_figures_counter > 0:
			self.product_figures_counter -= 1
			self.open_image(self.product_figures[self.product_figures_counter])


	# 下一張肥料袋圖片
	def next_image_on_canvas(self):
		if self.product_figures_counter < len(self.product_figures)-1:
			self.product_figures_counter += 1
			self.open_image(self.product_figures[self.product_figures_counter])


	# 讀取肥料袋圖片
	def open_image(self,image_path):
		fig = Image.open(image_path)
		self.canvas.image = ImageTk.PhotoImage(self.image_resize(fig))
		self.canvas.itemconfig(self.image_on_canvas, image=self.canvas.image)


	# 肥料廠牌商品選單
	def GoodInCategorize(self,event):
		self.combo_goods['values'] = self.fert_dict.廠牌商品名稱 \
		[self.fert_dict.品目 == self.combo_categorize.get()].tolist()


	# 視窗關閉返回主選單
	def pf_delete_window(self):
		from Option_List import optionlist
		self.CM.destroy()
		manu = optionlist(self.language)
		manu.main()


	# 呼叫"NodeAnswer.exe"程式 (利用施肥紀錄來回答專家系統問題)
	def hidden_node_answer(self):
		p = subprocess.run(self.NodeAnswer, shell=True)


	# 主程式介面	
	def main(self):
		self.CM = tk.Tk()
		self.CM.title(self.interface['fertilizer']['title'])
		self.CM.geometry('910x550')
		self.CM.resizable(width=False, height=False)
		self.CM.protocol("WM_DELETE_WINDOW",self.pf_delete_window)

		#---------- Fertilizer Optional Area ----------#
		ID = []; product = []; amount = []; aim = []; freqency = [];
		aim_value = []; amount_value = []; product_value = []; frequency_value = []; id_value = []

		fert_frame = tk.LabelFrame(self.CM,text=self.interface['fertilizer']['database'],fg='blue')
		fert_frame.place(x=15,y=20)

		tk.Label(self.CM,text=self.interface['fertilizer']['unit'],width=20).place(x=320,y=5)
		tk.Label(fert_frame,text=self.interface['fertilizer']['ID'],borderwidth=2,relief="groove",width=17).grid(row=0,column=0,pady=2)
		tk.Label(fert_frame,text=self.interface['fertilizer']['product'],borderwidth=2,relief="groove",width=23).grid(row=0,column=1,pady=2)
		tk.Label(fert_frame,text=self.interface['fertilizer']['amount'],borderwidth=2,relief="groove",width=10).grid(row=0,column=2,pady=2)
		tk.Label(fert_frame,text=self.interface['fertilizer']['aim'],borderwidth=2,relief="groove",width=20).grid(row=0,column=3,pady=2)
		tk.Label(fert_frame,text=self.interface['fertilizer']['frequency'],borderwidth=2,relief="groove",width=20).grid(row=0,column=4,pady=2)

		id_list = self.fert_dict['登記證字號']
		product_list = self.fert_dict['廠牌商品名稱']
		aim_list = ['春肥','夏肥','秋肥','基肥','春茶後深修剪','夏季留養','葉面施肥']
		frequency_list = ['每年一次','每季一次','雙月一次','每月一次','雙週一次','每週一次']

		for f in range(1,self.row_num+1):
			f = str(f)
			locals()["fert_ID%s" % f] = tk.StringVar()
			locals()["fert_product%s" % f] = tk.StringVar()
			locals()["fert_amount%s" % f] = tk.StringVar()
			locals()["fert_aim%s" % f] = tk.StringVar()
			locals()["fert_frequency%s" % f] = tk.StringVar()
			
			self.ID = AutocompleteCombobox(fert_frame)
			self.ID.primary_setting(
				completion_list=id_list,
				recepter=locals()["fert_ID%s" % f],
				ligand=locals()["fert_product%s" % f],
				df=self.fert_dict,
				order=1,
				width=14
			)

			self.product = AutocompleteCombobox(fert_frame)
			self.product.primary_setting(
				completion_list=product_list,
				recepter=locals()["fert_product%s" % f],
				ligand=locals()["fert_ID%s" % f],
				df=self.fert_dict,
				order=2,
				width=20
			)

			self.frequency = AutocompleteCombobox(fert_frame)
			self.frequency.primary_setting(
				completion_list=frequency_list,
				recepter=locals()["fert_frequency%s" % f],
				ligand=locals()["fert_aim%s" % f],
				width=17
			)

			self.aim = AutocompleteCombobox(fert_frame)
			self.aim.primary_setting(
				completion_list=aim_list,
				recepter=locals()["fert_aim%s" % f],
				ligand=locals()["fert_frequency%s" % f],
				df=frequency_list,
				order=3,
				target_object=self.frequency,
				width=17
			)

			self.amount = tk.Entry(fert_frame,textvariable=locals()["fert_amount%s" % f], width=10)

			ID.append(self.ID)
			product.append(self.product)
			aim.append(self.aim)
			freqency.append(self.frequency)
			amount.append(self.amount)
			id_value.append(locals()["fert_ID%s" % f])
			product_value.append(locals()["fert_product%s" % f])
			aim_value.append(locals()["fert_aim%s" % f])
			frequency_value.append(locals()["fert_frequency%s" % f])
			amount_value.append(locals()["fert_amount%s" % f])

		self.fertilizer = [ID,product,amount,aim,freqency]
		self.fert_value = [id_value,product_value,amount_value,aim_value,frequency_value]

		for i in range(self.row_num):
			for j in range(5):
				self.fertilizer[j][i].grid(row=i+1,column=j,padx=1,pady=2)

		#---------- Other Fertilizer Area ----------#
		other_ID = []; other_product = []; other_aim = []; other_frequency = []; other_amount = []
		other_aim_value = []; other_frequency_value = []

		other_frame = tk.LabelFrame(self.CM,text=self.interface['fertilizer']['adding'],fg='blue')
		other_frame.place(x=15,y=290)
		tk.Label(other_frame,text=self.interface['fertilizer']['ID'],borderwidth=2,relief="groove",width=17).grid(row=0,column=0,pady=2)
		tk.Label(other_frame,text=self.interface['fertilizer']['product'],borderwidth=2,relief="groove",width=23).grid(row=0,column=1,pady=2)
		tk.Label(other_frame,text=self.interface['fertilizer']['amount'],borderwidth=2,relief="groove",width=10).grid(row=0,column=2,pady=2)
		tk.Label(other_frame,text=self.interface['fertilizer']['aim'],borderwidth=2,relief="groove",width=20).grid(row=0,column=3,pady=2)
		tk.Label(other_frame,text=self.interface['fertilizer']['frequency'],borderwidth=2,relief="groove",width=20).grid(row=0,column=4,pady=2)

		for i in range(1,self.ot_row_num+1):
			i = str(i)
			locals()["other_ID%s" % i] = tk.StringVar()
			locals()["other_product%s" % i] = tk.StringVar()
			locals()["other_amount%s" % i] = tk.StringVar()
			locals()["other_aim%s" % i] = tk.StringVar()
			locals()["other_frequency%s" % i] = tk.StringVar()

			self.ot_frequency = AutocompleteCombobox(other_frame)
			self.ot_frequency.primary_setting(
				frequency_list,
				locals()["other_frequency%s" % i],
				width=17
			)

			self.ot_aim = AutocompleteCombobox(other_frame)
			self.ot_aim.primary_setting(
				completion_list=aim_list,
				recepter=locals()["other_aim%s" % i],
				ligand=locals()["other_frequency%s" % i],
				df=frequency_list,
				target_object=self.ot_frequency,
				order=3,
				width=17
			)

			other_ID.append(locals()["other_ID%s" % i])
			other_product.append(locals()["other_product%s" % i])
			other_amount.append(locals()["other_amount%s" % i])
			other_aim.append(self.ot_aim)
			other_frequency.append(self.ot_frequency)

			other_aim_value.append(locals()["other_aim%s" % i])
			other_frequency_value.append(locals()["other_frequency%s" % i])

		for j in range(self.ot_row_num):
			tk.Entry(other_frame,textvariable=other_ID[j],width=17).grid(row=j+1,column=0)
			tk.Entry(other_frame,textvariable=other_product[j],width=23).grid(row=j+1,column=1)
			tk.Entry(other_frame,textvariable=other_amount[j],width=10).grid(row=j+1,column=2)
			other_aim[j].grid(row=j+1,column=3,padx=1,pady=2)
			other_frequency[j].grid(row=j+1,column=4,padx=1,pady=2)

		self.other_fert_value = [other_ID, other_product, other_amount, other_aim_value, other_frequency_value]

		#---------- Ingredient Showing Area ----------#
		subtitle = [self.interface['fertilizer']['ID'],self.interface['fertilizer']['product'],'N','P2O5','K2O','CaO','MgO','OM']
		ingredient_frame = tk.LabelFrame(self.CM,text='肥料成分顯示區',fg='blue')
		ingredient_frame.place(x=15,y=460)

		for i in range(len(subtitle)):
			width = 19 if i < 2 else 7
			locals()["%s" % subtitle[i]] = tk.StringVar()
			tk.Label(ingredient_frame,text=subtitle[i],width=width,relief="groove").grid(row=0,column=i,padx=3)
			tk.Label(ingredient_frame,textvariable=locals()["%s" % subtitle[i]],width=width).grid(row=1,column=i,padx=3)
			ShowVehicle.append(locals()["%s" % subtitle[i]])					# Save the component of current fertilizer's product
			
			if i > 1:
				locals()["total_%s" % subtitle[i]] = tk.StringVar()
				tk.Label(ingredient_frame,textvariable=locals()["total_%s" % subtitle[i]],width=width).grid(row=2,column=i,padx=3)
				StorageVehicle.append(locals()["total_%s" % subtitle[i]])		# Save the component of all fertilizer's product

		tk.Label(ingredient_frame,text=self.interface['fertilizer']['total_fertilizer'],width=35).grid(row=2,columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S)
		tk.Label(ingredient_frame,text='(%)').grid(row=1,column=8,sticky=tk.W)
		tk.Label(ingredient_frame,text=self.interface['fertilizer']['unit_no_title']).grid(row=2,column=8,sticky=tk.W)

		#---------- Fertitlizer Search Area ----------#
		self.id_search = tk.StringVar()

		#de-duplicated items and keeping original sorting
		item_list = self.fert_dict['品目'].tolist()
		item_list = sorted(set(item_list),key=item_list.index) 

		search_frame = tk.LabelFrame(self.CM,text=self.interface['fertilizer']['fer_serarch'],fg='blue')
		search_frame.place(x=680, y=20)

		# frame for item search
		item_frame = tk.Frame(search_frame)
		item_frame.grid(row=0,column=0,pady=3,sticky=tk.W)

		tk.Label(item_frame,text=self.interface['fertilizer']['categorize']).grid(row=0,column=0,padx=1,pady=2)
		tk.Label(item_frame,text=self.interface['fertilizer']['good']).grid(row=1,column=0,padx=1,pady=2)
		self.combo_categorize = ttk.Combobox(item_frame,values=item_list,width=20,state='readonly')
		self.combo_categorize.grid(row=0,column=1,padx=1,pady=2)
		self.combo_categorize.bind("<<ComboboxSelected>>", self.GoodInCategorize)
		self.combo_goods = ttk.Combobox(item_frame,width=20,state='readonly')
		self.combo_goods.grid(row=1,column=1,padx=1,pady=2)

		# frame for id search
		id_frame = tk.Frame(search_frame)
		id_frame.grid(row=1,column=0,pady=3)

		tk.Label(id_frame,text=self.interface['fertilizer']['accession']).grid(row=0,column=0,padx=2,pady=2)
		tk.Button(id_frame,text=self.interface['fertilizer']['search'],width=5,command=self.search).grid(row=0,column=1,padx=2,pady=2)
		tk.Button(id_frame,text=self.interface['fertilizer']['import'],width=5,command=self.importID).grid(row=0,column=2,padx=2,pady=2)

		tk.Button(id_frame,text=self.interface['fertilizer']['clear'],width=5,command=self.clear).grid(row=0,column=3,padx=2,pady=2)
		tk.Entry(id_frame,textvariable=self.id_search,width=30).grid(row=1,columnspan=4,pady=3)

		# frame for figure setting
		figure_frame = tk.Frame(search_frame)
		figure_frame.grid(row=2,column=0,pady=3)

		self.canvas = tk.Canvas(figure_frame,width=180,height=200,bd=2,bg='lightgray',relief=tk.GROOVE)
		self.canvas.grid(row=0,column=0,ipadx=5,ipady=5)

		# it's an intra-frame of button
		button_intra_frame = tk.Frame(figure_frame)
		button_intra_frame.grid(row=1,column=0)
		self.pre_button = tk.Button(button_intra_frame,text=self.interface['fertilizer']['next'],width=7,command=self.previous_image_on_canvas)
		self.pre_button.grid(row=0,column=0,padx=15,pady=5)
		self.next_button = tk.Button(button_intra_frame,text=self.interface['fertilizer']['back'],width=7,command=self.next_image_on_canvas)
		self.next_button.grid(row=0,column=1,padx=15,pady=5)
		self.pre_button.config(state=tk.DISABLED)
		self.next_button.config(state=tk.DISABLED)

		tk.Button(self.CM,text=self.interface['fertilizer']['edit'],width=7,command=self.fertitlizer_edit).place(x=690,y=430)
		tk.Button(self.CM,text=self.interface['fertilizer']['calculate'],width=7,command=self.calculate).place(x=760,y=430)
		tk.Button(self.CM,text=self.interface['fertilizer']['suggest'],width=11,command=self.review).place(x=760,y=470)
		tk.Button(self.CM,text=self.interface['fertilizer']['submit'],width=7,command=self.submit).place(x=830,y=430)

		self.CM.mainloop()


# if __name__ == '__main__':
# 	fm = Fertilizer_management(2,'001-0002')
# 	fm.main()

