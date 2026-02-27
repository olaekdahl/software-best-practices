from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import time

STATE = {"db_ok": True, "queue_depth": 0}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path == "/health":
            ok = STATE["db_ok"]
            body = f'{{"status":"{"ok" if ok else "degraded"}","queue_depth":{STATE["queue_depth"]}}}'.encode()
            self.send_response(200 if ok else 503)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

def main() -> None:
    server = HTTPServer(("127.0.0.1", 0), Handler)
    host, port = server.server_address
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    print(f"Health endpoint running at http://{host}:{port}/health")
    print("Simulating health changes...")
    time.sleep(0.2)
    STATE["queue_depth"] = 12
    time.sleep(0.2)
    STATE["db_ok"] = False
    time.sleep(0.2)

    server.shutdown()
    server.server_close()
    print("Stopped.")

if __name__ == "__main__":
    main()
