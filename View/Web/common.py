#!/usr/bin/python
def header(title):
	print('Content-Type: text/html')
	print("")
	print("""<!DOCTYPE html>
		<html lang="en">
		<head>
		<title>"""+ title +"""</title>
		<meta charset="utf-8">
		</head>
		<body>""")

def headerCss(title):
	print('Content-Type: text/html')
	print("")
	print("""<!DOCTYPE html>
		<html lang="en">
		<head>
		<title>"""+ title +"""</title>
		<link rel="stylesheet" href="login.css"/>
		<meta charset="utf-8">
		</head>
		<body>""")


def footer():
	print("""</body>
</html>""")
