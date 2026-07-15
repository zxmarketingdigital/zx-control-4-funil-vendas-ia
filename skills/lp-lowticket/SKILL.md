---
name: lp-lowticket
description: "Etapa 3 do Kit Lançador. Wrapper fino que monta a landing page de venda do produto low-ticket white-label do aluno a partir do blueprint (etapa 1) e do manifesto do mini-app (etapa 2), invocando a skill-fonte /lp-low-ticket (modo MONTAR) com a marca e as cores do aluno. Entrega um index.html renderável e marca o gate 'lp' como done. Bloqueia se o gate 'criar-miniapp' não estiver concluído. Use quando o aluno escolher a etapa 3 no menu do /kit-lancador, ou disser: montar minha LP, criar landing page, página de vendas, etapa 3 do lançador."
model: sonnet
effort: high
---

# /lp-lowticket — Etapa 3 (gate `lp`)

Casca fina sobre **`/lp-low-ticket`** (modo MONTAR). Nome propositalmente diferente da fonte
(`lp-lowticket` vs `lp-low-ticket`) pra evitar colisão.

## Pré-condição (bloqueio)

```bash
python3 ~/.claude/skills/kit-lancador/estado.py can lp    # exit 1 se 'planejar'/'criar-miniapp' não estiverem done
python3 ~/.claude/skills/kit-lancador/estado.py start lp
```
Se bloqueado, avisar que as etapas anteriores (planejar + criar o mini-app) precisam terminar
primeiro e voltar ao menu.

## Passos

1. **Carregar** a marca (`~/.operacao-ia/config/marca.json`) + o blueprint da etapa 1 + o
   **manifesto do mini-app** (etapa 2) — a LP tem que anunciar **exatamente** o app construído:
   ```bash
   cat ~/.operacao-ia/config/marca.json
   cat "$(python3 ~/.claude/skills/kit-lancador/estado.py gate planejar | python3 -c 'import json,sys;print(json.load(sys.stdin).get("artifact",""))')"
   cat ~/kit-lancador-artefatos/miniapp/manifest.json 2>/dev/null   # nicho, agentes reais, preço
   ```
   As cores da LP saem de `marca.cores` (primária/acento/fundo); a copy sai do blueprint; os
   agentes/funcionalidades anunciados saem do `manifest.json` (nunca inventar features que o app
   não tem).

2. **Invocar `/lp-low-ticket`** no modo MONTAR, passando oferta + marca + manifesto já resolvidos
   (headline, benefit stack, objection handlers, CTA, Pixel/UTM/sticky-CTA). Deixar a fonte
   gerar o HTML. **Não repintar nem reescrever** o que ela devolve.

3. **Persistir**:
   ```bash
   mkdir -p ~/kit-lancador-artefatos/lp
   # salvar em ~/kit-lancador-artefatos/lp/index.html
   ```

4. **Fechar o gate**:
   ```bash
   python3 ~/.claude/skills/kit-lancador/estado.py done lp ~/kit-lancador-artefatos/lp/index.html
   ```

5. Voltar ao menu e sugerir a etapa 4 (checkout).

## Régua

Conversão × (1 − reembolso). LP tripwire honesta, sem promessa de renda. O CTA aponta pro
checkout que a etapa 4 vai montar.
