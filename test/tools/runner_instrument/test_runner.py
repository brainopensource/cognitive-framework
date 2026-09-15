"""W0: measured counts and bounded process-tree termination."""

import builtins
import importlib.util
import itertools
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch, Mock

ROOT = Path(__file__).resolve().parents[3]
RUNNER = ROOT / '.agents/skills/test-runner/scripts/run_test.py'
FALSIFIER = ROOT / '.agents/techniques/tdd-falsifier/scripts/run_falsifier.py'


def load(path):
    spec = importlib.util.spec_from_file_location('w0_' + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.runner = load(RUNNER)

    def capture(self, stdout='', stderr='', code=1):
        proc = Mock(returncode=code)
        proc.communicate.return_value = (stdout, stderr)
        with patch.object(self.runner.subprocess, 'Popen', return_value=proc):
            return self.runner.run_isolated_test('fixture')

    def test_every_count_subset_and_order(self):
        keys = [('failures', 5), ('errors', 27), ('skipped', 17),
                ('expected failures', 2), ('unexpected successes', 1)]
        for size in range(1, len(keys) + 1):
            for subset in itertools.combinations(keys, size):
                for order in itertools.permutations(subset):
                    bag = dict(order)
                    line = ', '.join(f'{key}={value}' for key, value in order)
                    with self.subTest(line=line):
                        result = self.capture(stderr=f'Ran 60 tests in 0.1s\n\nFAILED ({line})\n')
                        self.assertTrue(result.get('counts_parsed'))
                        self.assertEqual(result['counts'], bag)
                        self.assertEqual(result['total_count'], 60)
                        self.assertEqual(result['failures_count'], bag.get('failures', 0))
                        self.assertEqual(result['errors_count'], bag.get('errors', 0))
                        self.assertEqual(result['skipped_count'], bag.get('skipped', 0))
                        self.assertIn('total=60', result['summary'])
                        for key, value in order:
                            self.assertIn(f'{key}={value}', result['summary'])

    def test_success_expected_failures_and_empty_collection(self):
        for total, suffix in [(0, ''), (1, ' (skipped=1)'),
                              (2, ' (expected failures=2)')]:
            with self.subTest(total=total):
                result = self.capture(stderr=f'Ran {total} tests in 0.0s\n\nOK{suffix}\n', code=0)
                self.assertTrue(result['success'])
                self.assertTrue(result.get('counts_parsed'))
                self.assertEqual(result['total_count'], total)
                self.assertEqual(result['failures_count'], 0)
                self.assertEqual(result['errors_count'], 0)

    def test_last_summary_wins_over_nested_and_literal_output(self):
        result = self.capture(stdout='Ran 9 tests in 1s\nFAILED (errors=9)\nliteral FAILED (fake\n',
                              stderr='Ran 1 test in 0.1s\n\nOK (skipped=1)\n', code=0)
        self.assertEqual(result['errors_count'], 0)
        self.assertEqual(result.get('total_count'), 1)
        self.assertEqual(result.get('skipped_count'), 1)

    def test_parse_miss_is_unknown_not_zero(self):
        for output in ('', 'literal FAILED (errors=2)', 'FAILED (nonsense)',
                       'FAILED (errors=1, errors=2)'):
            with self.subTest(output=output):
                result = self.capture(stderr=output)
                self.assertIs(result.get('counts_parsed'), False)
                self.assertIsNone(result['failures_count'])
                self.assertIsNone(result['errors_count'])
                self.assertIn('unknown', result['summary'])

    def test_blocks_do_not_cross_associate_and_ids_are_not_duplicated(self):
        sep = '=' * 70
        dash = '-' * 70
        text = (f'{sep}\nFAIL: test_a (pkg.C.test_a) (x=1)\nsubtest description\n{dash}\n'
                f'AssertionError: first\n\n{sep}\nERROR: test_b (pkg.C)\n{dash}\n'
                'Traceback (most recent call last):\n  fixture\nValueError: second\n\n'
                f'{dash}\nRan 2 tests in 0.1s\nFAILED (errors=1, failures=1)\n')
        result = self.capture(stderr=text)
        self.assertEqual(len(result['failures']), 2)
        first, second = result['failures']
        self.assertEqual(first['test'], 'pkg.C.test_a')
        self.assertEqual(second['test'], 'pkg.C.test_b')
        self.assertIn('first', first['traceback'])
        self.assertNotIn('second', first['traceback'])
        self.assertIn('second', second['traceback'])
        self.assertNotIn('Ran 2', second['traceback'])

    def test_failure_blocks_are_explicitly_inferred_without_summary(self):
        text = '=' * 70 + '\nERROR: test_a (pkg.C.test_a)\n' + '-' * 70 + '\nRuntimeError: broken\n'
        result = self.capture(stderr=text)
        self.assertIs(result.get('counts_parsed'), False)
        self.assertEqual(result['errors_count'], 1)
        self.assertIsNone(result['failures_count'])


@unittest.skipUnless(os.name == 'posix', 'process-group timeout requires POSIX')
class TimeoutTests(unittest.TestCase):
    def exercise(self, runner):
        # Finite child lifetime keeps the original broken runner's RED bounded.
        with tempfile.TemporaryDirectory() as tmp:
            group_file = Path(tmp) / 'group'
            grandchild = 'import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(2)'
            parent = ("import os,subprocess,sys,time,signal; "
                      f"p=subprocess.Popen([sys.executable,'-c',{grandchild!r}]); "
                      "signal.signal(signal.SIGTERM,lambda *args:(p.wait(),sys.exit(0))); "
                      f"open({str(group_file)!r},'w').write(str(os.getpgrp())); "
                      'p.wait()')
            command = shlex.join([sys.executable, '-c', parent])
            start = time.monotonic()
            result = runner.run_isolated_test(command, timeout=0.2)
            elapsed = time.monotonic() - start
            group = int(group_file.read_text())
            try:
                self.assertTrue(result['timed_out'])
                self.assertEqual(result['exit_code'], 124)
                self.assertLess(elapsed, 1.8)
                self.assertNotEqual(group, os.getpgrp())
                found = subprocess.run(['pgrep', '-g', str(group)], capture_output=True, text=True)
                self.assertEqual(found.returncode, 1, found.stdout)
            finally:
                if group != os.getpgrp():
                    try:
                        os.killpg(group, signal.SIGKILL)
                    except ProcessLookupError:
                        pass

    def test_timeout_kills_sleeping_grandchild(self):
        self.exercise(load(RUNNER))

    def test_falsifier_import_fallback_preserves_timeout(self):
        original_import = builtins.__import__

        def importing(name, *args, **kwargs):
            if name == 'run_test':
                raise ImportError('injected import-path failure')
            return original_import(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=importing):
            runner = load(FALSIFIER)
        self.exercise(runner)


if __name__ == '__main__':
    unittest.main()
