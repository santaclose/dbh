from collections import defaultdict

def indentFunctionTrace(ftstring):
	perFunctionCounter = defaultdict(lambda: 0)
	output = ""
	currentIndent = 0
	for line in ftstring.split('\n'):
		isStart = line.startswith("[dbh]") and line.endswith("start")
		isEnd = line.startswith("[dbh]") and line.endswith("end")

		if isEnd:
			currentIndent -= 1

		output += '  ' * currentIndent
		output += line
		if isStart:
			output += ' ' + str(perFunctionCounter[line[:-5]])
		output += '\n'

		if isStart:
			perFunctionCounter[line[:-5]] += 1
			currentIndent += 1
	return output


if __name__ == "__main__":
	import sys
	with open(sys.argv[1], 'r') as file:
		print(indentFunctionTrace(file.read()))