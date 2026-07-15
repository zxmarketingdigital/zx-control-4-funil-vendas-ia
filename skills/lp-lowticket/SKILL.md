---
name: lp-lowticket
description: "Etapa 3 do Kit Lançador. Monta, do zero, a landing page de venda (HTML single-file) do produto low-ticket white-label do aluno — a partir do blueprint da oferta (Etapa 1) e do manifesto do mini-app (Etapa 2) — anunciando EXATAMENTE o app construído, com a marca/cores do aluno. Headline, benefit stack, objection handlers, prova social, CTA, Meta Pixel/UTM/sticky-CTA. É AUTOSSUFICIENTE: o método de copy de conversão e o HTML/CSS estão descritos aqui embaixo, sem depender de nenhum projeto ou skill externa à máquina do aluno. Marca o gate 'lp' como done. Bloqueia se o gate 'criar-miniapp' não estiver concluído. Use quando o aluno escolher a etapa 3 no menu do /kit-lancador, ou disser: montar minha LP, criar landing page, página de vendas, etapa 3 do lançador."
model: sonnet
effort: high
---

# /lp-lowticket — Etapa 3 (gate `lp`)

Monta a **página de vendas** do produto low-ticket que o aluno vai vender: a landing page que
recebe o tráfego (pago ou orgânico) e leva direto ao checkout. É copy de conversão + HTML
estático, não é teoria — o que esta skill produz é um **arquivo renderável no browser**.

> **Autossuficiente (importante).** Este repositório é **público** e roda na máquina do aluno. A
> skill **NÃO** depende de nenhum projeto, casca ou template externo à máquina dele — a estrutura
> de copy e o design system embutidos aqui embaixo são o que o Claude usa pra montar a LP. (Se
> você for o instrutor e tiver skills internas de LP/copy instaladas, pode reusá-las pra acelerar
> — mas isso é opcional; o caminho padrão constrói tudo a partir deste método.)

## Pré-condição (bloqueio)

```bash
python3 ~/.claude/skills/kit-lancador/estado.py can lp    # exit 1 se 'planejar'/'criar-miniapp' não estiverem done
python3 ~/.claude/skills/kit-lancador/estado.py start lp
```
Se bloqueado, avisar que as etapas anteriores (**Planejar produto** + **Agente Criador de
Mini-Apps**) precisam terminar primeiro e voltar ao menu.

## Passo 1 — Carregar marca + blueprint + manifesto (nada hardcoded)

A LP **não inventa nada** — copy, preço e features vêm sempre das etapas anteriores:

```bash
cat ~/.operacao-ia/config/marca.json
cat "$(python3 ~/.claude/skills/kit-lancador/estado.py gate planejar | python3 -c 'import json,sys;print(json.load(sys.stdin).get("artifact",""))')"
cat ~/kit-lancador-artefatos/miniapp/manifest.json
```

- **Marca** (`marca.json`) dá nome, nicho, persona, tom e **cores** (`marca.cores.primaria` /
  `acento` / `fundo`) — se `marca.json` não existir, **parar** e orientar o aluno a criá-la
  ("me ajuda a montar minha marca" no chat) antes de continuar. Nunca inventar uma marca.
- **Blueprint** (Etapa 1) dá a oferta resolvida: preço principal, order bump, upsell, ICP, dor
  nº1, garantia, benefit stack já ancorado.
- **Manifesto do mini-app** (Etapa 2, `~/kit-lancador-artefatos/miniapp/manifest.json`) dá o
  **produto real**: nicho, promessa, a lista exata de agentes/funcionalidades, se tem login,
  preço principal e order bump. **A LP só pode anunciar o que está nesta lista** — nenhum
  agente, funcionalidade ou benefício que o mini-app não tenha. Se o manifesto estiver ausente
  (a etapa 2 deveria ter bloqueado isso, mas confira), **parar** e voltar o aluno pra Etapa 2.

## 🚨 Régua central — conversão × (1 − reembolso) — NÃO violar

Em low-ticket a métrica que importa não é conversão bruta, é **conversão × (1 − reembolso)**.
Uma LP que promete demais converte no clique e devolve no cartão. Por isso, em TODA a copy:

1. **NUNCA prometer renda/faturamento garantido.** "Fature 5 dígitos" → "Aprenda a montar/operar
   X". Vender **capacidade e método**, não resultado financeiro.
2. **Valores de mercado ≠ promessa ao comprador.** "Esse tipo de serviço é cobrado R$1k-5k no
   mercado" ✅. "Você vai faturar R$X" ❌.
3. **Depoimentos = experiências individuais**, sempre com disclaimer ("resultados individuais,
   não são garantia") — e só se forem reais (nunca inventar depoimento).
4. **Urgência AUTÊNTICA.** Countdown só com deadline real (data fixa configurável) ou janela por
   visitante persistida em `localStorage` — **nunca** resetar a cada visita/minuto. Escassez só
   se real.
5. **Seção "Pra quem é / pra quem NÃO é" é obrigatória** — filtrar o comprador errado ANTES da
   compra é a maior alavanca anti-reembolso.

Se o aluno pedir copy de renda agressiva, alertar sobre o risco de reembolso e oferecer a versão
honesta como default.

## Passo 2 — Estrutura + copy (12 seções, método embutido)

Montar a copy em MD/rascunho antes de codar (rápido de revisar com o aluno). **Estrutura padrão
(tripwire honesto)**, adaptada com o manifesto do mini-app:

```
1.  Promo bar             → countdown honesto + preço âncora (ex.: de R$X por R$Y — os dois do blueprint)
2.  Hero                  → headline de CAPACIDADE + sub + CTA visível + print/demo do mini-app real
3.  Contexto antes/depois → a dor do jeito antigo vs. resolvida pelo mini-app (sem promessa de renda)
4.  Pra quem é / NÃO é    ★ filtro de comprador (anti-reembolso)
5.  O que você recebe     → os agentes/funcionalidades EXATOS do manifest.json, 1 bullet por agente
6.  Benefit stack ANCORADO → valor real de cada item somando → preço hoje (ver template abaixo)
7.  Casos de uso           → 2-4 cenários reais do nicho (valores = "o que o mercado cobra", com disclaimer)
8.  Prova social            → depoimentos reais (se houver) + "resultados individuais" — ou omitir a seção se não há prova real ainda
9.  Oferta + garantia      → preço, bullets do que leva, garantia em destaque (reversão de risco)
10. Autoridade              → quem monta/entrega, credenciais com lastro (sem exagero)
11. FAQ                     → objeções: preço, "tão barato?", "vou conseguir usar?", acesso, garantia
12. CTA final + STICKY mobile
```

**Headline (3 fórmulas de capacidade, escolher 1):**
- "Como [resultado] sem [dor/obstáculo]" — ex.: "Como automatizar [tarefa do nicho] sem contratar ninguém"
- "O sistema de N passos pra [resultado]" — ex.: "O sistema de 3 passos pra [transformação]"
- "[N] [persona] já usam pra [resultado]" — só se for número real, nunca inventado

**Benefit stack (ancoragem honesta):**
```
✅ [Agente 1 do manifesto] — [o que faz] ............ Valor: R$X
✅ [Agente 2 do manifesto] — [o que faz] ............ Valor: R$X
✅ [Bônus/order bump, se aplicável] ................. Valor: R$X
─────────────────────────────────────────────────────
Valor total: R$N   •   Hoje: R$[preco_principal do blueprint]
```

**Objection handlers (PAS — Problema/Agitação/Solução), no FAQ:**
- Preço: "Entendo que pareça investimento. Mas [produto] se paga quando você [ROI específico do
  nicho] — e com a garantia, o risco é seu, não meu."
- "Por que tão barato?": honestidade — é um produto de entrada, sem intermediário, entrega digital.
- "Vou conseguir usar?": login simples + [tempo real de onboarding] + suporte do que está incluso.
- Confiança/garantia: prazo e condição exatos da garantia do blueprint.

**Regras de copy (aplicar em TODA a LP):**
- Leitura nível 8ª série — frases curtas, 1 ideia por parágrafo.
- Benefício > feature; sempre na 2ª pessoa ("você"); liderar com a transformação, não com a lista
  técnica.
- **CTA em 1ª pessoa, específico**: "Quero meu acesso por R$[preço]", "Garantir minha vaga",
  "Quero [resultado]". Nunca "Enviar" / "Clique aqui".
- Power words só com lastro (grátis, comprovado, vitalício, passo a passo). "Garantido" **só**
  se referindo à garantia de reembolso — nunca a resultado/renda.

## Passo 3 — Build (HTML+CSS single-file, autocontido)

- **Um único arquivo HTML** com CSS inline via `<style>` (CSS variables) — sem build, sem
  framework, sem dependência externa além de fontes via `<link>`. É o que garante velocidade em
  tráfego pago e roda em qualquer host estático.
- **Design tokens (fallback estrutural embutido — sem depender de nenhum arquivo externo):**
  ```css
  :root {
    --cor-primaria: <marca.cores.primaria, senão #0B1220>;
    --cor-acento:   <marca.cores.acento,   senão #D97706>;  /* CTA, preço, destaques */
    --cor-fundo:    <marca.cores.fundo,    senão #FFFFFF>;
    --fonte-titulo: 'Inter', system-ui, sans-serif;
    --fonte-corpo:  'Inter', system-ui, sans-serif;
    --fonte-mono:   'JetBrains Mono', ui-monospace, monospace; /* preços, countdown, badges */
  }
  ```
  Se `marca.json` trouxer `cores`, usar SEMPRE a paleta do aluno (identidade white-label — nunca
  reusar a cor de outro aluno). Se não trouxer, cair no fallback acima (âmbar `#D97706` + Inter +
  JetBrains Mono) só pra não travar a etapa — e sinalizar ao aluno que pode personalizar depois.
- **Obrigatórios técnicos:**
  - **Meta Pixel**: `<script>` de inicialização + evento `InitiateCheckout`/`AddToCart` disparado
    no clique de cada CTA, com `<noscript>` fallback. Meta Pixel ID e GA ID são
    **identificadores client-side públicos**: se o aluno informar, inserir direto no HTML, por
    exemplo `fbq('init','<PIXEL_ID>')`, como em qualquer LP de produção. Se ele ainda não tiver
    Pixel ID, **não travar**: gerar em modo STUB com o placeholder comentado (`<!-- PIXEL_ID: cole
    aqui quando tiver -->`) e seguir.
  - **UTM/SCK tracker**: script pequeno que lê UTM da URL de entrada e propaga como parâmetro
    (`sck` ou equivalente) pros links de CTA que vão apontar pro checkout.
  - **CTA do checkout**: como a Etapa 4 (checkout) ainda não rodou, os links de CTA apontam pra
    um placeholder identificável (`href="#checkout-pendente"` ou `data-checkout="pendente"`) —
    documentar num comentário HTML que a Etapa 4 substitui esse href pelo link real do Pagar.me.
  - **Sticky CTA mobile**: barra fixa (preço + botão) com `env(safe-area-inset-bottom)` e
    `body{padding-bottom}` correspondente pra não cobrir conteúdo.
  - **Countdown honesto**: deadline fixo configurável no topo do script, OU janela por
    visitante via `localStorage` (grava o primeiro acesso, calcula o restante) — nunca reset a
    cada carregamento.
  - Fonts via `<link rel="preconnect">` + `<link rel="stylesheet">` (nunca `@import`, é mais
    lento). Meta tags Open Graph (title/description/image) preenchidas com a marca do aluno.
    CTA repetido a cada 2-3 seções (hero, benefit stack, oferta, FAQ, final).

## Passo 4 — Validar (DoD embutido — só considerar pronto se TODOS passarem)

- [ ] As 12 seções presentes e na ordem, `<section>`/`</section>` balanceados.
- [ ] **Zero** menção a renda/faturamento garantido — grep manual por "fatur", "renda garantida",
      "ganhe R$", "enriqueça" e remover/reescrever qualquer ocorrência.
- [ ] Os agentes/funcionalidades citados batem **exatamente** com `manifest.json` — nenhum a
      mais, nenhum a menos.
- [ ] Preço principal e order bump batem com o blueprint (Etapa 1) — não hardcodar outro valor.
- [ ] Pixel (ou STUB comentado) + UTM tracker + sticky CTA + countdown honesto presentes.
- [ ] Mobile: sem scroll horizontal, fonte ≥16px, alvo de toque ≥44px.
- [ ] HTML bem formado (parse rápido com `python3 -c "import html.parser"` ou abrir no browser).
- [ ] Abrir localmente (`python3 -m http.server` na pasta) e conferir visualmente hero + sticky
      CTA + FAQ — "pronto" é **visto renderizando**, não "arquivo criado".

## Passo 5 — Persistir o artefato + fechar a etapa

```bash
mkdir -p ~/kit-lancador-artefatos/lp
# salvar o HTML final em ~/kit-lancador-artefatos/lp/index.html
python3 ~/.claude/skills/kit-lancador/estado.py done lp ~/kit-lancador-artefatos/lp/index.html
```

Voltar ao menu do `/kit-lancador` e sugerir a **Etapa 4 (Checkout Pagar.me)** — ela vai ler esta
LP e trocar o placeholder `#checkout-pendente` pelo link real.

## Credenciais e identificadores — regra correta

Há duas categorias, sem misturar:

- **Segredos de verdade** — chave secreta Pagar.me e tokens de API: nunca vão para HTML ou
  repositório; ficam só em `.env` local. Isso é assunto da Etapa 4, não desta.
- **Identificadores client-side públicos** — Meta Pixel ID e GA ID: quando o aluno fornecer,
  entram direto no HTML (ex.: `fbq('init','<PIXEL_ID>')`), exatamente como qualquer LP de
  produção. Se não fornecer, manter só o placeholder comentado (STUB) e seguir.

Esta etapa não dispara email nem WhatsApp; se alguma automação futura reaproveitar esta LP pra
disparo em massa, isso roda **sempre em dry-run até o aluno dar OK explícito** — nunca disparo
automático.

## Régua

Conversão × (1 − reembolso). LP tripwire honesta, sem promessa de renda, anunciando exatamente o
mini-app que a Etapa 2 construiu. O CTA aponta pro checkout que a Etapa 4 vai montar.
