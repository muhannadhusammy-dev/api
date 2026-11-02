"""Wait for functional health responses from both local services."""
import json,time,urllib.request
for url in ['http://127.0.0.1:8091/health','http://127.0.0.1:5082/api/health']:
    for _ in range(120):
        try:
            with urllib.request.urlopen(url,timeout=2) as response:
                if json.load(response)['status']=='ok':break
        except (OSError, ValueError, KeyError):pass
        time.sleep(.5)
    else:raise SystemExit('Service did not become ready: '+url)
