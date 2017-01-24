from SchemeLex import *

def main():
	def _m_to_html(m, i):
		t = m[0]
		if t == None:
			return '''
<span onclick="doShowHide(this, '{i}')" class="showhidebtn">[<code>+</code>]</span>
<div>
<code>({m[0]!r},</code>
<div id="{i}" class="showhideblock">
<code style="position:relative;left:1em;">{m[1]!r})</code>
</div>
</div>
'''.format(m=m, i=i), i
		elif t == '*':
			ms_html = ''
			j = i
			for n in m[1]:
				m_html, j = _m_to_html(n, j + 1)
				ms_html += m_html
			return '''
<span onclick="doShowHide(this, '{i}')" class="showhidebtn">[<code>+</code>]</span>
<div>
<code>({m[0]!r}, [</code>
<div id="{i}" class="showhideblock">
{ms_html}
</div>
<code>])</code>
</div>
'''.format(m=m, i=i, ms_html=ms_html), j
		else:
			m_html, j = _m_to_html(m[1], i + 1)
			return '''
<span onclick="doShowHide(this, '{i}')" class="showhidebtn">[<code>+</code>]</span>
<div>
<code>({m[0]!r},</code>
<div id="{i}" class="showhideblock">
{m_html}
</div>
<code>)</code>
</div>
'''.format(m=m, i=i, m_html=m_html), j
	
	def m_to_html(m):
		return '''
<!DOCTYPE html>
<html>
<head>
<title>PyScheme.SchemeLex.m_to_html</title>
<style type="text/css">
body {
	font-size: 400%;
}
.showhidebtn {
	background-color: #ccc;
	color: inherit;
	cursor: pointer;
	float: left;
	font-size: 75%;
	position: relative;
	text-decoration: none;
	top: 0.25em;
}
.showhideblock {
	left: 1em;
	position: absolute;
	visibility: hidden;
}
</style>
<script type="text/javascript">
function doShowHide(btnElem, targetElemId) {
	var targetElem = document.getElementById(targetElemId);
	if (targetElem.style.visibility == "visible") {
		targetElem.style.visibility = "hidden";
		targetElem.style.position = "absolute";
		btnElem.innerHTML = "[<code>+</code>]";
	} else {
		targetElem.style.visibility = "visible";
		targetElem.style.position = "relative";
		btnElem.innerHTML = "[<code>-</code>]";
	}
}
</script>
</head>
<body>
''' + _m_to_html(m, 0)[0] + '''
</body>
</html>
'''
	
	html = m_to_html(lex('''
(let ((path '())
	  (c #f))
  (let ((add (lambda (s)
			   (set! path (cons s path)))))
	(dynamic-wind
	  (lambda () (add 'connect))
	  (lambda ()
		(add (call-with-current-continuation
			  (lambda (c0)
				(set! c c0)
				'talk1))))
	  (lambda () (add 'disconnect)))
	(if (< (length path) 4)
		(c 'talk2)
		(reverse path))))
'''))
	with open('scheme_lex_output.html', 'w') as f:
		f.write(html)
	
	import webbrowser, os
	webbrowser.open('file://' + os.path.abspath('scheme_lex_output.html'))
	
main()
