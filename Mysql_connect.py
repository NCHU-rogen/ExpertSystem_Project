#!usr/bin/python3g
# Coding: utf-8
# Author: Rogen
# Description: MySQL資料庫連結


# from datetime import datetime
from sqlalchemy import create_engine
from tkinter import messagebox
from GUI_language import *
import pymysql
import pandas as pd
import json
import re, os, sys
import csv, glob
import shutil
import tkinter as tk


class mysql(object):
	# 全域變數宣告
	global _anchor_code
	_anchor_code = {}

	def __init__(self,ver):
		super(mysql,self).__init__()
		self.var_list = []
		self.workpath = os.getcwd().replace('\\','/')
		self.language = ver
		# self.window = window

		if self.language == 1:
			ch = Chinese()
			self.interface = ch.SiteEva_Login_Interface()
		else:
			en = English()
			self.interface = en.SiteEva_Login_Interface()


	# 資料庫連接
	def initiate(self):
		try:
			# self.db = pymysql.connect(host=self.host.get(),port=int(self.port.get()),user=self.account.get(),password=self.pw.get(),charset='UTF8MB4',local_infile=True,connect_timeout=120)
			self.db = pymysql.connect(host=self.host.get(), port=int(self.port.get()), user=self.account.get(), password=self.pw.get(), charset='UTF8MB4', local_infile=True)
			self.cursor = self.db.cursor()
			# self.cursor.execute("GRANT ALL PRIVILEGES on *.* to 'root'@'127.0.0.1' identified by 'thinkive';")
			# self.cursor.execute("flush privileges")
			return(1)

		except Exception as e:
			messagebox.showerror('ERROR',e)
			return(0)


	# 資料庫連結關閉
	def close_conn(self):
		self.cursor.close()
		self.db.close()


	# 匯入資料庫
	def import_db(self, db, table, filename):
		self.cursor.execute("use %s" % db)
		try:
			import_tb = pd.read_csv(filename)
		except FileNotFoundError as e:
			messagebox.showerror('ERROR',e)

		importcsv_sql = "LOAD DATA LOCAL INFILE '%s' \
						REPLACE INTO TABLE %s \
						FIELDS TERMINATED BY ',' \
						LINES TERMINATED BY '\\r\\n' \
						IGNORE 1 ROWS \
						(%s);" % (filename, table, ','.join(list(import_tb.columns)).replace('(%)',''))

		self.cursor.execute(importcsv_sql)


	# 匯出資料庫
	def export_db(self, table, filename):
		if os.path.exists('%s/%s' % (self.workpath,filename)):
			os.remove('%s/%s' % (self.workpath,filename))

		exportcsv_sql = "SELECT * FROM %s" % table

		self.cursor.execute(exportcsv_sql)
		rows = self.cursor.fetchall()
		column_names = [i[0] for i in self.cursor.description]
		with open('%s' % filename, 'w', encoding='utf_8_sig') as f:
			output = csv.writer(f, lineterminator = '\n')
			output.writerow(column_names)
			output.writerows(rows)

	
 	# 創建資料庫
	def create_db(self):
		# self.cursor.execute("show databases;") 
		self.cursor.execute("CREATE DATABASE IF NOT EXISTS expert_system DEFAULT charset utf8mb4 COLLATE utf8mb4_general_ci;")
		# self.cursor.execute("ALTER DATABASE expert_system DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_general_ci;")
		self.cursor.execute("CREATE DATABASE IF NOT EXISTS fertilizer DEFAULT charset utf8mb4 COLLATE utf8mb4_general_ci;")
		# self.cursor.execute("ALTER DATABASE fertilizer DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_general_ci;")
		self.cursor.execute("CREATE DATABASE IF NOT EXISTS internal_code DEFAULT charset utf8mb4 COLLATE utf8mb4_general_ci;")
		# self.cursor.execute("ALTER DATABASE internal_code DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_general_ci;")


	# 創建代碼紀錄表
	def create_anchor(self):
		self.cursor.execute("use internal_code")
		sql = "CREATE TABLE IF NOT EXISTS anchor_code( \
				basecode VARCHAR(5) NOT NULL PRIMARY KEY, \
				serialcode VARCHAR(5) NOT NULL)"
		self.cursor.execute(sql)


	# 創建茶區登入表
	def create_siteva(self):
		self.cursor.execute("use expert_system;")
		sql = "CREATE TABLE IF NOT EXISTS sitevaluation( \
				Internal_Code VARCHAR(8) NOT NULL, \
				EW_Longitude VARCHAR(4) NOT NULL, \
				Longitude_Degree FLOAT(2) NOT NULL, \
				Longitude_Minute FLOAT(2) NOT NULL, \
				Longitude_Second FLOAT(2) NOT NULL, \
				NS_Latitude VARCHAR(4) NOT NULL, \
				Latitude_Degree FLOAT(2) NOT NULL, \
				Latitude_Minute FLOAT(2) NOT NULL, \
				Latitude_Second FLOAT(2) NOT NULL, \
				Country VARCHAR(20) NOT NULL, \
				Region VARCHAR(20) NOT NULL, \
				Name VARCHAR(8), \
				Phone VARCHAR(10), \
				EW_Field INT(4), \
				NS_Field INT(4), \
				Variety VARCHAR(8) NOT NULL, \
				Planting_Age INT(4), \
				Entry_Date DATE NOT NULL, \
				Surveyor VARCHAR(10) NOT NULL, \
				Latitude_TWD97 FLOAT(30) NOT NULL, \
				Longitude_TWD97 FLOAT(30) NOT NULL, \
				PRIMARY KEY (Internal_Code, Country, Region, Name));"
		self.cursor.execute(sql)


	# 創建施肥紀錄表
	def create_fert(self,internal_code):
		self.cursor.execute("use fertilizer;")
		sql = "CREATE TABLE IF NOT EXISTS %s( \
			Internal_Code VARCHAR(8) NOT NULL, \
			ID VARCHAR(20) PRIMARY KEY NOT NULL, \
			Item VARCHAR(30) NOT NULL, \
			Product VARCHAR(20) NOT NULL, \
			Amount INT(5) NOT NULL, \
			Aim VARCHAR(8) NOT NULL, \
			Frequency INT(5) NOT NULL, \
			N INT(5) NOT NULL, \
			P2O5 INT(5) NOT NULL, \
			K2O INT(5) NOT NULL, \
			CaO INT(5) NOT NULL, \
			MgO INT(5) NOT NULL, \
			OM INT(5) NOT NULL);" % internal_code
		self.cursor.execute(sql)


	# 創建灌溉紀錄表
	def create_water(self):
		self.cursor.execute("use expert_system;")
		sql = "CREATE TABLE IF NOT EXISTS watering( \
			Internal_Code VARCHAR(8) PRIMARY KEY NOT NULL, \
			Sprinkler_Density_W INT(10) NOT NULL, \
			Sprinkler_Density_H INT(10) NOT NULL, \
			Frequence VARCHAR(10) NOT NULL, \
			Amount INT(5) NOT NULL, \
			Electric_Bill_Year FLOAT(7), \
			Water_Bill_Year FLOAT(7), \
			Water_Bill_Degreed FLOAT(7));"
		self.cursor.execute(sql)


	# 創建土壤速測紀錄表
	def create_soils(self):
		self.cursor.execute("use expert_system;")
		sql = "CREATE TABLE IF NOT EXISTS soilstest( \
			Internal_Code VARCHAR(8) PRIMARY KEY NOT NULL, \
			T_Texture INT(5), \
			B_Texture INT(5), \
			T_BD_min FLOAT(7), \
			T_BD_max FLOAT(7), \
			B_BD_min FLOAT(7), \
			B_BD_max FLOAT(7), \
			SDepth_min FLOAT(7), \
			SDepth_max FLOAT(7), \
			CDepth_min FLOAT(7), \
			CDepth_max FLOAT(7), \
			MDepth_min FLOAT(7), \
			MDepth_max FLOAT(7), \
			pH_min FLOAT(7), \
			pH_max FLOAT(7), \
			EC_min FLOAT(7), \
			EC_max FLOAT(7), \
			OM_min FLOAT(7), \
			OM_max FLOAT(7), \
			NO3_min FLOAT(7), \
			NO3_max FLOAT(7), \
			PO4_min FLOAT(7), \
			PO4_max FLOAT(7), \
			K_min FLOAT(7), \
			K_max FLOAT(7), \
			Ca_min FLOAT(7), \
			Ca_max FLOAT(7));"
		self.cursor.execute(sql)


	# 匯出茶區登入表格
	def export_siteva(self):
		self.cursor.execute("use expert_system")
		self.export_db('sitevaluation', './Dataset/SiteEva_Table.csv')

		# self.cursor.execute("use expert_system")
		# # exportcsv_sql = "SELECT 'Internal_Code','EW_Longitude','Longitude_Degree','Longitude_Minute','Longitude_Second', \
		# # 				'NS_Latitude','Latitude_Degree','Latitude_Minute','Latitude_Second', \
		# # 				'Country','Region','Name','Phone','EW_Field','NS_Field','Variety', \
		# # 				'Planting_Age','Entry_Date','Surveyor','Latitude_TWD97','Longitude_TWD97' \
		# # 				UNION ALL \
		# # 				SELECT * FROM sitevaluation \
		# # 				INTO OUTFILE 'SiteEva_Table.csv' \
		# # 				FIELDS TERMINATED BY ',' \
		# # 				LINES TERMINATED BY '\\r\\n';"

		# exportcsv_sql = "SELECT * FROM sitevaluation"

		# if os.path.exists('%s/SiteEva_Table.csv' % self.workpath):
		# 	os.remove('%s/SiteEva_Table.csv' % self.workpath)

		# self.cursor.execute(exportcsv_sql)
		# rows = self.cursor.fetchall()
		# column_names = [i[0] for i in self.cursor.description]
		# with open('SiteEva_Table.csv', 'w', encoding='utf_8_sig') as f:
		# 	output = csv.writer(f, lineterminator = '\n')
		# 	output.writerow(column_names)
		# 	output.writerows(rows)


	# 匯出灌溉紀錄表格
	def export_water(self):
		self.cursor.execute("use expert_system")
		self.export_db('watering', './Dataset/Planting_Water.csv')


	# 匯出土壤速測紀錄表格
	def export_soilstest(self):
		self.cursor.execute("use expert_system")
		self.export_db('soilstest', './Dataset/Soils_Test.csv')


	# 匯出施肥紀錄表格
	def export_fert(self):
		self.cursor.execute("use fertilizer")
		self.cursor.execute("show tables")
		tables = self.cursor.fetchall()		# Return data from last query
		for t in tables:
			t = t[0]						# t is a tuple format
			self.export_db(t, './Dataset/Planting_Fertilizer_%s.csv' % t.replace('_','-'))


	# 匯出資料編碼紀錄表格
	def export_anchor(self):
		mydict = {}
		self.cursor.execute("use internal_code")
		self.cursor.execute("select * from anchor_code")
		data = self.cursor.fetchall()
		for d in data: 
			mydict[d[0]] = d[1]
		if len(data):						# We updated anchor code to a json file when data was uploaded in second or more times.
			print(111)
			with open('Code_Recode.json','w') as w:
				js = json.dumps(mydict)
				w.write(js)


	# 匯入茶區登入表格
	def import_siteva(self):
		self.import_db('expert_system', 'sitevaluation', './Dataset/SiteEva_Table_Update.csv')
		self.db.commit()
		os.remove('./Dataset/SiteEva_Table_Update.csv')

		# select_sql = "SELECT Internal_Code, Entry_Date from sitevaluation;"

		# self.cursor.execute(select_sql)
		# select_tb = self.cursor.fetchall()
		# select_tb = pd.DataFrame(list(select_tb), columns=['Internal_Code','Entry_Date'])
		# select_tb['Entry_Date'] = select_tb['Entry_Date'].apply(lambda x:x.strftime('%Y-%m-%d'))		#datetime2str

		# with open('tmp-siteva_table.csv', 'w+', encoding='utf_8_sig') as w:
		# 	w.write(','.join(list(import_tb.columns))+'\n')

		# 	for i in range(len(import_tb.index)):
		# 		bool_IC = select_tb.index[(select_tb['Internal_Code'] == import_tb['Internal_Code'][i])]
		# 		bool_ED = select_tb.index[(select_tb['Entry_Date'] == import_tb['Entry_Date'][i])]
		# 		cross_idx = list(set(bool_IC).intersection(bool_ED))

		# 		if len(cross_idx) == 0:
		# 			w.write(','.join(map(str,import_tb.iloc[i,:].to_list()))+'\n')


	# 匯入施肥紀錄表格
	def import_fert(self):
		results = glob.glob('./Dataset/Planting_Fertilizer_*.csv')
		for r in results:
			r = r.replace('\\','/')
			table = re.search(r'Fertilizer_(.+)\.csv',r).group(1)
			table = table.replace('-','_')
			self.create_fert(table)
			self.cursor.execute("truncate table %s" % table)
			filename = self.edit_anchor(r)
			self.import_db('fertilizer', table, filename)
			os.remove(filename)
		self.db.commit()


	# 匯入灌溉紀錄表格
	def import_water(self):
		filename = self.edit_anchor('./Dataset/Planting_water.csv')
		self.import_db('expert_system','watering',filename)
		self.db.commit()
		os.remove(filename)


	# 匯入土壤速測表格
	def import_soils(self):
		filename = self.edit_anchor('./Dataset/Soils_Test.csv')
		self.import_db('expert_system', 'soilstest', filename)
		self.db.commit()
		os.remove(filename)


	# 匯入資料碼號紀錄表格
	def import_anchor(self):
		if not len(self.code_recode):			# We read the anchor code from a json file when data was uploaded in first times.
			with open('Code_Recode.json','r') as r:
				self.code_recode = json.loads(r.readline())

		with open('anchor_code.csv','w+') as w:
			w.write('basecode,serialcode\n')
			for key in sorted(self.code_recode.keys()):
				w.write('%s,%s\n'%(key,self.code_recode[key]))

		self.import_db('internal_code','anchor_code','anchor_code.csv')
		self.db.commit()
		os.remove('anchor_code.csv')


	# 修改匯入資料的編號
	def edit_anchor(self, filename):
		df = pd.read_csv(filename)
		codes = df.Internal_Code.tolist()
		for code in codes:
			try:
				serial = _anchor_code[code]
				idx = df.index[df.Internal_Code == code]
				df.loc[idx,'Internal_Code'] = serial
			except Exception as e:
				pass
		filename = filename.replace('.csv','_Update.csv')
		df.to_csv(filename,index=False)
		return(filename)

			
	# 檢查資料庫連線資料是否填寫
	def button_check(self,event):
		flag = 0
		for var in self.var_list:
			if var.get() == '':
				flag += 1

		if flag == 0:
			self.up_button.config(state=tk.ACTIVE)
			self.down_button.config(state=tk.ACTIVE)
		else:
			self.up_button.config(state=tk.DISABLED)
			self.down_button.config(state=tk.DISABLED)


	# 重排茶區上傳資料代碼
	def code_rearrange(self):
		self.code_recode = {}
		es_con = 'mysql+pymysql://%s:%s@%s:%s/expert_system?charset=utf8' % (self.host.get(),self.pw.get(),self.host.get(),self.port.get())
		code_con = 'mysql+pymysql://%s:%s@%s:%s/internal_code?charset=utf8' % (self.host.get(),self.pw.get(),self.host.get(),self.port.get())
		code_sql = "select *from anchor_code"
		db_sql = "select * from sitevaluation"
		pc_df = pd.read_csv('./Dataset/SiteEva_Table.csv', header=0)
		db_df = pd.read_sql(db_sql, con=create_engine(es_con))

		# The second or more times upload
		if len(db_df) > 0:
			code_df = pd.read_sql(code_sql, con=create_engine(code_con))
			if len(code_df):
				for c in range(len(code_df)):
					self.code_recode[code_df.iloc[c,0]] = code_df.iloc[c,1]

			for i in pc_df.Internal_Code.tolist():
				sp_internal_code = i.split('-')
				basecode = sp_internal_code[0]

				df_idx = db_df.index[db_df.Internal_Code == i]
				pc_idx = pc_df.index[pc_df.Internal_Code == i]

				if len(df_idx):
					if db_df.loc[df_idx,'Name'].tolist()[0] != pc_df.loc[pc_idx,'Name'].tolist()[0] or \
						db_df.loc[df_idx,'Country'].tolist()[0] != pc_df.loc[pc_idx,'Country'].tolist()[0] or \
						db_df.loc[df_idx,'Region'].tolist()[0] != pc_df.loc[pc_idx,'Region'].tolist()[0]:
						
						serialnumber = self.code_recode[basecode]
						serialnumber = self.serial_code(serialnumber, func='plus')
						pc_df.loc[pc_idx,'Internal_Code'] = '-'.join([basecode, serialnumber])
						self.code_recode[basecode] = serialnumber
						_anchor_code[i] = '-'.join([basecode, serialnumber])

		pc_df.to_csv('./Dataset/SiteEva_Table_Update.csv',encoding='utf_8_sig',index=False)


	# 筆電資料上傳至資料庫
	def upload(self):
		e = self.initiate()
		if e == 1:	
			try:
				self.create_db()			# Create expert_system & fertilizer database
				self.create_siteva()		# Create site evaluation table
				self.create_water()			# Create plant watering table
				self.create_soils()			# Create soil's test table
				self.create_anchor()		# Create internal_code table
				self.code_rearrange()
				self.import_water()			# Import plant watering 
				self.import_siteva()		# Import site evaluation
				self.import_soils()			# Import soil's test
				self.import_fert()			# Create and import fertilizer table
				self.import_anchor()		# Import soil's test
				messagebox.showinfo('INFO',self.interface['db_connect']['ul_success'])
				# self.root.destroy()
			except Exception as e:
				messagebox.showerror('ERROR','%s\n%s' % (e,self.interface['db_connect']['ul_failure']))
			self.close_conn()


	# 資料庫資料下載至筆電
	def download(self):
		e = self.initiate()
		if e == 1:
			try:
				self.export_siteva()		# Download evaluation table of tea plantation
				self.export_fert()			# Download fertilizer table
				self.export_water()			# Download watering table
				self.export_soilstest()		# Download soil physicochemical tesing table
				self.export_anchor()		# Download internal_code table
				messagebox.showinfo('INFO',self.interface['db_connect']['dl_success'])
				# self.root.destroy()
			except Exception as e:
				messagebox.showerror('ERROR','%s\n%s' % (e,self.interface['db_connect']['dl_failure']))
			self.close_conn()


	# 主程式介面
	def sqlmain(self,window):
		self.root = tk.Toplevel(window)
		self.root.geometry('300x200')
		self.root.title(self.interface['db_connect']['title'])
		self.root.resizable(width=False,height=False)

		# self.host = tk.StringVar(value='140.120.203.66')
		# self.port = tk.IntVar(value=3306)
		# self.account = tk.StringVar(value='root')
		# self.pw = tk.StringVar(value='0000')

		self.host = tk.StringVar()
		self.port = tk.StringVar()
		self.account = tk.StringVar()
		self.pw = tk.StringVar()
		self.var_list = [self.host,self.port,self.account,self.pw]

		main_LF = tk.LabelFrame(self.root,text=self.interface['db_connect']['server_info'],fg='blue')
		main_LF.place(x=20,y=15,width=250,height=120)

		tk.Label(main_LF,text=self.interface['db_connect']['host']).grid(row=0,column=0,padx=2,pady=2,sticky=tk.E)
		tk.Label(main_LF,text=self.interface['db_connect']['port']).grid(row=1,column=0,padx=2,pady=2,sticky=tk.E)
		tk.Label(main_LF,text=self.interface['db_connect']['account']).grid(row=2,column=0,padx=2,pady=2,sticky=tk.E)
		tk.Label(main_LF,text=self.interface['db_connect']['pw']).grid(row=3,column=0,padx=2,pady=2,sticky=tk.E)

		for v in range(len(self.var_list)):
			c = tk.Entry(main_LF,textvariable=self.var_list[v],width=20)
			c.grid(row=v,column=1,padx=2,pady=2)
			c.bind("<KeyRelease>",self.button_check)

		button_L = tk.Label(self.root)
		button_L.place(x=65,y=150)

		self.up_button = tk.Button(button_L,text=self.interface['db_connect']['upload'],width=9,command=self.upload,state=tk.DISABLED)
		self.up_button.grid(row=0,column=0,padx=5)
		self.down_button = tk.Button(button_L,text=self.interface['db_connect']['download'],width=9,command=self.download,state=tk.DISABLED)
		self.down_button.grid(row=0,column=2,padx=5)


