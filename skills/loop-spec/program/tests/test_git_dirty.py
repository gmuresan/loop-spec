"""git.dirty() lists changed paths whole, including when the first porcelain line starts with a space."""
import subprocess
import tempfile
import unittest
from pathlib import Path

from loop_spec import git


def sh(cwd, *args):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def commit(worktree: Path, name: str, text: str) -> None:
    (worktree / name).write_text(text)
    sh(worktree, "git", "add", name)
    sh(worktree, "git", "commit", "-qm", f"add {name}")


class DirtyTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sh(self.repo, "git", "init", "-q", "-b", "main")
        for key, value in (("user.email", "t@example.com"), ("user.name", "t"), ("commit.gpgsign", "false")):
            sh(self.repo, "git", "config", key, value)
        commit(self.repo, "a.md", "one\n")

    def tearDown(self):
        self._tmp.cleanup()

    def test_clean(self):
        self.assertEqual(git.dirty(self.repo), [])

    def test_modified_tracked_file_first(self):
        (self.repo / "a.md").write_text("two\n")
        self.assertEqual(git.dirty(self.repo), ["a.md"])

    def test_untracked_file(self):
        (self.repo / "new.md").write_text("x\n")
        self.assertEqual(git.dirty(self.repo), ["new.md"])

    def test_both(self):
        (self.repo / "a.md").write_text("two\n")
        (self.repo / "z.md").write_text("x\n")
        self.assertEqual(git.dirty(self.repo), ["a.md", "z.md"])


if __name__ == "__main__":
    unittest.main()
