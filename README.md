# Doc2Markdown Bot 🤖

Bot Telegram que converte documentos e URLs para Markdown usando [Docling](https://github.com/docling-project/docling).

## Formatos suportados

**Documentos:** PDF, DOCX, XLSX, PPTX, HTML, XHTML, CSV, Markdown, AsciiDoc, LaTeX  
**Imagens:** PNG, JPEG, TIFF, BMP, WEBP

## Como usar

- **Arquivo:** envie diretamente no chat → recebe o `.md` de volta
- **URL:** cole o link como mensagem → recebe o `.md` de volta
- `/start` — boas-vindas
- `/help` — formatos suportados

---

## Deploy no Render (free tier)

### 1. Criar o bot no Telegram

1. Abra [@BotFather](https://t.me/BotFather) no Telegram
2. `/newbot` → defina nome e username
3. Copie o **BOT_TOKEN**

### 2. Obter seu chat_id

1. Abra [@userinfobot](https://t.me/userinfobot) no Telegram
2. Envie qualquer mensagem → ele retorna seu **Id**

### 3. Deploy no Render

1. Faça fork/push deste repositório no GitHub
2. Acesse [render.com](https://render.com) → **New Web Service**
3. Conecte o repositório
4. Render detecta o `render.yaml` automaticamente
5. Em **Environment Variables**, adicione:
   - `BOT_TOKEN` = seu token do BotFather
   - `ALLOWED_CHAT_IDS` = seu chat_id (ex: `123456789`)
6. Clique em **Deploy**

### 4. Configurar keep-alive (evitar hibernação)

O Render free hiberna após 15 min de inatividade. Configure um ping externo:

1. Acesse [uptimerobot.com](https://uptimerobot.com) (gratuito)
2. **New Monitor** → tipo **HTTP(s)**
3. URL: `https://seu-app.onrender.com/health`
4. Intervalo: **5 minutos**

---

## Desenvolvimento local

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis
cp .env.example .env
# edite .env com seu BOT_TOKEN e ALLOWED_CHAT_IDS

# Rodar
python bot.py
```

Para carregar o `.env` localmente, instale `python-dotenv` e adicione no topo do `bot.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```
