from __future__ import with_statement
import re #regex import
import json
import os
import io
from sys import exit, version
#from io import open

def dump(obj):
	for attr in dir(obj):
		console.write("obj.%s = %s" % (attr, getattr(obj, attr)))

def mainFunction():
	encoding = 'utf-8'

	#console.show()


	#http://npppythonscript.sourceforge.net/docs/latest/scintilla.html

	foundItems = []
	console.clear()

	currentLine = 0
	lineCount = editor.getLineCount()

	afterAction = '' #JSON, FORMAT

	#2.7.6-notepad++ r2 (default, Apr 21 2014, 19:26:54) [MSC v.1600 32 bit (Intel)]
	#console.write((sys.version) + '\r\n')

	
	

	#mainAction = notepad.prompt("main action parser 'PROP', 'ORDERPROP', 'LINE', 'FINDTAG', 'COLPROPREP': ", "-", "prop").strip().lower()
	mainAction = notepad.prompt("main action parser 'PROP', 'ORDERPROP', 'LINE', 'FINDTAG', 'COLPROPREP': ", "-", "colproprep").strip().lower()


	if mainAction == "orderprop":
		for i in range(0, lineCount):
			index = i
			#gets the line an trims it
			line = editor.getLine(index).strip()
			#console.write(str(index) + ': "' + line + '"\r\n')
			if len(line) > 7:
				searchObj = re.search( r'(public|private)', line)
				#checks if it starts with public or private
				if searchObj:
					startPos = searchObj.end()
					searchObj = re.search( r'([\s]{0,1}{[\s]{0,1}get;)', line, startPos)
					#finds the get setter
					if searchObj:
						endPos = searchObj.start()
						line = line[startPos:endPos].strip()
						posStr = len(line)-1
						while posStr > 0:
							currChar = line[posStr:posStr+1]
							if currChar == ' ':
								#add column tag, replaces the whole line
								propStr = line[posStr+1:endPos].strip()
								typeStr = line[0:posStr].strip()
								#console.write(str(startPos) +':'+ str(posStr) + propStr + ' - ' + typeStr + '\r\n')
								foundItems.append((propStr, typeStr))
								#console.write(str(index) + ' prop: "' + line[posStr+1:propEnd] + '"\r\n')
								break
							posStr -= 1
		if len(foundItems) > 0:
			foundItems.sort(key=lambda x: x[1])
					#'end', 'endpos', 'expand', 'group', 'groupdict', 'groups', 'lastgroup', 'lastindex', 'pos', 're', 'regs', 'span', 'start', 'string']
					#console.write(str(dir(searchObj)) + '"\r\n')

	elif mainAction == "findtag":
		#searchTag = notepad.prompt("tag starting name: (like: 'field' in: field=\"", "-", "field").strip().lower()
		searchTags = notepad.prompt("tag starting name: (like: 'field' in: field=\"), multiple = splitted by ,:", "-", "content").strip().lower().split(',')
		#searchTags = searchTag.split(',')
		#console.write('searchTags len: ' + str(len(searchTags)) + '"\r\n')
		for i in range(0, lineCount):
			index = i
			#gets the line an trims it
			line = editor.getLine(index).strip()
			for searchTag in searchTags:
				searchTag = searchTag.strip()
				#find the [tag]=" part
				#regexSearchString = ("(\b" + re.escape(searchTag.strip()) + "\b[\ ]{0,10}\=[\ ]{0,10}\\\")")
				regexSearchString = ("(" + re.escape(searchTag.strip()) + "[\ ]{0,10}\=[\ ]{0,10}\")")
				#regexSearchString = ('' + re.escape(searchTag.strip()) + '\=')
				foundTagObj = re.search(regexSearchString, line, re.IGNORECASE)
				#console.write('line: ' + line + ', regexSearchString: "' + regexSearchString + '"\r\n')
				if foundTagObj:
					foundTagStart = foundTagObj.end()
					#console.write('found - foundTagStart: ' + str(foundTagStart) + '\r\n')
					#find the next: "
					foundTagEnd = line.find('"', foundTagStart)
					if(foundTagEnd > -1 and foundTagEnd > foundTagStart):
						foundItems.append((line[foundTagStart:foundTagEnd], ''))
						#console.write("s:" + str(foundTagStart) + ", e:" + str(foundTagEnd) + "word:'" + line[foundTagStart:foundTagEnd] + "'\r\n")
					
	elif mainAction == "prop":
		for i in range(0, lineCount):
			index = i
			#gets the line an trims it
			line = editor.getLine(index).strip()
			#console.write(str(index) + ': "' + line + '"\r\n')
			propItem = findProperty(line)
			if propItem != None:
				foundItems.append(propItem)

	elif mainAction == "line":
		for i in range(0, lineCount):
			#gets the line an trims it
			line = editor.getLine(i).strip()
			foundItems.append((line, ''))
			
	#replaces all column tags with the prop tag in the selected area
	elif mainAction == "colproprep":
		line = 'a'
		selectionStart = editor.getSelectionStart()
		selectionEnd = editor.getSelectionEnd()
		if selectionStart > -1 and selectionEnd > selectionStart:
			selectedText = editor.getTextRange(selectionStart, selectionEnd)
			editor.deleteBack() #Delete the selection or if no selection, the character before the caret.
			lineCount = editor.getLineCount()
			foundColProps = getAllLinesColProp()
			
			if len(foundColProps) > 0:
				editor.clearAll()
				editor.setText(selectedText)
				for j in range(0, len(foundColProps)): #loop trough all found properties
					#replace whole word only
					editor.rereplace('\\b({0})\\b'.format(foundColProps[j][0][0]), foundColProps[j][1][0])
					#console.write('replace: "' + str(foundColProps[j][0][0]) + '", with: "' + str(foundColProps[j][1][0]) + '"\r\n')
					#console.write('added new found match: ' + str(foundProp)+ '\r\n')
					
	if mainAction != "colproprep":
		nothing1 = None
	if len(foundItems) > 0:
		afterAction = notepad.prompt("JSONIZE completed, after action: ('JSON', 'FORMAT', 'REALNAMES' [nothing])", "INPUT", "FORMAT").strip().lower()
		editor.clearAll()
		amountItems = len(foundItems)
		#reverse dem tuple
		foundItems = foundItems[::-1]
		if afterAction == "json":
			editor.insertText(0, '}\r\n')
			for i in range(0, amountItems):
				toAddComma = ','
				if(i==0):
					toAddComma = ''
				#editor.insertText(0, '\t"' + foundItems[i][0] + '-' + foundItems[i][1] + '": ""' + toAddComma + '\r\n')
				editor.insertText(0, '\t"' + foundItems[i][0] + '": ""' + toAddComma + '\r\n')
			editor.insertText(0, '{\r\n')
		if afterAction == "format":
			formatString = 'destination.{0} = (!string.IsNullOrEmpty(source.{0}) ? source.{0}.Trim() : string.Empty);'
			if mainAction == "orderprop":
				formatString = "public {1} {0} {{ get; set; }}"
			elif mainAction == "findtag":
				formatString = "{0}"
			formatString = notepad.prompt("format string: ", "FORMAT", formatString)
			
			for i in range(0, amountItems):
				#the type can be in the second part of the tuple
				if(len(foundItems[i]) > 1):
					editor.insertText(0, formatString.format(foundItems[i][0], foundItems[i][1]) + '\r\n')
				else:
					editor.insertText(0, formatString.format(foundItems[i][0]) + '\r\n')
		elif afterAction == "realnames":
			#scan all cs files for Column's and find their correspondending property names in the line(s) (max third line) below
			#we have all lines, check them agains the column props, then find the correspondending prop, if found, the name cannot be the same (case sensitive)
			#also check for more and add them below each other so you can remove them yourself
			directory = notepad.prompt("*.cs files folder location to search in: ", "FORMAT", "c:\\_Data_\\Projecten\\Wish3\\Source\\F2Wish\\Facility2.Model\\Model\\")
			foundMatches = {}
			for root, dirs, files in os.walk(directory):
				for file in files:
					if file.endswith('.cs'):
						fullFilePath = os.path.join(root, file)
						#console.write(fullFilePath + '\r\n')
						if (os.path.exists(fullFilePath)):
							#console.write(str(fullFilePath) + '\r\n')
							fileH = open(fullFilePath, 'rb')
							try:
								#content = fileH.read().decode("UTF-8")
								content = fileH.readlines()
								lines = [x.strip() for x in content]
								#lines = filter(str.strip, lines)
								i = 0
								foundColumn = None
								foundProp = None
								
								while i < len(lines):
									line = lines[i]
									if isinstance(line, str):
										line = str(line)
										#console.write(str(lines[i]) + '\r\n')
									elif isinstance(line, unicode):
										line = line.decode('ascii')
									foundProp = findProperty(line)
									#found a prop after a column
									if (foundProp != None and foundColumn != None):
										for j in range(0, len(foundItems)): #loop trough all found properties
											if foundItems[j][0] == foundColumn[0]: #foundItems and foundCOlum are always tuples: ('[PROPNAME]','')
												if foundItems[j][0] in foundMatches:
													isMatch = False
													for alreadyAddedItem in foundMatches[foundItems[j][0]]:
														if alreadyAddedItem == foundProp[0]:
															isMatch = True
															break
													if isMatch == False:
														foundMatches[foundItems[j][0]].append(foundProp[0])
														#console.write('added existing found match: ' + str(foundProp[0])+ '\r\n')
												else:
													foundMatches[foundItems[j][0]] = [foundProp[0]]
													#console.write('added new found match: ' + str(foundProp)+ '\r\n')
													
											
										#console.write('column: ' + str(foundColumn[0]) + ', prop: ' + str(foundProp[0]) + '\r\n')
									#found another prop, bud no column yet, skip it
									elif (foundProp != None and foundColumn is None):
										foundProp = None
									else:
										foundColumn = findColumn(line)
									i+=1
								#'[Column("' + propStr + '")]
							finally:
								fileH.close()
			#console.write('len:' + str(len(foundMatches)) + '\r\n')
			foundItems = foundItems[::-1] #switch tuple back again
			for item in foundItems: #loop through the origional found items
				editor.appendText('[Column("' + item[0] + '")]\r\n')
				if item[0] in foundMatches:
					isMatch = False
					for item2 in foundMatches[item[0]]:
						if item2 != item[0]:
							editor.appendText('public ' + item[1] + ' ' + item2 + ' { get; set; } \r\n')
							isMatch = True
					if isMatch == False:
						editor.appendText('public ' + item[1] + ' ' + item[0] + ' { get; set; } \r\n')
				else:
					editor.appendText('public ' + item[1] + ' ' + item[0] + ' { get; set; } \r\n')
					#console.write('K:' + str(key) + ', v:' + str(','.join(map(str,foundMatches[key]))) + '\r\n')
				editor.appendText('\r\n')
	else:
		notepad.messageBox("PARSING completed, nothing found!", "-", 0)


	#notepad.messageBox("JSONIZE completed", "-", 0)


	

def findProperty( strInput ):
	line = strInput.strip()
	#console.write(str(index) + ': "' + line + '"\r\n')
	if len(line) > 7:
		searchObj = re.search( r'(public|private)', line)
		#checks if it starts with public or private
		if searchObj:
			startPos = searchObj.end()
			try:
				searchObj = re.search( r'([\s]{0,1}{[\s]{0,1}get\;)', line, startPos)
				#finds the get setter
				if searchObj:
					endPos = searchObj.start()
					line = line[startPos:endPos].strip()
					posStr = len(line)-1
					while posStr > 0:
						currChar = line[posStr:posStr+1]
						if currChar == ' ':
							#add column tag, replaces the whole line
							propStr = line[posStr+1:endPos].strip()
							typeStr = line[0:posStr].strip()
							#console.write(str(startPos) +':'+ str(posStr) + propStr + ' - ' + typeStr + '\r\n')
							return (propStr, typeStr)
							#console.write(str(index) + ' prop: "' + line[posStr+1:propEnd] + '"\r\n')
							break
						posStr -= 1
						#console.write('posStr: "' + str(posStr) + '"\r\n')
			except:
				return None
			#except Exception, e:
				#console.write('error on: ' + str(line) + str(e) + '\r\n')
				#raise e
	return None

def findColumn (strInput):
	line = strInput.strip()
	#console.write(str(index) + ': "' + line + '"\r\n')
	if len(line) > 7:
		#console.write(': "' + line + '"\r\n')
		searchObj = re.search( r'\[Column\(\"([A-Za-z0-9\-\_]{1,255})\"\)\]', line)
		#console.write('found column: ' + str(searchObj is None) + '\r\n')
		if searchObj and len(searchObj.groups()) > 0:
			#console.write('groups: ' + str(searchObj.groups(1)) + '\r\n')
			columnStr = searchObj.group(1).strip()
			#find that real found regex in the line
			return (columnStr, '')
	return None
	
def getAllLinesColProp ():
	lineCount = editor.getLineCount()
	foundColProps = []
	i = 0
	while i < lineCount:
		line = editor.getLine(i).strip()
		if isinstance(line, str):
			line = str(line)
			#console.write(str(lines[i]) + '\r\n')
		elif isinstance(line, unicode):
			line = line.decode('ascii')
		foundProp = findProperty(line)
		#found a prop after a column
		if (foundProp != None and foundColumn != None):
			foundColProps.append((foundColumn, foundProp))
			
			foundProp = None
			foundColumn = None
			#console.write('column: ' + str(foundColumn[0]) + ', prop: ' + str(foundProp[0]) + '\r\n')
		#found another prop, bud no column yet, skip it
		elif (foundProp != None and foundColumn is None):
			foundProp = None
		else:
			foundColumn = findColumn(line)
		i+=1
	return foundColProps

mainFunction()
