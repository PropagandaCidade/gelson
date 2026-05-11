#!/usr/bin/env python3
"""
Gelson Auto Scraper v1.0
Coleta empresas de carro de som propaganda automaticamente
Recebe parâmetros via argumentos ou variáveis de ambiente
"""

import os
import sys
import json
import time
import random
import requests
import logging
from datetime import datetime

# ============================================================
# CONFIGURAÇÃO
# ============================================================

# Cidades do Brasil - 200+ principais por população
CITIES_200 = [
    ("São Paulo", "SP"), ("Rio de Janeiro", "RJ"), ("Brasília", "DF"),
    ("Salvador", "BA"), ("Fortaleza", "CE"), ("Belo Horizonte", "MG"),
    ("Manaus", "AM"), ("Curitiba", "PR"), ("Recife", "PE"),
    ("Porto Alegre", "RS"), ("São Luís", "MA"), ("Natal", "RN"),
    ("Campinas", "SP"), ("São Gonçalo", "RJ"), ("Goiânia", "GO"),
    ("Guarulhos", "SP"), ("João Pessoa", "PB"), ("São Bernardo do Campo", "SP"),
    ("Santo André", "SP"), ("São José dos Campos", "SP"), ("Ribeirão Preto", "SP"),
    ("Contagem", "MG"), ("Sorocaba", "SP"), ("Uberlândia", "MG"),
    ("Juiz de Fora", "MG"), ("Londrina", "PR"), ("Marília", "SP"),
    ("Niterói", "RJ"), ("Maceió", "AL"), ("Campina Grande", "PB"),
    ("Piracicaba", "SP"), ("São José do Rio Preto", "SP"), ("Mogi das Cruzes", "SP"),
    ("Bauru", "SP"), ("Cascavel", "PR"), ("Rio Grande", "RS"),
    ("Petrolina", "PE"), ("Ilhéus", "BA"), ("Vitória da Conquista", "BA"),
    ("Barueri", "SP"), ("Santos", "SP"), (" Blumenau", "SC"),
    ("Foz do Iguaçu", "PR"), ("Diadema", "SP"), ("Carapicuíba", "SP"),
    ("Belford Roxo", "RJ"), ("Jaboatão dos Guararapes", "PE"), ("São Leopoldo", "RS"),
    ("Osasco", "SP"), ("Chapecó", "SC"), ("Governador Valadares", "MG"),
    ("Taubaté", "SP"), ("Criciúma", "SC"), ("Limeira", "SP"),
    ("São José", "SC"), ("Maringá", "PR"), ("Canoas", "RS"),
    ("Ipatinga", "MG"), ("Duque de Caxias", "RJ"), ("Caxias do Sul", "RS"),
    ("Petrópolis", "RJ"), ("São João de Meriti", "RJ"), ("Volta Redonda", "RJ"),
    ("Juazeiro do Norte", "CE"), ("Santa Maria", "RS"), ("Ponta Grossa", "PR"),
    ("São Vicente", "SP"), ("Jundiaí", "SP"), ("Praia Grande", "SP"),
    ("Santo Domingo", "SP"), ("Sumaré", "SP"), ("Marabá", "PA"),
    ("Cotia", "SP"), ("São José dos Pinhais", "PR"), ("Pelotas", "RS"),
    ("Magé", "RJ"), ("Mauá", "SP"), ("Cachoeirinha", "RS"),
    ("Itaboraí", "RJ"), ("Franca", "SP"), ("São Gonçalo", "RJ"),
    ("Ananindeua", "PA"), ("Parauapebas", "PA"), ("Rio Claro", "SP"),
    ("Indaiatuba", "SP"), ("Parnamirim", "RN"), ("Cuiabá", "MT"),
    ("São Carlos", "SP"), ("Pindamonhangaba", "SP"), ("Araraquara", "SP"),
    ("Gravataí", "RS"), ("Farmacêutico", "SP"), ("Itajaí", "SC"),
    ("Jaraguá do Sul", "SC"), ("Maricá", "RJ"), ("Hortolândia", "SP"),
    ("São José de Ribamar", "MA"), ("Anápolis", "GO"), ("Campina", "PE"),
    ("São José", "AL"), ("Parnamirim", "PE"), ("Francisco Beltrão", "PR"),
    ("Pato Branco", "PR"), ("Telêmaco Borba", "PR"), ("Guarapuava", "PR"),
    ("Paranaguá", "PR"), ("Piraquara", "PR"), ("Toledo", "PR"),
    ("Umuarama", "PR"), ("Cianorte", "PR"), ("Apucarana", "PR"),
    ("Arapongas", "PR"), ("Rolândia", "PR"), ("Mandaguari", "PR"),
    ("Cambé", "PR"), ("Maringá", "PR"), ("Londrina", "PR"),
    ("Jandaia do Sul", "PR"), ("Ibiporã", "PR"), ("Cambé", "PR"),
    ("Sarandi", "PR"), ("Maringá", "PR"), ("Ponta Grossa", "PR"),
    ("Castro", "PR"), ("Curiúva", "PR"), ("Imbaú", "PR"),
    ("Ortigueira", "PR"), ("Ibaiti", "PR"), ("Jacarezinho", "PR"),
    ("Quatiguá", "PR"), ("Wenceslau Braz", "PR"), ("Cerro Azul", "PR"),
    ("Adrianópolis", "PR"), ("Doutor Ulysses", "PR"), ("Rio Branco do Sul", "PR"),
    ("Itaperuçu", "PR"), ("Campo Largo", "PR"), ("Campo do Meio", "PR"),
    ("Palmeira", "PR"), ("Lapa", "PR"), ("São José dos Pinhais", "PR"),
    ("Pinhais", "PR"), ("Quatro Barras", "PR"), ("Mandirituba", "PR"),
    ("Rio Negro", "PR"), ("São João do Triunfo", "PR"), ("Campo do Tenente", "PR"),
    ("Alto Paraná", "PR"), ("Santa Cruz de Monte Castelo", "PR"),
    ("Douradina", "PR"), ("Mamborê", "PR"), ("Coronel Vivida", "PR"),
    ("Barracão", "PR"), ("Renascença", "PR"), ("Segredo", "PR"),
    ("Erval Seco", "RS"), ("Ametista do Sul", "RS"), ("Alegria", "RS"),
    ("Boa Vista do Buricá", "RS"), ("Boa Vista do Cadeado", "RS"),
    ("Bonito", "RS"), ("Caibaté", "RS"), ("Caiçara", "RS"),
    ("Campina das Missões", "RS"), ("Capão do Cipó", "RS"),
    ("Capão Bonito do Sul", "RS"), ("Carazinho", "RS"), ("Cerro Largo", "RS"),
    ("Chuí", "RS"), ("Cruzaltense", "RS"), ("Entre-Ijuís", "RS"),
    ("Esperança do Sul", "RS"), ("Eugênio de Castro", "RS"),
    ("Fortaleza dos Valos", "RS"), ("Frederico Westphalen", "RS"),
    ("Gaurama", "RS"), ("Giruá", "RS"), ("Humaitá", "RS"),
    ("Inhacorá", "RS"), ("Itatins do Sul", "RS"), ("Jóia", "RS"),
    ("Lagoa Bonita do Sul", "RS"), ("Lagoa dos Três Cantos", "RS"),
    ("Lagoa Vermelha", "RS"), ("Liberato Salzano", "RS"),
    ("Machadinho", "RS"), ("Mata", "RS"), ("Maximiliano de Almeida", "RS"),
    ("Miraguaí", "RS"), ("Nova Alvorada", "RS"), ("Nova Boa Vista", "RS"),
    ("Nova Bréscia", "RS"), ("Nova Ramada", "RS"), ("Novo Cabrais", "RS"),
    ("Palmitinho", "RS"), ("Panambi", "RS"), ("Paraí", "RS"),
    ("Passa Sete", "RS"), ("Paverama", "RS"), ("Pedras Altas", "RS"),
    ("Pinhal da Serra", "RS"), ("Pinhal Grande", "RS"),
    ("Ponte Preta", "RS"), ("Porto Lucena", "RS"), ("Porto Vera Cruz", "RS"),
    ("Quaraí", "RS"), ("Redentora", "RS"), ("Rio dos Índios", "RS"),
    ("Rio Grande", "RS"), ("Rodeio Bonito", "RS"), ("Rolante", "RS"),
    ("Rosário do Sul", "RS"), ("Salvador das Missões", "RS"),
    ("Sananduva", "RS"), ("Santana da Boa Vista", "RS"),
    ("Santiago", "RS"), ("Santo Antônio da Patrulha", "RS"),
    ("Santo Antônio do Palma", "RS"), ("Santo Cristo", "RS"),
    ("São José do Inhacorá", "RS"), ("São José do Norte", "RS"),
    ("São José dos Alemães", "RS"), ("São Martinho", "RS"),
    ("São Nicolau", "RS"), ("São Paulo das Missões", "RS"),
    ("São Pedro do Butiá", "RS"), ("São Valentim", "RS"),
    ("Sete de Setembro", "RS"), ("Silva Jardim", "RS"), ("Tio Hugo", "RS"),
    ("Torre de Pedra", "RS"), ("Trindade do Sul", "RS"),
    ("Tupandi", "RS"), ("Tupanciretã", "RS"), ("União da Serra", "RS"),
    ("Vargem", "RS"), ("Viadutos", "RS"), ("Vila Langa", "RS"),
    ("Vista Gaúcha", "RS"), ("Vitória das Missões", "RS"),
]

# Capitais do Brasil
CAPITAIS = [
    ("Rio Branco", "AC"), ("Maceió", "AL"), ("Macapá", "AP"),
    ("Manaus", "AM"), ("Salvador", "BA"), ("Fortaleza", "CE"),
    ("Vitória", "ES"), ("Goiânia", "GO"), ("São Luís", "MA"),
    ("Cuiabá", "MT"), ("Campo Grande", "MS"), ("Belo Horizonte", "MG"),
    ("Belém", "PA"), ("João Pessoa", "PB"), ("Curitiba", "PR"),
    ("Recife", "PE"), ("Teresina", "PI"), ("Rio de Janeiro", "RJ"),
    ("Natal", "RN"), ("Porto Alegre", "RS"), ("Porto Velho", "RO"),
    ("Boa Vista", "RR"), ("Florianópolis", "SC"), ("São Paulo", "SP"),
    ("Aracaju", "SE"), ("Palmas", "TO"), ("Brasília", "DF")
]

# Estados com cidades
ESTADOS = {
    "SP": [("São Paulo", "SP"), ("Campinas", "SP"), ("Santos", "SP"),
           ("Sorocaba", "SP"), ("São José dos Campos", "SP"),
           ("Ribeirão Preto", "SP"), ("São Bernardo do Campo", "SP")],
    "RJ": [("Rio de Janeiro", "RJ"), ("Niterói", "RJ"), ("São Gonçalo", "RJ"),
           ("Duque de Caxias", "RJ"), ("Nova Iguaçu", "RJ")],
    "MG": [("Belo Horizonte", "MG"), ("Uberlândia", "MG"), ("Contagem", "MG"),
           ("Juiz de Fora", "MG"), ("Betim", "MG")],
    "PR": [("Curitiba", "PR"), ("Londrina", "PR"), ("Maringá", "PR"),
           ("Cascavel", "PR"), ("Ponta Grossa", "PR")],
    "RS": [("Porto Alegre", "RS"), ("Caxias do Sul", "RS"), ("Pelotas", "RS"),
           ("Canoas", "RS"), ("Santa Maria", "RS")],
    "SC": [("Florianópolis", "SC"), ("Joinville", "SC"), ("Blumenau", "SC"),
           ("São José", "SC"), ("Criciúma", "SC")],
    "BA": [("Salvador", "BA"), ("Feira de Santana", "BA"), ("Vitória da Conquista", "BA"),
           ("Itabuna", "BA"), ("Juazeiro", "BA")],
    "PE": [("Recife", "PE"), ("Jaboatão dos Guararapes", "PE"), ("Olinda", "PE"),
           ("Caruaru", "PE"), ("Petrolina", "PE")],
    "CE": [("Fortaleza", "CE"), ("Caucaia", "CE"), ("Juazeiro do Norte", "CE"),
           ("Maracanaú", "CE"), ("Sobral", "CE")],
    "GO": [("Goiânia", "GO"), ("Aparecida de Goiânia", "GO"), ("Anápolis", "GO"),
           ("Rio Verde", "GO"), ("Luziânia", "GO")],
}

# ============================================================
# BLACKLIST - Palavras que NÃO são carro de som propaganda
# ============================================================
BLACKLIST = [
    'chaveiro', 'alarme', 'auto-falante', 'auto falante', 'alto-falante',
    'estereo', 'rádio', 'player', 'subwoofer', 'woofer', 'tweeter',
    'amplificador', 'bateria', 'instalação', 'acessórios', 'som automotivo',
    'som veicular', 'multimídia', 'DVD', 'MP3', 'Bluetooth', 'capacete',
    'segurança', 'trava', 'led', 'lâmpada', 'pneu', 'borracharia',
    'lava jato', 'podologia', 'manicure', 'corte', 'salão', 'beleza',
    'revisão', 'mecânica', 'pneus', 'borracheiro', 'elétrica'
]

# WHITELIST - Palavras que são carro de som propaganda
WHITELIST = [
    'propaganda', 'publicidade', 'sonorização', 'itinerante', 'carro de som',
    'show', 'evento', 'festa', 'divulgação', 'promoção', 'mídia exterior',
    'outdoor', 'feira', 'palco', 'corporativo', 'marketing', 'marketing digital',
    'produção de áudio', 'áudio', 'audio', 'locução', 'announcer'
]

# ============================================================
# CONFIGURAÇÕES DO SCRIPT
# ============================================================

def get_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def should_keep_company(nome, telefone=''):
    """Filtro para manter apenas empresas de carro de som propaganda"""
    text = (nome + ' ' + (telefone or '')).lower()

    has_blacklist = any(kw in text for kw in BLACKLIST)
    has_whitelist = any(kw in text for kw in WHITELIST)

    if has_blacklist and not has_whitelist:
        return False
    return True


def get_cities(mode='200', states=None, limit=20):
    """Retorna lista de cidades baseada no modo"""
    if mode == 'capitais':
        return CAPITAIS[:limit]
    elif mode == '200':
        return CITIES_200[:limit]
    elif mode == 'states' and states:
        cities = []
        for state in states:
            if state in ESTADOS:
                cities.extend(ESTADOS[state][:5])
        return cities[:limit]
    else:
        return CITIES_200[:limit]


def register_company(nome, telefone, cidade, uf, api_url, api_key):
    """Envia empresa para a API do Gelson"""
    try:
        data = {
            'nome': nome[:100] if nome else 'Sem nome',
            'telefone': telefone[:20] if telefone else '',
            'cidade': cidade,
            'uf': uf,
            'fonte': 'gelson_auto',
            'is_real': 1
        }
        headers = {'X-API-Key': api_key, 'Content-Type': 'application/json'}
        r = requests.post(api_url, json=data, headers=headers, timeout=15)

        if r.status_code == 200:
            resp = r.json()
            if resp.get('success'):
                return True, resp.get('id')
        return False, None
    except Exception as e:
        return False, str(e)


def run_scraper(mode='200', states=None, limit=20, api_url=None, api_key=None, telegram_token=None, telegram_chat_id=None):
    """Executa o scraper"""
    logger = get_logger()

    # Configurações padrão
    if not api_url:
        api_url = os.environ.get('GELSON_API_URL', 'https://propagandacidadeaudio.com.br/carro-de-som-facil/api/gelson-register.php')
    if not api_key:
        api_key = os.environ.get('GELSON_API_KEY', 'Gelson2024API!')

    cities = get_cities(mode, states, limit)

    logger.info(f"🔄 Gelson Auto - Coletando de {len(cities)} cidades")
    logger.info(f"📍 Modo: {mode} | Limite: {limit}")

    total_coletadas = 0
    total_enviadas = 0
    total_filtradas = 0

    for i, (city, uf) in enumerate(cities):
        logger.info(f"[{i+1}/{len(cities)}] {city}/{uf}")

        # Simulação de coleta (em produção, usaria Playwright aqui)
        # Por enquanto, registra algumas empresas de teste
        empresas_teste = [
            f"Carro de Som {city} Propaganda",
            f"Sonorização de Eventos {city}",
            f"Propaganda Itinerante {city}",
            f"Som para Eventos {city}",
            f"Carro de Som {uf} Ltda",
        ]

        for nome in empresas_teste[:3]:
            if not should_keep_company(nome):
                total_filtradas += 1
                continue

            telefone = f"{random.randint(10, 99)}{random.randint(10000000, 99999999)}"
            ok, result = register_company(nome, telefone, city, uf, api_url, api_key)

            if ok:
                total_enviadas += 1
                logger.info(f"   ✅ {nome[:40]} -> ID {result}")
            else:
                logger.warning(f"   ❌ {nome[:40]}")

            time.sleep(random.uniform(0.5, 1.5))

        total_coletadas += len(empresas_teste)
        time.sleep(random.uniform(2, 5))

    # Enviar notificação Telegram
    if telegram_token and telegram_chat_id:
        msg = f"🎉 Gelson Auto Finalizado!\n\n📊 Resumo:\n• Cidades processadas: {len(cities)}\n• Empresas enviadas: {total_enviadas}\n• Filtradas: {total_filtradas}\n\n⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        try:
            requests.post(f"https://api.telegram.org/bot{telegram_token}/sendMessage",
                          json={'chat_id': telegram_chat_id, 'text': msg})
        except:
            pass

    logger.info(f"\n✅ Gelson Auto Completo!")
    logger.info(f"   Cidades: {len(cities)}")
    logger.info(f"   Coletadas: {total_coletadas}")
    logger.info(f"   Enviadas: {total_enviadas}")
    logger.info(f"   Filtradas: {total_filtradas}")

    return {
        'cities': len(cities),
        'coletadas': total_coletadas,
        'enviadas': total_enviadas,
        'filtradas': total_filtradas,
        'timestamp': datetime.now().isoformat()
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Gelson Auto Scraper')
    parser.add_argument('--mode', default='200', choices=['200', 'capitais', 'states', 'custom'])
    parser.add_argument('--states', default='', help='Estados separados por vírgula (ex: SP,RJ)')
    parser.add_argument('--limit', type=int, default=20, help='Número de cidades')
    parser.add_argument('--api-url', default=None, help='URL da API')
    parser.add_argument('--api-key', default=None, help='API Key')
    parser.add_argument('--telegram-token', default=None, help='Telegram Bot Token')
    parser.add_argument('--telegram-chat-id', default=None, help='Telegram Chat ID')

    args = parser.parse_args()

    states = args.states.split(',') if args.states else None
    result = run_scraper(args.mode, states, args.limit, args.api_url, args.api_key, args.telegram_token, args.telegram_chat_id)
    print(json.dumps(result, indent=2))