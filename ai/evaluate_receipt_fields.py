"""Synthetic full-page extraction fixture. Not a substitute for real receipt labels."""
import json,re
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,pytesseract
from rapidocr_onnxruntime import RapidOCR
from common import ROOT
F=ROOT/'data/receipt_fixtures';F.mkdir(exist_ok=True);engine=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=1)
rows=[];pred={k:[] for k in ['Tesseract full page','Paddle PP-OCR full page']}
for i in range(8):
 qty=10+i*5;total=qty*240;date=f'2026-10-{10+i}';supplier='Nile Wholesale'
 expected={'quantity':str(qty),'total':str(total),'date':date,'supplier':supplier.lower()};rows.append(expected)
 im=Image.new('RGB',(900,950),'white');d=ImageDraw.Draw(im);font=ImageFont.truetype(str(ROOT/'data/fonts/DejaVuSans.ttf'),28+i%3*2)
 lines=['DEMONSTRATION RECEIPT','Supplier: '+supplier,'Date: '+date,'Product: Cooking Oil','Quantity: '+str(qty),'Unit Price: 240 EGP','TOTAL: '+str(total)+' EGP','Synthetic evaluation fixture']
 for j,line in enumerate(lines):d.text((60,70+j*90),line,font=font,fill='black')
 im.save(F/f'{i}.png')
 texts={'Tesseract full page':pytesseract.image_to_string(im,lang='ara+eng',config=f'--tessdata-dir "{ROOT}/data/tessdata" --psm 6')}
 result,_=engine(np.array(im));texts['Paddle PP-OCR full page']='\n'.join(str(x[1]) for x in result) if result else ''
 for k,text in texts.items():
  got={}
  for field,pattern in [('quantity',r'(?:quantity|qty)\s*[:=]?\s*(\d+)'),('total',r'total\s*[:=]?\s*([\d,]+)'),('date',r'(\d{4}-\d{2}-\d{2})'),('supplier',r'supplier\s*:\s*([^\n]+)')]:
   m=re.search(pattern,text,re.I)
   if m:got[field]=m.group(1).strip().replace(',','').lower()
  pred[k].append(got)
def f1(ref,pred):
 tp=sum(sum(g.get(k)==v for k,v in r.items()) for r,g in zip(ref,pred));fp=sum(sum(k not in r or r[k]!=v for k,v in g.items()) for r,g in zip(ref,pred));fn=sum(sum(g.get(k)!=v for k,v in r.items()) for r,g in zip(ref,pred));return 2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0
comp=[{'model':k,'validationFieldF1':f1(rows[:4],v[:4])} for k,v in pred.items()];win=max(comp,key=lambda x:x['validationFieldF1'])['model']
report={'data':'8 generated English full-page receipts, 4 validation / 4 test, four fields each','comparison':comp,'selected':win,'testFieldF1':f1(rows[4:],pred[win][4:]),'limitations':'Synthetic clean fixtures only. They verify extraction plumbing; no claim of Arabic real-receipt field accuracy. Ties prefer the simpler Tesseract installation.'}
(ROOT/'results/receipt_fields.json').write_text(json.dumps(report,indent=2));print(report)
