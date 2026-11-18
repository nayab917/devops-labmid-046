"""Reads pytest's results.xml, builds the JSON test report and sends it (and optionally an email)."""
import json
import os
import smtplib
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.message import EmailMessage


def build_report(xml_file):
    tests = []
    if os.path.exists(xml_file):
        for case in ET.parse(xml_file).getroot().iter("testcase"):
            problem = case.find("failure")
            if problem is None:
                problem = case.find("error")
            tests.append({
                "name": case.get("name"),
                "result": "failed" if problem is not None else "passed",
                "failure_message": (problem.get("message") or "").split("\n")[0] if problem is not None else None,
            })
    passed = sum(t["result"] == "passed" for t in tests)
    failed = len(tests) - passed
    return {
        "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
        "branch": os.environ.get("GITHUB_REF_NAME", "local"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tests": tests,
        "summary": {
            "total": len(tests),
            "passed": passed,
            "failed": failed,
            "status": "passed" if tests and failed == 0 else "failed",
        },
    }


def send_to_receiver(report, url, token):
    request = urllib.request.Request(
        url,
        data=json.dumps(report).encode(),
        headers={"Content-Type": "application/json", "X-Report-Token": token},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        print("Receiver answered:", response.status, response.read().decode())


def send_email(report):
    user, password, to = (os.environ.get(k) for k in ("SMTP_USER", "SMTP_PASSWORD", "REPORT_EMAIL"))
    if not (user and password and to):
        print("Email settings not found, skipping email.")
        return
    s = report["summary"]
    msg = EmailMessage()
    msg["Subject"] = f"Test report: {s['status'].upper()} ({s['passed']}/{s['total']} passed) - {report['commit_sha'][:7]}"
    msg["From"] = user
    msg["To"] = to
    lines = [f"Repository: {report['repository']}", f"Branch: {report['branch']}",
             f"Commit: {report['commit_sha']}", f"Run ID: {report['run_id']}",
             f"Overall result: {s['status']}",
             f"Total: {s['total']}, Passed: {s['passed']}, Failed: {s['failed']}", "", "Tests:"]
    for t in report["tests"]:
        lines.append(f"- {t['name']}: {t['result']}" + (f" ({t['failure_message']})" if t["failure_message"] else ""))
    msg.set_content("\n".join(lines))
    msg.add_attachment(json.dumps(report, indent=2).encode(), maintype="application",
                       subtype="json", filename="test-report.json")
    with smtplib.SMTP_SSL(os.environ.get("SMTP_SERVER", "smtp.gmail.com"), 465) as server:
        server.login(user, password)
        server.send_message(msg)
    print("Email sent to", to)


if __name__ == "__main__":
    report = build_report("results.xml")
    for t in report["tests"]:
        print(f"{t['result'].upper():7} {t['name']}")
    s = report["summary"]
    print(f"Total: {s['total']}  Passed: {s['passed']}  Failed: {s['failed']}  Status: {s['status']}")
    ok = True
    url = os.environ.get("REPORT_URL")
    if url:
        try:
            send_to_receiver(report, url, os.environ.get("REPORT_TOKEN", ""))
        except Exception as e:
            print("Could not reach the receiver:", e)
            ok = False
    else:
        print("REPORT_URL not set, not sending.")
    try:
        send_email(report)
    except Exception as e:
        print("Could not send email:", e)
        ok = False
    sys.exit(0 if ok else 1)
