# 📚 Guia: Criar Repositório no GitHub

Este guia ajudará você a criar um repositório GitHub para o Doc2Markdown Bot com todos os arquivos preparados.

## 🔑 Pré-requisitos

1. Conta no GitHub ([github.com](https://github.com))
2. Git instalado localmente
3. Acesso à linha de comando/terminal

## 📝 Passo a Passo

### 1️⃣ Criar Repositório no GitHub

1. Acesse [github.com](https://github.com)
2. Clique em **"+"** (canto superior direito) → **"New repository"**
3. Preencha os dados:
   - **Repository name**: `doc2markdown-bot`
   - **Description**: `Bot Telegram que converte documentos para Markdown usando Docling`
   - **Visibility**: **Public** (para compartilhar) ou **Private** (só você)
   - **Initialize this repository**: **NÃO** marque nada
4. Clique em **"Create repository"**

### 2️⃣ Preparar Arquivos Localmente

Os arquivos já estão prontos em `/home/claude/doc2markdown-bot-github/`

Se estiver fazendo manualmente:

```bash
# Clone o repositório (vazio)
git clone https://github.com/seu-usuario/doc2markdown-bot.git
cd doc2markdown-bot

# Adicione todos os arquivos preparados
# (copie o conteúdo de doc2markdown-bot-github/)
```

### 3️⃣ Fazer Commit Inicial

```bash
# Configure seu Git (primeira vez)
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@example.com"

# Navegue para a pasta
cd doc2markdown-bot

# Verifique os arquivos
ls -la

# Estágio todos os arquivos
git add .

# Crie o commit inicial
git commit -m "chore: initial commit with bot structure"

# Push para o GitHub
git branch -M main
git push -u origin main
```

### 4️⃣ Verificar no GitHub

1. Acesse seu repositório: `github.com/seu-usuario/doc2markdown-bot`
2. Verifique se todos os arquivos estão lá:
   - ✅ `README.md` (arquivo principal)
   - ✅ `bot.py` (código do bot)
   - ✅ `requirements.txt` (dependências)
   - ✅ `LICENSE` (MIT)
   - ✅ `CONTRIBUTING.md` (guia de contribuição)
   - ✅ `.github/` (templates de issue/PR)
   - ✅ `.gitignore` (arquivos a ignorar)

### 5️⃣ Configurar Arquivo do Repositório

#### Adicionar Tópicos (Topics)

1. Na página do repositório, clique em ⚙️ **Settings**
2. Procure por **Topics** (sobre "About")
3. Adicione tags como:
   - `telegram-bot`
   - `docling`
   - `markdown-converter`
   - `python`

#### Ativar Discussions (Opcional)

1. Vá para **Settings** → **Features**
2. Marque ☑️ **Discussions**
3. Isso permite que colaboradores façam perguntas

#### Ativar Issues e Projetos

1. Na aba **Settings** → **Features**
2. Certifique-se que estão marcados:
   - ☑️ **Issues**
   - ☑️ **Projects**

### 6️⃣ Adicionar Badge ao README (Opcional)

No topo do seu `README.md`, você pode adicionar:

```markdown
# Doc2Markdown Bot 🤖

[![GitHub Stars](https://img.shields.io/github/stars/seu-usuario/doc2markdown-bot?style=social)](https://github.com/seu-usuario/doc2markdown-bot)
[![GitHub License](https://img.shields.io/github/license/seu-usuario/doc2markdown-bot)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
```

### 7️⃣ Configurar Secrets (para CI/CD futuro)

Se quiser adicionar automações depois:

1. Vá para **Settings** → **Secrets and variables** → **Actions**
2. Clique em **New repository secret**
3. Adicione seu `BOT_TOKEN` e `ALLOWED_CHAT_IDS` (opcional por enquanto)

## 🚀 Próximos Passos

Depois de criar o repositório:

1. **Compartilhe o link**: `https://github.com/seu-usuario/doc2markdown-bot`
2. **Faça o primeiro deploy**: Siga [SETUP.md](SETUP.md) para deployar no Render
3. **Teste o bot**: Verifique se está funcionando
4. **Promova**: Compartilhe em comunidades Python/Telegram

## 📋 Checklist Final

Antes de considerar pronto:

- [ ] Repositório criado no GitHub
- [ ] Todos os arquivos fazem push com sucesso
- [ ] README.md aparece na página principal
- [ ] LICENSE está visível
- [ ] Topics/Tags estão adicionados
- [ ] Issues estão habilitadas
- [ ] .gitignore está funcionando (nenhum `.env` commitado)

## ⚠️ Cuidados Importantes

1. **NÃO committe o `.env`**
   - Verifique `.gitignore` incluir `.env`
   - Se cometeu por acaso: `git rm --cached .env`

2. **NUNCA committe seu BOT_TOKEN**
   - Se vazar, regenere em @BotFather
   - Use `git-filter-branch` para remover do histórico se necessário

3. **Mensagens de commit claras**
   - Use o formato: `tipo: descrição`
   - Exemplo: `feat: add batch conversion`

4. **Síncrone regularmente**
   ```bash
   git pull origin main  # antes de trabalhar
   git push origin main  # depois de commitar
   ```

## 🆘 Troubleshooting

### Erro: "fatal: unable to access repository"

```bash
# Verifique se adicionou a chave SSH
ssh -T git@github.com

# Se não funcionar, use HTTPS
git remote set-url origin https://github.com/seu-usuario/doc2markdown-bot.git
```

### Erro: "Your branch is ahead of 'origin/main'"

```bash
# Faça push dos commits
git push origin main
```

### Arquivo `.env` foi cometido

```bash
# Remove do repositório (mas mantém localmente)
git rm --cached .env
git commit -m "remove: .env file"
git push origin main
```

## 📞 Precisa de Ajuda?

- Dúvidas sobre Git? [Git Docs](https://git-scm.com/doc)
- Dúvidas sobre GitHub? [GitHub Help](https://docs.github.com)
- Dúvidas sobre o projeto? Abra uma Issue no repositório

---

Parabéns! Seu repositório está pronto! 🎉

Se tiver dúvidas ou problemas, consulte [CONTRIBUTING.md](CONTRIBUTING.md) ou abra uma issue.
