"""Local report receiver: saves every test report it receives as test-report.json."""
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 5001
TOKEN = "nayab-046-secret"   # must match the REPORT_TOKEN secret on GitHub


class ReportHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.headers.get("X-Report-Token") != TOKEN:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b"wrong token")
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            report = json.loads(body)
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"not valid JSON")
            return
        with open("test-report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"[{datetime.now():%H:%M:%S}] Report saved: {report['summary']['status']} "
              f"({report['summary']['passed']}/{report['summary']['total']} passed), "
              f"commit {report['commit_sha'][:7]}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"saved")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Report receiver is running")


if __name__ == "__main__":
    print(f"Receiver listening on http://localhost:{PORT}")
    HTTPServer(("", PORT), ReportHandler).serve_forever()
