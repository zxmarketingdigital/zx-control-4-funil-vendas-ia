---
name: criar-miniapp
description: "Etapa 2 do Setup de Funil de Vendas com IA (Kit Lançador). O Agente Criador de Mini-Apps: constrói e formata, DO ZERO e de forma guiada, o mini-app de IA de nicho do aluno (1 a 5 agentes) já no mesmo padrão validado da ZX LAB (API em Cloudflare Workers + painel + demo populada + apresentação + proposta), pronto pra vender — perguntando ao aluno o nicho, a promessa, quantos agentes e a marca. Nada é hardcoded: JurisIA é só o exemplo da demo; serve pra QUALQUER nicho. É AUTOSSUFICIENTE — constrói a partir da anatomia descrita aqui, sem depender de template ou projeto externo. Bloqueia se a Etapa 1 (planejar) não estiver done e marca o gate 'criar-miniapp' como done. Use quando o aluno escolher a Etapa 2 no menu do /kit-lancador, ou disser: criar meu mini-app, construir o mini-app do zero, agente criador de mini-apps, quero um app de nicho pronto pra vender, etapa 2 do funil de vendas."
model: sonnet
effort: high
---

# /criar-miniapp — Etapa 2 (gate `criar-miniapp`)

O **Agente Criador de Mini-Apps**. Constrói, do zero, o mini-app de IA de nicho que o aluno vai
**vender** como produto low-ticket — no mesmo padrão de qualidade dos mini-apps prontos da ZX LAB
(API própria, painel com login por cliente, demo populada, apresentação e proposta). É a
alternativa a "revender um pronto": aqui o aluno cria o **próprio** produto.

**Genérico — a skill pergunta o nicho.** JurisIA (mini-app jurídico) é só o exemplo que a demo do
Setup usou. Esta skill serve pra QUALQUER nicho: clínica, imobiliária, contabilidade, delivery,
academia, restaurante, o que o aluno quiser. O nicho, a promessa, os agentes e a marca vêm das
**respostas do aluno** — nada aqui é preso a um segmento.

> **Autossuficiente (importante).** Este repositório é **público** e roda na máquina do aluno. A
> skill **NÃO** depende de nenhum projeto, casca ou template externo à máquina dele — a anatomia
> completa do mini-app está descrita aqui embaixo e é o que o Claude usa pra scaffoldar. (Se você
> for o instrutor e tiver skills internas de scaffolding instaladas, pode reusá-las pra acelerar —
> mas isso é opcional; o caminho padrão constrói tudo a partir desta anatomia.)

## Pré-condição (bloqueio)

```bash
python3 ~/.claude/skills/kit-lancador/estado.py can criar-miniapp    # exit 1 se 'planejar' não estiver done
python3 ~/.claude/skills/kit-lancador/estado.py start criar-miniapp
```
Se bloqueado, avisar que a **Etapa 1 (planejamento)** precisa terminar primeiro (o mini-app é
construído em cima do blueprint da oferta) e voltar ao menu.

## Passo 1 — Perguntar o produto ao aluno (AskUserQuestion) — nada hardcoded

Reaproveitar o que a Etapa 1 já definiu (`~/.operacao-ia/config/marca.json` + o blueprint em
`~/kit-lancador-artefatos/planejar/blueprint-oferta.md`). Confirmar / preencher com o aluno:

- **Nicho e persona do cliente final** (ex.: "advogado solo", "clínica de estética", "corretor").
- **Promessa** — o que o mini-app resolve pro cliente do aluno (a "dor nº1" do blueprint).
- **Quantos agentes de IA (1 a 5)** e **o que cada um faz** (ex.: analisar contrato, gerar
  proposta, resumir documento, extrair prazo, triar lead). Cada agente = uma tarefa clara.
- **Login por cliente (é o padrão).** Todo produto vendável isola dados por comprador — cada um
  acessa só o que é dele. É o que a anatomia abaixo assume e o que torna o mini-app vendável.
  Só dispensar auth se for uma **ferramenta pública de uso único** (sem dados por cliente) —
  nesse caso, sem tabelas por tenant e sem RLS de usuário (a anatomia de auth/RLS não se aplica).
  **Se dispensar login, PROTEGER contra abuso:** rota pública que chama o LLM com a chave do
  vendedor sem auth é dinheiro queimado por bot. Exigir **rate limit por IP + Turnstile (ou cota
  diária)** antes de chamar o Gemini — senão um caller automatizado esgota a cota/gasto do aluno.

Não chutar nenhuma resposta. Se o aluno não souber, sugerir a partir do nicho e confirmar.

## Passo 2 — Decidir o formato do produto (molda o schema, não depende de nada externo)

Duas formas comuns de mini-app — escolher com o aluno pela natureza do produto:

- **Consulta/Catálogo** — o app **casa uma necessidade do lead com um item** e um agente produz
  um resultado (imobiliária: imóvel↔perfil; jurídico: documento↔análise; e-commerce de nicho:
  produto↔dúvida). Entidades típicas: `clientes`, `itens/casos`, `documentos`, `resultados`.
- **Agendamento/Recompra** — o app gira em torno de **marcar horário e trazer o cliente de volta**
  (clínica, salão, consultório). Entidades típicas: `clientes`, `agendamentos`, `retornos`.

Isso só define QUAIS entidades o schema terá. A arquitetura (Passo 3) é a mesma nos dois casos.

## Passo 3 — Anatomia do mini-app (o padrão a scaffoldar — EMBUTIDO)

Construir em `~/kit-lancador-artefatos/miniapp/<slug-do-nicho>/` seguindo exatamente esta
estrutura. É o mesmo padrão dos mini-apps ZX LAB validados (API Cloudflare Workers + Supabase com
RLS + painel Pages + Gemini como cérebro trocável):

```
<slug>/
  package.json          # type:module; deps @supabase/supabase-js + zod; devDeps wrangler, vitest,
                        # @cloudflare/vitest-pool-workers, typescript. Scripts: test, typecheck,
                        # dev (wrangler dev), ci (typecheck+test+wrangler deploy --dry-run), deploy
  wrangler.toml         # name, main = src/index.ts, compatibility_date, (opcional) [triggers] crons
  tsconfig.json  vitest.config.ts  .env.example  README.md
  src/
    agentes.ts          # export const AGENTE_DEFS: Record<Agente,{titulo,prompt(entrada):string}>
                        #   — 1 a 5 agentes, cada um com um prompt de sistema do nicho
    schema.ts           # tipos + validação Zod das entidades + lista AGENTES
    auth.ts             # valida JWT do Supabase em TODA rota — fail-closed (sem token → 401)
    ia.ts               # wrapper do LLM (Gemini Flash), provider trocável; injeta disclaimer
    validacao.ts        # regras de negócio/guardrails do nicho
    db.ts               # 2 clientes Supabase: (a) por-comprador com o JWT DELE + anon key — é ele
                        #   que faz o CRUD, então a RLS aplica de verdade; (b) service role SÓ no
                        #   provisionamento/admin (criar-acesso), NUNCA no CRUD do tenant (fura RLS)
    config.ts           # "um valor, um lugar" — env/keys num só lugar
    index.ts            # router HTTP do Worker (rotas dos agentes + CRUD)
  painel/               # Cloudflare Pages (estático) — o que o CLIENTE FINAL do aluno usa
    index.html  app.js  style.css  config.example.js
                        # login + cards dos N agentes + CRUD das entidades (cada uma com "+ Novo")
  demo/                 # mostra o app funcionando SEM credencial nenhuma
    server.mjs  data.mjs
                        # mock server: login fake + dados fictícios do nicho (>=10 por entidade),
                        # serve o painel/ populado. É o que o aluno abre pra ver/demonstrar.
  setup/
    CLAUDE.md           # INSTALADOR conversacional (conduz o comprador, NÃO um wizard)
    smoke.mjs           # checagem rápida pós-instalação
  supabase/
    migrations/         # cria as tabelas do nicho; RLS LIGADA em TODA tabela e no Storage
    functions/criar-acesso/   # edge function que provisiona acesso de um novo cliente
  docs/
    apresentacao.html   # LP do mini-app (o aluno mostra pro cliente dele)
    proposta.html       # proposta comercial com o PREÇO preenchido (o preço vem do blueprint)
    DESIGN-TOKENS.md    # cores/tipografia da marca do aluno
  tests/                # Vitest: um arquivo por módulo + testes de invariante (auth fail-closed,
                        # RLS, validação) — teste que FICA VERMELHO se a regra for revertida
```

**Regras inquebráveis do padrão (não relaxar):**
- **Auth fail-closed** — nenhuma rota responde sem JWT válido do Supabase (quando há login).
- **RLS em toda tabela e no Storage** — cada cliente só enxerga os próprios dados. Multi-tenant real.
  O CRUD do comprador roda com o **JWT dele + anon key** (a RLS só protege se a query passar pela
  identidade do usuário); **service role jamais** faz CRUD de tenant (ele fura a RLS).
- **1 base Supabase por instalação.** **Cérebro = Gemini Flash**, atrás de `ia.ts` (provider trocável).
- **Um valor, um lugar** (`config.ts`) — zero credencial espalhada, zero segredo no código/repo.
- Cada agente de IA que gera texto injeta um **disclaimer** apropriado ao nicho (ex.: "rascunho —
  revise antes de usar").

## Passo 4 — Reskinar por nicho + aplicar a marca do aluno

- Gerar `src/agentes.ts` a partir das respostas do Passo 1: para cada agente, um `titulo` e um
  `prompt(entrada)` de sistema específico do nicho. **Replicar a ESTRUTURA do padrão, não copiar
  conteúdo de outro nicho.**
- Gerar o `schema.ts`/migrations com as entidades do Passo 2.
- Ler a marca do aluno (`~/.operacao-ia/config/marca.json`) e aplicar nome/cores/tipografia no
  `painel/` e nos HTMLs de `docs/`, gravando os valores em `DESIGN-TOKENS.md`. Cada aluno traz a
  **sua** paleta — nunca reusar a paleta de outro produto.

## Passo 5 — Popular a demo e validar o "pronto" (DoD embutido)

Só considerar a etapa concluída quando **TODOS** passarem (é o padrão de qualidade do produto, não
protótipo de brinquedo):

- [ ] `painel/` com **CRUD completo** de cada entidade (listar + "+ Novo" + editar).
- [ ] `demo/` **populada** com dados fictícios coerentes do nicho — **≥10 registros por entidade**,
      abrindo **sem credencial** (login fake + `data.mjs`).
- [ ] `docs/apresentacao.html` e `docs/proposta.html` renderizam, com o **preço do blueprint**
      preenchido e **zero placeholder** `{{...}}` sobrando.
- [ ] `tests/` verdes (`npm test`) — incluindo os testes de invariante (auth fail-closed, RLS).
- [ ] `npm run typecheck` e `npm run ci` (typecheck + test + `wrangler deploy --dry-run`) passam.

Abrir a demo local (`node demo/server.mjs`) e conferir no browser que o painel aparece populado.
"Pronto" = **visto funcionando**, não "arquivos criados".

> **O que este gate garante (e o que NÃO garante).** Fechar `criar-miniapp` significa: o app está
> **construído e validado rodando na demo local**. Ele **ainda não está hospedado** — o deploy real
> (Cloudflare Pages/Worker + aplicar as migrations Supabase + instalar os secrets no runtime) e a
> **URL real do painel** acontecem no **go-live, na Etapa 6 (Entrega)**, quando o aluno pluga as
> credenciais dele. A Entrega deploya primeiro e só então provisiona acesso — o email de acesso
> aponta pro painel **já no ar**, nunca pra um painel inexistente.

## Passo 6 — Persistir o manifesto + fechar a etapa

Antes de fechar, **gravar o manifesto do mini-app** — é o contrato que as etapas seguintes (LP,
entrega) leem pra descrever/entregar **exatamente este** app (senão a página de vendas e o email
de acesso anunciam um produto diferente do que foi construído):

```bash
mkdir -p ~/kit-lancador-artefatos/miniapp
# o mini-app construído fica em ~/kit-lancador-artefatos/miniapp/<slug>/
# gravar ~/kit-lancador-artefatos/miniapp/manifest.json com o contrato resolvido, ex.:
# {
#   "slug": "<slug>", "nicho": "...", "promessa": "...",
#   "agentes": [{"titulo":"...","funcao":"..."}, ...],   # a lista REAL (1 a 5) que você gerou
#   "entidades": ["clientes","..."], "tem_login": true,
#   "preco_principal": "<do blueprint>", "order_bump": "<do blueprint>"
# }
python3 ~/.claude/skills/kit-lancador/estado.py done criar-miniapp ~/kit-lancador-artefatos/miniapp/
```
Voltar ao menu do `/kit-lancador` e sugerir a **Etapa 3 (Página de vendas)**, que agora libera —
a LP vai anunciar exatamente este mini-app (lendo o `manifest.json`).

## Credenciais — pedidas na hora, salvas só em env local (nunca "depois", nunca no repo)

O mini-app usa **Gemini** (LLM) e **Supabase** (dados/RLS); na operação real, também um provedor de
envio pro provisionamento. Para **construir e rodar a demo**, **nenhuma** credencial é necessária
(a demo é sem-auth e populada). Quando o aluno for **plugar de verdade** (deploy/uso real), a skill
**verifica** se as chaves já estão em `~/.operacao-ia/config/*.env`; se faltar, **pede na hora e
salva lá** — **nunca** no repositório, nunca em arquivo versionado. Segredo só em env local.

> ⚠️ **Deploy real ≠ só ter o `.env`.** O runtime deployado (Cloudflare Worker / Supabase Edge
> Function) **não lê** o `~/.operacao-ia/config/*.env` da máquina do aluno — o `wrangler deploy
> --dry-run` passa e a produção falha em runtime por falta de chave. Ao deployar de verdade,
> **instalar os segredos no runtime**: `wrangler secret put GEMINI_API_KEY` (e demais) no Worker e
> `supabase secrets set ...` nas Edge Functions. O `.env` local serve só pra dev/demo.

## Régua

Um produto **de verdade, pronto pra vender** — API própria, painel com login por cliente, demo que
impressiona, apresentação e proposta com preço. Se não passa no DoD do Passo 5, **não está pronto**
— não avançar pra página de vendas anunciando um app que ainda não roda.
