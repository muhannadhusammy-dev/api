"""Download upstream model weights. Uses HTTPS and atomic file replacement."""
from pathlib import Path
import argparse,json,urllib.request,hashlib
ROOT=Path(__file__).resolve().parents[1]
hashes=json.loads((ROOT/'data/MODEL_HASHES.json').read_text())
def verify(path, artifact=None):
 expected=hashes.get(str((artifact or path).relative_to(ROOT)).replace('\\','/'))
 if expected and hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise RuntimeError('Model hash differs from evaluated artifact: '+str(path))
p=argparse.ArgumentParser();p.add_argument('--voice',action='store_true');p.add_argument('--all-voice',action='store_true');p.add_argument('--embedding',action='store_true');a=p.parse_args()
def get(url,path):
 path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():verify(path);print('Exists:',path);return
 print('Downloading',path.name,flush=True);tmp=path.with_suffix(path.suffix+'.part')
 try:
  urllib.request.urlretrieve(url,tmp);verify(tmp,path);tmp.replace(path)
 except Exception:
  tmp.unlink(missing_ok=True);raise
if a.voice or a.all_voice:
 report=ROOT/'results/speech.json';selected=json.loads(report.read_text())['selected'].split()[-1].lower() if report.exists() else 'base'
 for size in (['base','small'] if a.all_voice else [selected]):
  for name in ['config.json','model.bin','tokenizer.json','vocabulary.txt']:
   get(f'https://huggingface.co/Systran/faster-whisper-{size}/resolve/main/{name}',ROOT/'data/speech'/size/name)
if a.embedding:
 for name,remote in [('model_quantized.onnx','onnx/model_quantized.onnx'),('tokenizer.json','tokenizer.json'),('config.json','config.json')]:
  get('https://huggingface.co/Xenova/paraphrase-multilingual-MiniLM-L12-v2/resolve/main/'+remote,ROOT/'data/embedding'/name)
if not any(vars(a).values()):p.print_help()
