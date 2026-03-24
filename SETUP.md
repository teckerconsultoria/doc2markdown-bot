# Doc2Markdown Bot — Guia de Setup

> Bot Telegram que converte documentos e URLs para Markdown via Docling.  
> Deploy: Render free tier · Keep-alive: UptimeRobot · Acesso: whitelist por chat_id

---

## Pré-requisitos

- Conta no [GitHub](https://github.com)
- Conta no [Render](https://render.com)
- Conta no [UptimeRobot](https://uptimerobot.com)
- Telegram instalado

---

## Passo 1 — Criar o Bot no Telegram

1. Abra o Telegram e pesquise por **@BotFather**
2. Envie `/newbot`
3. Defina o **nome** do bot (ex: `Doc2Markdown`)
4. Defina o **username** (deve terminar em `bot`, ex: `doc2markdown_bot`)
5. O BotFather retorna o **BOT_TOKEN** — guarde, você vai precisar

```
Exemplo de token:
7412305689:AAFkLmNopQrStUvWxYz-AbCdEfGhIjKlMnO
```

---

## Passo 2 — Obter seu Chat ID

1. Pesquise por **@userinfobot** no Telegram
2. Envie qualquer mensagem
3. Ele retorna seu **Id** numérico — guarde

```
Exemplo:
Your user ID: 123456789
```

---

## Passo 3 — Repositório no GitHub

1. Crie um repositório **privado** no GitHub (recomendado — contém config do bot)
2. Faça upload ou commit dos 6 arquivos do projeto:

```
doc2markdown-bot/
├── bot.py
├── keep_alive.py
├── requirements.txt
├── render.yaml
├── .env.example
└── README.md
```

> ⚠️ **Nunca commite o arquivo `.env`** com seus tokens reais. O `.gitignore` já o exclui.

---

## Passo 4 — Deploy no Render

### 4.1 Criar o serviço

1. Acesse [render.com](https://render.com) → **New +** → **Web Service**
2. Conecte sua conta GitHub se ainda não conectou
3. Selecione o repositório `doc2markdown-bot`
4. O Render detecta o `render.yaml` automaticamente

### 4.2 Configurar variáveis de ambiente

No painel do serviço, acesse **Environment** e adicione:

| Key | Value |
|-----|-------|
| `BOT_TOKEN` | token obtido no Passo 1 |
| `ALLOWED_CHAT_IDS` | chat_id obtido no Passo 2 |

> Para liberar múltiplos usuários, separe por vírgula: `123456789,987654321`

### 4.3 Fazer o deploy

1. Clique em **Deploy Web Service**
2. Aguarde o build — **primeira vez demora ~10–15 min** (instala docling + baixa modelos ~1.5 GB)
3. Quando aparecer `Your service is live`, o bot está ativo

### 4.4 Copiar a URL do serviço

Na tela do serviço, copie a URL pública:
```
https://doc2markdown-bot.onrender.com
```
Você vai precisar dela no próximo passo.

---

## Passo 5 — Keep-Alive com UptimeRobot

O Render free hiberna serviços após **15 minutos de inatividade**.  
O UptimeRobot faz pings periódicos para manter o bot sempre acordado.

1. Acesse [uptimerobot.com](https://uptimerobot.com) e crie uma conta gratuita
2. Clique em **+ Add New Monitor**
3. Configure:
   - **Monitor Type:** `HTTP(s)`
   - **Friendly Name:** `Doc2Markdown Bot`
   - **URL:** `https://seu-app.onrender.com/health`
   - **Monitoring Interval:** `5 minutes`
4. Clique em **Create Monitor**

> O endpoint `/health` retorna `{"status": "ok"}` e é suficiente para manter o serviço ativo.

---

## Passo 6 — Testar o Bot

Abra o Telegram, pesquise pelo username do seu bot e:

| Teste | Ação | Resultado esperado |
|-------|------|--------------------|
| Iniciar | `/start` | Mensagem de boas-vindas |
| Ajuda | `/help` | Lista de formatos suportados |
| URL | Cole `https://arxiv.org/pdf/2408.09869` | Recebe `2408.09869.md` |
| Arquivo | Envie um PDF | Recebe `nome-do-arquivo.md` |
| Formato inválido | Envie um `.mp3` | Mensagem de erro com formatos válidos |
| Acesso negado | Outro usuário tenta usar | `⛔ Acesso não autorizado` |

---

## Formatos Suportados

| Categoria | Extensões |
|-----------|-----------|
| Documentos Office | `.pdf` `.docx` `.xlsx` `.pptx` |
| Web / Markup | `.html` `.xhtml` `.md` `.adoc` `.asciidoc` `.tex` |
| Dados | `.csv` |
| Imagens | `.png` `.jpg` `.jpeg` `.tiff` `.tif` `.bmp` `.webp` |

---

## Variáveis de Ambiente

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `BOT_TOKEN` | ✅ | Token do BotFather |
| `ALLOWED_CHAT_IDS` | ✅ | Chat IDs autorizados, separados por vírgula |
| `PORT` | ❌ | Porta HTTP do keep-alive (Render injeta automaticamente) |

---

## Desenvolvimento Local

```bash
# 1. Clonar o repositório
git clone https://github.com/seu-usuario/doc2markdown-bot
cd doc2markdown-bot

# 2. Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 3. Instalar dependências
pip install -r requirements.txt
pip install python-dotenv  # apenas para dev local

# 4. Configurar variáveis
cp .env.example .env
# edite .env com seu BOT_TOKEN e ALLOWED_CHAT_IDS

# 5. Adicionar no topo do bot.py (apenas local):
# from dotenv import load_dotenv
# load_dotenv()

# 6. Rodar
python bot.py
```

---

## Arquitetura

```
Usuário (Telegram)
       │
       │  arquivo ou URL
       ▼
  python-telegram-bot (polling)
       │
       │  path temporário / URL string
       ▼
  DocumentConverter (docling)
       │
       │  .export_to_markdown()
       ▼
  arquivo .md  ──────────────────► Usuário (Telegram)


  Flask /health  ◄──── ping a cada 5min (UptimeRobot)
  (keep-alive)          evita hibernação do Render
```

---

## Troubleshooting

**Bot não responde após deploy**
- Verifique os logs no Render → aba **Logs**
- Confirme que `BOT_TOKEN` e `ALLOWED_CHAT_IDS` estão corretos nas env vars
- Aguarde o primeiro build completo (pode demorar até 15 min)

**Erro `Unauthorized` nos logs**
- O `BOT_TOKEN` está incorreto ou expirado
- Gere um novo token via `/revoke` no @BotFather

**Bot fica offline periodicamente**
- O UptimeRobot não está configurado ou a URL está errada
- Confirme que o monitor aponta para `https://seu-app.onrender.com/health`

**Arquivo grande não converte**
- O Telegram limita uploads a **20 MB** para bots
- Para arquivos maiores, use a URL direta do documento

**`ALLOWED_CHAT_IDS` vazio — acesso aberto**
- Se a variável não estiver definida, o bot aceita qualquer usuário
- Sempre defina em produção

---

*Powered by [Docling](https://github.com/docling-project/docling) · [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)*
