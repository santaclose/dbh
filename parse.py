OPEN_TO_CLOSE_DICT = {
	'{': '}',
	'(': ')',
	'[': ']',
	'<': '>'
}

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


def getStringAndCommentIntervals(code, outCommentIntervals, outStringIntervals):
	multilineCommentStart = -1
	stringStart = -1
	codeLength = len(code)
	i = 0
	while i < codeLength:
		if stringStart == -1:
			if multilineCommentStart == -1 and i < codeLength - 1 and code[i] == '/' and code[i + 1] == '*':
				multilineCommentStart = i
			elif multilineCommentStart > -1 and i < codeLength - 1 and code[i] == '*' and code[i + 1] == '/':
				outCommentIntervals.append((multilineCommentStart, i + 2))
				multilineCommentStart = -1

		if multilineCommentStart == -1:
			if stringStart == -1 and code[i] == '"':
				stringStart = i
			elif stringStart > -1 and code[i] == '"' and code[i - 1] != '\\':
				outStringIntervals.append((stringStart, i + 1))
				stringStart = -1

		if stringStart == -1 and multilineCommentStart == -1:
			if i < codeLength - 1 and code[i] == '/' and code[i + 1] == '/':
				lineEnd = code.find('\n', i + 2)
				outCommentIntervals.append((i, lineEnd))
				i = lineEnd
				continue

		i += 1