# Production Two-Dimensional Regulatory Crosswalk Results (Sprint N: Atomic Assurance Engine)

**Retrieval Architecture**: Multi-Intent Clause Decompounding + Canonical MFA IA-2 Binding + Hybrid Candidate Retrieval (Dense + BM25 Okapi) with **Top-15 Recall Funnel**  
**Catalog Scoping**: Withdrawn & Blank Rev 5 Controls Purged (`RA-4`, `SA-12`, etc.)  
**Assurance Engine**: Qwen 35B Two-Dimensional Dual-Judge + **Atomic Coverage Verifier Gate + Dynamic Bayesian Confidence Scoring**  
**Database Dual-Write**: PostgreSQL (`obligation_framework_mappings`) & Memgraph (`:CROSSWALKS_TO`)  
**Execution Date**: 2026-08-16  

---

## Section A: Defensible Three-Way Crosswalk Metrics

| Assurance Dimension | Metric Description | Value | Interpretation |
|---|---|---|---|
| **1. Semantic Discoverability** | MAS Obligations with $\ge 1$ relevant NIST candidate | **85 / 85** (100.0%) | Measures semantic search recall across catalogs |
| **2. Defensible Full Assurance** | Crosswalk edges with verified complete coverage | **44 edges** (5.4%) | Gated by Atomic Action/Object/Scope Verifier |
| **3. True Regulatory Gaps** | MAS Obligations with zero defensible federal control | **5 / 85** (5.9%) | Retail customer notifications, customer fraud advisories |

### Dimension 1: Semantic Relationship Distribution (Source $\rightarrow$ Target Perspective)

| Semantic Relationship | Description | Edge Count | Percentage |
|---|---|---|---|
| `EQUIVALENT` | 1-to-1 Identical Scope & Intent (Transitivity Enforced) | 24 | 2.9% |
| `SUBSET_OF` | Target NIST control completely satisfies MAS (MAS $\subseteq$ NIST) | 309 | 37.7% |
| `SUPERSET_OF` | MAS obligation is broader; NIST control covers a sub-part | 138 | 16.8% |
| `OVERLAPS` | Material conceptual overlap without strict containment | 326 | 39.8% |
| `SUPPORTS` | Target control enables/supports MAS without satisfying it | 22 | 2.7% |

### Dimension 2: Assurance Coverage Distribution (Audit Defensibility)

| Assurance Coverage Level | Meaning | Edge Count | Percentage |
|---|---|---|---|
| `FULL_COVERAGE` | NIST evidence completely satisfies MAS obligation for audit | 44 | 5.4% |
| `PARTIAL_COVERAGE` | NIST evidence satisfies material part; remaining gaps | 705 | 86.1% |
| `NO_COVERAGE` | NIST evidence does NOT satisfy MAS (enabling / gap) | 70 | 8.5% |

---

## Section B: 25 Sample Two-Dimensional Matches (Complete Verbatim Text & Structured Rationales)

### Sample Match 1: `MAS-1.3.a` ⟷ `NIST-RA-6`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.83` | Dense Sim: `0.60`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0357 (Max Dense Sim: 0.60)
* **Defensible Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-RA-6 Technical Surveillance Countermeasures Survey: Employ a technical surveillance countermeasures survey at {{ insert: param, ra-06_odp.01 }} {{ insert: param, ra-06_odp.02 }}..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-6 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```

> **MAS TRM Clause [MAS-1.3.a]**:
> *The Financial Institution must evaluate its exposure to technology risks.*

> **NIST SP 800-53 Control [NIST-RA-6 - Technical Surveillance Countermeasures Survey]**:
> *Employ a technical surveillance countermeasures survey at {{ insert: param, ra-06_odp.01 }} {{ insert: param, ra-06_odp.02 }}.
A technical surveillance countermeasures survey is a service provided by qualified personnel to detect the presence of technical surveillance devices and hazards and to identify technical security weaknesses that could be used in the conduct of a technical penetration of the surveyed facility. Technical surveillance countermeasures surveys also provide evaluations of the technical security posture of organizations and facilities and include visual, electronic, and physical examinations of surveyed facilities, internally and externally. The surveys also provide useful input for risk assessments and information regarding organizational exposure to potential adversaries.
a technical surveillance countermeasures survey is employed at {{ insert: param, ra-06_odp.01 }} {{ insert: param, ra-06_odp.02 }}.
Risk assessment policy

procedures addressing technical surveillance countermeasures surveys

audit records/event logs

system security plan

other relevant documents or records
Organizational personnel with technical surveillance countermeasures surveys responsibilities

system/network administrators

organizational personnel with security responsibilities
Organizational processes for technical surveillance countermeasures surveys

mechanisms/tools supporting and/or implementing technical surveillance countermeasure surveys*

---

### Sample Match 2: `MAS-1.4(a).1` ⟷ `NIST-PM-19`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.84` | Dense Sim: `0.49`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0348 (Max Dense Sim: 0.49)
* **Defensible Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-PM-19 Privacy Program Leadership Role: Appoint a senior agency official for privacy with the authority, mission, accountability, and resources to coordinate, develop, and implement, applicable privacy requirements and manage privacy risks through the organization-wide privacy program..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-19 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```

> **MAS TRM Clause [MAS-1.4(a).1]**:
> *The Board of Directors and Senior Management must cultivate a strong risk culture.*

> **NIST SP 800-53 Control [NIST-PM-19 - Privacy Program Leadership Role]**:
> *Appoint a senior agency official for privacy with the authority, mission, accountability, and resources to coordinate, develop, and implement, applicable privacy requirements and manage privacy risks through the organization-wide privacy program.
The privacy officer is an organizational official. For federal agencies—as defined by applicable laws, executive orders, directives, regulations, policies, standards, and guidelines—this official is designated as the senior agency official for privacy. Organizations may also refer to this official as the chief privacy officer. The senior agency official for privacy also has roles on the data management board (see [PM-23](#pm-23) ) and the data integrity board (see [PM-24](#pm-24)).
a senior agency official for privacy with authority, mission, accountability, and resources is appointed;
the senior agency official for privacy coordinates applicable privacy requirements;
the senior agency official for privacy develops applicable privacy requirements;
the senior agency official for privacy implements applicable privacy requirements;
the senior agency official for privacy manages privacy risks through the organization-wide privacy program.
Privacy program documents, including policies, procedures, plans, and reports

public privacy notices, including Federal Register notices

privacy impact assessments

privacy risk assessments

Privacy Act statements

system of records notices

computer matching agreements and notices

contracts, information sharing agreements, and memoranda of understanding

governing requirements, including laws, executive orders, regulations, standards, and guidance

other relevant documents or records
Organizational personnel with privacy program planning and plan implementation responsibilities

organizational personnel with privacy responsibilities

senior agency official for privacy

privacy officials*

---

### Sample Match 3: `MAS-1.4(b).1` ⟷ `NIST-SI-20`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.83` | Dense Sim: `0.54`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0329 (Max Dense Sim: 0.54)
* **Defensible Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-SI-20 Tainting: Embed data or capabilities in the following systems or system components to determine if organizational data has been exfiltrated or improperly removed from the organization: {{ insert: param, si-20_odp }}..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SI-20 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```

> **MAS TRM Clause [MAS-1.4(b).1]**:
> *The Financial Institution must adopt a defence-in-depth approach to strengthen cyber resilience.*

> **NIST SP 800-53 Control [NIST-SI-20 - Tainting]**:
> *Embed data or capabilities in the following systems or system components to determine if organizational data has been exfiltrated or improperly removed from the organization: {{ insert: param, si-20_odp }}.
Many cyber-attacks target organizational information, or information that the organization holds on behalf of other entities (e.g., personally identifiable information), and exfiltrate that data. In addition, insider attacks and erroneous user procedures can remove information from the system that is in violation of the organizational policies. Tainting approaches can range from passive to active. A passive tainting approach can be as simple as adding false email names and addresses to an internal database. If the organization receives email at one of the false email addresses, it knows that the database has been compromised. Moreover, the organization knows that the email was sent by an unauthorized entity, so any packets it includes potentially contain malicious code, and that the unauthorized entity may have potentially obtained a copy of the database. Another tainting approach can include embedding false data or steganographic data in files to enable the data to be found via open-source analysis. Finally, an active tainting approach can include embedding software in the data that is able to "call home," thereby alerting the organization to its "capture," and possibly its location, and the path by which it was exfiltrated or removed.
data or capabilities are embedded in {{ insert: param, si-20_odp }} to determine if organizational data has been exfiltrated or improperly removed from the organization.
System and information integrity policy

system and information integrity procedures

personally identifiable information processing policy

procedures addressing software and information integrity

system design documentation

system configuration settings and associated documentation

policy and procedures addressing the systems security engineering technique of deception

system security plan

privacy plan

other relevant documents or records
Organizational personnel responsible for detecting tainted data

organizational personnel with systems security engineering responsibilities

organizational personnel with information security and privacy responsibilities
Automated mechanisms for post-breach detection

decoys, traps, lures, and methods for deceiving adversaries

detection and notification mechanisms*

---

### Sample Match 4: `MAS-1.4(b).3` ⟷ `NIST-AC-17`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.85` | Dense Sim: `0.50`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0234 (Max Dense Sim: 0.50)
* **Defensible Rationale**:
```text
• MAS Requirement: must continuously improve IT processes and controls to preserve the confidentiality, integrity, and availability of data and IT systems.
• NIST Control: NIST-AC-17 Remote Access: Establish and document usage restrictions, configuration/connection requirements, and implementation guidance for each type of remote access allowed; and.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-AC-17 provides technical control capabilities addressing obligations in MAS-1.4(b).3.)
```

> **MAS TRM Clause [MAS-1.4(b).3]**:
> *The Financial Institution must continuously improve IT processes and controls to preserve the confidentiality, integrity, and availability of data and IT systems.*

> **NIST SP 800-53 Control [NIST-AC-17 - Remote Access]**:
> *Establish and document usage restrictions, configuration/connection requirements, and implementation guidance for each type of remote access allowed; and
Authorize each type of remote access to the system prior to allowing such connections.
Remote access is access to organizational systems (or processes acting on behalf of users) that communicate through external networks such as the Internet. Types of remote access include dial-up, broadband, and wireless. Organizations use encrypted virtual private networks (VPNs) to enhance confidentiality and integrity for remote connections. The use of encrypted VPNs provides sufficient assurance to the organization that it can effectively treat such connections as internal networks if the cryptographic mechanisms used are implemented in accordance with applicable laws, executive orders, directives, regulations, policies, standards, and guidelines. Still, VPN connections traverse external networks, and the encrypted VPN does not enhance the availability of remote connections. VPNs with encrypted tunnels can also affect the ability to adequately monitor network communications traffic for malicious code. Remote access controls apply to systems other than public web servers or systems designed for public access. Authorization of each remote access type addresses authorization prior to allowing remote access without specifying the specific formats for such authorization. While organizations may use information exchange and system connection security agreements to manage remote access connections to other systems, such agreements are addressed as part of [CA-3](#ca-3) . Enforcing access restrictions for remote access is addressed via [AC-3](#ac-3).
usage restrictions are established and documented for each type of remote access allowed;
configuration/connection requirements are established and documented for each type of remote access allowed;
implementation guidance is established and documented for each type of remote access allowed;
each type of remote access to the system is authorized prior to allowing such connections.
Access control policy

procedures addressing remote access implementation and usage (including restrictions)

configuration management plan

system configuration settings and associated documentation

remote access authorizations

system audit records

system security plan

other relevant documents or records
Organizational personnel with responsibilities for managing remote access connections

system/network administrators

organizational personnel with information security responsibilities
Remote access management capability for the system*

---

### Sample Match 5: `MAS-6.5.3.a` ⟷ `NIST-PM-14`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.85` | Dense Sim: `0.64`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0317 (Max Dense Sim: 0.64)
* **Defensible Rationale**:
```text
• MAS Requirement: must establish a process to assess the risk of end-user developed or acquired applications.
• NIST Control: NIST-PM-14 Testing, Training, and Monitoring: Implement a process for ensuring that organizational plans for conducting security and privacy testing, training, and monitoring activities associated with organizational systems:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-14 provides technical control capabilities addressing obligations in MAS-6.5.3.a.)
```

> **MAS TRM Clause [MAS-6.5.3.a]**:
> *The Financial Institution must establish a process to assess the risk of end-user developed or acquired applications.*

> **NIST SP 800-53 Control [NIST-PM-14 - Testing, Training, and Monitoring]**:
> *Implement a process for ensuring that organizational plans for conducting security and privacy testing, training, and monitoring activities associated with organizational systems:
Are developed and maintained; and
Continue to be executed; and
Review testing, training, and monitoring plans for consistency with the organizational risk management strategy and organization-wide priorities for risk response actions.
A process for organization-wide security and privacy testing, training, and monitoring helps ensure that organizations provide oversight for testing, training, and monitoring activities and that those activities are coordinated. With the growing importance of continuous monitoring programs, the implementation of information security and privacy across the three levels of the risk management hierarchy and the widespread use of common controls, organizations coordinate and consolidate the testing and monitoring activities that are routinely conducted as part of ongoing assessments supporting a variety of controls. Security and privacy training activities, while focused on individual systems and specific roles, require coordination across all organizational elements. Testing, training, and monitoring plans and activities are informed by current threat and vulnerability assessments.
a process is implemented for ensuring that organizational plans for conducting security testing, training, and monitoring activities associated with organizational systems are developed;
a process is implemented for ensuring that organizational plans for conducting security testing, training, and monitoring activities associated with organizational systems are maintained;
a process is implemented for ensuring that organizational plans for conducting privacy testing, training, and monitoring activities associated with organizational systems are developed;
a process is implemented for ensuring that organizational plans for conducting privacy testing, training, and monitoring activities associated with organizational systems are maintained;
a process is implemented for ensuring that organizational plans for conducting security testing, training, and monitoring activities associated with organizational systems continue to be executed;
a process is implemented for ensuring that organizational plans for conducting privacy testing, training, and monitoring activities associated with organizational systems continue to be executed;
testing plans are reviewed for consistency with the organizational risk management strategy;
training plans are reviewed for consistency with the organizational risk management strategy;
monitoring plans are reviewed for consistency with the organizational risk management strategy;
testing plans are reviewed for consistency with organization-wide priorities for risk response actions;
training plans are reviewed for consistency with organization-wide priorities for risk response actions;
monitoring plans are reviewed for consistency with organization-wide priorities for risk response actions.
Information security program plan

privacy program plan

plans for conducting security and privacy testing, training, and monitoring activities

organizational procedures addressing the development and maintenance of plans for conducting security and privacy testing, training, and monitoring activities

risk management strategy

procedures for the review of plans for conducting security and privacy testing, training, and monitoring activities for consistency with risk management strategy and risk response priorities

results of risk assessments associated with conducting security and privacy testing, training, and monitoring activities

documentation of the timely execution of plans for conducting security and privacy testing, training, and monitoring activities

other relevant documents or records
Organizational personnel with responsibilities for developing and maintaining plans for conducting security and privacy testing, training, and monitoring activities

organizational personnel with information security and privacy responsibilities
Organizational processes for the development and maintenance of plans for conducting security and privacy testing, training, and monitoring activities

mechanisms supporting the development and maintenance of plans for conducting security and privacy testing, training, and monitoring activities*

---

### Sample Match 6: `MAS-6.5.3.d` ⟷ `NIST-PM-25`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.83` | Dense Sim: `0.57`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0355 (Max Dense Sim: 0.57)
* **Defensible Rationale**:
```text
• MAS Requirement: must conduct proper testing before deploying end-user developed or acquired applications.
• NIST Control: NIST-PM-25 Minimization of Personally Identifiable Information Used in Testing, Training, and Research: Develop, document, and implement policies and procedures that address the use of personally identifiable information for internal testing, training, and research;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-25 provides technical control capabilities addressing obligations in MAS-6.5.3.d.)
```

> **MAS TRM Clause [MAS-6.5.3.d]**:
> *The Financial Institution must conduct proper testing before deploying end-user developed or acquired applications.*

> **NIST SP 800-53 Control [NIST-PM-25 - Minimization of Personally Identifiable Information Used in Testing, Training, and Research]**:
> *Develop, document, and implement policies and procedures that address the use of personally identifiable information for internal testing, training, and research;
Limit or minimize the amount of personally identifiable information used for internal testing, training, and research purposes;
Authorize the use of personally identifiable information when such information is required for internal testing, training, and research; and
Review and update policies and procedures {{ insert: param, pm-25_prm_1 }}.
The use of personally identifiable information in testing, research, and training increases the risk of unauthorized disclosure or misuse of such information. Organizations consult with the senior agency official for privacy and/or legal counsel to ensure that the use of personally identifiable information in testing, training, and research is compatible with the original purpose for which it was collected. When possible, organizations use placeholder data to avoid exposure of personally identifiable information when conducting testing, training, and research.
policies that address the use of personally identifiable information for internal testing are developed and documented;
policies that address the use of personally identifiable information for internal training are developed and documented;
policies that address the use of personally identifiable information for internal research are developed and documented;
procedures that address the use of personally identifiable information for internal testing are developed and documented;
procedures that address the use of personally identifiable information for internal training are developed and documented;
procedures that address the use of personally identifiable information for internal research are developed and documented;
policies that address the use of personally identifiable information for internal testing, are implemented;
policies that address the use of personally identifiable information for training are implemented;
policies that address the use of personally identifiable information for research are implemented;
procedures that address the use of personally identifiable information for internal testing are implemented;
procedures that address the use of personally identifiable information for training are implemented;
procedures that address the use of personally identifiable information for research are implemented;
the amount of personally identifiable information used for internal testing purposes is limited or minimized;
the amount of personally identifiable information used for internal training purposes is limited or minimized;
the amount of personally identifiable information used for internal research purposes is limited or minimized;
the required use of personally identifiable information for internal testing is authorized;
the required use of personally identifiable information for internal training is authorized;
the required use of personally identifiable information for internal research is authorized;
policies are reviewed {{ insert: param, pm-25_odp.01 }};
policies are updated {{ insert: param, pm-25_odp.02 }};
procedures are reviewed {{ insert: param, pm-25_odp.03 }};
procedures are updated {{ insert: param, pm-25_odp.04 }}.
Privacy program plan

policies and procedures for the minimization of personally identifiable information used in testing, training, and research

documentation supporting policy implementation (e.g., templates for testing, training, and research

privacy threshold analysis

privacy risk assessment)

data sets used for testing, training, and research
Organizational personnel with privacy program responsibilities

organizational personnel with privacy responsibilities

system developers

personnel with IRB responsibilities
Organizational processes for data quality and personally identifiable information management

mechanisms supporting data quality management and personally identifiable information management to minimize the use of personally identifiable information*

---

### Sample Match 7: `MAS-7.2.2` ⟷ `NIST-SC-8`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `NO_COVERAGE` (Dynamic Confidence: `0.83` | Dense Sim: `0.56`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0258 (Max Dense Sim: 0.56)
* **Defensible Rationale**:
```text
• MAS Requirement: must review and verify the configuration information of its hardware and software on a regular basis.
• NIST Control: NIST-SC-8 Transmission Confidentiality and Integrity: Protect the {{ insert: param, sc-08_odp }} of transmitted information..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: NO_COVERAGE (NIST-SC-8 provides technical control capabilities addressing obligations in MAS-7.2.2.)
```

> **MAS TRM Clause [MAS-7.2.2]**:
> *The Financial Institution must review and verify the configuration information of its hardware and software on a regular basis.*

> **NIST SP 800-53 Control [NIST-SC-8 - Transmission Confidentiality and Integrity]**:
> *Protect the {{ insert: param, sc-08_odp }} of transmitted information.
Protecting the confidentiality and integrity of transmitted information applies to internal and external networks as well as any system components that can transmit information, including servers, notebook computers, desktop computers, mobile devices, printers, copiers, scanners, facsimile machines, and radios. Unprotected communication paths are exposed to the possibility of interception and modification. Protecting the confidentiality and integrity of information can be accomplished by physical or logical means. Physical protection can be achieved by using protected distribution systems. A protected distribution system is a wireline or fiber-optics telecommunications system that includes terminals and adequate electromagnetic, acoustical, electrical, and physical controls to permit its use for the unencrypted transmission of classified information. Logical protection can be achieved by employing encryption techniques.

Organizations that rely on commercial providers who offer transmission services as commodity services rather than as fully dedicated services may find it difficult to obtain the necessary assurances regarding the implementation of needed controls for transmission confidentiality and integrity. In such situations, organizations determine what types of confidentiality or integrity services are available in standard, commercial telecommunications service packages. If it is not feasible to obtain the necessary controls and assurances of control effectiveness through appropriate contracting vehicles, organizations can implement appropriate compensating controls.
the {{ insert: param, sc-08_odp }} of transmitted information is/are protected.
System and communications protection policy

procedures addressing transmission confidentiality and integrity

system design documentation

system configuration settings and associated documentation

system audit records

system security plan

other relevant documents or records
System/network administrators

organizational personnel with information security responsibilities

system developer
Mechanisms supporting and/or implementing transmission confidentiality and/or integrity*

---

### Sample Match 8: `MAS-7.3.2.a` ⟷ `NIST-SI-2`

* **Semantic Relation**: `SUPERSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.84` | Dense Sim: `0.60`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0485 (Max Dense Sim: 0.60)
* **Defensible Rationale**:
```text
• MAS Requirement: must develop a technology refresh plan for the replacement of hardware and software before they reach end-of-support.
• NIST Control: NIST-SI-2 Flaw Remediation: Identify, report, and correct system flaws;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SI-2 provides technical control capabilities addressing obligations in MAS-7.3.2.a.)
```

> **MAS TRM Clause [MAS-7.3.2.a]**:
> *The Financial Institution must develop a technology refresh plan for the replacement of hardware and software before they reach end-of-support.*

> **NIST SP 800-53 Control [NIST-SI-2 - Flaw Remediation]**:
> *Identify, report, and correct system flaws;
Test software and firmware updates related to flaw remediation for effectiveness and potential side effects before installation;
Install security-relevant software and firmware updates within {{ insert: param, si-02_odp }} of the release of the updates; and
Incorporate flaw remediation into the organizational configuration management process.
The need to remediate system flaws applies to all types of software and firmware. Organizations identify systems affected by software flaws, including potential vulnerabilities resulting from those flaws, and report this information to designated organizational personnel with information security and privacy responsibilities. Organizations consider establishing a controlled patching environment for mission-critical systems. Security-relevant updates include patches, service packs, and malicious code signatures. Organizations also address flaws discovered during assessments, continuous monitoring, incident response activities, and system error handling. By incorporating flaw remediation into configuration management processes, required remediation actions can be tracked and verified.

Organization-defined time periods for updating security-relevant software and firmware may vary based on a variety of risk factors, including the security category of the system, the criticality of the update (i.e., severity of the vulnerability related to the discovered flaw), the organizational risk tolerance, the mission supported by the system, or the threat environment. Some types of flaw remediation may require more testing than other types. Organizations determine the type of testing needed for the specific type of flaw remediation activity under consideration and the types of changes that are to be configuration-managed. Flaw remediation testing addresses both effectiveness of addressing security issues and for potential side effects on functionality, system and system component performance and operations. When implementing remediation activities, organizations consider the order and timing of updates to validate correct execution within the system environment, and to support system and component availability needs (i.e., implementing a staggered deployment strategy). In some situations, organizations may determine that the testing of software or firmware updates is not necessary or practical, such as when implementing simple malicious code signature updates. In testing decisions, organizations consider whether security-relevant software or firmware updates are obtained from authorized sources with appropriate digital signatures.

When implementing remediation activities, organizations consider the order and timing of updates to validate correct execution within the system environment, and to support system and component availability needs (i.e., implementing a staggered deployment strategy). Organizations verify that software and firmware updates come from authorized sources prior to downloading.
system flaws are identified;
system flaws are reported;
system flaws are corrected;
software updates related to flaw remediation are tested for effectiveness before installation;
software updates related to flaw remediation are tested for potential side effects before installation;
firmware updates related to flaw remediation are tested for effectiveness before installation;
firmware updates related to flaw remediation are tested for potential side effects before installation;
security-relevant software updates are installed within {{ insert: param, si-02_odp }} of the release of the updates;
security-relevant firmware updates are installed within {{ insert: param, si-02_odp }} of the release of the updates;
flaw remediation is incorporated into the organizational configuration management process.
System and information integrity policy

system and information integrity procedures

procedures addressing flaw remediation

procedures addressing configuration management

list of flaws and vulnerabilities potentially affecting the system

list of recent security flaw remediation actions performed on the system (e.g., list of installed patches, service packs, hot fixes, and other software updates to correct system flaws)

test results from the installation of software and firmware updates to correct system flaws

installation/change control records for security-relevant software and firmware updates

system security plan

privacy plan

other relevant documents or records
System/network administrators

organizational personnel with information security and privacy responsibilities

organizational personnel responsible for installing, configuring, and/or maintaining the system

organizational personnel responsible for flaw remediation

organizational personnel with configuration management responsibilities
Organizational processes for identifying, reporting, and correcting system flaws

organizational process for installing software and firmware updates

mechanisms supporting and/or implementing the reporting and correcting of system flaws

mechanisms supporting and/or implementing testing software and firmware updates*

---

### Sample Match 9: `MAS-7.3.2.c` ⟷ `NIST-SA-3`

* **Semantic Relation**: `SUPERSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.83` | Dense Sim: `0.60`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0457 (Max Dense Sim: 0.60)
* **Defensible Rationale**:
```text
• MAS Requirement: must implement effective risk mitigation measures for hardware and software approaching their end-of-support date.
• NIST Control: NIST-SA-3 System Development Life Cycle: Acquire, develop, and manage the system using {{ insert: param, sa-03_odp }} that incorporates information security and privacy considerations;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SA-3 provides technical control capabilities addressing obligations in MAS-7.3.2.c.)
```

> **MAS TRM Clause [MAS-7.3.2.c]**:
> *The Financial Institution must implement effective risk mitigation measures for hardware and software approaching their end-of-support date.*

> **NIST SP 800-53 Control [NIST-SA-3 - System Development Life Cycle]**:
> *Acquire, develop, and manage the system using {{ insert: param, sa-03_odp }} that incorporates information security and privacy considerations;
Define and document information security and privacy roles and responsibilities throughout the system development life cycle;
Identify individuals having information security and privacy roles and responsibilities; and
Integrate the organizational information security and privacy risk management process into system development life cycle activities.
A system development life cycle process provides the foundation for the successful development, implementation, and operation of organizational systems. The integration of security and privacy considerations early in the system development life cycle is a foundational principle of systems security engineering and privacy engineering. To apply the required controls within the system development life cycle requires a basic understanding of information security and privacy, threats, vulnerabilities, adverse impacts, and risk to critical mission and business functions. The security engineering principles in [SA-8](#sa-8) help individuals properly design, code, and test systems and system components. Organizations include qualified personnel (e.g., senior agency information security officers, senior agency officials for privacy, security and privacy architects, and security and privacy engineers) in system development life cycle processes to ensure that established security and privacy requirements are incorporated into organizational systems. Role-based security and privacy training programs can ensure that individuals with key security and privacy roles and responsibilities have the experience, skills, and expertise to conduct assigned system development life cycle activities.

The effective integration of security and privacy requirements into enterprise architecture also helps to ensure that important security and privacy considerations are addressed throughout the system life cycle and that those considerations are directly related to organizational mission and business processes. This process also facilitates the integration of the information security and privacy architectures into the enterprise architecture, consistent with the risk management strategy of the organization. Because the system development life cycle involves multiple organizations, (e.g., external suppliers, developers, integrators, service providers), acquisition and supply chain risk management functions and controls play significant roles in the effective management of the system during the life cycle.
the system is acquired, developed, and managed using {{ insert: param, sa-03_odp }} that incorporates information security considerations;
the system is acquired, developed, and managed using {{ insert: param, sa-03_odp }} that incorporates privacy considerations;
information security roles and responsibilities are defined and documented throughout the system development life cycle;
privacy roles and responsibilities are defined and documented throughout the system development life cycle;
individuals with information security roles and responsibilities are identified;
individuals with privacy roles and responsibilities are identified;
organizational information security risk management processes are integrated into system development life cycle activities;
organizational privacy risk management processes are integrated into system development life cycle activities.
System and services acquisition policy

system and services acquisition procedures

procedures addressing the integration of information security and privacy and supply chain risk management into the system development life cycle process

system development life cycle documentation

organizational risk management strategy

information security and privacy risk management strategy documentation

system security plan

privacy plan

privacy program plan

enterprise architecture documentation

role-based security and privacy training program documentation

data mapping documentation

other relevant documents or records
Organizational personnel with information security and privacy responsibilities

organizational personnel with system life cycle development responsibilities

organizational personnel with supply chain risk management responsibilities
Organizational processes for defining and documenting the system development life cycle

organizational processes for identifying system development life cycle roles and responsibilities

organizational processes for integrating information security and privacy and supply chain risk management into the system development life cycle

mechanisms supporting and/or implementing the system development life cycle*

---

### Sample Match 10: `MAS-7.6.1` ⟷ `NIST-AC-5`

* **Semantic Relation**: `SUPERSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.84` | Dense Sim: `0.76`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0782 (Max Dense Sim: 0.76)
* **Defensible Rationale**:
```text
• MAS Requirement: must enforce segregation of duties in the software release process to prevent any single individual from developing, compiling, and moving software codes between environments.
• NIST Control: NIST-AC-5 Separation of Duties: Identify and document {{ insert: param, ac-05_odp }} ; and.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-AC-5 provides technical control capabilities addressing obligations in MAS-7.6.1.)
```

> **MAS TRM Clause [MAS-7.6.1]**:
> *The Financial Institution must enforce segregation of duties in the software release process to prevent any single individual from developing, compiling, and moving software codes between environments.*

> **NIST SP 800-53 Control [NIST-AC-5 - Separation of Duties]**:
> *Identify and document {{ insert: param, ac-05_odp }} ; and
Define system access authorizations to support separation of duties.
Separation of duties addresses the potential for abuse of authorized privileges and helps to reduce the risk of malevolent activity without collusion. Separation of duties includes dividing mission or business functions and support functions among different individuals or roles, conducting system support functions with different individuals, and ensuring that security personnel who administer access control functions do not also administer audit functions. Because separation of duty violations can span systems and application domains, organizations consider the entirety of systems and system components when developing policy on separation of duties. Separation of duties is enforced through the account management activities in [AC-2](#ac-2) , access control mechanisms in [AC-3](#ac-3) , and identity management activities in [IA-2](#ia-2), [IA-4](#ia-4) , and [IA-12](#ia-12).
{{ insert: param, ac-05_odp }} are identified and documented;
system access authorizations to support separation of duties are defined.
Access control policy

procedures addressing divisions of responsibility and separation of duties

system configuration settings and associated documentation

list of divisions of responsibility and separation of duties

system access authorizations

system audit records

system security plan

other relevant documents or records
Organizational personnel with responsibilities for defining appropriate divisions of responsibility and separation of duties

organizational personnel with information security responsibilities

system/network administrators
Mechanisms implementing separation of duties policy*

---

### Sample Match 11: `MAS-7.7.2` ⟷ `NIST-CP-2`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.85` | Dense Sim: `0.62`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0386 (Max Dense Sim: 0.62)
* **Defensible Rationale**:
```text
• MAS Requirement: must allocate sufficient resources to facilitate and support incident response and recovery.
• NIST Control: NIST-CP-2 Contingency Plan: Develop a contingency plan for the system that:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-CP-2 provides technical control capabilities addressing obligations in MAS-7.7.2.)
```

> **MAS TRM Clause [MAS-7.7.2]**:
> *The Financial Institution must allocate sufficient resources to facilitate and support incident response and recovery.*

> **NIST SP 800-53 Control [NIST-CP-2 - Contingency Plan]**:
> *Develop a contingency plan for the system that:
Identifies essential mission and business functions and associated contingency requirements;
Provides recovery objectives, restoration priorities, and metrics;
Addresses contingency roles, responsibilities, assigned individuals with contact information;
Addresses maintaining essential mission and business functions despite a system disruption, compromise, or failure;
Addresses eventual, full system restoration without deterioration of the controls originally planned and implemented;
Addresses the sharing of contingency information; and
Is reviewed and approved by {{ insert: param, cp-2_prm_1 }};
Distribute copies of the contingency plan to {{ insert: param, cp-2_prm_2 }};
Coordinate contingency planning activities with incident handling activities;
Review the contingency plan for the system {{ insert: param, cp-02_odp.05 }};
Update the contingency plan to address changes to the organization, system, or environment of operation and problems encountered during contingency plan implementation, execution, or testing;
Communicate contingency plan changes to {{ insert: param, cp-2_prm_4 }};
Incorporate lessons learned from contingency plan testing, training, or actual contingency activities into contingency testing and training; and
Protect the contingency plan from unauthorized disclosure and modification.
Contingency planning for systems is part of an overall program for achieving continuity of operations for organizational mission and business functions. Contingency planning addresses system restoration and implementation of alternative mission or business processes when systems are compromised or breached. Contingency planning is considered throughout the system development life cycle and is a fundamental part of the system design. Systems can be designed for redundancy, to provide backup capabilities, and for resilience. Contingency plans reflect the degree of restoration required for organizational systems since not all systems need to fully recover to achieve the level of continuity of operations desired. System recovery objectives reflect applicable laws, executive orders, directives, regulations, policies, standards, guidelines, organizational risk tolerance, and system impact level.

Actions addressed in contingency plans include orderly system degradation, system shutdown, fallback to a manual mode, alternate information flows, and operating in modes reserved for when systems are under attack. By coordinating contingency planning with incident handling activities, organizations ensure that the necessary planning activities are in place and activated in the event of an incident. Organizations consider whether continuity of operations during an incident conflicts with the capability to automatically disable the system, as specified in [IR-4(5)](#ir-4.5) . Incident response planning is part of contingency planning for organizations and is addressed in the [IR](#ir) (Incident Response) family.
a contingency plan for the system is developed that identifies essential mission and business functions and associated contingency requirements;
a contingency plan for the system is developed that provides recovery objectives;
a contingency plan for the system is developed that provides restoration priorities;
a contingency plan for the system is developed that provides metrics;
a contingency plan for the system is developed that addresses contingency roles;
a contingency plan for the system is developed that addresses contingency responsibilities;
a contingency plan for the system is developed that addresses assigned individuals with contact information;
a contingency plan for the system is developed that addresses maintaining essential mission and business functions despite a system disruption, compromise, or failure;
a contingency plan for the system is developed that addresses eventual, full-system restoration without deterioration of the controls originally planned and implemented;
a contingency plan for the system is developed that addresses the sharing of contingency information;
a contingency plan for the system is developed that is reviewed by {{ insert: param, cp-02_odp.01 }};
a contingency plan for the system is developed that is approved by {{ insert: param, cp-02_odp.02 }};
copies of the contingency plan are distributed to {{ insert: param, cp-02_odp.03 }};
copies of the contingency plan are distributed to {{ insert: param, cp-02_odp.04 }};
contingency planning activities are coordinated with incident handling activities;
the contingency plan for the system is reviewed {{ insert: param, cp-02_odp.05 }};
the contingency plan is updated to address changes to the organization, system, or environment of operation;
the contingency plan is updated to address problems encountered during contingency plan implementation, execution, or testing;
contingency plan changes are communicated to {{ insert: param, cp-02_odp.06 }};
contingency plan changes are communicated to {{ insert: param, cp-02_odp.07 }};
lessons learned from contingency plan testing or actual contingency activities are incorporated into contingency testing;
lessons learned from contingency plan training or actual contingency activities are incorporated into contingency testing and training;
the contingency plan is protected from unauthorized disclosure;
the contingency plan is protected from unauthorized modification.
Contingency planning policy

procedures addressing contingency operations for the system

contingency plan

evidence of contingency plan reviews and updates

system security plan

other relevant documents or records
Organizational personnel with contingency planning and plan implementation responsibilities

organizational personnel with incident handling responsibilities

organizational personnel with knowledge of requirements for mission and business functions

organizational personnel with information security responsibilities
Organizational processes for contingency plan development, review, update, and protection

mechanisms for developing, reviewing, updating, and/or protecting the contingency plan*

---

### Sample Match 12: `MAS-7.7.3.b` ⟷ `NIST-IR-6`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.83` | Dense Sim: `0.60`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0365 (Max Dense Sim: 0.60)
* **Defensible Rationale**:
```text
• MAS Requirement: must include provisions for the maintenance and protection of supporting evidence for incident investigation and diagnosis in the incident management framework.
• NIST Control: NIST-IR-6 Incident Reporting: Require personnel to report suspected incidents to the organizational incident response capability within {{ insert: param, ir-06_odp.01 }} ; and.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-IR-6 provides technical control capabilities addressing obligations in MAS-7.7.3.b.)
```

> **MAS TRM Clause [MAS-7.7.3.b]**:
> *The Financial Institution must include provisions for the maintenance and protection of supporting evidence for incident investigation and diagnosis in the incident management framework.*

> **NIST SP 800-53 Control [NIST-IR-6 - Incident Reporting]**:
> *Require personnel to report suspected incidents to the organizational incident response capability within {{ insert: param, ir-06_odp.01 }} ; and
Report incident information to {{ insert: param, ir-06_odp.02 }}.
The types of incidents reported, the content and timeliness of the reports, and the designated reporting authorities reflect applicable laws, executive orders, directives, regulations, policies, standards, and guidelines. Incident information can inform risk assessments, control effectiveness assessments, security requirements for acquisitions, and selection criteria for technology products.
personnel is/are required to report suspected incidents to the organizational incident response capability within {{ insert: param, ir-06_odp.01 }};
incident information is reported to {{ insert: param, ir-06_odp.02 }}.
Incident response policy

procedures addressing incident reporting

incident reporting records and documentation

incident response plan

system security plan

privacy plan

other relevant documents or records
Organizational personnel with incident reporting responsibilities

organizational personnel with information security and privacy responsibilities

personnel who have/should have reported incidents

personnel (authorities) to whom incident information is to be reported

system users
Organizational processes for incident reporting

mechanisms supporting and/or implementing incident reporting*

---

### Sample Match 13: `MAS-13.4.2.a` ⟷ `NIST-AU-1`

* **Semantic Relation**: `SUPERSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.82` | Dense Sim: `0.60`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0330 (Max Dense Sim: 0.60)
* **Defensible Rationale**:
```text
• MAS Requirement: must define the objectives, scope, and rules of engagement before the commencement of the exercise.
• NIST Control: NIST-AU-1 Policy and Procedures: Develop, document, and disseminate to {{ insert: param, au-1_prm_1 }}:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-AU-1 provides technical control capabilities addressing obligations in MAS-13.4.2.a.)
```

> **MAS TRM Clause [MAS-13.4.2.a]**:
> *The Financial Institution must define the objectives, scope, and rules of engagement before the commencement of the exercise.*

> **NIST SP 800-53 Control [NIST-AU-1 - Policy and Procedures]**:
> *Develop, document, and disseminate to {{ insert: param, au-1_prm_1 }}:
{{ insert: param, au-01_odp.03 }} audit and accountability policy that:
Addresses purpose, scope, roles, responsibilities, management commitment, coordination among organizational entities, and compliance; and
Is consistent with applicable laws, executive orders, directives, regulations, policies, standards, and guidelines; and
Procedures to facilitate the implementation of the audit and accountability policy and the associated audit and accountability controls;
Designate an {{ insert: param, au-01_odp.04 }} to manage the development, documentation, and dissemination of the audit and accountability policy and procedures; and
Review and update the current audit and accountability:
Policy {{ insert: param, au-01_odp.05 }} and following {{ insert: param, au-01_odp.06 }} ; and
Procedures {{ insert: param, au-01_odp.07 }} and following {{ insert: param, au-01_odp.08 }}.
Audit and accountability policy and procedures address the controls in the AU family that are implemented within systems and organizations. The risk management strategy is an important factor in establishing such policies and procedures. Policies and procedures contribute to security and privacy assurance. Therefore, it is important that security and privacy programs collaborate on the development of audit and accountability policy and procedures. Security and privacy program policies and procedures at the organization level are preferable, in general, and may obviate the need for mission- or system-specific policies and procedures. The policy can be included as part of the general security and privacy policy or be represented by multiple policies that reflect the complex nature of organizations. Procedures can be established for security and privacy programs, for mission or business processes, and for systems, if needed. Procedures describe how the policies or controls are implemented and can be directed at the individual or role that is the object of the procedure. Procedures can be documented in system security and privacy plans or in one or more separate documents. Events that may precipitate an update to audit and accountability policy and procedures include assessment or audit findings, security incidents or breaches, or changes in applicable laws, executive orders, directives, regulations, policies, standards, and guidelines. Simply restating controls does not constitute an organizational policy or procedure.
an audit and accountability policy is developed and documented;
the audit and accountability policy is disseminated to {{ insert: param, au-01_odp.01 }};
audit and accountability procedures to facilitate the implementation of the audit and accountability policy and associated audit and accountability controls are developed and documented;
the audit and accountability procedures are disseminated to {{ insert: param, au-01_odp.02 }};
the {{ insert: param, au-01_odp.03 }} of the audit and accountability policy addresses purpose;
the {{ insert: param, au-01_odp.03 }} of the audit and accountability policy addresses scope;
the {{ insert: param, au-01_odp.03 }} of the audit and accountability policy addresses roles;
the {{ insert: param, au-01_odp.03 }} of the audit and accountability policy addresses responsibilities;
the {{ insert: param, au-01_odp.03 }} of the audit and accountability policy addresses management commitment;
the {{ insert: param, au-01_odp.03 }} of the audit and accountability policy addresses coordination among organizational entities;
the {{ insert: param, au-01_odp.03 }} of the audit and accountability policy addresses compliance;
the {{ insert: param, au-01_odp.03 }} of the audit and accountability policy is consistent with applicable laws, executive orders, directives, regulations, policies, standards, and guidelines;
the {{ insert: param, au-01_odp.04 }} is designated to manage the development, documentation, and dissemination of the audit and accountability policy and procedures;
the current audit and accountability policy is reviewed and updated {{ insert: param, au-01_odp.05 }};
the current audit and accountability policy is reviewed and updated following {{ insert: param, au-01_odp.06 }};
the current audit and accountability procedures are reviewed and updated {{ insert: param, au-01_odp.07 }};
the current audit and accountability procedures are reviewed and updated following {{ insert: param, au-01_odp.08 }}.
Audit and accountability policy and procedures

system security plan

privacy plan

other relevant documents or records
Organizational personnel with audit and accountability responsibilities

organizational personnel with information security and privacy responsibilities*

---

### Sample Match 14: `MAS-13.5.2.a` ⟷ `NIST-PM-7`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.83` | Dense Sim: `0.61`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0330 (Max Dense Sim: 0.61)
* **Defensible Rationale**:
```text
• MAS Requirement: must use threat intelligence relevant to its IT environment to identify threat actors most likely to pose a threat.
• NIST Control: NIST-PM-7 Enterprise Architecture: Develop and maintain an enterprise architecture with consideration for information security, privacy, and the resulting risk to organizational operations and assets, individuals, other organizations, and the Nation..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-7 provides technical control capabilities addressing obligations in MAS-13.5.2.a.)
```

> **MAS TRM Clause [MAS-13.5.2.a]**:
> *The Financial Institution must use threat intelligence relevant to its IT environment to identify threat actors most likely to pose a threat.*

> **NIST SP 800-53 Control [NIST-PM-7 - Enterprise Architecture]**:
> *Develop and maintain an enterprise architecture with consideration for information security, privacy, and the resulting risk to organizational operations and assets, individuals, other organizations, and the Nation.
The integration of security and privacy requirements and controls into the enterprise architecture helps to ensure that security and privacy considerations are addressed throughout the system development life cycle and are explicitly related to the organization’s mission and business processes. The process of security and privacy requirements integration also embeds into the enterprise architecture and the organization’s security and privacy architectures consistent with the organizational risk management strategy. For PM-7, security and privacy architectures are developed at a system-of-systems level, representing all organizational systems. For [PL-8](#pl-8) , the security and privacy architectures are developed at a level that represents an individual system. The system-level architectures are consistent with the security and privacy architectures defined for the organization. Security and privacy requirements and control integration are most effectively accomplished through the rigorous application of the Risk Management Framework [SP 800-37](#482e4c99-9dc4-41ad-bba8-0f3f0032c1f8) and supporting security standards and guidelines.
an enterprise architecture is developed with consideration for information security;
an enterprise architecture is maintained with consideration for information security;
an enterprise architecture is developed with consideration for privacy;
an enterprise architecture is maintained with consideration for privacy;
an enterprise architecture is developed with consideration for the resulting risk to organizational operations and assets, individuals, other organizations, and the Nation;
an enterprise architecture is maintained with consideration for the resulting risk to organizational operations and assets, individuals, other organizations, and the Nation.
Information security program plan

privacy program plan

enterprise architecture documentation

procedures addressing enterprise architecture development

results of risk assessments of enterprise architecture

other relevant documents or records
Organizational personnel with information security and privacy program planning and plan implementation responsibilities

organizational personnel responsible for developing enterprise architecture

organizational personnel responsible for risk assessments of enterprise architecture

organizational personnel with information security and privacy responsibilities
Organizational processes for enterprise architecture development

mechanisms supporting the enterprise architecture and its development*

---

### Sample Match 15: `MAS-13.6.1.a` ⟷ `NIST-CA-2`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `NO_COVERAGE` (Dynamic Confidence: `0.83` | Dense Sim: `0.60`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0300 (Max Dense Sim: 0.60)
* **Defensible Rationale**:
```text
• MAS Requirement: must perform severity assessment and classification of an issue.
• NIST Control: NIST-CA-2 Control Assessments: Select the appropriate assessor or assessment team for the type of assessment to be conducted;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: NO_COVERAGE (NIST-CA-2 provides technical control capabilities addressing obligations in MAS-13.6.1.a.)
```

> **MAS TRM Clause [MAS-13.6.1.a]**:
> *The Financial Institution must perform severity assessment and classification of an issue.*

> **NIST SP 800-53 Control [NIST-CA-2 - Control Assessments]**:
> *Select the appropriate assessor or assessment team for the type of assessment to be conducted;
Develop a control assessment plan that describes the scope of the assessment including:
Controls and control enhancements under assessment;
Assessment procedures to be used to determine control effectiveness; and
Assessment environment, assessment team, and assessment roles and responsibilities;
Ensure the control assessment plan is reviewed and approved by the authorizing official or designated representative prior to conducting the assessment;
Assess the controls in the system and its environment of operation {{ insert: param, ca-02_odp.01 }} to determine the extent to which the controls are implemented correctly, operating as intended, and producing the desired outcome with respect to meeting established security and privacy requirements;
Produce a control assessment report that document the results of the assessment; and
Provide the results of the control assessment to {{ insert: param, ca-02_odp.02 }}.
Organizations ensure that control assessors possess the required skills and technical expertise to develop effective assessment plans and to conduct assessments of system-specific, hybrid, common, and program management controls, as appropriate. The required skills include general knowledge of risk management concepts and approaches as well as comprehensive knowledge of and experience with the hardware, software, and firmware system components implemented.

Organizations assess controls in systems and the environments in which those systems operate as part of initial and ongoing authorizations, continuous monitoring, FISMA annual assessments, system design and development, systems security engineering, privacy engineering, and the system development life cycle. Assessments help to ensure that organizations meet information security and privacy requirements, identify weaknesses and deficiencies in the system design and development process, provide essential information needed to make risk-based decisions as part of authorization processes, and comply with vulnerability mitigation procedures. Organizations conduct assessments on the implemented controls as documented in security and privacy plans. Assessments can also be conducted throughout the system development life cycle as part of systems engineering and systems security engineering processes. The design for controls can be assessed as RFPs are developed, responses assessed, and design reviews conducted. If a design to implement controls and subsequent implementation in accordance with the design are assessed during development, the final control testing can be a simple confirmation utilizing previously completed control assessment and aggregating the outcomes.

Organizations may develop a single, consolidated security and privacy assessment plan for the system or maintain separate plans. A consolidated assessment plan clearly delineates the roles and responsibilities for control assessment. If multiple organizations participate in assessing a system, a coordinated approach can reduce redundancies and associated costs.

Organizations can use other types of assessment activities, such as vulnerability scanning and system monitoring, to maintain the security and privacy posture of systems during the system life cycle. Assessment reports document assessment results in sufficient detail, as deemed necessary by organizations, to determine the accuracy and completeness of the reports and whether the controls are implemented correctly, operating as intended, and producing the desired outcome with respect to meeting requirements. Assessment results are provided to the individuals or roles appropriate for the types of assessments being conducted. For example, assessments conducted in support of authorization decisions are provided to authorizing officials, senior agency officials for privacy, senior agency information security officers, and authorizing official designated representatives.

To satisfy annual assessment requirements, organizations can use assessment results from the following sources: initial or ongoing system authorizations, continuous monitoring, systems engineering processes, or system development life cycle activities. Organizations ensure that assessment results are current, relevant to the determination of control effectiveness, and obtained with the appropriate level of assessor independence. Existing control assessment results can be reused to the extent that the results are still valid and can also be supplemented with additional assessments as needed. After the initial authorizations, organizations assess controls during continuous monitoring. Organizations also establish the frequency for ongoing assessments in accordance with organizational continuous monitoring strategies. External audits, including audits by external entities such as regulatory agencies, are outside of the scope of [CA-2](#ca-2).
an appropriate assessor or assessment team is selected for the type of assessment to be conducted;
a control assessment plan is developed that describes the scope of the assessment, including controls and control enhancements under assessment;
a control assessment plan is developed that describes the scope of the assessment, including assessment procedures to be used to determine control effectiveness;
a control assessment plan is developed that describes the scope of the assessment, including the assessment environment;
a control assessment plan is developed that describes the scope of the assessment, including the assessment team;
a control assessment plan is developed that describes the scope of the assessment, including assessment roles and responsibilities;
the control assessment plan is reviewed and approved by the authorizing official or designated representative prior to conducting the assessment;
controls are assessed in the system and its environment of operation {{ insert: param, ca-02_odp.01 }} to determine the extent to which the controls are implemented correctly, operating as intended, and producing the desired outcome with respect to meeting established security requirements;
controls are assessed in the system and its environment of operation {{ insert: param, ca-02_odp.01 }} to determine the extent to which the controls are implemented correctly, operating as intended, and producing the desired outcome with respect to meeting established privacy requirements;
a control assessment report is produced that documents the results of the assessment;
the results of the control assessment are provided to {{ insert: param, ca-02_odp.02 }}.
Assessment, authorization, and monitoring policy

procedures addressing assessment planning

procedures addressing control assessments

control assessment plan

control assessment report

system security plan

privacy plan

other relevant documents or records
Organizational personnel with control assessment responsibilities

organizational personnel with information security and privacy responsibilities
Mechanisms supporting control assessment, control assessment plan development, and/or control assessment reporting*

---

### Sample Match 16: `MAS-14.1.1` ⟷ `NIST-SA-9`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.86` | Dense Sim: `0.66`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0330 (Max Dense Sim: 0.66)
* **Defensible Rationale**:
```text
• MAS Requirement: must implement security and control measures commensurate with the risk involved to ensure the security of data and online services.
• NIST Control: NIST-SA-9 External System Services: Require that providers of external system services comply with organizational security and privacy requirements and employ the following controls: {{ insert: param, sa-09_odp.01 }};.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SA-9 provides technical control capabilities addressing obligations in MAS-14.1.1.)
```

> **MAS TRM Clause [MAS-14.1.1]**:
> *The Financial Institution must implement security and control measures commensurate with the risk involved to ensure the security of data and online services.*

> **NIST SP 800-53 Control [NIST-SA-9 - External System Services]**:
> *Require that providers of external system services comply with organizational security and privacy requirements and employ the following controls: {{ insert: param, sa-09_odp.01 }};
Define and document organizational oversight and user roles and responsibilities with regard to external system services; and
Employ the following processes, methods, and techniques to monitor control compliance by external service providers on an ongoing basis: {{ insert: param, sa-09_odp.02 }}.
External system services are provided by an external provider, and the organization has no direct control over the implementation of the required controls or the assessment of control effectiveness. Organizations establish relationships with external service providers in a variety of ways, including through business partnerships, contracts, interagency agreements, lines of business arrangements, licensing agreements, joint ventures, and supply chain exchanges. The responsibility for managing risks from the use of external system services remains with authorizing officials. For services external to organizations, a chain of trust requires that organizations establish and retain a certain level of confidence that each provider in the consumer-provider relationship provides adequate protection for the services rendered. The extent and nature of this chain of trust vary based on relationships between organizations and the external providers. Organizations document the basis for the trust relationships so that the relationships can be monitored. External system services documentation includes government, service providers, end user security roles and responsibilities, and service-level agreements. Service-level agreements define the expectations of performance for implemented controls, describe measurable outcomes, and identify remedies and response requirements for identified instances of noncompliance.
providers of external system services comply with organizational security requirements;
providers of external system services comply with organizational privacy requirements;
providers of external system services employ {{ insert: param, sa-09_odp.01 }};
organizational oversight with regard to external system services are defined and documented;
user roles and responsibilities with regard to external system services are defined and documented;
{{ insert: param, sa-09_odp.02 }} are employed to monitor control compliance by external service providers on an ongoing basis.
System and services acquisition policy

system and services acquisition procedures

procedures addressing methods and techniques for monitoring control compliance by external service providers of system services

acquisition documentation

contracts

service level agreements

interagency agreements

licensing agreements

list of organizational security and privacy requirements for external provider services

control assessment results or reports from external providers of system services

system security plan

privacy plan

supply chain risk management plan

other relevant documents or records
Organizational personnel with acquisition responsibilities

external providers of system services

organizational personnel with information security and privacy responsibilities

organizational personnel with supply chain risk management responsibilities
Organizational processes for monitoring security and privacy control compliance by external service providers on an ongoing basis

mechanisms for monitoring security and privacy control compliance by external service providers on an ongoing basis*

---

### Sample Match 17: `MAS-14.1.3` ⟷ `NIST-RA-5`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.84` | Dense Sim: `0.70`)
* **Retrieval Trace**: Multi-Intent RRF: 0.2151 (Max Dense Sim: 0.70)
* **Defensible Rationale**:
```text
• MAS Requirement: must implement adequate measures to minimize exposure of its online financial services to common attack vectors such as code injection attacks, cross-site scripting, man-in-the-middle attacks, DNS hijacking, DDoS, malware, and spoofing attacks.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-14.1.3.)
```

> **MAS TRM Clause [MAS-14.1.3]**:
> *The Financial Institution must implement adequate measures to minimize exposure of its online financial services to common attack vectors such as code injection attacks, cross-site scripting, man-in-the-middle attacks, DNS hijacking, DDoS, malware, and spoofing attacks.*

> **NIST SP 800-53 Control [NIST-RA-5 - Vulnerability Monitoring and Scanning]**:
> *Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;
Employ vulnerability monitoring tools and techniques that facilitate interoperability among tools and automate parts of the vulnerability management process by using standards for:
Enumerating platforms, software flaws, and improper configurations;
Formatting checklists and test procedures; and
Measuring vulnerability impact;
Analyze vulnerability scan reports and results from vulnerability monitoring;
Remediate legitimate vulnerabilities {{ insert: param, ra-05_odp.03 }} in accordance with an organizational assessment of risk;
Share information obtained from the vulnerability monitoring process and control assessments with {{ insert: param, ra-05_odp.04 }} to help eliminate similar vulnerabilities in other systems; and
Employ vulnerability monitoring tools that include the capability to readily update the vulnerabilities to be scanned.
Security categorization of information and systems guides the frequency and comprehensiveness of vulnerability monitoring (including scans). Organizations determine the required vulnerability monitoring for system components, ensuring that the potential sources of vulnerabilities—such as infrastructure components (e.g., switches, routers, guards, sensors), networked printers, scanners, and copiers—are not overlooked. The capability to readily update vulnerability monitoring tools as new vulnerabilities are discovered and announced and as new scanning methods are developed helps to ensure that new vulnerabilities are not missed by employed vulnerability monitoring tools. The vulnerability monitoring tool update process helps to ensure that potential vulnerabilities in the system are identified and addressed as quickly as possible. Vulnerability monitoring and analyses for custom software may require additional approaches, such as static analysis, dynamic analysis, binary analysis, or a hybrid of the three approaches. Organizations can use these analysis approaches in source code reviews and in a variety of tools, including web-based application scanners, static analysis tools, and binary analyzers.

Vulnerability monitoring includes scanning for patch levels; scanning for functions, ports, protocols, and services that should not be accessible to users or devices; and scanning for flow control mechanisms that are improperly configured or operating incorrectly. Vulnerability monitoring may also include continuous vulnerability monitoring tools that use instrumentation to continuously analyze components. Instrumentation-based tools may improve accuracy and may be run throughout an organization without scanning. Vulnerability monitoring tools that facilitate interoperability include tools that are Security Content Automated Protocol (SCAP)-validated. Thus, organizations consider using scanning tools that express vulnerabilities in the Common Vulnerabilities and Exposures (CVE) naming convention and that employ the Open Vulnerability Assessment Language (OVAL) to determine the presence of vulnerabilities. Sources for vulnerability information include the Common Weakness Enumeration (CWE) listing and the National Vulnerability Database (NVD). Control assessments, such as red team exercises, provide additional sources of potential vulnerabilities for which to scan. Organizations also consider using scanning tools that express vulnerability impact by the Common Vulnerability Scoring System (CVSS).

Vulnerability monitoring includes a channel and process for receiving reports of security vulnerabilities from the public at-large. Vulnerability disclosure programs can be as simple as publishing a monitored email address or web form that can receive reports, including notification authorizing good-faith research and disclosure of security vulnerabilities. Organizations generally expect that such research is happening with or without their authorization and can use public vulnerability disclosure channels to increase the likelihood that discovered vulnerabilities are reported directly to the organization for remediation.

Organizations may also employ the use of financial incentives (also known as "bug bounties" ) to further encourage external security researchers to report discovered vulnerabilities. Bug bounty programs can be tailored to the organization’s needs. Bounties can be operated indefinitely or over a defined period of time and can be offered to the general public or to a curated group. Organizations may run public and private bounties simultaneously and could choose to offer partially credentialed access to certain participants in order to evaluate security vulnerabilities from privileged vantage points.
systems and hosted applications are monitored for vulnerabilities {{ insert: param, ra-05_odp.01 }} and when new vulnerabilities potentially affecting the system are identified and reported;
systems and hosted applications are scanned for vulnerabilities {{ insert: param, ra-05_odp.02 }} and when new vulnerabilities potentially affecting the system are identified and reported;
vulnerability monitoring tools and techniques are employed to facilitate interoperability among tools;
vulnerability monitoring tools and techniques are employed to automate parts of the vulnerability management process by using standards for enumerating platforms, software flaws, and improper configurations;
vulnerability monitoring tools and techniques are employed to facilitate interoperability among tools and to automate parts of the vulnerability management process by using standards for formatting checklists and test procedures;
vulnerability monitoring tools and techniques are employed to facilitate interoperability among tools and to automate parts of the vulnerability management process by using standards for measuring vulnerability impact;
vulnerability scan reports and results from vulnerability monitoring are analyzed;
legitimate vulnerabilities are remediated {{ insert: param, ra-05_odp.03 }} in accordance with an organizational assessment of risk;
information obtained from the vulnerability monitoring process and control assessments is shared with {{ insert: param, ra-05_odp.04 }} to help eliminate similar vulnerabilities in other systems;
vulnerability monitoring tools that include the capability to readily update the vulnerabilities to be scanned are employed.
Risk assessment policy

procedures addressing vulnerability scanning

risk assessment

assessment report

vulnerability scanning tools and associated configuration documentation

vulnerability scanning results

patch and vulnerability management records

system security plan

other relevant documents or records
Organizational personnel with risk assessment, control assessment, and vulnerability scanning responsibilities

organizational personnel with vulnerability scan analysis responsibilities

organizational personnel with vulnerability remediation responsibilities

organizational personnel with security responsibilities

system/network administrators
Organizational processes for vulnerability scanning, analysis, remediation, and information sharing

mechanisms supporting and/or implementing vulnerability scanning, analysis, remediation, and information sharing*

---

### Sample Match 18: `MAS-14.1.7` ⟷ `NIST-AC-19`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.83` | Dense Sim: `0.64`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0789 (Max Dense Sim: 0.64)
* **Defensible Rationale**:
```text
• MAS Requirement: must disallow rooted or jailbroken mobile devices from accessing the Financial Institution’s mobile applications to perform financial transactions unless the application is secured within a sandbox or container that insulates it from tampering and interception by malware.
• NIST Control: NIST-AC-19 Access Control for Mobile Devices: Establish configuration requirements, connection requirements, and implementation guidance for organization-controlled mobile devices, to include when such devices are outside of controlled areas; and.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-AC-19 provides technical control capabilities addressing obligations in MAS-14.1.7.)
```

> **MAS TRM Clause [MAS-14.1.7]**:
> *The Financial Institution must disallow rooted or jailbroken mobile devices from accessing the Financial Institution’s mobile applications to perform financial transactions unless the application is secured within a sandbox or container that insulates it from tampering and interception by malware.*

> **NIST SP 800-53 Control [NIST-AC-19 - Access Control for Mobile Devices]**:
> *Establish configuration requirements, connection requirements, and implementation guidance for organization-controlled mobile devices, to include when such devices are outside of controlled areas; and
Authorize the connection of mobile devices to organizational systems.
A mobile device is a computing device that has a small form factor such that it can easily be carried by a single individual; is designed to operate without a physical connection; possesses local, non-removable or removable data storage; and includes a self-contained power source. Mobile device functionality may also include voice communication capabilities, on-board sensors that allow the device to capture information, and/or built-in features for synchronizing local data with remote locations. Examples include smart phones and tablets. Mobile devices are typically associated with a single individual. The processing, storage, and transmission capability of the mobile device may be comparable to or merely a subset of notebook/desktop systems, depending on the nature and intended purpose of the device. Protection and control of mobile devices is behavior or policy-based and requires users to take physical action to protect and control such devices when outside of controlled areas. Controlled areas are spaces for which organizations provide physical or procedural controls to meet the requirements established for protecting information and systems.

Due to the large variety of mobile devices with different characteristics and capabilities, organizational restrictions may vary for the different classes or types of such devices. Usage restrictions and specific implementation guidance for mobile devices include configuration management, device identification and authentication, implementation of mandatory protective software, scanning devices for malicious code, updating virus protection software, scanning for critical software updates and patches, conducting primary operating system (and possibly other resident software) integrity checks, and disabling unnecessary hardware.

Usage restrictions and authorization to connect may vary among organizational systems. For example, the organization may authorize the connection of mobile devices to its network and impose a set of usage restrictions, while a system owner may withhold authorization for mobile device connection to specific applications or impose additional usage restrictions before allowing mobile device connections to a system. Adequate security for mobile devices goes beyond the requirements specified in [AC-19](#ac-19) . Many safeguards for mobile devices are reflected in other controls. [AC-20](#ac-20) addresses mobile devices that are not organization-controlled.
configuration requirements are established for organization-controlled mobile devices, including when such devices are outside of the controlled area;
connection requirements are established for organization-controlled mobile devices, including when such devices are outside of the controlled area;
implementation guidance is established for organization-controlled mobile devices, including when such devices are outside of the controlled area;
the connection of mobile devices to organizational systems is authorized.
Access control policy

procedures addressing access control for mobile device usage (including restrictions)

configuration management plan

system design documentation

system configuration settings and associated documentation

authorizations for mobile device connections to organizational systems

system audit records

system security plan

other relevant documents or records
Organizational personnel using mobile devices to access organizational systems

system/network administrators

organizational personnel with information security responsibilities
Access control capability for mobile device connections to organizational systems

configurations of mobile devices*

---

### Sample Match 19: `MAS-14.2.11.b` ⟷ `NIST-PS-4`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.87` | Dense Sim: `0.63`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0592 (Max Dense Sim: 0.63)
* **Defensible Rationale**:
```text
• MAS Requirement: must implement a process and procedure to revoke and replace authentication credentials and mechanisms that have been compromised.
• NIST Control: NIST-PS-4 Personnel Termination: Upon termination of individual employment:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PS-4 provides technical control capabilities addressing obligations in MAS-14.2.11.b.)
```

> **MAS TRM Clause [MAS-14.2.11.b]**:
> *The Financial Institution must implement a process and procedure to revoke and replace authentication credentials and mechanisms that have been compromised.*

> **NIST SP 800-53 Control [NIST-PS-4 - Personnel Termination]**:
> *Upon termination of individual employment:
Disable system access within {{ insert: param, ps-04_odp.01 }};
Terminate or revoke any authenticators and credentials associated with the individual;
Conduct exit interviews that include a discussion of {{ insert: param, ps-04_odp.02 }};
Retrieve all security-related organizational system-related property; and
Retain access to organizational information and systems formerly controlled by terminated individual.
System property includes hardware authentication tokens, system administration technical manuals, keys, identification cards, and building passes. Exit interviews ensure that terminated individuals understand the security constraints imposed by being former employees and that proper accountability is achieved for system-related property. Security topics at exit interviews include reminding individuals of nondisclosure agreements and potential limitations on future employment. Exit interviews may not always be possible for some individuals, including in cases related to the unavailability of supervisors, illnesses, or job abandonment. Exit interviews are important for individuals with security clearances. The timely execution of termination actions is essential for individuals who have been terminated for cause. In certain situations, organizations consider disabling the system accounts of individuals who are being terminated prior to the individuals being notified.
upon termination of individual employment, system access is disabled within {{ insert: param, ps-04_odp.01 }};
upon termination of individual employment, any authenticators and credentials are terminated or revoked;
upon termination of individual employment, exit interviews that include a discussion of {{ insert: param, ps-04_odp.02 }} are conducted;
upon termination of individual employment, all security-related organizational system-related property is retrieved;
upon termination of individual employment, access to organizational information and systems formerly controlled by the terminated individual are retained.
Personnel security policy

procedures addressing personnel termination

records of personnel termination actions

list of system accounts

records of terminated or revoked authenticators/credentials

records of exit interviews

system security plan

other relevant documents or records
Organizational personnel with personnel security responsibilities

organizational personnel with account management responsibilities

system/network administrators

organizational personnel with information security responsibilities
Organizational processes for personnel termination

mechanisms supporting and/or implementing personnel termination notifications

mechanisms for disabling system access/revoking authenticators*

---

### Sample Match 20: `MAS-15.1.1` ⟷ `NIST-SR-6`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.84` | Dense Sim: `0.62`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0364 (Max Dense Sim: 0.62)
* **Defensible Rationale**:
```text
• MAS Requirement: must conduct IT audit to provide the board of directors and senior management an independent and objective opinion on the adequacy and effectiveness of risk management, governance, and internal controls relative to existing and emerging technology risks.
• NIST Control: NIST-SR-6 Supplier Assessments and Reviews: Assess and review the supply chain-related risks associated with suppliers or contractors and the system, system component, or system service they provide {{ insert: param, sr-06_odp }}..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SR-6 provides technical control capabilities addressing obligations in MAS-15.1.1.)
```

> **MAS TRM Clause [MAS-15.1.1]**:
> *The Financial Institution must conduct IT audit to provide the board of directors and senior management an independent and objective opinion on the adequacy and effectiveness of risk management, governance, and internal controls relative to existing and emerging technology risks.*

> **NIST SP 800-53 Control [NIST-SR-6 - Supplier Assessments and Reviews]**:
> *Assess and review the supply chain-related risks associated with suppliers or contractors and the system, system component, or system service they provide {{ insert: param, sr-06_odp }}.
An assessment and review of supplier risk includes security and supply chain risk management processes, foreign ownership, control or influence (FOCI), and the ability of the supplier to effectively assess subordinate second-tier and third-tier suppliers and contractors. The reviews may be conducted by the organization or by an independent third party. The reviews consider documented processes, documented controls, all-source intelligence, and publicly available information related to the supplier or contractor. Organizations can use open-source information to monitor for indications of stolen information, poor development and quality control practices, information spillage, or counterfeits. In some cases, it may be appropriate or required to share assessment and review results with other organizations in accordance with any applicable rules, policies, or inter-organizational agreements or contracts.
the supply chain-related risks associated with suppliers or contractors and the systems, system components, or system services they provide are assessed and reviewed {{ insert: param, sr-06_odp }}.
Supply chain risk management policy and procedures

supply chain risk management strategy

supply chain risk management plan

system and services acquisition policy

procedures addressing supply chain protection

procedures addressing the integration of information security requirements into the acquisition process

records of supplier due diligence reviews

system security plan

other relevant documents or records
Organizational personnel with system and services acquisition responsibilities

organizational personnel with information security responsibilities

organizational personnel with supply chain protection responsibilities
Organizational processes for conducting supplier reviews

mechanisms supporting and/or implementing supplier reviews*

---

### Sample Match 21: `MAS-15.1.2.a` ⟷ `NIST-RA-8`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.82` | Dense Sim: `0.53`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0322 (Max Dense Sim: 0.53)
* **Defensible Rationale**:
```text
• MAS Requirement: must identify a comprehensive set of auditable areas for technology risk to enable effective risk assessment during audit planning.
• NIST Control: NIST-RA-8 Privacy Impact Assessments: Conduct privacy impact assessments for systems, programs, or other activities before:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-8 provides technical control capabilities addressing obligations in MAS-15.1.2.a.)
```

> **MAS TRM Clause [MAS-15.1.2.a]**:
> *The Financial Institution must identify a comprehensive set of auditable areas for technology risk to enable effective risk assessment during audit planning.*

> **NIST SP 800-53 Control [NIST-RA-8 - Privacy Impact Assessments]**:
> *Conduct privacy impact assessments for systems, programs, or other activities before:
Developing or procuring information technology that processes personally identifiable information; and
Initiating a new collection of personally identifiable information that:
Will be processed using information technology; and
Includes personally identifiable information permitting the physical or virtual (online) contacting of a specific individual, if identical questions have been posed to, or identical reporting requirements imposed on, ten or more individuals, other than agencies, instrumentalities, or employees of the federal government.
A privacy impact assessment is an analysis of how personally identifiable information is handled to ensure that handling conforms to applicable privacy requirements, determine the privacy risks associated with an information system or activity, and evaluate ways to mitigate privacy risks. A privacy impact assessment is both an analysis and a formal document that details the process and the outcome of the analysis.

Organizations conduct and develop a privacy impact assessment with sufficient clarity and specificity to demonstrate that the organization fully considered privacy and incorporated appropriate privacy protections from the earliest stages of the organization’s activity and throughout the information life cycle. In order to conduct a meaningful privacy impact assessment, the organization’s senior agency official for privacy works closely with program managers, system owners, information technology experts, security officials, counsel, and other relevant organization personnel. Moreover, a privacy impact assessment is not a time-restricted activity that is limited to a particular milestone or stage of the information system or personally identifiable information life cycles. Rather, the privacy analysis continues throughout the system and personally identifiable information life cycles. Accordingly, a privacy impact assessment is a living document that organizations update whenever changes to the information technology, changes to the organization’s practices, or other factors alter the privacy risks associated with the use of such information technology.

To conduct the privacy impact assessment, organizations can use security and privacy risk assessments. Organizations may also use other related processes that may have different names, including privacy threshold analyses. A privacy impact assessment can also serve as notice to the public regarding the organization’s practices with respect to privacy. Although conducting and publishing privacy impact assessments may be required by law, organizations may develop such policies in the absence of applicable laws. For federal agencies, privacy impact assessments may be required by [EGOV](#7b0b9634-741a-4335-b6fa-161228c3a76e) ; agencies should consult with their senior agency official for privacy and legal counsel on this requirement and be aware of the statutory exceptions and OMB guidance relating to the provision.
privacy impact assessments are conducted for systems, programs, or other activities before developing or procuring information technology that processes personally identifiable information;
privacy impact assessments are conducted for systems, programs, or other activities before initiating a collection of personally identifiable information that will be processed using information technology;
privacy impact assessments are conducted for systems, programs, or other activities before initiating a collection of personally identifiable information that includes personally identifiable information permitting the physical or virtual (online) contacting of a specific individual, if identical questions have been posed to, or identical reporting requirements imposed on, ten or more individuals, other than agencies, instrumentalities, or employees of the federal government.
Risk assessment policy

security and privacy risk assessment reports

acquisitions documents

system security plan

privacy plan

other relevant documents or records
Organizational personnel with assessment and auditing responsibilities

system/network administrators

system developers

program managers

legal counsel

organizational personnel with security and privacy responsibilities
Organizational processes for assessments and audits

mechanisms/tools supporting and/or implementing assessments and auditing*

---

### Sample Match 22: `MAS-Annex A.A.1.a` ⟷ `NIST-CP-2`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `NO_COVERAGE` (Dynamic Confidence: `0.85` | Dense Sim: `0.58`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0285 (Max Dense Sim: 0.58)
* **Defensible Rationale**:
```text
• MAS Requirement: must build proactive security assurance techniques into the various phases of the software development life cycle.
• NIST Control: NIST-CP-2 Contingency Plan: Develop a contingency plan for the system that:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: NO_COVERAGE (NIST-CP-2 provides technical control capabilities addressing obligations in MAS-Annex A.A.1.a.)
```

> **MAS TRM Clause [MAS-Annex A.A.1.a]**:
> *The Financial Institution must build proactive security assurance techniques into the various phases of the software development life cycle.*

> **NIST SP 800-53 Control [NIST-CP-2 - Contingency Plan]**:
> *Develop a contingency plan for the system that:
Identifies essential mission and business functions and associated contingency requirements;
Provides recovery objectives, restoration priorities, and metrics;
Addresses contingency roles, responsibilities, assigned individuals with contact information;
Addresses maintaining essential mission and business functions despite a system disruption, compromise, or failure;
Addresses eventual, full system restoration without deterioration of the controls originally planned and implemented;
Addresses the sharing of contingency information; and
Is reviewed and approved by {{ insert: param, cp-2_prm_1 }};
Distribute copies of the contingency plan to {{ insert: param, cp-2_prm_2 }};
Coordinate contingency planning activities with incident handling activities;
Review the contingency plan for the system {{ insert: param, cp-02_odp.05 }};
Update the contingency plan to address changes to the organization, system, or environment of operation and problems encountered during contingency plan implementation, execution, or testing;
Communicate contingency plan changes to {{ insert: param, cp-2_prm_4 }};
Incorporate lessons learned from contingency plan testing, training, or actual contingency activities into contingency testing and training; and
Protect the contingency plan from unauthorized disclosure and modification.
Contingency planning for systems is part of an overall program for achieving continuity of operations for organizational mission and business functions. Contingency planning addresses system restoration and implementation of alternative mission or business processes when systems are compromised or breached. Contingency planning is considered throughout the system development life cycle and is a fundamental part of the system design. Systems can be designed for redundancy, to provide backup capabilities, and for resilience. Contingency plans reflect the degree of restoration required for organizational systems since not all systems need to fully recover to achieve the level of continuity of operations desired. System recovery objectives reflect applicable laws, executive orders, directives, regulations, policies, standards, guidelines, organizational risk tolerance, and system impact level.

Actions addressed in contingency plans include orderly system degradation, system shutdown, fallback to a manual mode, alternate information flows, and operating in modes reserved for when systems are under attack. By coordinating contingency planning with incident handling activities, organizations ensure that the necessary planning activities are in place and activated in the event of an incident. Organizations consider whether continuity of operations during an incident conflicts with the capability to automatically disable the system, as specified in [IR-4(5)](#ir-4.5) . Incident response planning is part of contingency planning for organizations and is addressed in the [IR](#ir) (Incident Response) family.
a contingency plan for the system is developed that identifies essential mission and business functions and associated contingency requirements;
a contingency plan for the system is developed that provides recovery objectives;
a contingency plan for the system is developed that provides restoration priorities;
a contingency plan for the system is developed that provides metrics;
a contingency plan for the system is developed that addresses contingency roles;
a contingency plan for the system is developed that addresses contingency responsibilities;
a contingency plan for the system is developed that addresses assigned individuals with contact information;
a contingency plan for the system is developed that addresses maintaining essential mission and business functions despite a system disruption, compromise, or failure;
a contingency plan for the system is developed that addresses eventual, full-system restoration without deterioration of the controls originally planned and implemented;
a contingency plan for the system is developed that addresses the sharing of contingency information;
a contingency plan for the system is developed that is reviewed by {{ insert: param, cp-02_odp.01 }};
a contingency plan for the system is developed that is approved by {{ insert: param, cp-02_odp.02 }};
copies of the contingency plan are distributed to {{ insert: param, cp-02_odp.03 }};
copies of the contingency plan are distributed to {{ insert: param, cp-02_odp.04 }};
contingency planning activities are coordinated with incident handling activities;
the contingency plan for the system is reviewed {{ insert: param, cp-02_odp.05 }};
the contingency plan is updated to address changes to the organization, system, or environment of operation;
the contingency plan is updated to address problems encountered during contingency plan implementation, execution, or testing;
contingency plan changes are communicated to {{ insert: param, cp-02_odp.06 }};
contingency plan changes are communicated to {{ insert: param, cp-02_odp.07 }};
lessons learned from contingency plan testing or actual contingency activities are incorporated into contingency testing;
lessons learned from contingency plan training or actual contingency activities are incorporated into contingency testing and training;
the contingency plan is protected from unauthorized disclosure;
the contingency plan is protected from unauthorized modification.
Contingency planning policy

procedures addressing contingency operations for the system

contingency plan

evidence of contingency plan reviews and updates

system security plan

other relevant documents or records
Organizational personnel with contingency planning and plan implementation responsibilities

organizational personnel with incident handling responsibilities

organizational personnel with knowledge of requirements for mission and business functions

organizational personnel with information security responsibilities
Organizational processes for contingency plan development, review, update, and protection

mechanisms for developing, reviewing, updating, and/or protecting the contingency plan*

---

### Sample Match 23: `MAS-5.1.3` ⟷ `NIST-AC-19`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.82` | Dense Sim: `0.54`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0269 (Max Dense Sim: 0.54)
* **Defensible Rationale**:
```text
• MAS Requirement: must enable strict security policies within the virtual environment to restrict the copying and use of peripheral devices and prevent data leakage.
• NIST Control: NIST-AC-19 Access Control for Mobile Devices: Establish configuration requirements, connection requirements, and implementation guidance for organization-controlled mobile devices, to include when such devices are outside of controlled areas; and.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-AC-19 provides technical control capabilities addressing obligations in MAS-5.1.3.)
```

> **MAS TRM Clause [MAS-5.1.3]**:
> *The Financial Institution must enable strict security policies within the virtual environment to restrict the copying and use of peripheral devices and prevent data leakage.*

> **NIST SP 800-53 Control [NIST-AC-19 - Access Control for Mobile Devices]**:
> *Establish configuration requirements, connection requirements, and implementation guidance for organization-controlled mobile devices, to include when such devices are outside of controlled areas; and
Authorize the connection of mobile devices to organizational systems.
A mobile device is a computing device that has a small form factor such that it can easily be carried by a single individual; is designed to operate without a physical connection; possesses local, non-removable or removable data storage; and includes a self-contained power source. Mobile device functionality may also include voice communication capabilities, on-board sensors that allow the device to capture information, and/or built-in features for synchronizing local data with remote locations. Examples include smart phones and tablets. Mobile devices are typically associated with a single individual. The processing, storage, and transmission capability of the mobile device may be comparable to or merely a subset of notebook/desktop systems, depending on the nature and intended purpose of the device. Protection and control of mobile devices is behavior or policy-based and requires users to take physical action to protect and control such devices when outside of controlled areas. Controlled areas are spaces for which organizations provide physical or procedural controls to meet the requirements established for protecting information and systems.

Due to the large variety of mobile devices with different characteristics and capabilities, organizational restrictions may vary for the different classes or types of such devices. Usage restrictions and specific implementation guidance for mobile devices include configuration management, device identification and authentication, implementation of mandatory protective software, scanning devices for malicious code, updating virus protection software, scanning for critical software updates and patches, conducting primary operating system (and possibly other resident software) integrity checks, and disabling unnecessary hardware.

Usage restrictions and authorization to connect may vary among organizational systems. For example, the organization may authorize the connection of mobile devices to its network and impose a set of usage restrictions, while a system owner may withhold authorization for mobile device connection to specific applications or impose additional usage restrictions before allowing mobile device connections to a system. Adequate security for mobile devices goes beyond the requirements specified in [AC-19](#ac-19) . Many safeguards for mobile devices are reflected in other controls. [AC-20](#ac-20) addresses mobile devices that are not organization-controlled.
configuration requirements are established for organization-controlled mobile devices, including when such devices are outside of the controlled area;
connection requirements are established for organization-controlled mobile devices, including when such devices are outside of the controlled area;
implementation guidance is established for organization-controlled mobile devices, including when such devices are outside of the controlled area;
the connection of mobile devices to organizational systems is authorized.
Access control policy

procedures addressing access control for mobile device usage (including restrictions)

configuration management plan

system design documentation

system configuration settings and associated documentation

authorizations for mobile device connections to organizational systems

system audit records

system security plan

other relevant documents or records
Organizational personnel using mobile devices to access organizational systems

system/network administrators

organizational personnel with information security responsibilities
Access control capability for mobile device connections to organizational systems

configurations of mobile devices*

---

### Sample Match 24: `MAS-C.1.4` ⟷ `NIST-SC-35`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.84` | Dense Sim: `0.69`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0906 (Max Dense Sim: 0.69)
* **Defensible Rationale**:
```text
• MAS Requirement: must implement anti-hooking or anti-tampering mechanisms to prevent the injection of malicious code that could alter or monitor application behaviour at runtime.
• NIST Control: NIST-SC-35 External Malicious Code Identification: Include system components that proactively seek to identify network-based malicious code or malicious websites..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SC-35 provides technical control capabilities addressing obligations in MAS-C.1.4.)
```

> **MAS TRM Clause [MAS-C.1.4]**:
> *The Financial Institution must implement anti-hooking or anti-tampering mechanisms to prevent the injection of malicious code that could alter or monitor application behaviour at runtime.*

> **NIST SP 800-53 Control [NIST-SC-35 - External Malicious Code Identification]**:
> *Include system components that proactively seek to identify network-based malicious code or malicious websites.
External malicious code identification differs from decoys in [SC-26](#sc-26) in that the components actively probe networks, including the Internet, in search of malicious code contained on external websites. Like decoys, the use of external malicious code identification techniques requires some supporting isolation measures to ensure that any malicious code discovered during the search and subsequently executed does not infect organizational systems. Virtualization is a common technique for achieving such isolation.
system components that proactively seek to identify network-based malicious code or malicious websites are included.
System and communications protection policy

procedures addressing external malicious code identification

system design documentation

system configuration settings and associated documentation

system components deployed to identify malicious websites and/or web-based malicious code

system audit records

system security plan

other relevant documents or records
System/network administrators

organizational personnel with information security responsibilities

organizational personnel installing, configuring, and/or maintaining the system

system developers/integrators
Automated mechanisms supporting and/or implementing external malicious code identification*

---

### Sample Match 25: `MAS-C.1.7` ⟷ `NIST-SC-17`

* **Semantic Relation**: `SUPERSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.84` | Dense Sim: `0.64`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0410 (Max Dense Sim: 0.64)
* **Defensible Rationale**:
```text
• MAS Requirement: must implement certificate or public key pinning to protect against man-in-the-middle attacks.
• NIST Control: NIST-SC-17 Public Key Infrastructure Certificates: Issue public key certificates under an {{ insert: param, sc-17_odp }} or obtain public key certificates from an approved service provider; and.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SC-17 provides technical control capabilities addressing obligations in MAS-C.1.7.)
```

> **MAS TRM Clause [MAS-C.1.7]**:
> *The Financial Institution must implement certificate or public key pinning to protect against man-in-the-middle attacks.*

> **NIST SP 800-53 Control [NIST-SC-17 - Public Key Infrastructure Certificates]**:
> *Issue public key certificates under an {{ insert: param, sc-17_odp }} or obtain public key certificates from an approved service provider; and
Include only approved trust anchors in trust stores or certificate stores managed by the organization.
Public key infrastructure (PKI) certificates are certificates with visibility external to organizational systems and certificates related to the internal operations of systems, such as application-specific time services. In cryptographic systems with a hierarchical structure, a trust anchor is an authoritative source (i.e., a certificate authority) for which trust is assumed and not derived. A root certificate for a PKI system is an example of a trust anchor. A trust store or certificate store maintains a list of trusted root certificates.
public key certificates are issued under {{ insert: param, sc-17_odp }} , or public key certificates are obtained from an approved service provider;
only approved trust anchors are included in trust stores or certificate stores managed by the organization.
System and communications protection policy

procedures addressing public key infrastructure certificates

public key certificate policy or policies

public key issuing process

system security plan

other relevant documents or records
System/network administrators

organizational personnel with information security responsibilities

organizational personnel with responsibilities for issuing public key certificates

service providers
Mechanisms supporting and/or implementing the management of public key infrastructure certificates*

---

## Section C: True Regulatory Gaps (Retail Banking Consumer & Unmatched Obligations)

Total True Regulatory Gaps: **5** (5.9%)

### Regulatory Gap 1: `MAS-14.3.3.a`

> **MAS TRM Statement**:
> *The Financial Institution must notify customers of suspicious activities or funds transfers exceeding a threshold defined by the Financial Institution or the customers.*

* **Audit Analysis**: Direct external customer communication, advisory, or banking consumer protection requirement. No federal information system equivalent exists in NIST SP 800-53 Rev 5.

---

### Regulatory Gap 2: `MAS-14.3.3.b`

> **MAS TRM Statement**:
> *The Financial Institution must include meaningful information, such as transaction type and payment amount, along with instructions to report suspicious or unauthorized transactions, in customer notifications.*

* **Audit Analysis**: Direct external customer communication, advisory, or banking consumer protection requirement. No federal information system equivalent exists in NIST SP 800-53 Rev 5.

---

### Regulatory Gap 3: `MAS-14.4.1.a`

> **MAS TRM Statement**:
> *The Financial Institution must inform customers of security best practices to adopt when using online financial services.*

* **Audit Analysis**: Direct external customer communication, advisory, or banking consumer protection requirement. No federal information system equivalent exists in NIST SP 800-53 Rev 5.

---

### Regulatory Gap 4: `MAS-14.4.2`

> **MAS TRM Statement**:
> *The Financial Institution must alert customers on a timely basis to new cyber threats so they can take precautionary measures.*

* **Audit Analysis**: Direct external customer communication, advisory, or banking consumer protection requirement. No federal information system equivalent exists in NIST SP 800-53 Rev 5.

---

### Regulatory Gap 5: `MAS-14.4.3`

> **MAS TRM Statement**:
> *The Financial Institution must advise customers on means to detect unauthorized transactions and to report security issues, suspicious activities, or suspected fraud promptly.*

* **Audit Analysis**: Direct external customer communication, advisory, or banking consumer protection requirement. No federal information system equivalent exists in NIST SP 800-53 Rev 5.

---

## Section D: 5 Sample MAS Obligations with Multiple Matches (1-to-N Mapping Clusters)

### Cluster 1: `MAS-1.3.a` maps to 15 NIST Controls

> **MAS TRM Statement [MAS-1.3.a]**:
> *The Financial Institution must evaluate its exposure to technology risks.*

#### Control 1: `NIST-RA-6` (Technical Surveillance Countermeasures Survey)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-RA-6 Technical Surveillance Countermeasures Survey: Employ a technical surveillance countermeasures survey at {{ insert: param, ra-06_odp.01 }} {{ insert: param, ra-06_odp.02 }}..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-6 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Employ a technical surveillance countermeasures survey at {{ insert: param, ra-06_odp.01 }} {{ insert: param, ra-06_odp.02 }}.
A technical surveillance countermeasures survey is a service provided by qualified personnel to detect the presence of tech...*

#### Control 2: `NIST-RA-8` (Privacy Impact Assessments)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.88`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-RA-8 Privacy Impact Assessments: Conduct privacy impact assessments for systems, programs, or other activities before:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-8 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Conduct privacy impact assessments for systems, programs, or other activities before:
Developing or procuring information technology that processes personally identifiable information; and
Initiating a new collection of personally identifiable inform...*

#### Control 3: `NIST-RA-3` (Risk Assessment)
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Dyn Conf: `0.81`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: FULL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Conduct a risk assessment, including:
Identifying threats to and vulnerabilities in the system;
Determining the likelihood and magnitude of harm from unauthorized access, use, disclosure, disruption, modification, or destruction of the system, the in...*

#### Control 4: `NIST-SI-20` (Tainting)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.81`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-SI-20 Tainting: Embed data or capabilities in the following systems or system components to determine if organizational data has been exfiltrated or improperly removed from the organization: {{ insert: param, si-20_odp }}..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SI-20 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Embed data or capabilities in the following systems or system components to determine if organizational data has been exfiltrated or improperly removed from the organization: {{ insert: param, si-20_odp }}.
Many cyber-attacks target organizational in...*

#### Control 5: `NIST-RA-5` (Vulnerability Monitoring and Scanning)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;
Employ vulnerability monitoring tools and techniques...*

#### Control 6: `NIST-SR-6` (Supplier Assessments and Reviews)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-SR-6 Supplier Assessments and Reviews: Assess and review the supply chain-related risks associated with suppliers or contractors and the system, system component, or system service they provide {{ insert: param, sr-06_odp }}..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SR-6 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Assess and review the supply chain-related risks associated with suppliers or contractors and the system, system component, or system service they provide {{ insert: param, sr-06_odp }}.
An assessment and review of supplier risk includes security and...*

#### Control 7: `NIST-PM-30` (Supply Chain Risk Management Strategy)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-PM-30 Supply Chain Risk Management Strategy: Develop an organization-wide strategy for managing supply chain risks associated with the development, acquisition, maintenance, and disposal of systems, system components, and system services;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-30 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Develop an organization-wide strategy for managing supply chain risks associated with the development, acquisition, maintenance, and disposal of systems, system components, and system services;
Implement the supply chain risk management strategy cons...*

#### Control 8: `NIST-SR-2` (Supply Chain Risk Management Plan)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.85`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-SR-2 Supply Chain Risk Management Plan: Develop a plan for managing supply chain risks associated with the research and development, design, manufacturing, acquisition, delivery, integration, operations and maintenance, and disposal of the following systems, system components or system services: {{ insert: param, sr-02_odp.01 }};.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SR-2 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Develop a plan for managing supply chain risks associated with the research and development, design, manufacturing, acquisition, delivery, integration, operations and maintenance, and disposal of the following systems, system components or system ser...*

#### Control 9: `NIST-SC-8` (Transmission Confidentiality and Integrity)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.80`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-SC-8 Transmission Confidentiality and Integrity: Protect the {{ insert: param, sc-08_odp }} of transmitted information..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SC-8 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Protect the {{ insert: param, sc-08_odp }} of transmitted information.
Protecting the confidentiality and integrity of transmitted information applies to internal and external networks as well as any system components that can transmit information, i...*

#### Control 10: `NIST-CM-4` (Impact Analyses)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-CM-4 Impact Analyses: Analyze changes to the system to determine potential security and privacy impacts prior to change implementation..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-CM-4 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Analyze changes to the system to determine potential security and privacy impacts prior to change implementation.
Organizational personnel with security or privacy responsibilities conduct impact analyses. Individuals conducting impact analyses posse...*

#### Control 11: `NIST-PM-4` (Plan of Action and Milestones Process)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-PM-4 Plan of Action and Milestones Process: Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-4 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:
Are developed and maintained;
Document the remedial information ...*

#### Control 12: `NIST-PM-7` (Enterprise Architecture)
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.80`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-PM-7 Enterprise Architecture: Develop and maintain an enterprise architecture with consideration for information security, privacy, and the resulting risk to organizational operations and assets, individuals, other organizations, and the Nation..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-7 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Develop and maintain an enterprise architecture with consideration for information security, privacy, and the resulting risk to organizational operations and assets, individuals, other organizations, and the Nation.
The integration of security and pr...*

#### Control 13: `NIST-SA-2` (Allocation of Resources)
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-SA-2 Allocation of Resources: Determine the high-level information security and privacy requirements for the system or system service in mission and business process planning;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SA-2 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Determine the high-level information security and privacy requirements for the system or system service in mission and business process planning;
Determine, document, and allocate the resources required to protect the system or system service as part...*

#### Control 14: `NIST-SI-19` (De-identification)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-SI-19 De-identification: Remove the following elements of personally identifiable information from datasets: {{ insert: param, si-19_odp.01 }} ; and.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SI-19 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Remove the following elements of personally identifiable information from datasets: {{ insert: param, si-19_odp.01 }} ; and
Evaluate {{ insert: param, si-19_odp.02 }} for effectiveness of de-identification.
De-identification is the general term for t...*

#### Control 15: `NIST-PT-4` (Consent)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-PT-4 Consent: Implement {{ insert: param, pt-04_odp }} for individuals to consent to the processing of their personally identifiable information prior to its collection that facilitate individuals’ informed decision-making..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PT-4 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Implement {{ insert: param, pt-04_odp }} for individuals to consent to the processing of their personally identifiable information prior to its collection that facilitate individuals’ informed decision-making.
Consent allows individuals to participat...*

---

### Cluster 2: `MAS-1.3.b` maps to 15 NIST Controls

> **MAS TRM Statement [MAS-1.3.b]**:
> *The Financial Institution must implement a robust risk management framework to ensure IT and cyber resilience.*

#### Control 1: `NIST-SA-24` (Design For Cyber Resiliency)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.88`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-SA-24 Design For Cyber Resiliency: Design organizational systems, system components, or system services to achieve cyber resiliency by:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SA-24 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *Design organizational systems, system components, or system services to achieve cyber resiliency by:
Defining the following cyber resiliency goals: {{ insert: param, sa-24_odp.01 }}.
Defining the following cyber resiliency objectives: {{ insert: para...*

#### Control 2: `NIST-PM-9` (Risk Management Strategy)
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Dyn Conf: `0.86`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-PM-9 Risk Management Strategy: Develops a comprehensive strategy to manage:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: FULL_COVERAGE (NIST-PM-9 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *Develops a comprehensive strategy to manage:
Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and
Privacy risk to individuals resu...*

#### Control 3: `NIST-PM-7` (Enterprise Architecture)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.85`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-PM-7 Enterprise Architecture: Develop and maintain an enterprise architecture with consideration for information security, privacy, and the resulting risk to organizational operations and assets, individuals, other organizations, and the Nation..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-7 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *Develop and maintain an enterprise architecture with consideration for information security, privacy, and the resulting risk to organizational operations and assets, individuals, other organizations, and the Nation.
The integration of security and pr...*

#### Control 4: `NIST-PM-4` (Plan of Action and Milestones Process)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.85`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-PM-4 Plan of Action and Milestones Process: Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-4 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:
Are developed and maintained;
Document the remedial information ...*

#### Control 5: `NIST-CP-2` (Contingency Plan)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-CP-2 Contingency Plan: Develop a contingency plan for the system that:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-CP-2 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *Develop a contingency plan for the system that:
Identifies essential mission and business functions and associated contingency requirements;
Provides recovery objectives, restoration priorities, and metrics;
Addresses contingency roles, responsibilit...*

#### Control 6: `NIST-RA-3` (Risk Assessment)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.85`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *Conduct a risk assessment, including:
Identifying threats to and vulnerabilities in the system;
Determining the likelihood and magnitude of harm from unauthorized access, use, disclosure, disruption, modification, or destruction of the system, the in...*

#### Control 7: `NIST-PM-14` (Testing, Training, and Monitoring)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.85`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-PM-14 Testing, Training, and Monitoring: Implement a process for ensuring that organizational plans for conducting security and privacy testing, training, and monitoring activities associated with organizational systems:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-14 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *Implement a process for ensuring that organizational plans for conducting security and privacy testing, training, and monitoring activities associated with organizational systems:
Are developed and maintained; and
Continue to be executed; and
Review ...*

#### Control 8: `NIST-RA-9` (Criticality Analysis)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.86`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-RA-9 Criticality Analysis: Identify critical system components and functions by performing a criticality analysis for {{ insert: param, ra-09_odp.01 }} at {{ insert: param, ra-09_odp.02 }}..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-9 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *Identify critical system components and functions by performing a criticality analysis for {{ insert: param, ra-09_odp.01 }} at {{ insert: param, ra-09_odp.02 }}.
Not all system components, functions, or services necessarily require significant prote...*

#### Control 9: `NIST-PM-29` (Risk Management Program Leadership Roles)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-PM-29 Risk Management Program Leadership Roles: Appoint a Senior Accountable Official for Risk Management to align organizational information security and privacy management processes with strategic, operational, and budgetary planning processes; and.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-29 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *Appoint a Senior Accountable Official for Risk Management to align organizational information security and privacy management processes with strategic, operational, and budgetary planning processes; and
Establish a Risk Executive (function) to view a...*

#### Control 10: `NIST-RA-5` (Vulnerability Monitoring and Scanning)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;
Employ vulnerability monitoring tools and techniques...*

#### Control 11: `NIST-RA-7` (Risk Response)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-RA-7 Risk Response: Respond to findings from security and privacy assessments, monitoring, and audits in accordance with organizational risk tolerance..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-7 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *Respond to findings from security and privacy assessments, monitoring, and audits in accordance with organizational risk tolerance.
Organizations have many options for responding to risk including mitigating risk by implementing new controls or stren...*

#### Control 12: `NIST-PL-8` (Security and Privacy Architectures)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-PL-8 Security and Privacy Architectures: Develop security and privacy architectures for the system that:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PL-8 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *Develop security and privacy architectures for the system that:
Describe the requirements and approach to be taken for protecting the confidentiality, integrity, and availability of organizational information;
Describe the requirements and approach t...*

#### Control 13: `NIST-CP-11` (Alternate Communications Protocols)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-CP-11 Alternate Communications Protocols: Provide the capability to employ {{ insert: param, cp-11_odp }} in support of maintaining continuity of operations..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-CP-11 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *Provide the capability to employ {{ insert: param, cp-11_odp }} in support of maintaining continuity of operations.
Contingency plans and the contingency training or testing associated with those plans incorporate an alternate communications protocol...*

#### Control 14: `NIST-SC-8` (Transmission Confidentiality and Integrity)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-SC-8 Transmission Confidentiality and Integrity: Protect the {{ insert: param, sc-08_odp }} of transmitted information..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SC-8 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *Protect the {{ insert: param, sc-08_odp }} of transmitted information.
Protecting the confidentiality and integrity of transmitted information applies to internal and external networks as well as any system components that can transmit information, i...*

#### Control 15: `NIST-SA-3` (System Development Life Cycle)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-SA-3 System Development Life Cycle: Acquire, develop, and manage the system using {{ insert: param, sa-03_odp }} that incorporates information security and privacy considerations;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SA-3 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *Acquire, develop, and manage the system using {{ insert: param, sa-03_odp }} that incorporates information security and privacy considerations;
Define and document information security and privacy roles and responsibilities throughout the system deve...*

---

### Cluster 3: `MAS-1.4(a).1` maps to 14 NIST Controls

> **MAS TRM Statement [MAS-1.4(a).1]**:
> *The Board of Directors and Senior Management must cultivate a strong risk culture.*

#### Control 1: `NIST-PM-29` (Risk Management Program Leadership Roles)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.86`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-PM-29 Risk Management Program Leadership Roles: Appoint a Senior Accountable Official for Risk Management to align organizational information security and privacy management processes with strategic, operational, and budgetary planning processes; and.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-29 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Appoint a Senior Accountable Official for Risk Management to align organizational information security and privacy management processes with strategic, operational, and budgetary planning processes; and
Establish a Risk Executive (function) to view a...*

#### Control 2: `NIST-PM-9` (Risk Management Strategy)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-PM-9 Risk Management Strategy: Develops a comprehensive strategy to manage:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-9 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Develops a comprehensive strategy to manage:
Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and
Privacy risk to individuals resu...*

#### Control 3: `NIST-PM-19` (Privacy Program Leadership Role)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-PM-19 Privacy Program Leadership Role: Appoint a senior agency official for privacy with the authority, mission, accountability, and resources to coordinate, develop, and implement, applicable privacy requirements and manage privacy risks through the organization-wide privacy program..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-19 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Appoint a senior agency official for privacy with the authority, mission, accountability, and resources to coordinate, develop, and implement, applicable privacy requirements and manage privacy risks through the organization-wide privacy program.
The...*

#### Control 4: `NIST-PM-28` (Risk Framing)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-PM-28 Risk Framing: Identify and document:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-28 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Identify and document:
Assumptions affecting risk assessments, risk responses, and risk monitoring;
Constraints affecting risk assessments, risk responses, and risk monitoring;
Priorities and trade-offs considered by the organization for managing ris...*

#### Control 5: `NIST-CA-6` (Authorization)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-CA-6 Authorization: Assign a senior official as the authorizing official for the system;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-CA-6 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Assign a senior official as the authorizing official for the system;
Assign a senior official as the authorizing official for common controls available for inheritance by organizational systems;
Ensure that the authorizing official for the system, be...*

#### Control 6: `NIST-PM-2` (Information Security Program Leadership Role)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.81`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-PM-2 Information Security Program Leadership Role: Appoint a senior agency information security officer with the mission and resources to coordinate, develop, implement, and maintain an organization-wide information security program..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-2 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Appoint a senior agency information security officer with the mission and resources to coordinate, develop, implement, and maintain an organization-wide information security program.
The senior agency information security officer is an organizational...*

#### Control 7: `NIST-PM-4` (Plan of Action and Milestones Process)
- **Semantic Relation**: `SUPPORTS` | **Assurance Coverage**: `NO_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-PM-4 Plan of Action and Milestones Process: Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: NO_COVERAGE (NIST-PM-4 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:
Are developed and maintained;
Document the remedial information ...*

#### Control 8: `NIST-SA-3` (System Development Life Cycle)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-SA-3 System Development Life Cycle: Acquire, develop, and manage the system using {{ insert: param, sa-03_odp }} that incorporates information security and privacy considerations;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SA-3 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Acquire, develop, and manage the system using {{ insert: param, sa-03_odp }} that incorporates information security and privacy considerations;
Define and document information security and privacy roles and responsibilities throughout the system deve...*

#### Control 9: `NIST-PM-30` (Supply Chain Risk Management Strategy)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-PM-30 Supply Chain Risk Management Strategy: Develop an organization-wide strategy for managing supply chain risks associated with the development, acquisition, maintenance, and disposal of systems, system components, and system services;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-30 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Develop an organization-wide strategy for managing supply chain risks associated with the development, acquisition, maintenance, and disposal of systems, system components, and system services;
Implement the supply chain risk management strategy cons...*

#### Control 10: `NIST-PM-14` (Testing, Training, and Monitoring)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-PM-14 Testing, Training, and Monitoring: Implement a process for ensuring that organizational plans for conducting security and privacy testing, training, and monitoring activities associated with organizational systems:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-14 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Implement a process for ensuring that organizational plans for conducting security and privacy testing, training, and monitoring activities associated with organizational systems:
Are developed and maintained; and
Continue to be executed; and
Review ...*

#### Control 11: `NIST-PM-12` (Insider Threat Program)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.81`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-PM-12 Insider Threat Program: Implement an insider threat program that includes a cross-discipline insider threat incident handling team..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-12 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Implement an insider threat program that includes a cross-discipline insider threat incident handling team.
Organizations that handle classified information are required, under Executive Order 13587 [EO 13587](#0af071a6-cf8e-48ee-8c82-fe91efa20f94) a...*

#### Control 12: `NIST-PS-2` (Position Risk Designation)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-PS-2 Position Risk Designation: Assign a risk designation to all organizational positions;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PS-2 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Assign a risk designation to all organizational positions;
Establish screening criteria for individuals filling those positions; and
Review and update position risk designations {{ insert: param, ps-02_odp }}.
Position risk designations reflect Offic...*

#### Control 13: `NIST-PM-31` (Continuous Monitoring Strategy)
- **Semantic Relation**: `SUPPORTS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-PM-31 Continuous Monitoring Strategy: Develop an organization-wide continuous monitoring strategy and implement continuous monitoring programs that include:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-31 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Develop an organization-wide continuous monitoring strategy and implement continuous monitoring programs that include:
Establishing the following organization-wide metrics to be monitored: {{ insert: param, pm-31_odp.01 }};
Establishing {{ insert: pa...*

#### Control 14: `NIST-SR-2` (Supply Chain Risk Management Plan)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-SR-2 Supply Chain Risk Management Plan: Develop a plan for managing supply chain risks associated with the research and development, design, manufacturing, acquisition, delivery, integration, operations and maintenance, and disposal of the following systems, system components or system services: {{ insert: param, sr-02_odp.01 }};.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SR-2 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Develop a plan for managing supply chain risks associated with the research and development, design, manufacturing, acquisition, delivery, integration, operations and maintenance, and disposal of the following systems, system components or system ser...*

---

### Cluster 4: `MAS-1.4(a).2` maps to 13 NIST Controls

> **MAS TRM Statement [MAS-1.4(a).2]**:
> *The Board of Directors and Senior Management must establish a sound and robust technology risk management framework.*

#### Control 1: `NIST-PM-29` (Risk Management Program Leadership Roles)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.85`)
- **Rationale**:
```text
• MAS Requirement: must establish a sound and robust technology risk management framework.
• NIST Control: NIST-PM-29 Risk Management Program Leadership Roles: Appoint a Senior Accountable Official for Risk Management to align organizational information security and privacy management processes with strategic, operational, and budgetary planning processes; and.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-29 provides technical control capabilities addressing obligations in MAS-1.4(a).2.)
```
> *Appoint a Senior Accountable Official for Risk Management to align organizational information security and privacy management processes with strategic, operational, and budgetary planning processes; and
Establish a Risk Executive (function) to view a...*

#### Control 2: `NIST-PM-9` (Risk Management Strategy)
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must establish a sound and robust technology risk management framework.
• NIST Control: NIST-PM-9 Risk Management Strategy: Develops a comprehensive strategy to manage:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: FULL_COVERAGE (NIST-PM-9 provides technical control capabilities addressing obligations in MAS-1.4(a).2.)
```
> *Develops a comprehensive strategy to manage:
Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and
Privacy risk to individuals resu...*

#### Control 3: `NIST-SR-2` (Supply Chain Risk Management Plan)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must establish a sound and robust technology risk management framework.
• NIST Control: NIST-SR-2 Supply Chain Risk Management Plan: Develop a plan for managing supply chain risks associated with the research and development, design, manufacturing, acquisition, delivery, integration, operations and maintenance, and disposal of the following systems, system components or system services: {{ insert: param, sr-02_odp.01 }};.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SR-2 provides technical control capabilities addressing obligations in MAS-1.4(a).2.)
```
> *Develop a plan for managing supply chain risks associated with the research and development, design, manufacturing, acquisition, delivery, integration, operations and maintenance, and disposal of the following systems, system components or system ser...*

#### Control 4: `NIST-PM-23` (Data Governance Body)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must establish a sound and robust technology risk management framework.
• NIST Control: NIST-PM-23 Data Governance Body: Establish a Data Governance Body consisting of {{ insert: param, pm-23_odp.01 }} with {{ insert: param, pm-23_odp.02 }}..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-23 provides technical control capabilities addressing obligations in MAS-1.4(a).2.)
```
> *Establish a Data Governance Body consisting of {{ insert: param, pm-23_odp.01 }} with {{ insert: param, pm-23_odp.02 }}.
A Data Governance Body can help ensure that the organization has coherent policies and the ability to balance the utility of data...*

#### Control 5: `NIST-PM-7` (Enterprise Architecture)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must establish a sound and robust technology risk management framework.
• NIST Control: NIST-PM-7 Enterprise Architecture: Develop and maintain an enterprise architecture with consideration for information security, privacy, and the resulting risk to organizational operations and assets, individuals, other organizations, and the Nation..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-7 provides technical control capabilities addressing obligations in MAS-1.4(a).2.)
```
> *Develop and maintain an enterprise architecture with consideration for information security, privacy, and the resulting risk to organizational operations and assets, individuals, other organizations, and the Nation.
The integration of security and pr...*

#### Control 6: `NIST-RA-3` (Risk Assessment)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must establish a sound and robust technology risk management framework.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-1.4(a).2.)
```
> *Conduct a risk assessment, including:
Identifying threats to and vulnerabilities in the system;
Determining the likelihood and magnitude of harm from unauthorized access, use, disclosure, disruption, modification, or destruction of the system, the in...*

#### Control 7: `NIST-PM-28` (Risk Framing)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must establish a sound and robust technology risk management framework.
• NIST Control: NIST-PM-28 Risk Framing: Identify and document:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-28 provides technical control capabilities addressing obligations in MAS-1.4(a).2.)
```
> *Identify and document:
Assumptions affecting risk assessments, risk responses, and risk monitoring;
Constraints affecting risk assessments, risk responses, and risk monitoring;
Priorities and trade-offs considered by the organization for managing ris...*

#### Control 8: `NIST-PS-2` (Position Risk Designation)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must establish a sound and robust technology risk management framework.
• NIST Control: NIST-PS-2 Position Risk Designation: Assign a risk designation to all organizational positions;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PS-2 provides technical control capabilities addressing obligations in MAS-1.4(a).2.)
```
> *Assign a risk designation to all organizational positions;
Establish screening criteria for individuals filling those positions; and
Review and update position risk designations {{ insert: param, ps-02_odp }}.
Position risk designations reflect Offic...*

#### Control 9: `NIST-PM-31` (Continuous Monitoring Strategy)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must establish a sound and robust technology risk management framework.
• NIST Control: NIST-PM-31 Continuous Monitoring Strategy: Develop an organization-wide continuous monitoring strategy and implement continuous monitoring programs that include:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-31 provides technical control capabilities addressing obligations in MAS-1.4(a).2.)
```
> *Develop an organization-wide continuous monitoring strategy and implement continuous monitoring programs that include:
Establishing the following organization-wide metrics to be monitored: {{ insert: param, pm-31_odp.01 }};
Establishing {{ insert: pa...*

#### Control 10: `NIST-PM-4` (Plan of Action and Milestones Process)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must establish a sound and robust technology risk management framework.
• NIST Control: NIST-PM-4 Plan of Action and Milestones Process: Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-4 provides technical control capabilities addressing obligations in MAS-1.4(a).2.)
```
> *Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:
Are developed and maintained;
Document the remedial information ...*

#### Control 11: `NIST-PM-1` (Information Security Program Plan)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must establish a sound and robust technology risk management framework.
• NIST Control: NIST-PM-1 Information Security Program Plan: Develop and disseminate an organization-wide information security program plan that:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-1 provides technical control capabilities addressing obligations in MAS-1.4(a).2.)
```
> *Develop and disseminate an organization-wide information security program plan that:
Provides an overview of the requirements for the security program and a description of the security program management controls and common controls in place or plann...*

#### Control 12: `NIST-PM-14` (Testing, Training, and Monitoring)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must establish a sound and robust technology risk management framework.
• NIST Control: NIST-PM-14 Testing, Training, and Monitoring: Implement a process for ensuring that organizational plans for conducting security and privacy testing, training, and monitoring activities associated with organizational systems:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-14 provides technical control capabilities addressing obligations in MAS-1.4(a).2.)
```
> *Implement a process for ensuring that organizational plans for conducting security and privacy testing, training, and monitoring activities associated with organizational systems:
Are developed and maintained; and
Continue to be executed; and
Review ...*

#### Control 13: `NIST-SR-3` (Supply Chain Controls and Processes)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must establish a sound and robust technology risk management framework.
• NIST Control: NIST-SR-3 Supply Chain Controls and Processes: Establish a process or processes to identify and address weaknesses or deficiencies in the supply chain elements and processes of {{ insert: param, sr-03_odp.01 }} in coordination with {{ insert: param, sr-03_odp.02 }};.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SR-3 provides technical control capabilities addressing obligations in MAS-1.4(a).2.)
```
> *Establish a process or processes to identify and address weaknesses or deficiencies in the supply chain elements and processes of {{ insert: param, sr-03_odp.01 }} in coordination with {{ insert: param, sr-03_odp.02 }};
Employ the following controls ...*

---

### Cluster 5: `MAS-1.4(b).1` maps to 15 NIST Controls

> **MAS TRM Statement [MAS-1.4(b).1]**:
> *The Financial Institution must adopt a defence-in-depth approach to strengthen cyber resilience.*

#### Control 1: `NIST-SA-24` (Design For Cyber Resiliency)
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-SA-24 Design For Cyber Resiliency: Design organizational systems, system components, or system services to achieve cyber resiliency by:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: FULL_COVERAGE (NIST-SA-24 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *Design organizational systems, system components, or system services to achieve cyber resiliency by:
Defining the following cyber resiliency goals: {{ insert: param, sa-24_odp.01 }}.
Defining the following cyber resiliency objectives: {{ insert: para...*

#### Control 2: `NIST-RA-10` (Threat Hunting)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-RA-10 Threat Hunting: Establish and maintain a cyber threat hunting capability to:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-10 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *Establish and maintain a cyber threat hunting capability to:
Search for indicators of compromise in organizational systems; and
Detect, track, and disrupt threats that evade existing controls; and
Employ the threat hunting capability {{ insert: param...*

#### Control 3: `NIST-PL-8` (Security and Privacy Architectures)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-PL-8 Security and Privacy Architectures: Develop security and privacy architectures for the system that:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PL-8 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *Develop security and privacy architectures for the system that:
Describe the requirements and approach to be taken for protecting the confidentiality, integrity, and availability of organizational information;
Describe the requirements and approach t...*

#### Control 4: `NIST-CP-2` (Contingency Plan)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-CP-2 Contingency Plan: Develop a contingency plan for the system that:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-CP-2 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *Develop a contingency plan for the system that:
Identifies essential mission and business functions and associated contingency requirements;
Provides recovery objectives, restoration priorities, and metrics;
Addresses contingency roles, responsibilit...*

#### Control 5: `NIST-CP-11` (Alternate Communications Protocols)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-CP-11 Alternate Communications Protocols: Provide the capability to employ {{ insert: param, cp-11_odp }} in support of maintaining continuity of operations..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-CP-11 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *Provide the capability to employ {{ insert: param, cp-11_odp }} in support of maintaining continuity of operations.
Contingency plans and the contingency training or testing associated with those plans incorporate an alternate communications protocol...*

#### Control 6: `NIST-IR-8` (Incident Response Plan)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-IR-8 Incident Response Plan: Develop an incident response plan that:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-IR-8 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *Develop an incident response plan that:
Provides the organization with a roadmap for implementing its incident response capability;
Describes the structure and organization of the incident response capability;
Provides a high-level approach for how t...*

#### Control 7: `NIST-PM-4` (Plan of Action and Milestones Process)
- **Semantic Relation**: `SUPPORTS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.81`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-PM-4 Plan of Action and Milestones Process: Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-4 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:
Are developed and maintained;
Document the remedial information ...*

#### Control 8: `NIST-SI-20` (Tainting)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-SI-20 Tainting: Embed data or capabilities in the following systems or system components to determine if organizational data has been exfiltrated or improperly removed from the organization: {{ insert: param, si-20_odp }}..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SI-20 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *Embed data or capabilities in the following systems or system components to determine if organizational data has been exfiltrated or improperly removed from the organization: {{ insert: param, si-20_odp }}.
Many cyber-attacks target organizational in...*

#### Control 9: `NIST-PL-2` (System Security and Privacy Plans)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.80`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-PL-2 System Security and Privacy Plans: Develop security and privacy plans for the system that:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PL-2 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *Develop security and privacy plans for the system that:
Are consistent with the organization’s enterprise architecture;
Explicitly define the constituent system components;
Describe the operational context of the system in terms of mission and busine...*

#### Control 10: `NIST-RA-9` (Criticality Analysis)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-RA-9 Criticality Analysis: Identify critical system components and functions by performing a criticality analysis for {{ insert: param, ra-09_odp.01 }} at {{ insert: param, ra-09_odp.02 }}..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-9 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *Identify critical system components and functions by performing a criticality analysis for {{ insert: param, ra-09_odp.01 }} at {{ insert: param, ra-09_odp.02 }}.
Not all system components, functions, or services necessarily require significant prote...*

#### Control 11: `NIST-PM-9` (Risk Management Strategy)
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.81`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-PM-9 Risk Management Strategy: Develops a comprehensive strategy to manage:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-9 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *Develops a comprehensive strategy to manage:
Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and
Privacy risk to individuals resu...*

#### Control 12: `NIST-RA-7` (Risk Response)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.81`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-RA-7 Risk Response: Respond to findings from security and privacy assessments, monitoring, and audits in accordance with organizational risk tolerance..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-7 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *Respond to findings from security and privacy assessments, monitoring, and audits in accordance with organizational risk tolerance.
Organizations have many options for responding to risk including mitigating risk by implementing new controls or stren...*

#### Control 13: `NIST-RA-5` (Vulnerability Monitoring and Scanning)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.80`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;
Employ vulnerability monitoring tools and techniques...*

#### Control 14: `NIST-IR-9` (Information Spillage Response)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.80`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-IR-9 Information Spillage Response: Respond to information spills by:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-IR-9 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *Respond to information spills by:
Assigning {{ insert: param, ir-09_odp.01 }} with responsibility for responding to information spills;
Identifying the specific information involved in the system contamination;
Alerting {{ insert: param, ir-09_odp.02...*

#### Control 15: `NIST-CA-7` (Continuous Monitoring)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.80`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-CA-7 Continuous Monitoring: Develop a system-level continuous monitoring strategy and implement continuous monitoring in accordance with the organization-level continuous monitoring strategy that includes:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-CA-7 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *Develop a system-level continuous monitoring strategy and implement continuous monitoring in accordance with the organization-level continuous monitoring strategy that includes:
Establishing the following system-level metrics to be monitored: {{ inse...*

---

## Section E: 5 Sample NIST Controls with Multiple Matches (N-to-1 Mapping Clusters)

### Cluster 1: `NIST-RA-6` (Technical Surveillance Countermeasures Survey) addresses 2 MAS Obligations

> **NIST Control Statement [NIST-RA-6]**:
> *Employ a technical surveillance countermeasures survey at {{ insert: param, ra-06_odp.01 }} {{ insert: param, ra-06_odp.02 }}.
A technical surveillance countermeasures survey is a service provided by qualified personnel to detect the presence of technical surveillance devices and hazards and to iden...*

#### MAS Clause 1: `MAS-1.3.a`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-RA-6 Technical Surveillance Countermeasures Survey: Employ a technical surveillance countermeasures survey at {{ insert: param, ra-06_odp.01 }} {{ insert: param, ra-06_odp.02 }}..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-6 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *The Financial Institution must evaluate its exposure to technology risks.*

#### MAS Clause 2: `MAS-15.1.2.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must identify a comprehensive set of auditable areas for technology risk to enable effective risk assessment during audit planning.
• NIST Control: NIST-RA-6 Technical Surveillance Countermeasures Survey: Employ a technical surveillance countermeasures survey at {{ insert: param, ra-06_odp.01 }} {{ insert: param, ra-06_odp.02 }}..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-6 provides technical control capabilities addressing obligations in MAS-15.1.2.a.)
```
> *The Financial Institution must identify a comprehensive set of auditable areas for technology risk to enable effective risk assessment during audit planning.*

---

### Cluster 2: `NIST-RA-8` (Privacy Impact Assessments) addresses 4 MAS Obligations

> **NIST Control Statement [NIST-RA-8]**:
> *Conduct privacy impact assessments for systems, programs, or other activities before:
Developing or procuring information technology that processes personally identifiable information; and
Initiating a new collection of personally identifiable information that:
Will be processed using information te...*

#### MAS Clause 1: `MAS-1.3.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.88`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-RA-8 Privacy Impact Assessments: Conduct privacy impact assessments for systems, programs, or other activities before:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-8 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *The Financial Institution must evaluate its exposure to technology risks.*

#### MAS Clause 2: `MAS-7.3.2.b`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `NO_COVERAGE` (Dyn Conf: `0.85`)
- **Rationale**:
```text
• MAS Requirement: must conduct a risk assessment for hardware and software approaching their end-of-support date.
• NIST Control: NIST-RA-8 Privacy Impact Assessments: Conduct privacy impact assessments for systems, programs, or other activities before:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: NO_COVERAGE (NIST-RA-8 provides technical control capabilities addressing obligations in MAS-7.3.2.b.)
```
> *The Financial Institution must conduct a risk assessment for hardware and software approaching their end-of-support date.*

#### MAS Clause 3: `MAS-13.6.1.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must perform severity assessment and classification of an issue.
• NIST Control: NIST-RA-8 Privacy Impact Assessments: Conduct privacy impact assessments for systems, programs, or other activities before:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-8 provides technical control capabilities addressing obligations in MAS-13.6.1.a.)
```
> *The Financial Institution must perform severity assessment and classification of an issue.*

#### MAS Clause 4: `MAS-15.1.2.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must identify a comprehensive set of auditable areas for technology risk to enable effective risk assessment during audit planning.
• NIST Control: NIST-RA-8 Privacy Impact Assessments: Conduct privacy impact assessments for systems, programs, or other activities before:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-8 provides technical control capabilities addressing obligations in MAS-15.1.2.a.)
```
> *The Financial Institution must identify a comprehensive set of auditable areas for technology risk to enable effective risk assessment during audit planning.*

---

### Cluster 3: `NIST-RA-3` (Risk Assessment) addresses 17 MAS Obligations

> **NIST Control Statement [NIST-RA-3]**:
> *Conduct a risk assessment, including:
Identifying threats to and vulnerabilities in the system;
Determining the likelihood and magnitude of harm from unauthorized access, use, disclosure, disruption, modification, or destruction of the system, the information it processes, stores, or transmits, and ...*

#### MAS Clause 1: `MAS-1.3.a`
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Dyn Conf: `0.81`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: FULL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *The Financial Institution must evaluate its exposure to technology risks.*

#### MAS Clause 2: `MAS-1.3.b`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.85`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *The Financial Institution must implement a robust risk management framework to ensure IT and cyber resilience.*

#### MAS Clause 3: `MAS-1.4(a).2`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must establish a sound and robust technology risk management framework.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-1.4(a).2.)
```
> *The Board of Directors and Senior Management must establish a sound and robust technology risk management framework.*

#### MAS Clause 4: `MAS-6.5.2`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must establish measures to control and monitor the use of shadow IT within its environment.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-6.5.2.)
```
> *The Financial Institution must establish measures to control and monitor the use of shadow IT within its environment.*

#### MAS Clause 5: `MAS-6.5.3.a`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must establish a process to assess the risk of end-user developed or acquired applications.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-6.5.3.a.)
```
> *The Financial Institution must establish a process to assess the risk of end-user developed or acquired applications.*

#### MAS Clause 6: `MAS-7.1.1`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must establish an IT service management framework comprising governance structures, processes, and procedures for IT service management activities.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-7.1.1.)
```
> *The Financial Institution must establish an IT service management framework comprising governance structures, processes, and procedures for IT service management activities.*

#### MAS Clause 7: `MAS-7.3.2.b`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must conduct a risk assessment for hardware and software approaching their end-of-support date.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-7.3.2.b.)
```
> *The Financial Institution must conduct a risk assessment for hardware and software approaching their end-of-support date.*

#### MAS Clause 8: `MAS-7.5.6.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must define procedures for assessing, approving, and implementing emergency changes to reduce the risk to the security and stability of the production environment.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-7.5.6.a.)
```
> *The Financial Institution must define procedures for assessing, approving, and implementing emergency changes to reduce the risk to the security and stability of the production environment.*

#### MAS Clause 9: `MAS-13.4.1`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `NO_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must perform an adversarial attack simulation exercise to test and validate the effectiveness of its cyber defence and response plan against prevalent cyber threats.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: NO_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-13.4.1.)
```
> *The Financial Institution must perform an adversarial attack simulation exercise to test and validate the effectiveness of its cyber defence and response plan against prevalent cyber threats.*

#### MAS Clause 10: `MAS-13.4.2.b`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must conduct the exercise in a controlled manner under close supervision to prevent disruption to its production systems.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-13.4.2.b.)
```
> *The Financial Institution must conduct the exercise in a controlled manner under close supervision to prevent disruption to its production systems.*

#### MAS Clause 11: `MAS-13.5.1`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must design the threat scenario based on challenging but plausible cyber threats to simulate realistic adversarial attacks during any cyber security assessment.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-13.5.1.)
```
> *The Financial Institution must design the threat scenario based on challenging but plausible cyber threats to simulate realistic adversarial attacks during any cyber security assessment.*

#### MAS Clause 12: `MAS-13.5.2.a`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must use threat intelligence relevant to its IT environment to identify threat actors most likely to pose a threat.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: FULL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-13.5.2.a.)
```
> *The Financial Institution must use threat intelligence relevant to its IT environment to identify threat actors most likely to pose a threat.*

#### MAS Clause 13: `MAS-13.6.1.a`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must perform severity assessment and classification of an issue.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-13.6.1.a.)
```
> *The Financial Institution must perform severity assessment and classification of an issue.*

#### MAS Clause 14: `MAS-13.6.1.c`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.85`)
- **Rationale**:
```text
• MAS Requirement: must develop risk assessment and mitigation strategies to manage deviations from the framework.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-13.6.1.c.)
```
> *The Financial Institution must develop risk assessment and mitigation strategies to manage deviations from the framework.*

#### MAS Clause 15: `MAS-14.4.2`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `NO_COVERAGE` (Dyn Conf: `0.81`)
- **Rationale**:
```text
• MAS Requirement: must alert customers on a timely basis to new cyber threats so they can take precautionary measures.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: NO_COVERAGE (True Regulatory Gap: MAS-14.4.2 mandates direct communication, advisory, or incident notification to external retail customers. NIST-RA-3 governs internal federal system technical monitoring and does not provide retail customer notification mechanisms.)
```
> *The Financial Institution must alert customers on a timely basis to new cyber threats so they can take precautionary measures.*

#### MAS Clause 16: `MAS-15.1.1`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must conduct IT audit to provide the board of directors and senior management an independent and objective opinion on the adequacy and effectiveness of risk management, governance, and internal controls relative to existing and emerging technology risks.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-15.1.1.)
```
> *The Financial Institution must conduct IT audit to provide the board of directors and senior management an independent and objective opinion on the adequacy and effectiveness of risk management, governance, and internal controls relative to existing and emerging technology risks.*

#### MAS Clause 17: `MAS-15.1.2.a`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Dyn Conf: `0.85`)
- **Rationale**:
```text
• MAS Requirement: must identify a comprehensive set of auditable areas for technology risk to enable effective risk assessment during audit planning.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: FULL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-15.1.2.a.)
```
> *The Financial Institution must identify a comprehensive set of auditable areas for technology risk to enable effective risk assessment during audit planning.*

---

### Cluster 4: `NIST-SI-20` (Tainting) addresses 7 MAS Obligations

> **NIST Control Statement [NIST-SI-20]**:
> *Embed data or capabilities in the following systems or system components to determine if organizational data has been exfiltrated or improperly removed from the organization: {{ insert: param, si-20_odp }}.
Many cyber-attacks target organizational information, or information that the organization ho...*

#### MAS Clause 1: `MAS-1.3.a`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.81`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-SI-20 Tainting: Embed data or capabilities in the following systems or system components to determine if organizational data has been exfiltrated or improperly removed from the organization: {{ insert: param, si-20_odp }}..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SI-20 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *The Financial Institution must evaluate its exposure to technology risks.*

#### MAS Clause 2: `MAS-1.4(b).1`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-SI-20 Tainting: Embed data or capabilities in the following systems or system components to determine if organizational data has been exfiltrated or improperly removed from the organization: {{ insert: param, si-20_odp }}..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SI-20 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *The Financial Institution must adopt a defence-in-depth approach to strengthen cyber resilience.*

#### MAS Clause 3: `MAS-1.4(b).2`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must establish IT processes and controls to preserve the confidentiality, integrity, and availability of data and IT systems.
• NIST Control: NIST-SI-20 Tainting: Embed data or capabilities in the following systems or system components to determine if organizational data has been exfiltrated or improperly removed from the organization: {{ insert: param, si-20_odp }}..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SI-20 provides technical control capabilities addressing obligations in MAS-1.4(b).2.)
```
> *The Financial Institution must establish IT processes and controls to preserve the confidentiality, integrity, and availability of data and IT systems.*

#### MAS Clause 4: `MAS-6.5.1`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must manage shadow IT as part of its information assets.
• NIST Control: NIST-SI-20 Tainting: Embed data or capabilities in the following systems or system components to determine if organizational data has been exfiltrated or improperly removed from the organization: {{ insert: param, si-20_odp }}..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SI-20 provides technical control capabilities addressing obligations in MAS-6.5.1.)
```
> *The Financial Institution must manage shadow IT as part of its information assets.*

#### MAS Clause 5: `MAS-14.1.2`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `NO_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must secure its communications channels to protect customer data.
• NIST Control: NIST-SI-20 Tainting: Embed data or capabilities in the following systems or system components to determine if organizational data has been exfiltrated or improperly removed from the organization: {{ insert: param, si-20_odp }}..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: NO_COVERAGE (NIST-SI-20 provides technical control capabilities addressing obligations in MAS-14.1.2.)
```
> *The Financial Institution must secure its communications channels to protect customer data.*

#### MAS Clause 6: `MAS-14.1.6.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.80`)
- **Rationale**:
```text
• MAS Requirement: must actively monitor for phishing campaigns targeting the Financial Institution and its customers.
• NIST Control: NIST-SI-20 Tainting: Embed data or capabilities in the following systems or system components to determine if organizational data has been exfiltrated or improperly removed from the organization: {{ insert: param, si-20_odp }}..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SI-20 provides technical control capabilities addressing obligations in MAS-14.1.6.a.)
```
> *The Financial Institution must actively monitor for phishing campaigns targeting the Financial Institution and its customers.*

#### MAS Clause 7: `MAS-Annex B.B.1.a`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must implement data loss prevention measures on personal computing or mobile devices used to access its information assets.
• NIST Control: NIST-SI-20 Tainting: Embed data or capabilities in the following systems or system components to determine if organizational data has been exfiltrated or improperly removed from the organization: {{ insert: param, si-20_odp }}..
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SI-20 provides technical control capabilities addressing obligations in MAS-Annex B.B.1.a.)
```
> *The Financial Institution must implement data loss prevention measures on personal computing or mobile devices used to access its information assets.*

---

### Cluster 5: `NIST-RA-5` (Vulnerability Monitoring and Scanning) addresses 23 MAS Obligations

> **NIST Control Statement [NIST-RA-5]**:
> *Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;
Employ vulnerability monitoring tools and techniques that facilitate interoperability among tools and ...*

#### MAS Clause 1: `MAS-1.3.a`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *The Financial Institution must evaluate its exposure to technology risks.*

#### MAS Clause 2: `MAS-1.3.b`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *The Financial Institution must implement a robust risk management framework to ensure IT and cyber resilience.*

#### MAS Clause 3: `MAS-1.4(b).1`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.80`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *The Financial Institution must adopt a defence-in-depth approach to strengthen cyber resilience.*

#### MAS Clause 4: `MAS-6.5.2`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must establish measures to control and monitor the use of shadow IT within its environment.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-6.5.2.)
```
> *The Financial Institution must establish measures to control and monitor the use of shadow IT within its environment.*

#### MAS Clause 5: `MAS-6.5.3.a`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.86`)
- **Rationale**:
```text
• MAS Requirement: must establish a process to assess the risk of end-user developed or acquired applications.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-6.5.3.a.)
```
> *The Financial Institution must establish a process to assess the risk of end-user developed or acquired applications.*

#### MAS Clause 6: `MAS-6.5.3.d`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must conduct proper testing before deploying end-user developed or acquired applications.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-6.5.3.d.)
```
> *The Financial Institution must conduct proper testing before deploying end-user developed or acquired applications.*

#### MAS Clause 7: `MAS-7.2.2`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must review and verify the configuration information of its hardware and software on a regular basis.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-7.2.2.)
```
> *The Financial Institution must review and verify the configuration information of its hardware and software on a regular basis.*

#### MAS Clause 8: `MAS-7.3.1.a`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must avoid using outdated and unsupported hardware or software.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-7.3.1.a.)
```
> *The Financial Institution must avoid using outdated and unsupported hardware or software.*

#### MAS Clause 9: `MAS-7.3.1.b`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.85`)
- **Rationale**:
```text
• MAS Requirement: must closely monitor the end-of-support dates of its hardware and software.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-7.3.1.b.)
```
> *The Financial Institution must closely monitor the end-of-support dates of its hardware and software.*

#### MAS Clause 10: `MAS-7.3.2.b`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.86`)
- **Rationale**:
```text
• MAS Requirement: must conduct a risk assessment for hardware and software approaching their end-of-support date.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-7.3.2.b.)
```
> *The Financial Institution must conduct a risk assessment for hardware and software approaching their end-of-support date.*

#### MAS Clause 11: `MAS-7.3.2.c`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must implement effective risk mitigation measures for hardware and software approaching their end-of-support date.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-7.3.2.c.)
```
> *The Financial Institution must implement effective risk mitigation measures for hardware and software approaching their end-of-support date.*

#### MAS Clause 12: `MAS-7.7.1`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must establish an incident management framework to restore affected IT services or systems to a secure and stable state as quickly as possible, minimizing impact to the business and customers.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-7.7.1.)
```
> *The Financial Institution must establish an incident management framework to restore affected IT services or systems to a secure and stable state as quickly as possible, minimizing impact to the business and customers.*

#### MAS Clause 13: `MAS-13.4.1`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must perform an adversarial attack simulation exercise to test and validate the effectiveness of its cyber defence and response plan against prevalent cyber threats.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-13.4.1.)
```
> *The Financial Institution must perform an adversarial attack simulation exercise to test and validate the effectiveness of its cyber defence and response plan against prevalent cyber threats.*

#### MAS Clause 14: `MAS-13.5.1`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must design the threat scenario based on challenging but plausible cyber threats to simulate realistic adversarial attacks during any cyber security assessment.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-13.5.1.)
```
> *The Financial Institution must design the threat scenario based on challenging but plausible cyber threats to simulate realistic adversarial attacks during any cyber security assessment.*

#### MAS Clause 15: `MAS-13.5.2.b`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must identify the tactics, techniques, and procedures most likely to be used in such attacks.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-13.5.2.b.)
```
> *The Financial Institution must identify the tactics, techniques, and procedures most likely to be used in such attacks.*

#### MAS Clause 16: `MAS-13.6.1`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.86`)
- **Rationale**:
```text
• MAS Requirement: must establish a comprehensive remediation process to track and resolve issues identified from cyber security assessments or exercises.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-13.6.1.)
```
> *The Financial Institution must establish a comprehensive remediation process to track and resolve issues identified from cyber security assessments or exercises.*

#### MAS Clause 17: `MAS-13.6.1.b`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.81`)
- **Rationale**:
```text
• MAS Requirement: must define a timeframe to remediate issues of different severity.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-13.6.1.b.)
```
> *The Financial Institution must define a timeframe to remediate issues of different severity.*

#### MAS Clause 18: `MAS-13.6.1.c`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must develop risk assessment and mitigation strategies to manage deviations from the framework.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-13.6.1.c.)
```
> *The Financial Institution must develop risk assessment and mitigation strategies to manage deviations from the framework.*

#### MAS Clause 19: `MAS-14.1.3`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must implement adequate measures to minimize exposure of its online financial services to common attack vectors such as code injection attacks, cross-site scripting, man-in-the-middle attacks, DNS hijacking, DDoS, malware, and spoofing attacks.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-14.1.3.)
```
> *The Financial Institution must implement adequate measures to minimize exposure of its online financial services to common attack vectors such as code injection attacks, cross-site scripting, man-in-the-middle attacks, DNS hijacking, DDoS, malware, and spoofing attacks.*

#### MAS Clause 20: `MAS-14.1.4`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must implement specific measures aimed at addressing the risks unique to mobile applications.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-14.1.4.)
```
> *The Financial Institution must implement specific measures aimed at addressing the risks unique to mobile applications.*

#### MAS Clause 21: `MAS-14.1.6.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `NO_COVERAGE` (Dyn Conf: `0.81`)
- **Rationale**:
```text
• MAS Requirement: must actively monitor for phishing campaigns targeting the Financial Institution and its customers.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: NO_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-14.1.6.a.)
```
> *The Financial Institution must actively monitor for phishing campaigns targeting the Financial Institution and its customers.*

#### MAS Clause 22: `MAS-C.1.4`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.86`)
- **Rationale**:
```text
• MAS Requirement: must implement anti-hooking or anti-tampering mechanisms to prevent the injection of malicious code that could alter or monitor application behaviour at runtime.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-C.1.4.)
```
> *The Financial Institution must implement anti-hooking or anti-tampering mechanisms to prevent the injection of malicious code that could alter or monitor application behaviour at runtime.*

#### MAS Clause 23: `MAS-C.1.6`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must implement code obfuscation techniques to prevent reverse engineering of the mobile application.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Core technical controls and operational mechanisms], Missing: [Framework-specific reporting workflows or external parameters].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-C.1.6.)
```
> *The Financial Institution must implement code obfuscation techniques to prevent reverse engineering of the mobile application.*

---

