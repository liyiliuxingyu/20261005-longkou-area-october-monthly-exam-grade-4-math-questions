import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
import {GlobalFonts} from '@napi-rs/canvas';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
GlobalFonts.registerFromPath(root+'/deps/fandol/FandolHei-Regular.otf');
GlobalFonts.registerFromPath(root+'/deps/fandol/FandolHei-Bold.otf');
GlobalFonts.registerFromPath(root+'/deps/fandol/FandolKai-Regular.otf');
const data=JSON.parse(await fs.readFile(root+'/ppt_work/content.json','utf8'));
const p=Presentation.create({slideSize:{width:1280,height:720}});
const C={navy:'#193B50',blue:'#176B90',red:'#B83329',gray:'#54616C',pale:'#E6F1F5',orange:'#D47F25'};
const plans=[];const coverage=[];
function text(s,name,t,x,y,w,h,size=28,color=C.navy,bold=false,font='FandolHei'){
 let a=s.shapes.add({geometry:'textbox',name,position:{left:x,top:y,width:w,height:h},fill:'none',line:{style:'solid',fill:'none',width:0}});
 a.text=t;a.text.style={fontSize:size,typeface:font,color,bold,insets:0,wrap:'square',autoFit:'none',verticalAlignment:'middle'};return name;
}
function line(s,name,x1,y1,x2,y2,color=C.navy,width=2,dash=false){
 const x=Math.min(x1,x2),y=Math.min(y1,y2),w=Math.max(1,Math.abs(x2-x1)),h=Math.max(1,Math.abs(y2-y1));
 s.shapes.add({geometry:'custom',name,position:{left:x,top:y,width:w,height:h},fill:'none',line:{style:dash?'dash':'solid',fill:color,width},customPaths:[{width:w,height:h,commands:[{moveTo:{x:x1-x,y:y1-y}},{lineTo:{x:x2-x,y:y2-y}}]}]});return name;
}
function poly(s,name,pts,fill='none',color=C.blue,width=2){const xs=pts.map(a=>a[0]),ys=pts.map(a=>a[1]);const x=Math.min(...xs),y=Math.min(...ys),w=Math.max(...xs)-x,h=Math.max(...ys)-y;s.shapes.add({geometry:'custom',name,position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:color,width},customPaths:[{width:w,height:h,commands:[{moveTo:{x:pts[0][0]-x,y:pts[0][1]-y}},...pts.slice(1).map(a=>({lineTo:{x:a[0]-x,y:a[1]-y}})),{close:{}}]}]});return name;}
function rect(s,name,x,y,w,h,fill='none',color=C.navy){s.shapes.add({geometry:'rect',name,position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:color,width:2}});return name;}
function ellipse(s,name,x,y,w,h,fill='none',color=C.navy){s.shapes.add({geometry:'ellipse',name,position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:color,width:2}});return name;}
function dot(s,name,x,y,label){ellipse(s,name,x-4,y-4,8,8,C.navy,C.navy);if(label)text(s,name+'-label',label,x+7,y-30,50,34,25);}
function label(s,name,t,x,y,w=120,h=32,size=23,color=C.navy){return text(s,name,t,x,y,w,h,size,color,false,'FandolHei');}
function anim(plan,i,n,effect='appear',extra={}){plan.steps[i]??=[];plan.steps[i].push({name:n,effect,...extra});}
function corner(s,name,H,u,v,size=16){const pts=[[H[0]+u[0]*size,H[1]+u[1]*size],[H[0]+(u[0]+v[0])*size,H[1]+(u[1]+v[1])*size],[H[0]+v[0]*size,H[1]+v[1]*size]];line(s,name+'-a',...pts[0],...pts[1],C.red,2);line(s,name+'-b',...pts[1],...pts[2],C.red,2);return [name+'-a',name+'-b'];}
function triangleTool(s,name,H,u,v,L=140){return poly(s,name,[H,[H[0]+L*u[0],H[1]+L*u[1]],[H[0]+L*v[0],H[1]+L*v[1]]],'#E5F2F8/45',C.blue,2);}
function diagram(s,d,plan){
 const bx=730, by=320;
 if(d==='intersection'){
  const O=[1000,455];line(s,'a',792.75,594.75,1207.25,315.25);label(s,'a-label','a',1207,300,45);line(s,'b',849.07,231.17,1148.135,674.685);label(s,'b-label','b',1155,650);line(s,'c',869.2,340,894,650);label(s,'c-label','c',880,650);
  corner(s,'right',O,[.829,-.559],[-.559,-.829],18).forEach(n=>anim(plan,0,n));
  label(s,'four','4个直角',1000,520,180,40,28,C.red);anim(plan,1,'four');
  line(s,'c-ext',862,250,869.2,340,C.red,3,true);anim(plan,2,'c-ext','wipe');
 }
 if(d==='roads'){
  rect(s,'road',730,310,460,42,C.pale);label(s,'roadlabel','五一大街',900,315,160,34,26);
  const P=[950,610];dot(s,'home',...P);label(s,'homelab','李芳家',900,620,150,36,25);
  line(s,'B',950,610,950,352,C.red,4);label(s,'Bl','B',920,475,35,40,28,C.red);
  line(s,'C',950,610,1045,352);label(s,'Cl','C',1010,470,35,40,28);
  line(s,'A1',950,610,770,515);line(s,'A2',770,515,790,352);label(s,'Al','A',790,500,35,40,28);
  line(s,'D1',950,610,1170,510);line(s,'D2',1170,510,1180,352);label(s,'Dl','D',1150,500,35,40,28);
  corner(s,'B-right',[950,352],[0,1],[1,0]).forEach(n=>anim(plan,0,n));
  label(s,'short','900米',970,550,160,45,32,C.red);anim(plan,2,'short');
 }
 if(d==='spray'){
  rect(s,'field',720,360,460,200,'#E9F5ED','#4C8B64');
  for(let i=1;i<8;i++)line(s,'strip'+i,720+i*57.5,360,720+i*57.5,560,'#A8CDB3',1);
  label(s,'length','200米/分 × 8分',770,577,370,40,29);label(s,'width','4米',1185,430,80,40,28);
  label(s,'area','6400平方米',820,430,300,60,36,C.red);anim(plan,1,'area');
 }
 if(d==='vertical'){
  const x=800,y=285; const rows=['  120','×  12','  240',' 120 ',' 1440'];
  rows.forEach((t,i)=>text(s,'v'+i,t,x,y+i*57,250,60,45,C.navy,false,'DejaVu Sans Mono'));
  line(s,'vline1',790,398,1060,398,C.navy,3);line(s,'vline2',790,512,1060,512,C.navy,3);
  label(s,'v1lab','① 2小时',1070,400,180,50,28,C.red);label(s,'v2lab','② 10小时',1070,457,190,50,28,C.red);
  anim(plan,1,'v1lab');anim(plan,2,'v2lab');
 }
 if(d==='flow1'||d==='flow2'){
  const vals=d==='flow1'?['52＋29','81','26×81','2106','2106－128','1978']:['212＋460','672','672÷24','28','20×28','560'];
  for(let i=0;i<3;i++){rect(s,'fb'+i,760,285+i*112,430,80,'#F5F9FB');label(s,'fexpr'+i,vals[i*2],785,293+i*112,220,60,30);label(s,'fans'+i,'＝'+vals[i*2+1],1010,293+i*112,160,60,30,C.red);anim(plan,i,'fans'+i);if(i<2)line(s,'fconn'+i,975,365+i*112,975,397+i*112,C.blue,3);}
 }
 if(d==='fold'){
  rect(s,'paperA',720,340,210,230,'#F5FAFC');rect(s,'paperB',975,340,210,230,'#F5FAFC');
  label(s,'pa','同向对折',750,290,200,40,28);label(s,'pb','换方向对折',985,290,210,40,28);
  for(let i=1;i<=3;i++){line(s,'pa'+i,720+52.5*i,340,720+52.5*i,570,C.red,3,true);anim(plan,0,'pa'+i,'wipe',{direction:'down',duration:600});}
  line(s,'pbv',1080,340,1080,570,C.red,3,true);line(s,'pbh',975,455,1185,455,C.red,3,true);anim(plan,1,'pbv','wipe',{direction:'down'});anim(plan,1,'pbh','wipe',{direction:'right',delay:500});
  label(s,'parallel-fold','平行',785,590,140,45,32,C.red);label(s,'perp-fold','垂直',1045,590,140,45,32,C.red);anim(plan,0,'parallel-fold');anim(plan,1,'perp-fold');
 }
 if(d==='sets'){
  const ys=[290,420,550];const top=['相交','相交','互相平行'],inner=['互相垂直','互相平行','互相垂直'];
  for(let i=0;i<3;i++){label(s,'choice'+i,'ABC'[i],720,ys[i]+40,50,40,30);ellipse(s,'setout'+i,780,ys[i],420,110);label(s,'settop'+i,top[i],920,ys[i]+8,180,32,25);ellipse(s,'setin'+i,880,ys[i]+43,230,57);label(s,'setinlab'+i,inner[i],910,ys[i]+54,210,38,25);}
  label(s,'setmark','✓',1200,315,55,60,48,C.red);anim(plan,0,'setmark');
 }
 if(d==='train'){
  rect(s,'bridge',800,365,290,25,'#BACBD3');label(s,'bridge-label','桥长',895,320,150,35,26);
  rect(s,'train-start',700,410,100,45,'#E5EFF5',C.blue);label(s,'train-s','进桥时',720,463,160,35,24);
  rect(s,'train-end',1090,510,100,45,'#E5EFF5',C.blue);label(s,'train-e','离桥时',1080,565,170,35,24);
  line(s,'journey',800,625,1190,625,C.red,4);label(s,'journey-l','车头走过：桥长＋车长',780,650,480,36,25,C.red);anim(plan,0,'journey','wipe');anim(plan,0,'journey-l');
  const n=rect(s,'moving-train',700,410,100,45,'#CDE3EC',C.blue);anim(plan,0,n,'motion',{path:'M 0 0 L .3046875 0 E',duration:1400});
 }
 if(d==='bars'){
  const x=795; const y=[295,375,455,570];
  for(let i=0;i<4;i++)label(s,'barletter'+i,'ABCD'[i],715,y[i]-15,50,45,30);
  line(s,'barA',x,y[0]+20,1190,y[0]+20,C.navy,3);line(s,'barAmid',930,y[0]+8,930,y[0]+30);label(s,'barA1','16元',805,y[0]-22,100,35,22);label(s,'barA2','？元',1000,y[0]-22,100,35,22);label(s,'barAT','共50元',950,y[0]+25,200,35,22);
  line(s,'barB',x,y[1]+20,1190,y[1]+20,C.navy,3);[925,1055].forEach((v,i)=>line(s,'bdiv'+i,v,y[1]+8,v,y[1]+30));['10元','14元','26元'].forEach((t,i)=>label(s,'blab'+i,t,810+i*130,y[1]-22,100,35,22));label(s,'bt','共？元',950,y[1]+25,200,35,22);
  line(s,'barC1',x,y[2],1091.25,y[2],C.navy,3);line(s,'barC2',x,y[2]+42,1190,y[2]+42,C.navy,3);for(let i=0;i<=3;i++)line(s,'cudiv'+i,x+i*98.75,y[2]-7,x+i*98.75,y[2]+7);for(let i=0;i<=4;i++)line(s,'cldiv'+i,x+i*98.75,y[2]+35,x+i*98.75,y[2]+49);label(s,'clab','48元',900,y[2]-36,150,32,22);label(s,'cextra','多16元',1080,y[2]+5,130,32,22);label(s,'ct','共？元',950,y[2]+44,200,32,22);
  line(s,'barD',x,y[3],1190,y[3],C.red,4);for(let i=0;i<=5;i++)line(s,'ddiv'+i,x+i*79,y[3]-10,x+i*79,y[3]+10,C.red,2);label(s,'dprice','130元',792,y[3]-47,150,35,23,C.red);label(s,'dt','5个相同的单价，共？元',810,y[3]+15,420,40,25,C.red);anim(plan,2,'dt');
 }
 if(['parallelP','perpP','altitude','parallelA'].includes(d)){
  const ux=.94,uy=-.342, vx=.342,vy=.94;
  if(d==='parallelP'){
   const A=[735,340],B=[1185,440],P=[950,530],u=[.976,.217],v=[-.217,.976];
   line(s,'AB',...A,...B,C.navy,3);label(s,'A','A',710,308,50,40,30);label(s,'B','B',1190,425,50,40,30);dot(s,'P',...P,'P');
   const H=[980.117647,394.470588];triangleTool(s,'tool',H,u,v,170);anim(plan,0,'tool');
   line(s,'ruler',997.472,316.375,932.39,609.233,'#8396A1',8);anim(plan,0,'ruler');
   anim(plan,1,'tool','motion',{path:'M 0 0 L -.023529411 .188235294 E',duration:1100});
   line(s,'parallel-answer',730.4,481.2,1189.1,583.15,C.red,4);anim(plan,2,'parallel-answer','wipe',{direction:'right',duration:800});label(s,'line-l','l',1190,575,50,40,30,C.red);anim(plan,2,'line-l');anim(plan,2,'tool','disappear',{delay:850});anim(plan,2,'ruler','disappear',{delay:850});
  } else if(d==='perpP'){
   const H=[960,535],P=[915.54,412.8],u=[ux,uy],v=[-vx,-vy];
   line(s,'CD',730,619,1200,448,C.navy,3);label(s,'C','C',705,620,50,40,30);label(s,'D','D',1200,425,50,40,30);dot(s,'P',...P,'P');
   triangleTool(s,'tool',[850,575],u,v,160);anim(plan,0,'tool');anim(plan,1,'tool','motion',{path:'M 0 0 L .0859375 -.0555556 E',duration:1000});
   line(s,'perp-answer',891.6,347,997.6,638,C.red,4);anim(plan,2,'perp-answer','wipe',{direction:'down'});corner(s,'right',H,u,v,18).forEach(n=>anim(plan,2,n));label(s,'m','m',995,640,60,40,30,C.red);anim(plan,2,'m');anim(plan,2,'tool','disappear',{delay:800});
  } else {
   const B=[740,600],Cpt=[1190,436],H=[960,520],A=[905.28,369.6],u=[ux,uy],v=[-vx,-vy];
   line(s,'BC',...B,...Cpt,C.navy,3);line(s,'AB',...A,...B,C.navy,2);line(s,'AC',...A,...Cpt,C.navy,2);label(s,'A','A',A[0]-15,A[1]-42,50,40,30);label(s,'B','B',705,595,50,40,30);label(s,'C','C',1200,415,50,40,30);
   if(d==='altitude'){
    triangleTool(s,'tool',[850,560],u,v,160);anim(plan,0,'tool');anim(plan,0,'tool','motion',{path:'M 0 0 L .0859375 -.0555556 E',duration:1100,delay:200});
    line(s,'AH',...A,...H,C.red,4);anim(plan,1,'AH','wipe',{direction:'down'});corner(s,'right',H,u,v,18).forEach(n=>anim(plan,1,n));label(s,'H','H',H[0]+8,H[1]+4,50,40,28,C.red);anim(plan,1,'H');anim(plan,1,'tool','disappear',{delay:900});
    label(s,'dist','距离＝AH',1000,570,220,50,32,C.red);anim(plan,2,'dist');
   } else {
    triangleTool(s,'tool',H,u,v,150);anim(plan,0,'tool');line(s,'ruler',1000,625,880,295,'#8396A1',8);anim(plan,0,'ruler');anim(plan,1,'tool','motion',{path:'M 0 0 L -.04275 -.2088889 E',duration:1100});
    line(s,'parallel-answer',720,437,1190,266,C.red,4);anim(plan,2,'parallel-answer','wipe');label(s,'l','l',1192,242,50,40,30,C.red);anim(plan,2,'l');anim(plan,2,'tool','disappear',{delay:800});anim(plan,2,'ruler','disappear',{delay:800});
   }
  }
 }
 if(d==='knotTree'){
  const specs=[['盒数',860,280],['合格个数',730,400],['每盒8个',1030,400],['总个数',680,520],['不合格32个',900,520],['45×16',680,620]];
  specs.forEach(([t,x,y],i)=>{rect(s,'ktbox'+i,x,y,i==4?220:180,55,'#F5F9FB');label(s,'kttext'+i,t,x+10,y+8,i==4?200:160,40,26);});
  line(s,'kt1',950,335,820,400);line(s,'kt2',950,335,1120,400);line(s,'kt3',820,455,770,520);line(s,'kt4',820,455,1010,520);line(s,'kt5',770,575,770,620);
  label(s,'ktdiv','÷',980,365,50,40,32,C.red);anim(plan,0,'ktdiv');label(s,'ktsub','－',855,485,60,40,32,C.red);anim(plan,1,'ktsub');anim(plan,2,'kttext5');
 }
 if(d==='tunnel'){
  const x=720,y=430,total=480,left=218.18,right=261.82;
  line(s,'track',x,y,x+total,y,C.gray,5);label(s,'kt','开拓者队',720,310,220,42,28);label(s,'xf','先锋队',1040,310,180,42,28);label(s,'kl','350米/月',720,355,220,40,26);label(s,'xl','420米/月',1040,355,190,40,26);
  for(let i=0;i<4;i++){rect(s,'left'+i,x+i*left/4,y-20,left/4,40,'#4B8EB1',C.blue);rect(s,'right'+i,x+total-(i+1)*right/4,y-20,right/4,40,'#E6A66A',C.orange);anim(plan,1,'left'+i,'wipe',{delay:i*500,duration:450});anim(plan,1,'right'+i,'wipe',{direction:'left',delay:i*500,duration:450});}
  label(s,'meet','4个月相遇',865,500,250,50,32,C.red);anim(plan,1,'meet','appear',{delay:2000});label(s,'total','全长？米',895,570,250,50,32);anim(plan,2,'total');
 }
}
async function math(s,key,alt,x,y,maxW,height){const svg=await fs.readFile(root+'/ppt_work/formulas/'+key+'.svg','utf8');const m=svg.match(/viewBox="[^"]*?([\d.]+) ([\d.]+)"/);const wh=svg.match(/width="([\d.]+)(?:pt)?" height="([\d.]+)(?:pt)?"/);if(!wh)throw new Error('Missing SVG dimensions');const r=+wh[1]/+wh[2];let h=height,w=h*r;if(w>maxW){w=maxW;h=w/r;}s.images.add({svg,alt,fit:'contain',position:{left:x,top:y+(height-h)/2,width:w,height:h}});return alt;}
for(let si=0;si<data.length;si++){
 const d=data[si],s=p.slides.add();s.background.fill='#FFFFFF';const pl={slide:si+1,steps:d.steps.map(()=>[])};plans.push(pl);coverage.push({slide:si+1,id:d.id,title:d.title,clicks:d.steps.length});
 text(s,'title',d.title,64,40,1150,64,42,C.navy,true);line(s,'header-rule',64,112,1216,112,C.blue,3);
 text(s,'question',d.question,72,132,1138,d.questionFormula?72:102,29,C.navy,false,'FandolKai');
 if(d.qmath)await math(s,d.qmath,'question-formula',80,211,1100,44);
 const hasD=!!d.diagram;const x=72,tw=hasD?580:1125;const sy=d.table?455:(d.qmath?286:270);const stepH=d.steps.length>=4?91:(hasD?108:113);
 for(let i=0;i<d.steps.length;i++){
  const st=d.steps[i],y=sy+i*stepH,stem='step-'+i;
  ellipse(s,stem+'-circle',x,y+4,35,35,C.pale,C.pale);text(s,stem+'-num',String(i+1),x+6,y+3,25,35,22,C.blue,true);anim(pl,i,stem+'-circle');anim(pl,i,stem+'-num');
  const fs=hasD?26:29;const h=st.math?44:(d.steps.length>=4?77:90);
  text(s,stem+'-text',st.text,x+52,y,tw-52,h,fs,C.navy,false,'FandolKai');anim(pl,i,stem+'-text');
  if(st.math){await math(s,st.math,stem+'-formula',x+54,y+48,tw-65,hasD?38:43);anim(pl,i,stem+'-formula');}
 }
 if(d.diagram)diagram(s,d.diagram,pl);
 if(d.table){const table=s.tables.add({rows:2,columns:5,left:100,top:260,width:1080,height:160,values:[['品种','广玉兰','桂花','丁香','牡丹'],['单价/元','55','（空）','38（待核）','36']]});table.borders.assign({style:'solid',fill:'#597584',width:1.4});for(let r=0;r<2;r++)for(let c=0;c<5;c++){const cell=table.getCell(r,c);cell.fill=r===0?'#E6F1F5':'#FFFFFF';cell.text.style={fontSize:30,typeface:'FandolHei',color:C.navy,alignment:'center',verticalAlignment:'middle'};}}
 if(d.answer){text(s,'answer',d.answer,72,651,1140,38,27,C.red,true,'FandolKai');anim(pl,d.steps.length-1,'answer');}
 if(d.note)text(s,'note',d.note,72,690,1130,23,17,C.gray,false,'FandolHei');
 text(s,'page-number',String(si+1).padStart(2,'0'),1185,690,40,23,17,C.gray,false);
 s.speakerNotes.text='原始题目来源：用户提供试卷照片 grok_1792986837659.jpg、grok_1792986841214.jpg。\n'+d.title+'\n动画：每次单击揭示一个分析步骤；公式与文字同步出现。'+(d.note?'\n教学提示：'+d.note:'');
}
await fs.writeFile(root+'/ppt_work/animation_plan.json',JSON.stringify({slides:plans},null,2));
await fs.writeFile(root+'/ppt_work/coverage.json',JSON.stringify(coverage,null,2));
await fs.mkdir(root+'/ppt_work/previews',{recursive:true});
for(let i=0;i<p.slides.items.length;i++){
 const slide=p.slides.items[i];const png=await p.export({slide,format:'png',scale:1});await fs.writeFile(root+'/ppt_work/previews/slide-'+String(i+1).padStart(2,'0')+'.png',new Uint8Array(await png.arrayBuffer()));
}
await (await PresentationFile.exportPptx(p)).save(root+'/ppt_work/draft.pptx');
await fs.writeFile(root+'/ppt_work/deck.proto.json',JSON.stringify(p.toProto()));
console.log('slides',p.slides.items.length,'animations',plans.reduce((a,s)=>a+s.steps.flat().length,0));
