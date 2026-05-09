# 🤵 Gelson - Scanner de Empresas de Carro de Som

Agente automatizado para buscar empresas de carro de som/propaganda nas maiores cidades do Brasil e cadastrar no Carro de Som Fácil.

## Como funciona

1. Varre cidades do Brasil (200 maiores)
2. Busca empresas via Google e outras fontes
3. Filtra por critérios de qualidade
4. Cadastra automaticamente via API (status: pendente)
5. Notifica via Telegram

## Configuração

### Variáveis de Ambiente (Secrets no GitHub)

- `TELEGRAM_BOT_TOKEN` - Token do bot Telegram
- `TELEGRAM_CHAT_ID` - Seu chat ID

### API Endpoint

O Gelson usa a API:
- URL: `https://propagandacidadeaudio.com.br/carro-de-som-facil/api/gelson-register.php`
- Key: `Gelson2024API!`

## GitHub Actions

O scanner roda automaticamente a cada 2 horas via cron.

## Palavras-chave monitoradas

- carro de som
- propaganda de carro
- som itinerante
- propaganda volante
- moto som
- contratação de carro de som

## Status

- Em desenvolvimento
- Modo demo ativo (dados simulados)
- Próximo: integração com Google Places API para scraping real

## Admin

Acesse o painel de admin em:
`https://propagandacidadeaudio.com.br/carro-de-som-facil/admin-gelson.php`

Senha: `Gelson2024Admin!`