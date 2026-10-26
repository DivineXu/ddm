import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError

from download import download


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/file")
            self.end_headers()
            return
        if self.path == "/ftp":
            self.send_response(302)
            self.send_header("Location", "ftp://127.0.0.1/test")
            self.end_headers()
            return
        if self.path == "/missing":
            self.send_error(404)
            return
        self.send_response(200)
        if self.path != "/no-length":
            self.send_header("Content-Length", "100" if self.path == "/short" else "5")
        self.end_headers()
        self.wfile.write(b"hello")

    def log_message(self, *_):
        pass


class DownloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.worker = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.worker.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.worker.join()

    def test_download_redirect_and_response_without_length(self):
        with tempfile.TemporaryDirectory() as directory:
            for index, path in enumerate(["/file", "/redirect", "/no-length"]):
                target = Path(directory) / str(index)
                self.assertEqual(download(self.base + path, target), 5)
                self.assertEqual(target.read_bytes(), b"hello")

    def test_existing_file_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "existing"
            target.write_text("keep me")
            with self.assertRaises(FileExistsError):
                download(self.base + "/file", target)
            self.assertEqual(target.read_text(), "keep me")

    def test_non_http_urls_and_redirects_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "download"
            for url in ["file:///etc/hosts", "ftp://127.0.0.1/test", self.base + "/ftp"]:
                with self.assertRaises(ValueError):
                    download(url, target)
                self.assertFalse(target.exists())

    def test_errors_do_not_leave_completed_files(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "download"
            for path, error in [("/missing", HTTPError), ("/short", OSError)]:
                with self.assertRaises(error):
                    download(self.base + path, target)
                self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
