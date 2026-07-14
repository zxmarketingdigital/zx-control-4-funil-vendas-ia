---
name: divulgar-lowticket
description: "Etapa 6 (final) do Kit Lançador. Wrapper fino que monta o pacote de divulgação em massa do produto low-ticket white-label do aluno — GERA a copy do email de lançamento aqui (lendo marca + blueprint) e invoca as skills-fonte /gerar-copy-post (legenda + hashtags + CTA por plataforma) e /gerar-carrossel (PNGs para Instagram); /email-blast entra só como DISPARADOR em dry-run (ele exige HTML pronto + destinatários e não gera copy). Sem disparo real sem confirmação. Marca o gate 'divulgar' como done e fecha o ciclo. Bloqueia se o gate 'entrega' não estiver concluído. Use quando o aluno escolher a etapa 6 no menu do /kit-lancador, ou disser: divulgar meu produto, gerar posts, montar carrossel, email de lançamento, etapa 6 do lançador."
model: sonnet
effort: medium
---

# /divulgar-lowticket — Etapa 6 (gate `divulgar`)

Casca fina sobre as fontes de divulgação: **`/gerar-copy-post`** (post social) e
**`/gerar-carrossel`** (carrossel IG) geram artefato lendo `marca.json`. O **email de
lançamento** é montado aqui a partir da marca + blueprint (essas fontes não escrevem a copy
do email), e `/email-blast` entra só como **disparador em dry-run** — ele exige um HTML pronto
+ destinatários, **não** gera copy nem lê `marca.json`.

## Pré-condição (bloqueio)

```bash
python3 ~/.claude/skills/kit-lancador/estado.py can divulgar    # exit 1 se 'entrega' não estiver done
python3 ~/.claude/skills/kit-lancador/estado.py start divulgar
```

## Passos

1. **Carregar** marca (`~/.operacao-ia/config/marca.json`) + blueprint (oferta, preço, CTA).
   `/gerar-copy-post` e `/gerar-carrossel` já leem `marca.json`; o email é escrito aqui.
2. **GERAR a copy do email de lançamento (passo dedicado, ANTES do disparo).** As fontes de
   divulgação **não** geram o email e `/email-blast` **não** escreve copy — então este wrapper
   redige o email na **voz da marca** a partir de `marca.json` + blueprint (assunto, corpo,
   oferta, preço, CTA, garantia — sem promessa de renda) e salva **os dois formatos**:
   ```bash
   mkdir -p ~/kit-lancador-artefatos/divulgar
   # escrever a copy gerada em:
   #   ~/kit-lancador-artefatos/divulgar/email-lancamento.md   (revisão do aluno)
   #   ~/kit-lancador-artefatos/divulgar/email-lancamento.html (o que o /email-blast dispara)
   ```
3. **Invocar as fontes sociais** com a oferta resolvida — deixar cada uma gerar seu artefato,
   **sem reescrever**:
   - `/gerar-copy-post` → legenda + hashtags + CTA (Instagram, e/ou outra plataforma).
   - `/gerar-carrossel` → PNGs 1080×1350 do carrossel de lançamento.
4. **Disparar em dry-run** — `/email-blast` é **só o disparador**, não o gerador. Passar o HTML
   já gerado no passo 2 + a lista de destinatários do aluno, em modo teste:
   ```bash
   # /email-blast --dry-run  (HTML: ~/kit-lancador-artefatos/divulgar/email-lancamento.html)
   #   -> valida render + destinatários; NÃO envia. Envio real só com OK explícito do aluno.
   ```
5. **Fechar o gate** (e o ciclo):
   ```bash
   python3 ~/.claude/skills/kit-lancador/estado.py done divulgar ~/kit-lancador-artefatos/divulgar/
   ```
6. Voltar ao menu: os 6 gates estão `done`. Parabenizar o aluno e listar todos os artefatos
   (`python3 ~/.claude/skills/kit-lancador/estado.py status`).

## Regra dura — sem disparo cego

**Nunca** disparar email ou WhatsApp de verdade sem o aluno confirmar explicitamente. As
fontes rodam dry-run por padrão; manter assim. O canal/lista real é config do próprio aluno.
