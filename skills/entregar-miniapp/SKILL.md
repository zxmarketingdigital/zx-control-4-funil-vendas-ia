---
name: entregar-miniapp
description: "Etapa 5 do Kit Lançador. Wrapper fino que faz a ENTREGA do produto SaaS hospedado ao comprador — provisionamento automático de acesso: gera login/senha e o email de boas-vindas com as credenciais. O aluno NÃO instala nada no cliente (modelo escalável); o comprador paga e recebe acesso vitalício ao painel na nuvem. Reusa a casca nucleo-casca como referência do que o cliente acessa. Marca o gate 'entrega' como done. Bloqueia se o gate 'funil' não estiver concluído. Use quando o aluno escolher a etapa 5 no menu do /kit-lancador, ou disser: entregar o mini-app, provisionar acesso, gerar credenciais do cliente, email de boas-vindas, etapa 5 do lançador."
model: sonnet
effort: medium
---

# /entregar-miniapp — Etapa 5 (gate `entrega`)

Casca fina que representa a **entrega = provisionamento de acesso** ao SaaS hospedado.
**Importante:** o modelo é SaaS escalável — o aluno **não instala nada** no cliente. O
comprador paga (R$97 vitalício) e recebe **login + senha** pra acessar o painel na nuvem.

Referência do "que o cliente acessa": a casca `nucleo-casca` (mini-app hospedado, login por
token, sem DB) — usada só como modelo de painel, não copiada.

## Pré-condição (bloqueio)

```bash
python3 ~/.claude/skills/kit-lancador/estado.py can entrega     # exit 1 se 'funil' não estiver done
python3 ~/.claude/skills/kit-lancador/estado.py start entrega
```

## Passos

1. **Carregar** marca + blueprint (nome do produto, nº de agentes: 3 padrão + 2 no order bump).
2. **Provisionar acesso** (o coração desta etapa): gerar credenciais do comprador
   (login = email do cliente; senha inicial forte gerada localmente) e montar o **email de
   boas-vindas** com: URL do painel, login/senha, o que está incluído (3 ou 5 agentes),
   instrução de trocar a senha no 1º acesso.
   - **Segredo nunca no repo.** Credenciais reais vivem em env/loja local do aluno; o email
     é o único lugar que carrega a senha, entregue 1x ao comprador.
3. **Persistir** (credenciais fictícias na demo):
   ```bash
   mkdir -p ~/kit-lancador-artefatos/entrega
   # salvar o email de boas-vindas em ~/kit-lancador-artefatos/entrega/email-credenciais.md
   ```
4. **Fechar o gate**:
   ```bash
   python3 ~/.claude/skills/kit-lancador/estado.py done entrega ~/kit-lancador-artefatos/entrega/email-credenciais.md
   ```
5. Voltar ao menu e sugerir a etapa 6 (divulgar).

## Deixar explícito ao aluno

*"O cliente paga R$97 e recebe acesso vitalício automático ao painel na nuvem — você não
instala nada, não sobe servidor por cliente. É por isso que escala."*
