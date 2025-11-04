---
description: Extract relationships from BIA sections
allowed-tools: Bash(cd:*), Bash(python3:*)
---

Extract BIA relationships from all sections.

**Run extraction:**

```bash
cd /Users/jeffr/Local\ Project\ Repo/insolvency-knowledge && \
python3 src/extraction/relationship_extractor.py --mode all
```

**This will:**
- Process all 385 BIA sections
- Extract duty relationships (actor → procedure → deadline → consequence)
- Extract document requirements (procedure → document)
- Skip already-processed sections
- Use Gemini 2.0 Flash API
- Take ~15-30 minutes
- Cost ~$0.15-0.20

**Monitor progress:**
Check database periodically:
```sql
SELECT COUNT(*) FROM duty_relationships WHERE source_id = 2;
```

**After completion, show extraction statistics.**
