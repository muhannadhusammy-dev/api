from pathlib import Path
import json,re,time
from faster_whisper import WhisperModel
from jiwer import wer
from scipy.io import wavfile
import numpy as np
from common import ROOT,normalize
D=ROOT/'data/speech';items=json.loads((D/'labels.json').read_text());results=[];predictions={}
for size in ['base','small']:
 print('Whisper',size,flush=True);model=WhisperModel(str(D/size),device='cpu',compute_type='int8',cpu_threads=2)
 preds=[];start=time.perf_counter()
 for row in items:
  rate,wave=wavfile.read(D/row['file']); assert rate==16000
  wave=wave.astype(np.float32) if wave.dtype.kind=="f" else wave.astype(np.float32)/32768
  segments,_=model.transcribe(wave,language='ar',beam_size=3,vad_filter=False,condition_on_previous_text=False)
  pred=' '.join(x.text for x in segments);preds.append(pred);print(row['file'],pred,flush=True)
 refs=[normalize(r['text']) for r in items];norm=[normalize(x) for x in preds]
 results.append({'model':'Whisper '+size.title(),'validationWER':wer(refs[:4],norm[:4]),'secondsAll8':time.perf_counter()-start});predictions[size]=preds
win=min(results,key=lambda x:x['validationWER'])['model'];key=win.split()[-1].lower()
report={'data':'First 8 FLEURS ar_eg test clips: first 4 development validation, next 4 held-out test. Read Arabic speech, NOT validated conversational Egyptian dialect.','comparison':results,'selected':win,'testWER':wer([normalize(r['text']) for r in items[4:]],[normalize(x) for x in predictions[key][4:]]),'normalization':'Lowercase, Arabic diacritics removed, alef/ya normalization, punctuation removed, spaces collapsed.','limitations':'Very small convenience pilot. This cannot establish merchant speech accuracy, dialect robustness or noise robustness. No fine-tuning.','predictions':predictions}
(ROOT/'results/speech.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(report,flush=True)
