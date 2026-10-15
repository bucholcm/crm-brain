import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "plugins" / "crm-brain" / "skills"
EXPECTED_GROUPS = [
    {
        "title": "Get started",
        "description": "Create and configure a CRM Brain vault.",
        "skills": ["setup"],
    },
    {
        "title": "Sales workflows",
        "description": "Turn customer activity into sourced deal knowledge and follow-ups.",
        "skills": [
            "meeting-intake",
            "account-brief",
            "opp-review",
            "contact-sync",
            "vault-update",
        ],
    },
    {
        "title": "Maintenance",
        "description": "Find drift, contradictions, and stale CRM Brain records.",
        "skills": ["vault-lint"],
    },
]


class DistributionMetadataTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / "skills.sh.json").read_text())

    def test_uses_published_schema_and_grouping(self):
        self.assertEqual(
            self.config["$schema"],
            "https://skills.sh/schemas/skills.sh.schema.json",
        )
        self.assertEqual(self.config["notGrouped"], "bottom")
        self.assertEqual(self.config["groupings"], EXPECTED_GROUPS)

    def test_every_skill_is_listed_exactly_once(self):
        discovered = {
            path.parent.name for path in SKILLS_ROOT.glob("*/SKILL.md")
        }
        listed = [
            skill
            for grouping in self.config["groupings"]
            for skill in grouping["skills"]
        ]
        self.assertEqual(set(listed), discovered)
        self.assertEqual(len(listed), len(set(listed)))


if __name__ == "__main__":
    unittest.main()
