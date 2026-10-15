import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReadmeDistributionTests(unittest.TestCase):
    def setUp(self):
        self.readme = (ROOT / "README.md").read_text()

    def test_readme_has_canonical_distribution_badges(self):
        self.assertIn(
            "[![skills.sh](https://skills.sh/b/bucholcm/crm-brain)]"
            "(https://skills.sh/bucholcm/crm-brain)",
            self.readme,
        )
        self.assertIn(
            "[![M8ven Score]"
            "(https://m8ven.ai/badge/mcp/bucholcm-crm-brain-3o7mfi?"
            "v=f97bc4802c14b7af8e465031bec21c09)]"
            "(https://m8ven.ai/mcp/bucholcm-crm-brain-3o7mfi?s=readme)",
            self.readme,
        )

    def test_readme_documents_skills_cli(self):
        install = self.readme.split("## Install", 1)[1].split("## The vault", 1)[0]
        self.assertIn("npx skills add bucholcm/crm-brain", install)
        self.assertIn(
            "npx skills add bucholcm/crm-brain --skill account-brief",
            install,
        )
        self.assertNotIn("M8ven", install)


if __name__ == "__main__":
    unittest.main()
