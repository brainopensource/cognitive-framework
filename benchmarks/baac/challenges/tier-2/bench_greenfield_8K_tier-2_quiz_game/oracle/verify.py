#!/usr/bin/env python3
import sys, unittest
from pathlib import Path
class TestQuiz(unittest.TestCase):
    def test_quiz(self):
        sys.path.insert(0, str(Path(sys.argv[-1] if len(sys.argv) > 1 and sys.argv[-2] == '--workspace' else '.').resolve() / 'src'))
        from quiz_engine import Question, QuizEngine
        q = [Question(id='1', prompt='2+2?', options=['3','4'], correct_choice='4', points=10)]
        eng = QuizEngine(q)
        self.assertFalse(eng.is_finished())
        res = eng.submit_answer('4')
        self.assertTrue(res['correct'])
        self.assertTrue(eng.is_finished())
if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestQuiz)
    res = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if res.wasSuccessful() else 1)
