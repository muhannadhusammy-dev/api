"""Build the editable final presentation; photos originate in the supplied Grad deck."""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/TajerOS_Final_Presentation.pptx'
p=Presentation();p.slide_width=Inches(13.333);p.slide_height=Inches(7.5)
BG='F7F7F2';INK='254D41';MUTED='65776A';ACCENT='81966B';PALE='E8EDDF';WHITE='FFFFFF'
def rect(s,x,y,w,h,color,round=False):
    sh=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if round else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h));sh.fill.solid();sh.fill.fore_color.rgb=RGBColor.from_string(color);sh.line.fill.background();return sh

def text(s,value,x,y,w,h,size=22,color=INK,bold=False):
    sh=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=sh.text_frame;tf.word_wrap=True
    tf.margin_left=tf.margin_right=Inches(.02);tf.margin_top=tf.margin_bottom=0
    for i,line in enumerate(value.split('\n')):
        paragraph=tf.paragraphs[0] if i==0 else tf.add_paragraph();paragraph.text=line;paragraph.font.name='Aptos';paragraph.font.size=Pt(size);paragraph.font.bold=bold;paragraph.font.color.rgb=RGBColor.from_string(color);paragraph.space_after=Pt(14)
    return sh

def slide(title,section='BUSINESS',note=''):
    s=p.slides.add_slide(p.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=RGBColor.from_string(BG)
    rect(s,0,0,13.333,.09,INK);text(s,'T A J E R O S   /   '+section,.6,.4,11,.3,11,ACCENT,True)
    text(s,title,.6,1,12.1,1.1,34,INK,True)
    rect(s,.6,7.02,12.1,.012,'DCE2D4');text(s,'TAGER AI  •  Graduation project  •  Local academic prototype',.6,7.14,11,.2,10,MUTED)
    text(s,f'{len(p.slides):02}',12.05,7.1,.65,.25,11,MUTED)
    s.notes_slide.notes_text_frame.text=note
    return s

def picture(s,path,x,y,w,h):
    im=Image.open(path);ratio=im.width/im.height
    if ratio>w/h:nw=w;nh=w/ratio
    else:nh=h;nw=h*ratio
    s.shapes.add_picture(str(path), Inches(x+(w-nw)/2), Inches(y+(h-nh)/2), width=Inches(nw),height=Inches(nh))

def points(s,items,x=.65,y=2.35,w=6,h=4.25,size=23):
    text(s,'\n'.join('•  '+item for item in items),x,y,w,h,size)

def two(title,items,image,section='BUSINESS',note=''):
    s=slide(title,section,note);points(s,items,w=5.8,size=22);picture(s,ROOT/image,6.9,2.25,5.8,4.4);return s

s=slide('TAGER AI | TajerOS','RETAIL INTELLIGENCE','Introduce the original team and supervisors from the supplied Grad presentation. Explain that this is a tested academic prototype, not a production ERP.')
text(s,'Your business.\nIn your own words.',.65,2.3,7,2.1,46,INK,True)
text(s,'Business operations + sales intelligence + AI support',.68,4.6,8,.55,23,MUTED)
rect(s,9.2,2.4,3.4,2.4,PALE,True);text(s,'REVIEW\nAPPROVE\nACT',9.65,2.75,2.7,1.8,27,INK,True)
text(s,'Muhannad Husam · Adel Mostafa · Hisham Ashraf · Mohammad Tawif',.68,5.7,12,.4,18)
text(s,'Supervised by Eng. Shrouq Diaa & Eng. Mohammad Halim',.68,6.25,12,.35,17,MUTED)

s=slide('One story, two perspectives','OUTLINE','Follow the structure of the previous Grad deck: explain the business value first, then show the technical evidence and demonstration.')
rect(s,.65,2.3,5.8,4.1,WHITE,True);rect(s,6.85,2.3,5.8,4.1,PALE,True)
text(s,'01  Business value',.95,2.65,5,.5,26,INK,True);points(s,['The business problem','Our solution and target market','Dashboard and decision support','Business model and impact'],.95,3.4,5,3,23)
text(s,'02  Technical proof',7.15,2.65,5,.5,26,INK,True);points(s,['Architecture and approvals','Forecasting and document AI','Live demo and test evidence','Setup and next steps'],7.15,3.4,5,3,23)

two('The business problem',['Manual entry slows daily operations.','Reports explain the past; planning needs more context.','Stock and price mistakes distort profit.','Managers need traceable decisions.'],'docs/presentation_assets/image1.jpeg',note='Avoid claiming a measured business impact: no deployment study was supplied. Describe the problem and why the prototype addresses it.')
two('Our solution: TajerOS',['A single workspace for business records.','Arabic text commands and receipt OCR.','Owner approval before stock or money changes.','A separate dashboard for sales analysis.'],'docs/presentation_assets/image2.jpeg',note='The two applications are separate: business operations use local transactional data; Streamlit uses an uploaded sales CSV. They do not automatically synchronize.')
s=slide('Who is it for?','BUSINESS','These are proposed users and benefits. Customer acquisition and market sizing were not validated in this project.')
for x,title,body in [(0.65,'Shop owners','Review transactions, track stock\nand understand gross profit.'),(4.85,'Store staff','Capture business activity\nwithout approval authority.'),(9.05,'Retail analysts','Explore weekly sales\nand compare forecasting models.')]:
 rect(s,x,2.5,3.65,3.7,WHITE,True);text(s,title,x+.25,2.85,3.1,.65,26,INK,True);text(s,body,x+.25,3.9,3.1,1.9,22,MUTED)
two('Smart business dashboard',['Approved inventory and ledger records.','Gross profit = revenue minus goods cost.','Pending proposals remain separate.','Staff and owner permissions differ.'],'docs/screenshots/business-dashboard.png',note='This screenshot is from the current running application. Rice and sugar opening stock are demo assumptions. Gross profit excludes expenses and tax.')
two('Sales & store intelligence',['6,435 historical records across 45 stores.','Store filters, weekly trends and comparisons.','CSV upload for a new dataset.','Download selected records and forecasts.'],'docs/screenshots/sales-dashboard.png',note='The included Walmart data covers 2010–2012 and records monetary sales. Do not describe it as current Egyptian demand, product-level sales or unit quantities. The currency selector changes a label, not the numbers.')
two('AI demand forecasting',['Ridge and Random Forest candidates.','A 52-week seasonal-repeat baseline.','Chronological holdout; compare by MAE.','4–12 future weeks after the last data date.'],'docs/screenshots/sales-forecast.png',note='The lowest recent holdout MAE selects the model, then models are refit on all history. The same holdout is used for selection: it is not an independent final test. Missing weekly dates disable forecasting; forecasts remain estimates.')
two('Inventory & decision support',['Purchase approvals increase stock.','Sales approvals use weighted average cost.','Returns reverse the original sale cost.','Short history is disclosed before estimating.'],'docs/presentation_assets/image6.jpeg',note='The business app requires at least 14 distinct sales days before a shop-specific heuristic estimate. Streamlit sales currency is insufficient to derive reorder units without inventory and supplier lead-time data.')
s=slide('Business model & future impact','BUSINESS','This follows the prior deck. Describe a potential subscription model, not realized revenue. Production expansion requires customer validation, current data and operational hardening.')
points(s,['Proposed subscription plans by store size.','Potential value: less reporting work and clearer decisions.','Future integrations: point of sale, suppliers and current stock feeds.','Validate usefulness with store managers before scaling.'],w=11.8,size=27)

s=slide('Architecture: clear responsibilities','TECHNICAL','C# alone owns transactional business state. Python inference returns suggestions. Streamlit is a separate analytics app. The optional LLM receives facts/excerpts, not database write access.')
for x,title,body in [(.65,'React + TypeScript','Interface, forms, review\nand bilingual navigation'),(4.85,'ASP.NET Core 10','Authentication, approvals,\nledger and audit trail'),(9.05,'Python / FastAPI','Intent extraction, OCR,\nretrieval and optional speech')]:
 rect(s,x,2.5,3.65,2.25,PALE,True);text(s,title,x+.2,2.8,3.25,.6,23,INK,True);text(s,body,x+.2,3.65,3.25,.9,19,MUTED)
text(s,'→',4.35,3.15,.5,.6,29);text(s,'→',8.55,3.15,.5,.6,29)
text(s,'SQLite by default  •  PostgreSQL option via Docker Compose',.75,5.15,11.8,.5,24)
text(s,'Separate analytics path: CSV → Pandas → scikit-learn → Streamlit → optional OpenAI',.75,6,11.8,.7,21,MUTED)

s=slide('From suggestion to a controlled change','TECHNICAL','No model can post a sale or change stock. Staff submits; owner reviews and approves. Approval uses a database transaction and a write gate. Version checks reject stale updates. This is not a claim of multi-instance production concurrency readiness.')
for i,(title,body) in enumerate([('1  Capture','Text, receipt\nor manual review'),('2  Propose','Pending fields\nand warnings'),('3  Review','Price, quantity\nand anomalies'),('4  Approve','Owner-only\ntransaction')]):
 x=.65+i*3.15;rect(s,x,2.7,2.8,2.5,WHITE,True);text(s,title,x+.2,3,2.4,.6,24,INK,True);text(s,body,x+.2,3.9,2.4,1,22,MUTED)
text(s,'Version checks  •  Repeat-safe approvals  •  Stock validation  •  Audit records',.7,5.8,12,.6,24)
two('Receipt OCR: extract, then verify',['PNG/JPEG input with size limits.','Tesseract Arabic + English recognition.','Quantity and total appear in a review form.','8 synthetic fixtures checked on this build.'],'docs/screenshots/receipt-review.png','TECHNICAL','Show the current receipt screen. All eight synthetic receipts produced the expected quantity and total in current HTTP testing. That is not an accuracy estimate for real invoices. The form handles one reviewed product line.')
s=slide('Two AI assistants, explicit boundaries','TECHNICAL','Document Q&A works with BM25 and exact excerpts without a paid API. Optional LLM document generation checks citation IDs but does not automatically prove semantic grounding. Streamlit uses OpenAI Responses and aggregate statistics. Neither external provider route was executed because no key was supplied.')
rect(s,.65,2.35,5.8,3.8,WHITE,True);rect(s,6.85,2.35,5.8,3.8,PALE,True)
text(s,'Document evidence',.95,2.7,5.2,.5,26,INK,True);points(s,['Search approved company policies.','Return excerpts and citations.','Abstain when evidence is missing.'],.95,3.5,5.1,2.5,22)
text(s,'Optional LLM advisor',7.15,2.7,5.1,.5,26,INK,True);points(s,['Receives calculated sales facts.','Needs an operator-supplied API key.','Suggestions only; no record changes.'],7.15,3.5,5.1,2.5,22)
s=slide('Forecasting: method and honest limits','TECHNICAL','Features are time index and yearly/half-year sine/cosine components. Validation uses the most recent 4–12 weeks depending on history length. At least 30 consecutive weeks are needed. Seasonal repeat is available when sufficient history exists. No causal or guaranteed predictive claim.')
points(s,['Date trend and seasonality features; no future sales leakage.','Latest weeks held out for a chronological comparison.','MAE is in the selected sales currency; lower is better.','Invalid/infinite values are removed; gaps block forecasts.','No inventory, profit or order quantities are inferred from sales money.'],w=12,size=25)
s=slide('Live demo: follow the numbers','DEMONSTRATION','Use a fresh local demo database and owner account. Upload the synthetic receipt, create a purchase proposal and approve. Propose an Arabic sale, supply total selling price, approve. Activate a returns workflow, submit 2 cartons against the sale and approve. Ask the returns policy question and show citations.')
rows=[['Step','Action','Expected result'],['Purchase','50 cartons / EGP 12,000','Stock 50; cost 240/carton'],['Sale','15 cartons / EGP 4,500','Stock 35; gross profit 900'],['Return','2 cartons from that sale','Stock 37; gross profit 780'],['Policy Q&A','Ask about returns','Source excerpts + citations']]
table=s.shapes.add_table(5,3, Inches(.65), Inches(2.4), Inches(12), Inches(3.5)).table
for col,width in zip(table.columns,[2,5,5]):col.width=Inches(width)
for i,row in enumerate(rows):
 for j,v in enumerate(row):
  c=table.cell(i,j);c.text=v;c.fill.solid();c.fill.fore_color.rgb=RGBColor.from_string(INK if i==0 else WHITE)
  for par in c.text_frame.paragraphs:par.font.size=Pt(20);par.font.color.rgb=RGBColor.from_string(WHITE if i==0 else INK);par.font.bold=i==0
text(s,'Gross profit excludes expenses and tax. Approval is required at every posting step.',.7,6.25,12,.55,20,MUTED)
s=slide('Current delivery: validation evidence','VERIFICATION','These are distinct check categories, not a single statistical accuracy metric. Integration uses a fresh SQLite database. Dashboard tests use Streamlit AppTest. Browser smoke uses local Chromium. OCR uses supplied synthetic fixtures. Prior research reports remain included but were not recomputed in this delivery.')
for x,y,value,label in [(.65,2.4,'27','Business integration checks'),(6.85,2.4,'4','Dashboard regression tests'),(.65,4.45,'13','Browser smoke checks'),(6.85,4.45,'11','Media / AI service checks')]:
 rect(s,x,y,5.8,1.7,WHITE,True);text(s,value,x+.25,y+.2,1.4,1,48,INK,True);text(s,label,x+1.7,y+.5,3.8,.8,22,MUTED)
text(s,'.NET build: 0 warnings / 0 errors  •  TypeScript + Vite build passed',.7,6.55,12,.35,19)
s=slide('Ready for a local demonstration','DELIVERY & LIMITATIONS','Linux native setup and SQLite are validated. Windows scripts and Docker/PostgreSQL are supplied but untested in this delivery. Voice requires external weights and LLM routes need a key. No paid provider request or speech inference was executed. Production work includes password management, deployment, multi-tenant isolation, backups, observability and independent forecast backtesting.')
points(s,['Included: source, demo data, scripts, tests, documentation and this deck.','Start with QUICKSTART.md; run the workspace or sales dashboard.','Optional: download voice weights and configure an LLM API key.','Not yet verified: Windows execution and Docker/PostgreSQL.','Next: real-store trials, current data and production deployment controls.'],w=12,size=25)
s=slide('Thank you — questions?','TAGER AI','Suggested defense questions: Why human approval? Why chronological validation? Why not infer stock from monetary sales? What data goes to the LLM? Which current checks passed, and what remains untested? Source provenance is in data/SOURCES.json and docs/THIRD_PARTY_NOTICES.md. Photos are retained from the user-supplied Grad.pptx; screenshots were captured from the current applications.')
text(s,'Less paperwork.\nMore informed decisions.',.7,2.35,11.8,2.0,46,INK,True)
text(s,'Demonstrate the evidence. Explain the limits. Keep managers in control.',.75,5.0,11.8,.8,26,MUTED)
p.core_properties.title='TAGER AI | TajerOS — Final Project Presentation';p.core_properties.subject='Business value, architecture, demonstration and current validation';p.core_properties.author='TajerOS project team'
p.save(OUT)
# Structural validation also catches out-of-slide shapes.
r=Presentation(OUT)
for i,s in enumerate(r.slides,1):
 for sh in s.shapes:
  assert sh.left>=0 and sh.top>=0 and sh.left+sh.width<=r.slide_width+100 and sh.top+sh.height<=r.slide_height+100,(i,sh.name)
 assert s.notes_slide.notes_text_frame.text.strip(),i
print(f'Saved {OUT}: {len(r.slides)} slides, all with speaker notes and in-bounds shapes')
