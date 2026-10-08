"""The deployed artifact must come from the revision whose quality jobs passed."""
from pathlib import Path
import unittest
import yaml

WORKFLOWS = Path(__file__).resolve().parents[1] / '.github/workflows'


class ReleaseGateTests(unittest.TestCase):
    def test_deployment_requires_tests_and_links_at_the_same_revision(self):
        pages = yaml.load((WORKFLOWS / 'pages.yml').read_text(encoding='utf-8'), Loader=yaml.BaseLoader)
        jobs = pages['jobs']
        self.assertEqual({'tests', 'links'}, set(jobs['build']['needs']))
        self.assertEqual('build', jobs['deploy']['needs'])
        for name in ('build', 'deploy'):
            self.assertNotIn('if', jobs[name], 'Default success() gate must not be bypassed')
        for name in ('tests', 'links'):
            self.assertEqual(f'./.github/workflows/{name}.yml', jobs[name]['uses'])
            self.assertEqual("github.ref == 'refs/heads/main'", jobs[name]['if'])
            reusable = yaml.load((WORKFLOWS / f'{name}.yml').read_text(encoding='utf-8'), Loader=yaml.BaseLoader)
            self.assertIn('workflow_call', reusable['on'])
            self.assertIn('main', reusable['on']['push']['branches-ignore'])
        checkout = next(step for step in jobs['build']['steps'] if step.get('uses', '').startswith('actions/checkout@'))
        self.assertNotIn('ref', checkout.get('with', {}), 'Do not build a newer branch head than the tested SHA')


if __name__ == '__main__':
    unittest.main()
