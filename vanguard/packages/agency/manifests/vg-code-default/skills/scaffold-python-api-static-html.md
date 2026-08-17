# Skill: Scaffold Python API and Static HTML
Concrete file layout to create for a Python HTTP API + Static HTML task:

1. Create `app/server.py` with standard library `http.server`:
```python
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
        else:
            super().do_GET()
```

2. Create `static/index.html`:
```html
<!DOCTYPE html>
<html>
<head><title>App</title></head>
<body><h1>App</h1></body>
</html>
```

3. Run verification tests:
```bash
python3 -m unittest test_app.py
```
