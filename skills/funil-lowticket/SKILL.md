---
name: funil-lowticket
description: "Etapa 5 do Setup de Funil de Vendas com IA (Kit Lançador). Monta, do zero, o funil de conversão pós-checkout do produto low-ticket white-label do aluno: estrutura E copy do order bump (funcionalidades extras no checkout), do upsell OTO (oferta de maior ticket logo após a compra, ex. call de customização) e da recuperação de compra/checkout abandonado (email + WhatsApp anti-ban) — tudo refund-safe. É AUTOSSUFICIENTE: o método completo (validação do upsell + templates de copy) está embutido aqui, sem depender de nenhuma skill externa. Só gera copy e estrutura — não dispara nada. Bloqueia se a Etapa 4 (checkout) não estiver done e marca o gate 'funil' como done. Use quando o aluno escolher a etapa 5 no menu do /kit-lancador, ou disser: montar o funil, configurar upsell, copy do order bump, recuperar checkout abandonado, etapa 5 do lançador."
model: sonnet
effort: high
---

# /funil-lowticket — Etapa 5 (gate `funil`)

Monta o funil de conversão **pós-checkout** do produto low-ticket do aluno: o dinheiro que fica
na mesa depois que alguém já decidiu comprar. Três peças, nesta ordem de contato com o
comprador: **order bump** (oferecido no próprio checkout, antes de pagar) → **upsell OTO**
(oferecido logo depois da compra, enquanto o cliente está "quente") → **recuperação de
checkout abandonado** (quem começou e não terminou).

> **Autossuficiente (importante).** Este repositório é **público** e roda na máquina do aluno.
> Esta skill **NÃO** depende de nenhum outro projeto, template ou skill externa à máquina dele —
> o método de validação do upsell e todos os templates de copy estão escritos aqui embaixo. (Se
> você for o instrutor e tiver skills internas equivalentes instaladas, pode reusá-las pra
> acelerar — mas isso é opcional; o caminho padrão executa tudo a partir desta anatomia.)

**Esta etapa só gera copy e estrutura.** Nenhum disparo real (email/WhatsApp) acontece aqui —
isso é trabalho da automação de pós-venda do aluno, fora do escopo do Kit.

## Pré-condição (bloqueio)

```bash
python3 ~/.claude/skills/kit-lancador/estado.py can funil      # exit 1 se 'checkout' não estiver done
python3 ~/.claude/skills/kit-lancador/estado.py start funil
```
Se bloqueado, avisar que a **Etapa 4 (checkout)** precisa terminar primeiro (o funil se apoia no
preço e no fluxo de pagamento já definidos) e voltar ao menu.

## Passo 1 — Carregar o contexto (marca + blueprint)

```bash
cat ~/.operacao-ia/config/marca.json
cat "$(python3 ~/.claude/skills/kit-lancador/estado.py gate planejar | python3 -c 'import json,sys;print(json.load(sys.stdin).get("artifact",""))')"
```
Puxar de lá: `marca`, `nicho`, `persona`, `produto`, a seção de **preço de entrada**, a seção
**Order bump** (o que ele já prevê como funcionalidade extra), **`upsell`** (a oferta de maior
ticket já esboçada), `tom`, `cta`, dor nº1 do ICP e a garantia definida no blueprint.

Se `marca.json` não existir, **parar** e orientar o aluno a criá-la (não inventar marca). Se o
blueprint não existir, avisar que a Etapa 1 precisa ter rodado — sem preço e garantia definidos,
não dá pra estruturar o funil.

## Passo 2 — Régua anti-reembolso (aplica em TODA peça desta etapa)

Em low-ticket a métrica que importa não é conversão bruta, é **conversão × (1 − reembolso)**.
Copy que promete demais converte no clique e devolve no cartão — e reembolso alto derruba a
conta de pagamento. Vale para order bump, upsell e recuperação de compra:

1. **NUNCA prometer renda/faturamento.** Vender **capacidade e método**, não resultado
   financeiro ("acesse mais recursos" ✅, "vai faturar R$X" ❌).
2. **Depoimento/prova = experiência individual**, com disclaimer implícito ou explícito
   ("resultado individual"), e só se for real — não inventar prova.
3. **Urgência AUTÊNTICA.** Só usar prazo/janela se ela for real (condição de quem acabou de
   comprar, deadline fixo). Nunca countdown falso nem escassez inventada.
4. **Garantia real e honesta.** Herda a garantia do produto principal (ou define uma equivalente
   para o upsell) — nunca oferecer "garantia" que não vai ser cumprida.
5. **Recuperação de compra ajuda, não pressiona.** A pessoa que abandonou o checkout teve dúvida
   ou fricção, não desinteresse — a copy remove a fricção, não empurra.

Regras de escrita em toda peça: leitura simples, 1 ideia por parágrafo, benefício > feature,
sempre na 2ª pessoa ("você"), português brasileiro natural (nada de tradução engessada).

## Passo 3 — Validar e estruturar o upsell (planejamento embutido)

Antes de escrever qualquer copy, decidir a **estrutura** do order bump e do upsell — não sair
escrevendo em cima de uma oferta mal pensada. Resolver com o aluno (ou a partir do blueprint, se
já estiver claro):

- **Faz sentido?** O order bump e o upsell **complementam** o produto de entrada — não são um
  produto aleatório. Regra: se o comprador não entender em 1 frase por que essa oferta aparece
  logo depois da compra que ele acabou de fazer, o ângulo está errado.
- **Preço.** Order bump = acréscimo pequeno no checkout (ex.: +funcionalidades, versão com mais
  agentes/recursos). Upsell OTO = ticket bem maior que o produto de entrada (ex.: call de
  customização, implementação assistida, versão premium) — normalmente 3x a 10x o preço de
  entrada. Usar os valores do blueprint; se não estiverem lá, perguntar ao aluno.
- **Ângulo.** O upsell **acelera ou aprofunda** o que a pessoa já comprou — nunca é um segundo
  pitch do zero. Frase-chave: "você já provou que tem essa dor; isso leva você mais rápido/mais
  fundo".
- **Garantia.** Definir se o upsell tem garantia própria (recomendado) ou herda a do produto
  principal — deixar isso explícito na copy (Passo 4).
- **Economia do funil (vale o esforço?).** Estimar rapidamente se o upsell compensa a automação:
  ticket do upsell × taxa de conversão esperada, comparado ao esforço de manter a sequência de
  disparo ativa. Se o upsell for marginal (preço baixo, baixa aderência ao ICP), sinalizar ao
  aluno que talvez não valha construir a sequência completa — um order bump forte pode bastar.

Resumir a decisão numa tabela curta (vai para o artefato final):

| Peça | O que é | Preço | Ângulo | Garantia |
|------|---------|-------|--------|----------|
| Order bump | ... | ... | ... | ... |
| Upsell OTO | ... | ... | ... | ... |

## Passo 4 — Escrever a copy (as 3 peças)

Tom geral: depois do order bump (ainda no clima de decisão de compra), o upsell e a recuperação
são **conversa e suporte**, não venda agressiva — a pessoa já confiou (comprou ou quase).

### 4.1 — Order bump (checkbox no checkout)

Aparece **antes** do pagamento ser confirmado — precisa ser lido e decidido em segundos.

Como o gate `checkout` já está fechado, esta copy do order bump é **MATERIAL DE REFERÊNCIA** — o
aluno cola/ajusta manualmente no `~/kit-lancador-artefatos/checkout/checkout-preview.html` (ou na
hora de plugar o checkout real, pós-call).

```
[Headline — 1 linha, benefício direto]
✅ Sim, quero também [nome do extra] por apenas +R$[valor]

[2-3 bullets de benefício, não de feature]
• [o que o comprador ganha na prática, não "tem mais X"]
• [resultado/facilidade concreta]
• [remove uma objeção: "sem custo extra depois", "ativa na hora", etc.]

[Microcopy de reforço — 1 linha]
Só aparece agora — depois de fechar o pedido, esse preço não volta.
```
Regra: verdade sobre "só agora" — só usar se a oferta realmente não reaparecer no pós-venda
padrão. Se reaparecer, trocar por algo honesto ("o preço de order bump é o mais baixo que você
vai ver").

**Entrega 4.1:** o bloco preenchido com o extra real do blueprint (não inventar
funcionalidade) + 1 variante de headline para teste A/B.

### 4.2 — Upsell OTO (email + WhatsApp, logo após a compra)

**Email (2-3 mensagens):**

| # | Foco | Subject (modelo) |
|---|------|-------------------|
| U1 | Parabéns + "o próximo passo natural" | "Você já tem [produto]. Falta só [upsell] pra fechar o ciclo" |
| U2 | Prova + benefit stack do upsell | "Como isso acelera o que você acabou de comprar" |
| U3 | Janela fecha (só se for real) | "A condição de quem acabou de entrar fecha [data real]" |

**WhatsApp (3 mensagens, espaçadas — nunca todas juntas):**
```
[Msg 1 — sem link]
Opa [nome]! Vi que você acabou de garantir o [produto de entrada] 🙌
Curiosidade: quem pega isso costuma sentir falta de [o que o upsell resolve]. Faz sentido pra você?

[Msg 2 — depois da resposta / intervalo]
Tem um complemento que resolve exatamente isso: o [upsell].
Pega de onde o [produto] para e te leva até [resultado concreto]. Quer que eu mande o link com a
condição de quem acabou de entrar?

[Msg 3 — só após "sim" / intervalo, 1 link]
Boa! Tá aqui 👉 [link]
Qualquer dúvida me chama aqui mesmo. (E se não for a hora, sem problema — fica o convite.)
```
**Entrega 4.2:** emails + roteiro WhatsApp preenchidos com o upsell real do blueprint. Zero
promessa de renda. Saída fácil sempre sinalizada.

### 4.3 — Recuperação de compra / checkout abandonado (email + WhatsApp)

Gatilho: iniciou o checkout e não concluiu. Premissa: **dúvida ou fricção**, não desinteresse.

**Email (3 toques):**

| # | Papel | Subject (modelo) |
|---|-------|-------------------|
| R1 | Lembrete leve | "[Nome], você deixou seu acesso a meio caminho" |
| R2 | Objeção + garantia | "Travou no pagamento? (tem garantia, risco zero)" |
| R3 | Last call (só se a janela for real) | "Último aviso: sua condição expira [data real]" |

**WhatsApp (2-3 mensagens, espaçadas):**
```
[Msg 1 — sem link]
Oi [nome], aqui é do [marca] 👋
Vi que você começou a garantir o [produto] mas o pagamento não finalizou. Aconteceu algo no
checkout ou ficou alguma dúvida?

[Msg 2 — objeção/garantia, sem link ainda]
Se foi dúvida: o [produto] tem garantia de [X dias definidos no blueprint] — se não for pra você,
devolve. Risco zero.

[Msg 3 — só se houver interesse, 1 link]
Te mando o link pra finalizar de onde parou 👉 [link]
Se preferir, posso tirar qualquer dúvida antes. Sem pressa.
```
**Entrega 4.3:** emails + WhatsApp preenchidos. Incentivo honesto (garantia/dúvida), nunca falsa
escassez. Last call só com janela real.

## Passo 5 — Cuidados anti-ban do WhatsApp (aplica a 4.2 e 4.3)

- **Mensagens curtas**, tom de pessoa real — não bloco de marketing colado.
- **No máximo 1 link por mensagem**, e de preferência só na 2ª/3ª mensagem da sequência (nunca
  na primeira).
- **Staggered** — sequência espaçada no tempo, nunca várias mensagens seguidas no mesmo minuto
  (a cadência exata é definida pelo dispatcher do aluno; a copy só precisa assumir intervalos).
- Sem encurtador de link suspeito em massa — usar o link canônico do checkout.
- Personalizar com o primeiro nome. Sempre sinalizar saída fácil ("se não fizer sentido, é só
  ignorar").

## Passo 6 — Persistir o artefato

```bash
mkdir -p ~/kit-lancador-artefatos/funil
```
Gravar em `~/kit-lancador-artefatos/funil/copy-funil.md` o consolidado desta etapa:
1. A tabela do Passo 3 (order bump / upsell — preço, ângulo, garantia).
2. O bloco do order bump (4.1).
3. Emails + WhatsApp do upsell OTO (4.2).
4. Emails + WhatsApp da recuperação de checkout abandonado (4.3).
5. Um check final confirmando a régua do Passo 2 (zero promessa de renda, urgência autêntica
   onde houver, garantia coerente com o blueprint).

## Passo 7 — Fechar o gate

```bash
python3 ~/.claude/skills/kit-lancador/estado.py done funil ~/kit-lancador-artefatos/funil/copy-funil.md
```
Voltar ao menu do `/kit-lancador` e sugerir a **Etapa 6 (Entrega)**, que agora libera.

## Credenciais e disparo — pedidas na hora, nunca no repo, sempre dry-run

Esta etapa **não precisa de nenhuma credencial** para gerar a copy e a estrutura — é tudo texto.
Só entra credencial se o aluno quiser **testar um envio de exemplo** (preview de email/WhatsApp):

- Se a credencial do provedor de email/WhatsApp já estiver em `~/.operacao-ia/config/*.env`, usar.
- Se **faltar**, **perguntar na hora** e salvar **só** em `~/.operacao-ia/config/*.env` — nunca
  no repositório, nunca em arquivo versionado. Se o aluno preferir não configurar agora, seguir
  em modo **STUB/preview** (mostrar a copy pronta, sem enviar nada).
- **Qualquer envio de teste roda em modo dry-run** (simula, não entrega de verdade) até o aluno
  dar **OK explícito**. Nunca disparar email/WhatsApp real nesta etapa por conta própria.

## Fora de escopo aqui

Ativar o disparo real (cron/dispatcher do aluno) para o upsell e a recuperação de compra — isso
é automação de pós-venda, roda depois, fora do Kit. Aqui só se gera a copy e a estrutura do funil.

## Régua

Maximizar **conversão × (1 − reembolso)**. Order bump, upsell e recuperação só existem para
aumentar o valor entregue e recuperar fricção real — nunca para pressionar ou enganar quem já
confiou o suficiente para chegar até o checkout.
