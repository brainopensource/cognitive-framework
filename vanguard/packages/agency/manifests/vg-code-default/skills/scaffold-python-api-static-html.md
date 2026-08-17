# Skill: Scaffold Python API and Static HTML
Perform one action per turn to avoid multi-action proposal rejection:

- **Turn 1**: Write `app/server.py` via `Edit` (patch.apply with content):
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

- **Turn 2**: Write `static/index.html` via `Edit` (patch.apply with content):
```html
<!DOCTYPE html>
<html>
<head><title>App</title></head>
<body><h1>App</h1></body>
</html>
```

- **Turn 3**: Run tests via `Bash` (proc.exec):
```bash
python3 -m unittest test_app.py
```
