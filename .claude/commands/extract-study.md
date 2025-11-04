---
description: Extract relationships from study materials
allowed-tools: Bash(cd:*), Bash(python3:*)
---

Extract relationships from Insolvency Administration Study Materials.

**Run extraction:**

```bash
cd /Users/jeffr/Local\ Project\ Repo/insolvency-knowledge && \
python3 src/extraction/study_material_relationship_extractor.py
```

**This will:**
- Process 479 unique study material section contexts
- Extract workflow/duty relationships
- Extract document requirements
- Extract cross-references to BIA
- Use Gemini 2.0 Flash API
- Take ~20-40 minutes
- Cost ~$0.20-0.25

**After completion, show extraction statistics from both sources.**
