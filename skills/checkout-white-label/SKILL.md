---
name: checkout-white-label
description: "Etapa 4 do Kit Lançador. Constrói o checkout transparente Pagar.me do produto low-ticket white-label do aluno (produto principal + order bump nativo) — preço sempre resolvido a partir do blueprint da etapa 1, nunca hardcoded, nunca aceito do browser. É AUTOSSUFICIENTE: a anatomia do checkout (layout, regra de preço server-side, scaffold de backend) está toda embutida aqui, sem depender de template ou projeto externo. Sem credencial Pagar.me, roda em modo STUB/preview; a credencial e o deploy real do aluno acontecem pós-call, na Etapa 6 (Entrega). Bloqueia se o gate 'lp' não estiver concluído e marca o gate 'checkout' como done. Use quando o aluno escolher a etapa 4 no menu do /kit-lancador, ou disser: montar meu checkout, checkout pagar.me, adicionar order bump, etapa 4 do lançador."
model: sonnet
effort: medium
---

# /checkout-white-label — Etapa 4 (gate `checkout`)

Constrói a tela de checkout transparente do produto do aluno (produto principal + order bump
como funcionalidade extra) e o scaffold do backend que vai processar o pagamento de verdade
quando ele plugar a própria conta Pagar.me.

> **Autossuficiente (importante).** Este repositório é **público** e roda na máquina do aluno. A
> skill **NÃO** depende de nenhum projeto, casca ou template externo à máquina dele — a anatomia
> completa do checkout está descrita aqui embaixo e é o que o Claude usa pra montá-lo. (Se você
> for o instrutor e tiver skills internas de checkout instaladas, pode reusá-las pra acelerar —
> mas isso é opcional; o caminho padrão constrói tudo a partir desta anatomia.)

## Pré-condição (bloqueio)

```bash
python3 ~/.claude/skills/kit-lancador/estado.py can checkout   # exit 1 se 'lp' não estiver done
python3 ~/.claude/skills/kit-lancador/estado.py start checkout
```
Se bloqueado, avisar que a **Etapa 3 (Landing page)** precisa terminar primeiro (o checkout
anuncia o mesmo produto que a LP já vendeu) e voltar ao menu.

## Passo 1 — Carregar marca + blueprint (nada hardcoded)

```bash
cat ~/.operacao-ia/config/marca.json
cat "$(python3 ~/.claude/skills/kit-lancador/estado.py gate planejar | python3 -c 'import json,sys;print(json.load(sys.stdin).get("artifact",""))')"
cat ~/kit-lancador-artefatos/miniapp/manifest.json 2>/dev/null   # se já existir, dá o nome/slug exato do produto
```

- **Se `marca.json` não existir:** parar aqui e orientar o aluno a criá-la (não seguir com valor
  inventado).
- **Resolver o preço ANTES de montar o preview:**
  1. Localizar no blueprint a seção de **preço de entrada** e a seção **Order bump** — são texto
     livre tipo `"R$97 (pagamento único, acesso vitalício)"`; extrair o valor numérico (`97.00`)
     e guardar a descrição por extenso pra exibir ao lado do preço.
  2. Se o blueprint não trouxer preço, cair no default de `marca.preco_principal` /
     `marca.order_bump` (mesmo arquivo `marca.json`, mesmo formato de texto).
  3. Só na ausência de tudo, usar um placeholder explícito e visivelmente marcado como exemplo
     (ex.: `R$97 (exemplo — ajuste o preço na etapa 1)`), nunca uma constante muda no código.
  4. Se o valor extraído for ambíguo (dois números, faixa, "a combinar"), **perguntar ao aluno**
     o valor exato antes de seguir — não chutar.
- Usar o nome do produto do `manifest.json` (se existir) — senão `marca.produto` — pra manter o
  checkout anunciando **exatamente o que a LP e o mini-app já mostraram**.

## Passo 2 — Credenciais (regra dura)

**Nada de chave Pagar.me no repositório.** Credencial vive só em arquivo de ambiente **local**,
fora do git (ex.: `~/.operacao-ia/config/pagarme.env`) — `pk_test`/`sk_test` pra teste,
`pk_`/`sk_` pra produção (sem `_live_`).

- **Se não houver credencial no ambiente local** (caso normal nesta etapa): seguir em **modo
  STUB** — gera o preview completo (visual + scaffold de backend) sem criar cobrança real nem
  fazer deploy. Comunicar ao aluno: *"o checkout de verdade sai quando você plugar sua conta
  Pagar.me — isso acontece na Entrega (Etapa 6)."*
- **Se o aluno quiser plugar a credencial agora:** perguntar (AskUserQuestion) e, se ele
  confirmar, pedir a chave na hora e salvar **só** no arquivo de ambiente local — nunca em
  arquivo versionado, nunca ecoado de volta no chat/log.
- **Mesmo com credencial disponível, o deploy real (domínio próprio, Pixel, webhook de
  confirmação) continua sendo trabalho da Etapa 6.** Aqui o objetivo é construir e validar o
  preview localmente — igual ao mini-app da Etapa 2.
- Qualquer disparo de email/WhatsApp de confirmação que o preview eventualmente simule roda em
  **dry-run até o aluno dar OK explícito** — nunca envia de verdade nesta etapa.

## Passo 3 — Anatomia do checkout (o padrão a montar — EMBUTIDO)

```
LP do aluno  →  checkout-preview.html (esta etapa)  →  functions/api/checkout.js (scaffold)
                                                              ↓
                                                    Pagar.me v5 (Pix + Cartão)
                                                     — só quando deployado de verdade —
```

Construir em `~/kit-lancador-artefatos/checkout/`:

```
checkout/
  checkout-preview.html      # HTML+CSS+JS autocontido, abre local sem servidor nenhum
  functions/api/checkout.js  # scaffold da Pages Function que vai processar o pagamento real
  nota-stub.md                # o que falta pra ir ao ar (credencial, domínio, webhook)
```

**`checkout-preview.html`** — mobile-first, seções na ordem:
1. **Barra de urgência** (timer visual — mensagem, não precisa contar de verdade no STUB).
2. **Bloco do produto** — imagem (placeholder se não houver), nome, autor/marca, preço de/por
   vindo do Passo 1, a promessa (H1) do blueprint.
3. **Dados do cliente** — nome, e-mail, CPF (máscara), telefone.
4. **Abas de pagamento** — **Pix** (default) | **Cartão**.
5. **Order bump** — checkbox com nome/descrição/preço do bump (Passo 1); ao marcar, soma ao
   total no resumo. É a "funcionalidade extra" do produto do aluno, não um segundo produto.
6. **Resumo dinâmico** — recalcula ao vivo (JS no próprio HTML) conforme bump marcado/desmarcado.
7. **Botão de finalizar** — cor sólida da marca do aluno (âmbar/o que estiver em `marca.json`),
   **chapado, sem gradiente/glow/animação pulsante**.
8. **Ícones de confiança** (SVG simples: pagamento seguro, dados protegidos, etc).
9. **Rodapé** com identificação do vendedor.

No modo STUB, um banner fixo no topo diz **"MODO DEMONSTRAÇÃO"** e o botão de finalizar, ao
clicar, mostra uma mensagem explicando que o checkout real entra na Entrega — **não simula uma
cobrança bem-sucedida** (evita o aluno achar que já está vendendo).

**`functions/api/checkout.js`** — scaffold pronto pra virar uma Cloudflare Pages Function (ou
equivalente) no dia do deploy real:
- Define um `PRODUCT_CATALOG` no próprio arquivo (constante server-side) com os mesmos valores
  resolvidos no Passo 1 — produto principal + order bump, cada um com um `code` (SKU) e o preço
  em centavos.
- O handler recebe do front **apenas quais itens foram selecionados** (ids/booleans do bump) e
  os dados do cliente — **nunca um campo de preço**. O total é sempre recalculado a partir do
  `PRODUCT_CATALOG`, nunca aceito do corpo da requisição.
- Comentário `// TODO` nos pontos onde entram `PAGARME_SECRET_KEY` (lida de variável de
  ambiente/secret do provedor de deploy, nunca literal no arquivo) e a chamada
  `POST https://api.pagar.me/core/v5/orders` (`items[]` por SKU, `customer{}`, `payments[]` —
  cartão via token gerado no frontend com a chave pública, ou Pix).

**`nota-stub.md`** — lista objetivamente o que falta pra produção: conta Pagar.me do aluno,
domínio próprio (opcional), webhook de confirmação de pagamento, tokenização de cartão no
frontend (o número do cartão nunca deve trafegar pelo backend em produção).

## Passo 4 — Regra de preço server-side (dura, não relaxar)

O preço que aparece no preview é só **exibição**. A regra que protege o aluno de fraude/erro é:
**o total nunca é aceito do que o browser manda** — o `functions/api/checkout.js` (mesmo em
scaffold) sempre recalcula a partir do `PRODUCT_CATALOG` embutido no próprio backend, indexado
por SKU. Isso vale mesmo no STUB: é o padrão que já fica pronto pra quando o aluno conectar a
credencial de verdade. Nenhum preço deve existir como constante solta no HTML sem vir do Passo 1.

## Passo 5 — DoD (só considerar pronto quando)

Rodar `python3 -m http.server` na pasta `~/kit-lancador-artefatos/checkout/`, abrir
`http://localhost:8000/checkout-preview.html` no browser e conferir visualmente: preço correto
(do blueprint), order bump ativa/desativa o resumo, botão chapado com a cor da marca. Só marcar
`done` depois de ver renderizando — "pronto" = visto funcionando, não arquivo criado.

- [ ] `checkout-preview.html` abre local, sem nenhuma credencial, e mostra o preço **resolvido
      do blueprint** (não hardcoded, não placeholder genérico se o blueprint já tinha valor).
- [ ] Order bump ativa/desativa e o resumo recalcula ao vivo.
- [ ] Nenhuma chave/segredo aparece em texto no HTML ou no `checkout.js` gerado.
- [ ] `functions/api/checkout.js` só lê o preço do `PRODUCT_CATALOG` — nunca de um campo enviado
      pelo cliente.
- [ ] `nota-stub.md` explica com clareza o que falta pra ir ao ar.
- [ ] Botão de finalizar é chapado (sem gradiente/glow) e usa a cor da marca do aluno.
- [ ] Nenhum CTA da LP ainda aponta pra `#checkout-pendente` — a LP foi religada ao checkout
      desta etapa.

## Passo 6 — Religar a LP ao checkout

Ler `~/kit-lancador-artefatos/lp/index.html` se o arquivo existir. Se ainda não existir, avisar
que a **Etapa 3 (LP)** precisa rodar antes e seguir sem travar esta etapa.

Se existir, substituir **toda** ocorrência de `href="#checkout-pendente"` e
`data-checkout="pendente"` pelo caminho do checkout gerado aqui e regravar o mesmo
`~/kit-lancador-artefatos/lp/index.html`: no modo STUB, usar
`../checkout/checkout-preview.html`; quando houver URL real de deploy na Etapa 6, usar essa URL
real nos dois atributos.

## Passo 7 — Persistir + fechar o gate

```bash
mkdir -p ~/kit-lancador-artefatos/checkout ~/kit-lancador-artefatos/checkout/functions/api
# gravar:
#   ~/kit-lancador-artefatos/checkout/checkout-preview.html
#   ~/kit-lancador-artefatos/checkout/functions/api/checkout.js
#   ~/kit-lancador-artefatos/checkout/nota-stub.md
python3 ~/.claude/skills/kit-lancador/estado.py done checkout ~/kit-lancador-artefatos/checkout/checkout-preview.html
```
Voltar ao menu do `/kit-lancador` e sugerir a **Etapa 5 (Funil)**, que agora libera.

## Fora de escopo aqui

Conta Pagar.me própria, domínio custom, Pixel/CAPI, webhook de confirmação de pagamento e
liberação automática de acesso são trabalho **multi-tenant real, pós-call** — acontecem na
**Etapa 6 (Entrega)**, quando o aluno pluga as credenciais dele. Esta etapa entrega o preview
validado + o scaffold de backend pronto pra receber a credencial, não um checkout no ar.

## Régua

Maximizar conversão × (1 − reembolso). **Nunca prometer renda.** Oferta honesta, garantia real —
o checkout só expõe o que a oferta da etapa 1 já definiu, não infla nem esconde condições.
