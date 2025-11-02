"""Generate canonical role mappings using Gemini AI."""

import sqlite3
import os
import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Get all unique roles from database
db_path = Path(__file__).parent.parent.parent / 'data/output/insolvency_knowledge.db'
conn = sqlite3.connect(db_path)
cursor = conn.execute('''
    SELECT role_raw, COUNT(*) as count
    FROM actors
    WHERE role_raw IS NOT NULL
    GROUP BY role_raw
    ORDER BY count DESC
''')
roles_with_counts = cursor.fetchall()
conn.close()

print(f"Generating canonical mappings for {len(roles_with_counts)} role variations...")
print("="*70)

# Create detailed prompt
prompt = f"""You are analyzing legal role variations from a Canadian insolvency law document (BIA, CCAA).

Task: Normalize {len(roles_with_counts)} role variations to canonical forms.

CRITICAL LEGAL DISTINCTIONS TO PRESERVE:
1. debtor (owes money, financial condition) ≠ bankrupt (declared bankrupt, legal status)
2. creditor ≠ secured creditor ≠ unsecured creditor ≠ preferred creditor (different legal rights)
3. Trustee (general role) ≠ Licensed Insolvency Trustee (professional designation)
4. Receiver ≠ Receiver Manager (different powers) ≠ Interim Receiver (temporary)
5. Administrator ≠ Administrator of a Consumer Proposal (specific role)

MERGE THESE SAFE VARIATIONS:
- Case variants: "Trustee" = "trustee" = "TRUSTEE" → "Trustee"
- Plurals: "trustees" = "Trustee(s)" = "creditors" → use singular
- Abbreviations: "O.R." = "O. R." → "Official Receiver", "OSB" → "Office of the Superintendent of Bankruptcy"
- Parentheticals: Remove (s) → "creditor(s)" becomes "Creditor"

COMPOUND ROLES - USE JUDGMENT:
- "receiver and manager" = "receiver-manager" → "Receiver Manager" (formal role name)
- "Trustee/receiver" → "Trustee" (likely primary role, receiver is context)
- "debtor/bankrupt" → "Debtor" (transitional state, use less specific)

Here are ALL {len(roles_with_counts)} variations with frequency (most common first):

{chr(10).join(f"{role}: {count}" for role, count in roles_with_counts)}

Provide complete JSON mapping for ALL variations above:
{{
  "Trustee": "Trustee",
  "trustee": "Trustee",
  "TRUSTEE": "Trustee",
  "trustees": "Trustee",
  ... (continue for all {len(roles_with_counts)} variations)
}}

Output ONLY valid JSON, no explanation.
"""

# Call Gemini
model = genai.GenerativeModel('gemini-2.0-flash-exp')
response = model.generate_content(prompt)

print("\nGemini Response:")
print("-"*70)
print(response.text[:1000], "..." if len(response.text) > 1000 else "")

# Save full response
output_file = Path(__file__).parent.parent.parent / 'data/output/gemini_canonical_mappings.json'
with open(output_file, 'w') as f:
    # Try to extract JSON from response
    text = response.text
    # Remove markdown code fences if present
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    f.write(text.strip())

print(f"\n✅ Canonical mappings saved to: {output_file}")
print(f"\nNext: Review the JSON file and approve/modify suggested mappings")
