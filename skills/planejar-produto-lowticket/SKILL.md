---
name: planejar-produto-lowticket
description: "Etapa 1 do Kit Lançador. Wrapper fino que planeja a OFERTA do produto low-ticket white-label do aluno antes de qualquer LP — preço de entrada, ICP, dor nº1, benefit stack ancorado, order bump, upsell OTO e garantia — invocando a skill-fonte /oferta-low-ticket com a marca do aluno já resolvida. Entrega um blueprint em Markdown e marca o gate 'planejar' como done. Use quando o aluno escolher a etapa 1 no menu do /kit-lancador, ou disser: planejar meu produto, montar a oferta, blueprint da oferta, etapa 1 do lançador."
model: sonnet
effort: high
---

# /planejar-produto-lowticket — Etapa 1 (gate `planejar`)

Casca fina sobre **`/oferta-low-ticket`**. Zero lógica de oferta aqui — só resolve o input a
partir da marca do aluno, delega, persiste o artefato e fecha o gate.

## Pré-condição

Primeiro gate do fluxo — não depende de nenhum anterior. Ainda assim, checar estado:

```bash
python3 ~/.claude/skills/kit-lancador/estado.py can planejar   # deve dar exit 0
python3 ~/.claude/skills/kit-lancador/estado.py start planejar
```

## Passos

1. **Carregar a marca** (white-label):
   ```bash
   cat ~/.operacao-ia/config/marca.json
   ```
   Usar `marca`, `nicho`, `persona`, `produto`, `preco_principal`, `order_bump`, `upsell`,
   `tom`, `cta`. Se faltar `marca.json`, parar e orientar o aluno a criá-la.

2. **Invocar a skill-fonte `/oferta-low-ticket`** passando o input já resolvido (caminho
   feliz, não-interativo) — produto de entrada com pagamento único / acesso vitalício,
   order bump como funcionalidade extra, upsell OTO de maior ticket (call de customização).
   Deixar a fonte gerar o blueprint completo (benefit stack, ancoragem honesta, garantia,
   economia do funil). **Não reescrever o que a fonte produz.**

3. **Persistir o artefato** onde o aluno vai encontrar:
   ```bash
   mkdir -p ~/kit-lancador-artefatos/planejar
   # salvar o blueprint gerado em:
   # ~/kit-lancador-artefatos/planejar/blueprint-oferta.md
   ```

4. **Fechar o gate**:
   ```bash
   python3 ~/.claude/skills/kit-lancador/estado.py done planejar ~/kit-lancador-artefatos/planejar/blueprint-oferta.md
   ```

5. Voltar ao menu do `/kit-lancador` e sugerir a etapa 2 (criar o mini-app), que agora está liberada.

## Régua

Maximizar conversão × (1 − reembolso). **NUNCA prometer renda.** Preço de entrada baixo,
oferta honesta, garantia real. É a régua da skill-fonte — só reforçar, não relaxar.
