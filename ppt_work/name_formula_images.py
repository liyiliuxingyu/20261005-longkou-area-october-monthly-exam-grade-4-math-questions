#!/usr/bin/env python3
"""Restore formula picture names lost by Artifact Tool PPTX export.

Usage: name_formula_images.py INPUT.pptx CONTENT.json FORMULAS_DIR OUTPUT.pptx

Names are assigned in the same explicit image-creation order as build_deck.mjs:
question formula first, then step formula pictures. Every mapping is checked
against the exact SVG bytes in the PPTX, so this is not a position-only guess.
"""
from pathlib import Path
import argparse
import hashlib
import json
import posixpath
import zipfile
from lxml import etree as E

P='http://schemas.openxmlformats.org/presentationml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
ASVG='http://schemas.microsoft.com/office/drawing/2016/SVG/main'
NS={'p':P,'r':R,'asvg':ASVG}

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('input');a.add_argument('content');a.add_argument('formulas');a.add_argument('output')
    args=a.parse_args()
    ip,cp,fp,op=map(Path,(args.input,args.content,args.formulas,args.output))
    if ip.resolve()==op.resolve():raise ValueError('Input and output must differ')
    content=json.loads(cp.read_text(encoding='utf-8'))
    reports=[];patches={}
    with zipfile.ZipFile(ip) as zin:
        for i,d in enumerate(content,1):
            key=f'ppt/slides/slide{i}.xml'
            root=E.fromstring(zin.read(key))
            expected=[]
            if d.get('qmath'):expected.append(('question-formula',d['qmath'],d.get('questionFormula','')))
            expected += [(f'step-{j}-formula',s['math'],s.get('formula','')) for j,s in enumerate(d.get('steps',[])) if s.get('math')]
            pics=root.findall('.//p:pic',NS)
            if len(pics)!=len(expected):raise ValueError(f'Slide {i}: {len(pics)} pictures != {len(expected)} formula assets')
            if not expected:continue
            rels=E.fromstring(zin.read(f'ppt/slides/_rels/slide{i}.xml.rels'))
            targets={x.get('Id'):x.get('Target') for x in rels}
            for pic,(name,formula,alt) in zip(pics,expected):
                svg=pic.find('.//asvg:svgBlip',NS)
                if svg is None:raise ValueError(f'Slide {i} formula {name} lacks SVG reference')
                target=targets[svg.get(f'{{{R}}}embed')]
                target=target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join('ppt/slides',target))
                got=zin.read(target);wanted=(fp/f'{formula}.svg').read_bytes()
                if got!=wanted:raise ValueError(f'Slide {i} formula {name} SVG does not match its authored source')
                prop=pic.find('p:nvPicPr/p:cNvPr',NS)
                prop.set('name',name);prop.set('descr',alt or name)
                reports.append({'slide':i,'name':name,'shape_id':prop.get('id'),'svg_sha256':hashlib.sha256(got).hexdigest()})
            patches[key]=E.tostring(root,encoding='UTF-8',xml_declaration=True,standalone=True)
        op.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(op,'w',zipfile.ZIP_DEFLATED) as zout:
            for info in zin.infolist():zout.writestr(info,patches.get(info.filename,zin.read(info.filename)))
    report={'output':str(op),'named_formula_pictures':len(reports),'slides':len(content),'svg_exact_match':True,'pictures':reports}
    op.with_suffix('.formula_names.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='pictures'},ensure_ascii=False))

if __name__=='__main__':main()
