"""
Actor role normalization utility.

Handles case, plural, abbreviation, and parenthetical variations
while preserving legally significant distinctions.
"""

import re
from typing import Dict, Optional


class ActorNormalizer:
    """
    Normalizes actor role variations to canonical forms.

    Preserves legal distinctions:
    - debtor ≠ bankrupt (different legal status)
    - creditor ≠ secured creditor (different rights)
    - Trustee ≠ Licensed Insolvency Trustee (professional designation)
    """

    def __init__(self):
        """Initialize with normalization rules."""
        self._init_rules()

    def _init_rules(self):
        """Define normalization rules."""

        # Abbreviation expansion
        self.abbreviations = {
            "O.R.": "Official Receiver",
            "O. R.": "Official Receiver",
            "OSB": "Office of the Superintendent of Bankruptcy",
            "CRA": "Canada Revenue Agency",
            "CCAA": "Companies' Creditors Arrangement Act",
            "BIA": "Bankruptcy and Insolvency Act",
            "CAIRP": "Canadian Association of Insolvency and Restructuring Professionals",
        }

        # Plural to singular (preserving compounds)
        self.plural_rules = {
            "trustees": "Trustee",
            "creditors": "Creditor",
            "debtors": "Debtor",
            "bankrupts": "Bankrupt",
            "receivers": "Receiver",
            "inspectors": "Inspector",
            "liquidators": "Liquidator",
            "administrators": "Administrator",
            "landlords": "Landlord",
            "employees": "Employee",
            "farmers": "Farmer",
            "suppliers": "Supplier",
            "lenders": "Lender",
            "shareholders": "Shareholder",
            "directors": "Director",
        }

        # Legal distinctions to PRESERVE (don't merge these)
        self.preserve_distinct = {
            # Debtor vs Bankrupt
            "debtor": "Debtor",  # Financial condition - owes money
            "bankrupt": "Bankrupt",  # Legal status - declared bankrupt

            # Creditor types
            "creditor": "Creditor",
            "secured creditor": "Secured Creditor",
            "unsecured creditor": "Unsecured Creditor",
            "preferred creditor": "Preferred Creditor",

            # Trustee vs specialized
            "trustee": "Trustee",
            "Licensed Insolvency Trustee": "Licensed Insolvency Trustee",

            # Receiver types
            "receiver": "Receiver",
            "Receiver Manager": "Receiver Manager",
            "Interim Receiver": "Interim Receiver",
            "court-appointed receiver": "Court-Appointed Receiver",

            # Administrator types
            "administrator": "Administrator",
            "Administrator of a Consumer Proposal": "Administrator of a Consumer Proposal",
            "Insolvency Counsellor": "Insolvency Counsellor",
        }

        # Compound roles requiring manual review
        self.needs_review = [
            "Trustee/receiver",
            "debtor/bankrupt",
            "receiver and manager",
            "receiver-manager",
        ]

    def normalize(self, role: str) -> Dict[str, str]:
        """
        Normalize a role to canonical form.

        Args:
            role: Raw role string from extraction

        Returns:
            Dict with:
              - canonical: Normalized role name
              - original: Original input
              - confidence: high/medium/low
              - needs_review: bool
        """
        if not role:
            return {
                "canonical": None,
                "original": role,
                "confidence": "none",
                "needs_review": False
            }

        original = role
        normalized = role.strip()

        # Check if needs manual review
        if any(pattern in normalized.lower() for pattern in self.needs_review):
            return {
                "canonical": normalized,
                "original": original,
                "confidence": "low",
                "needs_review": True
            }

        # Step 1: Expand abbreviations
        if normalized in self.abbreviations:
            normalized = self.abbreviations[normalized]
            return {
                "canonical": normalized,
                "original": original,
                "confidence": "high",
                "needs_review": False
            }

        # Step 2: Remove parentheticals
        normalized = re.sub(r'\(s\)$', '', normalized)
        normalized = re.sub(r'\([^)]*\)$', '', normalized).strip()

        # Step 3: Check against preserve_distinct (case-insensitive)
        for key, canonical in self.preserve_distinct.items():
            if normalized.lower() == key.lower():
                return {
                    "canonical": canonical,
                    "original": original,
                    "confidence": "high",
                    "needs_review": False
                }

        # Step 4: Check plural rules
        lower = normalized.lower()
        if lower in self.plural_rules:
            return {
                "canonical": self.plural_rules[lower],
                "original": original,
                "confidence": "high",
                "needs_review": False
            }

        # Step 5: Case normalization (last resort)
        if normalized.isupper() or normalized.islower():
            # All caps or all lower - convert to title case
            normalized = normalized.title()

        # Medium confidence - simple transformation applied
        return {
            "canonical": normalized,
            "original": original,
            "confidence": "medium",
            "needs_review": False
        }

    def normalize_batch(self, roles: list) -> Dict:
        """
        Normalize a batch of roles.

        Returns:
            Dict with statistics and mappings
        """
        results = {}
        stats = {
            "total": len(roles),
            "high_confidence": 0,
            "medium_confidence": 0,
            "low_confidence": 0,
            "none_confidence": 0,
            "needs_review": 0,
            "unique_canonicals": set()
        }

        for role in roles:
            result = self.normalize(role)
            results[role] = result

            stats[f"{result['confidence']}_confidence"] += 1
            if result['needs_review']:
                stats['needs_review'] += 1
            if result['canonical']:
                stats['unique_canonicals'].add(result['canonical'])

        stats['unique_canonicals'] = len(stats['unique_canonicals'])

        return {
            "mappings": results,
            "stats": stats
        }


if __name__ == '__main__':
    import sqlite3
    import json

    # Test normalizer
    print("Testing Actor Normalizer...")
    print("="*70)

    normalizer = ActorNormalizer()

    # Get all unique roles from database
    conn = sqlite3.connect('data/output/insolvency_knowledge.db')
    cursor = conn.execute('SELECT DISTINCT role_raw FROM actors WHERE role_raw IS NOT NULL')
    unique_roles = [row[0] for row in cursor.fetchall()]
    conn.close()

    # Normalize all
    results = normalizer.normalize_batch(unique_roles)

    print(f"\\nNormalization Results:")
    print(f"  Total variations: {results['stats']['total']}")
    print(f"  Canonical roles: {results['stats']['unique_canonicals']}")
    print(f"  Reduction: {results['stats']['total']} → {results['stats']['unique_canonicals']} ({results['stats']['total'] / results['stats']['unique_canonicals']:.1f}x)")
    print(f"\\nConfidence breakdown:")
    print(f"  High confidence:   {results['stats']['high_confidence']:3d} ({100*results['stats']['high_confidence']/results['stats']['total']:.1f}%)")
    print(f"  Medium confidence: {results['stats']['medium_confidence']:3d} ({100*results['stats']['medium_confidence']/results['stats']['total']:.1f}%)")
    print(f"  Low confidence:    {results['stats']['low_confidence']:3d} ({100*results['stats']['low_confidence']/results['stats']['total']:.1f}%)")
    print(f"  Needs review:      {results['stats']['needs_review']:3d}")

    # Show sample mappings
    print(f"\\nSample mappings:")
    for i, (original, mapping) in enumerate(list(results['mappings'].items())[:15], 1):
        conf = mapping['confidence']
        canon = mapping['canonical']
        review = " ⚠️ REVIEW" if mapping['needs_review'] else ""
        print(f"  {i:2d}. {original:40s} → {canon}{review}")

    # Save full results
    with open('data/output/normalization_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\\n✅ Full results saved to: data/output/normalization_results.json")
