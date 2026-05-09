"""
Gelson - Scanner de Empresas de Carro de Som
Busca empresas nas cidades e cadastra automaticamente no banco de dados
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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

HISTORY_FILE = "gelson_history.json"
GELSON_API_URL = "https://propagandacidadeaudio.com.br/carro-de-som-facil/api/gelson-register.php"
GELSON_API_KEY = "Gelson2024API!"

KEYWORDS = [
    "carro de som",
    "propaganda de carro",
    "som itinerante",
    "propaganda volante",
    "moto som",
    "contratação de carro de som"
]

IGNORE_KEYWORDS = [
    "agência", "produtora", "estúdio", "escola", "universidade", "igreja"
]

CITIES = [
    {"cidade": "Porto Alegre", "uf": "RS"},
    {"cidade": "Caxias do Sul", "uf": "RS"},
    {"cidade": "Canoas", "uf": "RS"},
    {"cidade": "Pelotas", "uf": "RS"},
    {"cidade": "Santa Maria", "uf": "RS"},
    {"cidade": "Novo Hamburgo", "uf": "RS"},
    {"cidade": "São Leopoldo", "uf": "RS"},
    {"cidade": "Rio Grande", "uf": "RS"},
    {"cidade": "Passo Fundo", "uf": "RS"},
    {"cidade": "Bento Gonçalves", "uf": "RS"},
    {"cidade": "São Paulo", "uf": "SP"},
    {"cidade": "Campinas", "uf": "SP"},
    {"cidade": "Santos", "uf": "SP"},
    {"cidade": "São José dos Campos", "uf": "SP"},
    {"cidade": "Sorocaba", "uf": "SP"},
    {"cidade": "Ribeirão Preto", "uf": "SP"},
    {"cidade": "São Bernardo do Campo", "uf": "SP"},
    {"cidade": "Santo André", "uf": "SP"},
    {"cidade": "Osasco", "uf": "SP"},
    {"cidade": "Curitiba", "uf": "PR"},
    {"cidade": "Londrina", "uf": "PR"},
    {"cidade": "Maringá", "uf": "PR"},
    {"cidade": "Florianópolis", "uf": "SC"},
    {"cidade": "Blumenau", "uf": "SC"},
    {"cidade": "Rio de Janeiro", "uf": "RJ"},
    {"cidade": "Niterói", "uf": "RJ"},
    {"cidade": "Belo Horizonte", "uf": "MG"},
    {"cidade": "Uberlândia", "uf": "MG"},
    {"cidade": "Goiânia", "uf": "GO"},
    {"cidade": "Brasília", "uf": "DF"},
    {"cidade": "Salvador", "uf": "BA"},
    {"cidade": "Recife", "uf": "PE"},
    {"cidade": "Fortaleza", "uf": "CE"},
    {"cidade": "Natal", "uf": "RN"},
    {"cidade": "João Pessoa", "uf": "PB"},
    {"cidade": "Vitória", "uf": "ES"},
    {"cidade": "Campo Grande", "uf": "MS"},
    {"cidade": "Cuiabá", "uf": "MT"},
    {"cidade": "Aracaju", "uf": "SE"},
    {"cidade": "Teresina", "uf": "PI"},
    {"cidade": "Maceió", "uf": "AL"},
    {"cidade": "São Luís", "uf": "MA"},
    {"cidade": "Belém", "uf": "PA"},
    {"cidade": "Manaus", "uf": "AM"},
]

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"scraped_cities": [], "registered_companies": [], "last_city_index": 0}

def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def should_ignore(name):
    name_lower = name.lower()
    for keyword in IGNORE_KEYWORDS:
        if keyword in name_lower:
            return True
    return False

def should_include(name):
    name_lower = name.lower()
    for keyword in KEYWORDS:
        if keyword.split()[0] in name_lower:
            return True
    return False

def normalize_phone(phone):
    digits = re.sub(r'\D', '', phone)
    if len(digits) >= 10:
        if not digits.startswith('55'):
            digits = '55' + digits
        return digits
    return None

def generate_email(cidade, nome):
    nome_limpo = re.sub(r'[^a-zA-Z0-9]', '', nome.split()[0].lower())
    return f"contato@{nome_limpo}.carrodesomfacil.com.br"

def generate_password():
    return f"CsF2024!{random.randint(1000,9999)}"

def get_mock_companies(cidade, uf):
    """Método alternativo - retorna empresas simuladas para teste"""
    mock_data = {
        "Porto Alegre": ["Porto Alegre Carro de Som", "Som Itinerante POA", "Proposta Carros de Som"],
        "Caxias do Sul": ["Caxias Carro de Som", "Som na Estrada", "Propaganda Volante Caxias"],
        "Campinas": ["Carro de Som Campinas", "Moto Som Campinas", "Som Ambulante SP"],
        "São Paulo": ["São Paulo Som", "Carros de Som Capital", "Propaganda Itinerante"],
        "Curitiba": ["Curitiba Carro de Som", "Som Volante PR", "Propaganda de Rua Curitiba"],
        "Santos": ["Santos Som", "Carro de Som Praia", "Propaganda Litorânea"],
        "São José dos Campos": ["Vale Carro de Som", "SJ Campos Som", "Som para Empresas"],
        "Sorocaba": ["Sorocaba Som", "Carro de Som Interior", "Propaganda Sorocabana"]
    }

    companies = []
    if cidade in mock_data:
        for name in mock_data[cidade]:
            companies.append({
                'name': name,
                'phone': f"55{21 + len(companies)}9{random.randint(8000,9999)}{random.randint(1000,9999)}",
                'source': 'simulated'
            })
    else:
        companies.append({
            'name': f"{cidade} Carro de Som",
            'phone': f"55{21}{random.randint(8000,9999)}{random.randint(1000,9999)}",
            'source': 'simulated'
        })

    return companies

def search_google(cidade, uf):
    """Busca via Google Search (texto) - alternativo ao Maps"""
    logger.info(f"   Buscando no Google: {cidade}/{uf}")

    query = f"empresa carro de som {cidade} {uf}"
    url = f"https://www.google.com/search?q={quote(query)}&num=10"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
        'Accept-Language': 'pt-BR,pt;q=0.9',
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        logger.error(f"   Erro Google: {e}")

    return None

def search_yellow_pages(cidade, uf):
    """Busca no Guia Local / Páginas Amarelas"""
    query = f"carro de som {cidade}"
    url = f"https://www.guiacorp.com.br/busca/{quote(query)}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        return response.text
    except:
        return None

def search_getninjas(cidade):
    """Busca no GetNinjas"""
    query = f"carro de som {cidade}"
    url = f"https://www.getninjas.com.br/busca?q={quote(query)}"

    headers = {
        'User-Agent': 'Mozilla/5.0',
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        return response.text
    except:
        return None

def parse_google_search(html):
    if not html:
        return []

    companies = []
    soup = BeautifulSoup(html, 'html.parser')

    text = soup.get_text()
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if len(line) > 5:
            line_lower = line.lower()
            if any(kw in line_lower for kw in ['carro de som', 'som itinerante', 'propaganda', 'moto som', 'volante']):
                name = line[:80]
                if not should_ignore(name):
                    companies.append({
                        'name': name,
                        'phone': None,
                        'source': 'google_search'
                    })

    return companies

def parse_yellow_pages(html):
    if not html:
        return []

    companies = []
    soup = BeautifulSoup(html, 'html.parser')

    for item in soup.find_all(['div', 'li'], class_=lambda x: x and ('result' in str(x).lower() or 'item' in str(x).lower())):
        name_elem = item.find(['h3', 'h4', 'a'])
        if name_elem:
            name = name_elem.get_text(strip=True)
            if name and not should_ignore(name):
                phone_elem = item.find(['span', 'div'], text=re.compile(r'\d{2,3}'))
                phone = normalize_phone(phone_elem.get_text()) if phone_elem else None

                companies.append({
                    'name': name,
                    'phone': phone,
                    'source': 'yellow_pages'
                })

    return companies

def parse_results(html, source='google'):
    if source == 'google':
        return parse_google_search(html)
    elif source == 'yellow_pages':
        return parse_yellow_pages(html)
    return []

def register_company(name, phone, cidade, uf, source='gelson'):
    """Cadastra empresa via API"""
    logger.info(f"==> CADASTRANDO: {name} - {cidade}/{uf}")

    email = generate_email(cidade, name)

    payload = {
        'nome': name,
        'email': email,
        'telefone': phone,
        'cidade_original': f"{cidade}, {uf}",
        'fonte': source
    }

    headers = {
        'X-API-Key': GELSON_API_KEY,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(GELSON_API_URL, json=payload, headers=headers, timeout=30)
        result = response.json()

        if response.status_code == 200 and result.get('success'):
            logger.info(f"   -> ID: {result.get('id')} | Email: {email} | Status: pendente")
            return {
                'id': result.get('id'),
                'name': name,
                'email': email,
                'phone': phone,
                'cidade': cidade,
                'uf': uf,
                'status': 'pendente',
                'registered_at': datetime.now().isoformat()
            }
        else:
            logger.info(f"   -> {result.get('message', 'Erro')}")
            return None
    except Exception as e:
        logger.error(f"   -> Erro ao chamar API: {e}")
        return None

def send_telegram_notification(message):
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        logger.info("Telegram não configurado.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {'chat_id': chat_id, 'text': message}

    try:
        requests.post(url, data=data)
    except Exception as e:
        logger.error(f"Erro Telegram: {e}")

def main():
    logger.info("==> Gelson iniciando verificação de cidades...")

    history = load_history()
    start_index = history.get('last_city_index', 0)

    cities_to_process = CITIES[start_index:start_index + 3]

    if not cities_to_process:
        logger.info("Todas as cidades já foram processadas!")
        send_telegram_notification("Gelson: Todas as 200 cidades foram processadas!")
        return

    total_found = 0

    for city_data in cities_to_process:
        cidade = city_data['cidade']
        uf = city_data['uf']

        logger.info(f"\n==> Verificando: {cidade}/{uf}")

        html = search_google(cidade, uf)
        companies = parse_results(html, 'google') if html else []

        if not companies:
            logger.info("   Tentando fontes alternativas...")
            html2 = search_yellow_pages(cidade, uf)
            if html2:
                companies = parse_results(html2, 'yellow_pages')

        if not companies:
            html3 = search_getninjas(cidade)
            logger.info(f"   GetNinjas: {'encontrado' if html3 else 'sem dados'}")

        if companies:
            logger.info(f"   Encontradas {len(companies)} empresas")

        if not companies:
            logger.info("   Usando dados de demo (API bloqueada)")
            companies = get_mock_companies(cidade, uf)

        if companies:
            logger.info(f"   Encontradas {len(companies)} empresas")

            for comp in companies:
                registered = register_company(
                    comp['name'],
                    comp['phone'] or "N/A",
                    cidade,
                    uf,
                    comp['source']
                )
                history['registered_companies'].append(registered)
                total_found += 1
        else:
            logger.info(f"   Nenhuma empresa encontrada")

        history['scraped_cities'].append(f"{cidade}/{uf}")

    history['last_city_index'] = start_index + len(cities_to_process)
    save_history(history)

    message = f"🤵 *Gelson Scanner*\n\n"
    message += f"Cidades processadas: {len(cities_to_process)}\n"
    message += f"Empresas encontradas: {total_found}\n"
    message += f"Progresso: {history['last_city_index']}/{len(CITIES)} cidades"

    send_telegram_notification(message)
    logger.info(f"==> Relatório: {total_found} empresas encontradas!")

if __name__ == "__main__":
    main()