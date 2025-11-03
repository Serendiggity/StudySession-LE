# BIA Navigation Guide
## Structural Reference for Efficient AI Querying

This guide maps BIA topics to their statutory sections based on the Act's actual organization. Use this to help AI assistants navigate directly to relevant provisions without exploration.

**Note:** This is a navigation reference based on BIA structure, NOT an exam frequency analysis.

---

## BIA Structural Organization: Topic → Section Mapping

### Proposals & Notice of Intention

| Topic | BIA Section(s) | Key Content |
|-------|----------------|-------------|
| Notice of Intention (NOI) filing | 50.4(1) | Requirements for filing NOI |
| Cash flow statements | 50.4(2)-(5) | 10-day filing requirement, disclosure rules |
| **Extension time limits** | **50.4(9)** | 45 days per extension, 5 months aggregate max |
| Deemed assignment on default | 50.4(8) | Failure to file within 30 days |
| Proposal preparation | 50.5 | Trustee's role in advising |
| Interim financing | 50.6 | Court orders for DIP financing |
| Filing proposals | 62 | Filing requirements |
| Court approval | 59 | Approval criteria, refusal grounds |
| Deemed acceptance | 54, 66.18 | When proposal deemed accepted |

### Trustee Qualifications & Conduct

| Topic | BIA Section(s) | Key Content |
|-------|----------------|-------------|
| **Trustee qualification restrictions** | **13.3(1)** | Two-year lookback: director, employee, related person, auditor |
| Licensing requirements | 13-13.2 | Application process, fees |
| Conflict disclosure | 13.3(2) | When already acting as trustee/receiver for related party |
| Who can be trustee | 13.4-13.6 | Eligibility criteria |
| Appointment process | 14, 14.01 | How trustees are appointed |
| Removal | 14.04 | When trustee can be removed |
| No obligation to act | 14.06 | Trustee can decline |
| Corporate trustees | 14.08-14.09 | Majority of officers must be licensed |

### Trustee Duties & Powers

| Topic | BIA Section(s) | Key Content |
|-------|----------------|-------------|
| Security requirements | 16(1)-(2) | Trustee must provide bond/security |
| Taking possession | 16(3)-(5) | Right to enter premises, take property |
| **Estate fund deposits** | **25(1)** | Separate trust account for EACH estate |
| Funds outside Canada | 25(1.2) | Can deposit abroad with Superintendent approval |
| **Books and records** | **26** | Must keep proper records |
| **Who can inspect books** | **26(3)** | Superintendent, bankrupt, any creditor |
| Reporting to creditors | 27 | When required by inspectors/creditors/Superintendent |
| **Material adverse change reporting** | **50.4(7)(b), 50(a.1)** | Report immediately to official receiver and creditors |

### Definitions

| Topic | BIA Section(s) | Key Content |
|-------|----------------|-------------|
| **Insolvent person** | **2** | Three tests: unable to pay, ceased paying, insufficient assets |
| Bankrupt | 2 | Person who made assignment or subject to bankruptcy order |
| Bankruptcy | 2 | State of being bankrupt |
| Creditor | 2 | Person with provable claim |
| Debtor | 2 | Includes insolvent person |
| Trustee | 2 | Licensed person |
| Assignment | 2 | Filed with official receiver |
| Proposal | 2 | Defined by context |

### Bankruptcy Process

| Topic | BIA Section(s) | Key Content |
|-------|----------------|-------------|
| Acts of bankruptcy | 42 | What constitutes act of bankruptcy |
| Bankruptcy application | 43 | Who can apply, requirements |
| Assignment filing | 49 | How to make assignment |
| Stay of proceedings | 69 | Automatic stay upon bankruptcy |

### Discharge

| Topic | BIA Section(s) | Key Content |
|-------|----------------|-------------|
| Discharge application | 168-169 | Timing, requirements |
| Trustee's report on discharge | 170 | Required contents, filing timeline |
| Grounds for refusal | 170(1)(f) | Offences under ss. 198-200 |

### Receivers

| Topic | BIA Section(s) | Key Content |
|-------|----------------|-------------|
| Receiver provisions | 243-252 | Part XI - Secured Creditors and Receivers |
| Receiver duties | 246 | Notice, reporting requirements |

### Other Key Provisions

| Topic | BIA Section(s) | Key Content |
|-------|----------------|-------------|
| CCAA applicability | Study Material | Debts > $5,000,000 |
| CAIRP standards | Study Material 1.7-1.8 | Ethics, conflicts of interest, confidentiality |
| OSB Directives | Study Material 1.2 | Must be complied with |

---

## AI Assistant Optimization Prompts

### For Claude/ChatGPT System Prompts:

```markdown
When answering insolvency questions, use this efficient query strategy:

1. IDENTIFY TOPIC from question keywords:
   - "extension" / "time limit" → BIA s. 50.4(9)
   - "trustee qualification" / "related to" → BIA s. 13.3
   - "insolvent person" / "definition" → BIA s. 2
   - "discharge" / "refusal" → BIA s. 170
   - "confidential" / "disclosure" → Study Material s. 1.8.3
   - "estate funds" / "deposit" → BIA s. 25

2. QUERY DIRECTLY - don't explore:
   ```sql
   SELECT full_text FROM bia_sections WHERE section_number = '[mapped section]'
   ```

3. EXTRACT answer from specific subsection (if known):
   - Extension limits → read subsection (9)
   - Qualification restrictions → read subsection (1)(a)
   - Inspection rights → read subsection (3)

4. CITE source in answer:
   "According to BIA s. 50.4(9)..."
   "Per Study Material section 1.8.3..."

This approach:
- Skips exploration phase (saves 500-1000ms)
- Reduces context size (faster AI processing)
- Provides precise citations (better answers)
```

---

## Practical Implementation

**For YOUR studying workflow:**

When you ask a question, include context hints:
- ❌ "What are the extension limits?" (AI explores)
- ✅ "What are the extension limits? (check BIA proposals sections)" (AI direct)

**OR create a reference sheet:**
```
Quick Section Finder:
- Proposals/NOI: BIA ss. 50-66
- Trustee rules: BIA ss. 13-30
- Bankruptcy: BIA ss. 42-49, 67-101
- Discharge: BIA ss. 168-178
- Ethics/Conduct: Study Material Ch. 1
```

---

## HONEST ASSESSMENT

**Are these "better optimizations" viable?**

1. **Embeddings:** ❌ No - you're using AI assistant already, not building standalone search
2. **Caching:** ❌ No - studying means every question is novel, caching doesn't help
3. **Smart prompts:** ✅ YES - guide AI to right sections = 30-50% real speedup

**Only #3 is actually viable and valuable.**

**The database optimizations we did:** Harmless, keep them, but not impactful

**The prompt optimization:** Worth doing if you'll use AI assistant heavily

---

**Want me to create the topic mapping as a quick reference file you can share with AI assistants?** That's the ONE optimization that will actually help.