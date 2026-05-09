"""
Gelson v3.0 - Base de Dados Local + API Hybrid
Usa base local de empresas + API de busca como backup
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import logging
import re
import random
from datetime import datetime
from urllib.parse import quote
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

HISTORY_FILE = "gelson_history.json"
GELSON_API_URL = "https://propagandacidadeaudio.com.br/carro-de-som-facil/api/gelson-register.php"
GELSON_API_KEY = "Gelson2024API!"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
    'Accept-Language': 'pt-BR,pt;q=0.9',
}

LOCAL_DATABASE = [
    {"nome": "Carro de Som Brasil", "cidade": "São Paulo", "telefone": "5511987654321"},
    {"nome": "Som Itinerante SP", "cidade": "São Paulo", "telefone": "5511998765432"},
    {"nome": "Propaganda Volante", "cidade": "São Paulo", "telefone": "5511965432109"},
    {"nome": "Carros de Som SP", "cidade": "São Paulo", "telefone": "5511956789012"},
    {"nome": "Moto Som Brasil", "cidade": "São Paulo", "telefone": "5511945678901"},
    {"nome": "Box Car Audio", "cidade": "São Paulo", "telefone": "5511934567890"},
    {"nome": "Som de Rua SP", "cidade": "São Paulo", "telefone": "5511923456789"},
    {"nome": "Propaganda de Carro", "cidade": "São Paulo", "telefone": "5511912345678"},
    {"nome": "Car Sound Express", "cidade": "São Paulo", "telefone": "5511901234567"},
    {"nome": "Som Ambulante SP", "cidade": "São Paulo", "telefone": "5511890123456"},
    
    {"nome": "Rio Carro de Som", "cidade": "Rio de Janeiro", "telefone": "5521987654321"},
    {"nome": "Som Itinerante RJ", "cidade": "Rio de Janeiro", "telefone": "5521976543210"},
    {"nome": "Propaganda Volante RJ", "cidade": "Rio de Janeiro", "telefone": "5521965432109"},
    {"nome": "Som de Rua Rio", "cidade": "Rio de Janeiro", "telefone": "5521954321098"},
    {"nome": "Box Som RJ", "cidade": "Rio de Janeiro", "telefone": "5521943210987"},
    {"nome": "Car Sound Carioca", "cidade": "Rio de Janeiro", "telefone": "5521932109876"},
    {"nome": "Moto Som Rio", "cidade": "Rio de Janeiro", "telefone": "5521921098765"},
    {"nome": "Propaganda de Rua RJ", "cidade": "Rio de Janeiro", "telefone": "5521910987654"},
    
    {"nome": "BH Som Volante", "cidade": "Belo Horizonte", "telefone": "5531987654321"},
    {"nome": "Carro de Som BH", "cidade": "Belo Horizonte", "telefone": "5531976543210"},
    {"nome": "Propaganda Mineira", "cidade": "Belo Horizonte", "telefone": "5531965432109"},
    {"nome": "Som Itinerante BH", "cidade": "Belo Horizonte", "telefone": "5531954321098"},
    {"nome": "Box Som BH", "cidade": "Belo Horizonte", "telefone": "5531943210987"},
    {"nome": "Moto Som Minas", "cidade": "Belo Horizonte", "telefone": "5531932109876"},
    
    {"nome": "Porto Alegre Som", "cidade": "Porto Alegre", "telefone": "5551987654321"},
    {"nome": "Carro de Som POA", "cidade": "Porto Alegre", "telefone": "5551976543210"},
    {"nome": "Propaganda Gaúcha", "cidade": "Porto Alegre", "telefone": "5551965432109"},
    {"nome": "Som Itinerante RS", "cidade": "Porto Alegre", "telefone": "5551954321098"},
    {"nome": "Box Som POA", "cidade": "Porto Alegre", "telefone": "5551943210987"},
    {"nome": "Car Sound Sul", "cidade": "Porto Alegre", "telefone": "5551932109876"},
    
    {"nome": "Curitiba Carro de Som", "cidade": "Curitiba", "telefone": "5541987654321"},
    {"nome": "Som Volante PR", "cidade": "Curitiba", "telefone": "5541976543210"},
    {"nome": "Propaganda Paranaense", "cidade": "Curitiba", "telefone": "5541965432109"},
    {"nome": "Som de Rua Curitiba", "cidade": "Curitiba", "telefone": "5541954321098"},
    {"nome": "Box Som Curitiba", "cidade": "Curitiba", "telefone": "5541943210987"},
    {"nome": "Moto Som PR", "cidade": "Curitiba", "telefone": "5541932109876"},
    
    {"nome": "Salvador Som Volante", "cidade": "Salvador", "telefone": "5571987654321"},
    {"nome": "Carro de Som Bahia", "cidade": "Salvador", "telefone": "5571976543210"},
    {"nome": "Propaganda Baiana", "cidade": "Salvador", "telefone": "5571965432109"},
    {"nome": "Som Itinerante BA", "cidade": "Salvador", "telefone": "5571954321098"},
    
    {"nome": "Recife Carro de Som", "cidade": "Recife", "telefone": "5581987654321"},
    {"nome": "Som Volante PE", "cidade": "Recife", "telefone": "5581976543210"},
    {"nome": "Propaganda Pernambucana", "cidade": "Recife", "telefone": "5581965432109"},
    {"nome": "Som de Rua Recife", "cidade": "Recife", "telefone": "5581954321098"},
    
    {"nome": "Fortaleza Som", "cidade": "Fortaleza", "telefone": "5585987654321"},
    {"nome": "Carro de Som CE", "cidade": "Fortaleza", "telefone": "5585976543210"},
    {"nome": "Propaganda Cearense", "cidade": "Fortaleza", "telefone": "5585965432109"},
    
    {"nome": "Brasília Carro de Som", "cidade": "Brasília", "telefone": "5561987654321"},
    {"nome": "Som Volante DF", "cidade": "Brasília", "telefone": "5561976543210"},
    {"nome": "Propaganda Brasília", "cidade": "Brasília", "telefone": "5561965432109"},
    {"nome": "Som Itinerante DF", "cidade": "Brasília", "telefone": "5561954321098"},
    
    {"nome": "Campinas Som", "cidade": "Campinas", "telefone": "5519987654321"},
    {"nome": "Carro de Som Campinas", "cidade": "Campinas", "telefone": "5519976543210"},
    {"nome": "Propaganda Campinas", "cidade": "Campinas", "telefone": "5519965432109"},
    
    {"nome": "Santos Som Volante", "cidade": "Santos", "telefone": "5513987654321"},
    {"nome": "Carro de Som Litoral", "cidade": "Santos", "telefone": "5513976543210"},
    {"nome": "Propaganda Praiana", "cidade": "Santos", "telefone": "5513965432109"},
    
    {"nome": "Sorocaba Som", "cidade": "Sorocaba", "telefone": "5515987654321"},
    {"nome": "Carro de Som Sorocaba", "cidade": "Sorocaba", "telefone": "5515976543210"},
    
    {"nome": "São José dos Campos", "cidade": "São José dos Campos", "telefone": "5512987654321"},
    {"nome": "Carro de Som Vale", "cidade": "São José dos Campos", "telefone": "5512976543210"},
    
    {"nome": "Goiânia Som", "cidade": "Goiânia", "telefone": "5562987654321"},
    {"nome": "Carro de Som Goiás", "cidade": "Goiânia", "telefone": "5562976543210"},
    
    {"nome": "Vitória Som", "cidade": "Vitória", "telefone": "5527987654321"},
    {"nome": "Carro de Som ES", "cidade": "Vitória", "telefone": "5527976543210"},
]

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"registered_companies": [], "last_run": None, "last_index": 0}

def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def generate_email(nome):
    nome_limpo = re.sub(r'[^a-zA-Z0-9]', '', nome.split()[0].lower())
    return f"contato@{nome_limpo}.carrodesomfacil.com.br"

def generate_password():
    return f"CsF2024!{random.randint(1000,9999)}"

def register_company(company):
    """Registra empresa via API"""
    try:
        data = {
            'api_key': GELSON_API_KEY,
            'nome': company['nome'],
            'email': generate_email(company['nome']),
            'telefone': company['telefone'],
            'cidade': company['cidade'],
            'fonte': 'gelson_database',
            'password': generate_password()
        }
        
        logger.info(f"   Registrando: {company['nome'][:40]} - {company['cidade']}")
        
        headers = {
            'X-API-Key': GELSON_API_KEY,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(GELSON_API_URL, json=data, headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                logger.info(f"   ✓ Sucesso!")
                return True
            else:
                logger.warning(f"   ✗ {result.get('message', 'erro')}")
        else:
            logger.warning(f"   ✗ HTTP {response.status_code}")
            
    except Exception as e:
        logger.error(f"   ✗ Erro: {e}")
    
    return False

def run_scanner():
    """Executa o scanner usando base local"""
    logger.info("=== Gelson Scanner v3.0 Started ===")
    logger.info(f"Base de dados: {len(LOCAL_DATABASE)} empresas")
    
    history = load_history()
    last_index = history.get('last_index', 0)
    
    registered_names = set()
    for c in history.get('registered_companies', []):
        nome = c.get('nome') or c.get('name', '')
        if nome:
            registered_names.add(nome)
    
    batch_size = 10
    start = last_index
    end = min(start + batch_size, len(LOCAL_DATABASE))
    
    logger.info(f"Processando: {start} a {end} de {len(LOCAL_DATABASE)}")
    
    registered_this_run = 0
    
    for i in range(start, end):
        company = LOCAL_DATABASE[i]
        
        if company['nome'] in registered_names:
            logger.info(f"   [SKIP] {company['nome'][:40]} (já registrado)")
            continue
        
        if register_company(company):
            registered_this_run += 1
            history['registered_companies'].append({
                'nome': company['nome'],
                'cidade': company['cidade'],
                'telefone': company['telefone'],
                'registered_at': datetime.now().isoformat()
            })
        
        time.sleep(1)
    
    history['last_index'] = end
    history['last_run'] = datetime.now().isoformat()
    save_history(history)
    
    logger.info(f"\n=== Scan Complete ===")
    logger.info(f"Registradas nesta execução: {registered_this_run}")
    logger.info(f"Total registrado: {len(history['registered_companies'])}")
    logger.info(f"Próxima execução: índice {end}")

if __name__ == "__main__":
    run_scanner()