# Lumina - A Legal Due Diligence AI Agent

Autonomous due diligence agent for M&A legal review. Given a natural language goal and a corpus of legal documents, the agent plans an investigation, reads documents, records findings and conflicts, and produces a structured report.


## Problem Statement
When one company wants to buy another, lawyers have to read hundreds of pages of contracts, corporate filings, and court records to find risks. This AI assistant automates that process: it takes a goal (like *"Can Company A safely buy Company B?"*), plans its own search across a folder of local documents, reads them, flags any missing papers or conflicting claims, and writes a clear summary report.

---

## 🚀 Quick Start

### 1. Installation
First, install the necessary Python packages:
```bash
pip install -r requirements.txt
```

### 2. Set Up Your API Key
Create a file named `.env` in the project root folder and add your OpenAI API key like this:
```env
OPENAI_KEY=your-api-key-here
```

### 3. Run the Assistant
To start an investigation on a sample set of documents:
```bash
python -m agent.runner "Can Orion Capital safely acquire Nexus Legal Technologies?" data/documents
```

The assistant will:
1. Look at all the files available in the folder.
2. Create an investigation plan (a list of questions to answer).
3. Read the files, search for keywords, and take notes.
4. Print its step-by-step thinking to the screen.
5. Save a detailed log file in the `logs/` folder.
6. Print a final summary report showing what it found, what was missing, and any risks.

---

## 📊 Running the Tests

We built a testing program (an "evaluation harness") to check how well the assistant performs when files are missing or contain conflicting information.

To run the tests:
```bash
# Run a single test scenario
python eval/harness.py --scenario S1

# Run all test scenarios and save the results
python eval/harness.py --all --output results/eval_results.json
```

---

## 🛠 How the Assistant Works

Instead of trying to read everything all at once, the assistant works like a human investigator using a simple loop:


```mermaid
flowchart TD
    %% Nodes
    A([🎯 User Goal]) --> B[🤖 Planner]
    B --> C[📋 Generate Initial Tasks]
    C --> D[(🗂️ Task Queue)]

    subgraph Loop [Investigation Loop]
        E[Select Next Task] --> F[🛠️ Tool Decision]
        F --> G[🔍 Search Corpus / Read File]
        G --> H[📝 Observation & Analysis]
        H --> I{❓ Observation Type}
        
        I -->|Finding| J[✅ Mark Task Complete]
        I -->|Conflict| K[⚠️ Conflict: Insert Task]
        I -->|Gap| L[🔄 Gap: Retry Task]
        
        L --> E
        J --> N{❓ More Tasks?}
        N -->|Yes| E
    end

    D --> E
    K --> D
    N -->|No| O([📄 Final Report])

    %% Styling
    classDef startEnd fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1;
    classDef process fill:#f5f5f5,stroke:#424242,stroke-width:2px,color:#212121;
    classDef decision fill:#fff8e1,stroke:#ff8f00,stroke-width:2px,color:#5d4037;
    classDef db fill:#efebe9,stroke:#4e342e,stroke-width:2px,color:#3e2723;
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20;
    classDef alert fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#b71c1c;

    class A,O startEnd;
    class B,C,E,F,G,H process;
    class D db;
    class I,N decision;
    class J,L success;
    class K alert;
```




### The 4 Files That Power the Agent:
* [agent/state.py](file:///Users/omerkhanjadoon/Documents/libra/agent/state.py) — Stores the list of questions, notes, and files read so far.
* [agent/tools.py](file:///Users/omerkhanjadoon/Documents/libra/agent/tools.py) — The tools the AI uses to list files, read them, and search for keywords.
* [agent/planner.py](file:///Users/omerkhanjadoon/Documents/libra/agent/planner.py) — The "brain" of the AI. It handles planning, choosing tools, interpreting search results, and writing the final report.
* [agent/runner.py](file:///Users/omerkhanjadoon/Documents/libra/agent/runner.py) — The engine that runs the loop, prints the status to your screen, and saves log files.

---



## Example Runs
```
{"event": "plan", "ts": "2026-07-14T18:02:39.974520+00:00", "tasks": [{"step": 1, "category": "IP Ownership", "question": "Does the IP assignment transfer ownership of Nexus's core technology to Nexus Legal Technologies?", "approach": "Read nexus_ip_assignment.txt and identify the assigned assets, assignee, scope, and any retained ownership rights."}, {"step": 2, "category": "IP Ownership", "question": "Does the university licence impose any third-party ownership claim or encumbrance over Nexus's core technology?", "approach": "Search nexus_university_licence.txt for ownership, lien, security interest, retained rights, sublicensing, and exclusivity provisions."}, {"step": 3, "category": "Contractual Obligations", "question": "Does the Law Firm Alpha client contract require consent for a change of control of Nexus?", "approach": "Search nexus_client_contract_lawfirm_alpha.txt for change-of-control, assignment, consent, merger, and acquisition clauses."}, {"step": 4, "category": "Contractual Obligations", "question": "Can Law Firm Alpha terminate its contract because of Orion Capital's proposed acquisition of Nexus?", "approach": "Search nexus_client_contract_lawfirm_alpha.txt for termination rights triggered by ownership changes, assignment, merger, or acquisition."}, {"step": 5, "category": "Litigation & Liabilities", "question": "Does the litigation register disclose any active or threatened claim against Nexus?", "approach": "Read nexus_litigation_register.txt and identify matters marked pending, active, threatened, or unresolved."}, {"step": 6, "category": "Litigation & Liabilities", "question": "Does the litigation register disclose any unresolved monetary liability of Nexus?", "approach": "Search nexus_litigation_register.txt for claimed damages, settlement obligations, judgments, provisions, and unpaid awards."}, {"step": 7, "category": "Corporate Structure", "question": "Does the incorporation certificate evidence that Nexus Legal Technologies was validly incorporated?", "approach": "Read nexus_incorporation_certificate.txt and verify the entity name, incorporation date, jurisdiction, registration number, and issuing authority."}, {"step": 8, "category": "Corporate Structure", "question": "Does the shareholder register disclose any restriction on transferring Nexus shares to Orion Capital?", "approach": "Search nexus_shareholder_register.txt for transfer restrictions, pre-emption rights, consent rights, options, pledges, and shareholder vetoes."}, {"step": 9, "category": "Regulatory & Compliance", "question": "Does the regulatory filing show that Nexus currently holds the registrations or authorisations required for its stated business?", "approach": "Read nexus_regulatory_filing.txt and identify each registration or authorisation, its status, scope, effective date, and expiry date."}, {"step": 10, "category": "Regulatory & Compliance", "question": "Does the regulatory filing disclose any regulatory enforcement action against Nexus?", "approach": "Search nexus_regulatory_filing.txt for investigations, warnings, violations, penalties, suspensions, revocations, and remediation orders."}]}
{"event": "tool_call", "ts": "2026-07-14T18:03:01.080460+00:00", "tool": "search_corpus", "args": {"directory": "C:\\Users\\z00571dh\\AppData\\Local\\Temp\\tmpquw7m6hu\\corpus", "query": "IP assignment transfer ownership of Nexus core technology to Nexus Legal Technologies, including assigned inventions, software, source code, intellectual property rights, exclusions, and retained rights"}, "decision": "Search the full corpus for the IP assignment and its operative transfer language because the relevant filename is unknown and ownership depends on conceptually related grant, scope, exclusion, and retained-rights clauses.", "expected_outcome": "The result should identify the assignment document and passages showing whether Nexus's core technology and associated intellectual property rights were fully assigned to Nexus Legal Technologies."}
{"event": "tool_result", "ts": "2026-07-14T18:03:01.082175+00:00", "tool": "search_corpus", "chars": 1526, "label": "1526 chars read"}
{"event": "observation", "ts": "2026-07-14T18:03:40.139236+00:00", "step": 0, "kind": "finding", "category": "IP Ownership", "description": "Clause 1 of nexus_ip_assignment.txt states that on 14 March 2022 Dr. Elena Vasquez assigned to Nexus Legal Technologies Ltd all rights, title, and interest in LexScan v1, the associated training datasets compiled between January 2020 and December 2021, and pending patent application GB2201234 filed on 3 January 2022. Clause 2 provides \u00a350,000 consideration, and Clause 3 represents that Dr. Vasquez is the sole inventor and that no third party has any claim over the assigned IP. The agreement is signed by Dr. Vasquez and Marcus Webb for Nexus.", "sources": ["nexus_ip_assignment.txt"], "action": "continue", "reason": "The assignment expressly transfers ownership of the identified core technology to Nexus, while the planned university-licence review will separately test for third-party claims or encumbrances."}
{"event": "decide", "ts": "2026-07-14T18:03:40.139394+00:00", "action": "continue", "step": 1}
{"event": "tool_call", "ts": "2026-07-14T18:04:06.751252+00:00", "tool": "search_corpus", "args": {"directory": "C:\\Users\\z00571dh\\AppData\\Local\\Temp\\tmpquw7m6hu\\corpus", "query": "university licence ownership rights third-party claim encumbrance over Nexus core technology LexScan intellectual property"}, "decision": "Search all documents for university licence provisions concerning ownership, third-party rights, or encumbrances because the relevant licence filename is not yet known.", "expected_outcome": "The result should identify the university licence and quote provisions establishing whether the university retains ownership, a licence, security interest, reversion right, or other claim over Nexus's core technology."}
{"event": "tool_result", "ts": "2026-07-14T18:04:06.752381+00:00", "tool": "search_corpus", "chars": 1524, "label": "1524 chars read"}
{"event": "observation", "ts": "2026-07-14T18:05:00.594853+00:00", "step": 1, "kind": "conflict", "category": "IP Ownership", "description": "Clause 1 of nexus_university_licence.txt grants Dr. Elena Vasquez, trading as Vasquez AI Research, a non-exclusive, non-transferable licence dated 1 September 2019 to use Imperial College London's ImperialNLP framework, and Clause 2 prohibits sublicensing, assignment, or transfer without Imperial's approval. This conflicts with Clauses 1 and 3 of nexus_ip_assignment.txt, under which Dr. Vasquez assigned all rights, title, and interest in LexScan v1, related datasets, and patent application GB2201234 to Nexus on 14 March 2022 for \u00a350,000 while representing that she was the sole inventor and no third party had any claim. If LexScan v1 incorporates or depends on ImperialNLP, the non-transferable university licence may encumber Nexus's core technology and prevent Nexus from holding the necessary usage rights.", "sources": ["nexus_university_licence.txt", "nexus_ip_assignment.txt"], "action": "insert_task", "reason": "The documents reveal a potential Imperial licence encumbrance whose applicability and consent status are not addressed by the remaining plan."}
{"event": "replan", "ts": "2026-07-14T18:05:00.595002+00:00", "replan_action": "insert_task", "detail": "The documents reveal a potential Imperial licence encumbrance whose applicability and consent status are not addressed by the remaining plan.", "new_task": {"category": "IP Ownership", "question": "Does LexScan v1 incorporate or depend on ImperialNLP, and if so did Imperial College London approve Nexus's acquisition or use of the licensed framework?", "approach": "Review the complete nexus_university_licence.txt, technical provenance and dependency records for LexScan v1, and any Imperial consent, novation, sublicense, or transfer correspondence."}}
{"event": "tool_call", "ts": "2026-07-14T18:05:41.451271+00:00", "tool": "search_corpus", "args": {"directory": "C:\\Users\\z00571dh\\AppData\\Local\\Temp\\tmpquw7m6hu\\corpus", "query": "LexScan v1 incorporation of or dependency on ImperialNLP framework, and Imperial College London consent, approval, assignment, transfer, sublicence, or authorisation for Nexus Legal Technologies to acquire or use ImperialNLP"}, "decision": "Search the full corpus for technical dependency evidence and any Imperial approval because those facts may appear in separate technical, correspondence, or consent documents not yet identified.", "expected_outcome": "Relevant passages will establish whether LexScan v1 uses ImperialNLP and whether Imperial College London approved Nexus's acquisition or continued use of the framework."}
{"event": "tool_result", "ts": "2026-07-14T18:05:41.452806+00:00", "tool": "search_corpus", "chars": 1519, "label": "1519 chars read"}
{"event": "observation", "ts": "2026-07-14T18:07:10.792249+00:00", "step": 2, "kind": "conflict", "category": "IP Ownership", "description": "Clause 1 of nexus_university_licence.txt grants Dr. Elena Vasquez, trading as Vasquez AI Research, a non-exclusive, non-transferable licence dated 1 September 2019 to use ImperialNLP, while Clause 2 prohibits sublicensing, assignment, or transfer without Imperial College London's prior written consent. Clause 3 further provides that all improvements or derivatives of ImperialNLP created by Dr. Vasquez are jointly owned by Imperial and Dr. Vasquez. These provisions conflict with Clauses 1 and 3 of nexus_ip_assignment.txt, under which Dr. Vasquez assigned all rights in LexScan v1, its January 2020\u2013December 2021 datasets, and patent application GB2201234 to Nexus on 14 March 2022 for \u00a350,000 while representing that she was the sole inventor and no third party had any claim. The documents provided do not establish whether LexScan v1 incorporates or depends on ImperialNLP and contain no written Imperial approval for Nexus's acquisition or use of the framework.", "sources": ["nexus_university_licence.txt", "nexus_ip_assignment.txt"], "action": "continue", "reason": "The available documents establish a material IP conflict but do not evidence LexScan v1's technical dependency or Imperial's required written consent, so the acquisition cannot presently be treated as safe on this issue."}
{"event": "decide", "ts": "2026-07-14T18:07:10.792438+00:00", "action": "continue", "step": 3}
{"event": "tool_call", "ts": "2026-07-14T18:07:56.280193+00:00", "tool": "search_corpus", "args": {"directory": "C:\\Users\\z00571dh\\AppData\\Local\\Temp\\tmpquw7m6hu\\corpus", "query": "Law Firm Alpha client contract consent required for change of control, acquisition, merger, or transfer of ownership of Nexus Legal Technologies"}, "decision": "Search the corpus for the Law Firm Alpha contract's change-of-control provisions because the relevant filename and exact clause terminology are not yet known.", "expected_outcome": "The result should identify the client contract and quote any clause stating whether Law Firm Alpha's prior consent is required upon Orion Capital's acquisition or another change of control of Nexus."}
{"event": "tool_result", "ts": "2026-07-14T18:07:56.281191+00:00", "tool": "search_corpus", "chars": 1636, "label": "1636 chars read"}
{"event": "observation", "ts": "2026-07-14T18:08:35.863650+00:00", "step": 3, "kind": "finding", "category": "Contractual Obligations", "description": "Clause 4 of nexus_client_contract_lawfirm_alpha.txt does not require Alpha & Partners LLP's consent to a change of control of Nexus Legal Technologies Ltd. Instead, it permits Alpha & Partners LLP to terminate the 1 June 2021 Master Services Agreement with 30 days' written notice if a transaction results in a new entity acquiring more than 50% of Nexus's voting shares.", "sources": ["nexus_client_contract_lawfirm_alpha.txt"], "action": "continue", "reason": "Clause 4 also conclusively answers the planned termination question, making Step 5 redundant."}
{"event": "decide", "ts": "2026-07-14T18:08:35.863721+00:00", "action": "continue", "step": 4}
{"event": "tool_call", "ts": "2026-07-14T18:08:57.105279+00:00", "tool": "search_corpus", "args": {"directory": "C:\\Users\\z00571dh\\AppData\\Local\\Temp\\tmpquw7m6hu\\corpus", "query": "Orion Capital proposed acquisition of Nexus percentage of voting shares change of control more than 50%"}, "decision": "Search the full corpus for the proposed acquisition terms, because the Alpha contract's termination threshold is already known but the percentage of Nexus voting shares Orion would acquire may appear in another document.", "expected_outcome": "A successful result will identify Orion's proposed voting-share percentage and allow comparison with Clause 4's more-than-50% threshold to determine whether Alpha may terminate on 30 days' written notice."}
{"event": "tool_result", "ts": "2026-07-14T18:08:57.106255+00:00", "tool": "search_corpus", "chars": 1635, "label": "1635 chars read"}
{"event": "observation", "ts": "2026-07-14T18:09:24.274142+00:00", "step": 4, "kind": "finding", "category": "Contractual Obligations", "description": "Clause 4 of nexus_client_contract_lawfirm_alpha.txt gives Alpha & Partners LLP the right to terminate the 1 June 2021 Master Services Agreement with 30 days' written notice if Orion Capital's proposed acquisition results in a new entity acquiring more than 50% of the voting shares of Nexus Legal Technologies Ltd. Alpha's consent is not required, but the termination right would be triggered if the acquisition satisfies that change-of-control threshold.", "sources": ["nexus_client_contract_lawfirm_alpha.txt"], "action": "continue", "reason": "The contract clearly answers the current question, so the investigation should proceed to the next planned step."}
{"event": "decide", "ts": "2026-07-14T18:09:24.274268+00:00", "action": "continue", "step": 5}
{"event": "tool_call", "ts": "2026-07-14T18:09:49.382072+00:00", "tool": "search_corpus", "args": {"directory": "C:\\Users\\z00571dh\\AppData\\Local\\Temp\\tmpquw7m6hu\\corpus", "query": "Nexus Legal Technologies litigation register active pending threatened claims disputes proceedings lawsuits"}, "decision": "Search all documents for active, pending, or threatened claims because the relevant litigation-register filename is not confirmed and the inquiry is conceptual.", "expected_outcome": "The result will identify the litigation register and quote any disclosure confirming or denying an active or threatened claim against Nexus."}
{"event": "tool_result", "ts": "2026-07-14T18:09:49.383186+00:00", "tool": "search_corpus", "chars": 1589, "label": "1589 chars read"}
{"event": "observation", "ts": "2026-07-14T18:11:11.721210+00:00", "step": 5, "kind": "conflict", "category": "Litigation & Liabilities", "description": "nexus_litigation_register.txt discloses active Matter LIT-2023-004, in which DataVault Ltd alleges breach of the May 2022 development agreement and claims \u00a3150,000 for missed API integration milestones; as of 15 January 2024, the matter was at the pre-action stage, with a 40% estimated probability of litigation and rated Moderate risk. It also discloses threatened Matter LIT-2023-007 arising from an anonymous letter received in December 2023, alleging that LexScan v1 was trained on proprietary datasets without a licence; the claimant remains unknown, no formal claim has been issued, and the matter is rated High risk because it could affect the validity of Nexus's core IP. This anonymous third-party IP claim conflicts with Clause 3 of nexus_ip_assignment.txt, which represents that Dr. Elena Vasquez was the sole inventor and that no third party had any claim over LexScan v1, the January 2020\u2013December 2021 training datasets, and patent application GB2201234 assigned to Nexus on 14 March 2022.", "sources": ["nexus_litigation_register.txt", "nexus_ip_assignment.txt"], "action": "insert_task", "reason": "The register answers the current question but reveals an anonymous IP threat that conflicts with the sole-inventor and no-third-party-claim representation and requires targeted investigation."}
{"event": "replan", "ts": "2026-07-14T18:11:11.721357+00:00", "replan_action": "insert_task", "detail": "The register answers the current question but reveals an anonymous IP threat that conflicts with the sole-inventor and no-third-party-claim representation and requires targeted investigation.", "new_task": {"category": "IP Ownership", "question": "Who sent the December 2023 letter in Matter LIT-2023-007, and what evidence supports the allegation that LexScan v1 used proprietary training datasets without a licence?", "approach": "Review the December 2023 threat letter, Nexus's investigation file, LexScan v1 dataset provenance records, and relevant licences to identify the claimant and assess whether the allegation affects the assigned datasets or patent application GB2201234."}}
{"event": "tool_call", "ts": "2026-07-14T18:11:36.099617+00:00", "tool": "search_corpus", "args": {"directory": "C:\\Users\\z00571dh\\AppData\\Local\\Temp\\tmpquw7m6hu\\corpus", "query": "Matter LIT-2023-007 December 2023 letter sender identity and evidence that LexScan v1 used proprietary training datasets without a licence"}, "decision": "Search the full corpus for the matter number, letter, sender identity, and supporting evidence because these details may appear outside the known litigation register in correspondence or technical records.", "expected_outcome": "The results should identify who sent the December 2023 letter, or confirm that the sender was anonymous, and describe any documents, dataset identifiers, access records, technical analysis, or other evidence supporting the unlicensed-use allegation."}
{"event": "tool_result", "ts": "2026-07-14T18:11:36.100496+00:00", "tool": "search_corpus", "chars": 1583, "label": "1583 chars read"}
{"event": "observation", "ts": "2026-07-14T18:12:40.897917+00:00", "step": 6, "kind": "conflict", "category": "IP Ownership", "description": "Matter LIT-2023-007 in nexus_litigation_register.txt identifies the sender only as an unknown, anonymous counterparty and states that a letter received in December 2023 alleged LexScan v1 was trained on proprietary datasets without a licence. The register provides no underlying datasets, technical analysis, provenance records, correspondence, or other evidence supporting that allegation; no formal claim has been issued, Nexus's legal team is investigating, and the matter is rated High risk. This anonymous third-party claim conflicts with Clause 3 of nexus_ip_assignment.txt, under which Dr. Elena Vasquez represented that she was the sole inventor and that no third party had any claim over LexScan v1, the associated January 2020\u2013December 2021 training datasets, or patent application GB2201234 assigned to Nexus on 14 March 2022.", "sources": ["nexus_litigation_register.txt", "nexus_ip_assignment.txt"], "action": "continue", "reason": "The register answers that the sender is unknown and confirms that the materials reviewed contain only the unsupported allegation, so the investigation should proceed to the next planned step."}
{"event": "decide", "ts": "2026-07-14T18:12:40.898070+00:00", "action": "continue", "step": 7}
{"event": "tool_call", "ts": "2026-07-14T18:12:57.132885+00:00", "tool": "read_file", "args": {"directory": "C:\\Users\\z00571dh\\AppData\\Local\\Temp\\tmpquw7m6hu\\corpus", "filename": "nexus_litigation_register.txt"}, "decision": "Read the complete litigation register because the known document may contain multiple matters, claimed amounts, statuses, and resolution details needed to identify every unresolved monetary liability.", "expected_outcome": "The register will show whether any matter exposes Nexus to an unpaid or unresolved monetary claim, including the amount sought and the matter's current status."}
{"event": "tool_result", "ts": "2026-07-14T18:12:57.150672+00:00", "tool": "read_file", "chars": 1471, "label": "1471 chars read"}
{"event": "observation", "ts": "2026-07-14T18:13:39.946413+00:00", "step": 7, "kind": "conflict", "category": "Litigation & Liabilities", "description": "nexus_litigation_register.txt discloses unresolved monetary exposure under active Matter LIT-2023-004: DataVault Ltd claims \u00a3150,000 for alleged breach of a May 2022 development agreement, with the matter at pre-action correspondence as of 15 January 2024, a 40% estimated probability of litigation, and a Moderate risk rating. The \u00a322,000 settlement in resolved Matter LIT-2021-001 does not represent an unresolved liability. Matter LIT-2023-007 is also rated High risk and records an anonymous December 2023 allegation that LexScan v1 used proprietary training data without a licence; this contradicts Clause 3 of nexus_ip_assignment.txt, which represents that Dr. Elena Vasquez was the sole inventor and that no third party had any claim over LexScan v1, the January 2020\u2013December 2021 training datasets, or patent application GB2201234.", "sources": ["nexus_litigation_register.txt", "nexus_ip_assignment.txt"], "action": "continue", "reason": "The register clearly confirms unresolved monetary exposure of up to \u00a3150,000, so the investigation can proceed to the next planned step."}
{"event": "decide", "ts": "2026-07-14T18:13:39.946492+00:00", "action": "continue", "step": 8}
{"event": "tool_call", "ts": "2026-07-14T18:13:58.415986+00:00", "tool": "search_corpus", "args": {"directory": "C:\\Users\\z00571dh\\AppData\\Local\\Temp\\tmpquw7m6hu\\corpus", "query": "Nexus Legal Technologies certificate of incorporation company number incorporation date Companies Act 2006 validly incorporated"}, "decision": "Search the corpus for the incorporation certificate and its operative details because the relevant filename is not yet identified and conceptual search is preferable to listing all files.", "expected_outcome": "The result should identify the certificate and show whether the registrar certified Nexus Legal Technologies Ltd's incorporation, including its company number, incorporation date, and jurisdiction or statutory basis."}
{"event": "tool_result", "ts": "2026-07-14T18:13:58.417185+00:00", "tool": "search_corpus", "chars": 1234, "label": "1234 chars read"}
{"event": "observation", "ts": "2026-07-14T18:14:16.820237+00:00", "step": 8, "kind": "finding", "category": "Corporate Structure", "description": "nexus_incorporation_certificate.txt states that Nexus Legal Technologies Ltd, company number 12345678, was incorporated on 3 March 2018 as a private company limited by shares under the Companies Act 2006. The certificate, issued by the Registrar of Companies for England and Wales, expressly confirms that Nexus is duly incorporated and is a limited company; it also records an initial share capital of 1,000 ordinary shares of \u00a31 each and identifies Marcus Webb and Dr. Elena Vasquez as directors at incorporation.", "sources": ["nexus_incorporation_certificate.txt"], "action": "continue", "reason": "The incorporation certificate directly evidences on its face that Nexus was validly incorporated, so the investigation can proceed to the next planned step."}
{"event": "decide", "ts": "2026-07-14T18:14:16.820413+00:00", "action": "continue", "step": 9}
{"event": "tool_call", "ts": "2026-07-14T18:14:36.994254+00:00", "tool": "search_corpus", "args": {"directory": "C:\\Users\\z00571dh\\AppData\\Local\\Temp\\tmpquw7m6hu\\corpus", "query": "Nexus Legal Technologies shareholder register restrictions on transfer of shares pre-emption rights board approval consent Orion Capital"}, "decision": "Search the corpus conceptually for the Nexus shareholder register and any share-transfer restrictions because the relevant filename is not yet known and restrictions may be expressed as pre-emption, consent, or approval provisions.", "expected_outcome": "The result should identify the shareholder register and passages stating whether Nexus shares are freely transferable or subject to any restriction relevant to a transfer to Orion Capital."}
{"event": "tool_result", "ts": "2026-07-14T18:14:36.995224+00:00", "tool": "search_corpus", "chars": 1626, "label": "1626 chars read"}
{"event": "observation", "ts": "2026-07-14T18:15:15.914964+00:00", "step": 9, "kind": "finding", "category": "Corporate Structure", "description": "The shareholder register, last updated 30 November 2023, states that a shareholders' agreement dated 15 April 2022 governs transfer restrictions. Its extracted key terms require any transfer of Ordinary A shares to be offered first to the existing Ordinary A shareholders under a right of first refusal. This restriction applies to the 4,500 Ordinary A shares held by Marcus Webb (45%) and the 3,500 Ordinary A shares held by Dr. Elena Vasquez (35%); the register discloses no Orion Capital-specific restriction and no transfer restriction for Meridian Ventures Fund II's 2,000 Preferred B shares (20%) in the provided text.", "sources": ["nexus_shareholder_register.txt"], "action": "continue", "reason": "The register clearly discloses a right-of-first-refusal restriction affecting transfers of Ordinary A shares, so the current question is answered."}
{"event": "decide", "ts": "2026-07-14T18:15:15.915135+00:00", "action": "continue", "step": 10}
{"event": "tool_call", "ts": "2026-07-14T18:15:38.154384+00:00", "tool": "search_corpus", "args": {"directory": "C:\\Users\\z00571dh\\AppData\\Local\\Temp\\tmpquw7m6hu\\corpus", "query": "Nexus Legal Technologies regulatory filing current registrations authorisations licences required for its stated business registration status authorised regulated activities"}, "decision": "Search the full corpus for the regulatory filing and passages addressing Nexus's current registrations or authorisations because the relevant filename is not yet known and the issue is conceptual.", "expected_outcome": "The results should identify the regulatory filing and state which registrations or authorisations Nexus holds, their current status, and whether they cover its stated business activities."}
{"event": "tool_result", "ts": "2026-07-14T18:15:38.155646+00:00", "tool": "search_corpus", "chars": 1535, "label": "1535 chars read"}
{"event": "observation", "ts": "2026-07-14T18:16:26.894452+00:00", "step": 10, "kind": "finding", "category": "Regulatory & Compliance", "description": "nexus_regulatory_filing.txt records Nexus Legal Technologies Ltd under ICO Registration Number ZA987654 with status \u201cActive\u201d and a renewal date of 28 February 2025, covering AI-assisted analysis of legal documents for law-firm clients and storage of anonymised contract metadata for model improvement. It states that Nexus is a software provider rather than an authorised legal services provider and therefore does not require SRA authorisation, as confirmed by SRA correspondence dated 4 April 2023. The filing also reports no ICO enforcement notices or fines as of the record date, a LexScan v2 DPIA completed in October 2023, and a December 2023 external UK GDPR review by Lawton Privacy Ltd that identified no material issues.", "sources": ["nexus_regulatory_filing.txt"], "action": "continue", "reason": "The filing answers the current authorisation question and conclusively covers planned Step 12 by reporting no ICO enforcement notices or fines as of the record date."}
{"event": "decide", "ts": "2026-07-14T18:16:26.894564+00:00", "action": "continue", "step": 11}
{"event": "tool_call", "ts": "2026-07-14T18:16:39.896619+00:00", "tool": "search_in_file", "args": {"directory": "C:\\Users\\z00571dh\\AppData\\Local\\Temp\\tmpquw7m6hu\\corpus", "filename": "nexus_regulatory_filing.txt", "query": "enforcement"}, "decision": "Search the known regulatory filing for the exact term \u201cenforcement,\u201d which is more targeted than reading the entire document or searching the corpus.", "expected_outcome": "The result will identify whether the filing reports any enforcement notices, fines, investigations, or other regulatory action against Nexus."}
{"event": "tool_result", "ts": "2026-07-14T18:16:39.898736+00:00", "tool": "search_in_file", "chars": 71, "label": "1 lines matched"}
{"event": "observation", "ts": "2026-07-14T18:16:55.324092+00:00", "step": 11, "kind": "finding", "category": "Regulatory & Compliance", "description": "nexus_regulatory_filing.txt reports that no ICO enforcement notices or fines had been issued against Nexus Legal Technologies Ltd as of the record date.", "sources": ["nexus_regulatory_filing.txt"], "action": "continue", "reason": "The regulatory filing clearly answers the current question and discloses no ICO enforcement action against Nexus."}
{"event": "decide", "ts": "2026-07-14T18:16:55.324177+00:00", "action": "continue", "step": 12}
{"event": "conclude", "ts": "2026-07-14T18:18:56.637867+00:00", "chars": 7077}


```

More examples in logs folder.

---

## 💡 Key Design Choices

### 1. Simple Notes over Full History
Many AI tools send the entire conversation history back and forth on every step. This makes them slow and expensive. Instead, our assistant keeps a simple list of **Notes** (Findings, Gaps, and Conflicts). The AI only looks at these notes and its current plan to make its next move. 
<br/>In many AI agents, the message history grows O(n) with loop iterations i.e by step 15 you are paying for every prior tool call in every subsequent prompt. I switched to an O(1) state snapshot: current step count, the plan, and the notes recorded so far. That is always under ~300 tokens regardless of how many steps have run. The tradeoff is that the LLM does not see verbatim tool output from prior steps, but that is fine because the *note* from each step is what matters, not the raw text.

### 2. Splitting Up the Decisions
Instead of asking the AI to "read this search result, decide what it means, and pick the next tool" all in one prompt, we split it into separate, focused steps:
* **Step A:** Pick a tool to search for information.
* **Step B:** Read the search result and record what was learned.
This split makes the AI much more accurate.

### 3. Using Keyword Search (BM25) Instead of Vector Search
We chose a direct keyword search rather than modern "vector search" because keyword search is predictable. If we search for a word like "litigation" and get zero results, the AI knows for sure that the word isn't there and can immediately flag a missing document. 

Another reason for not using the vector embeddings in this initial version is that the focus is on testing the agent's ability to plan and reason over the given documents rather than building a production-ready RAG system.
Using a hybrid retrieval system with bm25 and vector embeddings would be a good next step.

---




## What I would do with more time

The thing I would change first is retrieval. BM25 requires exact term overlap and that is a meaningful constraint on legal language, which is full of synonymy ("IP assignment" vs "intellectual property transfer"). A **hybrid pipeline — BM25 plus dense embeddings plus a cross-encoder reranker** — would catch the cases the current system misses silently, and it would also let the agent send the top-3 relevant paragraphs to the LLM instead of full documents, cutting token usage significantly.

The second thing I would address is **Conflict Classification**. Right now the observer sometimes records a conflict as a plain finding if the contradiction is subtle. I would make this a separate, targeted prompt — "here are two notes from different documents, do they contradict each other?" — rather than asking the observer to detect conflicts while also extracting a note from a single result. Focused calls beat multipurpose ones.

The third thing is **Parallelism**. Independent investigation questions (litigation history, IP chain of title, corporate structure) have no dependency between them and could run concurrently. The current sequential loop is simple and correct but slow at ~20 minutes per run. An async task queue would reduce that to a few minutes without changing any of the core logic.


## Evaluation Method: 

Four scenarios are defined in `eval/scenarios.py`:

| ID | Name | Corpus | Min required passes |
|----|------|--------|---------------------|
| S1 | Full Corpus — Happy Path | All 7 documents | 5 / 5 |
| S2 | Missing Litigation Register | 6 documents | 3 / 5 |
| S3 | Missing IP Assignment | 6 documents | 3 / 5 |
| S4 | IP Conflict Detection — Narrow Corpus | 2 documents | 1 / 5 |

Scoring uses an adversarial LLM judge (gpt-5.6-sol, temperature=0) via the Libra Azure endpoint. Ten rubric criteria are defined in `eval/rubric.py`; five are required.

## Evaluation Results


The assistant was tested against four scenarios with different document folders (some complete, some with missing files):

| Test Case | Description | Score | Result |
|:---|:---|:---:|:---:|
| **Test 1: Full Corpus** | All documents present. | 9.5 / 10 | ✅ PASS |
| **Test 2: Missing Court Records** | Court history register was withheld. | 8.0 / 10 | ✅ PASS |
| **Test 3: Missing Ownership Contract** | Main technology transfer contract was withheld. | 9.0 / 10 | ✅ PASS |
| **Test 4: Bare Minimum Info** | Only 2 documents provided. | 5.5 / 10 | ✅ PASS |

For a detailed breakdown of what these scores mean and how we graded the AI, see the [docs/evaluation.md](file:///Users/omerkhanjadoon/Documents/libra/docs/evaluation.md) document.


## Known limitations

**Azure sandbox throttling:** The Libra endpoint enforces a 100k TPM rate limit and can return HTTP 500 under peak load. The agent retries both `RateLimitError` (429) and `InternalServerError` (500) with exponential backoff (30/60/90/120/150 s, 6 attempts). Investigation runs may take 10–30 minutes depending on sandbox load.


