# devops-labmid-046: Assignment Submission Portal

DevOps Lab Mid, Nayab (SP23-BCS-046).

Students enter their name, registration number, assignment title and submission URL.
The portal validates the fields and the URL, saves valid submissions in `submissions.json`,
and shows all saved submissions. Every push runs the tests in GitHub Actions and sends a JSON
test report to a receiver running on my computer, where it is saved as `test-report.json`.

## Project files

| File | Purpose |
|---|---|
| `app.py` | Flask web application (the portal) |
| `templates/index.html` | Page with the form and the list of submissions |
| `tests/test_portal.py` | Automated tests (pytest) |
| `send_report.py` | Builds the JSON test report and sends it to the receiver (and by email) |
| `receiver.py` | Local HTTP receiver that saves the report as `test-report.json` |
| `.github/workflows/ci.yml` | CI pipeline: test, send report, deploy demo to GitHub Pages |
| `docs/index.html` | Static demo of the portal for GitHub Pages |

## Run the application

```
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

## Run the tests

```
python -m pytest -v
```

## Start the receiver

Terminal 1:

```
python receiver.py
```

Terminal 2 (tunnel, so GitHub can reach the receiver):

```
cloudflared tunnel --url http://localhost:5001
```

Copy the `https://....trycloudflare.com` address into the GitHub secret `REPORT_URL`.
`REPORT_TOKEN` must match `TOKEN` in `receiver.py`. Keep both terminals open.

## GitHub secrets

| Secret | Value |
|---|---|
| `REPORT_URL` | Tunnel address |
| `REPORT_TOKEN` | Same as TOKEN in receiver.py |
| `SMTP_USER`, `SMTP_PASSWORD`, `REPORT_EMAIL` | Gmail address, Gmail app password, email that receives the report (bonus) |

## Live demo

https://nayab917.github.io/devops-labmid-046/
