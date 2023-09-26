
def indentFunctionTrace(ftstring):
	output = ""
	currentIndent = 0
	for line in ftstring.split('\n'):
		if line.endswith("end"):
			currentIndent -= 1

		output += '  ' * currentIndent
		output += line
		output += '\n'

		if line.endswith("start"):
			currentIndent += 1
	return output


if __name__ == "__main__":
	import sys
	with open(sys.argv[1], 'r') as file:
		print(indentFunctionTrace(file.read()))