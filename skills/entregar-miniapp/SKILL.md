---
name: entregar-miniapp
description: "Etapa 6 do Kit Lançador. Wrapper fino que faz a ENTREGA do mini-app hospedado ao comprador — provisionamento automático de acesso: gera login/senha e o email de boas-vindas com as credenciais. O aluno NÃO instala nada no cliente (modelo escalável); o comprador paga e recebe acesso ao painel na nuvem. Entrega exatamente o mini-app criado na etapa 2 (lê o manifesto). Marca o gate 'entrega' como done. Bloqueia se o gate 'funil' não estiver concluído. Use quando o aluno escolher a etapa 6 no menu do /kit-lancador, ou disser: entregar o mini-app, provisionar acesso, gerar credenciais do cliente, email de boas-vindas, etapa 6 do lançador."
model: sonnet
effort: medium
---

# /entregar-miniapp — Etapa 6 (gate `entrega`)

Casca fina que representa a **entrega = provisionamento de acesso** ao mini-app hospedado.
**Importante:** o modelo é escalável — o aluno **não instala nada** no cliente. O comprador paga
(o preço do produto, definido no blueprint) e recebe **login + senha** pra acessar o painel na nuvem.

O "que o cliente acessa" é **exatamente o mini-app criado na etapa 2** — o painel, os agentes e a
autenticação por cliente já construídos lá. Ler o manifesto (`~/kit-lancador-artefatos/miniapp/manifest.json`)
pra saber o produto, os agentes reais e o preço; nunca descrever features que o app não tem.

## Pré-condição (bloqueio)

```bash
python3 ~/.claude/skills/kit-lancador/estado.py can entrega     # exit 1 se 'funil' não estiver done
python3 ~/.claude/skills/kit-lancador/estado.py start entrega
```

## Passos

1. **Carregar** marca + blueprint + **manifesto do mini-app** (`~/kit-lancador-artefatos/miniapp/manifest.json`)
   — nome do produto, a **lista real de agentes** que foi construída (1 a 5, mais o que o order
   bump adiciona) e o preço. Não assumir contagem fixa de agentes; usar a do manifesto.
2. **Colocar o mini-app NO AR (go-live) ANTES de provisionar** — a Etapa 2 só validou o app na
   demo local; aqui ele vira um painel hospedado de verdade (senão a credencial aponta pra um
   painel que não existe). Com as credenciais do aluno (pedidas na hora, env local):
   - deploy do **Worker/Pages** (`wrangler deploy` / `wrangler pages deploy`),
   - aplicar as **migrations Supabase** + a edge function `criar-acesso`,
   - instalar os **secrets no runtime** (`wrangler secret put ...`, `supabase secrets set ...`) —
     o `~/.operacao-ia/config/*.env` local **não** chega no runtime deployado,
   - **capturar a URL real do painel** — é ela que vai no email de acesso.
   Na **demo** (sem credenciais), pular o deploy e marcar a URL como placeholder de exemplo.
3. **Provisionar acesso** (o coração desta etapa): gerar credenciais do comprador
   (login = email do cliente; senha inicial forte gerada localmente) e montar o **email de
   boas-vindas** com: URL do painel, login/senha, o que está incluído (os agentes do manifesto),
   instrução de trocar a senha no 1º acesso.
   - **Segredo nunca no repo.** Credenciais reais vivem em env/loja local do aluno; o email
     é o único lugar que carrega a senha, entregue 1x ao comprador.
4. **Persistir** (credenciais fictícias na demo):
   ```bash
   mkdir -p ~/kit-lancador-artefatos/entrega
   # salvar o email de boas-vindas em ~/kit-lancador-artefatos/entrega/email-credenciais.md
   ```
5. **Fechar o gate**:
   ```bash
   python3 ~/.claude/skills/kit-lancador/estado.py done entrega ~/kit-lancador-artefatos/entrega/email-credenciais.md
   ```
6. Voltar ao menu e sugerir a etapa 7 (divulgar).

## Deixar explícito ao aluno

*"O cliente paga e recebe acesso automático ao painel na nuvem — você não instala nada, não sobe
servidor por cliente. É por isso que escala."*
