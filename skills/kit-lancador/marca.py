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
    cores.fundo      cor de fundo, hex (opcional; se faltar, #FFFFFF)
    logo             caminho do arquivo copiado p/ a pasta de config, ou URL https; null = o aluno
                     escolheu não ter logo (só o nome em texto); ausente = ainda não perguntado
    cor_padrao_zx    true quando o aluno recusou informar a cor e ficou o âmbar padrão (com aviso)

CLI:
    python3 marca.py check                   # exit 0 se nome+cor existem; 1 e lista o que falta
    python3 marca.py set [--nome N] [--acento #HEX] [--primaria #HEX] [--fundo #HEX]
                         [--logo CAMINHO|URL|nenhum] [--usar-padrao-zx]
    python3 marca.py resolve                 # JSON final p/ as etapas (cores, texto sobre a cor, logo)
    python3 marca.py texto-sobre #HEX        # imprime #111827 ou #FFFFFF (maior contraste)
"""
from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
import shutil
import sys
from pathlib import Path

PADRAO_ZX = "#D97706"           # âmbar ZX — só entra se o aluno recusar informar a cor
PRIMARIA_FALLBACK = "#0B1220"
FUNDO_FALLBACK = "#FFFFFF"
TEXTO_ESCURO = "#111827"
TEXTO_CLARO = "#FFFFFF"
LOGO_EXTS = {".png", ".jpg", ".jpeg", ".svg", ".webp"}
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


def texto_sobre(hex6: str) -> str:
    """Cor de texto (escuro ou branco) com MAIOR contraste sobre a cor dada (botão da marca)."""
    lum = _luminancia(hex6)
    c_escuro = _contraste(lum, _luminancia(TEXTO_ESCURO))
    c_claro = _contraste(lum, _luminancia(TEXTO_CLARO))
    return TEXTO_ESCURO if c_escuro > c_claro else TEXTO_CLARO


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
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(dados, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, p)


def _copiar_logo(origem: str) -> str:
    """URL https fica como está; arquivo local é copiado para a pasta de config. Devolve o valor a gravar."""
    if origem.lower().startswith("https://"):
        return origem
    if origem.lower().startswith("http://"):
        raise SystemExit("ERRO: URL de logo precisa ser https://. Use https ou um arquivo local.")
    src = Path(origem).expanduser()
    if not src.is_file():
        raise SystemExit(f"ERRO: arquivo de logo não encontrado: {src}")
    ext = src.suffix.lower()
    if ext not in LOGO_EXTS:
        raise SystemExit(f"ERRO: logo precisa ser png, jpg, svg ou webp (veio '{ext or 'sem extensão'}').")
    if src.stat().st_size > LOGO_MAX_BYTES:
        raise SystemExit("ERRO: logo maior que 2 MB. Use uma versão menor.")
    destino = config_dir() / f"marca-logo{ext}"
    destino.parent.mkdir(parents=True, exist_ok=True)
    # remove logos antigos de outra extensão para não sobrar lixo
    for velho in config_dir().glob("marca-logo.*"):
        if velho != destino:
            velho.unlink()
    if src.resolve() != destino.resolve():
        shutil.copyfile(src, destino)
    return str(destino)


# ───────────────────────── comandos ─────────────────────────

def _faltando(m: dict) -> list[str]:
    falta = []
    if not str(m.get("marca", "")).strip():
        falta.append("nome (marca)")
    acento = (m.get("cores") or {}).get("acento")
    if not (isinstance(acento, str) and normalizar_hex(acento)):
        falta.append("cor da marca (cores.acento, hex)")
    return falta


def cmd_check(_args: list[str]) -> int:
    m = ler_marca()
    falta = _faltando(m)
    logo_estado = "perguntado" if "logo" in m else "nao_perguntado"
    print(json.dumps({"faltando": falta, "logo": logo_estado}, ensure_ascii=False))
    return 1 if falta else 0


def cmd_set(args: list[str]) -> int:
    m = ler_marca()
    cores = dict(m.get("cores") or {})
    i = 0
    usar_padrao = False
    while i < len(args):
        a = args[i]
        if a == "--usar-padrao-zx":
            usar_padrao = True
            i += 1
            continue
        if a not in ("--nome", "--acento", "--primaria", "--fundo", "--logo") or i + 1 >= len(args):
            raise SystemExit(f"argumento inválido: {a}")
        valor = args[i + 1]
        i += 2
        if a == "--nome":
            if not valor.strip():
                raise SystemExit("ERRO: nome vazio.")
            m["marca"] = valor.strip()
        elif a in ("--acento", "--primaria", "--fundo"):
            h = normalizar_hex(valor)
            if not h:
                raise SystemExit(f"ERRO: '{valor}' não é uma cor válida. Use hex tipo #1A73E8 ou #1AE.")
            cores[a[2:]] = h
            if a == "--acento":
                m.pop("cor_padrao_zx", None)
        elif a == "--logo":
            m["logo"] = None if valor.strip().lower() in ("nenhum", "nao", "não", "") else _copiar_logo(valor.strip())
    if usar_padrao and not cores.get("acento"):
        cores["acento"] = PADRAO_ZX
        m["cor_padrao_zx"] = True
        print(f"AVISO: Usando a cor padrão ZX (âmbar {PADRAO_ZX}). Troque depois em {marca_path()} (campo cores.acento).",
              file=sys.stderr)
    if cores:
        m["cores"] = cores
    gravar_marca(m)
    print(f"marca.json atualizado em {marca_path()}")
    return 0


def _logo_info(m: dict) -> dict:
    logo = m.get("logo")
    if not logo:
        return {"tipo": None, "src": None, "html_src": None, "copiar_para_pasta": False}
    if str(logo).lower().startswith("https://"):
        return {"tipo": "url", "src": logo, "html_src": logo, "copiar_para_pasta": False}
    p = Path(str(logo)).expanduser()
    if not p.is_file():
        return {"tipo": None, "src": None, "html_src": None, "copiar_para_pasta": False,
                "aviso": f"logo configurado não existe mais: {p}"}
    tam = p.stat().st_size
    if tam <= LOGO_DATA_URI_MAX:
        mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        b64 = base64.b64encode(p.read_bytes()).decode("ascii")
        return {"tipo": "arquivo", "src": str(p), "html_src": f"data:{mime};base64,{b64}", "copiar_para_pasta": False}
    return {"tipo": "arquivo", "src": str(p), "html_src": p.name, "copiar_para_pasta": True}


def cmd_resolve(_args: list[str]) -> int:
    m = ler_marca()
    falta = _faltando(m)
    if falta:
        print(json.dumps({"faltando": falta}, ensure_ascii=False))
        return 1
    cores = m.get("cores") or {}
    acento = normalizar_hex(cores["acento"])
    primaria = normalizar_hex(cores.get("primaria") or "") or PRIMARIA_FALLBACK
    fundo = normalizar_hex(cores.get("fundo") or "") or FUNDO_FALLBACK
    avisos = []
    if m.get("cor_padrao_zx"):
        avisos.append(f"Usando a cor padrão ZX (âmbar {PADRAO_ZX}). Troque depois em {marca_path()} (campo cores.acento).")
    logo = _logo_info(m)
    if logo.get("aviso"):
        avisos.append(logo.pop("aviso"))
    print(json.dumps({
        "marca": m["marca"].strip(),
        "acento": acento,
        "texto_sobre_acento": texto_sobre(acento),
        "primaria": primaria,
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
