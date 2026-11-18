"""Prints every test and its result as a table for the GitHub Actions run summary."""
from send_report import build_report

report = build_report("results.xml")
s = report["summary"]
icon = "✅" if s["status"] == "passed" else "❌"

print(f"## {icon} Test results: {s['status'].upper()} ({s['passed']}/{s['total']} passed)")
print()
print("| # | Test | Result | Failure message |")
print("|---|---|---|---|")
for i, t in enumerate(report["tests"], 1):
    mark = "✅ passed" if t["result"] == "passed" else "❌ failed"
    print(f"| {i} | `{t['name']}` | {mark} | {t['failure_message'] or '-'} |")
print()
print(f"**Total:** {s['total']} &nbsp; **Passed:** {s['passed']} &nbsp; **Failed:** {s['failed']}")
print()
print(f"Commit `{report['commit_sha'][:7]}` · Run ID `{report['run_id']}`")
