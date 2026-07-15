---
name: checkout-white-label
description: "Etapa 4 do Kit Lançador. Wrapper fino que monta o checkout Pagar.me do produto low-ticket white-label do aluno (produto principal + order bump nativo), invocando a skill-fonte /criar-checkout-pagarme. Na demo roda como STUB (sem chave/deploy) — as credenciais Pagar.me são plugadas depois via env local do aluno. Marca o gate 'checkout' como done. Bloqueia se o gate 'lp' não estiver concluído. Use quando o aluno escolher a etapa 4 no menu do /kit-lancador, ou disser: montar meu checkout, checkout pagar.me, adicionar order bump, etapa 4 do lançador."
model: sonnet
effort: medium
---

# /checkout-white-label — Etapa 4 (gate `checkout`)

Casca fina sobre **`/criar-checkout-pagarme`**. Monta a tela de checkout transparente
(produto principal + order bump como funcionalidade extra). Zero lógica de pagamento aqui.

## Pré-condição (bloqueio)

```bash
python3 ~/.claude/skills/kit-lancador/estado.py can checkout   # exit 1 se 'lp' não estiver done
python3 ~/.claude/skills/kit-lancador/estado.py start checkout
```

## Credenciais — regra dura

**Nada de chave Pagar.me no repo.** As credenciais do aluno vivem só em env local
(`~/.operacao-ia/config/pagarme.env` ou equivalente), fora do git. Se a chave não estiver
presente, **rodar em modo STUB**: gera a tela/preview do checkout sem criar cobrança real nem
fazer deploy. Comunicar ao aluno:
*"o checkout de verdade sai quando você plugar sua conta Pagar.me nas próximas aulas."*

**O valor exibido no preview vem do blueprint resolvido (etapa 1), nunca de constante.** Carregar
o blueprint ANTES de montar o preview e exibir `preco_principal` (pagamento único) + o order bump
como valor separado — assim o STUB funciona pra qualquer aluno e qualquer preço. Se o
blueprint não trouxer preço, cair no default da marca (`marca.preco_principal`); só então, na
ausência de tudo, usar um placeholder explícito marcado como exemplo.

## Passos

1. **Carregar** marca + blueprint (etapa 1) e **resolver o preço ANTES do preview**:
   `preco_principal` (pagamento único) + valor do `order_bump`. Esses valores alimentam o
   preview — nada de constante hardcoded.
2. **Invocar `/criar-checkout-pagarme`** com o produto já resolvido (principal + 1 order bump),
   passando o preço resolvido no passo 1. Em ausência de credencial → caminho STUB (preview/tela
   com o valor do blueprint), não deploy.
3. **Persistir**:
   ```bash
   mkdir -p ~/kit-lancador-artefatos/checkout
   # salvar a tela/preview em ~/kit-lancador-artefatos/checkout/ (html ou png + nota-stub.md)
   ```
4. **Fechar o gate**:
   ```bash
   python3 ~/.claude/skills/kit-lancador/estado.py done checkout ~/kit-lancador-artefatos/checkout/checkout-preview.html
   ```
5. Voltar ao menu e sugerir a etapa 5 (funil).

## Fora de escopo aqui

Conta Pagar.me / domínio / Pixel por aluno é multi-tenant real — pós-call. A demo é um stub.
