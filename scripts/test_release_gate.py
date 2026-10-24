"""The deployed artifact must come from the revision whose quality jobs passed."""
from pathlib import Path
import unittest
import yaml

WORKFLOWS = Path(__file__).resolve().parents[1] / '.github/workflows'


def _jobs(name):
    return yaml.load((WORKFLOWS / f'{name}.yml').read_text(encoding='utf-8'),
                     Loader=yaml.BaseLoader)['jobs']


def _step(jobs, job, prefix):
    return next(step for step in jobs[job]['steps'] if step.get('uses', '').startswith(prefix))


class ReleaseGateTests(unittest.TestCase):
    def test_deployment_requires_tests_links_and_book_at_the_same_revision(self):
        jobs = _jobs('pages')
        self.assertEqual({'tests', 'links', 'book'}, set(jobs['build']['needs']))
        self.assertEqual('build', jobs['deploy']['needs'])
        for name in ('build', 'deploy'):
            self.assertNotIn('if', jobs[name], 'Default success() gate must not be bypassed')
        for name in ('tests', 'links', 'book'):
            self.assertEqual(f'./.github/workflows/{name}.yml', jobs[name]['uses'])
            self.assertEqual("github.ref == 'refs/heads/main'", jobs[name]['if'])
            reusable = yaml.load((WORKFLOWS / f'{name}.yml').read_text(encoding='utf-8'), Loader=yaml.BaseLoader)
            self.assertIn('workflow_call', reusable['on'])
            self.assertIn('main', reusable['on']['push']['branches-ignore'])
        checkout = _step(jobs, 'build', 'actions/checkout@')
        self.assertNotIn('ref', checkout.get('with', {}), 'Do not build a newer branch head than the tested SHA')

    def test_pages_publishes_the_book_artifact_built_by_the_gated_job(self):
        jobs = _jobs('pages')
        download = _step(jobs, 'build', 'actions/download-artifact@')
        self.assertEqual('analog-circuit-book', download['with']['name'])
        self.assertEqual('analog-book/dist', download['with']['path'])
        runs = [step.get('run', '') for step in jobs['build']['steps']]
        self.assertTrue(any('scripts/publish_book.py' in run for run in runs))
        upload = _step(jobs, 'build', 'actions/upload-pages-artifact@')
        self.assertEqual('build/site', upload['with']['path'])

        book_upload = _step(_jobs('book'), 'book', 'actions/upload-artifact@')
        self.assertEqual('analog-circuit-book', book_upload['with']['name'])
        self.assertEqual('analog-book/dist/', book_upload['with']['path'])

        deploy_runs = '\n'.join(step.get('run', '') for step in jobs['deploy']['steps'])
        self.assertIn('book/analog-circuit-book.html', deploy_runs)
        self.assertIn('book/analog-circuit-book.pdf', deploy_runs)


if __name__ == '__main__':
    unittest.main()
