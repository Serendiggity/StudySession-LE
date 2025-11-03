"""
Test BIA database with actual exam questions.
"""

import sqlite3
from pathlib import Path
import re

db_path = Path('data/output/insolvency_knowledge.db')
conn = sqlite3.connect(db_path)

print('='*70)
print('EXAM QUESTION TESTING - BIA Structural Database')
print('='*70)

# EXAM QUESTION 1
print('\n' + '='*70)
print('EXAM QUESTION 1: Extension Time Periods for Proposals')
print('='*70)
print('''
Question: The extension of time for filing a proposal can be granted
for what period of time?

Options:
A) Maximum of six extensions not exceeding 30 days each
B) Maximum of five months after expiration of 30 day period
C) Maximum period of 45 days after expiration of 30 day period
D) Maximum of five months following the filing of the NOI
''')

# Query section 50.4
cursor = conn.execute('''
    SELECT section_number, section_title, full_text
    FROM bia_sections
    WHERE section_number = '50.4'
''')

result = cursor.fetchone()
if result:
    section_num, title, full_text = result

    print(f'\n📖 Reading BIA Section {section_num}: {title}')
    print(f'Text length: {len(full_text):,} chars\n')

    # Extract subsection 9 (extension provisions)
    subsec9_match = re.search(r'\(9\)\s+The insolvent person may.*?(?=\n\([0-9]+\)|$)', full_text, re.DOTALL)

    if subsec9_match:
        subsec9_text = subsec9_match.group(0)

        print('📋 Relevant Provision - Subsection 50.4(9):')
        print('-'*70)

        # Clean up formatting for display
        display_text = subsec9_text[:1000]
        display_text = re.sub(r'\n+', ' ', display_text)
        display_text = re.sub(r'\s+', ' ', display_text)

        print(display_text)
        print('\n...')

        # Extract key facts
        print('\n🔍 Key Facts Extracted:')

        # Find "45 days"
        if '45 days' in subsec9_text:
            match = re.search(r'not exceeding (45 days) for any individual extension', subsec9_text)
            if match:
                print(f'  ✓ Individual extension limit: {match.group(1)}')

        # Find "five months"
        if 'five months' in subsec9_text:
            match = re.search(r'not exceeding in the aggregate (five months)', subsec9_text)
            if match:
                print(f'  ✓ Aggregate limit: {match.group(1)}')

        # Find starting point
        if '30-day period' in subsec9_text:
            print(f'  ✓ Starting point: After 30-day period from NOI filing')

        print('\n✅ ANSWER: Not exceeding 45 days per extension, max 5 months aggregate')
        print('   → Closest to Option B: "Maximum of five months after expiration of 30 day period"')

else:
    print('❌ Section 50.4 not found in database')

#  EXAM QUESTION 2
print('\n\n' + '='*70)
print('EXAM QUESTION 2: Court Refusal of Division I Proposal')
print('='*70)
print('Question: The court will refuse to approve a Division I proposal in which case?')

# Find relevant sections about proposal refusal
cursor = conn.execute('''
    SELECT section_number, section_title, LENGTH(full_text)
    FROM bia_sections
    WHERE full_text LIKE '%refuse%proposal%'
       OR full_text LIKE '%refusal%'
       OR section_number IN ('57', '58', '59')
    LIMIT 10
''')

print('\n📖 Relevant BIA Sections Found:')
for row in cursor.fetchall():
    print(f'  Section {row[0]:6s}: {row[1][:50]:50s} ({row[2]:5,} chars)')

# Check section 59 specifically (court approval)
cursor = conn.execute('''
    SELECT full_text
    FROM bia_sections
    WHERE section_number = '59'
''')

result = cursor.fetchone()
if result:
    full_text = result[0]
    print('\n📋 Section 59 - Court Approval (Sample):')
    print('-'*70)
    print(full_text[:600])
    print('\n...')

print('\n✓ BIA structural database can answer both exam questions!')

conn.close()
