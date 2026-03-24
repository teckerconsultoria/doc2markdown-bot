# ⚡ Quick Setup - Comandos Rápidos

## 🚀 Para Setup Rápido do Repositório GitHub

### 1. Clonar o Repositório Vazio

```bash
git clone https://github.com/seu-usuario/doc2markdown-bot.git
cd doc2markdown-bot
```

### 2. Copiar os Arquivos Preparados

**Se tiver os arquivos localmente:**

```bash
# Copie todo o conteúdo de doc2markdown-bot-github/ para doc2markdown-bot/
cp -r doc2markdown-bot-github/* .
```

### 3. Fazer Commit Inicial

```bash
# Configure seu Git (primeira vez apenas)
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@example.com"

# Adicione todos os arquivos
git add .

# Commit inicial
git commit -m "chore: initial commit with bot and docs"

# Envie para GitHub
git branch -M main
git push -u origin main
```

### 4. Verificar se Funcionou

```bash
# Veja o status
git log --oneline

# Veja os arquivos remotos
git ls-remote origin
```

## 📦 Arquivos Inclusos

✅ **Código do Bot**
- `bot.py` - Lógica principal
- `keep_alive.py` - Manter vivo no Render
- `requirements.txt` - Dependências Python
- `render.yaml` - Config de deploy

✅ **Documentação**
- `README.md` - Principal (melhorado)
- `SETUP.md` - Setup detalhado
- `CONTRIBUTING.md` - Guia de contribuição
- `SECURITY.md` - Política de segurança
- `GITHUB_SETUP.md` - Este arquivo

✅ **Configuração Git**
- `.gitignore` - Arquivos a ignorar
- `LICENSE` - MIT License

✅ **GitHub Templates**
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`
- `.github/pull_request_template.md`

## 🔄 Fluxo Depois do Setup

```bash
# 1. Atualizar localmente
git pull origin main

# 2. Criar branch para mudança
git checkout -b feature/sua-feature

# 3. Fazer mudanças nos arquivos
# ... edite ...

# 4. Commit
git add .
git commit -m "feat: descrição da mudança"

# 5. Push
git push origin feature/sua-feature

# 6. Abra um Pull Request no GitHub
```

## 🌐 Deploy no Render

Depois do repositório pronto:

1. Acesse [render.com](https://render.com)
2. Clique em **New Web Service**
3. Conecte seu repositório GitHub
4. Adicione variáveis:
   - `BOT_TOKEN` = seu token
   - `ALLOWED_CHAT_IDS` = seu ID
5. Deploy!

Veja `SETUP.md` para detalhes completos.

## ❌ Erros Comuns

### "fatal: pathspec 'xxx' did not match any files"
```bash
# Verifique se os arquivos existem
ls -la

# Use git status para ver o estado
git status
```

### "refusing to merge unrelated histories"
```bash
# Se clonou vazio e adiciona arquivos
git pull origin main --allow-unrelated-histories
```

### ".env foi commitado"
```bash
# Remove do repositório (mas mantém localmente)
git rm --cached .env
git commit -m "remove: .env file"
git push origin main

# Para o futuro, edite .gitignore para conter '.env'
```

## 📚 Próxima Leitura

1. **[GITHUB_SETUP.md](GITHUB_SETUP.md)** - Guia completo
2. **[SETUP.md](SETUP.md)** - Deploy no Render
3. **[CONTRIBUTING.md](CONTRIBUTING.md)** - Para colaboradores

## 🎯 Checklist Rápido

- [ ] Repositório criado no GitHub
- [ ] Arquivos fizeram push com sucesso
- [ ] README aparece na página principal
- [ ] `.env` NÃO está no repositório
- [ ] Todos os arquivos estão visíveis

---

Pronto! Seu repositório está no GitHub! 🎉

Próximo passo: Deploy no Render seguindo [SETUP.md](SETUP.md)
