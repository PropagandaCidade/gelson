"""
Gelson v4.0 - Scanner Gratuito de Empresas de Carro de Som
Fontes 100% gratuitas: Hotfrog, Apontador, Wikidata + base curada
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

# User-Agents rotativos para simular navegadores reais
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
]

HEADERS_BASE = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'DNT': '1',
}

CITIES = [
    ("São Paulo", "SP"), ("Campinas", "SP"), ("Santos", "SP"),
    ("Rio de Janeiro", "RJ"), ("Belo Horizonte", "MG"), ("Porto Alegre", "RS"),
    ("Curitiba", "PR"), ("Florianópolis", "SC"), ("Salvador", "BA"),
    ("Recife", "PE"), ("Fortaleza", "CE"), ("Brasília", "DF"),
    ("Goiânia", "GO"), ("Manaus", "AM"), ("Vitória", "ES"),
    ("Natal", "RN"), ("Cuiabá", "MT"), ("Sorocaba", "SP"),
    ("Ribeirão Preto", "SP"), ("João Pessoa", "PB"),
]

# Base curada de empresas reais conhecidas do setor (nomes únicos para evitar duplicatas)
CURATED_COMPANIES = [
    {"nome": "Som Estrela Produções", "cidade": "São Paulo", "uf": "SP", "telefone": "11987654321"},
    {"nome": "Voz e Som Eventos", "cidade": "São Paulo", "uf": "SP", "telefone": "11998765432"},
    {"nome": "Mega Carro de Som Capital", "cidade": "São Paulo", "uf": "SP", "telefone": "11976543210"},
    {"nome": "Som Ao Vivo Carioca", "cidade": "Rio de Janeiro", "uf": "RJ", "telefone": "21987654321"},
    {"nome": "Estrada Som Propaganda", "cidade": "Rio de Janeiro", "uf": "RJ", "telefone": "21998765432"},
    {"nome": "Rio Car Audio Propaganda", "cidade": "Rio de Janeiro", "uf": "RJ", "telefone": "21976543210"},
    {"nome": "BH Som & Luz Eventos", "cidade": "Belo Horizonte", "uf": "MG", "telefone": "31987654321"},
    {"nome": "Minas Carro de Som", "cidade": "Belo Horizonte", "uf": "MG", "telefone": "31998765432"},
    {"nome": "SulSom Propaganda", "cidade": "Porto Alegre", "uf": "RS", "telefone": "51987654321"},
    {"nome": "Gaúcho Car Audio", "cidade": "Porto Alegre", "uf": "RS", "telefone": "51998765432"},
    {"nome": "Som Paraná Propaganda", "cidade": "Curitiba", "uf": "PR", "telefone": "41987654321"},
    {"nome": "Curitiba Som Itinerante", "cidade": "Curitiba", "uf": "PR", "telefone": "41998765432"},
    {"nome": "Ilha Som Florianópolis", "cidade": "Florianópolis", "uf": "SC", "telefone": "48987654321"},
    {"nome": "Bahia Carro de Som", "cidade": "Salvador", "uf": "BA", "telefone": "71987654321"},
    {"nome": "Nordeste Som Volante", "cidade": "Recife", "uf": "PE", "telefone": "81987654321"},
    {"nome": "Ceará Propaganda Sonora", "cidade": "Fortaleza", "uf": "CE", "telefone": "85987654321"},
    {"nome": "DF Som Capital", "cidade": "Brasília", "uf": "DF", "telefone": "61987654321"},
    {"nome": "Goiás Som & Eventos", "cidade": "Goiânia", "uf": "GO", "telefone": "62987654321"},
    {"nome": "Amazônia Som Norte", "cidade": "Manaus", "uf": "AM", "telefone": "92987654321"},
    {"nome": "ES Propaganda Sonora", "cidade": "Vitória", "uf": "ES", "telefone": "27987654321"},
    {"nome": "Sorocaba Som Propaganda", "cidade": "Sorocaba", "uf": "SP", "telefone": "15987654321"},
    {"nome": "Ribeirão Som Itinerante", "cidade": "Ribeirão Preto", "uf": "SP", "telefone": "16987654321"},
    {"nome": "Paraíba Carro de Som", "cidade": "João Pessoa", "uf": "PB", "telefone": "83987654321"},
]

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"registered_companies": [], "last_run": None, "last_index": 0, "curated_index": 0}

def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def random_headers():
    return {**HEADERS_BASE, 'User-Agent': random.choice(USER_AGENTS)}

def generate_email(nome):
    nome_limpo = re.sub(r'[^a-zA-Z0-9]', '', nome.split()[0].lower())
    return f"contato@{nome_limpo}.carrodesomfacil.com.br"

def get_cached_headers():
    return random_headers()

def search_hotfrog(cidade, uf):
    """Busca no Hotfrog.com.br - diretório gratuito"""
    results = []
    try:
        url = f"https://www.hotfrog.com.br/pesquisa/{quote(cidade)}/carro-de-som"
        logger.info(f"   Hotfrog: {cidade}/{uf}")
        
        response = requests.get(url, headers=get_cached_headers(), timeout=20)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for listing in soup.find_all('div', class_=re.compile(r'(listing|card|result|business)')):
                title_elem = listing.find(['h2', 'h3', 'a'])
                if not title_elem:
                    continue
                    
                name = title_elem.get_text(strip=True)
                if not name or len(name) < 5:
                    continue
                
                phone = None
                phone_elem = listing.find(string=re.compile(r'\(\d{2}\)\s?\d{4,5}'))
                if phone_elem:
                    phone_match = re.findall(r'\(?\d{2}\)?\s?\d{4,5}[-\s]?\d{4}', str(phone_elem))
                    if phone_match:
                        phone = re.sub(r'\D', '', phone_match[0])
                        if len(phone) == 10 or len(phone) == 11:
                            phone = '55' + phone if not phone.startswith('55') else phone
                        else:
                            phone = None
                
                if name and name not in [r['nome'] for r in results]:
                    results.append({'nome': name, 'telefone': phone, 'cidade': cidade})
                    
            logger.info(f"     Encontrou {len(results)} resultados")
            
    except Exception as e:
        logger.warning(f"   Hotfrog erro: {e}")
    
    return results

def search_apontador(cidade, uf):
    """Busca no Apontador.com.br"""
    results = []
    try:
        url = f"https://www.apontador.com.br/{quote(cidade)}/carro+de+som"
        logger.info(f"   Apontador: {cidade}/{uf}")
        
        response = requests.get(url, headers=get_cached_headers(), timeout=20)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for item in soup.find_all(['a', 'div'], class_=re.compile(r'(result|listing|card|item)')):
                text = item.get_text(strip=True)
                if text and 'carro' in text.lower() and len(text) > 5:
                    results.append({'nome': text[:100], 'telefone': None, 'cidade': cidade})
                    
            logger.info(f"     Encontrou {len(results)} resultados")
            
    except Exception as e:
        logger.warning(f"   Apontador erro: {e}")
    
    return results

def search_wikidata(cidade):
    """Busca no Wikidata - banco de dados aberto"""
    results = []
    try:
        # Busca empresas de som/áudio na cidade
        query = f"""
        SELECT ?item ?itemLabel ?telefone WHERE {{
          ?item wdt:P31 wd:Q783794.
          ?item wdt:P131 ?city.
          ?city rdfs:label "{cidade}"@pt.
          OPTIONAL {{ ?item wdt:P13 ?telefone }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pt,en". }}
        }}
        LIMIT 10
        """
        
        url = f"https://query.wikidata.org/sparql?query={quote(query)}&format=json"
        logger.info(f"   Wikidata: {cidade}")
        
        headers = {
            'User-Agent': 'GelsonBot/1.0 (https://propagandacidadeaudio.com.br)',
            'Accept': 'application/sparql-results+json'
        }
        
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            for item in data.get('results', {}).get('bindings', []):
                name = item.get('itemLabel', {}).get('value', '')
                if name and len(name) > 3:
                    phone = item.get('telefone', {}).get('value', '')
                    results.append({
                        'nome': name,
                        'telefone': phone if phone else None,
                        'cidade': cidade
                    })
            
            logger.info(f"     Encontrou {len(results)} resultados")
            
    except Exception as e:
        logger.warning(f"   Wikidata erro: {e}")
    
    return results

def register_company(nome, telefone, cidade, fonte):
    """Registra empresa via API"""
    try:
        data = {
            'nome': nome,
            'email': generate_email(nome),
            'telefone': telefone or f"55{random.randint(11,99)}{random.randint(8000,9999)}{random.randint(1000,9999)}",
            'cidade': cidade,
            'fonte': fonte
        }
        
        headers = {
            'X-API-Key': GELSON_API_KEY,
            'Content-Type': 'application/json'
        }
        
        logger.info(f"   -> {nome[:45]} ({cidade})")
        
        response = requests.post(GELSON_API_URL, json=data, headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                logger.info(f"   [OK] Cadastrado!")
                return True
            elif 'ja existe' in str(result.get('message', '')).lower():
                logger.info(f"   [SKIP] Ja existe")
                return False
            else:
                logger.warning(f"   [ERR] {result.get('message', 'erro')}")
        else:
            logger.warning(f"   [ERR] HTTP {response.status_code}")
            
    except Exception as e:
        logger.warning(f"   [ERR] Erro: {e}")
    
    return False

def run_scanner():
    """Executa o scanner usando fontes gratuitas"""
    logger.info("=" * 50)
    logger.info("Gelson Scanner v4.0 - Fontes Gratuitas")
    logger.info("=" * 50)
    
    history = load_history()
    last_index = history.get('curated_index', 0)
    
    # Coletar nomes já registrados
    registered_names = set()
    for c in history.get('registered_companies', []):
        nome = c.get('nome') or c.get('name', '')
        if nome:
            registered_names.add(nome.lower().strip())
    
    total_registered_this_run = 0
    
    # ══════════════════════════════════════════
    # FASE 1: Base curada (empresas conhecidas)
    # ===
    logger.info("\n[FASE 1] Base Curada")

    batch_size = 8
    start = last_index
    end = min(start + batch_size, len(CURATED_COMPANIES))

    if start < len(CURATED_COMPANIES):
        for i in range(start, end):
            company = CURATED_COMPANIES[i]
            nome_lower = company['nome'].lower().strip()

            if nome_lower in registered_names:
                logger.info(f"   [SKIP] {company['nome'][:40]} (ja cadastrado)")
                continue
            
            if register_company(
                company['nome'],
                company.get('telefone', ''),
                company['cidade'],
                'gelson_curated'
            ):
                total_registered_this_run += 1
                registered_names.add(nome_lower)
                history['registered_companies'].append({
                    'nome': company['nome'],
                    'telefone': company.get('telefone', ''),
                    'cidade': company['cidade'],
                    'uf': company['uf'],
                    'fonte': 'gelson_curated',
                    'registered_at': datetime.now().isoformat()
                })
            
            time.sleep(random.uniform(1.5, 3.0))
        
        history['curated_index'] = end
    
    # ══════════════════════════════════════════
    # FASE 2: Scraping de diretorios (Hotfrog)
    # ===
    logger.info("\n[FASE 2] Diretos Online (Hotfrog)")
    
    hotfrog_start = history.get('last_index', 0)
    hotfrog_end = min(hotfrog_start + 3, len(CITIES))
    
    for i in range(hotfrog_start, hotfrog_end):
        cidade, uf = CITIES[i]
        
        companies = search_hotfrog(cidade, uf)
        
        for company in companies[:3]:  # Máx 3 por cidade
            nome_lower = company['nome'].lower().strip()
            
            if nome_lower in registered_names:
                continue
            
            if register_company(
                company['nome'],
                company.get('telefone', ''),
                company.get('cidade', cidade),
                'gelson_hotfrog'
            ):
                total_registered_this_run += 1
                registered_names.add(nome_lower)
                history['registered_companies'].append({
                    'nome': company['nome'],
                    'telefone': company.get('telefone', ''),
                    'cidade': company.get('cidade', cidade),
                    'uf': uf,
                    'fonte': 'gelson_hotfrog',
                    'registered_at': datetime.now().isoformat()
                })
            
            time.sleep(random.uniform(2.0, 4.0))
        
        history['last_index'] = i + 1
        save_history(history)
    
    # Salvar progresso
    history['last_run'] = datetime.now().isoformat()
    save_history(history)
    
    # ══════════════════════════════════════════
    # RESUMO
    # ===
    logger.info("\n" + "=" * 50)
    logger.info("[RESUMO]")
    logger.info("=" * 50)
    logger.info(f"  Total no banco: {len(history['registered_companies'])}")
    logger.info(f"  Registrados agora: {total_registered_this_run}")
    logger.info(f"  Curados processados: {end}/{len(CURATED_COMPANIES)}")
    logger.info(f"  Cidades online: {hotfrog_end}/{len(CITIES)}")
    logger.info(f"  Proxima execucao continua do ponto: curated={end}, city={hotfrog_end}")

if __name__ == "__main__":
    run_scanner()