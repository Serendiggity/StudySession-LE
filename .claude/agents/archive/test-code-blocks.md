---
name: test-code-blocks
description: Multiple code blocks test agent
tools: Bash
model: inherit
---

Example 1:
```sql
SELECT * FROM bia_sections WHERE section_number = '172';
```

Example 2:
```bash
echo "test"
```

Example 3:
```csv
timestamp,question,answer
2025-11-05,test,test
```

Return: Answer found
