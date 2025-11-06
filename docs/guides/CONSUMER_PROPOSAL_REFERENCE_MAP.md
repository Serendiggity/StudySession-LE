# Consumer Proposal - Complete Reference Map

**All BIA Sections, Directives, and Forms - How They Connect**

---

## Master Relationship Diagram

```mermaid
graph TB
    subgraph Eligibility["ELIGIBILITY"]
        S66_11["§66.11-66.12<br/>WHO CAN FILE<br/>Natural person<br/>Debt ≤$250k"]
        D6R7["Directive 6R7<br/>ASSESSMENT<br/>Financial evaluation"]
        D2R["Directive 2R<br/>JOINT FILING<br/>Couples/partners"]

        S66_11 -.->|requires| D6R7
        S66_11 -.->|if applicable| D2R
    end

    subgraph Filing["FILING STAGE"]
        F47["Form 47<br/>PROPOSAL<br/>Terms & conditions"]
        F65["Form 65<br/>STATEMENT OF AFFAIRS<br/>+ Budget"]
        F79["Form 79<br/>ESTATE SUMMARY<br/>Overview"]
        S50_3["§50(3)<br/>INSPECTORS APPROVAL<br/>if already bankrupt"]

        F47 --> FileOR[File with<br/>Official Receiver]
        F65 --> FileOR
        F79 --> FileOR
        S50_3 -.->|if bankrupt| FileOR
    end

    subgraph StayProtection["STAY OF PROCEEDINGS"]
        S69_2["§69.2<br/>STAY BEGINS<br/>Immediate on filing"]
        S69_2_end["STAY ENDS when:<br/>- Withdrawn<br/>- Refused<br/>- Annulled<br/>- Admin discharged"]

        S69_2 --> Protection["🛡️ PROTECTION:<br/>- No lawsuits<br/>- No garnishment<br/>- No collection calls"]
        Protection --> S69_2_end
    end

    subgraph AdminActions["ADMINISTRATOR ACTIONS (Days 1-10)"]
        F51["Form 51<br/>ADMINISTRATOR REPORT<br/>Fairness opinion"]
        F31["Form 31<br/>PROOF OF CLAIM<br/>Blank form"]
        F37_1["Form 37.1<br/>VOTING LETTER<br/>Vote without attending"]
        F49["Form 49<br/>NOTICE<br/>Meeting info"]
        S66_14["§66.14(b)<br/>SEND TO CREDITORS<br/>Within 10 days"]

        F51 --> S66_14
        F31 --> S66_14
        F37_1 --> S66_14
        F49 --> S66_14
    end

    subgraph Voting["VOTING PROCESS (Days 11-45)"]
        S66_15["§66.15<br/>MEETING IF REQUESTED<br/>≥25% of claims"]
        D22R4["Directive 22R4<br/>QUORUM & VOTING<br/>Procedures"]
        S66_18["§66.18<br/>DEEMED ACCEPTED<br/>After 45 days"]
        S54_3["§54(3)<br/>RELATED CREDITORS<br/>Can vote AGAINST only"]

        S66_15 -.->|procedures| D22R4
        S66_15 -->|if <25% request| S66_18
        S66_15 -->|applies| S54_3
    end

    subgraph CourtApproval["COURT APPROVAL (Days 46-60)"]
        S66_22["§66.22<br/>DEEMED APPROVED<br/>After 15 days"]
        S66_23["§66.23<br/>IF HEARING REQUESTED<br/>Procedures"]

        S66_22 -.->|unless requested| S66_23
    end

    subgraph StatutoryTerms["REQUIRED TERMS IN PROPOSAL"]
        S66_12_5["§66.12(5-6)<br/>MANDATORY TERMS"]
        S60_1["§60(1)<br/>PRIORITY PAYMENTS<br/>Preferred claims first"]
        S136["§136<br/>PRIORITY SCHEME<br/>Order of payment"]
        S60_1_1["§60(1.1)<br/>CROWN TRUST AMOUNTS<br/>6 months"]
        MaxTerm["MAX 5 YEARS<br/>§66.12(6)"]

        S66_12_5 --> S60_1
        S60_1 --> S136
        S60_1 --> S60_1_1
        S66_12_5 --> MaxTerm
    end

    subgraph Counselling["COUNSELLING"]
        S66_13["§66.13(2)(b)<br/>MANDATORY<br/>2 sessions"]
        D1R8["Directive 1R8<br/>COUNSELLING DETAILS<br/>Timing & topics"]
        Session1["SESSION 1:<br/>Days 10-90"]
        Session2["SESSION 2:<br/>+30 days after S1"]

        S66_13 --> D1R8
        D1R8 --> Session1
        Session1 --> Session2
    end

    subgraph Performance["PERFORMANCE PERIOD"]
        Payments["Debtor makes<br/>periodic payments"]
        Dividends["Administrator pays<br/>dividends to creditors<br/>§60(2)"]
        S66_29["§66.29<br/>CERTIFICATE FILING<br/>Optional - for land"]

        Payments --> Dividends
        Dividends -.->|optional| S66_29
    end

    subgraph Completion["COMPLETION"]
        S66_38["§66.38<br/>CERTIFICATE OF<br/>FULL PERFORMANCE"]
        F46["Form 46<br/>CERTIFICATE<br/>Issued by admin"]
        S66_38_2["§66.38(2)<br/>NO CERT if no<br/>counselling"]
        S173["§173<br/>SURVIVING DEBTS<br/>Not discharged"]

        S66_38 --> F46
        S66_38 -.->|unless| S66_38_2
        F46 --> Discharge["DISCHARGE<br/>Debts forgiven"]
        Discharge -.->|except| S173
    end

    subgraph Default["DEFAULT & ANNULMENT"]
        S66_31["§66.31<br/>DEEMED ANNULLED<br/>3 months default"]
        S66_31_5["§66.31(5)<br/>AUTO REVIVAL<br/>If default cured"]
        S66_3["§66.3<br/>COURT ANNULMENT<br/>Ineligible/fraud/injustice"]
        S66_35["§66.35<br/>CANNOT REFILE<br/>6 months waiting"]

        S66_31 -.->|can trigger| S66_31_5
        S66_3 --> S66_35
        S66_31 --> S66_35
    end

    subgraph AdminDischarge["ADMINISTRATOR DISCHARGE"]
        S66_39["§66.39<br/>ADMIN DISCHARGE<br/>3 months after notice"]
        F14["Form 14<br/>FINAL STATEMENT<br/>Receipts & disbursements"]
        F16["Form 16<br/>DISCHARGE NOTICE"]

        F14 --> F16
        F16 --> S66_39
    end

    %% Connect the stages
    Eligibility --> Filing
    Filing --> StayProtection
    StayProtection --> AdminActions
    AdminActions --> Voting
    Voting --> CourtApproval
    CourtApproval --> StatutoryTerms
    StatutoryTerms --> Counselling
    Counselling --> Performance
    Performance --> Completion
    Completion --> AdminDischarge

    Performance -.->|if default| Default
    Default -.->|if revived| Performance

    style S69_2 fill:#90EE90
    style S66_18 fill:#87CEEB
    style S66_22 fill:#87CEEB
    style S66_38 fill:#FFD700
    style S66_31 fill:#FFB6C1
```

---

## Detailed Section-by-Section Map

### Pre-Filing & Eligibility

```mermaid
graph LR
    subgraph Who["WHO CAN FILE?"]
        S66_11["§66.11<br/>Consumer debtor definition"]
        S66_12["§66.12<br/>Natural person<br/>≤$250k debt"]
        S66_12_1_1["§66.12(1.1)<br/>Joint filing allowed"]
    end

    subgraph Assessment["ASSESSMENT"]
        D6R7a["Directive 6R7<br/>Financial evaluation<br/>Viable proposal?"]
        D2Ra["Directive 2R<br/>Joint filing criteria<br/>Substantially same debts"]
    end

    S66_11 --> S66_12
    S66_12 -.-> D6R7a
    S66_12_1_1 -.-> D2Ra

    D6R7a --> Decision{Administrator<br/>recommendation}
    D2Ra --> Decision

    Decision -->|Viable| Proceed[Proceed to filing]
    Decision -->|Not viable| Alternative[Consider Division I<br/>or bankruptcy]
```

### Filing Documents & Forms

```mermaid
graph TB
    subgraph FilingDocs["FILING DOCUMENTS"]
        direction TB
        Form47["📄 FORM 47<br/>The Proposal<br/>- Payment terms<br/>- Dividend method<br/>- Duration ≤5 years"]

        Form65["📄 FORM 65<br/>Statement of Affairs<br/>- Assets<br/>- Liabilities<br/>- Income<br/>- Expenses<br/>- BUDGET (not cash flow)"]

        Form79["📄 FORM 79<br/>Estate Summary<br/>- Overview<br/>- Key data"]

        Assess["📄 ASSESSMENT<br/>Directive 6R7<br/>- Administrator opinion<br/>- Viability"]

        InspApp["📄 INSPECTORS APPROVAL<br/>§50(3)<br/>Only if already bankrupt"]
    end

    subgraph Requirements["PROPOSAL MUST INCLUDE (§66.12)"]
        Req1["Priority payments §60(1)<br/>Per §136 scheme"]
        Req2["Administrator fees<br/>Tariff-based"]
        Req3["Counselling fees<br/>Directive 1R8"]
        Req4["Distribution method<br/>How creditors get paid"]
        Req5["Term ≤ 5 years<br/>§66.12(6)"]
    end

    Form47 -.->|must include| Req1
    Form47 -.->|must include| Req2
    Form47 -.->|must include| Req3
    Form47 -.->|must include| Req4
    Form47 -.->|must include| Req5

    Form47 --> Submit[Submit to<br/>Official Receiver]
    Form65 --> Submit
    Form79 --> Submit
    Assess --> Submit
    InspApp -.->|if bankrupt| Submit

    Submit --> S69_2["§69.2<br/>STAY BEGINS"]

    style S69_2 fill:#90EE90
```

### Administrator's 10-Day Duties

```mermaid
graph TD
    Filed[Proposal Filed<br/>Day 0] --> Prep["Administrator prepares<br/>within 10 days"]

    Prep --> Report["📄 FORM 51<br/>Administrator's Report"]

    Report --> Content["Report Contents:<br/>✓ Investigation results<br/>✓ Opinion (fair & reasonable?)<br/>✓ Condensed financials<br/>✓ List creditors >$250"]

    Content --> SendReport["Send Form 51 to:<br/>1. Official Receiver<br/>2. All creditors"]

    Prep --> Package["📦 NOTICE PACKAGE<br/>§66.14(b)"]

    Package --> P1["📄 Form 31<br/>Blank proof of claim"]
    Package --> P2["📄 Form 37.1<br/>Voting letter"]
    Package --> P3["📄 Form 49<br/>Explanatory notice"]
    Package --> P4["📄 Copy of proposal"]
    Package --> P5["📄 Copy of Form 51 report"]

    P1 --> SendAll["Send to EVERY<br/>known creditor"]
    P2 --> SendAll
    P3 --> SendAll
    P4 --> SendAll
    P5 --> SendAll

    SendAll --> Explain["Form 49 explains:<br/>✓ Meeting only if requested<br/>✓ Court review only if requested<br/>✓ Otherwise deemed accepted/approved"]

    style Report fill:#FFE4B5
    style Package fill:#87CEEB
```

### Voting & Meeting Process

```mermaid
flowchart TD
    Start[45-Day Period Begins<br/>Day 1] --> Creditors[Creditors receive<br/>notice package]

    Creditors --> Options["Creditor Options:"]

    Options --> Opt1["1. Do nothing<br/>(proposal deemed accepted)"]
    Options --> Opt2["2. File proof of claim<br/>Form 31"]
    Options --> Opt3["3. Request meeting<br/>(if ≥25% join request)"]

    Opt2 --> Vote["Can vote via:<br/>- Voting letter Form 37.1<br/>- Attend in person<br/>- Send proxy"]

    Opt3 --> Check25{Do ≥25% of<br/>proven claims<br/>request meeting?}

    Check25 -->|NO| Day45A[Day 45:<br/>DEEMED ACCEPTED<br/>§66.18]
    Check25 -->|YES| MeetingHeld["Meeting held<br/>§66.15"]

    MeetingHeld --> ChairCheck["Chair checks:<br/>Directive 22R4"]

    ChairCheck --> Quorum{Quorum?<br/>≥1 creditor with<br/>proven claim present}

    Quorum -->|NO| Day45A[DEEMED ACCEPTED<br/>Dir 22R4]
    Quorum -->|YES| VoteProcess["VOTE PROCESS"]

    VoteProcess --> Count["Count votes:<br/>- In person<br/>- By proxy<br/>- Voting letters<br/>Simple majority §66.15"]

    Count --> Result{Result?}

    Result -->|>50% YES| Day45A
    Result -->|≤50% YES| Refused[REFUSED]

    Day45A --> Court15["15-Day Period<br/>Days 46-60"]

    Court15 --> CourtReq{OR or interested<br/>party requests<br/>court review?}

    CourtReq -->|NO| Day60[Day 60:<br/>DEEMED APPROVED<br/>§66.22]
    CourtReq -->|YES| Hearing["Court Hearing<br/>§66.23"]

    Hearing --> HearDocs["Administrator files:<br/>- Report on proposal<br/>- Report on conduct<br/>15 days notice to:<br/>• Debtor<br/>• Proven creditors<br/>• OR"]

    HearDocs --> CourtDec{Court decision}
    CourtDec -->|Approve| Day60
    CourtDec -->|Refuse| Refused

    Day60 --> Binding["✅ PROPOSAL BINDING<br/>§62(2) applies"]

    Refused --> NotBankrupt["NOT auto bankruptcy<br/>(unless already bankrupt)"]

    style Day45A fill:#87CEEB
    style Day60 fill:#90EE90
    style Refused fill:#FFB6C1
```

### Statutory Terms & Priority Payments

```mermaid
graph TD
    Proposal["Consumer Proposal<br/>§66.12(5-6)"] --> Term1["TERM 1:<br/>Priority Payments"]
    Proposal --> Term2["TERM 2:<br/>Fees"]
    Proposal --> Term3["TERM 3:<br/>Distribution Method"]
    Proposal --> Term4["TERM 4:<br/>Max 5 Years"]

    Term1 --> S60_1["§60(1)<br/>Must respect priorities"]
    S60_1 --> S136["§136<br/>Priority Scheme"]

    S136 --> Priority["PRIORITY ORDER:"]
    Priority --> Pr1["1. Admin fees §136(b)(ii)"]
    Priority --> Pr2["2. Levy §136(c)"]
    Priority --> Pr3["3. Wages §136(d)<br/>If employer"]
    Priority --> Pr4["4. Crown trust amounts<br/>§60(1.1)<br/>Within 6 months"]
    Priority --> Pr5["5. Municipal taxes §136(e)"]
    Priority --> Pr6["6. Other preferred §136"]
    Priority --> Pr7["7. Ordinary unsecured<br/>Pro-rata"]

    Term2 --> Fees["Administrator fees<br/>+ Counselling fees"]
    Fees -.->|tariff-based| S66_39["§66.39<br/>No taxation unless<br/>OSB requests"]

    Term3 --> Method["e.g., $500/month<br/>for 48 months"]

    Term4 --> Max["Cannot exceed<br/>60 months"]

    style Pr1 fill:#FFB6C1
    style Pr2 fill:#FFB6C1
    style Pr3 fill:#FFE4B5
    style Pr4 fill:#FFE4B5
    style Pr7 fill:#90EE90
```

### Counselling Requirements

```mermaid
graph TD
    Approved["Proposal Approved<br/>Day 60+"] --> Mandatory["§66.13(2)(b)<br/>COUNSELLING MANDATORY"]

    Mandatory --> D1R8["Directive 1R8<br/>Counselling Details"]

    D1R8 --> S1Window["SESSION 1 WINDOW:<br/>Days 10-90 from filing"]
    S1Window --> S1["First Session"]

    S1 --> Topics1["Topics:<br/>- Budgeting<br/>- Financial goals<br/>- Spending habits<br/>- Credit use"]

    Topics1 --> Wait["Wait ≥30 days"]

    Wait --> S2["Second Session<br/>Before certificate"]

    S2 --> Topics2["Topics:<br/>- Progress review<br/>- Budget refinement<br/>- Credit rebuilding<br/>- Future planning"]

    Topics2 --> Special{Non-budgetary<br/>issues?}

    Special -->|YES| Refer["Refer to:<br/>- Gambling counselling<br/>- Substance abuse<br/>- Family services"]
    Special -->|NO| Complete["✅ Counselling<br/>complete"]
    Refer --> Complete

    Complete --> Cert["Eligible for<br/>certificate"]

    Mandatory -.->|if refused| S66_38_2["§66.38(2)<br/>NO CERTIFICATE<br/>if counselling neglected"]

    style S1 fill:#FFE4B5
    style S2 fill:#FFE4B5
    style S66_38_2 fill:#FFB6C1
    style Complete fill:#90EE90
```

### Certificate & Discharge

```mermaid
graph LR
    subgraph Completion["PROPOSAL COMPLETION"]
        AllPaid{All payments<br/>completed?}
        AllCounsel{Both counselling<br/>sessions done?}

        AllPaid -->|NO| KeepPaying[Continue<br/>performing...]
        AllPaid -->|YES| AllCounsel

        AllCounsel -->|NO| NoCert["❌ NO CERTIFICATE<br/>§66.38(2)"]
        AllCounsel -->|YES| IssueCert
    end

    IssueCert["Administrator issues<br/>§66.38"] --> F46["📄 FORM 46<br/>Certificate of<br/>Full Performance"]

    F46 --> Send1["Send to:<br/>✓ Debtor<br/>✓ Official Receiver"]

    Send1 --> Effect["EFFECT:<br/>Debts discharged"]

    Effect --> S173Check["§173 Check:<br/>Some debts survive"]

    S173Check --> Survives["SURVIVE:<br/>- Student loans <7 years<br/>- Fraud debts<br/>- Fines<br/>- Alimony/support<br/>- Misrepresentation"]

    Survives --> Unless["UNLESS:<br/>Proposal explicitly<br/>provided for discharge<br/>AND creditor voted YES"]

    Effect --> Credit["Credit Bureau:<br/>R7 rating<br/>3 years from completion"]

    style IssueCert fill:#FFD700
    style Effect fill:#90EE90
    style NoCert fill:#FFB6C1
```

### Default & Annulment Process

```mermaid
flowchart TD
    subgraph DeemedAnnulment["DEEMED ANNULMENT (Automatic)"]
        Miss["Debtor misses<br/>payment"] --> Month1["Month 1 in default"]
        Month1 --> Month2["Month 2 in default"]
        Month2 --> Month3["Month 3 in default"]
        Month3 --> S66_31["§66.31<br/>DEEMED ANNULLED"]

        Month1 -.->|if paid| Cured1["✅ Cured"]
        Month2 -.->|if paid| Cured2["✅ Cured"]
        Month3 -.->|if paid| S66_31_5["§66.31(5)<br/>AUTO REVIVAL!"]
    end

    subgraph CourtAnnulment["COURT ANNULMENT"]
        S66_3a["§66.3(1)(a)<br/>Not eligible when filed"]
        S66_3b["§66.3(1)(b)<br/>Cannot continue<br/>without injustice/delay"]
        S66_3c["§66.3(1)(c)<br/>Approval by fraud"]
        S66_3_3["§66.3(3)<br/>Debtor convicted<br/>of BIA offense"]
    end

    subgraph Effects["EFFECTS OF ANNULMENT"]
        S66_3_2["§66.3(2)<br/>Valid acts remain valid"]
        S66_3_4["§66.3(4)<br/>Admin notifies<br/>creditors + OR"]
        S66_3_5["§66.3(5)<br/>If bankrupt:<br/>deemed assignment"]
        S66_35["§66.35<br/>Cannot refile for<br/>6 MONTHS"]
        S66_36["§66.36<br/>Cannot amend for<br/>6 MONTHS"]
    end

    S66_31 --> Effects
    S66_3a --> Effects
    S66_3b --> Effects
    S66_3c --> Effects
    S66_3_3 --> Effects

    style S66_31 fill:#FFB6C1
    style S66_31_5 fill:#90EE90
    style S66_3_5 fill:#FFB6C1
```

### Administrator Discharge Process

```mermaid
sequenceDiagram
    participant D as Debtor
    participant A as Administrator
    participant C as Creditors
    participant OSB as OSB
    participant OR as Official Receiver

    Note over D,A: Proposal completed

    A->>D: Issue Certificate (Form 46)
    A->>OR: Send Certificate

    Note over A: Prepare final accounting

    A->>A: Prepare Form 14<br/>Final Statement of<br/>Receipts & Disbursements

    A->>OSB: Send Form 14 for comment

    OSB->>A: Letter of comment

    A->>C: Send Form 16<br/>Notice of Deemed Taxation<br/>+ Form 14 + Dividend sheet
    A->>OR: Copy of notice

    Note over C: 30-day objection period

    alt No objections in 30 days
        Note over A: Wait 3 months from notice
        A->>A: Deemed discharged §66.39
    else Objection filed
        C->>OSB: File objection
        OSB->>A: Resolve or court hearing
    end

    Note over A: Administrator discharged!
```

---

## Complete Forms Reference

### By Stage

#### Stage 1: Pre-Filing/Assessment
- **Directive 6R7** - Assessment of Individual Debtor
- **Directive 2R** - Joint Filing (if applicable)

#### Stage 2: Filing
- **Form 47** - Consumer Proposal
- **Form 65** - Statement of Affairs (with budget)
- **Form 79** - Estate Summary Information
- **§50(3)** - Inspectors' approval (if already bankrupt)

#### Stage 3: Notice to Creditors (Within 10 days)
- **Form 51** - Administrator's Report to Creditors
- **Form 31** - Proof of Claim (blank)
- **Form 37.1** - Voting Letter
- **Form 49** - Notice (explains process)

#### Stage 4: Meeting (If held)
- **Directive 22R4** - Quorum and voting procedures
- **§54(3)** - Related creditors (vote against only)

#### Stage 5: Court Review (If requested)
- **§66.23** - Hearing procedures
- **§66.22** - Deemed approval (if not requested)

#### Stage 6: Performance
- **Directive 1R8** - Counselling (2 sessions)
- **§66.12(6)** - 5-year maximum term

#### Stage 7: Completion
- **Form 46** - Certificate of Full Performance
- **§66.38** - Certificate issuance

#### Stage 8: Administrator Discharge
- **Form 14** - Final Statement of Receipts & Disbursements
- **Form 16** - Notice of Deemed Taxation & Discharge
- **§66.39** - Administrator discharge (3 months)

---

## Section Number Quick Finder

### Division II Core Sections (§66.11 - §66.4)

```
ELIGIBILITY & FILING:
├─ §66.11 - Consumer debtor definition
├─ §66.12 - Who can file, debt limits, joint filing
├─ §66.13 - Counselling requirement
└─ §66.14 - Administrator duties (notice)

MEETING & VOTING:
├─ §66.15 - Meeting requirement (≥25%)
├─ §66.16 - (Reserved)
├─ §66.17 - (Reserved)
├─ §66.18 - Deemed acceptance (45 days)
└─ §66.19 - Amendment at meeting

COURT APPROVAL:
├─ §66.21 - (Reserved)
├─ §66.22 - Deemed court approval (15 days)
└─ §66.23 - Court hearing procedures (if requested)

PERFORMANCE & COMPLETION:
├─ §66.28 - Performance obligations
├─ §66.29 - Certificate filing (optional - for land)
└─ §66.38 - Certificate of Full Performance

DEFAULT & ANNULMENT:
├─ §66.3 - Court annulment
├─ §66.31 - Deemed annulment (3 months default)
├─ §66.31(5) - Automatic revival
├─ §66.35 - Cannot refile (6 months)
└─ §66.36 - Cannot amend (6 months)

ADMINISTRATOR DISCHARGE:
└─ §66.39 - Deemed discharge (3 months)
```

### Division I Sections That Apply to Division II

```
THESE SECTIONS APPLY (via §66(1)):
├─ §50(3) - Inspectors' approval (if bankrupt)
├─ §54(3) - Related creditors (vote against only)
├─ §60(1) - Priority payment requirement
├─ §60(1.1) - Crown trust amounts
├─ §60(2) - All payments through administrator
├─ §62(2) - Binding effect when approved
├─ §69.2 - Stay of proceedings
└─ §173 - Debts that survive discharge
```

---

## Directive Quick Reference

### Directive 1R8: Counselling in Insolvency Matters

**Purpose:** Mandatory financial counselling to help debtors avoid future insolvency

**Requirements:**
- **2 sessions** required
- **Session 1:** Days 10-90 from filing
- **Session 2:** ≥30 days after Session 1, before certificate
- **Topics:** Budgeting, financial goals, spending habits, responsible credit use
- **Special needs:** Identify gambling, substance abuse, family issues → refer to specialists
- **Consequence:** No counselling = NO certificate §66.38(2)

---

### Directive 2R: Joint Filing

**Purpose:** Allow couples/partners to file together when debts overlap

**Requirements:**
- Debts must be "substantially the same"
- Must have "financial relationship"
- Administrator must determine it's in best interest of debtors AND creditors

**Benefits:**
- One administration (not two)
- Same admin fee (not doubled)
- Counselling max 2× cost (not 2× full)

**Can separate later** if circumstances change

---

### Directive 6R7: Assessment of Individual Debtor

**Purpose:** Administrator evaluates if proposal is viable before filing

**Assessment includes:**
- Financial situation analysis
- Debt load review ($250k limit check)
- Income/expense evaluation
- Viability of proposed repayment
- Whether joint proposal appropriate
- Recommendation: File or explore alternatives

---

### Directive 22R4: Proofs of Claim, Proxies, Quorums and Voting

**Purpose:** Rules for creditor meetings and voting

**Key Rules:**

**Quorum:**
- ≥1 creditor with proven claim (filed before meeting)
- Voting letters count toward quorum
- Can attend electronically
- **If no quorum in consumer proposal:** Deemed accepted!

**Proxies:**
- Can be letter or electronic
- Filing before meeting NOT required (unlike proofs of claim)
- Blank proxy = trustee can vote
- No corporate seal needed (unless bylaws require)

**Voting:**
- $1 = 1 vote
- Simple majority in consumer proposals
- Only votes cast are counted (abstentions ignored)

---

## Complete Process Map (All Elements Connected)

```mermaid
graph TB
    subgraph Phase1["PHASE 1: ELIGIBILITY & ASSESSMENT"]
        E1["§66.11-66.12<br/>Eligibility test"]
        E2["Directive 6R7<br/>Assessment"]
        E3["Directive 2R<br/>Joint filing?"]
    end

    subgraph Phase2["PHASE 2: DOCUMENTATION"]
        D1["Form 47 - Proposal<br/>Must include §66.12(5-6) terms"]
        D2["Form 65 - Statement of Affairs<br/>+ Budget"]
        D3["Form 79 - Estate Summary"]
        D4["§50(3) Approval<br/>if bankrupt"]
    end

    subgraph Phase3["PHASE 3: FILING"]
        F1["File with Official Receiver"] --> F2["§69.2 Stay begins<br/>IMMEDIATELY"]
    end

    subgraph Phase4["PHASE 4: NOTIFICATION (10 days)"]
        N1["Form 51<br/>Admin report"]
        N2["Forms 31, 37.1, 49<br/>Notice package"]
        N3["§66.14(b)<br/>Send to all creditors"]
    end

    subgraph Phase5["PHASE 5: CREDITOR RESPONSE (45 days)"]
        C1["Creditors file<br/>proofs of claim"]
        C2["Request meeting?<br/>§66.15 if ≥25%"]
        C3["§66.18<br/>Deemed accepted<br/>Day 45"]
    end

    subgraph Phase6["PHASE 6: MEETING (If applicable)"]
        M1["Dir 22R4<br/>Quorum check"]
        M2["Vote: Simple majority<br/>§54(3) related=against only"]
        M3["Accepted or Refused"]
    end

    subgraph Phase7["PHASE 7: COURT APPROVAL (15 days)"]
        CA1["§66.22<br/>Deemed approved<br/>Day 60"]
        CA2["§66.23<br/>Hearing if requested"]
    end

    subgraph Phase8["PHASE 8: PERFORMANCE (≤5 years)"]
        P1["Directive 1R8<br/>2 counselling sessions"]
        P2["§60(2)<br/>Payments to admin"]
        P3["Admin pays dividends<br/>to creditors"]
        P4["§66.12(6)<br/>Max 5 years"]
    end

    subgraph Phase9["PHASE 9: COMPLETION"]
        CP1["§66.38<br/>Admin issues certificate"]
        CP2["Form 46<br/>To debtor + OR"]
        CP3["Discharge<br/>except §173 debts"]
    end

    subgraph Phase10["PHASE 10: ADMIN DISCHARGE"]
        AD1["Form 14<br/>Final statement"]
        AD2["Form 16<br/>Deemed taxation notice"]
        AD3["§66.39<br/>Deemed discharged<br/>3 months"]
    end

    subgraph Default["IF DEFAULT"]
        Def1["§66.31<br/>3 months = deemed annulled"]
        Def2["§66.31(5)<br/>Can revive if cured"]
        Def3["§66.3<br/>Court annulment"]
        Def4["§66.35-36<br/>6 month waiting"]
    end

    Phase1 --> Phase2 --> Phase3 --> Phase4 --> Phase5
    Phase5 --> Phase6 --> Phase7 --> Phase8 --> Phase9 --> Phase10
    Phase8 -.->|if default| Default
    Default -.->|if revived| Phase8

    style F2 fill:#90EE90
    style C3 fill:#87CEEB
    style CA1 fill:#87CEEB
    style CP1 fill:#FFD700
    style Def1 fill:#FFB6C1
```

---

## Form Connections Map

```mermaid
graph TD
    subgraph Input["FORMS DEBTOR PROVIDES"]
        F47i[Form 47<br/>Proposal]
        F65i[Form 65<br/>Statement of Affairs]
        F79i[Form 79<br/>Estate Summary]
    end

    subgraph AdminCreates["FORMS ADMINISTRATOR CREATES"]
        F51a[Form 51<br/>Report to Creditors]
        F46a[Form 46<br/>Certificate Full Performance]
        F14a[Form 14<br/>Final Statement R&D]
        F16a[Form 16<br/>Discharge Notice]
    end

    subgraph CreditorForms["FORMS CREDITORS USE"]
        F31c[Form 31<br/>Proof of Claim]
        F37c[Form 37.1<br/>Voting Letter]
    end

    subgraph Notices["NOTICES/INFO"]
        F49n[Form 49<br/>Explanatory Notice]
    end

    F47i --> OR[Official Receiver]
    F65i --> OR
    F79i --> OR

    OR --> F51a
    F51a --> AllCred[Sent to ALL<br/>creditors]
    F49n --> AllCred

    AllCred --> F31c
    AllCred --> F37c

    F31c --> Admin[Administrator<br/>receives]
    F37c --> Admin

    Admin --> F46a
    F46a --> Debtor[To Debtor + OR]

    Admin --> F14a
    F14a --> F16a
    F16a --> AllCred2[To proven<br/>creditors]

    style OR fill:#87CEEB
    style Admin fill:#FFE4B5
    style F46a fill:#FFD700
```

---

## Summary: The "Deeming" Framework

**Consumer proposals use "deemed" provisions extensively to simplify:**

```mermaid
mindmap
    root((Deemed<br/>Provisions))
        Deemed Accepted
            §66.18 After 45 days
            Dir 22R4 No quorum
        Deemed Approved
            §66.22 After 15 days
        Deemed Annulled
            §66.31 3 months default
        Deemed Revived
            §66.31 5 Default cured
        Deemed Discharged
            §66.39 Admin 3 months
```

**Philosophy:** Default = acceptance/approval (favor debtor, reduce admin)

**Compare to Division I:**
- Division I: Must actively vote/approve
- Division II: Automatic unless someone objects

**Why?** "Minimum of administration and cost" (Study 5.3.1)

---

**This map covers ALL sections, directives, and forms in the consumer proposal process!**

Use this as your master reference - every connection is shown.
