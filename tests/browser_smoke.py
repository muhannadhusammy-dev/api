"""Browser smoke checks against running local services; screenshots are real UI."""
from pathlib import Path
import json, os
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
checks=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.getenv('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto('http://127.0.0.1:5082')
    page.get_by_role('button',name='Open workspace').click()
    page.get_by_role('button',name='Overview',exact=True).wait_for()
    page.get_by_role('heading', name='Less paperwork. More room to grow.').wait_for()
    checks.append('Owner login renders workspace')
    page.screenshot(path=str(ROOT/'docs/screenshots/business-dashboard.png'),full_page=True)
    for name in ['Assistant','Receipts','Inventory','Workflows','Knowledge','AIOps','Evidence']:
        page.get_by_role('button',name=name,exact=True).click()
        page.wait_for_timeout(500)
        assert page.locator('main h1').is_visible(),name
        checks.append(name+' screen renders')
    page.get_by_role('button',name='Receipts',exact=True).click()
    page.locator('input[type=file]').first.set_input_files(str(ROOT/'data/demo_receipt.png'))
    page.get_by_role('heading',name='OCR transcript',exact=True).wait_for(timeout=30000)
    assert page.get_by_label('Quantity (cartons)').input_value()=='50'
    assert page.get_by_label('Total purchase cost (EGP)').input_value()=='12000'
    page.screenshot(path=str(ROOT/'docs/screenshots/receipt-review.png'),full_page=True)
    checks.append('Receipt OCR produces review form')
    page.get_by_role('button',name='العربية',exact=True).click()
    assert page.locator('.rtl').count()==1
    checks.append('Arabic right-to-left layout switches')
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 2')
    checks.append('Mobile layout fits viewport')
    assert not errors,errors
    checks.append('No browser JavaScript exceptions')
    page.set_viewport_size({'width':1440,'height':1000})
    page.goto('http://127.0.0.1:8501')
    page.get_by_text('Business dashboard',exact=True).wait_for(timeout=30000)
    page.get_by_text('USD 6,737,218,987',exact=True).wait_for(timeout=30000)
    page.wait_for_function("document.querySelectorAll('.js-plotly-plot').length >= 3")
    page.screenshot(path=str(ROOT/'docs/screenshots/sales-dashboard.png'),full_page=True)
    page.get_by_text('Forecast',exact=True).click()
    page.get_by_text('Future decisions | Forecasting',exact=True).wait_for()
    page.wait_for_timeout(1000)
    page.screenshot(path=str(ROOT/'docs/screenshots/sales-forecast.png'),full_page=True)
    checks.append('Live Streamlit dashboard and forecast render')
    browser.close()
(ROOT/'results/browser_smoke.json').write_text(json.dumps({'passed':len(checks),'checks':checks},indent=2))
print(json.dumps(checks,indent=2))
