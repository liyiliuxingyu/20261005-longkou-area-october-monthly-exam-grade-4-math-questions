import json,subprocess,hashlib,concurrent.futures,re
from pathlib import Path
BASE=Path(__file__).resolve().parent
C=BASE/'content.json'; S=json.loads(C.read_text()); out=BASE/'formulas';out.mkdir(exist_ok=True)
jobs={}
for s in S:
 if s.get('questionFormula'):
  f=s['questionFormula'];k=hashlib.md5(('193B50'+f).encode()).hexdigest();s['qmath']=k;jobs[k]=(f,'193B50')
 for i,st in enumerate(s['steps']):
  if st.get('formula'):
   f=st['formula'];col='B83329' if i==len(s['steps'])-1 else '193B50';k=hashlib.md5((col+f).encode()).hexdigest();st['math']=k;jobs[k]=(f,col)
def render(item):
 k,(f,c)=item;d=out/k;d.mkdir(exist_ok=True)
 tex=r'\documentclass[border=1pt]{standalone}'+'\n'+r'\usepackage{amsmath,amssymb,xcolor}'+'\n'+r'\begin{document}$\displaystyle\color[HTML]{'+c+'}'+f+r'$\end{document}'
 (d/'m.tex').write_text(tex)
 run=subprocess.run(['pdflatex','-interaction=batchmode','-halt-on-error','-output-directory',str(d),str(d/'m.tex')],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 if run.returncode: return (k,False,run.stdout.decode()[-400:])
 run=subprocess.run(['pdftocairo','-svg',str(d/'m.pdf'),str(out/(k+'.svg'))],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 return (k,run.returncode==0,run.stdout.decode()[-300:])
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
 results=list(ex.map(render,jobs.items()))
failed=[r for r in results if not r[1]]
print('formulas',len(jobs),'failed',failed)
if failed:raise SystemExit(1)
C.write_text(json.dumps(S,ensure_ascii=False,indent=2))
