import pytest

from app import app


@pytest.fixture
def client(tmp_path):
    app.config["TESTING"] = True
    app.config["DATA_FILE"] = str(tmp_path / "submissions.json")
    with app.test_client() as client:
        yield client


GOOD = {
    "name": "Nayab",
    "reg_no": "SP23-BCS-046",
    "title": "Lab Mid",
    "url": "https://github.com/nayab917/lab-mid",
}


def test_valid_submission_is_saved_and_listed(client):
    response = client.post("/", data=GOOD, follow_redirects=True)
    assert response.status_code == 200
    assert b"Submission saved." in response.data, "Valid submission was not saved"
    assert b"SP23-BCS-046" in response.data, "Saved submission is not shown in the list"


def test_missing_registration_number_is_rejected(client):
    data = dict(GOOD, reg_no="")
    response = client.post("/", data=data)
    assert b"Registration number is required." in response.data, "Missing registration number was not rejected"
    assert b"Submission saved." not in response.data, "Submission without registration number was saved"


def test_invalid_url_is_rejected_and_not_saved(client):
    data = dict(GOOD, url="not-a-link")
    response = client.post("/", data=data)
    assert b"Submission URL is not valid" in response.data, "Invalid URL was not rejected"
    page = client.get("/")
    assert b"not-a-link" not in page.data, "Submission with invalid URL was saved"
