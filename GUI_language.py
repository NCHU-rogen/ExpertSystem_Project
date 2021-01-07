#!/usr/bin/python3
# coding: utf-8
# Author: Rogen
# Description: 介面語言


class Chinese(object):
	def ES_GUI_Interface(self):
		windows = {
			'main':'茶樹土壤問題診斷專家系統',
			'done':'專家系統診斷結果顯示'
		}
		menubar = {
			'function':'功能',
			'language':'介面語言',
			'restart':'重啟動',
			'exit':'離開',
			'edit':'編輯',
			'import':'載入',
			'tool':'工具',
			'importresult':'匯入診斷結果',
			'rulebase':'規則庫編輯',
			'rulepath':'規則路徑紀錄',
			'diagnosis':'診斷結果',
			'add_rule':'新增規則',
			'delete_rule':'刪除規則',
			'edit_rule':'編輯規則',
			'satellite':'顯示衛星圖'
		}
		main_title = {
			'answer':'使 用 者 回 答',
			'record':'選項紀錄',
			'query_descript':'問題說明',
			'figure_descript':'圖片說明'
		}
		diag_complete = {
			'done':'請按完成, 顯示診斷結果'
		}
		radiobutten = {
			'yes':'是',
			'no':'否',
			'unknown':'不清楚'
		}
		butten = {
			'back':'上一步',
			'next':'下一步',
			'done':'完成',
			'analyze':'分析'
		}
		done_title = {
			'node':'節點',
			'question':'問題', 
			'answer':'回答',
			'yescore':'Yes分數',
			'noscore':'No分數',
			'diagnosis':'診斷結果',
			'solution':'處理對策'
		}
		sub_title = {
			'rulepath':'詢問路徑',
			'diagnosis':'診斷結果', 
			'yes_prob':'是的可能機率',
			'no_prob':'否的可能機率',
			'main_brach':'主要診斷'
		}
		done_unknown = {
			'unknown':'暫無解答!'
		}
		ruledb_name = {
			'SiteEvaluation':'茶園點評估結果',
			'Soils':'土壤結果',
			'Nutrition':'營養結果',
			'PestDiseases':'病蟲害結果',
			'Agromet':'農耕結果'
		}

		return({'windows':windows,'menubar':menubar, 'main_title':main_title, 'diag_complete':diag_complete, 
			'radiobutten':radiobutten, 'butten':butten, 'sub_title':sub_title, 'done_title':done_title, 
			'done_unknown':done_unknown, 'ruledb_name':ruledb_name})

	def SiteEva_Login_Interface(self):
		login = {
			'title':'勘查場地登入',
			'country':'國家：',
			'region':'茶區：',
			'longitude':'經度:',
			'latitude':'緯度:',
			'name':'姓名:',
			'range':'搜尋範圍(公尺):',
			'degree':'度',
			'minute':'分',
			'second':'秒'
		}
		table = {
			'country':'國家',
			'region':'茶區',
			'name':'姓名',
			'longitude':'經度',
			'latitude':'緯度',
			'phone':'電話',
			'date':'日期'
		}
		menubar = {
			'setting':'設定',
			'db_connect':'資料庫連結'
		}
		db_connect = {
			'title':'資料庫連線',
			'server_info':'伺服器連線',
			'host':'TCP/IP：',
			'port':'端口：',
			'account':'帳號：',
			'pw':'密碼：',
			'upload':'資料上傳',
			'download':'資料下載',
			'ul_success':'上傳成功!',
			'ul_failure':'上傳失敗!',
			'dl_success':'下載成功!',
			'dl_failure':'下載失敗!'
		}
		button = {
			'delete':'刪除',
			'search':'搜尋',
			'add':'新增',
			'edit':'編輯',
			'submit':'提交'
		}
		new = {
			'title':'新增勘查場地',
			'country':'國家',
			'region':'茶區',
			'longitude':'經度',
			'latitude':'緯度',
			'degree':'度',
			'minute':'分',
			'second':'秒',
			'name':'姓名',
			'phone':'電話',
			'field_EW':'東西向\n長度(m)',
			'field_NS':'南北向\n長度(m)',
			'variety':'品種',
			'plant_year':'栽種年份',
			'entry_date':'日期',
			'surveyor':'紀錄者'
		}
		edit = {
			'title':'茶園個資編輯',
			'degree':'度',
			'minute':'分',
			'second':'秒',
			'submit':'提交'
		}
		field = {
			'title':'茶園場地資訊',
			'information':'茶園資訊'
		}

		return({'menubar':menubar, 'db_connect':db_connect,'login':login, 'edit':edit, 'table':table, 'button':button, 
			'new':new, 'field':field})

	def Plating_Management(self):
		fertilizer = {
			'title':'茶園栽培管理',
			'database':'已建立的資料庫',
			'adding':'新增資料庫',
			'ID':'登記證字號',
			'product':'廠牌商品名稱',
			'amount':'施用量',
			'aim':'施用目的',
			'frequency':'施用頻率',
			'unit':'施用量單位：公斤/分地',
			'total_fertilizer':'全年肥料施用量 (只計算已建立資料庫部分)',
			'unit_no_title':'(公斤/分地)',
			'fer_serarch':'肥料袋相片查詢',
			'categorize':'品目：',
			'good':'品名：',
			'accession':'登記證字號',
			'search':'查詢',
			'import':'匯入',
			'clear':'清除',
			'next':'前一張',
			'back':'後一張',
			'edit':'修改',
			'calculate':'計算',
			'suggest':'肥料建議用量',
			'submit':'提交'
		}
		water = {
			'title':'茶園灌溉狀況調查',
			'frequence':'灌溉頻率',
			'amount':'灌溉水量/次',
			'bill_year':'水費/年',
			'bill_degree':'水費/度',
			'sprinkler_density':'噴灌頭密度',
			'electric_bill_year':'電費/年'
		}
		quicktest = {
			'title':'茶園土壤速測',
			'soils':'土壤\n深度',
			'compact':'壓實\n深度',
			'rust':'鏽斑\n深度',
			'top_BD':'表土\nBD',
			'bottom_BD':'底土\nBD',
			'texture':'質\n地',
			'top_soils':'表土',
			'buttom_soils':'底土',
			'gravel':'石\n礫',
			'sand':'砂\n土',
			'loam':'壤\n土',
			'clay':'黏\n土',
			'edit':'編輯',
			'reset':'重置',
			'submit':'提交'
		}
		return({'fertilizer':fertilizer,'water':water,'quicktest':quicktest,'button':self.SiteEva_Login_Interface()})

	def option_panel(self):
		option = {
			'title':'功能選單',
			'main_function':'專家診斷系統',
			'expert_system':'開始診斷',
			'report_output':'開立診斷書',
			'database':'茶園建檔紀錄',
			'water_usage':'水用量',
			'fert_usage':'肥料用量',
			'quick_test':'土壤速測',
			'coordinate':'茶區座標調整',
			'back':'返回'
		}
		return({'option':option})


class English(object):	
	def ES_GUI_Interface(self):
		windows = {
			'main':'Expert System of Tea Soil-Problem Diagnosis',
			'done':'The Results of Expert System Diagnosed'
		}
		menubar = {
			'function':'Function',
			'language':'Language',
			'restart':'Restart',
			'exit':'Exit',
			'edit':'Edit',
			'import':'Import Rulebase',
			'tool':'Tools',
			'importresult':'Import Result',
			'rulebase':'Rulebase Edition',
			'rulepath':'Rule Path Recoded',
			'diagnosis':'Diagnosis Export',
			'add_rule':'Add Rule',
			'delete_rule':'Delete Rule',
			'edit_rule':'Edit Rule',
			'satellite':'Show Satellite'
		}
		main_title = {
			'answer':'Your Answer',
			'record':'Option Record',
			'query_descript':'Query Description',
			'figure_descript':'Figure Description'
		}
		diag_complete = {
			'done':'Please click "Done button" to show diagnosed results'
		}
		radiobutten = {
			'yes':'YES',
			'no':'NO',
			'unknown':'Unknown'
		}
		butten = {
			'back':'Back Step',
			'next':'Next Step',
			'done':'Done',
			'analyze':'Analyze'
		}
		done_title = {
			'node':'Node',
			'question':'Question',
			'answer':'Answer',
			'yescore':'Yes score',
			'noscore':'No score',
			'diagnosis':'Diagnosis',
			'solution':'Solution'
		}
		sub_title = {
			'rulepath':'RulePath',
			'diagnosis':'Diagnosed Results',
			'yes_prob':'Yes Probability',
			'no_prob':'No Probability',
			'main_brach':'Main brach'
		}
		done_unknown = {
			'unknown':'Unknown!'
		}
		ruledb_name = {
			'SiteEvaluation':'SiteEvaluation Result',
			'Soils':'Soils Result',
			'Nutrition':'Nutrition Result',
			'PestDiseases':'Pest&Diseases Result',
			'Agromet':'Agromet Result'
		}

		return({'windows':windows,'menubar':menubar, 'main_title':main_title, 'diag_complete':diag_complete, 
			'radiobutten':radiobutten, 'butten':butten, 'sub_title':sub_title, 'done_title':done_title, 
			'done_unknown':done_unknown, 'ruledb_name':ruledb_name})

	def SiteEva_Login_Interface(self):
		login = {
			'title':'Tea Farm Login',
			'country':'Country:',
			'region':'Tea Area:',
			'longitude':'Longitude:',
			'latitude':'Latitude:',
			'name':'Name:',
			'range':'Range(m):',
			'degree':'Deg.',
			'minute':'Min.',
			'second':'Sec.'
		}
		table = {
			'country':'Country',
			'region':'Region',
			'name':'Name',
			'longitude':'Longitude',
			'latitude':'Latitude',
			'phone':'Phone',
			'date':'Date'
		}
		menubar = {
			'setting':'Setting',
			'db_connect':'Database Connect'
		}
		db_connect = {
			'title':'Database Connection',
			'server_info':'Server Information',
			'host':'Host:',
			'port':'Port:',
			'account':'Account:',
			'pw':'Password:',
			'upload':'Upload',
			'download':'Download',
			'ul_success':'Upload Success!',
			'ul_failure':'Upload Failure!',
			'dl_success':'Download Success!',
			'dl_failure':'Download Failure!'
		}
		button = {
			'delete':'Delete',
			'search':'Search',
			'add':'Registration',
			'edit':'Edit',
			'submit':'Submit'
		}
		new = {
			'title':'Tea Farm Registration',
			'country':'Country',
			'region':'Region',
			'longitude':'Longitude',
			'latitude':'Latitude',
			'degree':'D',
			'minute':'M',
			'second':'S',
			'name':'Name',
			'phone':'Phone',
			'field_EW':'Field of\nWest-East(m)',
			'field_NS':'Field of\nNorth-South(m)',
			'variety':'Variety',
			'plant_year':'Plant Year',
			'entry_date':'Entry Date',
			'surveyor':'Surveyor'
		}
		edit = {
			'title':'Editor of Personal Information of Tea Plantation',
			'degree':'D',
			'minute':'M',
			'second':'S',
			'submit':'Submit'
		}
		field = {
			'title':'Venue Information',
			'information':'Information of Tea Farm'
		}

		return({'menubar':menubar, 'db_connect':db_connect, 'login':login, 'edit':edit, 'table':table, 'button':button, 
			'new':new, 'field':field})

	def Plating_Management(self):
		fertilizer = {
			'title':'Tea Plating Management',
			'database':'Database Built',
			'adding':'Database Adding',
			'ID':'Certificate Number',
			'amount':'Usage',
			'aim':'Fertilizer Aim',
			'product':'Product Name',
			'frequency':'Frequency',
			'unit':'Unit: kg/cent',
			'total_fertilizer':'Fertilizer Application (year)',
			'unit_no_title':'(Kg/cent)',
			'fer_serarch':'Fertilizer Query',
			'categorize':'Catego.:',
			'good':'Good:',
			'accession':'Accession\nNumber',
			'search':'Search',
			'import':'Import',
			'clear':'Clear',
			'next':'Next',
			'back':'previous',
			'edit':'Edit',
			'calculate':'Calculate',
			'suggest':'Fert. Suggest',
			'submit':'Submit'
		}
		water = {
			'title':'Investigation of Tea Irrigation',
			'frequence':'Sprinkling\nFrequency',
			'amount':'Sprinkling Amount\n/time',
			'bill_year':'Water bill\n/year',
			'bill_degree':'Water bill\n/degree',
			'sprinkler_density':'Sprinkler density',
			'electric_bill_year':'Electric bill\n/year'
		}
		quicktest = {
			'title':'Soils quick testing of tea plantation',
			'soils':'Soils\nDepth',
			'compact':'Compact\nDepth',
			'rust':'Rust\nDepth',
			'top_BD':'Top\nBD',
			'bottom_BD':'Buttom\nBD',
			'texture':'Texture',
			'top_soils':'Top',
			'buttom_soils':'Buttom',
			'gravel':'Gra-\nvel',
			'sand':'Sa-\nnd',
			'loam':'Lo-\nam',
			'clay':'Cl-\nay',
			'edit':'Edit',
			'reset':'Reset',
			'submit':'Submit'
		}
		return({'fertilizer':fertilizer,'water':water,'quicktest':quicktest,'button':self.SiteEva_Login_Interface()})

	def option_panel(self):
		option = {
			'title':'Option Panel',
			'main_function':'Expert System　Diagnosis',
			'expert_system':'Start Diagnosis',
			'report_output':'Diagnosis Report',
			'database':'Databases',
			'water_usage':'Water Usage',
			'fert_usage':'Fertilizer Usage',
			'quick_test':'Quick Testing',
			'coordinate':'Coor. Adjusted',
			'back':'Back'
		}
		return({'option':option})

