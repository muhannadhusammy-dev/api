"""Live AI HTTP checks: real OCR fixtures, validation and missing-model response."""
import json,urllib.request,urllib.error,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def upload(path,filename,content,expected=200):
    boundary='tajer'+uuid.uuid4().hex
    body=(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode()+content+f'\r\n--{boundary}--\r\n'.encode())
    request=urllib.request.Request('http://127.0.0.1:8091/'+path,data=body,headers={'Content-Type':'multipart/form-data; boundary='+boundary})
    try:
        response=urllib.request.urlopen(request,timeout=60);status=response.status;result=json.load(response)
    except urllib.error.HTTPError as error:status=error.code;result=json.load(error)
    assert status==expected,(path,status,result)
    return result
for i in range(8):
    result=upload('ocr',f'{i}.png',(ROOT/f'data/receipt_fixtures/{i}.png').read_bytes())
    qty=10+i*5
    assert result['quantity']==qty and result['total']==qty*240,result
    checks.append(f'Synthetic receipt {i}: quantity and total match')
upload('ocr','invalid.png',b'not an image',400)
checks.append('Invalid image rejected')
with urllib.request.urlopen('http://127.0.0.1:8091/health') as response: health=json.load(response)
assert health['speechModel']=='small'
checks.append('Health reports selected speech model')
if not health['speechReady']:
    upload('transcribe','sample.wav',(ROOT/'data/speech/0.wav').read_bytes(),503)
    checks.append('Missing optional speech weights return clear 503')
(ROOT/'results/media_smoke.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'scope':'Synthetic OCR fixtures only; no speech transcription or real receipt accuracy claim'},indent=2))
print('\n'.join('PASS '+check for check in checks))
