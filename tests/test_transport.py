import hashlib
import io
import sys
import tarfile
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from xorder.transport import download, unpack


PAYLOAD = bytes(range(256)) * 2049
PAYLOAD_SHA256 = hashlib.sha256(PAYLOAD).hexdigest()


class ArtifactServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "http://example.test/artifact")
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Length", str(len(PAYLOAD)))
        self.end_headers()
        self.wfile.write(PAYLOAD)

    def log_message(self, *args):
        pass


class TransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), ArtifactServer)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def archive(self, members):
        path = self.root / "artifact.tar.gz"
        with tarfile.open(path, "w:gz") as archive:
            for name, kind, mode in members:
                member = tarfile.TarInfo(name)
                member.type = kind
                member.mode = mode
                if kind == tarfile.REGTYPE:
                    member.size = len(b"#!/bin/sh\nprintf ready\\n\n")
                    archive.addfile(member, io.BytesIO(b"#!/bin/sh\nprintf ready\\n\n"))
                else:
                    member.linkname = "../outside"
                    archive.addfile(member)
        return path

    def test_real_download_reports_identity_and_stages_published_filename(self):
        cached = self.root / "cache" / PAYLOAD_SHA256
        facts = download(self.url + "/artifact", cached, PAYLOAD_SHA256, allow_local_http=True)
        self.assertEqual(facts, {"sha256": PAYLOAD_SHA256, "size_bytes": len(PAYLOAD)})
        self.assertEqual(cached.read_bytes(), PAYLOAD)
        destination = self.root / "installation"
        self.assertEqual(unpack(cached, "file", destination, filename="composer.phar"), destination)
        self.assertEqual((destination / "composer.phar").read_bytes(), PAYLOAD)
        self.assertEqual(list(cached.parent.iterdir()), [cached])

    def test_corrupted_download_does_not_replace_existing_destination(self):
        destination = self.root / "accepted"
        destination.write_bytes(b"previous verified release")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            download(self.url + "/artifact", destination, "0" * 64, allow_local_http=True)
        self.assertEqual(destination.read_bytes(), b"previous verified release")
        self.assertEqual(list(self.root.iterdir()), [destination])

    def test_http_is_rejected_without_opt_in_and_opt_in_cannot_redirect_to_public_http(self):
        for url, opt_in in [(self.url + "/artifact", False), ("http://example.test/artifact", True),
                            (self.url + "/redirect", True), ("file:///etc/passwd", True)]:
            with self.subTest(url=url, opt_in=opt_in):
                with self.assertRaises(ValueError):
                    download(url, self.root / "download", PAYLOAD_SHA256, allow_local_http=opt_in)
                self.assertEqual(list(self.root.iterdir()), [])

    def test_tar_extracts_exact_bytes_and_preserves_executable_permissions(self):
        archive = self.archive([("nested", tarfile.DIRTYPE, 0o755), ("nested/run.sh", tarfile.REGTYPE, 0o755)])
        target = self.root / "unpacked"
        self.assertEqual(unpack(archive, "tar", target), target)
        self.assertEqual((target / "nested/run.sh").read_bytes(), b"#!/bin/sh\nprintf ready\\n\n")
        self.assertEqual((target / "nested/run.sh").stat().st_mode & 0o777, 0o755)

    def test_tar_rejects_unsafe_paths_links_special_files_and_permissions_before_writes(self):
        unsafe = [("../outside", tarfile.REGTYPE, 0o644), ("/outside", tarfile.REGTYPE, 0o644),
                  ("nested/../outside", tarfile.REGTYPE, 0o644), ("C:/outside", tarfile.REGTYPE, 0o644),
                  ("nested\\outside", tarfile.REGTYPE, 0o644), ("link", tarfile.SYMTYPE, 0o777),
                  ("link", tarfile.LNKTYPE, 0o644), ("device", tarfile.CHRTYPE, 0o644),
                  ("fifo", tarfile.FIFOTYPE, 0o644), ("privileged", tarfile.REGTYPE, 0o4755)]
        outside = self.root / "outside"
        outside.write_bytes(b"unrelated")
        for member in unsafe:
            with self.subTest(member=member):
                archive = self.archive([("valid-first", tarfile.REGTYPE, 0o644), member])
                target = self.root / "unpacked"
                with self.assertRaises(ValueError):
                    unpack(archive, "tar", target)
                self.assertFalse(target.exists())
                self.assertEqual(outside.read_bytes(), b"unrelated")

    def test_tar_rejects_duplicate_normalized_names_and_file_parent_collisions(self):
        for names in [[("same", tarfile.REGTYPE, 0o644), ("./same", tarfile.REGTYPE, 0o644)],
                      [("parent/child", tarfile.REGTYPE, 0o644), ("parent", tarfile.REGTYPE, 0o644)]]:
            with self.subTest(names=names):
                archive = self.archive(names)
                with self.assertRaises(ValueError):
                    unpack(archive, "tar", self.root / "unpacked")
                self.assertFalse((self.root / "unpacked").exists())

    def test_extraction_never_overlays_an_existing_destination(self):
        source = self.root / "source"
        source.write_bytes(b"new")
        target = self.root / "owned-elsewhere"
        target.mkdir()
        (target / "keep").write_bytes(b"keep")
        with self.assertRaises(FileExistsError):
            unpack(source, "file", target, filename="new")
        self.assertEqual(list(target.iterdir()), [target / "keep"])
        self.assertEqual((target / "keep").read_bytes(), b"keep")

    def test_single_file_name_cannot_escape_destination(self):
        source = self.root / "source"
        source.write_bytes(b"artifact")
        for filename in ["../outside", "/outside", "nested/file", ".", "nested\\file"]:
            with self.subTest(filename=filename):
                with self.assertRaises(ValueError):
                    unpack(source, "file", self.root / "unpacked", filename=filename)
                self.assertFalse((self.root / "unpacked").exists())


if __name__ == "__main__":
    unittest.main()
