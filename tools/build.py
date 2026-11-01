#!/usr/bin/env python3
"""Genera index.html y logic.js a partir de src/page.html (sin eval, compatible con CSP estricta)."""
import os,re
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s=open(os.path.join(R,'src/page.html')).read()
a=s.index('<script type="text/plain" id="dc-logic">'); b=s.index('</script>',a)
logic=s[s.index('>',a)+1:b]
open(os.path.join(R,'logic.js'),'w').write('/* generado por tools/build.py */\n'+logic.strip()+'\nwindow.Component = Component;\n')
html=s[:a]+'<script src="dclogic.js"></script>\n<script src="logic.js"></script>'+s[b+len('</script>'):]
open(os.path.join(R,'index.html'),'w').write(html)
print('ok')
