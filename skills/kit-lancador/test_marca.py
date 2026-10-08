#!/usr/bin/env python3
"""Smoke do contrato de marca. Rodar: python3 -m unittest skills/kit-lancador/test_marca.py -v"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MARCA = Path(__file__).with_name("marca.py")
PNG_1x1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d49444154789c6360f8cfc0f01f0005000201a5f645400000000049454e44ae426082"
)


class MarcaTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cfg = Path(self.tmp.name) / "config"
        self.env = dict(os.environ, OPERACAO_IA_CONFIG_DIR=str(self.cfg))

    def tearDown(self):
        self.tmp.cleanup()

    def run_marca(self, *args):
        return subprocess.run([sys.executable, str(MARCA), *args], capture_output=True, text=True, env=self.env)

    def marca_json(self):
        return json.loads((self.cfg / "marca.json").read_text())

    def test_check_sem_arquivo_falha_e_lista(self):
        r = self.run_marca("check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("nome", r.stdout)

    def test_set_normaliza_hex_curto_e_preserva_outros_campos(self):
        self.cfg.mkdir(parents=True)
        (self.cfg / "marca.json").write_text(json.dumps({"nicho": "dentistas", "cta": "Quero"}))
        r = self.run_marca("set", "--nome", "Clínica X", "--acento", "#1ae")
        self.assertEqual(r.returncode, 0, r.stderr)
        m = self.marca_json()
        self.assertEqual(m["cores"]["acento"], "#11AAEE")
        self.assertEqual(m["nicho"], "dentistas")
        self.assertEqual(self.run_marca("check").returncode, 0)

    def test_hex_invalido_e_rejeitado_sem_gravar(self):
        for ruim in ("azul", "#12", "#GGGGGG", "1AE", "#1234567"):
            r = self.run_marca("set", "--nome", "X", "--acento", ruim)
            self.assertNotEqual(r.returncode, 0, ruim)
        self.assertFalse((self.cfg / "marca.json").exists())

    def test_padrao_zx_avisa_explicitamente_e_marca_flag(self):
        self.run_marca("set", "--nome", "X")
        r = self.run_marca("set", "--usar-padrao-zx")
        self.assertEqual(r.returncode, 0)
        self.assertIn("cor padrão ZX", r.stderr)
        self.assertTrue(self.marca_json()["cor_padrao_zx"])
        res = json.loads(self.run_marca("resolve").stdout)
        self.assertEqual(res["acento"], "#D97706")
        self.assertTrue(res["avisos"])

    def test_cor_informada_limpa_flag_padrao(self):
        self.run_marca("set", "--nome", "X", "--usar-padrao-zx")
        self.run_marca("set", "--acento", "#0055AA")
        self.assertNotIn("cor_padrao_zx", self.marca_json())
        self.assertEqual(json.loads(self.run_marca("resolve").stdout)["avisos"], [])

    def test_padrao_zx_nao_sobrescreve_cor_ja_informada(self):
        self.run_marca("set", "--nome", "X", "--acento", "#0055AA")
        self.run_marca("set", "--usar-padrao-zx")
        self.assertEqual(self.marca_json()["cores"]["acento"], "#0055AA")

    def test_contraste_texto_sobre_cor(self):
        self.assertEqual(self.run_marca("texto-sobre", "#FFEB3B").stdout.strip(), "#111827")  # amarelo claro
        self.assertEqual(self.run_marca("texto-sobre", "#0B1220").stdout.strip(), "#FFFFFF")  # azul escuro
        self.assertEqual(self.run_marca("texto-sobre", "#D97706").stdout.strip(), "#111827")  # âmbar
        # cinza médio: nem o escuro nem o branco chegam a 4,5:1 -> preto puro
        self.assertEqual(self.run_marca("texto-sobre", "#777777").stdout.strip(), "#000000")

    def test_logo_local_copiado_e_vira_data_uri(self):
        png = Path(self.tmp.name) / "meu logo.png"
        png.write_bytes(PNG_1x1)
        r = self.run_marca("set", "--nome", "X", "--acento", "#0055AA", "--logo", str(png))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.cfg / "marca-logo.png").is_file())
        res = json.loads(self.run_marca("resolve").stdout)
        self.assertEqual(res["logo"]["tipo"], "arquivo")
        self.assertTrue(res["logo"]["html_src"].startswith("data:image/png;base64,"))

    def test_logo_extensao_invalida_e_url_http_rejeitadas(self):
        txt = Path(self.tmp.name) / "a.txt"
        txt.write_text("x")
        self.assertNotEqual(self.run_marca("set", "--nome", "X", "--logo", str(txt)).returncode, 0)
        self.assertNotEqual(self.run_marca("set", "--nome", "X", "--logo", "http://x.com/a.png").returncode, 0)
        self.assertEqual(self.run_marca("set", "--nome", "X", "--logo", "https://x.com/a.png").returncode, 0)

    def test_logo_nenhum_grava_null_e_check_diferencia_de_nao_perguntado(self):
        self.run_marca("set", "--nome", "X", "--acento", "#0055AA")
        self.assertEqual(json.loads(self.run_marca("check").stdout)["logo"], "nao_perguntado")
        self.run_marca("set", "--logo", "nenhum")
        self.assertIsNone(self.marca_json()["logo"])
        self.assertEqual(json.loads(self.run_marca("check").stdout)["logo"], "perguntado")
        self.assertIsNone(json.loads(self.run_marca("resolve").stdout)["logo"]["tipo"])

    def test_logo_destino_symlink_recusado(self):
        self.cfg.mkdir(parents=True)
        alvo = Path(self.tmp.name) / "alvo.png"
        alvo.write_bytes(PNG_1x1)
        (self.cfg / "marca-logo.png").symlink_to(alvo)
        novo = Path(self.tmp.name) / "novo.png"
        novo.write_bytes(PNG_1x1 + b"x")
        r = self.run_marca("set", "--nome", "X", "--logo", str(novo))
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(alvo.read_bytes(), PNG_1x1)  # alvo do link não foi sobrescrito

    def test_troca_de_logo_mantem_antigo_se_copia_falha_e_remove_outra_extensao_se_ok(self):
        a = Path(self.tmp.name) / "a.png"
        a.write_bytes(PNG_1x1)
        self.run_marca("set", "--nome", "X", "--logo", str(a))
        # origem inválida (extensão): falha antes de mexer em qualquer coisa
        txt = Path(self.tmp.name) / "b.txt"
        txt.write_text("x")
        self.assertNotEqual(self.run_marca("set", "--logo", str(txt)).returncode, 0)
        self.assertTrue((self.cfg / "marca-logo.png").is_file())
        # troca por jpg: png antigo some só depois da cópia nova
        j = Path(self.tmp.name) / "c.jpg"
        j.write_bytes(b"\xff\xd8\xff")
        self.assertEqual(self.run_marca("set", "--logo", str(j)).returncode, 0)
        self.assertTrue((self.cfg / "marca-logo.jpg").is_file())
        self.assertFalse((self.cfg / "marca-logo.png").exists())
        self.assertEqual(list(self.cfg.glob("*.tmp")), [])

    def test_json_corrompido_nao_e_sobrescrito(self):
        self.cfg.mkdir(parents=True)
        (self.cfg / "marca.json").write_text("{quebrado")
        r = self.run_marca("set", "--nome", "X")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual((self.cfg / "marca.json").read_text(), "{quebrado")


if __name__ == "__main__":
    unittest.main()
