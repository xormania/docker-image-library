"""Exercise post-push refresh recovery against a real local Git remote."""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from library import ROOT, read
import refresh
import writeback


class RefreshRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.remote = self.root / "origin.git"
        self.seed = self.root / "seed"
        self.worker = self.root / "worker"
        self.git(self.root, "init", "--bare", "--initial-branch=master", str(self.remote))
        self.git(self.root, "clone", str(self.remote), str(self.seed))
        shutil.copytree(ROOT, self.seed, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns(".git", "__pycache__", "out"))
        # Keep the recovery scenario independent of the repository's current
        # revisions: master starts at 1.0.0 and this refresh allocates 1.0.1.
        for path in (self.seed / "images").glob("*/definition.json"):
            definition = read(path)
            for line in definition["lines"].values():
                line["revision"] = "1.0.0"
            path.write_text(json.dumps(definition, indent=2) + "\n")
        self.git(self.seed, "config", "user.name", "Fixture")
        self.git(self.seed, "config", "user.email", "fixture@example.test")
        self.git(self.seed, "add", ".")
        self.git(self.seed, "commit", "-m", "Initial definitions")
        self.git(self.seed, "push", "origin", "master")
        self.git(self.root, "clone", str(self.remote), str(self.worker))
        self.branch = "automation/refresh-42"
        self.pr_attempts = 0
        self.pr_requests = []

    @staticmethod
    def git(cwd, *args):
        return subprocess.check_output(["git", *args], cwd=cwd, text=True, stderr=subprocess.PIPE).strip()

    @staticmethod
    def upstream(url, **kwargs):
        if url.endswith("stable.txt"):
            return io.BytesIO(b"1.0.0")
        if url.endswith("/Release"):
            return io.BytesIO((" " + "c" * 64 + " 123 main/binary-amd64/Packages.xz\n").encode())
        if "/infection/" in url:
            return io.BytesIO(json.dumps({"tag_name": "0.35.6", "assets": [{
                "name": "infection.phar", "digest": "sha256:" + "b" * 64,
                "browser_download_url": "https://example.test/infection.phar"}]}).encode())
        return io.BytesIO(json.dumps({"tag_name": "v9.9.9", "assets": [{
            "name": "symfony-cli_linux_amd64.tar.gz", "digest": "sha256:" + "a" * 64,
            "browser_download_url": "https://example.test/symfony.tar.gz"}]}).encode())

    def run_writeback(self, existing_prs=None):
        original_output = writeback.output

        def output(*args):
            if args[0] == "gh":
                self.assertEqual(args[:4], ("gh", "api", "--method", "GET"))
                self.assertIn("head=xormania:" + self.branch, args)
                self.assertIn("base=master", args)
                self.assertIn("state=open", args)
                return json.dumps(existing_prs or [])
            return original_output(*args)

        def run(*args, **kwargs):
            if args[0] == "gh":
                # Reject the GraphQL CLI path that requires read:org on a
                # public_repo-only machine token, and retain the REST request.
                self.assertEqual(args[:3], ("gh", "api", "--method"))
                self.pr_requests.append((args[3], args[4], read(args[-1])))
                self.pr_attempts += 1
                if self.pr_attempts == 1:
                    raise RuntimeError("PR creation interrupted after push")
                return
            return subprocess.run(args, cwd=self.worker, check=True, capture_output=True, **kwargs)

        with patch.object(writeback, "ROOT", self.worker), \
                patch.object(refresh, "ROOT", self.worker), \
                patch.object(writeback, "output", side_effect=output), \
                patch.object(writeback, "run", side_effect=run), \
                patch.object(refresh, "resolve", return_value={"digest": "sha256:" + "a" * 64}), \
                patch.object(refresh.urllib.request, "urlopen", side_effect=self.upstream), \
                patch.dict(os.environ, {"GITHUB_RUN_ID": "42",
                                        "GITHUB_REPOSITORY": "xormania/docker-image-library"}):
            writeback.main(refresh=True)

    def interrupt_after_push(self):
        with self.assertRaisesRegex(RuntimeError, "PR creation interrupted"):
            self.run_writeback()
        first = self.git(self.seed, "ls-remote", "--heads", "origin", self.branch).split()[0]
        shutil.rmtree(self.worker)
        self.git(self.root, "clone", str(self.remote), str(self.worker))
        return first

    def test_unchanged_rerun_recovers_missing_pr_and_preserves_revision(self):
        first = self.interrupt_after_push()
        self.run_writeback()
        after = self.git(self.seed, "ls-remote", "--heads", "origin", self.branch).split()[0]
        self.assertEqual(after, first)
        self.assertEqual(self.pr_attempts, 2)
        d = read(self.worker / "images/php-dev/definition.json")
        self.assertEqual(d["lines"]["8.4-trixie"]["revision"], "1.0.1")

    def test_rerun_merges_new_master_without_replacing_remote_history(self):
        first = self.interrupt_after_push()
        readme = self.seed / "README.md"
        readme.write_text(readme.read_text() + "\nUpstream documentation update.\n")
        self.git(self.seed, "add", "README.md")
        self.git(self.seed, "commit", "-m", "Update documentation on master")
        self.git(self.seed, "push", "origin", "master")
        self.run_writeback()
        after = self.git(self.seed, "ls-remote", "--heads", "origin", self.branch).split()[0]
        self.assertNotEqual(after, first)
        self.git(self.worker, "merge-base", "--is-ancestor", first, after)
        self.assertIn("Upstream documentation update.", (self.worker / "README.md").read_text())
        self.assertEqual(self.pr_attempts, 2)
        d = read(self.worker / "images/php-dev/definition.json")
        self.assertEqual(d["lines"]["8.4-trixie"]["revision"], "1.0.1")


    def test_rerun_updates_existing_pr_with_repository_rest_api(self):
        first = self.interrupt_after_push()
        self.run_writeback(existing_prs=[{"number": 5}])
        after = self.git(self.seed, "ls-remote", "--heads", "origin", self.branch).split()[0]
        self.assertEqual(after, first)
        method, endpoint, payload = self.pr_requests[-1]
        self.assertEqual(method, "PATCH")
        self.assertEqual(endpoint, "repos/xormania/docker-image-library/pulls/5")
        self.assertEqual(set(payload), {"title", "body"})
        self.assertIn("\n\n", payload["body"])

    def test_refresh_with_identical_pins_has_no_changes_and_uv_refresh_is_scoped(self):
        tools = read(self.worker / "images/tools.json")
        digests = {tools[name]["tag"]: tools[name]["digest"] for name in ("composer", "uv", "node")}
        for path in (self.worker / "images").glob("*/definition.json"):
            for line in read(path)["lines"].values():
                if "tag" in line["base"]:
                    digests[line["base"]["tag"]] = line["base"]["digest"]

        def unchanged(url, **kwargs):
            if url.endswith("stable.txt"):
                name = url.split("/r/")[1].split("/")[0]
                return io.BytesIO(tools[name + "_version"].encode())
            name = "infection" if "/infection/" in url else "symfony"
            pin = tools[name]
            return io.BytesIO(json.dumps({"tag_name": pin["version"], "assets": [{
                "name": "infection.phar" if name == "infection" else "symfony-cli_linux_amd64.tar.gz",
                "digest": "sha256:" + pin["sha256"], "browser_download_url": pin["url"]}]}).encode())

        paths = list((self.worker / "images").glob("*/definition.json")) + [self.worker / "images/tools.json"]
        before = {path: path.read_bytes() for path in paths}
        with patch.object(refresh, "ROOT", self.worker), \
                patch.object(refresh, "resolve", side_effect=lambda tag: {"digest": digests[tag]}), \
                patch.object(refresh.urllib.request, "urlopen", side_effect=unchanged), \
                patch.object(refresh, "apt_indexes", return_value=tools["apt_indexes"]):
            refresh.refresh()
            self.assertEqual({path: path.read_bytes() for path in paths}, before)
            digests[tools["uv"]["tag"]] = "sha256:" + "f" * 64
            refresh.refresh()
        for path in paths:
            if path.name == "definition.json" and path.parent.name != "python-dev":
                self.assertEqual(path.read_bytes(), before[path])
        python = read(self.worker / "images/python-dev/definition.json")
        self.assertEqual(python["lines"]["3.14-trixie"]["revision"], "1.0.1")

    def test_missing_pr_posts_to_repository_with_explicit_base_and_head(self):
        self.interrupt_after_push()
        self.run_writeback()
        method, endpoint, payload = self.pr_requests[-1]
        self.assertEqual(method, "POST")
        self.assertEqual(endpoint, "repos/xormania/docker-image-library/pulls")
        self.assertEqual(payload["base"], "master")
        self.assertEqual(payload["head"], self.branch)
        self.assertIn("Approve workflows to run", payload["body"])


if __name__ == "__main__":
    unittest.main()
