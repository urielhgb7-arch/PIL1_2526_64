def test_matieres_endpoint_returns_200(client):
    response = client.get('/api/matieres')
    assert response.status_code == 200
