import requests
import json

# URL base da API
BASE_URL = "http://127.0.0.1:8000"

def test_criar_hiperfoco():
    """Testa a criação de um novo hiperfoco."""
    url = f"{BASE_URL}/hiperfocos/"
    dados = {
        "titulo": "Meu Primeiro Hiperfoco",
        "descricao": "Este é um teste de hiperfoco",
        "cor": "#3b82f6"
    }
    
    response = requests.post(url, json=dados)
    
    print("\n=== Teste de Criação de Hiperfoco ===")
    print(f"Status Code: {response.status_code}")
    print("Resposta:", json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    assert response.status_code == 200
    assert "id" in response.json()
    
    return response.json()

def test_listar_hiperfocos():
    """Testa a listagem de hiperfocos."""
    url = f"{BASE_URL}/hiperfocos/"
    response = requests.get(url)
    
    print("\n=== Teste de Listagem de Hiperfocos ===")
    print(f"Status Code: {response.status_code}")
    print("Resposta:", json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    return response.json()

if __name__ == "__main__":
    # Executa os testes
    print("=== Iniciando Testes da API ===\n")
    
    # Testa a criação de um hiperfoco
    novo_hiperfoco = test_criar_hiperfoco()
    
    # Testa a listagem de hiperfocos
    hiperfocos = test_listar_hiperfocos()
    
    # Verifica se o hiperfoco criado está na lista
    hiperfoco_ids = [h.get('id') for h in hiperfocos]
    assert novo_hiperfoco['id'] in hiperfoco_ids, "O hiperfoco criado não foi encontrado na listagem!"
    
    print("\n=== Todos os testes foram concluídos com sucesso! ===")
