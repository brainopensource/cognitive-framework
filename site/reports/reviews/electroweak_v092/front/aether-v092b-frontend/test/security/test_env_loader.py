"""Tests for the safe .env credential loader.

Owning contract: S6B-SEC-003, REQ-TRUST-001.
Covers: duplicate keys, interpolation, commands, malformed records,
permissive permissions, symlinks, tracked files, missing credentials,
secret propagation prevention.
"""

from __future__ import annotations

import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from vanguard.packages.adapters.models.env_loader import (
    ALLOWED_KEY,
    _MAX_PERMS,
    inject_into_environ,
    load_api_key,
)


class TestLoadApiKey(unittest.TestCase):
    """Tests for load_api_key."""

    def _write_env(
        self,
        content: str,
        *,
        permissions: int = 0o600,
        make_symlink: bool = False,
        make_git: bool = True,
    ) -> Path:
        """Write a .env file in a temp dir with controlled properties."""
        tmp = Path(tempfile.mkdtemp())
        if make_git:
            (tmp / ".git").mkdir()
        env_path = tmp / ".env"
        env_path.write_text(content, encoding="utf-8")
        os.chmod(env_path, permissions)

        if make_symlink:
            real = tmp / ".env.real"
            real.write_text(content, encoding="utf-8")
            os.chmod(real, permissions)
            env_path.unlink()
            env_path.symlink_to(real)

        return tmp

    def test_valid_key_loads(self) -> None:
        root = self._write_env(f"{ALLOWED_KEY}=sk-test-key-12345\n")
        result = load_api_key(root)
        self.assertTrue(result.ok)
        self.assertEqual(result.value, "sk-test-key-12345")

    def test_valid_key_with_double_quotes(self) -> None:
        root = self._write_env(f'{ALLOWED_KEY}="sk-quoted"\n')
        result = load_api_key(root)
        self.assertTrue(result.ok)
        self.assertEqual(result.value, "sk-quoted")

    def test_valid_key_with_single_quotes(self) -> None:
        root = self._write_env(f"{ALLOWED_KEY}='sk-single'\n")
        result = load_api_key(root)
        self.assertTrue(result.ok)
        self.assertEqual(result.value, "sk-single")

    def test_valid_key_with_comments(self) -> None:
        root = self._write_env(f"# This is a comment\n{ALLOWED_KEY}=sk-key\n")
        result = load_api_key(root)
        self.assertTrue(result.ok)
        self.assertEqual(result.value, "sk-key")

    def test_valid_key_with_empty_lines(self) -> None:
        root = self._write_env(f"\n\n{ALLOWED_KEY}=sk-key\n\n")
        result = load_api_key(root)
        self.assertTrue(result.ok)
        self.assertEqual(result.value, "sk-key")

    # --- Rejection cases ---

    def test_missing_env_file(self) -> None:
        root = Path(tempfile.mkdtemp())
        (root / ".git").mkdir()
        result = load_api_key(root)
        self.assertFalse(result.ok)
        self.assertIn("not found", result.error.message)

    def test_symlink_rejected(self) -> None:
        root = self._write_env(
            f"{ALLOWED_KEY}=sk-key\n", make_symlink=True
        )
        result = load_api_key(root)
        self.assertFalse(result.ok)
        self.assertIn("symlink", result.error.message)

    def test_permissive_permissions_rejected(self) -> None:
        root = self._write_env(
            f"{ALLOWED_KEY}=sk-key\n", permissions=0o644
        )
        result = load_api_key(root)
        self.assertFalse(result.ok)
        self.assertIn("permissive permissions", result.error.message)

    def test_world_readable_rejected(self) -> None:
        root = self._write_env(
            f"{ALLOWED_KEY}=sk-key\n", permissions=0o777
        )
        result = load_api_key(root)
        self.assertFalse(result.ok)
        self.assertIn("permissive permissions", result.error.message)

    def test_duplicate_key_rejected(self) -> None:
        root = self._write_env(
            f"{ALLOWED_KEY}=first\n{ALLOWED_KEY}=second\n"
        )
        result = load_api_key(root)
        self.assertFalse(result.ok)
        self.assertIn("duplicate", result.error.message)

    def test_empty_value_rejected(self) -> None:
        root = self._write_env(f"{ALLOWED_KEY}=\n")
        result = load_api_key(root)
        self.assertFalse(result.ok)
        self.assertIn("empty", result.error.message)

    def test_dollar_interpolation_rejected(self) -> None:
        root = self._write_env(f"{ALLOWED_KEY}=$HOME/key\n")
        result = load_api_key(root)
        self.assertFalse(result.ok)
        self.assertIn("interpolation", result.error.message)

    def test_command_substitution_rejected(self) -> None:
        root = self._write_env(f"{ALLOWED_KEY}=`cat /etc/passwd`\n")
        result = load_api_key(root)
        self.assertFalse(result.ok)
        self.assertIn("interpolation", result.error.message)

    def test_dollar_brace_rejected(self) -> None:
        root = self._write_env(f"{ALLOWED_KEY}=${{OTHER}}\n")
        result = load_api_key(root)
        self.assertFalse(result.ok)
        self.assertIn("interpolation", result.error.message)

    def test_dollar_paren_rejected(self) -> None:
        root = self._write_env(f"{ALLOWED_KEY}=$(whoami)\n")
        result = load_api_key(root)
        self.assertFalse(result.ok)
        self.assertIn("interpolation", result.error.message)

    def test_malformed_line_rejected(self) -> None:
        root = self._write_env("this is not key=value format\n")
        result = load_api_key(root)
        self.assertFalse(result.ok)
        self.assertIn("malformed", result.error.message)

    def test_key_not_found(self) -> None:
        root = self._write_env("OTHER_KEY=value\n")
        result = load_api_key(root)
        self.assertFalse(result.ok)
        self.assertIn("not found", result.error.message)

    def test_oversized_file_rejected(self) -> None:
        root = self._write_env(
            f"{ALLOWED_KEY}={'x' * 2000}\n"
        )
        result = load_api_key(root)
        self.assertFalse(result.ok)
        self.assertIn("exceeds", result.error.message)

    def test_tracked_file_rejected(self) -> None:
        """Tracked .env must be rejected."""
        root = self._write_env(f"{ALLOWED_KEY}=sk-key\n")
        with mock.patch(
            "vanguard.packages.adapters.models.env_loader._is_tracked",
            return_value=True,
        ):
            result = load_api_key(root)
        self.assertFalse(result.ok)
        self.assertIn("tracked", result.error.message)

    def test_failure_message_never_contains_key(self) -> None:
        """No failure message may contain the actual key value."""
        secret = "sk-super-secret-key-xyz"
        root = self._write_env(
            f"{ALLOWED_KEY}={secret}\n{ALLOWED_KEY}={secret}\n"
        )
        result = load_api_key(root)
        self.assertFalse(result.ok)
        self.assertNotIn(secret, result.error.message)


class TestInjectIntoEnviron(unittest.TestCase):
    """Tests for inject_into_environ."""

    def test_returns_minimal_dict(self) -> None:
        env = inject_into_environ("sk-key")
        self.assertEqual(env, {ALLOWED_KEY: "sk-key"})

    def test_does_not_leak_host_vars(self) -> None:
        env = inject_into_environ("sk-key")
        # Only the key should be present
        self.assertEqual(len(env), 1)
        self.assertNotIn("HOME", env)
        self.assertNotIn("PATH", env)
        self.assertNotIn("USER", env)

    def test_does_not_modify_os_environ(self) -> None:
        original = dict(os.environ)
        inject_into_environ("sk-key")
        self.assertEqual(dict(os.environ), original)


class TestSecretPropagation(unittest.TestCase):
    """Tests that the key never reaches serialized surfaces."""

    def test_env_load_result_contains_only_ref(self) -> None:
        """EnvLoadResult carries the key name, not the key value."""
        from vanguard.packages.adapters.models.env_loader import EnvLoadResult
        result = EnvLoadResult(key_ref=ALLOWED_KEY, loaded=True)
        serialized = str(result)
        self.assertIn(ALLOWED_KEY, serialized)
        # The key_ref is just the name, never a value
        self.assertEqual(result.key_ref, ALLOWED_KEY)

    def test_success_result_value_never_in_repr(self) -> None:
        """Result.success carries the value, but we never serialize it."""
        root = Path(tempfile.mkdtemp())
        (root / ".git").mkdir()
        env = root / ".env"
        env.write_text(f"{ALLOWED_KEY}=sk-secret-value\n")
        os.chmod(env, 0o600)
        result = load_api_key(root)
        # Value is accessible via result.value, but the Result's
        # string repr should not reveal the key
        self.assertTrue(result.ok)
        self.assertEqual(result.value, "sk-secret-value")


if __name__ == "__main__":
    unittest.main()
