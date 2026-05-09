# SPEC.md - Gelson Scanner

## Agente: Gelson

**Nome:** Gelson  
**Objetivo:** Buscar empresas de carro de som/propaganda nas 200 maiores cidades do Brasil e cadastrar automaticamente no banco de dados do Carro de Som Fácil.

---

### Palavras-chave de Busca

```
carro de som [cidade]
propaganda de carro [cidade]
som itinerante [cidade]
carro de som para evento [cidade]
locação carro de som [cidade]
serviço de carro de som [cidade]
propaganda volante [cidade]
moto som [cidade]
contratação de carro de som [cidade]
```

### Critérios de Qualidade

**Palavras para IGNORAR:**
- agência, produtora, estúdio (a menos que tenha "carro de som" no nome)
- escola, universidade, igreja (comunitários)
- "aluguel", "locação" de equipamentos (não serviços)
- "festa", "evento" apenas (sem referência a carro de som)

**Palavras para INCLUIR:**
- "carro de som"
- "som itinerante"
- "propaganda"
- "volante"
- "moto som"
- "carro de som" + nome da cidade

### Estrutura de Dados

```
empresas:
  - nome (required)
  - email (gerar: gelson@[cidade].carrodesomfacil.com.br)
  - telefone (required, formato: 55XX9XXXXXXXX)
  - senha (padrão: "CsF2024!" + 4随机 dígitos)
  - status: "pendente"
  - fonte: "google_maps" | "getninjas"
  - cidade_original: "[cidade], [UF]"
  - scraped_at: timestamp

cidades (vinculadas):
  - nome_cidade: [cidade]
  - uf: [UF]
  - bairros: ""
  - taxa_deslocamento: 0
```

### Cronograma

**Fase 1 - RS (20 cidades) - PRIORIDADE**
**Fase 2 - Capitais + SP (50 cidades)**
**Fase 3 - Cidades médias (130 cidades)**

### Frequência

- Teste: 5 cidades/dia
- Produção: 20-30 cidades/dia
- Meta: 200 cidades em ~10-15 dias

### Notificações Telegram

- "Gelson encontrou X empresas em [cidade]!"
- "Total pendentes: Y empresas"

---

## Configuração do Banco

O Gelson vai usar as mesmas credenciais do Carro de Som Fácil:
- Servidor: localhost
- Usuário: u667346992_dsncua
- Senha: Tangerina_01
- Banco: u667346992_dsncua
- Tabela: empresas ( mesma do register-empresa.php )