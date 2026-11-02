"""Reproducible small-scope comparisons. Never mix benchmark scores with shop data."""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='3';os.environ['TF_NUM_INTRAOP_THREADS']='1';os.environ['TF_NUM_INTEROP_THREADS']='1'
from pathlib import Path
import json,time,hashlib
import numpy as np,pandas as pd,joblib
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import f1_score,accuracy_score,confusion_matrix,mean_absolute_error,mean_squared_error
from sklearn.ensemble import RandomForestRegressor,IsolationForest
from sklearn.preprocessing import StandardScaler
from lightgbm import LGBMRegressor
from common import ROOT,normalize,Embedder
R=ROOT/'results';R.mkdir(exist_ok=True);np.random.seed(42)
report={'seed':42,'status':'measured','sources':{'retail':'https://raw.githubusercontent.com/GonzaloBP/Almacen-de-datos-Walmart/main/Walmart.csv','ocr':'https://huggingface.co/datasets/abdoelsayed/CORU','speech':'https://huggingface.co/datasets/google/fleurs','embedding':'https://huggingface.co/Xenova/paraphrase-multilingual-MiniLM-L12-v2'}}
def save(): (R/'benchmarks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('Intent benchmark',flush=True)
rows=json.loads((ROOT/'data/intents.json').read_text());sets={k:[r for r in rows if r['split']==k] for k in ['train','validation','test']};X={k:[r['text'] for r in a] for k,a in sets.items()};y={k:[r['intent'] for r in a] for k,a in sets.items()}
models={'TF-IDF + Linear SVM':make_pipeline(TfidfVectorizer(analyzer='char',ngram_range=(2,5),preprocessor=normalize),LinearSVC(random_state=42)), 'TF-IDF + Logistic Regression':make_pipeline(TfidfVectorizer(analyzer='char',ngram_range=(2,5),preprocessor=normalize),LogisticRegression(max_iter=2000,random_state=42))}
emb=Embedder();E={k:emb.encode(text) for k,text in X.items()};models['Multilingual transformer + LR']=LogisticRegression(max_iter=2000,random_state=42)
comparison=[]
for name,m in models.items():
 start=time.perf_counter();m.fit(E['train'] if name.startswith('Multilingual') else X['train'],y['train']);pred=m.predict(E['validation'] if name.startswith('Multilingual') else X['validation']);comparison.append({'model':name,'validationMacroF1':f1_score(y['validation'],pred,average='macro'),'validationAccuracy':accuracy_score(y['validation'],pred),'fitSeconds':time.perf_counter()-start})
win=sorted(comparison,key=lambda a:-a['validationMacroF1'])[0]['model'];m=models[win];pred=m.predict(E['test'] if win.startswith('Multilingual') else X['test']);classes=sorted(set(y['train']))
joblib.dump({'name':win,'model':m},R/'intent.joblib')
report['intent']={'data':'150 authored development utterances, not customer conversations','counts':{k:len(v) for k,v in X.items()},'comparison':comparison,'selected':win,'testMacroF1':f1_score(y['test'],pred,average='macro'),'testAccuracy':accuracy_score(y['test'],pred),'classes':classes,'confusionMatrix':confusion_matrix(y['test'],pred,labels=classes).tolist(),'limitations':'Small authored split with distinct phrases, overlapping vocabulary and no independent customer sampling. Frozen transformer embeddings plus LR, not end-to-end fine-tuning.'};save()
print(report['intent'],flush=True)
print('Forecast benchmark',flush=True)
df=pd.read_csv(ROOT/'data/walmart.csv');df['Date']=pd.to_datetime(df.Date,dayfirst=True);df=df.sort_values(['Store','Date']);g=df.groupby('Store').Weekly_Sales
for lag in [1,2,4,52]:df[f'lag{lag}']=g.shift(lag)
df['rolling4']=g.transform(lambda s:s.shift(1).rolling(4).mean());df['week']=df.Date.dt.isocalendar().week.astype(int);df['sin']=np.sin(df.week*2*np.pi/52);df['cos']=np.cos(df.week*2*np.pi/52);df=df.dropna();dates=sorted(df.Date.unique());tr=dates[:-36];va=dates[-36:-18];te=dates[-18:];features=['Store','Holiday_Flag','lag1','lag2','lag4','lag52','rolling4','sin','cos'];parts={k:df[df.Date.isin(d)] for k,d in [('train',tr),('validation',va),('test',te)]}
mods={'Seasonal Naive (52 weeks)':None,'Random Forest':RandomForestRegressor(n_estimators=120,min_samples_leaf=3,random_state=42,n_jobs=2),'LightGBM':LGBMRegressor(n_estimators=200,num_leaves=15,max_depth=6,learning_rate=.05,random_state=42,verbosity=-1,n_jobs=2)}
def metrics(y,p):return {'MAE':float(mean_absolute_error(y,p)),'RMSE':float(np.sqrt(mean_squared_error(y,p))),'WAPE':float(np.sum(np.abs(np.asarray(y)-p))/np.sum(np.abs(y)))}
comp=[]
for name,m in mods.items():
 start=time.perf_counter()
 if m is not None:m.fit(parts['train'][features],parts['train'].Weekly_Sales)
 p=parts['validation'].lag52.to_numpy() if m is None else m.predict(parts['validation'][features]);comp.append({'model':name,**metrics(parts['validation'].Weekly_Sales,p),'fitSeconds':time.perf_counter()-start})
win=min(comp,key=lambda x:x['WAPE'])['model'];m=mods[win];test=parts['test'];p=test.lag52.to_numpy() if m is None else m.predict(test[features]);test=test.assign(prediction=p)
series=test.groupby('Date')[['Weekly_Sales','prediction']].sum().reset_index();series['Date']=series.Date.dt.strftime('%Y-%m-%d');series.to_csv(R/'forecast_test_series.csv',index=False);joblib.dump({'name':win,'model':m,'features':features},R/'forecast.joblib')
report['forecast']={'data':'Historical Walmart US store-week sales, 45 stores. Currency USD, not EGP or units.','rows':{k:len(v) for k,v in parts.items()},'dates':{k:[str(v.Date.min().date()),str(v.Date.max().date())] for k,v in parts.items()},'comparison':comp,'selected':win,'test':metrics(test.Weekly_Sales,p),'series':series.to_dict('records'),'limitations':'Rolling one-week-ahead evaluation uses actual preceding observations. It is not a fixed-origin 18-week forecast and not Egyptian shop validation.'};save();print(report['forecast']['test'],flush=True)
print('Anomaly benchmark (unlabelled)',flush=True)
import tensorflow as tf
tf.keras.utils.set_random_seed(42)
A=np.c_[df.Weekly_Sales/df.lag1-1,df.Weekly_Sales/df.lag52-1,df.Weekly_Sales/df.rolling4-1,df.Holiday_Flag]
train_mask=df.Date.isin(tr).to_numpy();test_mask=df.Date.isin(te).to_numpy();scale=StandardScaler();at=scale.fit_transform(A[train_mask]);ae=scale.transform(A[test_mask]);iso=IsolationForest(n_estimators=150,contamination=.05,random_state=42).fit(at)
net=tf.keras.Sequential([tf.keras.layers.Input((4,)),tf.keras.layers.Dense(8,activation='relu'),tf.keras.layers.Dense(2,activation='relu'),tf.keras.layers.Dense(8,activation='relu'),tf.keras.layers.Dense(4)])
net.compile(optimizer='adam',loss='mse');net.fit(at,at,epochs=25,batch_size=32,verbose=0)
median=np.median(at,axis=0);mad=np.median(np.abs(at-median),axis=0);mad[mad<.01]=1
scores={'Robust statistical rule':(np.max(np.abs(at-median)/mad,axis=1),np.max(np.abs(ae-median)/mad,axis=1)),'Isolation Forest':(-iso.score_samples(at),-iso.score_samples(ae)),'Autoencoder':(np.mean((at-net(at,training=False).numpy())**2,axis=1),np.mean((ae-net(ae,training=False).numpy())**2,axis=1))}
report['anomaly']={'data':'Same real retail rows; no verified anomaly labels','comparison':[{'model':name,'threshold':float(np.quantile(a,.95)),'testAlerts':int((b>np.quantile(a,.95)).sum()),'testAlertRate':float((b>np.quantile(a,.95)).mean())} for name,(a,b) in scores.items()],'testRows':len(ae),'selected':None,'limitations':'No precision, recall, F1 or accuracy can be measured. Alert counts do not establish which detector is best. Live purchase-cost alerts use an explicit 35% business rule, not this retail model.'};save()
# Retrieval evaluation uses authored policies and qrels; independent phrases are listed in the package.
print('Retrieval benchmark',flush=True)
from rank_bm25 import BM25Okapi
policies=[('returns','Unopened goods can be returned within 14 days with a receipt. المنتجات غير المفتوحة ترجع خلال 14 يوم مع الفاتورة.'),('approval','Owner approval is mandatory before refunds. رد الفلوس يحتاج موافقة المالك.'),('purchasing','Purchases above 5000 EGP require owner approval. شراء فوق 5000 جنيه يحتاج موافقة المالك.'),('oil','Oil supplier lead time is 3 days and safety stock is 10 cartons. توريد الزيت 3 ايام ومخزون الامان 10 كراتين.'),('credit','Customer credit limit is 2000 EGP. الحد الائتماني للعميل 2000 جنيه.'),('discount','Maximum cashier discount is 5 percent. الخصم المسموح للكاشير 5 بالمية.'),('delivery','Local delivery fee is 30 EGP. رسوم التوصيل المحلي 30 جنيه.'),('hours','The shop opens at 9 AM and closes at 11 PM. المحل يفتح 9 الصبح ويقفل 11 بالليل.'),('damage','Damaged goods must be photographed and quarantined. البضاعة التالفة تتصور وتتعزل.'),('backup','The owner reviews daily backups at closing. المالك يراجع النسخ الاحتياطي يوميا عند القفل.'),('rice','Rice supplier requires two days lead time. توريد الارز يحتاج يومين.'),('payment','Cash and bank transfer are accepted. الدفع كاش او تحويل بنكي.'),('staff','New staff require owner-created accounts. حساب الموظف الجديد ينشئه المالك.'),('stocktake','Count stock every Sunday morning. جرد المخزون كل احد الصبح.'),('expenses','Record rent separately from cost of goods sold. سجل الايجار منفصل عن تكلفة البضاعة المباعة.')]
queries=[('How long can I return unopened items?','returns'),('مين يوافق على رد الفلوس','approval'),('شراء بست الاف يحتاج موافقة مين','purchasing'),('امتى المورد يوصل الزيت','oil'),('العميل ممكن ياخد اجل بكام','credit'),('اقصى خصم للكاشير كام','discount'),('التوصيل المحلي بكام','delivery'),('المحل بيقفل الساعة كام','hours'),('اعمل ايه في البضاعة التالفة','damage'),('مين يراجع النسخة الاحتياطية','backup'),('When can a customer bring goods back?','returns'),('هل الموظف يقدر يعمل ريفند لوحده','approval'),('فاتورة مورد كبيرة محتاجة اعتماد','purchasing'),('مخزون امان الزيت قد ايه','oil'),('What is the customer credit cap?','credit'),('What discount may the cashier offer?','discount'),('How much does local shipping cost?','delivery'),('What time does the shop open?','hours'),('متى يتم جرد الاصناف','stocktake'),('Where should rent be recorded?','expenses')]
texts=[t for _,t in policies];bm=BM25Okapi([normalize(t).split() for t in texts]);de=emb.encode(texts);qe=emb.encode([q for q,_ in queries]);raw={name:[] for name in ['BM25','Multilingual embeddings','Hybrid RRF']}
for i,(q,target) in enumerate(queries):
 bs=bm.get_scores(normalize(q).split());es=de@qe[i];br=np.argsort(-bs);er=np.argsort(-es);rrf=np.zeros(len(texts))
 for rank,ix in enumerate(br):rrf[ix]+=1/(60+rank+1)
 for rank,ix in enumerate(er):rrf[ix]+=1/(60+rank+1)
 for name,rank in [('BM25',br),('Multilingual embeddings',er),('Hybrid RRF',np.argsort(-rrf))]:
  pos=[policies[j][0] for j in rank].index(target)+1;raw[name].append((int(pos<=5),1/pos if pos<=5 else 0))
comp=[{'model':n,'validationRecall5':float(np.mean([x[0] for x in a[:10]])),'validationMRR5':float(np.mean([x[1] for x in a[:10]]))} for n,a in raw.items()];win=sorted(comp,key=lambda x:(-x['validationRecall5'],-x['validationMRR5']))[0]['model'];vals=raw[win][10:]
report['retrieval']={'data':'15 authored bilingual policies; 10 validation and 10 held-out authored questions','comparison':comp,'selected':win,'testRecall5':float(np.mean([x[0] for x in vals])),'testMRR5':float(np.mean([x[1] for x in vals])),'limitations':'One relevant policy per query. Source-span integrity is tested separately; retrieval recall is not generated-answer correctness.'};(ROOT/'data/retrieval_fixture.json').write_text(json.dumps({'policies':policies,'queries':queries},ensure_ascii=False,indent=2));save()
print('Tabular/text benchmarks done',flush=True)
