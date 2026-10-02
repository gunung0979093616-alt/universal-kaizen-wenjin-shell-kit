import http.server
import json
import os
import socketserver
import subprocess
import sys
import tempfile
import threading
import unittest
import zipfile
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))
import shell_gate  # noqa: E402


class ShellGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "tests").mkdir()
        (self.root / "pyproject.toml").write_text("[project]\nname='demo'\nversion='0.1.0'\n")
        (self.root / ".env.example").write_text("TOKEN=example\n")
        subprocess.run(["git", "init"], cwd=self.root, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Shell gate test"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=self.root, capture_output=True, check=True)

    def tearDown(self):
        self.temp.cleanup()

    def test_doctor_and_project_check_return_real_metadata(self):
        self.assertEqual(shell_gate.doctor(self.root)["state"], "VERIFIED")
        check = shell_gate.project_check(self.root)
        self.assertIn("pyproject.toml", check["dependency_or_runtime_files"])
        self.assertIn("tests", check["test_directories"])
        self.assertTrue(check["git"]["commit"])

    def test_safe_command_records_evidence(self):
        record, proof = shell_gate.run_argv(self.root, [sys.executable, "-c", "print('ok')"], allow_write=True)
        self.assertEqual(record.result, "SUCCESS")
        self.assertEqual(record.state, "VERIFIED")
        self.assertTrue(proof.exists())
        saved = json.loads(proof.read_text())
        self.assertEqual(saved["exit_code"], 0)
        self.assertIn("ok", saved["stdout"])

    def test_failed_command_stays_failed_and_preserves_stderr(self):
        record, proof = shell_gate.run_argv(self.root, [sys.executable, "-c", "import sys; print('broken', file=sys.stderr); sys.exit(7)"], allow_write=True)
        self.assertEqual(record.result, "FAILED")
        self.assertEqual(record.exit_code, 7)
        self.assertIn("broken", json.loads(proof.read_text())["stderr"])

    def test_write_requires_explicit_allow_write(self):
        record, _ = shell_gate.run_argv(self.root, ["git", "add", "pyproject.toml"])
        self.assertEqual(record.state, "BLOCKED")
        self.assertEqual(record.risk, "write")

    def test_destructive_command_is_blocked_even_with_allow_write(self):
        record, _ = shell_gate.run_argv(self.root, ["rm", "-rf", "something"], allow_write=True)
        self.assertEqual(record.state, "BLOCKED")
        self.assertEqual(record.risk, "high")

    def test_output_secrets_are_redacted(self):
        record, _ = shell_gate.run_argv(self.root, [sys.executable, "-c", "print('api_key=sk-abcdefghijklmnop')"], allow_write=True)
        self.assertNotIn("sk-abcdefghijklmnop", record.stdout)
        self.assertIn("[REDACTED]", record.stdout)

    def test_zip_excludes_env_and_private_key_and_validates(self):
        (self.root / "app.py").write_text("print('safe')\n")
        (self.root / ".env").write_text("SHOULD_NOT_SHIP=1\n")
        (self.root / "private.pem").write_text("SHOULD_NOT_SHIP\n")
        target = self.root / "out" / "delivery.zip"
        result = shell_gate.make_zip(self.root, target)
        self.assertEqual(result["state"], "VERIFIED")
        with zipfile.ZipFile(target) as archive:
            names = archive.namelist()
            self.assertIn("app.py", names)
            self.assertNotIn(".env", names)
            self.assertNotIn("private.pem", names)
            self.assertIsNone(archive.testzip())

    def test_inline_python_write_requires_allow_write(self):
        target = self.root / "should-not-exist.txt"
        code = "from pathlib import Path; Path('should-not-exist.txt').write_text('x')"
        record, _ = shell_gate.run_argv(self.root, [sys.executable, "-c", code])
        self.assertEqual(record.state, "BLOCKED")
        self.assertEqual(record.risk, "write")
        self.assertFalse(target.exists())

    def test_harmless_destructive_words_are_not_blocked(self):
        record, _ = shell_gate.run_argv(self.root, [sys.executable, "-c", "print('drop table users')"], allow_write=True)
        self.assertEqual(record.state, "VERIFIED")
        self.assertIn("drop table users", record.stdout)

    def test_zip_excludes_common_secret_files(self):
        (self.root / "app.py").write_text("print('safe')\n")
        for name in ("credentials.json", ".npmrc", "id_rsa"):
            (self.root / name).write_text("SECRET\n")
        target = self.root / "delivery.zip"
        shell_gate.make_zip(self.root, target)
        with zipfile.ZipFile(target) as archive:
            names = archive.namelist()
        for name in ("credentials.json", ".npmrc", "id_rsa"):
            self.assertNotIn(name, names)

    def test_zip_does_not_follow_symlinks(self):
        outside_dir = tempfile.TemporaryDirectory()
        try:
            outside = Path(outside_dir.name) / "outside-secret.txt"
            outside.write_text("OUTSIDE_SECRET\n")
            link = self.root / "linked-secret.txt"
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("symlink unavailable on this platform")
            (self.root / "app.py").write_text("print('safe')\n")
            target = self.root / "delivery.zip"
            shell_gate.make_zip(self.root, target)
            with zipfile.ZipFile(target) as archive:
                self.assertNotIn("linked-secret.txt", archive.namelist())
        finally:
            outside_dir.cleanup()

    def test_http_check_uses_real_server_response(self):
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
            def log_message(self, *args):
                pass
        server = socketserver.TCPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            result = shell_gate.http_check(f"http://127.0.0.1:{server.server_address[1]}/health")
            self.assertEqual(result["state"], "VERIFIED")
            self.assertEqual(result["status"], 200)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
