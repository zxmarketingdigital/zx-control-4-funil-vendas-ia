---
name: planejar-produto-lowticket
description: "Etapa 1 do Kit Lançador. Planeja a OFERTA do produto low-ticket white-label do aluno antes de qualquer LP — preço de entrada (pagamento único/vitalício), ICP/persona, dor nº1, benefit stack ancorado honestamente, order bump (funcionalidade extra), upsell OTO (call de customização de maior ticket), garantia real e economia do funil. É AUTOSSUFICIENTE — o método de desenho de oferta está descrito aqui embaixo, sem depender de nenhuma skill ou projeto externo à máquina do aluno. Entrega um blueprint em Markdown e marca a etapa 'planejar' como concluída. Use quando o aluno escolher a etapa 1 no menu do /kit-lancador, ou disser: planejar meu produto, montar a oferta, blueprint da oferta, etapa 1 do lançador."
model: sonnet
effort: high
---

# /planejar-produto-lowticket — Etapa 1 (gate `planejar`)

Esta skill desenha a **estratégia e a oferta** do produto low-ticket white-label do aluno — o
passo que vem **antes** de qualquer landing page. Ela não constrói página nenhuma: produz um
**blueprint da oferta** (preço, ICP, dor, benefit stack, order bump, upsell, garantia, economia do
funil) que as etapas seguintes (LP, checkout, funil, entrega) vão ler.

> **Autossuficiente (importante).** Este repositório é **público** e roda na máquina do aluno. A
> skill **NÃO** depende de nenhuma skill-fonte, projeto ou template externo — o método completo de
> desenho de oferta está descrito aqui embaixo. (Se você for o instrutor e tiver skills internas
> equivalentes instaladas, pode reusá-las pra acelerar — mas isso é opcional; o caminho padrão
> segue o método embutido nesta skill.)

## Pré-condição

Primeiro gate do fluxo — não depende de nenhum anterior. Ainda assim, checar estado:

```bash
python3 ~/.claude/skills/kit-lancador/estado.py can planejar   # deve dar exit 0
python3 ~/.claude/skills/kit-lancador/estado.py start planejar
```

## Passo 1 — Carregar a marca do aluno (ask-vs-crash)

```bash
cat ~/.operacao-ia/config/marca.json
```

Usar `marca`, `nicho`, `persona`, `produto`, `preco_principal`, `order_bump`, `upsell`, `tom`,
`cta` como ponto de partida (o aluno pode ajustar qualquer campo nesta etapa).

**Se o arquivo não existir, NÃO travar/crashar.** Parar aqui e orientar o aluno: "Você ainda não
tem uma marca configurada — me diga o nome do seu produto/marca, o nicho, a persona do cliente
final e o tom de voz que eu monto o `~/.operacao-ia/config/marca.json` com você." Só seguir depois
que o arquivo existir (mesmo que mínimo).

## 🚨 Régua anti-reembolso — vale para toda a etapa

Em produto low-ticket a métrica que importa **não é conversão bruta**, é **conversão × (1 −
reembolso)**. Uma oferta que promete demais converte no clique e devolve no cartão — e ainda queima
a reputação do checkout. É mais barato corrigir isso na oferta do que depois na LP.

1. **NUNCA prometer renda/faturamento garantido.** A promessa é de **CAPACIDADE**: "saia com X
   pronto pra usar", "seu cliente final passa a ter Y". Nunca "você vai faturar R$Y".
2. **Valores de mercado ≠ promessa ao comprador.** "Esse tipo de serviço custa R$1k–5k no mercado"
   ✅ (ancoragem contextual). "Você vai faturar R$15.000 com isso" ❌ (promessa de resultado).
3. **Ancoragem de valor HONESTA.** Cada item do benefit stack tem um valor real defensável — o que
   custaria se comprado avulso ou no mercado. Se não dá pra justificar o valor de um item, baixe o
   número ou tire o item.
4. **Urgência só AUTÊNTICA.** Lote que sobe de verdade em data fixa, bônus que sai mesmo, vagas que
   existem de verdade. Nunca countdown que reseta a cada visita nem escassez fabricada.
5. **Filtro de comprador é parte da oferta.** Definir "pra quem é / pra quem NÃO é" no blueprint —
   é a maior alavanca anti-reembolso, porque evita a venda errada antes dela acontecer.
6. **Garantia real, nunca decorativa.** Cobre satisfação, não é desculpa pra prometer demais.

## Passo 2 — Discovery da oferta

Levantar com o aluno (pular o que a marca já resolve; perguntar só o que falta):

| Campo | Pergunta | Por que importa |
|-------|----------|------------------|
| Produto | O que o mini-app/produto entrega pro cliente final do aluno? | Define o que entra no stack |
| **Preço de entrada** | Quanto vai custar — pagamento único, acesso vitalício? | Ancora todo o resto (faixa típica R$9–97) |
| ICP / persona | Quem é o comprador ideal do aluno? (perfil, momento) | Direciona dor e linguagem |
| Dor nº1 | Qual a dor mais aguda que esse comprador sente HOJE? | Vira o ângulo da headline da LP |
| Transformação real | O que ele consegue FAZER depois? (capacidade, não renda) | Vira a promessa honesta |
| Fonte de tráfego | Pago frio / orgânico / lista / grupo? | Pago frio → oferta tem que ser auto-explicativa |
| Checkout | Pagar.me (padrão do Kit) — suporta bump + upsell one-click | Confirma que a estrutura abaixo é aplicável |
| Produto maior | Existe uma versão mais robusta / customizada por trás? | Alimenta o upsell OTO |

Este Kit trabalha sempre na faixa **tripwire low-ticket** (entrada barata, pagamento único,
monetização imediata via order bump + upsell). Confirmar com o aluno **produto + preço + ICP + dor
+ transformação + tráfego + produto maior** antes de avançar — sem isso fechado, não montar o
resto.

## Passo 3 — Critérios da oferta (validar antes de montar o stack)

Um bom produto de entrada passa nos 5 critérios abaixo. Marcar ✅/❌ com o aluno; se algum falhar,
ajustar a oferta antes de seguir:

| # | Critério | Pergunta de validação |
|---|----------|------------------------|
| 1 | Resolve 1 problema rápido | Entrega UMA vitória clara e específica (não "tudo sobre X")? |
| 2 | Valor percebido ≫ preço | O comprador sente que levou muito mais do que pagou? |
| 3 | Entrega digital | Acesso imediato, sem fricção de entrega física? |
| 4 | Complementa o produto maior | É um "gostinho" que faz desejar o próximo passo (a call de customização)? |
| 5 | Fácil dizer sim | Nesse preço a decisão é por impulso, sem precisar pensar muito? |

## Passo 4 — Benefit stack ancorado (valor honesto somando → preço)

Montar o que o comprador recebe, com **valor real defensável** por item. A soma cria a âncora; o
preço de hoje vira "pechincha racional".

```
O que você recebe:

✅ [Item core — o mini-app / funcionalidade principal] .......... Valor: R$X
✅ [Bônus 1 — complementa o core] ................................ Valor: R$X
✅ [Bônus 2 — remove um obstáculo de uso] ........................ Valor: R$X
─────────────────────────────────────────────
Valor total: R$N   •   Hoje: R$[preço de entrada]
```

Regras:
- **3 a 5 itens** — mais que isso dilui. 1 core forte + 2-4 bônus que removem objeções.
- Cada bônus deve **matar uma objeção** ("não vou saber usar" → bônus "guia rápido de uso").
- Valor total **crível** — uma âncora absurda gera desconfiança e reembolso. Mire numa proporção
  honesta (ex.: vale ~R$150–300, hoje R$37).
- Cada valor precisa ter resposta pronta pra "por que vale R$X?".

## Passo 5 — Order bump + upsell OTO + economia do funil

### Order bump (funcionalidade extra, mostrada no checkout)
- **Complementa** o produto de entrada (não compete, não confunde).
- **Barato** em relação à entrada (faixa +R$17 a +R$47 sobre uma entrada de R$37).
- **No-brainer**: é a funcionalidade extra óbvia pra quem acabou de comprar o core.

```
✅ ADICIONE ISTO: [funcionalidade extra] (só +R$[X])
A maioria adiciona — [benefício em 1 frase].
```

### Upsell OTO (call de customização, one-click pós-compra)
Oferta mostrada **depois** da compra confirmada:
1. Parabéns (reforça a boa decisão).
2. "Espere — seu pedido ainda não está completo" (interrupção de padrão).
3. Apresenta o upsell: uma **call de customização/orientação estratégica** com o aluno (o produto
   maior por trás do tripwire) — framing de próximo nível natural.
4. Botão one-click de compra.
5. Link "Não, obrigado" sempre visível (nunca esconder a recusa).

Faixa típica do upsell: R$97–R$497 (a call de customização), com downsell opcional mais leve se
recusar.

### Economia do funil (provar que o funil se paga)
Modelar com os números que o aluno tiver (ou uma estimativa conservadora explícita):

```
EXEMPLO (1.000 leads — ajustar às taxas reais do aluno):
1.000 leads
→  80 compram entrada R$37          = R$2.960   (8% conv.)
→  24 add order bump R$27           = R$  648   (30% take-rate)
→  12 compram upsell R$197          = R$2.364   (15% take-rate)
──────────────────────────────────────────────
Receita total                        = R$5.972
Receita por lead                     = R$5,97
```

Benchmarks de referência (alvos, não promessas):

| Métrica | Alvo |
|---------|------|
| Conversão visita/lead → entrada | > 8% |
| Take-rate order bump | > 30% |
| Take-rate upsell OTO | > 15% |

Deixar explícito no blueprint: **a meta é que a receita por lead cubra o custo de aquisição**, pra
o tráfego pago se pagar na entrada. Se a conta não fecha com os números do aluno, ajustar
oferta/bump/upsell antes de recomendar tráfego pago.

## Passo 6 — Garantia e urgência

**Garantia (reversão de risco):**
- Tipo: garantia incondicional de X dias (7 dias é o padrão de mercado em low-ticket).
- Texto honesto: "Se em 7 dias você sentir que não é pra você, devolvemos 100%, sem perguntas." —
  sem letra miúda escondida.
- Cobre satisfação, **não é desculpa pra prometer resultado financeiro**.

**Urgência (só autêntica, marcar qual mecanismo real se aplica):**
- Lote por data — preço sobe em data fixa de verdade.
- Bônus por janela — bônus extra sai mesmo após a data/quantidade.
- Vagas reais — só se houver limite verdadeiro.
- ❌ Nunca: countdown que reseta, "últimas vagas" permanente, escassez fabricada.

## Passo 7 — Montar e persistir o blueprint

Escrever o Markdown abaixo com tudo que foi decidido nos passos 1-6:

```markdown
# BLUEPRINT DE OFERTA — [Nome do produto]

## Discovery
- Produto: ...
- Preço de entrada: R$[X] (pagamento único, acesso vitalício)
- ICP / persona: ...
- Dor nº1: ...
- Transformação real (capacidade, não renda): ...
- Fonte de tráfego: ...
- Checkout: Pagar.me (bump + upsell one-click)
- Produto maior / call de customização: ...

## Conceito de headline (capacidade, sem promessa de renda)
"[Como {resultado-capacidade} sem {dor/esforço}]"
(2-3 variações pra a LP testar)

## Promessa central
O que o comprador SAI sabendo fazer / com o que pronto. (Capacidade, não renda.)

## Pra quem é / Pra quem NÃO é
- É pra: ...
- NÃO é pra: ...   ← filtro anti-reembolso

## Benefit stack ancorado
✅ [Core] — ... .......... Valor: R$X
✅ [Bônus 1] — ... ....... Valor: R$X
✅ [Bônus 2] — ... ....... Valor: R$X
Valor total: R$N  •  Hoje: R$[preço de entrada]
(cada valor com justificativa de 1 linha)

## Order bump
- Funcionalidade extra: ...
- Preço: +R$X
- Copy: "✅ ADICIONE ISTO: ... (só +R$X) — ..."

## Upsell OTO (call de customização)
- O que inclui: ...
- Preço: R$X
- Downsell (opcional): R$X

## Economia do funil
[tabela receita por lead — prova que se paga]

## Garantia
[X dias incondicional — texto honesto]

## Urgência (autêntica)
[mecanismo real — lote/data/vagas, ou "sem urgência artificial" se não houver]

## Âncora de preço
R$N (valor total) → R$[preço de entrada] hoje
```

Persistir onde as próximas etapas vão ler:

```bash
mkdir -p ~/kit-lancador-artefatos/planejar
# salvar o blueprint acima em:
# ~/kit-lancador-artefatos/planejar/blueprint-oferta.md
```

## Passo 8 — Fechar a etapa

```bash
python3 ~/.claude/skills/kit-lancador/estado.py done planejar ~/kit-lancador-artefatos/planejar/blueprint-oferta.md
```

Voltar ao menu do `/kit-lancador` e sugerir a etapa 2 (Agente Criador de Mini-Apps), que agora está
liberada — ela vai construir exatamente o produto descrito neste blueprint.

## Anti-teatro
- **Não inventar valores** pro benefit stack — cada âncora precisa de justificativa real. Número
  de fantasia = risco de reembolso.
- **Não pular o cálculo de economia do funil** — uma oferta bonita que não se paga não é oferta,
  é prejuízo.
- Confirmar discovery COMPLETO antes de montar — blueprint sobre dados incompletos gera LP errada
  nas próximas etapas.

## Régua

Maximizar conversão × (1 − reembolso). **NUNCA prometer renda.** Preço de entrada baixo, oferta
honesta, garantia real, urgência só quando for verdadeira.
