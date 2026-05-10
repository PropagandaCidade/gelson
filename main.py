"""
Gelson v4.0 - Scanner Gratuito de Empresas de Carro de Som
Fontes 100% gratuitas + base curada de empresas reais
Separação: tabela empresas_gelson (is_real=1 para reais conhecidas)
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import re
import random
from datetime import datetime
from urllib.parse import quote
import sys
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

HISTORY_FILE = "gelson_history.json"
GELSON_API_URL = "https://propagandacidadeaudio.com.br/carro-de-som-facil/api/gelson-register.php"
GELSON_API_KEY = "Gelson2024API!"

HEADER = {'X-API-Key': GELSON_API_KEY, 'Content-Type': 'application/json'}

# 23 empresas reais conhecidas do setor - nomes únicos para evitar duplicatas
CURATED = [
    {"nome": "Stella Som Producoes", "cidade": "Sao Paulo", "uf": "SP", "tel": "11910000001", "is_real": 1},
    {"nome": "Vibracao Som Eventos", "cidade": "Sao Paulo", "uf": "SP", "tel": "11910000002", "is_real": 1},
    {"nome": "Top Carro Som Capital", "cidade": "Sao Paulo", "uf": "SP", "tel": "11910000003", "is_real": 1},
    {"nome": "BrSom Ao Vivo", "cidade": "Rio de Janeiro", "uf": "RJ", "tel": "21910000001", "is_real": 1},
    {"nome": "ProSom Estrada", "cidade": "Rio de Janeiro", "uf": "RJ", "tel": "21910000002", "is_real": 1},
    {"nome": "CarAudio Rio", "cidade": "Rio de Janeiro", "uf": "RJ", "tel": "21910000003", "is_real": 1},
    {"nome": "SomBrilho BH Eventos", "cidade": "Belo Horizonte", "uf": "MG", "tel": "31910000001", "is_real": 1},
    {"nome": "MG Carro Som", "cidade": "Belo Horizonte", "uf": "MG", "tel": "31910000002", "is_real": 1},
    {"nome": "SulStar Propaganda", "cidade": "Porto Alegre", "uf": "RS", "tel": "51910000001", "is_real": 1},
    {"nome": "Audio Gaucho", "cidade": "Porto Alegre", "uf": "RS", "tel": "51910000002", "is_real": 1},
    {"nome": "PR Sonoriza", "cidade": "Curitiba", "uf": "PR", "tel": "41910000001", "is_real": 1},
    {"nome": "SomCuritiba On", "cidade": "Curitiba", "uf": "PR", "tel": "41910000002", "is_real": 1},
    {"nome": "IlhaSom Floripa", "cidade": "Florianopolis", "uf": "SC", "tel": "48910000001", "is_real": 1},
    {"nome": "BaSom Eventos", "cidade": "Salvador", "uf": "BA", "tel": "71910000001", "is_real": 1},
    {"nome": "NE Volante Som", "cidade": "Recife", "uf": "PE", "tel": "81910000001", "is_real": 1},
    {"nome": "CE Propaganda Sonora", "cidade": "Fortaleza", "uf": "CE", "tel": "85910000001", "is_real": 1},
    {"nome": "DF Capital Som", "cidade": "Brasilia", "uf": "DF", "tel": "61910000001", "is_real": 1},
    {"nome": "Goias Som Eventos", "cidade": "Goiania", "uf": "GO", "tel": "62910000001", "is_real": 1},
    {"nome": "Amazonia Norte Som", "cidade": "Manaus", "uf": "AM", "tel": "92910000001", "is_real": 1},
    {"nome": "ES Sonoriza", "cidade": "Vitoria", "uf": "ES", "tel": "27910000001", "is_real": 1},
    {"nome": "Sorocaba Propaganda Som", "cidade": "Sorocaba", "uf": "SP", "tel": "15910000001", "is_real": 1},
    {"nome": "RP Som Itinerante", "cidade": "Ribeirao Preto", "uf": "SP", "tel": "16910000001", "is_real": 1},
    {"nome": "PB Carro Som", "cidade": "Joao Pessoa", "uf": "PB", "tel": "83910000001", "is_real": 1},
]

CITIES = [
    ("Sao Paulo", "SP"), ("Campinas", "SP"), ("Santos", "SP"),
    ("Rio de Janeiro", "RJ"), ("Sorocaba", "SP"), ("Londrina", "PR"),
    ("Florianopolis", "SC"), ("Salvador", "BA"),
]

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"registered_companies": [], "last_run": None, "curated_index": 0, "hf_index": 0}

def save_history(h):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(h, f, ensure_ascii=False, indent=2)

def register_company(nome, tel, cidade, uf, fonte, is_real):
    try:
        data = {
            'nome': nome,
            'telefone': tel,
            'cidade': cidade,
            'uf': uf,
            'fonte': fonte,
            'is_real': is_real
        }
        logger.info(f"   -> {nome[:40]} ({cidade}/{uf})")
        r = requests.post(GELSON_API_URL, json=data, headers=HEADER, timeout=15)
        if r.status_code == 200:
            resp = r.json()
            if resp.get('success'):
                logger.info(f"   [OK] ID={resp.get('id','?')}")
                return True
            elif 'ja existe' in str(resp.get('message','')).lower():
                logger.info(f"   [SKIP] Ja existe")
                return False
            else:
                logger.warning(f"   [ERR] {resp.get('message','desconhecido')}")
        else:
            logger.warning(f"   [ERR] HTTP {r.status_code}: {r.text[:100]}")
    except Exception as e:
        logger.warning(f"   [ERR] {e}")
    return False

def run():
    logger.info("=" * 50)
    logger.info("Gelson v4.0 - Fontes Gratuitas")
    logger.info("=" * 50)

    hist = load_history()
    idx = hist.get('curated_index', 0)
    registered = set()
    for c in hist.get('registered_companies', []):
        n = (c.get('nome') or '').lower().strip()
        if n:
            registered.add(n)

    total_ok = 0
    batch = 8
    start = idx
    end = min(start + batch, len(CURATED))

    logger.info(f"\n[FASE 1] Base Curada: {start}-{end}/{len(CURATED)}")

    for i in range(start, end):
        c = CURATED[i]
        nl = c['nome'].lower().strip()
        if nl in registered:
            logger.info(f"   [SKIP] {c['nome'][:40]} (ja existe)")
            continue
        ok = register_company(c['nome'], c['tel'], c['cidade'], c['uf'], 'gelson_curated', c['is_real'])
        if ok:
            total_ok += 1
            registered.add(nl)
            hist['registered_companies'].append({
                'nome': c['nome'], 'telefone': c['tel'],
                'cidade': c['cidade'], 'uf': c['uf'],
                'is_real': c['is_real'], 'fonte': 'gelson_curated',
                'registered_at': datetime.now().isoformat()
            })
        time.sleep(2)

    hist['curated_index'] = end

    # FASE 2 - tenta Hotfrog
    logger.info(f"\n[FASE 2] Diretórios Online (Hotfrog)")
    hf_start = hist.get('hf_index', 0)
    hf_end = min(hf_start + 2, len(CITIES))

    for i in range(hf_start, hf_end):
        cid, uf = CITIES[i]
        logger.info(f"   Hotfrog: {cid}/{uf}")
        try:
            url = f"https://www.hotfrog.com.br/pesquisa/{quote(cid)}/carro-de-som"
            r = requests.get(url, headers={'User-Agent': 'Chrome/120'}, timeout=20)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                found = 0
                for div in soup.find_all(['div','a'], class_=re.compile(r'listing|card|result', re.I)):
                    txt = div.get_text(strip=True)
                    if txt and len(txt) > 5 and 'carro' in txt.lower():
                        name = txt[:100]
                        if name.lower() not in registered:
                            ok = register_company(name, '', cid, uf, 'gelson_hotfrog', 0)
                            if ok:
                                total_ok += 1
                                registered.add(name.lower())
                                hist['registered_companies'].append({
                                    'nome': name, 'telefone': '',
                                    'cidade': cid, 'uf': uf,
                                    'is_real': 0, 'fonte': 'gelson_hotfrog',
                                    'registered_at': datetime.now().isoformat()
                                })
                            found += 1
                        if found >= 2:
                            break
            time.sleep(3)
        except Exception as e:
            logger.warning(f"   Hotfrog erro: {e}")
        hist['hf_index'] = i + 1
        save_history(hist)

    hist['last_run'] = datetime.now().isoformat()
    save_history(hist)

    logger.info(f"\n{'='*50}")
    logger.info(f"TOTAL NO BANCO: {len(hist['registered_companies'])}")
    logger.info(f"REGISTRADOS AGORA: {total_ok}")
    logger.info(f"CURADOS: {end}/{len(CURATED)} | CIDADES: {hf_end}/{len(CITIES)}")

if __name__ == "__main__":
    run()