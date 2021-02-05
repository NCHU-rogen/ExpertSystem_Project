#!/usr/bin/python3
# Coding: utf-8
# Author: Rogen
# Description: 專家系統功能集


from os import walk
from tkinter import *
from PIL import ImageTk, Image
from tkinter import ttk, messagebox, font, filedialog
from tkintertable.TableModels import TableModel
from tkintertable.Tables import TableCanvas
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from GUI_language import *
from Table4Results import TkSheet
from openpyxl import load_workbook
import matplotlib.pyplot as plt
import matplotlib.backends._tkagg
import pandas as pd
import graphviz as gz
import os, re, subprocess, csv, shutil


class RuleStruct(object):
	"""docstring for RuleStruct"""
	def __init__(self, sheet_name='SiteEvaluation'):
		os.environ["PATH"] += os.pathsep + './Graphviz2.38/bin/'
		self.rules_database_path = './Diagnosis_Rules.xlsm'
		self.rule_srtucture_graph = './RuleGraph/'
		self.dataset_path = './Dataset/'
		self.sheet_name = sheet_name
		self.all_diagnosis = []
		self.OpenRuleFile()


	# 讀取規則庫excel
	def OpenRuleFile(self):
		rule_counter = 0
		del_nodes = []
		self.subtitle = {}
		self.subtitle[1] = {}		# Storage chinese subtitle
		self.subtitle[2] = {}		# Storage english subtitle
		self.df = pd.read_excel(self.rules_database_path, header=0, sheet_name=self.sheet_name, encoding='utf_8_sig', 
			converters = {'Rule':str, 'Node':int, 'Question':str, 'Yes':str, 'No':str, 'Unknown':str, 'Pictures':str})
		self.rulebase_list = pd.ExcelFile(self.rules_database_path).sheet_names

		for rule_num in map(str, self.df.iloc[:, 0]):					# Rule column
			if re.search(r'Main Branch', rule_num):
				del_nodes.append(rule_counter)
				sp_rule_num = rule_num.split(': ')
				en_subtitle = sp_rule_num[1]
				ch_subtitle = self.df.iloc[rule_counter,9]				# Chinese question column
			elif rule_num == 'nan':
				del_nodes.append(rule_counter)
			else:
				self.subtitle[1][self.df.Node[rule_counter]] = ch_subtitle
				self.subtitle[2][self.df.Node[rule_counter]] = en_subtitle
			rule_counter += 1

		self.df.drop(del_nodes, inplace=True)
		self.df.reset_index(drop=True, inplace=True)


	# 規則關係圖形化 (會搭配Graphviz2.38套件來畫圖，只會在新增、篩除、修改規則時使用)
	def __graph__(self, master):
		def senten_cut(sentence):
			line = []
			temp = []
			count = 1
			senten = ''
			sp_sen = sentence.split(' ')
			for word in sp_sen:
				if count == len(sp_sen):
					temp.append(word)
					line.append(' '.join(temp))
					senten = '\n'.join(line)
				elif count % 6 != 0:
					temp.append(word)
				else:
					line.append(' '.join(temp))
					temp = []
					temp.append(word)
				count += 1
			return(senten)


		# 規則關係圖x、y軸
		def scrolled_canvas(frame):
			w,h = frame.maxsize()
			frame.title('Rule Structure Graph')
			canv = Canvas(frame, relief=SUNKEN)
			sbarV = Scrollbar(frame, orient=VERTICAL, command=canv.yview)
			sbarH = Scrollbar(frame, orient=HORIZONTAL, command=canv.xview)
			
			im = Image.open(self.rule_srtucture_graph + 'Graph.png')
			im = ExpertSystemFunctions(1,self.sheet_name).image_resize(im, w)
			im2 = ImageTk.PhotoImage(im)
			width,height = self.im.size
			canv.config(scrollregion=(0,0,width,height), width=width, height=height, yscrollcommand=sbarV.set, xscrollcommand=sbarH.set, highlightthickness=0)
			canv.create_image(0,0,anchor="nw",image=im2)

			sbarV.pack(side=RIGHT, fill=Y)
			sbarH.pack(side=BOTTOM, fill=X)
			canv.pack(side=LEFT, expand=YES, fill=BOTH)

		dot = gz.Digraph()
		for row in range(len(self.df.index)):
			l = self.df.iloc[row].tolist()
			dot.node(str(l[1]), senten_cut(str(l[1])+': '+l[2])) # Original_Node

			if str(l[3]) == 'nan' or str(l[4]) == 'nan':
				pass
			else:
				l[3] = l[3].replace('#','')
				l[4] = l[4].replace('#','')

				if re.search(r'\d+:.+', l[3]): # Yes_Node
					sp_ = l[3].split(':')
					dot.node(sp_[0], senten_cut(l[3]))
					dot.edge(str(l[1]), sp_[0], label='yes')
				else:
					dot.edge(str(l[1]), l[3], label='yes')

				if re.search(r'\d+:.+', l[4]): # No_Node
					sp_ = l[4].split(':')
					dot.node(sp_[0], senten_cut(l[4]))
					dot.edge(str(l[1]), sp_[0], label='No')
				else:
					dot.edge(str(l[1]), l[4], label='No')

		dot.render(self.rule_srtucture_graph + 'Graph', format='png')
		# dot.view('test')
		self.rule_win = Toplevel(master)
		scrolled_canvas(self.rule_win)


	# 診斷結果表格顯示
	def __table__(self, master):
		try:
			if self.rule_win.state() == 'normal':
				pass
		except:
			data = {}
			colnums = ['Rule','Node','Question','Yes','No']
			rule_dict = self.df.ix[:,'Rule':'No']

			for r in range(len(rule_dict.index)):
				plice = {}
				for c in range(len(rule_dict.columns)):
					if rule_dict.iloc[r,c] == 'nan':
						plice[rule_dict.columns[c]] = ' '
					else:
						plice[rule_dict.columns[c]] = rule_dict.iloc[r,c]
				data[str(r)] = plice

			self.rule_win = Toplevel(master)
			frame = Frame(self.rule_win)
			frame.pack()
			model = TableModel()

			for key in colnums:
				model.addColumn(key) #sort the columns

			model.importDict(data)
			table = TableCanvas(frame, model=model, width=800, height=500, rowheight=20, editable=False, cellbackgr='#E3F6CE', reverseorder=1, rowselectedcolor='yellow')
			table.createTableFrame()
			table.sortTable(columnName='Rule')


	def __destroy__(self):
		try:
			if self.rule_win.state() == 'normal':
				self.rule_win.destroy()
		except:
			pass


class ExpertSystemFunctions(RuleStruct):
	# 全域變數宣告
	global _rulebase_diagnosis_recode, _rulebase_diagnosis_done, _answer_dict
	_rulebase_diagnosis_recode = {}
	_rulebase_diagnosis_done = []
	_answer_dict = {}

	def __init__(self, ver, sheet_name, code):
		super(ExpertSystemFunctions, self).__init__(sheet_name)
		self.sheet_name = sheet_name
		self.language = ver
		self.internal_code = code
		self.answer_store = {}
		self.answer_diagnosis = ''
		self.query = ''
		self.Yes_score = 0
		self.No_score = 0
		self.tree_iterater = 0
		self.optiontree_iterater = 0
		self.photo_image_counter = 0
		self.note_pointer = 0
		self.save_path = '.\\Save'
		self.photo_path = '.\\Photo\\' + self.sheet_name
		self.photo_temp = '.\\Photo\\TempFile'
		self.image_nonavailable = '.\\Photo\\Interface\\img_not_available.png'
		self.hidden_answer = '.\\Temp\\Answers.TXT'
		self.GuiInitiation()


	# 專家系統啟動前超參數設定
	def GuiInitiation(self):
		if self.language == 1:
			ch = Chinese()
			self.interface = ch.ES_GUI_Interface()
			self.Q_list = self.df.中文問題

		elif self.language == 2:
			en = English()

			self.interface = en.ES_GUI_Interface()
			self.Q_list = self.df.Question

		self.cur_node = self.df.Node[0]
		self.query = self.Q_list[0]


	# 專家系統離開設定
	def GuiClose(self):
		# Update the SiteEva_Table.csv
		self.siteval_df = pd.read_csv('./Dataset/SiteEva_Table.csv')
		with open('CropVISTMapInfo.txt','r',encoding='utf-8') as file:
			lines = file.readlines()

		inter_code = lines[6].split(r' = ')[1].replace('\n','')
		index = self.siteval_df.index[self.siteval_df['Internal_Code'] == inter_code]

		center_location = re.split(r'[,|=| ]+',lines[3])
		NS_direction = lines[4].split(' = ')[1].replace('\n','')
		EW_direction = lines[5].split(' = ')[1].replace('\n','')
		self.siteval_df.iloc[index,2:5] = center_location[2:5]
		self.siteval_df.iloc[index,6:9] = center_location[6:9]
		self.siteval_df.iloc[index,13:15] = [EW_direction,NS_direction]
		self.siteval_df.to_csv('./Dataset/SiteEva_Table.csv', index=False, encoding='utf_8_sig')
		print(center_location,EW_direction,NS_direction,inter_code)

		# Delete the figures of TempFile folder 
		for root, dirs, files in walk(self.photo_temp):
			for f in files:
				fullpath = os.path.join(root,f)
				if os.path.isfile(fullpath):
					os.remove(fullpath)

		# Delete the diagnosed csv files
		for root, dirs, files in walk(self.save_path):
			for f in files:
				fullpath = os.path.join(root,f)
				if os.path.isfile(fullpath) and re.search(r'.+_Diagnosis\.csv', f):
					os.remove(fullpath)

		# Listing the full diagnosed results of rulebases into excel file
		# self.diagnosis_export()


	#---------- Photograph Controled Area ----------#
	# 第一張圖片設定
	def pri_photo(self):
		if str(self.df.Pictures[0]) == 'nan':
			self.photo_images = [self.image_nonavailable]
		else:
			priphoto_folder = os.path.join(self.photo_path, self.df.Pictures[0])
			exist = self.node_folder_exist(priphoto_folder)
			if exist:
				self.photo_images = [os.path.join(priphoto_folder, _) for _ in os.listdir(priphoto_folder)]
				if len(self.photo_images) == 0:
					self.photo_images = [self.image_nonavailable]
			else:
				self.photo_images = [self.image_nonavailable]

		self.im = Image.open(self.photo_images[0])
		image_file = ImageTk.PhotoImage(self.image_resize(self.im))
		self.figure_title(self.photo_images[0])

		return(image_file)


	# 專家系統第一張圖片設定
	def figure_iterator(self,state):
		if len(self.photo_images) < 2:
			pass
		else:
			if state == 'forward' and self.photo_image_counter < len(self.photo_images)-1:
				self.photo_image_counter += 1
			elif state == 'back' and self.photo_image_counter > 0:
				self.photo_image_counter -= 1

			self.im = Image.open(self.photo_images[self.photo_image_counter])
			self.iterative_image = ImageTk.PhotoImage(self.image_resize(self.im))

			self.fig_label.config(image=self.iterative_image)
			self.fig_label.update_idletasks()
			self.figure_title(self.photo_images[self.photo_image_counter])


	# 下一張圖片
	def next_figure(self):
		self.photo_image_counter = 0
		self.photo_folder = self.df.Pictures[self.df.Node == self.cur_node].tolist()[0]
		
		if str(self.photo_folder) == 'nan':
			self.photo_images = [self.image_nonavailable]
		else:
			self.photo_fullpath = os.path.join(self.photo_path, self.photo_folder)
			if re.match(r'^N\d\d$',self.photo_folder):
				try:
					self.temp_path = os.path.join(self.photo_temp, self.photo_folder)
					self.photo_images = [os.path.join(self.temp_path, _) for _ in os.listdir(self.temp_path)]
				except FileNotFoundError as e:
					self.photo_images = ''
			else:
				exist = self.node_folder_exist(self.photo_fullpath)
				if exist:
					self.photo_images = [os.path.join(self.photo_fullpath, _) for _ in os.listdir(self.photo_fullpath)]
				else:
					self.photo_images = [self.image_nonavailable]

		# If the node's folder exists, there are no picture in folder
		if len(self.photo_images) == 0:
			self.photo_images = [self.image_nonavailable]

		self.im = Image.open(self.photo_images[0])
		self.next_image = ImageTk.PhotoImage(self.image_resize(self.im))

		self.fig_label.config(image=self.next_image)
		self.fig_label.update_idletasks()
		self.figure_title(self.photo_images[0])


	# 圖片控制(放大、截圖、移動等)
	def figure_magnification(self, image):
		# Setting figure size and quality
		f = Figure(figsize=(5,3), dpi=150)
		a = f.add_subplot(111)

		# Plotting figure
		# img_arr = matplotlib.image.imread('figure path')
		a.imshow(image)
		a.axis('off')
		a.axes.get_xaxis().set_visible(False)
		a.axes.get_yaxis().set_visible(False)

		# Display the graphics on the tkinter window
		canvas = FigureCanvasTkAgg(f, master=self.photo_win)
		canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=1)

		# Putting the toolbar of matplotlib graphics on the tkinter window
		toolbar = NavigationToolbar2Tk(canvas, self.photo_win)
		toolbar.update()
		canvas._tkcanvas.pack(side=BOTTOM, fill=BOTH, expand=True)


	# 判斷資料夾是否存在
	def node_folder_exist(self, path):
		result = 1 if os.path.exists(path) else 0
		return(result)


	# 圖像尺寸縮放
	def image_resize(self, image):
		w, h = image.size
		f1 = self.label_width/w
		f2 = self.label_height/h
		factor = min([f1, f2])
		width = int(w*factor)
		height = int(h*factor)
		return(image.resize((width, height), Image.ANTIALIAS))


	#---------- Query Controled Area ----------#
	# 圖片路徑
	def figure_title(self,name):
		self.figframe.config(text=name)


	# 問題標題
	def query_title(self,note):
		def branch(n):
			return(self.subtitle[self.language][n])

		if len(str(note)) == 1: 	#main branch
			return(branch(note))
		else:						#secondary branch
			m = int(re.match(r'^(\d)',str(note)).group(0))
			main_branch = branch(m)
			sec_branch = branch(note)

			if sec_branch == '':
				return(main_branch)
			else:
				return('%s-%s' % (main_branch,sec_branch))


	# 初始診斷問題
	def pri_query(self):
		self.unknown_button_control(self.cur_node)

		# The node is been hidden
		if str(self.df.Hidden_Answer[self.df.Node == self.cur_node].tolist()[0]) != 'nan':
			ans, error = self.note_hidden(0)
			if error == 0:		# Hidden node have answer
				self.user_answer.set(ans)
				self.next_step()
			else:				# Hidden node don't have answer, but user loaded previous study
				self.loading_answer()

		# The node isn't been hidden
		else:
			self.loading_answer()


	# 上一步
	def back_step(self):
		array = [k for k in sorted(self.answer_store.keys()) if int(k) % 100 != 0]

		self.cur_node = int(array[-1])
		self.next_node = self.cur_node
		self.query = self.answer_store[str(self.cur_node)][1]
		self.querylabel.config(text=self.query)
		del self.answer_store[str(self.cur_node)]		# delete the current node
		self.next_figure()
		self.figure_descript()
		self.query_descript()

		# Button crontrol
		self.r1.config(state=ACTIVE)
		self.r2.config(state=ACTIVE)
		self.next_button.config(state=ACTIVE)
		self.submit_button.config(state=DISABLED)
		self.unknown_button_control(self.cur_node)
		
		self.note_pointer -= 1
		if self.note_pointer == 0:
			self.back_button.config(state=DISABLED)

		try:
			if self.rulepath_win.state() == 'normal':
				self.option_record('onebyone',-1)		# Delete one answer of rule path
		except:
			pass


	#---- Record the current note info and give next note ----#
	# 下一步
	def next_step(self):
		yesScore = '-'; noScore = '-'; diag = '-'

		if self.user_answer.get() == 'None':
			messagebox.showerror('ERROR', 'The option is empty!')
		else:
			curIdx = self.df.index[self.df.Node == self.cur_node].tolist()[0]

			# Cumulative yes/no score
			if self.user_answer.get() == 'yes':
				self.next_node = self.df.Yes[curIdx]

				if str(self.df.Yes診斷[curIdx]) != 'nan':
					if self.language == 1:
						diag = self.df.Yes診斷[curIdx]
					elif self.language == 2:
						# If the english version of diagnosis is presented, it will be changed...
						diag = self.df.Yes診斷[curIdx]

				if str(self.df.Yes_score[curIdx]) != 'nan':
					self.Yes_score += self.df.Yes_score[curIdx]
					yesScore = self.df.Yes_score[curIdx]
				
			elif self.user_answer.get() == 'no':
				self.next_node = self.df.No[curIdx]

				if str(self.df.No診斷[curIdx]) != 'nan':
					if self.language == 1:
						diag = self.df.No診斷[curIdx]
					elif self.language == 2:
						# If the english version of diagnosis is presented, it will be changed...
						diag = self.df.No診斷[curIdx]

				if str(self.df.No_score[curIdx]) != 'nan':
					self.No_score += self.df.No_score[curIdx]
					noScore = self.df.No_score[curIdx]

			else:
				self.next_node = self.df.Unknown[curIdx]

			# Recode the solution way of each note 
			solution = '-' if str(self.df.處理對策[curIdx]) == 'nan' else self.df.處理對策[curIdx]
			diag = self.answer_diagnosis if self.answer_diagnosis != '' else diag
			
			self.answer_store[str(self.cur_node)] = [self.cur_node, self.query, str(self.user_answer.get()), yesScore, noScore, diag, solution]
			self.next_node = int(self.next_node.replace('#',''))

			# Button controled
			if self.next_node == 0:
				self.done()
			self.unknown_button_control(self.next_node)
			self.back_button.config(state=ACTIVE)
			self.analyze_button.config(state=DISABLED)

			try:
				if self.rulepath_win.state() == 'normal':
					self.option_record('onebyone',1)		# Inserting one rule in the rule path
			except:
				pass

			# the Order of code can not change!!!
			self.answer_diagnosis = ''
			self.next_query(curIdx)
			self.query_descript()
			self.figure_descript()
			self.note_pointer += 1


	#---- Goto the next query, and resetting the figures and buttons ----#
	# 下一個診斷問題
	def next_query(self, curIdx):
		next_node_idx = self.df.index[self.df.Node == self.next_node].tolist()[0]

		if str(self.Q_list[next_node_idx]) == 'nan':
			# Ending this section of all diagnosis
			self.querylabel.config(text=self.interface['diag_complete']['done'])
		else:
			# Hidden node find corresponding answer
			if str(self.df.Hidden_Answer[next_node_idx]) != 'nan':
				ans, error = self.note_hidden(next_node_idx)
				if error == 0:
					# Entry the chapter of diagnosis after hidden node
					if self.next_node % 100 == 0:
						self.diag_summary(next_node_idx)
					else:
						self.query = self.Q_list[next_node_idx]
						self.cur_node = self.df.Node[next_node_idx]
						self.user_answer.set(ans)
						self.next_step()

			# Error replace hidden node not find corresponding answer
			if str(self.df.Hidden_Answer[next_node_idx]) == 'nan' or error == 1:
				# Entry the chapter of diagnosis
				if self.next_node % 100 == 0:
					self.diag_summary(next_node_idx)
				else:
					self.cur_node = self.df.Node[next_node_idx]
					self.query = self.Q_list[next_node_idx]
					self.querylabel.config(text=self.query)

			querytitle = self.query_title(self.cur_node)
			self.queryframe.config(text=querytitle)
			self.user_answer.set(None)
			self.next_figure()
			self.loading_answer()


	# 診斷結束
	def done(self):
		self.submit_button.config(state=ACTIVE)
		self.next_button.config(state=DISABLED)
		self.r1.config(state=DISABLED)
		self.r2.config(state=DISABLED)
		self.r3.config(state=DISABLED)
		self.querylabel.config(text=self.interface['diag_complete']['done'])


	# "分析"按鈕控制
	def analyze_button_control(self, option):
		if option == 1 and self.sheet_name == 'SiteEvaluation' and (self.cur_node == 1101 or self.cur_node == 1201):
			self.analyze_button.config(state=ACTIVE)
			self.next_button.config(state=DISABLED)
		elif option == 2:
			self.analyze_button.config(state=DISABLED)
			self.next_button.config(state=ACTIVE)


	# "未知"按鈕控制		
	def unknown_button_control(self, note):
		if str(self.df.Unknown[self.df.Node == note].tolist()[0]) == 'nan':
			self.r3.config(state=DISABLED)
		else:
			self.r3.config(state=ACTIVE)


	# 診斷結果分數計算
	def diag_summary(self,next_node_idx):
		self.cur_node = self.df.Node[next_node_idx]
		self.query = self.Q_list[next_node_idx]

		if self.df.Yes_score[next_node_idx] != 0 and str(self.df.Yes_score[next_node_idx]) != 'nan':
			y = round(self.Yes_score*100/self.df.Yes_score[next_node_idx])
			y = [100 if y >= 100 else y][0]
		else:
			y = 0

		if self.df.No_score[next_node_idx] != 0 and str(self.df.No_score[next_node_idx]) != 'nan':
			n = round(self.No_score*100/self.df.No_score[next_node_idx])
			n = [100 if n >= 100 else n][0]
		else:
			n = 0

		self.Yes_score = 0
		self.No_score = 0
		self.answer_store[str(self.cur_node)] = [self.cur_node, self.query, '*', str(y)+'%', str(n)+'%', '-', '-']

		# It's end note, but it is deprecated
		if self.df.No[next_node_idx] == 'Max Possible' and str(self.df.Yes[next_node_idx]) == 'nan':
			self.done()

		elif self.df.No[next_node_idx] == 'Max Possible' and str(self.df.Yes[next_node_idx]) != 'nan':
			self.next_node = self.df.Yes[next_node_idx]
			self.next_node = int(self.next_node.replace('#',''))
			next_node_idx = self.df.index[self.df.Node == self.next_node].tolist()[0]

			# It's end note (#node:0)
			if self.df.Node[next_node_idx] == 0:
				self.done()
			else:
				if str(self.df.Hidden_Answer[next_node_idx]) != 'nan':
					ans, error = self.note_hidden(next_node_idx)
					if error == 0:
						self.cur_node = self.df.Node[next_node_idx]
						self.query = self.Q_list[next_node_idx]
						self.user_answer.set(ans)
						self.next_step()

				if str(self.df.Hidden_Answer[next_node_idx]) == 'nan' or error == 1:
					self.query = self.Q_list[next_node_idx]
					self.cur_node = self.df.Node[next_node_idx]
					self.querylabel.config(text=self.query)
					self.unknown_button_control(self.next_node)
					self.loading_answer()



	#---------- Output Controled Area ----------#
	# 儲存診斷結果
	def save_diagnosis(self):
		mode = 'a' if os.path.exists('%s/Diagnosis_%s.xlsx' % (self.save_path, self.internal_code)) else 'w'

		with pd.ExcelWriter('%s/Diagnosis_%s.xlsx' % (self.save_path, self.internal_code), engine='openpyxl', mode=mode) as writer:
			save_df = pd.read_csv('%s/%s_Diagnosis.csv' % (self.save_path, self.sheet_name), delimiter=",")
			save_df.to_excel(writer, sheet_name=self.sheet_name, index = None)
			writer.save()

		self.save.config(state=DISABLED)


	# 所有規則庫診斷結果匯出成一個CSV檔
	def diagnosis_export(self):
		# Export full rulebased diagnosis into csv file
		file = self.save_path+'/Diagnosis-Export.csv'
		flag = [True for f in os.listdir(self.save_path) if re.search('tmp-.+',f)]
		if not True in flag:
			messagebox.showinfo('ERROR','No any diagnosed output!')
		else:
			if os.path.exists(file):
				os.remove(file)
			with open(file, 'w+', encoding='utf_8_sig', newline='') as d:
				out_csv = csv.writer(d, quoting=csv.QUOTE_ALL)
				for i in self.rulebase_list:
					if os.path.exists(self.save_path+'/tmp-'+i):
						out_lines = [
							[self.interface['ruledb_name'][i]],
							['-'*50],
							[self.interface['done_title']['diagnosis'], self.interface['done_title']['yescore'], self.interface['done_title']['noscore']],
							['-'*50]
						]
						out_csv.writerows(out_lines)

						with open(self.save_path+'/tmp-'+i, 'r', encoding='utf_8_sig', newline='') as t:
							data = csv.reader(t, delimiter='\t')
							out_csv.writerows(data)
						out_csv.writerow(['_'*50])
						out_csv.writerow(['\n'*2])
						os.remove(self.save_path+'/tmp-'+i)

			# Including the "Diagnosis-Export" file into excel file
			# with pd.ExcelWriter('%s/Diagnosis_%s.xlsx' % (self.save_path, self.internal_code), engine='openpyxl', mode='a') as writer:
			# 	diagnosis_df = pd.read_csv(file, delimiter='\t')
			# 	diagnosis_df.to_excel(writer, sheet_name='Diagnosis-Export', index = None)
			# 	writer.save()
			# 	os.remove(file)

			messagebox.showinfo('INFO','Output have done.')


	# 診斷結果表格設置
	def diagnosis_done(self,tree):
		for key in sorted(self.answer_store.keys()):
			if self.answer_store[key][2] == '*' or len(key) == 1:
				branchs = 'main_branch' if len(key) == 1 else 'secondary_branch'
				tree.insert('',self.tree_iterater,values=['']*7)
				tree.insert('',self.tree_iterater+1,values=self.answer_store[key][:7],tags=(branchs,))
				self.tree_iterater += 2
			else:
				if self.answer_store[key][2] == 'no' or self.answer_store[key][2] == 'unknown':
					self.answer_store[key][6] = '-'
				tree.insert('',self.tree_iterater,values=self.answer_store[key][:7])
				self.tree_iterater += 1

		with open(self.save_path+'/tmp-'+self.sheet_name, 'w+', encoding='utf_8_sig') as f:
			tag = 0
			for key in sorted(self.answer_store.keys()):
				ans = self.answer_store[key]
				if ans[5] != '-':
					f.write('\t'.join(map(str,[ans[5],ans[3],ans[4]])) + '\n')
					tag = 1
				elif ans[2] == '*':
					# f.write('\n')
					f.write('\t'.join(map(str,[ans[1],ans[3],ans[4]])) + '\n')
					tag = 1
			if tag == 0:
				f.write(self.interface['done_unknown']['unknown'])
				f.write('\n')
 
		# Save diagnosis results in csv file
		with open(self.save_path+'/'+self.sheet_name+'_Diagnosis.csv', 'w', encoding='utf_8_sig', newline='') as out_csv:
			out_writer = csv.writer(out_csv, quoting=csv.QUOTE_ALL)
			out_writer.writerow(['Node','Question','Answer','Yes score','No score','Diagnosis','Solution'])
			for key in sorted(self.answer_store.keys()):
				out_writer.writerow(map(str,self.answer_store[key]))

		# Rulebase OptioinMenu Controled Area
		if self.sheet_name == 'SiteEvaluation':
			for i in range(len(self.rulebase_list)):
				s = ACTIVE if i == 1 else DISABLED
				self.next_rulebase['menu'].entryconfigure(i, state=s)

		elif self.sheet_name == 'Soils':
			for j in range(len(self.rulebase_list)):
				s = DISABLED if j <= 1 else ACTIVE
				self.next_rulebase['menu'].entryconfigure(j, state=s)

		else:
			for index in _rulebase_diagnosis_done+[0]:			# Adding "[0]" into list because the 'SiteEvaluate' rulebase does not include in list.  
				self.next_rulebase['menu'].entryconfigure(index, state=DISABLED)

		if len(_rulebase_diagnosis_done) == 4:
			self.submit.config(state=DISABLED)

		# Recodeing this diagosed results
		_rulebase_diagnosis_recode[self.sheet_name] = self.answer_store


	# 診斷結果表格(使用TkSheet外部套件設置，沒用到)
	def table4result(self):
		result = []; tag = []; i = 0
		for key in sorted(self.answer_store.keys()):
			if self.answer_store[key][2] == '*' or len(key) == 1:
				i+=1
				branchs = 'main_branch' if len(key) == 1 else 'secondary_branch'
				result.append(['']*7)
				tag.append([i,branchs])

			result.append(self.answer_store[key])
			i+=1

		ts = TkSheet(result, tag, self.interface)
		ts.mainloop()


	# 將儲存的結果用excel開啟 (方便使用者查閱)
	def open_csv_excel(self):
		os.startfile("%s/Save/%s_Diagnosis.csv" % (os.getcwd(),self.sheet_name))
		# command_line = 'C:/Program Files/Microsoft Office/root/Office16/EXCEL.EXE %s/Save/%s_Diagnosis.csv' % (os.getcwd(),self.sheet_name)
		# subprocess.Popen(command_line)


	# 給新增、刪除、修改規則使用 (沒用到)
	def diagnosis_node_index(self,index):
		No_Node = self.df.No.dropna().tolist()
		No_Node.remove('Max Possible')
		yesDiag = [i for i in self.df.Yes.dropna().tolist() if int(re.search(r'#(\d+)',i).group(1)) == index.get()]
		noDiag = [i for i in No_Node if int(re.search(r'#(\d+)',i).group(1)) == index.get()]
		return(yesDiag, noDiag)


	#---------- Other Controled Area ----------#
	# 紀錄使用者回答規則路徑
	def option_record(self, condiction, step=None):
		if condiction == 'showhand':
			count = 0
			for key in sorted(self.answer_store.keys()):
				if int(key) % 100 != 0:
					self.optiontree.insert('','end',values=self.answer_store[key][:3])
				else:
					count += 1
			self.optiontree_iterater = len(self.answer_store)-count
		else:
			if step == 1:
				if self.cur_node % 100 != 0:
					self.optiontree.insert('',self.optiontree_iterater,values=self.answer_store[str(self.cur_node)][:3])
					self.optiontree_iterater += 1
			else:
				tree_items = self.optiontree.get_children()
				self.optiontree.delete(tree_items[-1])
				self.optiontree_iterater -= 1


	# 處理規則中隱藏的節點，加速專家系統的診斷
	def note_hidden(self,note_index):
		note_hindden_error = 0
		negative_flag = 0
		answer = ''
		answer_list = {'Y':'yes','N':'no','U':'unknown'}
		opposite_answer = {'yes':'no','no':'yes','unknown':'unknown'}

		correspondence = self.df.Hidden_Answer[note_index]
		sp_correspondence = correspondence.split('-')

		if re.match('Answer', sp_correspondence[0]):
			csvfile = pd.read_csv(self.hidden_answer, delimiter=',')
			index = csvfile.index[csvfile['Q ID'] == int(sp_correspondence[1])].tolist()[0]
			answer = csvfile.iloc[index,3]
			answer = answer_list[answer]
			if re.match(r'[yes|no]',answer) and str(csvfile.iloc[index,4]) != 'nan':
				self.answer_diagnosis = csvfile.iloc[index,4]
		else:
			if re.match('Negative', sp_correspondence[0]):
				rulebase = sp_correspondence[0].split(' ')[1]
				negative_flag = 1
			else:
				rulebase = sp_correspondence[0]

			note = sp_correspondence[1]

			# If the note's answer don't recode in the base, progress must search in the dictionary of rulebase diagnosis
			if rulebase != self.sheet_name:
				dictionary = _rulebase_diagnosis_recode[rulebase]

				# To confirm whether the correspond answer exists in dictory or not
				try:
					answer = opposite_answer[dictionary[note][2]] if negative_flag == 1 else dictionary[note][2]
				except:
					note_hindden_error = 1
			else:
				try:
					answer = opposite_answer[self.answer_store[note][2]] if negative_flag == 1 else self.answer_store[note][2]
				except:
					note_hindden_error = 1

		return(answer, note_hindden_error)


	# 問題的原因描述
	def query_descript(self):
		self.query_desc_text.delete(1.0,END)
		texture = self.df.問題說明[self.next_node == self.df.Node].tolist()[0]
		if str(texture) == 'nan':
			self.query_desc_text.insert(1.0,'')
		else:
			self.query_desc_text.insert(1.0,texture)


	# 圖片的內容描述
	def figure_descript(self):
		self.fig_desc_text.delete(1.0,END)
		texture = self.df.圖片說明[self.next_node == self.df.Node].tolist()[0]
		if str(texture) == 'nan':
			self.fig_desc_text.insert(1.0,'')
		else:
			self.fig_desc_text.insert(1.0,texture)


	# 程序重啟動
	def program_restart(self):
		super().__destroy__()												# Destroy rule structure graph
		self.windows.destroy()												# Destroy main windows
		self.__init__(self.language, self.sheet_name, self.internal_code)	# To get the newest dataframe
		self.gui()


	# 下一個診斷規則庫
	def next_rulesbase_diag(self):
		sheet = self.rulebase.get()
		if sheet == '':
			messagebox.showwarning('WARNNING','You must choose one of rulebases!')
		else:
			_rulebase_diagnosis_done.append(self.rulebase_list.index(sheet))
			self.windows.destroy()											# Destroy windows must be the first step
			self.sheet_name = sheet
			self.__init__(self.language, self.sheet_name, self.internal_code)
			self.gui()


	# 外部程式連接 (UVA跟衛星影像圖分析程式)
	def external_link(self):
		if self.language == 1:
			CropVISTMapInfo = 'CropVISTMapInfoTWN.exe'
			UVA_Analysis = 'UAV_Analysis.exe'
		elif self.language == 2:
			CropVISTMapInfo = 'CropVISTMapInfoENG.exe'
			UVA_Analysis = 'UAV_Analysis.exe'

		exe = UVA_Analysis if str(self.cur_node) == '1101' else CropVISTMapInfo
		# p = subprocess.run(exe, shell=True)
		p = subprocess.call(exe, shell=True)

		# Checking progress does exist or not
		# command_line = 'TASKLIST', '/FI', 'imagename eq %s.exe' % exe
		# output = subprocess.check_output(command_line).decode()
		# last_line = output.strip().split('\r\n')[-1]
		# if not last_line.lower().startswith(exe.lower()):
		# 	self.program_restart()

		# Move figure of UVA/VIST to TempFile folder
		for f in os.listdir(self.photo_temp):
			if os.path.isfile(os.path.join(self.photo_temp,f)):
				findout = re.search(r'[NDVI|NDWI|SWC|\d+]_(\d)-(N\d+)',f)
				if findout:
					note_folder = findout.group(2)
					if not os.path.exists('%s/%s'% (self.photo_temp,note_folder)):
						os.mkdir('%s/%s'% (self.photo_temp,note_folder))
					shutil.move(os.path.join(self.photo_temp,f),os.path.join(self.photo_temp,note_folder,f))

		self.next_figure()
		self.next_button.config(state=ACTIVE)


	# 外部診斷結果匯入
	def save_import(self):
		temp = {}
		file = filedialog.askopenfilename(initialdir = "./Save", title='Select Input file', filetype=[("excel file","*.xls"),("excel file","*.xlsx")])
		xl = pd.ExcelFile(file)
		for sheet in xl.sheet_names:
			df = xl.parse(sheet)
			df = df.drop(df.index[df.Answer == '*'])
			df = df.reset_index(drop=True)
			df = df[['Node','Answer']]
			for i in range(len(df)):
				temp[df.Node[i]] = df.Answer[i]
			_answer_dict[sheet] = temp
		self.program_restart()


	# 外部診斷結果查詢
	def loading_answer(self):
		try:
			answer = _answer_dict[self.sheet_name][self.cur_node]
			self.user_answer.set(answer)

		except Exception as e:
			pass

	# 衛星航拍圖開啟介面
	def open_temp_images(self):
		def openimage():
			types = imagename.get()

			if types == 'None':
				messagebox.showerror('ERROR','Please choose which image would you like to view!')
			else:
				if types == 'uva':
					floder = 'N11'
				elif types == 'ndvi':
					floder = 'N12'
				elif types == 'ndwi':
					floder = 'N13'
				elif types == 'swc':
					floder = 'N15'
				elif types == 'irrig':
					floder = 'N16'
				else:
					floder = 'N17'

				images = [os.path.join(self.photo_temp,floder, _) for _ in os.listdir(os.path.join(self.photo_temp,floder))]
				for image in images:
					im = Image.open(image)
					im.show()

		showtempimages = Toplevel(self.windows)
		showtempimages.title('Show Figures')
		showtempimages.geometry('320x120')

		imagename = StringVar()
		imagename.set(None)

		option_frame = LabelFrame(showtempimages, text='Please choose one type of figure')
		option_frame.place(x=10,y=10)

		for folder in ['N11','N12','N13','N15','N16','N17']:
			if not os.path.exists(os.path.join(self.photo_temp, folder)):
				os.mkdir('./%s/%s' % (self.photo_temp,folder))
				
			locals()['%s_state' % folder] = ACTIVE if os.listdir(os.path.join(self.photo_temp, folder)) else DISABLED

		uva = Radiobutton(option_frame, text='UVA', variable=imagename, value='uva', state=locals()['%s_state' % 'N11'])
		uva.grid(row=0, column=0, padx=3, pady=1)
		ndvi = Radiobutton(option_frame, text='NDVI', variable=imagename, value='ndvi', state=locals()['%s_state' % 'N12'])
		ndvi.grid(row=0, column=1, padx=3, pady=1)
		ndwi = Radiobutton(option_frame, text='NDWI', variable=imagename, value='ndwi', state=locals()['%s_state' % 'N13'])
		ndwi.grid(row=0, column=2, padx=3, pady=1)
		swc = Radiobutton(option_frame, text='SWC', variable=imagename, value='swc', state=locals()['%s_state' % 'N15'])
		swc.grid(row=1, column=0, padx=3, pady=1)
		irrig = Radiobutton(option_frame, text='Irrigation', variable=imagename, value='irrig', state=locals()['%s_state' % 'N16'])
		irrig.grid(row=1, column=1, padx=3, pady=1)
		msavi = Radiobutton(option_frame, text='MSAVI', variable=imagename, value='msavi', state=locals()['%s_state' % 'N17'])
		msavi.grid(row=1, column=2, padx=3, pady=1)

		showbutton = Button(showtempimages, text='Show Figure',command=openimage)
		showbutton.place(x=200,y=90)


		