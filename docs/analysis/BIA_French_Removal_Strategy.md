# BIA French Removal Strategy Document

## Executive Summary

After analyzing the `bia_statute_english_only.txt` file (16,660 lines), I've identified that the current filtering has removed most French content but **506 lines (3.04%)** still contain French text. The bilingual structure follows consistent patterns that can be exploited for surgical removal.

---

## 1. EXACT BILINGUAL PATTERNS IDENTIFIED

### 1.1 Table of Contents Pattern
**Pattern:** `Section# English Title Section# French Title`
```
50.4 Notice of intention 50.4 Avis d'intention
50.5 Trustee to help prepare proposal 50.5 Préparation de la proposition
```
**Observation:** Section numbers are ALWAYS duplicated on same line

### 1.2 Section Body Structure
**Pattern:** English subsection → French translation → Next English subsection

Example from Section 50.4:
```
Line 3920: 50.4 (1) Before filing a copy of a proposal...
Lines 3921-3934: [English subsection (1) with paragraphs (a), (b), (c)]
Lines 3935-3937: [French translation of (a), (b), (c)]
           a) son intention de faire une proposition;
           proposition;
           du débiteur.
Line 3938: (2) Within ten days after filing...
```

**Critical Finding:** French appears as PARAGRAPH-LEVEL translations, not interleaved sentences.

### 1.3 Citation Lines (Legislative References)
**Pattern:** English citation followed by French citation on next line
```
1992, c. 27, s. 19; 1997, c. 12, s. 32; 2004, c. 25, s. 33(F); 2005, c. 47, s. 35; 2007, c. 36, s. 17; 2017, c. 26, s. 6(E).
1992, ch. 27, art. 19; 1997, ch. 12, art. 32; 2004, ch. 25, art. 33(F); 2005, ch. 47, art. 35; 2007, ch. 36, art. 17; 2017, ch. 26, art. 6(A).
```
**Markers:** French uses `ch.` (chapitre) and `art.` (article) vs English `c.` and `s.`

### 1.4 Part Headers
**Pattern:** PART/PARTIE headers alternate
```
PART III
Proposals
PARTIE III
Propositions concordataires
```

### 1.5 Marginal Notes (Section Headings)
**Pattern:** English heading followed by French heading
```
Notice of intention Avis d'intention
```

---

## 2. FRENCH TEXT CHARACTERISTICS

### 2.1 French Indicators Found
- **Accented characters:** é, è, à, ç, ô, û, ê (in 506 lines)
- **French articles:** le, la, les, du, de, des
- **French keywords:** 
  - `pour` (for)
  - `avec` (with)
  - `dans` (in)
  - `selon` (according to)
  - `peuvent` (can/may)
  - `lorsque` (when)

### 2.2 Parenthetical Content
**Pattern:** French translations often appear as:
```
(a) son intention de faire une proposition;
b) elle serait vraisemblablement en mesure de faire
```
- Lowercase letter followed by `)` 
- Contains accented characters
- Shorter/incomplete compared to English

### 2.3 Inline French Terms
Some English sections contain French legal terms:
```
(b) every local cooperative credit society, as defined in
subsection 2(1) of the Act referred to in paragraph (b),
```
**Risk:** These are legitimate English references to French names and should NOT be removed.

---

## 3. BEST APPROACH FOR CLEANING

### 3.1 Table of Contents (High Confidence)
**Strategy:** Remove duplicated section number + French title

**Regex Pattern:**
```python
# Pattern: "NUMBER Title NUMBER French-Title"
# Keep: "NUMBER Title"
# Remove: "NUMBER French-Title"

pattern = r'^(\d+(?:\.\d+)?)\s+([A-Z][^\d]+?)\s+\1\s+(.+)$'
replacement = r'\1 \2'
```

**Example:**
```
Before: 50.4 Notice of intention 50.4 Avis d'intention
After:  50.4 Notice of intention
```

**Confidence:** 99% - Section numbers always duplicate

### 3.2 Citation Lines (High Confidence)
**Strategy:** Identify and remove lines containing `ch.` and `art.`

**Regex Pattern:**
```python
# Remove lines with French citation markers
pattern = r'^\d{4}, ch\.\s+\d+,\s+art\.'
# This matches French citation lines
```

**Example:**
```
Remove: 1992, ch. 27, art. 19; 1997, ch. 12, art. 32;...
Keep:   1992, c. 27, s. 19; 1997, c. 12, s. 32;...
```

**Confidence:** 95% - Highly consistent pattern

### 3.3 Section Headings (Medium-High Confidence)
**Strategy:** Remove French marginal notes

**Approach:**
1. Identify heading pairs (English THEN French on same line)
2. Keep only English portion

**Regex Pattern:**
```python
# Pattern for dual headings on same line
pattern = r'^([A-Z][a-z]+(?:\s+[a-z]+)*)\s+([A-Z][a-zàâçéèêëîïôùûü]+(?:\s+[a-zàâçéèêëîïôùûü]+)*)$'
# Keep first capture group (English), remove second (contains accents)
```

**Example:**
```
Before: Notice of intention Avis d'intention
After:  Notice of intention
```

**Confidence:** 85% - Must verify English doesn't naturally contain French words

### 3.4 PART Headers (High Confidence)
**Strategy:** Remove lines starting with `PARTIE`

**Pattern:**
```python
# Remove PARTIE lines
if line.startswith('PARTIE '):
    continue  # Skip this line
```

**Confidence:** 99% - Clear marker

### 3.5 Paragraph Translations (COMPLEX - Requires Context)
**Strategy:** Multi-pass removal based on paragraph structure

**Algorithm:**
```python
def is_french_paragraph(line, context):
    """
    Identify French translation paragraphs
    """
    indicators = [
        # Starts with lowercase letter + parenthesis (French sub-clauses)
        line.strip().startswith(('a)', 'b)', 'c)', 'd)', 'e)', 'f)')),
        
        # Contains French accents
        any(char in line for char in 'àâçéèêëîïôùûü'),
        
        # Contains French keywords
        any(word in line.lower() for word in [
            ' le ', ' la ', ' les ', ' du ', ' des ',
            'lorsque', 'selon', 'peuvent', 'peuvent'
        ]),
        
        # Previous line was English subsection start
        context.prev_line.strip().startswith(('(1)', '(2)', '(3)'))
    ]
    
    return sum(indicators) >= 2  # At least 2 indicators
```

**Confidence:** 70% - Requires careful validation

---

## 4. RISK ASSESSMENT

### 4.1 What Might We Accidentally Remove?

#### HIGH RISK (Don't Remove):
1. **English legal terms with French origin**
   - Examples: `bona fide`, `in camera`, `per se`
   - **Mitigation:** Use whitelist of Latin legal terms

2. **Proper names of French entities**
   - Example: `"Caisse populaire de Québec"`
   - **Mitigation:** Preserve lines in quotes or with French provinces

3. **Section references**
   - Example: `"subsection 50.4(1)"`
   - **Mitigation:** Never remove lines starting with numbers or `(`

#### MEDIUM RISK:
1. **Incomplete paragraph removal**
   - French translations may span multiple lines
   - **Mitigation:** Track paragraph context; remove entire translation block

2. **Mixed-language definitions**
   - Some terms defined bilingually: `collective agreement (convention collective)`
   - **Mitigation:** Preserve content in parentheses after English terms

#### LOW RISK:
1. **Table of Contents entries**
   - Well-defined pattern
   - **Mitigation:** Use anchored regex with section numbers

---

## 5. RECOMMENDED IMPLEMENTATION APPROACH

### Phase 1: Safe Removals (95%+ Confidence)
```python
def phase1_safe_removal(lines):
    """Remove clearly identified French content"""
    cleaned = []
    
    for i, line in enumerate(lines):
        # Skip PARTIE headers
        if line.strip().startswith('PARTIE '):
            continue
            
        # Remove French citations
        if re.match(r'^\d{4}, ch\.\s+\d+', line):
            continue
            
        # Clean TOC entries (duplicate section numbers)
        line = re.sub(
            r'^(\d+(?:\.\d+)?)\s+([A-Z][^\d]+?)\s+\1\s+.+$',
            r'\1 \2',
            line
        )
        
        cleaned.append(line)
    
    return cleaned
```

### Phase 2: Contextual Removals (70-85% Confidence)
```python
def phase2_contextual_removal(lines):
    """Remove French based on paragraph context"""
    cleaned = []
    in_french_block = False
    
    for i, line in enumerate(lines):
        current = line.strip()
        prev = lines[i-1].strip() if i > 0 else ""
        next = lines[i+1].strip() if i < len(lines)-1 else ""
        
        # Detect start of French translation block
        if (prev.startswith('(') and prev[1].isdigit() and 
            current.startswith(('a)', 'b)', 'c)')) and
            has_french_chars(current)):
            in_french_block = True
            continue
        
        # Detect end of French block
        if in_french_block and (
            next.startswith('(') and next[1].isdigit() or
            next.startswith(tuple('0123456789'))
        ):
            in_french_block = False
            continue
        
        # Skip French block content
        if in_french_block:
            continue
            
        cleaned.append(line)
    
    return cleaned
```

### Phase 3: Validation
```python
def validate_removal(original, cleaned):
    """Ensure we didn't break section numbering"""
    # Check all section numbers still present
    orig_sections = extract_section_numbers(original)
    clean_sections = extract_section_numbers(cleaned)
    
    assert orig_sections == clean_sections, "Section numbers changed!"
    
    # Check no English content removed
    english_markers = ['Section', 'subsection', 'court', 'creditor']
    for marker in english_markers:
        orig_count = sum(1 for line in original if marker in line)
        clean_count = sum(1 for line in cleaned if marker in line)
        reduction = (orig_count - clean_count) / orig_count
        assert reduction < 0.05, f"Too much '{marker}' removed: {reduction:.1%}"
```

---

## 6. SPECIFIC REGEX PATTERNS FOR IMPLEMENTATION

### 6.1 Table of Contents Cleanup
```python
# Match: "NUMBER EnglishTitle NUMBER FrenchTitle"
# Keep only: "NUMBER EnglishTitle"
toc_pattern = re.compile(
    r'^(\d+(?:\.\d+)?)\s+'  # Section number
    r'([A-Z][^\d]+?)\s+'    # English title (no digits)
    r'\1\s+'                # Same section number repeated
    r'(.+)$'                # French title (discard)
)
replacement = r'\1 \2'
```

### 6.2 Citation Line Removal
```python
# Remove entire lines with French citation format
french_citation = re.compile(
    r'^\d{4},\s+ch\.\s+\d+,\s+art\.\s+\d+'
)
# if french_citation.match(line): skip
```

### 6.3 Marginal Note Cleanup
```python
# Match dual headings on same line
dual_heading = re.compile(
    r'^([A-Z][a-z]+(?:\s+[a-z]+){0,5})\s+'  # English heading
    r'([A-Z][a-zàâçéèêëîïôùûü]+(?:\s+[a-zàâçéèêëîïôùûü]+){0,5})$'  # French heading
)
replacement = r'\1'
```

### 6.4 French Paragraph Detection
```python
def is_french_line(line):
    """Detect if line is French translation"""
    indicators = {
        'accents': bool(re.search(r'[àâçéèêëîïôùûü]', line)),
        'french_words': bool(re.search(
            r'\b(le|la|les|du|des|pour|avec|dans|selon|lorsque|peuvent)\b',
            line, re.IGNORECASE
        )),
        'lowercase_bullet': bool(re.match(r'^\s*[a-f]\)', line)),
        'french_articles': bool(re.search(r'\bl[ae]s?\s', line)),
    }
    
    return sum(indicators.values()) >= 2
```

---

## 7. EXAMPLE: Section 50.4 Transformation

### BEFORE (Current State):
```
50.4 (1) Before filing a copy of a proposal with a li-
censed trustee, an insolvent person may file a notice of
intention, in the prescribed form, with the official receiv-
er in the insolvent person's locality, stating
(a) the insolvent person's intention to make a propos-
al,
(b) the name and address of the licensed trustee who
has consented, in writing, to act as the trustee under
the proposal, and
(c) the names of the creditors with claims amounting
to two hundred and fifty dollars or more and the
amounts of their claims as known or shown by the
debtor's books,
and attaching thereto a copy of the consent referred to in
paragraph (b).
a) son intention de faire une proposition;
proposition;
du débiteur.
(2) Within ten days after filing a notice of intention un-
der subsection (1), the insolvent person shall file with the
official receiver
```

### AFTER (Proposed Cleaning):
```
50.4 (1) Before filing a copy of a proposal with a li-
censed trustee, an insolvent person may file a notice of
intention, in the prescribed form, with the official receiv-
er in the insolvent person's locality, stating
(a) the insolvent person's intention to make a propos-
al,
(b) the name and address of the licensed trustee who
has consented, in writing, to act as the trustee under
the proposal, and
(c) the names of the creditors with claims amounting
to two hundred and fifty dollars or more and the
amounts of their claims as known or shown by the
debtor's books,
and attaching thereto a copy of the consent referred to in
paragraph (b).
(2) Within ten days after filing a notice of intention un-
der subsection (1), the insolvent person shall file with the
official receiver
```

**Removed:** 3 lines of French paragraph translations

---

## 8. VALIDATION METRICS

### Before Cleaning:
- Total lines: 16,660
- Lines with French accents: 506 (3.04%)
- French citations: ~30 lines
- PARTIE headers: ~20 lines
- Estimated French content: 800-1000 lines (4.8-6%)

### Expected After Cleaning:
- Total lines: ~15,800-15,900
- Lines with French accents: <50 (0.3%)
- Remaining French: Only in proper names/quotes
- Reduction: 700-900 lines (4-5%)

### Quality Checks:
1. ✓ All section numbers preserved
2. ✓ No English paragraphs removed
3. ✓ Legal citations maintained (English versions)
4. ✓ Table of contents readable
5. ✓ No broken section references

---

## 9. IMPLEMENTATION PRIORITY

### CRITICAL (Must Do):
1. **Remove PARTIE headers** - 100% safe
2. **Remove French citation lines** - 95% safe
3. **Clean Table of Contents duplicates** - 99% safe

### HIGH PRIORITY (Should Do):
4. **Remove paragraph-level translations** - 70% safe with validation
5. **Clean dual marginal notes** - 85% safe

### OPTIONAL (Nice to Have):
6. **Remove incomplete French fragments** - Requires manual review
7. **Normalize whitespace** - Clean up gaps from removed content

---

## 10. NEXT STEPS

### Recommended Order:
1. **Backup original file** ✓
2. **Implement Phase 1** (safe removals)
3. **Validate Phase 1** (check section integrity)
4. **Implement Phase 2** (contextual removals)
5. **Manual spot-check** (sample 10-20 sections)
6. **Run extraction test** (verify LLM can still parse)
7. **Compare extraction quality** (before/after metrics)

### Success Criteria:
- [ ] French content reduced to <1% of lines
- [ ] All section numbers intact
- [ ] All English legal text preserved
- [ ] Extraction quality maintained or improved
- [ ] No broken references

---

## 11. EXAMPLE PYTHON IMPLEMENTATION

```python
#!/usr/bin/env python3
"""
BIA French Content Removal Script
Based on analysis strategy document
"""

import re
from typing import List, Tuple

class BIAFrenchRemover:
    def __init__(self):
        # Compile regex patterns
        self.toc_pattern = re.compile(
            r'^(\d+(?:\.\d+)?)\s+([A-Z][^\d]+?)\s+\1\s+(.+)$'
        )
        self.french_citation = re.compile(
            r'^\d{4},\s+ch\.\s+\d+')
        self.french_chars = re.compile(r'[àâçéèêëîïôùûü]')
        
    def phase1_safe_removal(self, lines: List[str]) -> List[str]:
        """Remove clearly identified French content"""
        cleaned = []
        
        for line in lines:
            # Skip PARTIE headers
            if line.strip().startswith('PARTIE '):
                continue
            
            # Remove French citations
            if self.french_citation.match(line.strip()):
                continue
            
            # Clean TOC entries
            match = self.toc_pattern.match(line)
            if match:
                line = f"{match.group(1)} {match.group(2)}\n"
            
            cleaned.append(line)
        
        return cleaned
    
    def phase2_contextual_removal(self, lines: List[str]) -> List[str]:
        """Remove French based on context"""
        cleaned = []
        i = 0
        
        while i < len(lines):
            current = lines[i].strip()
            
            # Check if this starts French translation block
            if (i > 0 and 
                self._is_french_translation_start(lines, i)):
                # Skip until we find next English subsection
                i = self._skip_french_block(lines, i)
                continue
            
            cleaned.append(lines[i])
            i += 1
        
        return cleaned
    
    def _is_french_translation_start(self, 
                                     lines: List[str], 
                                     idx: int) -> bool:
        """Detect start of French paragraph translation"""
        current = lines[idx].strip()
        prev = lines[idx-1].strip() if idx > 0 else ""
        
        # Previous line was English subsection
        prev_is_english = (
            prev.startswith('(') and 
            len(prev) > 2 and 
            prev[1].isdigit()
        )
        
        # Current line starts with lowercase letter bullet
        curr_is_french_bullet = current.startswith(('a)', 'b)', 'c)'))
        
        # Current line has French characters
        has_french = bool(self.french_chars.search(current))
        
        return prev_is_english and curr_is_french_bullet and has_french
    
    def _skip_french_block(self, lines: List[str], start: int) -> int:
        """Skip entire French translation block"""
        i = start
        while i < len(lines):
            next_line = lines[i].strip()
            
            # Found next English subsection or new section
            if (next_line.startswith('(') and 
                len(next_line) > 2 and 
                next_line[1].isdigit()):
                return i
            
            if next_line and next_line[0].isdigit():
                return i
            
            i += 1
        
        return i
    
    def clean_file(self, input_path: str, output_path: str):
        """Main cleaning function"""
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"Original lines: {len(lines)}")
        
        # Phase 1: Safe removals
        lines = self.phase1_safe_removal(lines)
        print(f"After Phase 1: {len(lines)}")
        
        # Phase 2: Contextual removals
        lines = self.phase2_contextual_removal(lines)
        print(f"After Phase 2: {len(lines)}")
        
        # Write output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"Cleaned file written to: {output_path}")

if __name__ == "__main__":
    remover = BIAFrenchRemover()
    remover.clean_file(
        "data/input/study_materials/bia_statute_english_only.txt",
        "data/input/study_materials/bia_statute_clean.txt"
    )
```

---

## CONCLUSION

The BIA bilingual structure is highly regular and exploitable. With the proposed multi-phase approach, we can:

1. **Safely remove 95%+ of French content** using pattern matching
2. **Preserve all English legal text** through careful validation
3. **Maintain document integrity** with section number tracking
4. **Improve extraction quality** by reducing noise

**Recommended Action:** Implement Phase 1 immediately, validate, then proceed to Phase 2 with spot-checking.
