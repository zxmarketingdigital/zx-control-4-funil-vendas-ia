#!/usr/bin/env python3
"""
marca.py — Contrato de marca do aluno (Kit Lançador, ZX Control 4, Setup 14).

Helper standalone, só stdlib — mora na mesma pasta do estado.py e é instalado junto com as skills
(`~/.claude/skills/kit-lancador/marca.py`). Não depende de nada fora deste repositório.

Lê e grava `~/.operacao-ia/config/marca.json` (ou o diretório de OPERACAO_IA_CONFIG_DIR) e é o
ÚNICO lugar que valida cor, copia logo e decide o texto sobre a cor da marca — assim as 7 etapas
aplicam a marca do mesmo jeito e nenhuma cai em silêncio no âmbar da ZX.

Campos do marca.json que este contrato cobre (os demais — nicho, persona, tom, cta, preço… —
são preservados intactos):

    marca            nome da marca/produto (obrigatório)
    cores.acento     COR DA MARCA, hex #RRGGBB (obrigatório; botões, preço, destaques)
    cores.primaria   cor de apoio/escura, hex (opcional; se faltar, #0B1220)
    cores.secundaria cor secundária da marca, hex (opcional)
    (aliases do contrato, lidos se cores.* faltar: nome, cor_primaria, cor_secundaria)
    cores.fundo      cor de fundo, hex (opcional; se faltar, #FFFFFF)
    logo             caminho do arquivo copiado p/ a pasta de config, ou URL https; null = o aluno
                     escolheu não ter logo (só o nome em texto); ausente = ainda não perguntado
    cor_padrao_zx    true quando o aluno recusou informar a cor e ficou o âmbar padrão (com aviso)

CLI:
    python3 marca.py check                   # exit 0 se nome+cor existem; 1 e lista o que falta
    python3 marca.py set --json -   # valores via stdin (preferido: sem aspas nem shell no meio)
    python3 marca.py set [--nome N] [--acento #HEX] [--primaria #HEX] [--secundaria #HEX] [--fundo #HEX]
                         [--logo CAMINHO|URL|nenhum] [--usar-padrao-zx]
    python3 marca.py resolve                 # JSON final p/ as etapas (cores, texto sobre a cor, logo)
    python3 marca.py texto-sobre #HEX        # imprime #111827 ou #FFFFFF (maior contraste)
"""
from __future__ import annotations

import base64
import contextlib
import hashlib
import json
import mimetypes
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

PADRAO_ZX = "#D97706"           # âmbar ZX — só entra se o aluno recusar informar a cor
PRIMARIA_FALLBACK = "#0B1220"
FUNDO_FALLBACK = "#FFFFFF"
TEXTO_ESCURO = "#111827"
TEXTO_CLARO = "#FFFFFF"
LOGO_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
LOGO_MAX_BYTES = 2 * 1024 * 1024     # recusa logo gigante
LOGO_DATA_URI_MAX = 300 * 1024       # acima disso não vira data URI (copiar ao lado do HTML)

HEX_RE = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def config_dir() -> Path:
    env = os.environ.get("OPERACAO_IA_CONFIG_DIR")
    return Path(env).expanduser() if env else Path.home() / ".operacao-ia" / "config"


def marca_path() -> Path:
    return config_dir() / "marca.json"


# ───────────────────────── cor ─────────────────────────

def normalizar_hex(valor: str) -> str | None:
    """Aceita #RGB e #RRGGBB; devolve #RRGGBB maiúsculo. Qualquer outra coisa -> None."""
    v = (valor or "").strip()
    if not HEX_RE.match(v):
        return None
    h = v[1:]
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return "#" + h.upper()


def _luminancia(hex6: str) -> float:
    def canal(c: int) -> float:
        s = c / 255
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hex6[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * canal(r) + 0.7152 * canal(g) + 0.0722 * canal(b)


def _contraste(l1: float, l2: float) -> float:
    a, b = max(l1, l2), min(l1, l2)
    return (a + 0.05) / (b + 0.05)


MIN_CONTRASTE = 4.5   # WCAG AA para texto normal


def texto_sobre(hex6: str) -> str:
    """Cor de texto sobre a cor da marca com contraste >= 4,5:1: escuro, senão branco, senão preto puro.
    (Preto ou branco sempre chegam a >= 4,58:1, então o resultado nunca fica abaixo do mínimo.)"""
    lum = _luminancia(hex6)
    for cand in (TEXTO_ESCURO, TEXTO_CLARO, "#000000"):
        if _contraste(lum, _luminancia(cand)) >= MIN_CONTRASTE:
            return cand
    return "#000000"


# ───────────────────────── arquivo ─────────────────────────

def ler_marca() -> dict:
    p = marca_path()
    if not p.exists():
        return {}
    try:
        dados = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"ERRO: {p} não é um JSON válido ({e}). Corrija o arquivo ou apague para recriar.")
    if not isinstance(dados, dict):
        raise SystemExit(f"ERRO: {p} deveria ser um objeto JSON.")
    return dados


def gravar_marca(dados: dict) -> None:
    p = marca_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".marca-", suffix=".tmp", dir=str(p.parent))   # nome exclusivo: não segue symlink
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(dados, indent=2, ensure_ascii=False) + "\n")
        os.replace(tmp, p)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _copiar_logo(origem: str) -> str:
    """URL https fica como está; arquivo local é copiado para a pasta de config. Devolve o valor a gravar."""
    if origem.lower().startswith("https://"):
        u = urlsplit(origem)
        if not u.hostname or u.username or u.password or u.query or u.fragment:
            raise SystemExit("ERRO: URL de logo não pode ter usuário, senha, parâmetros (?token=...) nem #. "
                             "Use um link público direto da imagem ou um arquivo local.")
        return origem
    if origem.lower().startswith("http://"):
        raise SystemExit("ERRO: URL de logo precisa ser https://. Use https ou um arquivo local.")
    src = Path(origem).expanduser()
    if src.is_symlink():
        raise SystemExit(f"ERRO: {src} é um link simbólico; informe o arquivo de imagem real.")
    if not src.is_file():
        raise SystemExit(f"ERRO: arquivo de logo não encontrado: {src}")
    ext = src.suffix.lower()
    if ext not in LOGO_EXTS:
        raise SystemExit(f"ERRO: logo precisa ser png, jpg, svg ou webp (veio '{ext or 'sem extensão'}').")
    if src.stat().st_size > LOGO_MAX_BYTES:
        raise SystemExit("ERRO: logo maior que 2 MB. Use uma versão menor.")
    # nome com hash do conteúdo: trocar de logo nunca sobrescreve o arquivo que o marca.json atual referencia
    h = hashlib.sha256(src.read_bytes()).hexdigest()[:8]
    destino = config_dir() / f"marca-logo-{h}{ext}"
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.is_symlink():
        raise SystemExit(f"ERRO: {destino} é um link simbólico; remova-o e tente de novo.")
    if src.resolve() != destino.resolve():
        # copia para temporário e troca atômica: se a cópia falhar, o logo antigo continua intacto
        tmp = destino.with_name(destino.name + ".tmp")
        if tmp.is_symlink() or tmp.exists():
            tmp.unlink()
        try:
            shutil.copyfile(src, tmp)
            os.replace(tmp, destino)
        except OSError as e:
            if tmp.exists() or tmp.is_symlink():
                tmp.unlink()
            raise SystemExit(f"ERRO: não consegui copiar o logo ({e}). O logo anterior foi mantido.")
    return str(destino)


def _limpar_logos_orfaos(m: dict) -> None:
    """Depois que o marca.json novo foi gravado: remove marca-logo* que ele não referencia mais."""
    atual = m.get("logo")
    atual_nome = Path(str(atual)).name if atual and not str(atual).lower().startswith("https://") else None
    for velho in config_dir().glob("marca-logo*"):
        if velho.name != atual_nome and not velho.name.endswith(".tmp") and not velho.is_dir():
            velho.unlink()


# ───────────────────────── comandos ─────────────────────────

def _cor_marca(m: dict):
    """Cor da marca: cores.acento (formato do kit) ou cor_primaria (chave do contrato/SPEC)."""
    return (m.get("cores") or {}).get("acento") or m.get("cor_primaria")


def _cor_apoio(m: dict):
    """Cor secundária opcional: cores.secundaria ou cor_secundaria (contrato)."""
    return (m.get("cores") or {}).get("secundaria") or m.get("cor_secundaria")


def _faltando(m: dict) -> list[str]:
    falta = []
    if not str(m.get("marca", "") or m.get("nome", "")).strip():
        falta.append("nome (marca)")
    acento = _cor_marca(m)
    if not (isinstance(acento, str) and normalizar_hex(acento)):
        falta.append("cor da marca (cores.acento, hex)")
    return falta


def cmd_check(_args: list[str]) -> int:
    m = ler_marca()
    falta = _faltando(m)
    logo_estado = "perguntado" if "logo" in m else "nao_perguntado"
    print(json.dumps({"faltando": falta, "logo": logo_estado}, ensure_ascii=False))
    return 1 if falta else 0


@contextlib.contextmanager
def _trava_config():
    """Serializa execuções de `set` (cópia + gravação + limpeza). Sem suporte a lock no sistema, segue sem travar."""
    config_dir().mkdir(parents=True, exist_ok=True)
    f = open(config_dir() / ".marca.lock", "a+")
    travado = False
    try:
        try:
            import fcntl
            fcntl.flock(f, fcntl.LOCK_EX)
            travado = True
        except ImportError:
            try:
                import msvcrt
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
                travado = True
            except (ImportError, OSError):
                pass
        yield
    finally:
        if travado:
            try:
                import fcntl
                fcntl.flock(f, fcntl.LOCK_UN)
            except ImportError:
                try:
                    import msvcrt
                    f.seek(0)
                    msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                except (ImportError, OSError):
                    pass
        f.close()


def cmd_set(args: list[str]) -> int:
    with _trava_config():
        return _cmd_set(args)


def _args_de_json(args: list[str]) -> list[str]:
    """`set --json -`: lê os valores de um JSON no stdin (nome, acento, primaria, secundaria, fundo, logo).
    Evita montar comando de shell com texto digitado pelo aluno (aspas, $(...), crases)."""
    if args.count("--json") != 1 or args[args.index("--json") + 1:args.index("--json") + 2] != ["-"]:
        return args
    i = args.index("--json")
    resto = args[:i] + args[i + 2:]
    try:
        dados = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        raise SystemExit(f"ERRO: JSON inválido no stdin ({e}).")
    if not isinstance(dados, dict):
        raise SystemExit("ERRO: o JSON do stdin deve ser um objeto.")
    # aliases do contrato (SPEC): cor_primaria = acento, cor_secundaria = secundaria; o nome canônico vence se vierem os dois
    for alias, canon in (("cor_primaria", "acento"), ("cor_secundaria", "secundaria")):
        if alias in dados:
            dados.setdefault(canon, dados[alias])
            del dados[alias]
    extras = []
    for k in ("nome", "acento", "primaria", "secundaria", "fundo", "logo"):
        if k in dados and dados[k] is not None:
            if not isinstance(dados[k], str):
                raise SystemExit(f"ERRO: '{k}' deve ser texto.")
            extras += [f"--{k}", dados[k]]
    desconhecidas = set(dados) - {"nome", "acento", "primaria", "secundaria", "fundo", "logo"}
    if desconhecidas:
        raise SystemExit(f"ERRO: campos desconhecidos no JSON: {sorted(desconhecidas)}")
    return resto + extras


def _cmd_set(args: list[str]) -> int:
    args = _args_de_json(args)
    m = ler_marca()
    cores = dict(m.get("cores") or {})
    i = 0
    usar_padrao = False
    logo_mexido = False
    while i < len(args):
        a = args[i]
        if a == "--usar-padrao-zx":
            usar_padrao = True
            i += 1
            continue
        if a not in ("--nome", "--acento", "--primaria", "--secundaria", "--fundo", "--logo") or i + 1 >= len(args):
            raise SystemExit(f"argumento inválido: {a}")
        valor = args[i + 1]
        i += 2
        if a == "--nome":
            if not valor.strip():
                raise SystemExit("ERRO: nome vazio.")
            m["marca"] = valor.strip()
        elif a in ("--acento", "--primaria", "--secundaria", "--fundo"):
            h = normalizar_hex(valor)
            if not h:
                raise SystemExit(f"ERRO: '{valor}' não é uma cor válida. Use hex tipo #1A73E8 ou #1AE.")
            cores[a[2:]] = h
            if a == "--acento":
                m.pop("cor_padrao_zx", None)
        elif a == "--logo":
            logo_mexido = True
            m["logo"] = None if valor.strip().lower() in ("nenhum", "nao", "não", "") else _copiar_logo(valor.strip())
    atual = cores.get("acento") or m.get("cor_primaria")
    if usar_padrao and not (isinstance(atual, str) and normalizar_hex(atual)):
        # sem cor, ou com cor inválida já gravada: aplica o padrão e avisa
        cores["acento"] = PADRAO_ZX
        m["cor_padrao_zx"] = True
        print(f"AVISO: Usando a cor padrão ZX (âmbar {PADRAO_ZX}). Troque depois em {marca_path()} (campo cores.acento).",
              file=sys.stderr)
    if cores:
        m["cores"] = cores
    gravar_marca(m)
    if logo_mexido:
        _limpar_logos_orfaos(m)   # só depois do JSON novo no disco: falha antes disso mantém o logo antigo
    print(f"marca.json atualizado em {marca_path()}")
    return 0


def _logo_info(m: dict) -> dict:
    logo = m.get("logo")
    if not logo:
        return {"tipo": None, "src": None, "html_src": None, "copiar_para_pasta": False, "data_uri": None}
    if str(logo).lower().startswith("https://"):
        u = urlsplit(str(logo))
        if not u.hostname or u.username or u.password or u.query or u.fragment:   # mesma regra do `set`, para JSON editado à mão
            return {"tipo": None, "src": None, "html_src": None, "copiar_para_pasta": False, "data_uri": None,
                    "aviso": "logo https ignorado: a URL não pode ter usuário, senha, parâmetros nem #."}
        return {"tipo": "url", "src": logo, "html_src": logo, "copiar_para_pasta": False, "data_uri": None}
    p = Path(str(logo)).expanduser()
    try:
        dentro = p.resolve().parent == config_dir().resolve()
    except OSError:
        dentro = False
    if p.suffix.lower() not in LOGO_EXTS or p.is_symlink() or not dentro:
        return {"tipo": None, "src": None, "html_src": None, "copiar_para_pasta": False,
                "aviso": f"logo ignorado (precisa ser imagem png/jpg/gif/svg/webp dentro de {config_dir()}): {p.name}. "
                         "Rode marca.py set --logo <arquivo> para copiá-lo."}
    if not p.is_file():
        return {"tipo": None, "src": None, "html_src": None, "copiar_para_pasta": False,
                "aviso": f"logo configurado não existe mais: {p.name}"}
    tam = p.stat().st_size
    info = {"tipo": "arquivo", "src": str(p), "html_src": p.name, "copiar_para_pasta": True, "data_uri": None}
    if tam <= LOGO_DATA_URI_MAX:   # alternativa p/ HTML de arquivo único; as etapas preferem copiar o arquivo
        mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        try:
            uri = f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode('ascii')}"
        except OSError:   # arquivo trocado/limpo por um set concorrente: segue sem data URI
            uri = ""
        if uri and len(uri) <= LOGO_DATA_URI_MAX:   # o limite vale para o tamanho já codificado
            info["data_uri"] = uri
    return info


def cmd_resolve(_args: list[str]) -> int:
    m = ler_marca()
    falta = _faltando(m)
    if falta:
        print(json.dumps({"faltando": falta}, ensure_ascii=False))
        return 1
    cores = m.get("cores") or {}
    acento = normalizar_hex(_cor_marca(m))
    apoio = normalizar_hex(_cor_apoio(m) or "")
    primaria = normalizar_hex(cores.get("primaria") or "") or PRIMARIA_FALLBACK
    fundo = normalizar_hex(cores.get("fundo") or "") or FUNDO_FALLBACK
    avisos = []
    if m.get("cor_padrao_zx"):
        avisos.append(f"Usando a cor padrão ZX (âmbar {PADRAO_ZX}). Troque depois em {marca_path()} (campo cores.acento).")
    logo = _logo_info(m)
    if logo.get("aviso"):
        avisos.append(logo.pop("aviso"))
    print(json.dumps({
        "marca": str(m.get("marca") or m.get("nome")).strip(),
        "acento": acento,
        "texto_sobre_acento": texto_sobre(acento),
        "primaria": primaria,
        "secundaria": apoio,
        "fundo": fundo,
        "logo": logo,
        "avisos": avisos,
    }, ensure_ascii=False, indent=2))
    return 0


def cmd_texto_sobre(args: list[str]) -> int:
    h = normalizar_hex(args[0]) if args else None
    if not h:
        raise SystemExit("uso: marca.py texto-sobre #HEX")
    print(texto_sobre(h))
    return 0


def main(argv: list[str]) -> int:
    cmds = {"check": cmd_check, "set": cmd_set, "resolve": cmd_resolve, "texto-sobre": cmd_texto_sobre}
    cmd = argv[0] if argv else "check"
    fn = cmds.get(cmd)
    if not fn:
        raise SystemExit(f"comando desconhecido: {cmd}. Válidos: {', '.join(cmds)}")
    return fn(argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
