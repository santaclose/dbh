#!/usr/bin/python3
import re
import os
import sys
from collections import defaultdict

mode = sys.argv[1]
targetPath = sys.argv[2]

OPEN_TO_CLOSE_DICT = {
	'{': '}',
	'(': ')',
	'[': ']',
	'<': '>'
}

def filesInFolderRec(folder):
	return [os.path.join(dp, f).replace('\\', '/') for dp, dn, filenames in os.walk(folder) for f in filenames]

def findClosingBracket(code, openBracketIndex):
	i = openBracketIndex
	openChar = code[openBracketIndex]
	closeChar = OPEN_TO_CLOSE_DICT[openChar] if openChar in OPEN_TO_CLOSE_DICT.keys() else openChar
	counter = 0
	while i < len(code):
		if code[i] == closeChar: # close first in case it's the same as open
			counter -= 1
			if counter == 0:
				return i
		elif code[i] == openChar:
			counter += 1
		i += 1
	return -1

# asume comment stuff doesn't happen inside strings for now
def getCommentedIntervals(code):
	result = []
	# multiline comments
	currentStart = 0
	while True:
		commentStart = code.find("/*", currentStart)
		if commentStart < 0:
			break
		commentEnd = code.find("*/", commentStart + 2) + 2
		if commentEnd < 0:
			result.append((commentStart, len(code)))
			break
		result.append((commentStart, commentEnd))
		currentStart = commentEnd
	# multiline comments
	currentStart = 0
	while True:
		commentStart = code.find("//", currentStart)
		if commentStart < 0:
			break
		commentEnd = code.find("\n", commentStart + 2) + 1
		if commentEnd < 0:
			result.append((commentStart, len(code)))
			break
		result.append((commentStart, commentEnd))
		currentStart = commentEnd
	return result

def isValueInIntervals(value, intervals):
	for interval in intervals:
		if value > interval[0] and value < interval[1]:
			return True
	return False

def addFunctionTrace(filePath, openAndClose=False):
	with open(filePath, 'r') as cppFile:
		code = cppFile.read()
	functionMatches = [(x.start(), x.end()) for x in re.finditer(r"\w+\([^;{()]*\)[\s\n]*{", code)]
	for fm in reversed(functionMatches):
		fms = fm[0]
		fme = fm[1]
		fmv = code[fms:fme]
		code = code[:fme] + f'/*dhelper_ft_s*/printf("[dhelper] %s start\\n", __func__);/*dhelper_ft_e*/' + code[fme:]
		if openAndClose:
			openBracketIndex = fme - 1
			closeBracketIndex = findClosingBracket(code, openBracketIndex)
			functionCode = code[openBracketIndex + 1:closeBracketIndex]
			commentedIntervals = getCommentedIntervals(functionCode)
			returnMatches = [(x.start(), x.end()) for x in re.finditer(r"return [^;]+;|return;", functionCode)]
			for rm in reversed(returnMatches):
				rms = rm[0]
				rme = rm[1]
				rmv = functionCode[rms:rme]
				if isValueInIntervals(rms, commentedIntervals):
					continue
				functionCode = functionCode[:rms] + '/*dhelper_ft_s*/{printf("[dhelper] %s end\\n", __func__);/*dhelper_ft_e*/' + rmv + '/*dhelper_ft_s*/}/*dhelper_ft_e*/' + functionCode[rme:]
			code = code[:openBracketIndex + 1] + functionCode + '/*dhelper_ft_s*/printf("[dhelper] %s end\\n", __func__);/*dhelper_ft_e*/' + code[closeBracketIndex:]
	with open(filePath, 'w') as cppFile:
		cppFile.write(code)

def removeFunctionTrace(filePath):
	with open(filePath, 'r') as cppFile:
		code = cppFile.read()
	endComment = "/*dhelper_ft_e*/"
	while True:
		i = code.find("/*dhelper_ft_s*/")
		if i == -1:
			break
		j = code.find(endComment) + len(endComment)
		code = code[:i] + code[j:]
	with open(filePath, 'w') as cppFile:
		cppFile.write(code)

def clear(filePath):
	with open(filePath, 'r') as cppFile:
		code = cppFile.read()
	actionDict = defaultdict(lambda: 0)
	while True:
		ms = re.search(r'/\*dhelper_([^_]+)_s\*/', code)
		if ms is None:
			break
		me = re.search(r'/\*dhelper_([^_]+)_e\*/', code)
		actionDict[me.group(1)] += 1
		code = code[:ms.start()] + code[me.end():]
	with open(filePath, 'w') as cppFile:
		cppFile.write(code)
	for k in actionDict.keys():
		print(f"removed {actionDict[k]} instances of {k} in {filePath}")


if "ft" in mode:
	if os.path.isdir(targetPath):
		for f in filesInFolderRec(targetPath):
			removeFunctionTrace(f) if "r" in mode else addFunctionTrace(f, "c" in mode)
	else:
		removeFunctionTrace(targetPath) if "r" in mode else addFunctionTrace(targetPath, "c" in mode)
elif mode == "clear":
	if os.path.isdir(targetPath):
		for f in filesInFolderRec(targetPath):
			clear(f)
	else:
		clear(targetPath)