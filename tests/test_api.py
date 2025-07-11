import sys
import os
import pytest

# 👇 This line makes sure Python can find `calculator.py`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from calculator import app  # ✅ Now this will work!

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_add_route(client):
    response = client.get("/add?a=10&b=5")
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data["result"] == 15.0

def test_add_missing_params(client):
    response = client.get("/add")
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data["result"] == 0.0

def test_add_invalid_input(client):
    response = client.get("/add?a=abc&b=5")
    assert response.status_code == 400
