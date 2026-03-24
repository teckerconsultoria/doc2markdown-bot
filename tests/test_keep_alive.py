import os
import time
import urllib.request
import pytest

TEST_PORT = 18080
BASE_URL = f"http://localhost:{TEST_PORT}"


@pytest.fixture(scope="session", autouse=True)
def keep_alive_server():
    """Sobe o servidor uma única vez para toda a sessão de testes."""
    os.environ["PORT"] = str(TEST_PORT)
    from keep_alive import start_keep_alive
    start_keep_alive()
    time.sleep(0.3)  # aguardar thread subir
    yield  # testes rodam aqui
    # servidor é daemon — encerra automaticamente com o processo


def test_health_endpoint_returns_200():
    """GET /health deve retornar 200 com body contendo 'ok'."""
    with urllib.request.urlopen(f"{BASE_URL}/health") as resp:
        assert resp.status == 200
        assert "ok" in resp.read().decode()


def test_root_endpoint_returns_200():
    """GET / deve retornar 200."""
    with urllib.request.urlopen(f"{BASE_URL}/") as resp:
        assert resp.status == 200
