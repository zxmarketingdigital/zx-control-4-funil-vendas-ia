# 🚀 Comece aqui — Setup de Funil de Vendas com IA (Kit Lançador · ZX Control 4)

Você acabou de clonar o **Setup de Funil de Vendas com IA**: um orquestrador no seu Claude Code que
te conduz por todo o ciclo de **lançar um produto digital low-ticket white-label** — do zero à
divulgação:

**planejar produto → criar o mini-app de IA do nicho → landing page → checkout Pagar.me → funil
(order bump + upsell) → entrega (acesso ao seu mini-app) → divulgação em massa.**

Você **não precisa saber programar** nem decorar comando nenhum. Quem escreve, monta e organiza
é o Claude. Seu papel é **conduzir e aprovar**. É mais simples do que parece — me conduza que eu
te levo.

---

## Parte 1 — Preparação (só uma vez)

1. **Instale as skills no seu Claude.** Com este repositório aberto, copie a pasta `skills/`
   para o seu diretório de skills do Claude Code:

   ```bash
   mkdir -p ~/.claude/skills && cp -R skills/* ~/.claude/skills/
   ```

   (Isso instala 8 skills: o orquestrador `kit-lancador` + as 7 etapas.)

2. **Crie a sua marca.** As skills leem a sua identidade de marca de
   `~/.operacao-ia/config/marca.json` (nome, nicho, persona, cores, CTA). Se você ainda não tem
   esse arquivo, é só me dizer **"me ajuda a montar minha marca"** que eu monto com você.

   > 🔒 **Segurança:** suas credenciais (conta Pagar.me, domínio, Pixel, chaves de API) vivem
   > **só em arquivos de ambiente locais** na sua máquina (`~/.operacao-ia/config/*.env`) — elas
   > **nunca** entram neste repositório nem em git. Este repo é público; nada de segredo aqui.

---

## Parte 2 — Como usar (toda vez)

3. Com o repositório aberto, escreva pro Claude exatamente:

   > **`leia o CLAUDE.md e me conduza`**

4. O Claude carrega o **menu do Setup de Funil de Vendas com IA** — as 7 etapas numeradas,
   mostrando o que já foi feito e o que falta:

   ```
   1. Planejar produto (oferta/blueprint)
   2. Agente Criador de Mini-Apps (constrói o app do seu nicho do zero)
   3. Landing page
   4. Checkout Pagar.me
   5. Funil (order bump + upsell + copy)
   6. Entrega (provisionar acesso ao seu mini-app)
   7. Divulgação (email + posts + carrossel)

   S. Status   ·   C. Continuar de onde parei   ·   R. Refazer uma etapa
   ```

5. **Digite o número da etapa** (ou `INICIAR` pra começar do 1). O Claude executa aquela etapa,
   te mostra o resultado, e salva tudo. Você aprova e segue pra próxima.

6. **Pode parar quando quiser.** Da próxima vez, é só abrir e escrever **`C`** (ou "continua de
   onde parei") — o Claude retoma exatamente no ponto certo. O progresso fica guardado em
   `~/.kit-lancador/estado.json`, controlado pelo `estado.py` da **skill já instalada**
   (`~/.claude/skills/kit-lancador/estado.py`) — não pela cópia dentro deste repo. Por isso o
   Kit funciona de qualquer pasta, mesmo com este repositório fechado.

---

## Como funciona por dentro (pra você entender, não pra decorar)

- Cada etapa é uma skill que **chama uma ferramenta já pronta e testada** da ZX LAB — você não
  reinventa nada.
- As etapas têm **ordem**: a etapa 2 (criar o mini-app) só libera depois da 1 (planejar); a 3 (LP)
  só depois da 2; e assim por diante. Isso te protege de montar a página de vendas sem o produto
  pronto, ou o checkout sem oferta definida.
- Todos os artefatos que você gerar (blueprint, LP, checkout, copy, email de boas-vindas, posts,
  carrossel) ficam salvos em `~/kit-lancador-artefatos/`, organizados por etapa.

---

## Regras de ouro

- ✅ **Dúvida? Pergunte antes.** Se não souber o que responder numa etapa, me pergunte "o que é
  isso?" — não deixe o Claude adivinhar.
- ✅ **Uma etapa de cada vez.** O menu te guia; siga a ordem.
- 🔒 **Nunca coloque senha, chave ou token no código ou no repositório.** Credenciais só em
  `~/.operacao-ia/config/*.env` (local, fora do git).
- 🧪 **Nada é disparado sem você confirmar.** Email e WhatsApp de divulgação rodam em modo de
  teste (dry-run) até você dar o OK explícito.

Qualquer travada, é só me chamar aqui no chat. Bora lançar. 🚀
