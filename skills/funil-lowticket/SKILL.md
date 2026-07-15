---
name: funil-lowticket
description: "Etapa 5 do Kit Lançador. Wrapper fino que monta o funil de conversão do produto low-ticket white-label do aluno — order bump, upsell OTO e recuperação de compra — invocando as skills-fonte /configurar-upsell-produto (estrutura da oferta de upsell) e /copy-funil-low-ticket (copy que converte: email + WhatsApp, refund-safe). Entrega a copy do funil e marca o gate 'funil' como done. Bloqueia se o gate 'checkout' não estiver concluído. Use quando o aluno escolher a etapa 5 no menu do /kit-lancador, ou disser: montar o funil, configurar upsell, copy do order bump, etapa 5 do lançador."
model: sonnet
effort: high
---

# /funil-lowticket — Etapa 5 (gate `funil`)

Casca fina sobre **duas** fontes: `/configurar-upsell-produto` (planeja/estrutura o upsell) e
`/copy-funil-low-ticket` (Bloco B — copy de upsell multicanal + recuperação, refund-safe).
Zero copy escrita à mão aqui.

## Pré-condição (bloqueio)

```bash
python3 ~/.claude/skills/kit-lancador/estado.py can funil      # exit 1 se 'checkout' não estiver done
python3 ~/.claude/skills/kit-lancador/estado.py start funil
```

## Passos

1. **Carregar** marca + blueprint (etapa 1) — o upsell OTO já foi ancorado lá (call de
   customização de maior ticket) e o order bump também.
2. **Invocar `/configurar-upsell-produto` (Fase 0 — planejamento)** pra validar/estruturar a
   oferta de upsell (faz sentido? preço, ângulo, garantia, economia do funil). Na demo, só a
   parte de planejamento + copy — **sem** deploy de LP nem ativar disparo real.
3. **Invocar `/copy-funil-low-ticket` (Bloco B)** pra gerar a copy pronta:
   - order bump (+funcionalidades extras),
   - upsell OTO (call R$497),
   - recuperação de compra / checkout abandonado (email + WhatsApp anti-ban).
   Deixar a fonte escrever. **Não reescrever.**
4. **Persistir**:
   ```bash
   mkdir -p ~/kit-lancador-artefatos/funil
   # salvar a copy consolidada em ~/kit-lancador-artefatos/funil/copy-funil.md
   ```
5. **Fechar o gate**:
   ```bash
   python3 ~/.claude/skills/kit-lancador/estado.py done funil ~/kit-lancador-artefatos/funil/copy-funil.md
   ```
6. Voltar ao menu e sugerir a etapa 6 (entrega).

## Fora de escopo aqui

Ativar o disparo real (cron/dispatcher) do aluno — pós-call. Aqui só se gera a copy e a
estrutura do funil.
