from pathlib import Path
import json,hashlib,time,shutil
import pytesseract,numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR
from jiwer import cer
from common import ROOT,normalize
D=ROOT/'data/ocr_evaluation';files=sorted(D.glob('*.txt'),key=lambda p:hashlib.sha256(p.name.encode()).hexdigest())[:40]
engine=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=1)
refs=[];pred={'Tesseract Arabic+English':[],'Paddle PP-OCR via RapidOCR ONNX':[]};times={k:0 for k in pred};manifest=[]
for i,p in enumerate(files):
 ref=' '.join(json.loads(p.read_text()));img=p.with_suffix('.jpg');refs.append(normalize(ref));im=Image.open(img).convert('RGB');start=time.perf_counter()
 txt=pytesseract.image_to_string(im,lang='ara+eng',config=f'--tessdata-dir "{ROOT}/data/tessdata" --psm 7');pred['Tesseract Arabic+English'].append(normalize(txt));times['Tesseract Arabic+English']+=time.perf_counter()-start
 start=time.perf_counter();result,_=engine(np.array(im),use_det=False,use_cls=False,use_rec=True)
 txt=' '.join(str(x[0]) for x in result) if result else '';pred['Paddle PP-OCR via RapidOCR ONNX'].append(normalize(txt));times['Paddle PP-OCR via RapidOCR ONNX']+=time.perf_counter()-start
 manifest.append({'file':p.name,'reference':ref,'split':'validation' if i<20 else 'test'})
 if i%10==0:print(i,ref,txt,flush=True)
# Use the first half for choosing between these exact configurations.
comp=[{'model':k,'validationCER':cer(refs[:20],v[:20]),'secondsAll40':times[k]} for k,v in pred.items()];win=min(comp,key=lambda x:x['validationCER'])['model']
report={'data':'40 CORU OCR line crops selected deterministically by filename SHA-256; 20 development validation / 20 held-out test.','comparison':comp,'selected':win,'testCER':cer(refs[20:],pred[win][20:]),'normalization':'Same Arabic normalization and punctuation removal for both systems. Annotation tokens joined in supplied order.','limitations':'This evaluates recognition on pre-cropped lines, not full-page detection or field extraction. RapidOCR ships a Chinese/English Paddle-trained recognizer, not an Arabic-tuned PaddleOCR model; comparison does not establish the best Arabic PaddleOCR configuration. Tiny pilot only.','manifest':manifest,'predictions':pred}
(ROOT/'results/ocr.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(report['comparison'],report['testCER'],flush=True)
# Keep the small evaluated subset for reproducibility, rather than the full download.
subset=ROOT/'data/ocr_evaluation';subset.mkdir(exist_ok=True)
# The bundled subset is the source; no copy is required.
