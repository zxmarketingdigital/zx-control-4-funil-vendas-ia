---
name: kit-lancador
description: "Orquestrador do Setup de Funil de Vendas com IA (Kit Lançador — ZX Control 4). Conduz o aluno pelo ciclo completo de lançar um produto digital low-ticket white-label — planejar produto → criar o mini-app de IA do nicho → landing page → checkout Pagar.me → funil (order bump + upsell) → entrega/onboarding do mini-app → divulgação em massa — com menu numérico, estado persistido e bloqueio de avanço (cada etapa exige a anterior concluída). Lê a marca do aluno de ~/.operacao-ia/config/marca.json. Use SEMPRE que o aluno disser: INICIAR, funil de vendas com ia, kit lançador, lançar produto low ticket, menu do lançador, menu do setup, quero lançar meu produto, começar lançamento, /kit-lancador, continuar lançamento, status do lançamento, próximo passo do lançamento."
model: sonnet
effort: medium
---

# /kit-lancador — Orquestrador do Setup de Funil de Vendas com IA

Casca fina que **conduz o aluno** pelas 7 etapas de lançar um produto digital low-ticket
(R$9–97) white-label, no Claude Code dele. Não reimplementa nada: cada etapa é um wrapper
que invoca uma skill-fonte já validada. O valor desta skill é o **fluxo guiado + estado + gates**.

**Esta skill NÃO escreve arquivo de produto diretamente.** Ela só:
1. lê a marca do aluno e o estado do lançamento,
2. mostra o menu,
3. delega a etapa escolhida à skill wrapper correspondente,
4. bloqueia o avanço se a etapa anterior não estiver `done`.

## As 7 etapas (ordem fixa — é lei)

| # | Gate | Skill wrapper | O que produz |
|---|------|---------------|--------------|
| 1 | `planejar` | `/planejar-produto-lowticket` | Blueprint da oferta (preço, benefit stack, order bump, upsell, garantia) |
| 2 | `criar-miniapp` | `/criar-miniapp` | Mini-app de IA do nicho do zero (1 a 5 agentes) — painel + demo + apresentação + proposta |
| 3 | `lp` | `/lp-lowticket` | Landing page HTML com a marca do aluno |
| 4 | `checkout` | `/checkout-white-label` | Checkout Pagar.me (produto principal + order bump, preço do blueprint) |
| 5 | `funil` | `/funil-lowticket` | Copy do funil: order bump + upsell OTO + recuperação |
| 6 | `entrega` | `/entregar-miniapp` | Provisionamento de acesso ao mini-app (credenciais + email de boas-vindas) |
| 7 | `divulgar` | `/divulgar-lowticket` | Pacote de divulgação: email blast + copy de post + carrossel |

**Regra dura:** cada gate só libera com o anterior `done`. Não pular etapa.

## Estado / resume

Fonte da verdade: `~/.kit-lancador/estado.json`, lido/escrito **só** via
`~/.claude/skills/kit-lancador/estado.py` (stdlib puro, escrita atômica). Comandos:

```bash
python3 ~/.claude/skills/kit-lancador/estado.py status      # tabela dos 7 gates + próximo
python3 ~/.claude/skills/kit-lancador/estado.py continuar    # imprime o próximo gate pendente
python3 ~/.claude/skills/kit-lancador/estado.py can <gate>   # exit 0 se pode avançar, 1 se bloqueado
python3 ~/.claude/skills/kit-lancador/estado.py start <gate> # marca in-progress
python3 ~/.claude/skills/kit-lancador/estado.py done <gate> <artefato>  # marca done + salva caminho
python3 ~/.claude/skills/kit-lancador/estado.py redo <gate>  # volta um gate pra pending
python3 ~/.claude/skills/kit-lancador/estado.py abortar      # arquiva e zera o estado
```

## Fluxo do orquestrador

### Passo 0 — carregar contexto (toda invocação)

```bash
# Marca do aluno (white-label). Se não existir, orienta a criar antes de seguir.
cat ~/.operacao-ia/config/marca.json 2>/dev/null || echo "SEM_MARCA"
# Estado do lançamento
python3 ~/.claude/skills/kit-lancador/estado.py status
```

- Se `marca.json` não existe → avisar: *"Antes de começar, preciso da sua marca em
  `~/.operacao-ia/config/marca.json` (nome, nicho, cores, CTA). Quer que eu ajude a montar?"*
  e **não avançar** sem isso (as skills de LP/copy/carrossel leem essa marca).
- Sempre mostrar o `status` antes do menu, pra o aluno saber onde parou.

### Passo 1 — mostrar o menu

```
╔══════════════════════════════════════════════════════════╗
║   FUNIL DE VENDAS COM IA — <marca>  •  produto low-ticket  ║
╠══════════════════════════════════════════════════════════╣
║   1. Planejar produto (oferta/blueprint)          [⏳]     ║
║   2. Agente Criador de Mini-Apps                  [⏳]     ║
║   3. Landing page                                 [⏳]     ║
║   4. Checkout Pagar.me                            [⏳]     ║
║   5. Funil (order bump + upsell + copy)           [⏳]     ║
║   6. Entrega (provisionar acesso ao mini-app)     [⏳]     ║
║   7. Divulgação (email + posts + carrossel)       [⏳]     ║
╠══════════════════════════════════════════════════════════╣
║   S. Status    C. Continuar de onde parei    R. Refazer   ║
╚══════════════════════════════════════════════════════════╝
```

Os ícones `[⏳/🔄/✅]` vêm do `estado.py status`. Preencher `<marca>` com o nome da marca.

### Passo 2 — rotear a escolha

| Entrada | Ação |
|---------|------|
| `1`–`7` | Antes de delegar: `~/.claude/skills/kit-lancador/estado.py can <gate>`. Se **bloqueado**, avisar qual etapa falta e voltar ao menu. Se ok → `~/.claude/skills/kit-lancador/estado.py start <gate>` → **invocar a skill wrapper** da etapa → ao concluir, o wrapper roda `~/.claude/skills/kit-lancador/estado.py done <gate> <artefato>`. |
| `S` | `~/.claude/skills/kit-lancador/estado.py status` |
| `C` | `~/.claude/skills/kit-lancador/estado.py continuar` → pega o próximo gate pendente e roteia como se fosse o número dele (respeitando o gate). |
| `R` | perguntar qual etapa refazer → `~/.claude/skills/kit-lancador/estado.py redo <gate>` (isso re-bloqueia as etapas seguintes até refazer). |

**Nunca** invocar a skill de uma etapa sem antes checar `can <gate>`. O bloqueio é o
principal motivo desta orquestradora existir — evita LP sem oferta, checkout sem LP, etc.

### Passo 3 — depois de cada etapa

- Confirmar que o wrapper marcou `done` (rodar `status` de novo).
- Mostrar o menu atualizado e sugerir a próxima etapa (`continuar`).
- Quando os 7 gates estiverem `done` → parabenizar e listar todos os artefatos
  (`~/.claude/skills/kit-lancador/estado.py status` mostra o caminho de cada um).

## Não fazer

- Não plugar conta Pagar.me, domínio ou Pixel reais aqui — isso é config por env local do
  aluno (`~/.operacao-ia/config/`), comunicada como "nas próximas aulas você pluga suas
  credenciais". A demo/gate roda com stub.
- Não disparar email/WhatsApp de verdade sem o aluno confirmar (as skills-fonte já rodam
  dry-run por padrão).
- Não copiar lógica das skills-fonte pra cá. Se precisar mudar como uma etapa funciona,
  mexe na skill-fonte, não no wrapper.
