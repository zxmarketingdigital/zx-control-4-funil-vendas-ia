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

    def test_path_respeita_env_e_nao_exige_arquivo(self):
        r = self.run_marca("path")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), str(self.cfg / "marca.json"))
        self.assertFalse(self.cfg.exists())
        env = {k: v for k, v in os.environ.items() if k != "OPERACAO_IA_CONFIG_DIR"}
        r = subprocess.run([sys.executable, str(MARCA), "path"], capture_output=True, text=True, env=env)
        self.assertEqual(r.stdout.strip(), str(Path.home() / ".operacao-ia" / "config" / "marca.json"))

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
        self.assertEqual(len(list(self.cfg.glob("marca-logo-*.png"))), 1)
        res = json.loads(self.run_marca("resolve").stdout)
        self.assertEqual(res["logo"]["tipo"], "arquivo")
        self.assertTrue(res["logo"]["copiar_para_pasta"])
        self.assertTrue(res["logo"]["html_src"].startswith("marca-logo-"))
        self.assertTrue(res["logo"]["data_uri"].startswith("data:image/png;base64,"))

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
        novo = Path(self.tmp.name) / "novo.png"
        novo.write_bytes(PNG_1x1 + b"x")
        import hashlib
        (self.cfg / f"marca-logo-{hashlib.sha256(novo.read_bytes()).hexdigest()[:8]}.png").symlink_to(alvo)
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
        self.assertEqual(len(list(self.cfg.glob("marca-logo-*.png"))), 1)
        # troca por jpg: png antigo some só depois da cópia nova
        j = Path(self.tmp.name) / "c.jpg"
        j.write_bytes(b"\xff\xd8\xff")
        self.assertEqual(self.run_marca("set", "--logo", str(j)).returncode, 0)
        self.assertEqual(len(list(self.cfg.glob("marca-logo-*.jpg"))), 1)
        self.assertEqual(list(self.cfg.glob("marca-logo-*.png")), [])
        self.assertEqual(list(self.cfg.glob("*.tmp")), [])

    def test_chaves_do_contrato_cor_primaria_e_secundaria_sao_aceitas(self):
        self.cfg.mkdir(parents=True)
        (self.cfg / "marca.json").write_text(json.dumps({"nome": "Clínica Y", "cor_primaria": "#1ae", "cor_secundaria": "#334455"}))
        self.assertEqual(self.run_marca("check").returncode, 0)
        res = json.loads(self.run_marca("resolve").stdout)
        self.assertEqual(res["acento"], "#11AAEE")
        self.assertEqual(res["secundaria"], "#334455")
        self.assertEqual(res["marca"], "Clínica Y")

    def test_padrao_zx_corrige_cor_invalida_ja_gravada(self):
        self.cfg.mkdir(parents=True)
        (self.cfg / "marca.json").write_text(json.dumps({"marca": "X", "cores": {"acento": "azul"}}))
        self.assertEqual(self.run_marca("check").returncode, 1)
        r = self.run_marca("set", "--usar-padrao-zx")
        self.assertEqual(r.returncode, 0)
        self.assertIn("cor padrão ZX", r.stderr)
        self.assertEqual(self.marca_json()["cores"]["acento"], "#D97706")
        self.assertEqual(self.run_marca("check").returncode, 0)

    def test_secundaria_via_set(self):
        self.run_marca("set", "--nome", "X", "--acento", "#0055AA", "--secundaria", "#abc")
        self.assertEqual(json.loads(self.run_marca("resolve").stdout)["secundaria"], "#AABBCC")

    def test_resolve_ignora_logo_fora_da_pasta_de_config(self):
        self.cfg.mkdir(parents=True)
        segredo = Path(self.tmp.name) / "cred.png"
        segredo.write_bytes(b"conteudo-sensivel")
        (self.cfg / "marca.json").write_text(json.dumps({"marca": "X", "cores": {"acento": "#0055AA"}, "logo": str(segredo)}))
        res = json.loads(self.run_marca("resolve").stdout)
        self.assertIsNone(res["logo"]["tipo"])
        self.assertTrue(res["avisos"])
        self.assertNotIn("conteudo", json.dumps(res))

    def test_logo_antigo_sobrevive_se_marca_json_nao_grava(self):
        a = Path(self.tmp.name) / "a.png"
        a.write_bytes(PNG_1x1)
        self.run_marca("set", "--nome", "X", "--logo", str(a))
        # marca.json corrompido faz o set abortar antes de gravar: o logo antigo continua lá
        (self.cfg / "marca.json").write_text("{quebrado")
        j = Path(self.tmp.name) / "c.jpg"
        j.write_bytes(b"\xff\xd8\xff")
        self.assertNotEqual(self.run_marca("set", "--logo", str(j)).returncode, 0)
        self.assertEqual(len(list(self.cfg.glob("marca-logo-*.png"))), 1)

    def test_json_corrompido_nao_e_sobrescrito(self):
        self.cfg.mkdir(parents=True)
        (self.cfg / "marca.json").write_text("{quebrado")
        r = self.run_marca("set", "--nome", "X")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual((self.cfg / "marca.json").read_text(), "{quebrado")

    def test_logo_origem_symlink_recusado(self):
        real = Path(self.tmp.name) / "real.png"
        real.write_bytes(PNG_1x1)
        link = Path(self.tmp.name) / "link.png"
        link.symlink_to(real)
        self.assertNotEqual(self.run_marca("set", "--nome", "X", "--logo", str(link)).returncode, 0)
        self.assertEqual(list(self.cfg.glob("marca-logo-*")), [])

    def test_data_uri_respeita_limite_depois_do_base64(self):
        g = Path(self.tmp.name) / "g.png"
        g.write_bytes(PNG_1x1 + b"\0" * (250 * 1024))   # 250 KB crus viram ~333 KB em base64
        self.run_marca("set", "--nome", "X", "--acento", "#0055AA", "--logo", str(g))
        info = json.loads(self.run_marca("resolve").stdout)["logo"]
        self.assertEqual(info["tipo"], "arquivo")
        self.assertIsNone(info["data_uri"])

    def test_sets_concorrentes_deixam_logo_existente(self):
        import subprocess
        arqs = []
        for i in range(6):
            f = Path(self.tmp.name) / f"c{i}.png"
            f.write_bytes(PNG_1x1 + bytes([i]))
            arqs.append(f)
        env = dict(os.environ, OPERACAO_IA_CONFIG_DIR=str(self.cfg))
        procs = [subprocess.Popen([sys.executable, str(MARCA), "set", "--nome", "X", "--acento", "#0055AA", "--logo", str(f)],
                                  env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for f in arqs]
        for pr in procs:
            self.assertEqual(pr.wait(), 0)
        logo = self.marca_json()["logo"]
        self.assertTrue(Path(logo).is_file())
        self.assertEqual(len(list(self.cfg.glob("marca-logo-*"))), 1)

    def test_url_de_logo_com_credencial_ou_token_recusada(self):
        for u in ("https://user:pw@cdn.example/logo.png", "https://cdn.example/logo.png?token=abc", "https://cdn.example/logo.png#x"):
            self.assertNotEqual(self.run_marca("set", "--nome", "X", "--logo", u).returncode, 0, u)
        self.assertEqual(self.run_marca("set", "--nome", "X", "--logo", "https://cdn.example/logo.png").returncode, 0)

    def test_json_stdin_nao_passa_pelo_shell(self):
        nome = "$(touch /tmp/zx-nao-deve-existir) `x` \" ' ; |"
        r = subprocess.run([sys.executable, str(MARCA), "set", "--json", "-"], input=json.dumps({"nome": nome, "acento": "#0055AA"}),
                           capture_output=True, text=True, env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.marca_json()["marca"], nome)
        bad = subprocess.run([sys.executable, str(MARCA), "set", "--json", "-"], input='{"foo": 1}', capture_output=True, text=True, env=self.env)
        self.assertNotEqual(bad.returncode, 0)

    def test_json_aceita_aliases_e_resolve_ignora_url_com_token(self):
        r = subprocess.run([sys.executable, str(MARCA), "set", "--json", "-"], input=json.dumps({"nome": "X", "cor_primaria": "#05A", "cor_secundaria": "#FA0"}),
                           capture_output=True, text=True, env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.marca_json()["cores"]["acento"], "#0055AA")
        j = self.marca_json()
        j["logo"] = "https://cdn.example/logo.png?token=abc"
        (self.cfg / "marca.json").write_text(json.dumps(j))
        info = json.loads(self.run_marca("resolve").stdout)["logo"]
        self.assertIsNone(info["tipo"])

    def test_json_logo_null_remove_logo(self):
        a = Path(self.tmp.name) / "a.png"
        a.write_bytes(PNG_1x1)
        self.run_marca("set", "--nome", "X", "--acento", "#0055AA", "--logo", str(a))
        subprocess.run([sys.executable, str(MARCA), "set", "--json", "-"], input='{"logo": null}', capture_output=True, text=True, env=self.env)
        self.assertIsNone(self.marca_json()["logo"])
        self.assertEqual(list(self.cfg.glob("marca-logo-*")), [])


if __name__ == "__main__":
    unittest.main()
