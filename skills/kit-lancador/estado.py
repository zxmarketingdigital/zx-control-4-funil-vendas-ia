#!/usr/bin/env python3
"""
estado.py — Estado persistido do Setup de Funil de Vendas com IA (Kit Lançador, ZX Control 4, Setup 14).

Helper standalone, SÓ stdlib. NÃO depende da infra Mission Control (setup_io.py é
acoplado a ~/.zxlab-mission-control e não pode shipar em repo público). Este helper
guarda o progresso do aluno pelas 7 etapas do lançamento num único JSON em
~/.kit-lancador/estado.json, com escrita atômica.

Fluxo fixo (ordem é lei — cada gate exige o anterior 'done'):
    planejar → criar-miniapp → lp → checkout → funil → entrega → divulgar

CLI:
    python3 estado.py status            # tabela dos 7 gates
    python3 estado.py continuar         # imprime o próximo gate pendente
    python3 estado.py redo <gate>       # volta um gate pra 'pending'
    python3 estado.py abortar           # arquiva e zera o estado
    python3 estado.py start <gate>      # marca gate 'in-progress'
    python3 estado.py done <gate> [art] # marca gate 'done' (+ caminho do artefato)
    python3 estado.py can <gate>        # exit 0 se pode avançar, 1 se bloqueado
    python3 estado.py gate <gate>       # imprime o JSON de um gate
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

SCHEMA_VERSION = 1
HOME = Path.home()
STATE_DIR = HOME / ".kit-lancador"
STATE_PATH = STATE_DIR / "estado.json"

# Ordem de execução — cada gate só libera com o anterior 'done'.
GATES = ["planejar", "criar-miniapp", "lp", "checkout", "funil", "entrega", "divulgar"]
LABELS = {
    "planejar": "Planejar produto (oferta/blueprint)",
    "criar-miniapp": "Agente Criador de Mini-Apps",
    "lp": "Landing page",
    "checkout": "Checkout Pagar.me",
    "funil": "Funil (order bump + upsell + copy)",
    "entrega": "Entrega (provisionar acesso ao SaaS)",
    "divulgar": "Divulgação (email + posts + carrossel)",
}
ICONS = {"done": "✅", "in-progress": "🔄", "pending": "⏳", "aborted": "🚫"}


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _empty_state() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "produto": "(defina no planejamento)",
        "created_at": _now(),
        "updated_at": _now(),
        "gates": {g: {"status": "pending", "artifact": None} for g in GATES},
    }


def read_state() -> dict:
    if not STATE_PATH.exists():
        return _empty_state()
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _empty_state()
    if data.get("schema_version") != SCHEMA_VERSION:
        raise SystemExit(
            f"estado.json tem schema_version={data.get('schema_version')}, "
            f"esperado {SCHEMA_VERSION}. Rode `abortar` pra recomeçar."
        )
    gates = data.setdefault("gates", {})
    # Migração — inserção do gate 'criar-miniapp' (Etapa 2) num estado que não o tinha (fluxo
    # antigo de 6 gates). Os gates a jusante (lp..divulgar) que estavam 'done' foram concluídos
    # ANTES do mini-app existir, então a invariante de ordenação está quebrada e a LP/entrega
    # não consumiram o manifesto do app. Resetá-los pra 'pending' preserva a ordem e força o
    # refazimento consumindo o mini-app novo; 'planejar' (a montante) permanece intacto.
    if "criar-miniapp" not in gates:
        for g in GATES[GATES.index("criar-miniapp"):]:
            if g in gates:
                gates[g] = {"status": "pending", "artifact": None}
    # Garante que todos os gates existem (tolerante a schema estendido).
    for g in GATES:
        gates.setdefault(g, {"status": "pending", "artifact": None})
    return data


def write_state(data: dict) -> None:
    data["updated_at"] = _now()
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(f".tmp.{os.getpid()}")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, STATE_PATH)  # atômico em POSIX


def _check_gate(gate: str) -> None:
    if gate not in GATES:
        raise SystemExit(f"Gate desconhecido: {gate}. Válidos: {', '.join(GATES)}")


def next_pending() -> str | None:
    gates = read_state()["gates"]
    for g in GATES:
        if gates[g]["status"] != "done":
            return g
    return None


def can_advance(gate: str) -> tuple[bool, str]:
    """Pode iniciar `gate`? Só se todos os anteriores estão 'done'."""
    _check_gate(gate)
    gates = read_state()["gates"]
    idx = GATES.index(gate)
    for prev in GATES[:idx]:
        if gates[prev]["status"] != "done":
            return False, f"gate '{prev}' ainda não está done (status={gates[prev]['status']})"
    return True, "ok"


def set_status(gate: str, status: str, artifact: str | None = None) -> dict:
    _check_gate(gate)
    state = read_state()
    g = state["gates"][gate]
    g["status"] = status
    if status == "in-progress" and "started_at" not in g:
        g["started_at"] = _now()
    if status == "done":
        g["completed_at"] = _now()
        if artifact:
            g["artifact"] = artifact
    write_state(state)
    return state


# ── CLI ──────────────────────────────────────────────────────────────────────
def cmd_status(_args: list[str]) -> int:
    state = read_state()
    gates = state["gates"]
    print(f"Setup de Funil de Vendas com IA — {state.get('produto', '?')}")
    print(f"Estado: {STATE_PATH}\n")
    for i, g in enumerate(GATES, 1):
        st = gates[g]["status"]
        art = gates[g].get("artifact")
        line = f"  {i}. {ICONS.get(st, '⚠️')} {LABELS[g]:<44} [{st}]"
        if art:
            line += f"\n        └─ artefato: {art}"
        print(line)
    nxt = next_pending()
    print("\n" + ("🎉 Todos os 7 gates concluídos." if nxt is None
                  else f"→ Próximo gate: {nxt} ({LABELS[nxt]})"))
    return 0


def cmd_continuar(_args: list[str]) -> int:
    nxt = next_pending()
    print("concluido" if nxt is None else nxt)
    return 0


def cmd_redo(args: list[str]) -> int:
    if not args:
        raise SystemExit("uso: estado.py redo <gate>")
    set_status(args[0], "pending")
    print(f"gate '{args[0]}' voltou pra pending")
    return 0


def cmd_abortar(_args: list[str]) -> int:
    if STATE_PATH.exists():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        STATE_PATH.rename(STATE_DIR / f"estado-abortado-{stamp}.json")
        print("estado arquivado e zerado")
    else:
        print("nenhum estado em andamento")
    return 0


def cmd_start(args: list[str]) -> int:
    if not args:
        raise SystemExit("uso: estado.py start <gate>")
    ok, reason = can_advance(args[0])
    if not ok:
        raise SystemExit(f"bloqueado: {reason}")
    set_status(args[0], "in-progress")
    print(f"gate '{args[0]}' em progresso")
    return 0


def cmd_done(args: list[str]) -> int:
    if not args:
        raise SystemExit("uso: estado.py done <gate> [caminho-do-artefato]")
    gate = args[0]
    _check_gate(gate)
    # Não confia no caller (cmd_start): valida aqui antes de marcar 'done'.
    # Aceita concluir só se o gate já está 'in-progress' OU se pode avançar
    # (todos os anteriores 'done'). Como um gate só chega a 'in-progress' via
    # cmd_start — que exige can_advance — a invariante de ordenação dos 7 gates
    # é preservada mesmo que o caller pule o 'start' ou marque 'done' fora de hora.
    status = read_state()["gates"][gate]["status"]
    ok, reason = can_advance(gate)
    if status != "in-progress" and not ok:
        raise SystemExit(f"bloqueado: não dá pra concluir '{gate}' — {reason}")
    artifact = args[1] if len(args) > 1 else None
    set_status(gate, "done", artifact)
    print(f"gate '{gate}' done" + (f" ({artifact})" if artifact else ""))
    return 0


def cmd_can(args: list[str]) -> int:
    if not args:
        raise SystemExit("uso: estado.py can <gate>")
    ok, reason = can_advance(args[0])
    print(reason)
    return 0 if ok else 1


def cmd_gate(args: list[str]) -> int:
    if not args:
        raise SystemExit("uso: estado.py gate <gate>")
    _check_gate(args[0])
    print(json.dumps(read_state()["gates"][args[0]], indent=2, ensure_ascii=False))
    return 0


def main(argv: list[str]) -> int:
    cmds = {
        "status": cmd_status, "continuar": cmd_continuar, "redo": cmd_redo,
        "abortar": cmd_abortar, "start": cmd_start, "done": cmd_done,
        "can": cmd_can, "gate": cmd_gate,
    }
    cmd = argv[0] if argv else "status"
    fn = cmds.get(cmd)
    if not fn:
        raise SystemExit(f"comando desconhecido: {cmd}. Válidos: {', '.join(cmds)}")
    return fn(argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
