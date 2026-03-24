# Guia de Contribuição

Obrigado por se interessar em contribuir com o Doc2Markdown Bot! Este documento fornece diretrizes e instruções para colaborar com o projeto.

## 📋 Código de Conduta

Todos os colaboradores devem seguir este código de conduta:

- Seja respeitoso e inclusivo
- Aceite críticas construtivas
- Mantenha um ambiente seguro e welcoming
- Reporte comportamentos inapropriados

## 🐛 Reportando Bugs

### Antes de Reportar

- Verifique se o bug já foi reportado em [Issues](https://github.com/seu-usuario/doc2markdown-bot/issues)
- Tente reproduzir o problema com a versão mais recente
- Verifique se você está usando a versão correta do Python (3.8+)

### Ao Reportar

Inclua:

1. **Título descritivo**: "Erro ao processar PDF com imagens"
2. **Descrição clara**: O que esperava que acontecesse vs o que aconteceu
3. **Passos para reproduzir**: Instruções passo a passo
4. **Exemplo de código** (se aplicável)
5. **Screenshots/arquivos**: Se for problema visual ou com arquivo específico
6. **Informações do ambiente**:
   - OS (Windows, Linux, macOS)
   - Versão Python
   - Versão das dependências (`pip freeze`)

## ✨ Sugerindo Melhorias

### Antes de Sugerir

- Verifique se a sugestão já existe em [Issues](https://github.com/seu-usuario/doc2markdown-bot/issues)
- Avalie o escopo: pequeno ajuste vs grande feature

### Ao Sugerir

Inclua:

1. **Título claro**: "Suporte a conversão em lote"
2. **Descrição**: Por quê isso seria útil
3. **Exemplos**: Casos de uso específicos
4. **Benefícios**: O que ganharíamos

## 🔧 Desenvolvimento Local

### Setup do Ambiente

```bash
# Clone seu fork
git clone https://github.com/seu-usuario/doc2markdown-bot.git
cd doc2markdown-bot

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instale dependências de desenvolvimento
pip install -r requirements.txt

# Para desenvolvimento (opcional):
pip install pytest black flake8
```

### Branch Strategy

- `main`: Versão estável
- `develop`: Próximas features
- `feature/*`: Novas features (ex: `feature/batch-conversion`)
- `fix/*`: Correções (ex: `fix/pdf-parsing-bug`)

### Workflow

```bash
# 1. Sincronize com main
git checkout main
git pull upstream main

# 2. Crie sua branch
git checkout -b feature/sua-feature

# 3. Desenvolva
# ... edite arquivos ...

# 4. Teste suas mudanças
python bot.py  # teste local

# 5. Commit com mensagens descritivas
git commit -m "feat: adiciona suporte a DOCX"
git commit -m "fix: corrige erro de timeout"
git commit -m "docs: atualiza README"

# 6. Push
git push origin feature/sua-feature

# 7. Abra um Pull Request no GitHub
```

## 📝 Commit Messages

Siga o padrão [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>: <descrição curta>

<corpo detalhado (opcional)>

<rodapé (opcional)>
```

**Tipos:**
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Mudanças na documentação
- `style:` Formatação, sem mudanças lógicas
- `refactor:` Reorganização de código
- `test:` Testes
- `chore:` Atualizações de dependências

**Exemplos:**

```bash
git commit -m "feat: suporte a XLSX com múltiplas abas"
git commit -m "fix: corrige erro de encoding UTF-8"
git commit -m "docs: adiciona exemplos de uso"
```

## 🧪 Testes

Antes de submeter um PR, teste:

```bash
# Teste local com seu BOT_TOKEN e ALLOWED_CHAT_IDS
python bot.py

# Teste com diferentes tipos de arquivo
# - PDF normal
# - PDF com imagens
# - DOCX
# - URL
```

Se usar pytest (opcional):

```bash
pytest tests/
```

## 📋 Pull Request Process

### Antes de Criar o PR

1. Atualize o `main` localmente
2. Rebase sua branch: `git rebase main`
3. Resolva conflitos, se houver
4. Teste tudo novamente

### Ao Criar o PR

Use o template:

```markdown
## 📝 Descrição
Breve descrição do que foi feito

## 🎯 Tipo de Mudança
- [ ] Bug fix (mudança que corrige um problema)
- [ ] Nova feature (mudança que adiciona funcionalidade)
- [ ] Breaking change (mudança que pode quebrar funcionalidade existente)
- [ ] Atualização de documentação

## 📸 Como Testar
Passos para verificar as mudanças

## ✅ Checklist
- [ ] Meu código segue o style do projeto
- [ ] Executei testes locais
- [ ] Atualizei a documentação
- [ ] Commit messages seguem o padrão

## 🔗 Relacionado
Closes #123
```

## 💭 Code Review

Esperamos que:

- **Mantenedores** respondam em até 7 dias
- **Colaboradores** respeitem feedback
- **Todos** focam no código, não na pessoa

## 📚 Recursos

- [Docling Docs](https://github.com/docling-project/docling)
- [Python-Telegram-Bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Conventional Commits](https://www.conventionalcommits.org/)

## ❓ Dúvidas?

- Abra uma Discussion no repositório
- Commente em um Issue existente
- Envie um email (se houver contato disponível)

---

Obrigado por contribuir! 🎉
