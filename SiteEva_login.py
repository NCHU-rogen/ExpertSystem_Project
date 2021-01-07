#!usr/bin/python3
# Coding: utf-8
# Author: Rogen
# Description: 茶區地點登入


from Option_List import optionlist
from Mysql_connect import mysql
from GUI_language import *
from tkinter import filedialog, ttk, messagebox
import tkinter as tk
import re, os, time
import pandas as pd
import subprocess
import twd97
import json


class SiteEvaLogin(mysql):
	def __init__(self, ver):
		super(SiteEvaLogin,self).__init__(ver)
		self.UVA_photo_Path = './Photo/SiteEvaluation/N1101'
		self.language = ver
		self.SaveCSV = './Dataset/SiteEva_Table.csv'
		self.TeaRegion = pd.read_excel('CropBasedInfo.xlsx', sheet_name='TeaRegions', header=0, dtype={'Base Code':'str'})
		self.TeaRegion = self.TeaRegion.dropna(subset=['Country Name'])
		self.TeaRegion = self.TeaRegion.reset_index(drop=True)
		self.Cultivar = pd.read_excel('CropBasedInfo.xlsx',sheet_name='Cultivars')
		self.__PrimarySet()
		self.__update_csv__()


	def __PrimarySet(self):
		if self.language == 1:
			ch = Chinese()
			self.interface = ch.SiteEva_Login_Interface()
		else:
			en = English()
			self.interface = en.SiteEva_Login_Interface()

		if not os.path.exists(self.SaveCSV):
			with open(self.SaveCSV, 'w', encoding='utf_8_sig') as w:
				w.write(','.join(['Internal_Code','EW_Longitude','Longitude_Degree','Longitude_Minute','Longitude_second','NS_Latitude','Latitude_degree','Latitude_minute','Latitude_second',
					'Country','Region','Name','Phone','EW_Field','NS_Field','Variety','Planting_Age','Entry_Date','Surveyor','Latitude_TWD97','Longitude_TWD97'])+'\n')


	def __update_csv__(self):
		self.siteva_df = pd.read_csv(self.SaveCSV, dtype={'Internal_Code':str,'Name':str,'Phone':str,'Variety':str,'Entry_Date':str,'Surveyor':str,
			'Longitude_Degree':float, 'Longitude_Minute':float, 'Longitude_second':float, 'Latitude_degree':float, 'Latitude_minute':float, 'Latitude_second':float, 
			'Latitude_TWD97':float, 'Longitude_TWD97':float}, encoding='utf_8_sig')


	# 將TWD97座標轉為WGS84經緯度
	def latlon_transform(self,alist):
		alist = [float(i) for i in alist]
		lat = (alist[2]/60+alist[1])/60+alist[0]
		lon = (alist[5]/60+alist[4])/60+alist[3]
		return(round(lat,5),round(lon,5))


	# 茶區序列編號
	def serial_code(self, serial_number, func, digit=3):
		while True:
			for i in range(digit):
				locals()["flag%s" % i] = 0

			carry_digit = digit-1
			sp_serial_number = list(serial_number)
			number = ord(sp_serial_number[digit])
			number = number+1 if func == 'plus' else number-1

			if number <= 57 or (number >= 65 and number <= 90): 
				character = chr(number)
			elif number == 58:
				character = chr(number+7) 						# plus 7 indicates the ASCII number gap of character '9' and 'a'
			elif number > 90:
				character = chr(number-43)
				locals()["flag%s" % carry_digit] = 1

			sp_serial_number[digit] = character
			serial_number = ''.join(sp_serial_number)
			
			if locals()["flag%s" % carry_digit] == 1:
				digit = digit-1
			else:
				break

		return(serial_number)


	# 串接到資料庫登入
	def Connect2Sql(self):
		# cont = mysql(self.language, self.siteva)
		# cont.main()
		self.sqlmain(self.siteva)


	# 主程式介面
	def main(self,update={}):
		def RegionCategorize(event):
			regionList['values'] = self.TeaRegion['Region Name'][self.TeaRegion['Country Name'] == self.country.get()].tolist()

		self.siteva = tk.Tk()
		self.siteva.title(self.interface['login']['title'])
		self.siteva.geometry('530x450')
		self.siteva.resizable(width=False, height=False)
		self.siteva.protocol("WM_DELETE_WINDOW",self.wm_delete_window)
		
		default = {
			'country':'',
			'region':'',
			'lon_EW':'東經',
			'lat_NS':'北緯',
			'name':'',
			'lon_D':'120',
			'lon_M':'43',
			'lon_S':'7.15',
			'lat_D':'23',
			'lat_M':'50',
			'lat_S':'4.12',
			'search_range':'100'
		}
		default.update(update)

		self.country = tk.StringVar(value=default['country'])
		self.region = tk.StringVar(value=default['region'])
		self.lon_EW = tk.StringVar(value=default['lon_EW'])
		self.lat_NS = tk.StringVar(value=default['lat_NS'])
		self.name = tk.StringVar(value=default['name'])
		self.lon_D = tk.StringVar(value=default['lon_D'])
		self.lon_M = tk.StringVar(value=default['lon_M'])
		self.lon_S = tk.StringVar(value=default['lon_S'])
		self.lat_D = tk.StringVar(value=default['lat_D'])
		self.lat_M = tk.StringVar(value=default['lat_M'])
		self.lat_S = tk.StringVar(value=default['lat_S'])
		self.search_range = tk.StringVar(value=default['search_range'])

		lat = [self.lat_D,self.lat_M,self.lat_S]
		lon = [self.lon_D,self.lon_M,self.lon_S]

		table_header = [self.interface['table']['country'],
						self.interface['table']['region'],
						self.interface['table']['longitude'],
						self.interface['table']['latitude'],
						self.interface['table']['name'],
						self.interface['table']['date']]

		dimension = [self.interface['login']['degree'],
					self.interface['login']['minute'],
					self.interface['login']['second']]

		#---------- menubar Setting Area ----------#
		menubar = tk.Menu(self.siteva)
		filemenu = tk.Menu(menubar, tearoff=0)
		menubar.add_cascade(label=self.interface['menubar']['setting'],menu=filemenu)
		filemenu.add_command(label=self.interface['menubar']['db_connect'],command=self.Connect2Sql)
		self.siteva.config(menu=menubar)

		#---------- Option Setting Area ----------#
		frame_country = tk.Frame(self.siteva)
		frame_country.place(x=15,y=10,anchor='nw')
		frame_locate = tk.Frame(self.siteva)
		frame_locate.place(x=15,y=50,anchor='nw')
		frame_lon = tk.Frame(frame_locate)
		frame_lon.grid(row=0,column=1,padx=5,pady=5,ipady=3)
		frame_lat = tk.Frame(frame_locate)
		frame_lat.grid(row=1,column=1,padx=5,pady=5,ipady=3)

		self.countryName = self.TeaRegion['Country Name'].tolist()

		tk.Label(frame_country,text=self.interface['login']['country']).grid(row=0,column=0,padx=5,pady=5,ipady=3)
		tk.Label(frame_country,text=self.interface['login']['region']).grid(row=0,column=2,padx=5,pady=5,ipady=3)
		countryList = ttk.Combobox(
			frame_country,
			textvariable=self.country,
			values=sorted(set(self.countryName),key=self.countryName.index),
			state='readonly'
		)
		countryList.grid(row=0,column=1,padx=5,pady=5,ipady=3)
		countryList.bind("<<ComboboxSelected>>",RegionCategorize)

		regionList = ttk.Combobox(
			frame_country,
			textvariable=self.region,
			state='readonly'
		)
		regionList.grid(row=0,column=3,padx=5,pady=5,ipady=3)
		
		tk.Label(frame_locate,text=self.interface['login']['longitude']).grid(row=0,column=0,padx=1,pady=5,ipady=3,sticky=tk.E)
		tk.Label(frame_locate,text=self.interface['login']['latitude']).grid(row=1,column=0,padx=1,pady=5,ipady=3,sticky=tk.E)

		EW_option = ttk.Combobox(
			frame_locate,
			values=['東經','西經'],
			textvariable=self.lon_EW,
			state='readonly',
			width=10
		)
		EW_option.grid(row=0,column=2,padx=1,pady=5,ipady=3,sticky=tk.W)

		NS_option = ttk.Combobox(
			frame_locate,
			values=['北緯','南緯'],
			textvariable=self.lat_NS,
			state='readonly',
			width=10
		)
		NS_option.grid(row=1,column=2,padx=1,pady=5,ipady=3,sticky=tk.W)

		tk.Label(frame_locate,text=self.interface['login']['name']).grid(row=2,column=0,padx=2,pady=5,ipady=3,sticky=tk.E)
		tk.Entry(frame_locate,textvariable=self.name, width=20).grid(row=2,column=1,padx=2,pady=5,ipady=3,sticky=tk.W)
		tk.Label(frame_locate,text=self.interface['login']['range']).grid(row=2,column=2,padx=2,pady=5,ipady=3,sticky=tk.E)
		tk.Entry(frame_locate,textvariable=self.search_range, width=7).grid(row=2,column=3,padx=2,pady=5,ipady=3,sticky=tk.W)

		for i in range(2):
			col_counter = 0
			text_counter = 0
			if i == 1:
				frame = frame_lon
				l = lon
			else:
				frame = frame_lat
				l = lat

			for d in dimension:
				tk.Entry(frame, textvariable=l[text_counter], width=7).grid(row=0,column=col_counter,padx=1,sticky=tk.W)
				tk.Label(frame,text=d).grid(row=0,column=col_counter+1,padx=1,sticky=tk.W)
				col_counter += 2
				text_counter += 1

		#---------- Table Setting Area ----------#
		self.tree = ttk.Treeview(self.siteva, columns=['1','2','3','4','5','6'], show='headings')
		for i in range(6):
			if i >= 2 and i <= 3:
				self.tree.column(str(i+1),width=100,anchor='center')
			elif i <= 1:
				self.tree.column(str(i+1),width=70,anchor='center')
			else:
				self.tree.column(str(i+1),width=85,anchor='center')
			self.tree.heading(str(i+1),text=table_header[i])
		self.tree.place(x=10,y=170)
		self.tree.bind('<ButtonRelease-1>', self.field_info)

		tk.Button(self.siteva,text=self.interface['button']['search'],width=10,command=self.search).place(x=260,y=410)
		tk.Button(self.siteva,text=self.interface['button']['add'],width=10,command=self.addnew).place(x=360,y=410)
		
		self.siteva.mainloop()


	# 視窗關閉返回主選單
	def wm_delete_window(self):
		for file in ['TeaRegionLoading.txt','CropVISTMapInfo.txt','SuppliedInfo.txt']:
			if os.path.exists(file):
				os.remove(file)
		self.siteva.destroy()


	# 刪除茶區資料
	def delete(self, internal_code):
		idx = self.siteva_df.index[self.siteva_df['Internal_Code'] == internal_code]
		self.siteva_df = self.siteva_df.drop(idx)
		self.siteva_df.to_csv(self.SaveCSV, index=False, encoding='utf_8_sig')
		self.field_win.destroy()
		self.tree.delete(*self.tree.get_children())
		
		# Edited internal_code of Code_Recode.json
		# with open('Code_Recode.json','r') as l:
		# 	code_dict = json.loads(l.readline())
		# 	sp_code = internal_code.split('-')[0]
		# 	number = code_dict[sp_code]
		# 	number = self.serial_code(number, func='minus')
		# 	code_dict[sp_code] = number

		# with open('Code_Recode.json','w') as d:
		# 	d.write(json.dumps(code_dict, sort_keys=True))


	# 新增茶區資料
	def addnew(self):
		def inter_code(lat,lon,digit=3):
			code_dict = {}
			basecode_idx = self.TeaRegion.index[self.TeaRegion['Region Name'] == add_Region.get()]

			#---------- To find what code of tea's area belong for? ----------#
			# sql_str = 'select Internal_Code from regionboundary where \
			# 			LeftTop_Longitude <= %f and RightBottom_Longitude >= %f and \
			# 			LeftTop_Latitude >= %f and RightBottom_Latitude <= %f;' % (lon,lon,lat,lat)
			# self.initiate()
			# self.cursor.execute('use expert_system')
			# self.cursor.execute(sql_str)
			# area_code = self.cursor.fetchall()
			# self.close_conn()

			internal = list((self.TeaRegion['UL Long'][basecode_idx] <= lon) & (self.TeaRegion['LR Long'][basecode_idx] >= lon) & \
							(self.TeaRegion['UL Lat'][basecode_idx] >= lat) & (self.TeaRegion['LR Lat'][basecode_idx] <= lat))
			area_code = self.TeaRegion['Base Code'][basecode_idx].tolist()

			if internal[0] == False:
				tk.messagebox.showinfo('INFO','No belong in any tea area with your input location...')
				return(0,'')
			else:
				#---------- To retrive serial number of the tea's area ----------#
				if os.path.exists('./Code_Recode.json'):
					with open('Code_Recode.json', 'r') as r:
						jsonData = r.readline()
						code_dict = json.loads(jsonData)
					try:
						serial_number = code_dict[area_code[0]]			# Some tea's location had been registered in the tea's area
					except:
						serial_number = '0000'							# No tea's location had been registered in the tea's area yet
				else:
					serial_number = '0000'								# Not any tea's area had been registered

				#---------- Serial number carry ----------#
				serial_number = self.serial_code(serial_number, func='plus')

				#---------- To recode serial number of the tea's area ----------#
				code_dict[area_code[0]] = serial_number
				jsonDump = json.dumps(code_dict, sort_keys=True)
				with open('Code_Recode.json', 'w') as w:
					w.write(jsonDump)

				intercode = '%s-%s' % (area_code[0],serial_number)
				return(1,intercode)

		def datatype_check():
			mylist = option_get[:4]+option_get[6:]
			error = [option[option_get.index(o)] for o in mylist if o.get() == '']
			for o in option_get[4]:
				if o.get() == 0:
					error.append(Lon_DMS[option_get[4].index(o)])
			for o in option_get[5]:
				if o.get() == 0:
					error.append(Lat_DMS[option_get[5].index(o)])
			return error

		def submit(option_get):
			writer = []; situation = 1
			error = datatype_check()

			if len(error) != 0:
				error_billboard.delete(1.0, tk.END)
				for e in error:
					error_billboard.insert(1.0,'The Field '+e+' is not empty!\n')
			else:
				with open(self.SaveCSV, 'a+', encoding='utf_8_sig') as a:
					name_idx = self.siteva_df.index[self.siteva_df['Name'] == option_get[2].get()]
					phone_idx = self.siteva_df.index[self.siteva_df['Phone'] == option_get[3].get()]
					cross_idx = list(set(phone_idx).intersection(name_idx))

					for opt in option_get[4:6]:
						for o in opt:
							writer.append(o.get())
					for o in option_get[:4]+option_get[6:]:
						writer.append(o.get())

					twd97_lat,twd97_lon = self.latlon_transform(writer[3:6]+writer[0:3])
					twd = list(twd97.fromwgs84(twd97_lat,twd97_lon))

					#------ database exist same data when searching ------#
					if len(cross_idx) != 0:
						intercode = self.siteva_df.iloc[cross_idx[0],0]

					#------ database not exist the data when searching ------#
					else:
						(situation, intercode) = inter_code(twd97_lat,twd97_lon)

					if situation == 1:
						writer.insert(0,intercode)				# Adding an international code of tea region
						writer.insert(1,self.lon_EW.get())		# Adding east-west longitude
						writer.insert(5,self.lat_NS.get())		# Adding north-south latitude
						writer = writer + twd					# Adding twd97 longitude and twd97 latitude
						a.write(','.join(map(str,writer))+'\n')
				new.destroy()

		def combobox(event,obj=None):
			o = obj if obj else event.widget
			self.combo_region['values'] = self.TeaRegion['Region Name'][self.TeaRegion['Country Name'] == o.get()].tolist()
			code = self.TeaRegion['Country Code'][self.TeaRegion['Country Name'] == o.get()].tolist()[0]
			variety = self.Cultivar['品種名'][self.Cultivar['Language Code'] == code].tolist()
			self.combo_variety['values'] = sorted(set(variety),key=variety.index)

		new = tk.Toplevel(self.siteva)
		new.title(self.interface['new']['title'])
		new.geometry('600x410')
		new.grab_set()
		new.resizable(width=False,height=False)

		frame_new = tk.Frame(new)
		frame_new.place(x=20,y=10)

		add_Country = tk.StringVar(value=self.country.get())
		add_Region = tk.StringVar(value=self.region.get())
		add_Name = tk.StringVar(value=self.name.get())
		add_Phone = tk.StringVar()
		add_FieldEW = tk.StringVar()
		add_FieldNS = tk.StringVar()
		add_Variety = tk.StringVar()
		add_PlantingYear = tk.StringVar(value='YYYY')
		add_Surveyor = tk.StringVar()
		add_EntryDate = tk.StringVar(value=time.strftime('%Y-%m-%d',time.localtime()))
		add_Lon_D = tk.StringVar(value=self.lon_D.get())
		add_Lon_M = tk.StringVar(value=self.lon_M.get())
		add_Lon_S = tk.StringVar(value=self.lon_S.get())
		add_Lat_D = tk.StringVar(value=self.lat_D.get())
		add_Lat_M = tk.StringVar(value=self.lat_M.get())
		add_Lat_S = tk.StringVar(value=self.lat_S.get())

		counter = 0; tag = 0
		option = [
			self.interface['new']['country'],
			self.interface['new']['region'],
			self.interface['new']['name'],
			self.interface['new']['phone'],
			self.interface['new']['longitude'],
			self.interface['new']['latitude'],
			self.interface['new']['field_EW'],
			self.interface['new']['field_NS'],
			self.interface['new']['variety'],
			self.interface['new']['plant_year'],
			self.interface['new']['entry_date'],
			self.interface['new']['surveyor']
		]

		option_get = [
			add_Country,
			add_Region,
			add_Name,
			add_Phone,
			[add_Lon_D,add_Lon_M,add_Lon_S],
			[add_Lat_D,add_Lat_M,add_Lat_S],
			add_FieldEW,
			add_FieldNS,
			add_Variety,
			add_PlantingYear,
			add_EntryDate,
			add_Surveyor
		]
		Lon_DMS = ['Longitude_Degree','Longitude_Minute','Longitude_second']
		Lat_DMS = ['Latitude_degree','Latitude_minute','Latitude_second']

		for i in option:
			if counter % 2 == 0: 
				tk.Label(frame_new,text=i+':').grid(row=counter//2,column=0,padx=1,pady=5,ipady=3,sticky=tk.W)
				if counter != 0 and counter != 4 and counter != 8:
					tk.Entry(frame_new, textvariable=option_get[counter], width=20).grid(row=counter//2,column=1,padx=1,pady=5,ipady=3,sticky=tk.W)
			else:
				tk.Label(frame_new,text=i+':').grid(row=counter//2,column=2,padx=1,pady=5,ipady=3,sticky=tk.W)
				if counter != 5 and counter != 1:
					tk.Entry(frame_new, textvariable=option_get[counter], width=20).grid(row=counter//2,column=3,padx=1,pady=5,ipady=3,sticky=tk.W)

			# Setting columns of degreed, minutes and seconds in Lon, Lat
			if counter == 4 or counter == 5:
				text = [self.interface['new']['degree'],self.interface['new']['minute'],self.interface['new']['second']]
				f = tk.Frame(frame_new,width=10)
				if counter == 4:
					f.grid(row=2,column=1)
					locus = 'E' if self.lon_EW.get() == '東經' else 'W'
				else:
					f.grid(row=2,column=3)
					locus = 'N' if self.lat_NS.get() == '北緯' else 'S'
				text.append(locus)

				for ii in range(4):
					if ii < 3:
						tk.Entry(f,textvariable=option_get[counter][ii],width=4).grid(row=0,column=tag,padx=1,pady=5,ipady=3,sticky=tk.W)
						tk.Label(f, text=text[ii]).grid(row=0,column=tag+1,padx=1,pady=5,ipady=3,sticky=tk.W)
					else:
						tk.Label(f,text='[%s]'%text[ii],fg='red').grid(row=0,column=tag,padx=1,pady=5,ipady=3,sticky=tk.W)
					tag += 2

			# Setting combobox option
			if counter == 0 or counter == 1 or counter == 8:
				if counter == 0:			# Country column
					self.combo_country = ttk.Combobox(frame_new,textvariable=add_Country,values=sorted(set(self.countryName),key=self.countryName.index),width=17,state='disabled')
					self.combo_country.grid(row=counter//2,column=1,padx=1,pady=5,ipady=3,sticky=tk.W)
					self.combo_country.bind('<<ComboboxSelected>>',combobox)
				elif counter == 1:			# Region column
					self.combo_region = ttk.Combobox(frame_new,textvariable=add_Region,width=17,state='disabled')
					self.combo_region.grid(row=counter//2,column=3,padx=1,pady=5,ipady=3,sticky=tk.W)
				elif counter == 8:			# Variety column
					self.combo_variety = ttk.Combobox(frame_new,textvariable=add_Variety,width=17)
					self.combo_variety.grid(row=counter//2,column=1,padx=1,pady=5,ipady=3,sticky=tk.W)
					self.combo_variety.bind('<Button-1>',lambda event, x=add_Country: combobox(event,x))

			counter += 1

		error_billboard = tk.Text(new, width=80,height=8,bg='lightgray')
		error_billboard.place(x=20,y=250)
		tk.Button(new, text=self.interface['button']['submit'],width=12,command=lambda:submit(option_get)).place(x=450,y=370)


	# 茶區搜尋功能
	def search(self):
		def check():
			warner = []
			if self.country.get() == '':
				warning.append('Country option is empty!')
			if self.region.get() == '':
				warning.append('Region option is empty!')
			if self.name.get() == '':
				warning.append('Name filed is empty!')
			if self.search_range.get() == '':
				warning.append('Range of search filed is empty!')	
			if self.lon_D.get() == '':
				warning.append('Longitude degree filed is empty!')
			if self.lon_M.get() == '':
				warning.append('Longitude minute filed is empty!')
			if self.lon_S.get() == '':
				warning.append('Longitude second filed is empty!')
			if self.lat_D.get() == '':
				warning.append('Latitude degree filed is empty!')
			if self.lat_M.get() == '':
				warning.append('Latitude minute filed is empty!')
			if self.lat_S.get() == '':
				warning.append('Latitude second filed is empty!')
			return(warner)

		# warning = check()
		lat = []; lon = []; name = []; phone = []; date = []; idx1 = []; idx2 = []; country = []; region = []
		idx = []; idx_name = []; idx_latlon = []; idx_country = []
		self.__update_csv__()

		ser_country = self.country.get()
		ser_region = self.region.get()
		ser_Lon_D = self.lon_D.get()
		ser_Lon_M = self.lon_M.get()
		ser_Lon_S = self.lon_S.get()
		ser_Lat_D = self.lat_D.get()
		ser_Lat_M = self.lat_M.get()
		ser_Lat_S = self.lat_S.get()
		ser_lon_EW = self.lon_EW.get()
		ser_lat_NS = self.lat_NS.get()
		farmer = self.name.get()
		ranges = self.search_range.get()

		if ser_country and ser_region:
			idx_country = self.siteva_df.index[(self.siteva_df['Country'] == ser_country) & (self.siteva_df['Region'] == ser_region)]
			idx_lonlat = self.siteva_df.index[(self.siteva_df['EW_Longitude'] == ser_lon_EW) & (self.siteva_df['NS_Latitude'] == ser_lat_NS)]

			# Searching tea area in the range of lat and lon where user look for
			if ser_Lon_D and ser_Lon_M and ser_Lon_S and ser_Lat_D and ser_Lat_M and ser_Lat_S and ranges:

				twd97_lat,twd97_lon = self.latlon_transform([ser_Lat_D, ser_Lat_M, ser_Lat_S, ser_Lon_D, ser_Lon_M, ser_Lon_S])
				twd = twd97.fromwgs84(twd97_lat,twd97_lon)

				min_lat = twd[0]-int(ranges)
				max_lat = twd[0]+int(ranges)
				min_lon = twd[1]-int(ranges)
				max_lon = twd[1]+int(ranges)

				idx_lattwd97 = self.siteva_df.index[(self.siteva_df['Latitude_TWD97'] >= min_lat) & (self.siteva_df['Latitude_TWD97'] <= max_lat)]
				idx_lontwd97 = self.siteva_df.index[(self.siteva_df['Longitude_TWD97'] >= min_lon) & (self.siteva_df['Longitude_TWD97'] <= max_lon)]
				idx_latlon = list(set(idx_lattwd97).intersection(idx_lontwd97))

			# Searching tea area with farmer's name
			if farmer:
				name_boolean = [bool(re.match(farmer,i)) for i in self.siteva_df.Name.tolist()]
				idx_name = self.siteva_df.index[name_boolean]
			
			# Intersection of comparison results
			if len(idx_country):
				if len(idx_latlon) and len(idx_name):			# Combined the lat-lon with name to find intersetion
					idx = list(set(idx_country).intersection(idx_latlon,idx_lonlat,idx_name))
				elif len(idx_latlon) and (not len(idx_name)):	# Combined the lat-lon without name to find intersetion
					idx = list(set(idx_country).intersection(idx_latlon,idx_lonlat))
				elif len(idx_name) and (not len(idx_latlon)):	# Combined the name without lat-lon to find intersetion
					idx = list(set(idx_country).intersection(idx_name))

			# Collecting the data which are retrived
			if len(idx) > 0:
				for c in self.siteva_df.iloc[idx,9].values.tolist():
					country.append(c)

				for r in self.siteva_df.iloc[idx,10].values.tolist():
					region.append(r)

				for row in self.siteva_df.iloc[idx,2:5].values.tolist():
					locus = 'E' if self.lon_EW.get() == '東經' else 'W'
					row = [int(_) if type(_) == 'int' else float(_) for _ in row]
					row = list(map(str,row))
					lon.append('%s°%s\'%s"%s' % (row[0],row[1],row[2],locus))

				for row in self.siteva_df.iloc[idx,6:9].values.tolist():
					locus = 'N' if self.lat_NS.get() == '北緯' else 'S'
					row = [int(_) if type(_) == 'int' else float(_) for _ in row]
					row = list(map(str,row))
					lat.append('%s°%s\'%s"%s' % (row[0],row[1],row[2],locus))

				for n in self.siteva_df.iloc[idx,11].values.tolist():
					name.append(n)

				for d in self.siteva_df.iloc[idx,17].values.tolist():
					date.append(d)
			else:
				tk.messagebox.showinfo('INFO','Can not find any result!')
		else:
			tk.messagebox.showinfo('INFO','The country and region don not empty!')

		# Clearing results of pervious search
		x = self.tree.get_children()
		for item in x:			
			self.tree.delete(item)
		# Listing results
		for z in range(len(name)):
			self.tree.insert('','end',values=[country[z],region[z],lon[z],lat[z],name[z],date[z]])


	# 茶區詳細資訊
	def field_info(self, event):
		if len(self.tree.selection()):
			try:
				if self.field_win.state() == 'normal':
					pass
			except:
				self.field_win = tk.Toplevel(self.siteva)
				self.field_win.title(self.interface['field']['title'])
				self.field_win.geometry('550x380')
				self.field_win.resizable(width=False, height=False)
				labelframe = tk.LabelFrame(self.field_win, fg='blue', font=('Arial',14), text=self.interface['field']['information'])
				labelframe.pack(expand=tk.Y, anchor=tk.N)

				for item in self.tree.selection():
					i = 0
					item_text = self.tree.item(item,"values")
					idx = self.siteva_df.index[(self.siteva_df['Name'] == item_text[4]) & (self.siteva_df['Entry_Date'] == item_text[5])]
					info = self.siteva_df.iloc[idx,:-2].values[0]		# Remove TWD97 coordinate
					for o in info:
						if i < 9:
							row = i; col = 0
						else:
							row = i-9; col = 2
						tk.Label(labelframe, text=self.siteva_df.columns.values[i], font=('Arial',12)).grid(row=row,column=col,padx=7,pady=3,sticky=tk.E)
						tk.Label(labelframe, text=o, font=('Arial',12)).grid(row=row,column=col+1,padx=7,pady=3,sticky=tk.E)
						i += 1
			buttonframe = tk.Label(self.field_win)
			buttonframe.place(x=130,y=340,width=300,height=40)
			tk.Button(buttonframe,text=self.interface['button']['submit'],width=7,command=lambda x=info: self.save_mapinfo(x)).grid(row=0,column=0,padx=20)
			tk.Button(buttonframe,text=self.interface['button']['edit'],width=7,command=lambda x=info, y=idx: self.edit_mapinfo(x,y)).grid(row=0,column=1,padx=20)
			tk.Button(buttonframe,text=self.interface['button']['delete'],width=7,command=lambda x=info[0]: self.delete(x)).grid(row=0,column=2,padx=20)


	# 茶區登入資訊修改
	def edit_mapinfo(self, info, edit_idx):
		def edit_submit():
			# Update the tea information into csv
			info[2:5] = [edit_Lon_D.get(),edit_Lon_M.get(),edit_Lon_S.get()]
			info[6:9] = [edit_Lat_D.get(),edit_Lat_M.get(),edit_Lat_S.get()]
			info[9:] = [combo_country.get(),combo_region.get(),edit_Name.get(),edit_Phone.get(),edit_FieldEW.get(),edit_FieldNS.get(),
						combo_variety.get(),edit_PlantingYear.get(),edit_EntryDate.get(),edit_Surveyor.get()]
			self.siteva_df.iloc[edit_idx,:-2] = info
			self.siteva_df.to_csv(self.SaveCSV, index=False, encoding='utf_8_sig')
			# Into the option table
			self.editmap_win.destroy()
			self.field_win.destroy()
			self.save_mapinfo(info)

		self.editmap_win = tk.Toplevel(self.field_win) 
		self.editmap_win.title(self.interface['edit']['title'])
		self.editmap_win.geometry('600x300')

		frame_edit = tk.Frame(self.editmap_win)
		frame_edit.place(x=20,y=10)

		edit_Lon_D = tk.StringVar(value=info[2])
		edit_Lon_M = tk.StringVar(value=info[3])
		edit_Lon_S = tk.StringVar(value=info[4])
		edit_Lat_D = tk.StringVar(value=info[6])
		edit_Lat_M = tk.StringVar(value=info[7])
		edit_Lat_S = tk.StringVar(value=info[8])
		edit_Country = tk.StringVar(value=info[9])
		edit_Region = tk.StringVar(value=info[10])
		edit_Name = tk.StringVar(value=info[11])
		edit_Phone = tk.StringVar(value=info[12])
		edit_FieldEW = tk.StringVar(value=info[13])
		edit_FieldNS = tk.StringVar(value=info[14])
		edit_Variety = tk.StringVar(value=info[15])
		edit_PlantingYear = tk.StringVar(value=info[16])
		edit_EntryDate = tk.StringVar(value=info[17])
		edit_Surveyor = tk.StringVar(value=info[18])

		counter = 0; tag = 0
		option = [
			self.interface['new']['country'],
			self.interface['new']['region'],
			self.interface['new']['name'],
			self.interface['new']['phone'],
			self.interface['new']['longitude'],
			self.interface['new']['latitude'],
			self.interface['new']['field_EW'],
			self.interface['new']['field_NS'],
			self.interface['new']['variety'],
			self.interface['new']['plant_year'],
			self.interface['new']['entry_date'],
			self.interface['new']['surveyor']
		]

		option_get = [
			edit_Country,
			edit_Region,
			edit_Name,
			edit_Phone,
			[edit_Lon_D,edit_Lon_M,edit_Lon_S],
			[edit_Lat_D,edit_Lat_M,edit_Lat_S],
			edit_FieldEW,
			edit_FieldNS,
			edit_Variety,
			edit_PlantingYear,
			edit_EntryDate,
			edit_Surveyor
		]

		for i in option:
			if counter % 2 == 0: 
				tk.Label(frame_edit,text=i+':').grid(row=counter//2,column=0,padx=1,pady=5,ipady=3,sticky=tk.W)
				if counter != 0 and counter != 4 and counter != 8:
					tk.Entry(frame_edit, textvariable=option_get[counter], width=20).grid(row=counter//2,column=1,padx=1,pady=5,ipady=3,sticky=tk.W)
			else:
				tk.Label(frame_edit,text=i+':').grid(row=counter//2,column=2,padx=1,pady=5,ipady=3,sticky=tk.W)
				if counter != 1 and counter != 5:
					tk.Entry(frame_edit, textvariable=option_get[counter], width=20).grid(row=counter//2,column=3,padx=1,pady=5,ipady=3,sticky=tk.W)

			# Setting columns of degreed, minutes and seconds in Lon, Lat
			if counter == 4 or counter == 5:
				text = [self.interface['edit']['degree'],
						self.interface['edit']['minute'],
						self.interface['edit']['second']]
				f = tk.Frame(frame_edit,width=10)
				if counter == 4:
					f.grid(row=2,column=1)
					locus = 'E' if info[1] == '東經' else 'W'
				else:
					f.grid(row=2,column=3)
					locus = 'N' if info[5] == '北緯' else 'S'
				text.append(locus)

				for ii in range(4):
					if ii < 3:
						tk.Entry(f,textvariable=option_get[counter][ii],width=4).grid(row=0,column=tag,padx=1,pady=5,ipady=3,sticky=tk.W)
						tk.Label(f, text=text[ii]).grid(row=0,column=tag+1,padx=1,pady=5,ipady=3,sticky=tk.W)
					else:
						tk.Label(f,text='[%s]'%text[ii],fg='red').grid(row=0,column=tag,padx=1,pady=5,ipady=3,sticky=tk.W)
					tag += 2

			# Setting combobox option
			if counter == 0 or counter == 1 or counter == 8:
				if counter == 0:			# Country column
					combo_country = ttk.Combobox(frame_edit,values=sorted(set(self.countryName),key=self.countryName.index),width=17,state=tk.DISABLED)
					combo_country.grid(row=counter//2,column=1,padx=1,pady=5,ipady=3,sticky=tk.W)
					combo_country.current(combo_country['values'].index(info[9]))

				elif counter == 1:			# Region column
					combo_region = ttk.Combobox(frame_edit,width=17,values=self.TeaRegion['Region Name'][self.TeaRegion['Country Name'] == edit_Country.get()].tolist(),state=tk.DISABLED)
					combo_region.grid(row=counter//2,column=3,padx=1,pady=5,ipady=3,sticky=tk.W)
					combo_region.current(combo_region['values'].index(edit_Region.get()))

				elif counter == 8:			# Variety column
					combo_variety = ttk.Combobox(frame_edit,width=17)
					combo_variety.grid(row=counter//2,column=1,padx=1,pady=5,ipady=3,sticky=tk.W)
					code = self.TeaRegion['Country Code'][self.TeaRegion['Country Name'] == edit_Country.get()].tolist()[0]
					variety = self.Cultivar['品種名'][self.Cultivar['Language Code'] == code].tolist()
					combo_variety['values'] = sorted(set(variety),key=variety.index)
					combo_variety.current(combo_variety['values'].index(edit_Variety.get()))
			counter += 1

		tk.Button(self.editmap_win, text=self.interface['edit']['submit'], width=7, command=edit_submit).place(x=500,y=250)


	# 儲存茶區資訊
	def save_mapinfo(self, info):
		with open('CropVISTMapInfo.txt', 'w', encoding='utf-8') as w:
			note = []
			EW_Location = ', '.join(map(str,info[2:5]))
			NS_Location = ', '.join(map(str,info[6:9]))
			lon = 'E' if info[1] == '東經' else 'W'
			lat = 'N' if info[5] == '北緯' else 'S'
			Location = '%s, %s, %s, %s' % (EW_Location,lon,NS_Location,lat)
			EW_direction = info[13]
			NS_direction = info[14]
			Internal_code = info[0]
			note.append('CropVISTMapInfo  V1.1')
			note.append('Main Working Directory = \\CropPlantationInfo')
			note.append('Output Directory = .\\Photo\\TempFile')
			note.append('Center Location = '+Location)
			note.append('N-S Direction = '+str(NS_direction))
			note.append('E-W Direction = '+str(EW_direction))
			note.append('Internal Code = '+Internal_code)
			w.write('\n'.join(note))

		with open('SuppliedInfo.txt', 'w', encoding='utf-8') as w:
			note = []
			note.append('Supplied Info for Answers of ES')
			note.append('Expert System = Tea')
			note.append('Directory of CSV Files = .\\Dataset\\')
			note.append('Internal Code = '+Internal_code)
			note.append('Output Directory = .\\Temp')
			w.write('\n'.join(note))

		with open('TeaRegionLoading.txt','w',encoding='utf-8') as w:
			w.write('country = '+info[9]+'\n')
			w.write('region = '+info[10])

		self.hidden_node_answer()
		self.field_win.destroy()
		self.siteva.destroy()

		# callback of optionlist
		optionlist(self.language).main()


	# 呼叫"NodeAnswer.exe"程式
	def hidden_node_answer(self):
		process = subprocess.run('NodeAnswer.exe',shell=True)


# if __name__ == '__main__':
# 	a = SiteEvaLogin(2)
# 	a.main()
