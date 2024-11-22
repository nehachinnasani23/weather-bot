import pytest
from app import app, saved_locations


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to the Weather Bot" in response.data


def test_save_valid_city(client):
    saved_locations.clear()
    response = client.post("/save-city", data={"city": "London"})
    assert response.status_code == 200
    assert response.json["message"] == "City 'London' saved successfully!"
    assert "London" in saved_locations


def test_save_duplicate_city(client):
    saved_locations.clear()
    saved_locations.append("London")
    response = client.post("/save-city", data={"city": "London"})
    assert response.status_code == 400
    assert response.json["error"] == "City 'London' is already saved."


def test_save_empty_city(client):
    response = client.post("/save-city", data={"city": ""})
    assert response.status_code == 400
    assert response.json["error"] == "City not provided."


def test_geo_weather_valid(client, monkeypatch):
    def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 200

            @staticmethod
            def json():
                return {
                    "name": "London",
                    "main": {"temp": 10.5},
                    "weather": [{"description": "clear sky", "icon": "01d"}],
                }

        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)
    response = client.get("/geo-weather?lat=51.5074&lon=-0.1278")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "London"
    assert data["temperature"] == 10.5
    assert data["description"] == "Clear sky"


def test_geo_weather_valid(client, monkeypatch):
    # Mock the API response for geo-weather
    def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 200

            @staticmethod
            def json():
                return {
                    "name": "London",
                    "main": {"temp": 10.5},
                    "weather": [{"description": "clear sky", "icon": "01d"}],
                }

        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)  # Mock the requests.get function
    response = client.get("/geo-weather?lat=51.5074&lon=-0.1278")
    assert response.status_code == 200
    data = response.get_json()  # Use get_json() to parse JSON directly
    assert data["city"] == "London"
    assert data["temperature"] == 10.5
    assert data["description"] == "Clear sky"



def test_weather_invalid_city(client, monkeypatch):
    def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 404

            @staticmethod
            def json():
                return {"message": "City not found"}

        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)
    response = client.post("/", data={"cities": "InvalidCity"})
    assert response.status_code == 200
    assert b"City 'InvalidCity' not found" in response.data


def test_weather_empty_city(client):
    response = client.post("/", data={"cities": ""})
    assert response.status_code == 200
    assert b"Please enter at least one city name" in response.data
