---
name: divulgar-lowticket
description: "Etapa 7 (final) do Setup de Funil de Vendas com IA. Produz, do ZERO e de forma AUTOSSUFICIENTE (sem invocar nenhuma skill externa), o pacote de divulgação em massa do produto low-ticket white-label do aluno: copy do EMAIL de lançamento (assunto+corpo+oferta+preço+CTA+garantia, voz da marca, sem promessa de renda) salva em .md e .html; copy de POST social (legenda+hashtags+CTA por plataforma); e CARROSSEL de lançamento (PNGs 1080x1350) na paleta da marca do aluno. O disparo de email/WhatsApp roda SEMPRE em modo teste (dry-run) até o aluno confirmar explicitamente. Marca a etapa 'divulgar' como concluída e fecha o ciclo. Bloqueia se a etapa 'entrega' não estiver concluída. Use quando o aluno escolher a etapa 7 no menu do /kit-lancador, ou disser: divulgar meu produto, gerar posts, montar carrossel, email de lançamento, etapa 7 do lançador."
model: sonnet
effort: medium
---

# /divulgar-lowticket — Etapa 7 (gate `divulgar`)

Fecha o ciclo do Setup de Funil de Vendas com IA: monta o pacote completo de divulgação em massa
do produto do aluno — email de lançamento, copy de post social e carrossel — **e nunca dispara
nada de verdade sem confirmação**.

> **Autossuficiente (importante).** Este repositório é **público** e roda na máquina do aluno. A
> skill **NÃO** depende de nenhum serviço/skill externo à máquina dele — nem gerador de imagem
> pago, nem provedor de email específico, nem MCP de terceiro. O método completo (como escrever o
> email, como estruturar o post, como desenhar o carrossel) está descrito aqui embaixo e é o que
> o Claude usa pra produzir os três artefatos. (Se você for o instrutor e tiver ferramentas
> internas de geração de copy/imagem instaladas, pode reusá-las pra acelerar — mas isso é
> opcional; o caminho padrão produz tudo a partir do método embutido nesta skill.)

## Pré-condição (bloqueio)

```bash
python3 ~/.claude/skills/kit-lancador/estado.py can divulgar    # exit 1 se 'entrega' não estiver done
python3 ~/.claude/skills/kit-lancador/estado.py start divulgar
```
Se bloqueado, avisar que a **Etapa 6 (Entrega)** precisa terminar primeiro — divulgar um produto
que o cliente ainda não recebe é vender fumaça — e voltar ao menu.

## Passo 1 — Carregar contexto (nada hardcoded)

```bash
cat ~/.operacao-ia/config/marca.json                              # nome, nicho, persona, tom, cores, cta
cat "$(python3 ~/.claude/skills/kit-lancador/estado.py gate planejar | python3 -c 'import json,sys;print(json.load(sys.stdin).get("artifact",""))')" # oferta, preço, order bump, upsell, garantia
cat ~/kit-lancador-artefatos/miniapp/manifest.json                 # produto real: agentes, entidades, preço
```
Se `marca.json` não existir, **parar** e orientar o aluno: *"Antes de divulgar, preciso da sua
marca — me diga nome, nicho, persona, tom de voz, cor da marca (hex), logo e o CTA principal, ou
rode a Etapa 1 se ainda não montou."* Nunca inventar marca nem seguir sem ela.

**Cor e logo antes de gerar qualquer peça visual (email em HTML e carrossel):**
```bash
python3 ~/.claude/skills/kit-lancador/marca.py resolve     # exit 1 = falta nome ou cor da marca; imprime acento, texto_sobre_acento, logo e avisos
```
exit 1 → PERGUNTAR ao aluno a cor da marca (hex) e o nome e gravar com
`marca.py set --json -` com `{"nome": "...", "acento": "#HEX"}` no stdin (heredoc `<<'JSON'`) (**nunca** colar o texto do aluno numa linha de shell com aspas: `$(...)` e crases executariam; usar `--json -` com heredoc de delimitador entre aspas, que não expande nada); se ele não quiser informar a cor, rodar
`python3 ~/.claude/skills/kit-lancador/marca.py set --usar-padrao-zx` (grava o âmbar **e imprime o aviso**) e repetir o aviso ao aluno.
Logo ainda não perguntado (`python3 ~/.claude/skills/kit-lancador/marca.py check` → `"logo": "nao_perguntado"`): perguntar uma vez e gravar
com `marca.py set --json -` com `{"logo": "<caminho|https|nenhum>"}` no stdin (heredoc `<<'JSON'`). Sem logo, os materiais levam só o nome da marca em
texto — nunca o logo ou o nome da ZX.

Usar sempre o **preço e os agentes reais do manifesto** (nunca reaproveitar contagem/preço de
outro produto ou de exemplo). Isso vale para os três artefatos abaixo.

## Passo 2 — Email de lançamento (escrito aqui, na voz da marca)

Redigir o email **do zero**, a partir de `marca.json` + blueprint. Estrutura:

1. **Assunto** — gancho de curiosidade ou benefício direto, até ~60 caracteres. Gerar 2 variantes
   e deixar o aluno escolher (ex.: "Seu {nicho} agora com IA" vs "Abri o acesso — {promessa}").
2. **Abertura** — nomeia a dor nº1 do ICP (do blueprint), em 1-2 frases, tom = `marca.tom`.
3. **Apresentação da solução** — o mini-app real (nome + o que ele faz), citando os agentes do
   `manifest.json` — nunca prometer features que o produto não tem.
4. **Benefit stack** — 3-5 bullets do "o que você recebe" (ancorados no blueprint, não inventados).
5. **Oferta** — preço principal, order bump (se houver) e o que cada um destrava.
6. **Prova/garantia** — a garantia real definida no blueprint (nunca inventar prazo ou condição).
7. **CTA** — botão/link único e claro, o `cta` de `marca.json`.
8. **PS** — reforço de urgência **honesto** (ex.: vaga/cohort, não escassez falsa).

**Regra dura de conteúdo:** nunca prometer renda ("ganhe R$X/mês"), nunca inflar resultado do
cliente final, nunca esconder o preço. Oferta honesta = régua da casa.

Salvar **os dois formatos**:
```bash
mkdir -p ~/kit-lancador-artefatos/divulgar
# ~/kit-lancador-artefatos/divulgar/email-lancamento.md    → revisão do aluno (texto puro)
# ~/kit-lancador-artefatos/divulgar/email-lancamento.html  → HTML pronto pra disparo (Passo 5)
```
O `.html` é um template simples e responsivo (largura ~600px, fontes do sistema, cores do
`resolve`, botão de CTA sólido — sem gradiente/glow), com o texto do `.md` já formatado. Botão:
fundo `resolve.acento` e texto `resolve.texto_sobre_acento` (contraste legível mesmo com cor
clara). **Todo valor dinâmico (nome da marca, nome do destinatário, assunto, links) entra no HTML escapado** (`html.escape(valor, quote=True)`; `&`, `<`, `>`, aspas viram entidades); links (CTA, logo) só aceitos se começarem com `https://` — `javascript:`, `data:` e afins são recusados antes de entrar em `href`/`src` — nunca interpolar texto cru em atributo ou corpo. Topo do email: logo do aluno só se for **link https** (`<img src="<resolve.logo.html_src>" alt="<nome da marca>"
height="40">`); logo local não funciona em email (clientes bloqueiam imagem `data:` e arquivo local) — nesse
caso usar o nome da marca em texto e avisar o aluno que, para ter o logo no email, ele precisa hospedá-lo
e gravar o link com `marca.py set --json -` (campo `logo`, como nas outras etapas). Sem logo, o nome da marca em texto.

## Passo 3 — Copy de post social (legenda + hashtags + CTA)

Perguntar ao aluno a(s) **plataforma(s)** (default: Instagram, se ele não tiver preferência).
Regras por plataforma (aplicar a que for escolhida):

| Plataforma | Estrutura | Comprimento | Hashtags |
|---|---|---|---|
| **Instagram** (reel/feed) | Hook (1ª linha) + corpo (3-5 linhas) + CTA + hashtags | 150-300 caracteres no corpo | 8-12, nicho + amplas, ao final |
| **TikTok** | Hook curtíssimo + punchline + hashtags | até 150 caracteres no total | 4-6, focadas em nicho |
| **LinkedIn** | Hook + insight/framework + CTA | 800-1200 caracteres | 3-5, tom B2B |
| **WhatsApp Status/Grupo** | Texto curto + CTA + link | até 3 linhas | nenhuma |

- Tema = o mini-app + a promessa do blueprint (nunca gancho genérico desconectado do produto).
- CTA = leva ao checkout/LP da Etapa 3/4 (não "compra agora" agressivo sem contexto — isso é
  copy de tráfego pago, fora do escopo desta etapa).
- Escrever **2 variantes** — A (direta) e B (storytelling curto) — mostrar as duas e perguntar ao
  aluno qual usar (ou pedir uma 3ª).
- Máximo 3 emojis por post. Nunca usar hashtags genéricas demais (`#love #life`) — diluem alcance.

Salvar em:
```
~/kit-lancador-artefatos/divulgar/post-social-<plataforma>.md
```
com o formato:
```
PLATAFORMA: {plataforma}
TEMA: {produto do manifesto}
CRIADO: {timestamp ISO}

--- COPY (variante escolhida) ---
{copy}

--- HASHTAGS ---
{hashtags}
```

## Passo 4 — Carrossel de lançamento (PNGs 1080×1350, montado localmente)

Sem gerador de imagem por IA nem credencial nenhuma — o carrossel é **tipográfico**, desenhado
com a paleta da marca (`marca.json.cores`), no mesmo espírito de carrossel educativo que domina o
Instagram de criadores/infoprodutos.

### 4.1 — Escrever a copy de cada slide ANTES de desenhar

5 a 10 slides (default 7), máximo **50 palavras por slide**:
- **Slide 1 (Capa)** — hook + nome da marca (o script já coloca logo ou nome no topo de todos
  os slides; SVG não é lido pelo Pillow, então com logo em SVG o nome em texto é usado).
- **Slide 2 (Problema)** — a dor nº1 do blueprint, em 1-2 frases que o leitor reconhece.
- **Slides 3 a N-1 (Conteúdo)** — pontos numerados do benefit stack / como o mini-app resolve.
- **Slide N (CTA)** — "Salvou? Manda pra quem precisa. Link nos comentários/bio" + `marca.cta`.

Mostrar os textos ao aluno e pedir aprovação antes de desenhar.

### 4.2 — Desenhar os PNGs (script embutido — Pillow, sem serviço externo)

Verificar/instalar dependência local (sem credencial, é só uma lib):
```bash
python3 -c "import PIL" 2>/dev/null || python3 -m pip install --user --quiet pillow
```

Se a instalação falhar (sem internet/pip bloqueado), **não travar**: cair no fallback do item 4.3
(HTML) e avisar o aluno em 1 linha.

Escrever e rodar um script assim (ajustar a lista `SLIDES` com os textos aprovados no 4.1):

```python
#!/usr/bin/env python3
import json, os, pathlib, textwrap
from PIL import Image, ImageDraw, ImageFont

HOME = pathlib.Path.home()
CFG = pathlib.Path(os.environ.get("OPERACAO_IA_CONFIG_DIR") or HOME / ".operacao-ia/config").expanduser()
marca = json.loads((CFG / "marca.json").read_text())
cores = dict(marca.get("cores") or {})
cores.setdefault("acento", marca.get("cor_primaria"))  # aceita também as chaves do contrato (cor_primaria)
NOME = str(marca.get("marca") or marca.get("nome") or "").strip()
if not NOME or not cores.get("acento"):
    raise SystemExit("Falta nome ou cor da marca em marca.json. Rode: python3 ~/.claude/skills/kit-lancador/marca.py set --json - (ou set --usar-padrao-zx)")
if marca.get("cor_padrao_zx"):
    print("AVISO: usando a cor padrão ZX (âmbar) porque a cor da marca não foi informada. "
          "Troque em ~/.operacao-ia/config/marca.json (cores.acento).")

def hx(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

# O carrossel é escuro: se o aluno não definiu fundo, usa um azul-noite neutro (o fundo claro
# do cores.fundo da LP não serve aqui).
FUNDO, ACENTO = hx(cores.get("fundo") or "#0B1220"), hx(cores["acento"])

def _lum(rgb):
    c = [(v / 255 / 12.92) if v / 255 <= 0.03928 else (((v / 255) + 0.055) / 1.055) ** 2.4 for v in rgb]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

def _contraste(a, b):
    x, y = _lum(a), _lum(b)
    return (max(x, y) + 0.05) / (min(x, y) + 0.05)

# Texto do carrossel: claro ou escuro, o que tiver >= 4,5:1 sobre o fundo (nunca texto ilegível).
# Candidatos em ordem de preferência; entra o primeiro com >= 4,5:1 (preto e branco puros sempre chegam a 4,58:1 em algum lado).
TEXTO = next((c for c in [(245, 245, 245), (17, 24, 39), (255, 255, 255), (0, 0, 0)] if _contraste(c, FUNDO) >= 4.5), (0, 0, 0))
# Cor de destaque (CTA e contador de slides): a cor da marca só se ler bem (>= 4,5:1) sobre o fundo;
# senão usa o TEXTO — a identidade da marca fica na barra do topo e no logo.
DESTAQUE = ACENTO if _contraste(ACENTO, FUNDO) >= 4.5 else TEXTO
W, H = 1080, 1350

def carregar_logo(altura=90):
    """Logo do aluno (png/jpg/webp local ou https). SVG ou falha de leitura -> None (usa o nome em texto)."""
    logo = marca.get("logo")
    if not logo:
        return None
    try:
        if str(logo).lower().startswith("https://"):
            import io, ipaddress, socket, urllib.parse, urllib.request
            host = urllib.parse.urlsplit(logo).hostname or ""
            if not all(ipaddress.ip_address(a[4][0]).is_global for a in socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)):
                raise ValueError("logo https aponta para endereço não público")
            class _SemRedirect(urllib.request.HTTPRedirectHandler):
                def redirect_request(self, *a, **k):
                    return None            # redirecionamento = recusado (poderia apontar para a rede interna)
            with urllib.request.build_opener(_SemRedirect).open(logo, timeout=10) as r:
                dados = r.read(2_000_001)
                if len(dados) > 2_000_000:
                    raise ValueError("logo https maior que 2 MB")
                im = Image.open(io.BytesIO(dados))
                if im.width * im.height > 4_000_000:
                    raise ValueError("logo com dimensões grandes demais")
        else:
            lp = pathlib.Path(logo).expanduser()
            # só aceita imagem dentro da pasta de config (nada de ler arquivo arbitrário nem symlink)
            if lp.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp") or lp.is_symlink() or lp.resolve().parent != CFG.resolve():
                raise ValueError("logo local fora da pasta de config ou formato não aceito")
            im = Image.open(lp)
            if im.width * im.height > 4_000_000:
                raise ValueError("logo com dimensões grandes demais")
        im = im.convert("RGBA")
        im.thumbnail((500, altura))   # mantém a proporção; logo panorâmico não estoura o slide
        return im
    except Exception as e:
        print(f"AVISO: não consegui usar o logo ({e}); a marca aparece só com o nome em texto.")
        return None

LOGO = carregar_logo()

def fonte(tamanho, negrito=False):
    candidatos = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if negrito else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if negrito else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for c in candidatos:
        try:
            return ImageFont.truetype(c, tamanho)
        except OSError:
            continue
    return ImageFont.load_default()

def slide(texto, idx, total, tipo, out_path):
    img = Image.new("RGB", (W, H), FUNDO)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 20], fill=ACENTO)  # barra de identidade da marca
    if LOGO is not None:                         # logo do aluno no topo; sem logo, o nome em texto
        img.paste(LOGO, (60, 50), LOGO)
    else:
        draw.text((60, 55), NOME, font=fonte(36, negrito=True), fill=TEXTO)
    tamanho = 66 if tipo == "capa" else 48
    f = fonte(tamanho, negrito=(tipo in ("capa", "cta")))
    linhas = textwrap.wrap(texto, width=22 if tipo == "capa" else 28)
    total_h = len(linhas) * (tamanho + 16)
    y = (H - total_h) // 2
    for linha in linhas:
        bbox = draw.textbbox((0, 0), linha, font=f)
        x = (W - (bbox[2] - bbox[0])) // 2
        cor = DESTAQUE if tipo == "cta" else TEXTO
        draw.text((x, y), linha, font=f, fill=cor)
        y += tamanho + 16
    if tipo != "capa":
        marcador = fonte(32)
        draw.text((W - 110, H - 70), f"{idx}/{total}", font=marcador, fill=DESTAQUE)
    img.save(out_path)

SLIDES = [
    # (texto, tipo)  tipo ∈ {"capa","problema","conteudo","cta"} — preencher com os textos do 4.1
]

out_dir = HOME / "kit-lancador-artefatos/divulgar/carrossel"
out_dir.mkdir(parents=True, exist_ok=True)
total = len(SLIDES)
for i, (texto, tipo) in enumerate(SLIDES, start=1):
    nome = f"slide-{i:02d}-{tipo}.png"
    slide(texto, i, total, tipo, out_dir / nome)
print(f"{total} slides gerados em {out_dir}")
```

Salvar o script em `~/kit-lancador-artefatos/divulgar/build_carrossel.py`, preencher `SLIDES` com
os textos aprovados, rodar (`python3 ~/kit-lancador-artefatos/divulgar/build_carrossel.py`) e
conferir os PNGs no dir de saída.

### 4.3 — Fallback sem Pillow (nunca travar o aluno)

Se a instalação da lib falhar, gerar em vez dos PNGs um único
`~/kit-lancador-artefatos/divulgar/carrossel/carrossel.html` com um `<div>` de 1080×1350px por
slide (CSS inline, cores e logo (ou nome) do `resolve`, quebra de página entre eles) — o aluno abre no navegador
e tira print de cada slide (ou imprime em PDF e recorta). Avisar que é o modo alternativo e por quê.

### 4.4 — Legenda do carrossel

Salvar `~/kit-lancador-artefatos/divulgar/carrossel/copy.txt`: hook do slide 1 + corpo (3-5
linhas expandindo o framework) + CTA do slide N + 8-12 hashtags (nicho + amplas), mesma regra do
Passo 3.

## Passo 5 — Disparo em modo teste (dry-run — sem serviço externo, sem segredo)

O disparo real (email ou WhatsApp) é **operação do aluno**, feita com o provedor/canal **dele**.
Esta etapa nunca embute token nem endpoint de terceiro — só valida o material e faz um preview
seguro:

1. Perguntar ao aluno o **caminho do arquivo de destinatários** (CSV/TXT com 1 email ou telefone
   por linha, ou `nome,email`). Se ele não tiver um ainda, **parar aqui** e orientar — não inventar
   lista.
2. Checar se há credencial de envio configurada em `~/.operacao-ia/config/*.env` (o provedor é
   escolha do aluno — Resend, SMTP próprio, API do WhatsApp Business, etc.). **Nenhuma credencial
   obrigatória pra chegar até aqui.**
3. Rodar sempre em **dry-run**: ler a lista, aplicar dedup, substituir placeholders (`{{nome}}`,
   `{{email}}`) no `email-lancamento.html`, e **imprimir só um preview**:
   ```
   ═══════════════════════════════════════
   DRY-RUN — pacote de divulgação
   ═══════════════════════════════════════
   Assunto:     {assunto escolhido}
   Destinatários: N (após dedup)
   Preview (5 primeiros, mascarados): n***@e***.com, ...
   Preview do corpo (200 chars): "Oi {{nome}}, ..." (com nome de exemplo, nunca o de um contato real)
   Nenhum email/WhatsApp foi enviado.
   ═══════════════════════════════════════
   ```
4. **Nunca disparar de verdade** nesta etapa. Se o aluno confirmar explicitamente que quer enviar
   ("pode disparar", "envia de verdade") **e** a credencial do provedor dele estiver presente,
   isso é uma ação separada e fora do escopo desta skill — explicar que o disparo real usa a
   ferramenta/API do provedor que ele escolheu, com a lista e o HTML já prontos aqui. Se faltar
   credencial, orientar a criar `~/.operacao-ia/config/email.env` (ou equivalente) e nunca commitar.

## Passo 6 — Persistir tudo e fechar a etapa

Abrir `~/kit-lancador-artefatos/divulgar/email-lancamento.html` no browser e conferir que o
layout responsivo e as cores da marca renderizam — mesma régua "visto renderizando" das outras
etapas.

Conferir que o diretório tem:
```
~/kit-lancador-artefatos/divulgar/
  email-lancamento.md
  email-lancamento.html
  post-social-<plataforma>.md   (1 por plataforma escolhida)
  carrossel/
    slide-01-capa.png ... slide-N-cta.png   (ou carrossel.html no fallback)
    copy.txt
  build_carrossel.py
```

```bash
python3 ~/.claude/skills/kit-lancador/estado.py done divulgar ~/kit-lancador-artefatos/divulgar/
```

## Passo 7 — Fechar o ciclo

Voltar ao menu do `/kit-lancador`: as 7 etapas estão concluídas. Parabenizar o aluno, listar
todos os artefatos com:
```bash
python3 ~/.claude/skills/kit-lancador/estado.py status
```
e resumir o caminho completo: blueprint → mini-app → LP → checkout → funil → entrega → pacote de
divulgação — tudo pronto pra ele rodar a divulgação com a lista/canal dele.

## Regra dura — sem disparo cego

**Nunca** disparar email ou WhatsApp de verdade sem o aluno confirmar explicitamente E ter a
própria credencial do provedor configurada. Esta skill só produz o material e o preview em
dry-run — o canal, a lista e a conta de envio são sempre do aluno, nunca hardcoded aqui.

## Régua

Mesma régua das outras etapas: maximizar conversão × (1 − reembolso). **Nunca prometer renda.**
Oferta honesta, garantia real, preço e features exatamente os do blueprint/manifesto — não inflar
o que o produto entrega.
