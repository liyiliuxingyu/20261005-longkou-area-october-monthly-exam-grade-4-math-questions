#!/usr/bin/env python3
"""Idempotent final layout correction. Usage: SCRIPT INPUT.pptx OUTPUT.pptx"""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
import sys
src,dst=map(Path,sys.argv[1:3])
if src.resolve()==dst.resolve():raise ValueError('Input and output must differ')
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
with ZipFile(src) as zi,ZipFile(dst,'w',ZIP_DEFLATED) as zo:
 for item in zi.infolist():
  b=zi.read(item.filename)
  if item.filename=='ppt/slides/slide5.xml':
   r=E.fromstring(b);sp=r.xpath('//p:sp[p:nvSpPr/p:cNvPr[@name="a-label"]]',namespaces=ns)
   assert len(sp)==1
   sp[0].find('p:spPr/a:xfrm/a:ext',ns).set('cx',str(45*9525))
   b=E.tostring(r,xml_declaration=True,encoding='UTF-8',standalone=True)
  zo.writestr(item,b)
print(dst)
