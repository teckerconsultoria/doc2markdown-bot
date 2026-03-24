# Política de Segurança

## Relatando Vulnerabilidades

Se você descobrir uma vulnerabilidade de segurança, **não abra um issue público**. Em vez disso:

1. **Envie um email privado** para o mantenedor com:
   - Descrição da vulnerabilidade
   - Passos para reproduzir (se possível)
   - Impacto potencial
   - Sugestão de correção (se houver)

2. **Não compartilhe** os detalhes da vulnerabilidade publicamente até que seja corrigida

3. **Aguarde** uma resposta dentro de 7 dias

## Segurança Conhecida

### BOT_TOKEN

- **Nunca** committe o `BOT_TOKEN` no Git
- Use `.env` local e adicione `.env` ao `.gitignore`
- Use variáveis de ambiente no Render
- Se um token vazar, regenere imediatamente em @BotFather

### ALLOWED_CHAT_IDS

- Mantenha privado
- Separe múltiplos IDs com vírgula
- Valide IDs no código antes de processar

### Processamento de Arquivos

- Tenha cuidado com arquivos malformados
- Docling é responsável pela parsing segura
- Considere limitar tamanho de arquivo (se necessário)

## Dependências

### Atualizações Regulares

```bash
# Verifique vulnerabilidades conhecidas
pip install safety
safety check

# Ou use pip-audit
pip install pip-audit
pip-audit
```

### Dependências Críticas

- `python-telegram-bot`: Mantém API Telegram
- `docling`: Conversão de documentos
- `flask`: Web server

Monitore atualizações de segurança em:
- GitHub Dependabot
- PyPI security notices

## Boas Práticas de Segurança

1. **Validação de Input**
   - Valide todos os inputs do usuário
   - Restrinja tipos de arquivo se necessário
   - Use `ALLOWED_CHAT_IDS` para controle de acesso

2. **Processamento de Arquivos**
   - Defina timeout para conversão
   - Limite tamanho máximo de arquivo
   - Limpe arquivos temporários após uso

3. **Logs**
   - Não logue tokens ou IDs sensíveis
   - Logue erros para debugging
   - Revise logs regularmente

4. **Ambiente**
   - Use `.env` para configurações locais
   - Proteja seu `BOT_TOKEN`
   - Atualize Python regularmente

## Auditoria

Este projeto utiliza:

- [Dependabot](https://dependabot.com/) para alertas de vulnerabilidades
- [Safety](https://pyup.io/safety/) para auditoria de dependências
- Code review antes de merge

## Suportes e Patches

Vulnerabilidades descobertas receberão:

- **Críticas**: Patch dentro de 24-48h
- **Altas**: Patch dentro de 1 semana
- **Médias**: Patch no próximo release
- **Baixas**: Considerado para próxima release

---

Obrigado por ajudar a manter este projeto seguro! 🔒
