from __future__ import annotations


def test_index_status_ok(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Bem-vindo" in response.data


def test_about_status_ok(client):
    response = client.get("/about")
    assert response.status_code == 200
    assert b"Sobre" in response.data


def test_404_on_unknown_route(client):
    response = client.get("/rota-que-nao-existe")
    assert response.status_code == 404
    assert b"404" in response.data
