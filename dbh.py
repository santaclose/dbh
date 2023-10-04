#!/usr/bin/python3
import re
import os
import sys
import parse
import indentft
from collections import defaultdict

def filesInFolderRec(folder):
	return [os.path.join(dp, f).replace('\\', '/') for dp, dn, filenames in os.walk(folder) for f in filenames]

def isValueInIntervals(value, intervals):
	for interval in intervals:
		if value > interval[0] and value < interval[1]:
			return True
	return False

def addFunctionTrace(filePath, functionExitToo=False):
	with open(filePath, 'r') as cppFile:
		code = cppFile.read()
	commentIntervals = []
	stringIntervals = []
	parse.getStringAndCommentIntervals(code, commentIntervals, stringIntervals)

	functionMatches = [(x.start(), x.end()) for x in re.finditer(r"\w+\([^;{()]*\)[\s\n]*(const)?[\s\n]*{", code)]
	for fm in reversed(functionMatches):
		fms = fm[0]
		fme = fm[1]
		fmv = code[fms:fme]

		if isValueInIntervals(fms, commentIntervals) or isValueInIntervals(fms, stringIntervals):
			continue

		if functionExitToo:
			openBracketIndex = fme - 1
			closeBracketIndex = parse.findClosingBracket(code, openBracketIndex)
			functionCode = code[openBracketIndex + 1:closeBracketIndex]
			returnMatches = [(x.start(), x.end()) for x in re.finditer(r"return [^;]+;|return;", functionCode)]
			for rm in reversed(returnMatches):
				rms = rm[0]
				rme = rm[1]
				rmv = functionCode[rms:rme]

				if isValueInIntervals(openBracketIndex + 1 + rms, commentIntervals) or isValueInIntervals(openBracketIndex + 1 + rms, stringIntervals):
					continue

				functionCode = functionCode[:rms] + '/*dbh_ft_s*/{printf("[dbh] %s end\\n", __func__);/*dbh_ft_e*/' + rmv + '/*dbh_ft_s*/}/*dbh_ft_e*/' + functionCode[rme:]
			code = code[:openBracketIndex + 1] + functionCode + '/*dbh_ft_s*/printf("[dbh] %s end\\n", __func__);/*dbh_ft_e*/' + code[closeBracketIndex:]
		code = code[:fme] + f'/*dbh_ft_s*/printf("[dbh] %s start\\n", __func__);/*dbh_ft_e*/' + code[fme:]

	with open(filePath, 'w') as cppFile:
		cppFile.write(code)

def removeFunctionTrace(filePath):
	with open(filePath, 'r') as cppFile:
		code = cppFile.read()
	endComment = "/*dbh_ft_e*/"
	while True:
		i = code.find("/*dbh_ft_s*/")
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
		ms = re.search(r'/\*dbh_([^_]+)_s\*/', code)
		if ms is None:
			break
		me = re.search(r'/\*dbh_([^_]+)_e\*/', code)
		actionDict[me.group(1)] += 1
		code = code[:ms.start()] + code[me.end():]
	index = -1
	while True:
		index = code.rfind(" // /*dbh_", 0, index)
		if index < 0:
			break
		index = code.rfind('\n', 0, index) + 1
		lineEnd = code.find('\n', index) + 1
		code = code[:index] + code[lineEnd:]
	with open(filePath, 'w') as cppFile:
		cppFile.write(code)
	for k in actionDict.keys():
		print(f"removed {actionDict[k]} instances of {k} in {filePath}")


if __name__ == "__main__":
	mode = sys.argv[1]
	targetPath = sys.argv[2]

	if mode == "clear":
		if os.path.isdir(targetPath):
			for f in filesInFolderRec(targetPath):
				clear(f)
		else:
			clear(targetPath)
	elif mode == "indentft":
		with open(targetPath, 'r') as file:
			print(indentft.indentFunctionTrace(file.read()))
	elif "ft" in mode:
		if os.path.isdir(targetPath):
			for f in filesInFolderRec(targetPath):
				removeFunctionTrace(f) if "r" in mode else addFunctionTrace(f, "e" in mode)
		else:
			removeFunctionTrace(targetPath) if "r" in mode else addFunctionTrace(targetPath, "e" in mode)