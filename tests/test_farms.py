from tests.conftest import client


def test_create_farm(client):
    """Test farm creation with valid data."""
    response = client.post("/api/v1/farms", json={
        "state": "Maharashtra",
        "district": "Pune",
        "village": "Hadapsar",
        "area_hectare": 1.5,
        "soil_type": "black",
        "irrigation_type": "tube_well",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["state"] == "Maharashtra"
    assert data["district"] == "Pune"
    assert data["area_hectare"] == 1.5
    assert "id" in data


def test_create_farm_invalid_area(client):
    """Test farm creation rejects non-positive area."""
    response = client.post("/api/v1/farms", json={
        "state": "Maharashtra",
        "district": "Pune",
        "area_hectare": 0,
    })
    assert response.status_code == 422


def test_get_farm_not_found(client):
    """Test fetching a non-existent farm returns 404."""
    response = client.get("/api/v1/farms/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Farm not found"


def test_add_soil_test(client):
    """Test adding a soil test to a farm."""
    create_resp = client.post("/api/v1/farms", json={
        "state": "Maharashtra",
        "district": "Pune",
        "area_hectare": 2.0,
    })
    farm_id = create_resp.json()["id"]

    response = client.post(f"/api/v1/farms/{farm_id}/soil-test", json={
        "ph": 7.2,
        "nitrogen": 12.5,
        "phosphorus": 8.3,
        "potassium": 45.0,
        "organic_carbon": 0.8,
        "test_date": "2024-10-01",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["ph"] == 7.2
    assert data["farm_id"] == farm_id


def test_add_soil_test_invalid_ph(client):
    """Test soil test rejects out-of-range pH."""
    create_resp = client.post("/api/v1/farms", json={
        "state": "Maharashtra",
        "district": "Pune",
        "area_hectare": 2.0,
    })
    farm_id = create_resp.json()["id"]

    response = client.post(f"/api/v1/farms/{farm_id}/soil-test", json={
        "ph": 15.0,  # invalid
        "test_date": "2024-10-01",
    })
    assert response.status_code == 422