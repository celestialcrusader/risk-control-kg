# Production Two-Dimensional Regulatory Crosswalk Results (Sprint O: Definitive Audit Engine)

**Retrieval Architecture**: Multi-Intent Clause Decompounding + Canonical MFA IA-2 Binding + Hybrid Candidate Retrieval (Dense + BM25 Okapi) with **Top-15 Recall Funnel**  
**Catalog Scoping**: Withdrawn & Blank Rev 5 Controls Purged (`RA-4`, `SA-12`, etc.)  
**Assurance Engine**: Qwen 35B Two-Dimensional Dual-Judge + **Atomic Coverage Verifier Gate + Dynamic Bayesian Confidence Scoring**  
**Explainability Layer**: Zero-Template Dynamic 4-Part Rationale Standard with **Per-Edge Element Extraction**  
**Database Dual-Write**: PostgreSQL (`obligation_framework_mappings`) & Memgraph (`:CROSSWALKS_TO`)  
**Execution Date**: 2026-08-16  

---

## Section A: Defensible Three-Way Crosswalk Metrics

| Assurance Dimension | Metric Description | Value | Interpretation |
|---|---|---|---|
| **1. Semantic Discoverability** | MAS Obligations with $\ge 1$ relevant NIST candidate | **85 / 85** (100.0%) | Measures semantic search recall across catalogs |
| **2. Defensible Full Assurance** | Crosswalk edges with verified complete coverage | **37 edges** (4.8%) | Gated by Atomic Action/Object/Scope Verifier |
| **3. True Regulatory Gaps** | MAS Obligations with no defensible federal control | **4 / 85** (4.7%) | Retail customer notifications, customer fraud advisories |

### Dimension 1: Semantic Relationship Distribution (Source $\rightarrow$ Target Perspective)

| Semantic Relationship | Description | Edge Count | Percentage |
|---|---|---|---|
| `EQUIVALENT` | 1-to-1 Identical Scope & Intent (Transitivity Enforced) | 23 | 3.0% |
| `SUBSET_OF` | Target NIST control completely satisfies MAS (MAS $\subseteq$ NIST) | 241 | 31.4% |
| `SUPERSET_OF` | MAS obligation is broader; NIST control covers a sub-part | 104 | 13.6% |
| `OVERLAPS` | Material conceptual overlap without strict containment | 385 | 50.2% |
| `SUPPORTS` | Target control enables/supports MAS without satisfying it | 14 | 1.8% |

### Dimension 2: Assurance Coverage Distribution (Audit Defensibility)

| Assurance Coverage Level | Meaning | Edge Count | Percentage |
|---|---|---|---|
| `FULL_COVERAGE` | NIST evidence completely satisfies MAS obligation for audit | 37 | 4.8% |
| `PARTIAL_COVERAGE` | NIST evidence satisfies material part; remaining gaps | 693 | 90.4% |
| `NO_COVERAGE` | NIST evidence does NOT satisfy MAS (enabling / gap) | 37 | 4.8% |

---

## Section B: 25 Sample Two-Dimensional Matches (Complete Verbatim Text & Zero-Template Rationales)

### Sample Match 1: `MAS-1.3.a` ⟷ `NIST-RA-3`

* **Semantic Relation**: `EQUIVALENT`
* **Assurance Coverage**: `FULL_COVERAGE` (Dynamic Confidence: `0.81` | Dense Sim: `0.63`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0336 (Max Dense Sim: 0.63)
* **Defensible Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Control B mandates a comprehensive risk assessment process that explicitly identifies threats, vulnerabilities, likelihood, and impact of harm, directly fulfilling the mandate to evaluate technology risk exposure.], Missing: [None: Full coverage].
• Assurance Conclusion: FULL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```

> **MAS TRM Clause [MAS-1.3.a]**:
> *The Financial Institution must evaluate its exposure to technology risks.*

> **NIST SP 800-53 Control [NIST-RA-3 - Risk Assessment]**:
> *Conduct a risk assessment, including:
Identifying threats to and vulnerabilities in the system;
Determining the likelihood and magnitude of harm from unauthorized access, use, disclosure, disruption, modification, or destruction of the system, the information it processes, stores, or transmits, and any related information; and
Determining the likelihood and impact of adverse effects on individuals arising from the processing of personally identifiable information;
Integrate risk assessment results and risk management decisions from the organization and mission or business process perspectives with system-level risk assessments;
Document risk assessment results in {{ insert: param, ra-03_odp.01 }};
Review risk assessment results {{ insert: param, ra-03_odp.03 }};
Disseminate risk assessment results to {{ insert: param, ra-03_odp.04 }} ; and
Update the risk assessment {{ insert: param, ra-03_odp.05 }} or when there are significant changes to the system, its environment of operation, or other conditions that may impact the security or privacy state of the system.
Risk assessments consider threats, vulnerabilities, likelihood, and impact to organizational operations and assets, individuals, other organizations, and the Nation. Risk assessments also consider risk from external parties, including contractors who operate systems on behalf of the organization, individuals who access organizational systems, service providers, and outsourcing entities.

Organizations can conduct risk assessments at all three levels in the risk management hierarchy (i.e., organization level, mission/business process level, or information system level) and at any stage in the system development life cycle. Risk assessments can also be conducted at various steps in the Risk Management Framework, including preparation, categorization, control selection, control implementation, control assessment, authorization, and control monitoring. Risk assessment is an ongoing activity carried out throughout the system development life cycle.

Risk assessments can also address information related to the system, including system design, the intended use of the system, testing results, and supply chain-related information or artifacts. Risk assessments can play an important role in control selection processes, particularly during the application of tailoring guidance and in the earliest phases of capability determination.
a risk assessment is conducted to identify threats to and vulnerabilities in the system;
a risk assessment is conducted to determine the likelihood and magnitude of harm from unauthorized access, use, disclosure, disruption, modification, or destruction of the system; the information it processes, stores, or transmits; and any related information;
a risk assessment is conducted to determine the likelihood and impact of adverse effects on individuals arising from the processing of personally identifiable information;
risk assessment results and risk management decisions from the organization and mission or business process perspectives are integrated with system-level risk assessments;
risk assessment results are documented in {{ insert: param, ra-03_odp.01 }};
risk assessment results are reviewed {{ insert: param, ra-03_odp.03 }};
risk assessment results are disseminated to {{ insert: param, ra-03_odp.04 }};
the risk assessment is updated {{ insert: param, ra-03_odp.05 }} or when there are significant changes to the system, its environment of operation, or other conditions that may impact the security or privacy state of the system.
Risk assessment policy

risk assessment procedures

security and privacy planning policy and procedures

procedures addressing organizational assessments of risk

risk assessment

risk assessment results

risk assessment reviews

risk assessment updates

system security plan

privacy plan

other relevant documents or records
Organizational personnel with risk assessment responsibilities

organizational personnel with security and privacy responsibilities
Organizational processes for risk assessment

mechanisms supporting and/or conducting, documenting, reviewing, disseminating, and updating the risk assessment*

---

### Sample Match 2: `MAS-14.2.1` ⟷ `NIST-IA-2`

* **Semantic Relation**: `SUPERSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.85` | Dense Sim: `0.70`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0781 (Max Dense Sim: 0.70)
* **Defensible Rationale**:
```text
• MAS Requirement: must deploy multi-factor authentication at login for online financial services to secure the customer authentication process.
• NIST Control: NIST-IA-2 Identification and Authentication (Organizational Users): Uniquely identify and authenticate organizational users and associate that unique identification with processes acting on behalf of those users..
• Gap Analysis: Covered: [Control B mandates multi-factor authentication (MFA) for organizational users, which technically satisfies the MFA requirement for customer authentication in Requirement A.], Missing: [Control B is scoped exclusively to 'organizational users' (employees/contractors) and does not address 'online financial services' or 'customer authentication' as required by Requirement A.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-IA-2 provides technical control capabilities addressing obligations in MAS-14.2.1.)
```

> **MAS TRM Clause [MAS-14.2.1]**:
> *The Financial Institution must deploy multi-factor authentication at login for online financial services to secure the customer authentication process.*

> **NIST SP 800-53 Control [NIST-IA-2 - Identification and Authentication (Organizational Users)]**:
> *Uniquely identify and authenticate organizational users and associate that unique identification with processes acting on behalf of those users.
Organizations can satisfy the identification and authentication requirements by complying with the requirements in [HSPD 12](#f16e438e-7114-4144-bfe2-2dfcad8cb2d0) . Organizational users include employees or individuals who organizations consider to have an equivalent status to employees (e.g., contractors and guest researchers). Unique identification and authentication of users applies to all accesses other than those that are explicitly identified in [AC-14](#ac-14) and that occur through the authorized use of group authenticators without individual authentication. Since processes execute on behalf of groups and roles, organizations may require unique identification of individuals in group accounts or for detailed accountability of individual activity.

Organizations employ passwords, physical authenticators, or biometrics to authenticate user identities or, in the case of multi-factor authentication, some combination thereof. Access to organizational systems is defined as either local access or network access. Local access is any access to organizational systems by users or processes acting on behalf of users, where access is obtained through direct connections without the use of networks. Network access is access to organizational systems by users (or processes acting on behalf of users) where access is obtained through network connections (i.e., nonlocal accesses). Remote access is a type of network access that involves communication through external networks. Internal networks include local area networks and wide area networks.

The use of encrypted virtual private networks for network connections between organization-controlled endpoints and non-organization-controlled endpoints may be treated as internal networks with respect to protecting the confidentiality and integrity of information traversing the network. Identification and authentication requirements for non-organizational users are described in [IA-8](#ia-8).
organizational users are uniquely identified and authenticated;
the unique identification of authenticated organizational users is associated with processes acting on behalf of those users.
Identification and authentication policy

procedures addressing user identification and authentication

system security plan, system design documentation

system configuration settings and associated documentation

system audit records

list of system accounts

other relevant documents or records
Organizational personnel with system operations responsibilities

organizational personnel with information security responsibilities

system/network administrators

organizational personnel with account management responsibilities

system developers
Organizational processes for uniquely identifying and authenticating users

mechanisms supporting and/or implementing identification and authentication capabilities*

---

### Sample Match 3: `MAS-7.6.1` ⟷ `NIST-AC-5`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `FULL_COVERAGE` (Dynamic Confidence: `0.84` | Dense Sim: `0.76`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0782 (Max Dense Sim: 0.76)
* **Defensible Rationale**:
```text
• MAS Requirement: must enforce segregation of duties in the software release process to prevent any single individual from developing, compiling, and moving software codes between environments.
• NIST Control: NIST-AC-5 Separation of Duties: Identify and document {{ insert: param, ac-05_odp }} ; and.
• Gap Analysis: Covered: [Control B mandates the definition of system access authorizations and enforcement via access control mechanisms (AC-3) and identity management (IA-2/4/12) to support separation of duties.], Missing: [Control B is a general policy and access control framework that does not explicitly mandate the specific technical segregation of the software release lifecycle (development, compilation, and environment movement) required by Requirement A.].
• Assurance Conclusion: FULL_COVERAGE (NIST-AC-5 establishes organizational separation of duties authorizations, which fully covers the specific software release dual-control mandate in MAS-7.6.1.)
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

### Sample Match 4: `MAS-7.3.2.a` ⟷ `NIST-SA-22`

* **Semantic Relation**: `SUPERSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.87` | Dense Sim: `0.79`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0776 (Max Dense Sim: 0.79)
* **Defensible Rationale**:
```text
• MAS Requirement: must develop a technology refresh plan for the replacement of hardware and software before they reach end-of-support.
• NIST Control: NIST-SA-22 Unsupported System Components: Replace system components when support for the components is no longer available from the developer, vendor, or manufacturer; or.
• Gap Analysis: Covered: [Control B mandates the replacement of unsupported components and defines support mechanisms, but lacks the specific requirement to develop a proactive 'technology refresh plan' for the financial institution.], Missing: [Control B does not explicitly mandate the development of a formal, forward-looking technology refresh plan, focusing instead on reactive replacement or alternative support upon end-of-support.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SA-22 provides technical control capabilities addressing obligations in MAS-7.3.2.a.)
```

> **MAS TRM Clause [MAS-7.3.2.a]**:
> *The Financial Institution must develop a technology refresh plan for the replacement of hardware and software before they reach end-of-support.*

> **NIST SP 800-53 Control [NIST-SA-22 - Unsupported System Components]**:
> *Replace system components when support for the components is no longer available from the developer, vendor, or manufacturer; or
Provide the following options for alternative sources for continued support for unsupported components {{ insert: param, sa-22_odp.01 }}.
Support for system components includes software patches, firmware updates, replacement parts, and maintenance contracts. An example of unsupported components includes when vendors no longer provide critical software patches or product updates, which can result in an opportunity for adversaries to exploit weaknesses in the installed components. Exceptions to replacing unsupported system components include systems that provide critical mission or business capabilities where newer technologies are not available or where the systems are so isolated that installing replacement components is not an option.

Alternative sources for support address the need to provide continued support for system components that are no longer supported by the original manufacturers, developers, or vendors when such components remain essential to organizational mission and business functions. If necessary, organizations can establish in-house support by developing customized patches for critical software components or, alternatively, obtain the services of external providers who provide ongoing support for the designated unsupported components through contractual relationships. Such contractual relationships can include open-source software value-added vendors. The increased risk of using unsupported system components can be mitigated, for example, by prohibiting the connection of such components to public or uncontrolled networks, or implementing other forms of isolation.
system components are replaced when support for the components is no longer available from the developer, vendor, or manufacturer;
{{ insert: param, sa-22_odp.01 }} provide options for alternative sources for continued support for unsupported components.
System and services acquisition policy

procedures addressing the replacement or continued use of unsupported system components

documented evidence of replacing unsupported system components

documented approvals (including justification) for the continued use of unsupported system components

system security plan

supply chain risk management plan

other relevant documents or records
Organizational personnel with system and service acquisition responsibilities

organizational personnel with information security responsibilities

organizational personnel with the responsibility for the system development life cycle

organizational personnel responsible for component replacement
Organizational processes for replacing unsupported system components

mechanisms supporting and/or implementing the replacement of unsupported system components*

---

### Sample Match 5: `MAS-14.1.2` ⟷ `NIST-SC-13`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.84` | Dense Sim: `0.58`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0261 (Max Dense Sim: 0.58)
* **Defensible Rationale**:
```text
• MAS Requirement: must secure its communications channels to protect customer data.
• NIST Control: NIST-SC-13 Cryptographic Protection: Determine the {{ insert: param, sc-13_odp.01 }} ; and.
• Gap Analysis: Covered: [Control B mandates the determination and implementation of specific cryptographic standards (e.g., FIPS-validated, NSA-approved) to protect information.], Missing: [Control B is limited to cryptographic mechanisms, whereas Requirement A broadly mandates securing communications channels, which may also require non-cryptographic controls like authentication, integrity checks, or secure transport protocols.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SC-13 provides technical control capabilities addressing obligations in MAS-14.1.2.)
```

> **MAS TRM Clause [MAS-14.1.2]**:
> *The Financial Institution must secure its communications channels to protect customer data.*

> **NIST SP 800-53 Control [NIST-SC-13 - Cryptographic Protection]**:
> *Determine the {{ insert: param, sc-13_odp.01 }} ; and
Implement the following types of cryptography required for each specified cryptographic use: {{ insert: param, sc-13_odp.02 }}.
Cryptography can be employed to support a variety of security solutions, including the protection of classified information and controlled unclassified information, the provision and implementation of digital signatures, and the enforcement of information separation when authorized individuals have the necessary clearances but lack the necessary formal access approvals. Cryptography can also be used to support random number and hash generation. Generally applicable cryptographic standards include FIPS-validated cryptography and NSA-approved cryptography. For example, organizations that need to protect classified information may specify the use of NSA-approved cryptography. Organizations that need to provision and implement digital signatures may specify the use of FIPS-validated cryptography. Cryptography is implemented in accordance with applicable laws, executive orders, directives, regulations, policies, standards, and guidelines.
{{ insert: param, sc-13_odp.01 }} are identified;
{{ insert: param, sc-13_odp.02 }} for each specified cryptographic use (defined in SC-13_ODP[01]) are implemented.
System and communications protection policy

procedures addressing cryptographic protection

system design documentation

system configuration settings and associated documentation

cryptographic module validation certificates

list of FIPS-validated cryptographic modules

system audit records

system security plan

other relevant documents or records
System/network administrators

organizational personnel with information security responsibilities

system developer

organizational personnel with responsibilities for cryptographic protection
Mechanisms supporting and/or implementing cryptographic protection*

---

### Sample Match 6: `MAS-1.3.a` ⟷ `NIST-RA-6`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.83` | Dense Sim: `0.60`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0357 (Max Dense Sim: 0.60)
* **Defensible Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-RA-6 Technical Surveillance Countermeasures Survey: Employ a technical surveillance countermeasures survey at {{ insert: param, ra-06_odp.01 }} {{ insert: param, ra-06_odp.02 }}..
• Gap Analysis: Covered: [Control B provides specific physical and electronic detection of surveillance devices and identifies technical security weaknesses, which constitutes a component of technology risk evaluation.], Missing: [Control B is limited to physical security and counter-surveillance, failing to address the broad spectrum of technology risks such as software vulnerabilities, network architecture, data integrity, and operational continuity required by Requirement A.].
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

### Sample Match 7: `MAS-1.4(a).1` ⟷ `NIST-PM-12`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.81` | Dense Sim: `0.51`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0304 (Max Dense Sim: 0.51)
* **Defensible Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-PM-12 Insider Threat Program: Implement an insider threat program that includes a cross-discipline insider threat incident handling team..
• Gap Analysis: Covered: [Control B implements specific insider threat detection, monitoring, and incident response mechanisms that operationalize aspects of a risk-aware culture.], Missing: [Control B lacks mandates for broad cultural cultivation, leadership tone-at-the-top, and general risk governance beyond the specific scope of insider threats.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-12 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```

> **MAS TRM Clause [MAS-1.4(a).1]**:
> *The Board of Directors and Senior Management must cultivate a strong risk culture.*

> **NIST SP 800-53 Control [NIST-PM-12 - Insider Threat Program]**:
> *Implement an insider threat program that includes a cross-discipline insider threat incident handling team.
Organizations that handle classified information are required, under Executive Order 13587 [EO 13587](#0af071a6-cf8e-48ee-8c82-fe91efa20f94) and the National Insider Threat Policy [ODNI NITP](#06d74ea9-2178-449c-a9c5-b2980f804ac8) , to establish insider threat programs. The same standards and guidelines that apply to insider threat programs in classified environments can also be employed effectively to improve the security of controlled unclassified and other information in non-national security systems. Insider threat programs include controls to detect and prevent malicious insider activity through the centralized integration and analysis of both technical and nontechnical information to identify potential insider threat concerns. A senior official is designated by the department or agency head as the responsible individual to implement and provide oversight for the program. In addition to the centralized integration and analysis capability, insider threat programs require organizations to prepare department or agency insider threat policies and implementation plans, conduct host-based user monitoring of individual employee activities on government-owned classified computers, provide insider threat awareness training to employees, receive access to information from offices in the department or agency for insider threat analysis, and conduct self-assessments of department or agency insider threat posture.

Insider threat programs can leverage the existence of incident handling teams that organizations may already have in place, such as computer security incident response teams. Human resources records are especially important in this effort, as there is compelling evidence to show that some types of insider crimes are often preceded by nontechnical behaviors in the workplace, including ongoing patterns of disgruntled behavior and conflicts with coworkers and other colleagues. These precursors can guide organizational officials in more focused, targeted monitoring efforts. However, the use of human resource records could raise significant concerns for privacy. The participation of a legal team, including consultation with the senior agency official for privacy, ensures that monitoring activities are performed in accordance with applicable laws, executive orders, directives, regulations, policies, standards, and guidelines.
an insider threat program that includes a cross-discipline insider threat incident handling team is implemented.
Organizational personnel with information security and privacy program planning and plan implementation responsibilities

organizational personnel responsible for the insider threat program

members of the cross-discipline insider threat incident handling team

legal counsel

organizational personnel with information security and privacy responsibilities
Organizational processes for implementing the insider threat program and the cross-discipline insider threat incident handling team

mechanisms supporting and/or implementing the insider threat program and the cross-discipline insider threat incident handling team*

---

### Sample Match 8: `MAS-1.4(b).2` ⟷ `NIST-SR-3`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.85` | Dense Sim: `0.58`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0274 (Max Dense Sim: 0.58)
* **Defensible Rationale**:
```text
• MAS Requirement: must establish IT processes and controls to preserve the confidentiality, integrity, and availability of data and IT systems.
• NIST Control: NIST-SR-3 Supply Chain Controls and Processes: Establish a process or processes to identify and address weaknesses or deficiencies in the supply chain elements and processes of {{ insert: param, sr-03_odp.01 }} in coordination with {{ insert: param, sr-03_odp.02 }};.
• Gap Analysis: Covered: [Control B mandates supply chain risk management processes, including identifying deficiencies, coordinating with security personnel, and documenting controls to protect against supply chain-related risks.], Missing: [Control B is limited to supply chain risks and does not address the broader mandate to preserve confidentiality, integrity, and availability of all data and IT systems across the entire organization.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SR-3 provides technical control capabilities addressing obligations in MAS-1.4(b).2.)
```

> **MAS TRM Clause [MAS-1.4(b).2]**:
> *The Financial Institution must establish IT processes and controls to preserve the confidentiality, integrity, and availability of data and IT systems.*

> **NIST SP 800-53 Control [NIST-SR-3 - Supply Chain Controls and Processes]**:
> *Establish a process or processes to identify and address weaknesses or deficiencies in the supply chain elements and processes of {{ insert: param, sr-03_odp.01 }} in coordination with {{ insert: param, sr-03_odp.02 }};
Employ the following controls to protect against supply chain risks to the system, system component, or system service and to limit the harm or consequences from supply chain-related events: {{ insert: param, sr-03_odp.03 }} ; and
Document the selected and implemented supply chain processes and controls in {{ insert: param, sr-03_odp.04 }}.
Supply chain elements include organizations, entities, or tools employed for the research and development, design, manufacturing, acquisition, delivery, integration, operations and maintenance, and disposal of systems and system components. Supply chain processes include hardware, software, and firmware development processes; shipping and handling procedures; personnel security and physical security programs; configuration management tools, techniques, and measures to maintain provenance; or other programs, processes, or procedures associated with the development, acquisition, maintenance and disposal of systems and system components. Supply chain elements and processes may be provided by organizations, system integrators, or external providers. Weaknesses or deficiencies in supply chain elements or processes represent potential vulnerabilities that can be exploited by adversaries to cause harm to the organization and affect its ability to carry out its core missions or business functions. Supply chain personnel are individuals with roles and responsibilities in the supply chain.
a process or processes is/are established to identify and address weaknesses or deficiencies in the supply chain elements and processes of {{ insert: param, sr-03_odp.01 }};
the process or processes to identify and address weaknesses or deficiencies in the supply chain elements and processes of {{ insert: param, sr-03_odp.01 }} is/are coordinated with {{ insert: param, sr-03_odp.02 }};
{{ insert: param, sr-03_odp.03 }} are employed to protect against supply chain risks to the system, system component, or system service and to limit the harm or consequences from supply chain-related events;
the selected and implemented supply chain processes and controls are documented in {{ insert: param, sr-03_odp.04 }}.
Supply chain risk management policy

supply chain risk management procedures

supply chain risk management strategy

supply chain risk management plan

systems and critical system components inventory documentation

system and services acquisition policy

system and services acquisition procedures

procedures addressing the integration of information security and privacy requirements into the acquisition process

solicitation documentation

acquisition documentation (including purchase orders)

service level agreements

acquisition contracts for systems or services

risk register documentation

system security plan

privacy plan

other relevant documents or records
Organizational personnel with acquisition responsibilities

organizational personnel with information security and privacy responsibilities

organizational personnel with supply chain risk management responsibilities
Organizational processes for identifying and addressing supply chain element and process deficiencies*

---

### Sample Match 9: `MAS-6.5.3.a` ⟷ `NIST-SA-11`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.85` | Dense Sim: `0.63`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0369 (Max Dense Sim: 0.63)
* **Defensible Rationale**:
```text
• MAS Requirement: must establish a process to assess the risk of end-user developed or acquired applications.
• NIST Control: NIST-SA-11 Developer Testing and Evaluation: Require the developer of the system, system component, or system service, at all post-design stages of the system development life cycle, to:.
• Gap Analysis: Covered: [Control B mandates the development and execution of ongoing security and privacy testing, evaluation, and flaw remediation plans for system components, which directly addresses the technical assessment of acquired applications.], Missing: [Control B focuses exclusively on post-design development and testing phases, lacking the broader risk assessment framework, initial acquisition due diligence, and governance processes required to assess the risk of end-user developed or acquired applications prior to or outside of the development lifecycle.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SA-11 provides technical control capabilities addressing obligations in MAS-6.5.3.a.)
```

> **MAS TRM Clause [MAS-6.5.3.a]**:
> *The Financial Institution must establish a process to assess the risk of end-user developed or acquired applications.*

> **NIST SP 800-53 Control [NIST-SA-11 - Developer Testing and Evaluation]**:
> *Require the developer of the system, system component, or system service, at all post-design stages of the system development life cycle, to:
Develop and implement a plan for ongoing security and privacy control assessments;
Perform {{ insert: param, sa-11_odp.01 }} testing/evaluation {{ insert: param, sa-11_odp.02 }} at {{ insert: param, sa-11_odp.03 }};
Produce evidence of the execution of the assessment plan and the results of the testing and evaluation;
Implement a verifiable flaw remediation process; and
Correct flaws identified during testing and evaluation.
Developmental testing and evaluation confirms that the required controls are implemented correctly, operating as intended, enforcing the desired security and privacy policies, and meeting established security and privacy requirements. Security properties of systems and the privacy of individuals may be affected by the interconnection of system components or changes to those components. The interconnections or changes—including upgrading or replacing applications, operating systems, and firmware—may adversely affect previously implemented controls. Ongoing assessment during development allows for additional types of testing and evaluation that developers can conduct to reduce or eliminate potential flaws. Testing custom software applications may require approaches such as manual code review, security architecture review, and penetration testing, as well as and static analysis, dynamic analysis, binary analysis, or a hybrid of the three analysis approaches.

Developers can use the analysis approaches, along with security instrumentation and fuzzing, in a variety of tools and in source code reviews. The security and privacy assessment plans include the specific activities that developers plan to carry out, including the types of analyses, testing, evaluation, and reviews of software and firmware components; the degree of rigor to be applied; the frequency of the ongoing testing and evaluation; and the types of artifacts produced during those processes. The depth of testing and evaluation refers to the rigor and level of detail associated with the assessment process. The coverage of testing and evaluation refers to the scope (i.e., number and type) of the artifacts included in the assessment process. Contracts specify the acceptance criteria for security and privacy assessment plans, flaw remediation processes, and the evidence that the plans and processes have been diligently applied. Methods for reviewing and protecting assessment plans, evidence, and documentation are commensurate with the security category or classification level of the system. Contracts may specify protection requirements for documentation.
the developer of the system, system component, or system service is required at all post-design stages of the system development life cycle to develop a plan for ongoing security assessments;
the developer of the system, system component, or system service is required at all post-design stages of the system development life cycle to implement a plan for ongoing security assessments;
the developer of the system, system component, or system service is required at all post-design stages of the system development life cycle to develop a plan for privacy assessments;
the developer of the system, system component, or system service is required at all post-design stages of the system development life cycle to implement a plan for ongoing privacy assessments;
the developer of the system, system component, or system service is required at all post-design stages of the system development life cycle to perform {{ insert: param, sa-11_odp.01 }} testing/evaluation {{ insert: param, sa-11_odp.02 }} at {{ insert: param, sa-11_odp.03 }};
the developer of the system, system component, or system service is required at all post-design stages of the system development life cycle to produce evidence of the execution of the assessment plan;
the developer of the system, system component, or system service is required at all post-design stages of the system development life cycle to produce the results of the testing and evaluation;
the developer of the system, system component, or system service is required at all post-design stages of the system development life cycle to implement a verifiable flaw remediation process;
the developer of the system, system component, or system service is required at all post-design stages of the system development life cycle to correct flaws identified during testing and evaluation.
System and services acquisition policy

system and services acquisition procedures

procedures addressing system developer security and privacy testing

procedures addressing flaw remediation

solicitation documentation

acquisition documentation

service level agreements

acquisition contracts for the system, system component, or system service

security and privacy architecture

system design documentation

system developer security and privacy assessment plans

results of developer security and privacy assessments for the system, system component, or system service

security and privacy flaw and remediation tracking records

system security plan

privacy plan

privacy impact assessment

privacy risk assessment documentation

other relevant documents or records
Organizational personnel with system and service acquisition responsibilities

organizational personnel with information security and privacy responsibilities

organizational personnel with developer security and privacy testing responsibilities

system developers
Organizational processes for monitoring developer security testing and evaluation

mechanisms supporting and/or implementing the monitoring of developer security and privacy testing and evaluation*

---

### Sample Match 10: `MAS-6.5.3.d` ⟷ `NIST-IA-9`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.82` | Dense Sim: `0.50`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0238 (Max Dense Sim: 0.50)
* **Defensible Rationale**:
```text
• MAS Requirement: must conduct proper testing before deploying end-user developed or acquired applications.
• NIST Control: NIST-IA-9 Service Identification and Authentication: Uniquely identify and authenticate {{ insert: param, ia-09_odp }} before establishing communications with devices, users, or other services or applications..
• Gap Analysis: Covered: [Control B mandates cryptographic verification (e.g., code signing, provenance graphs) to authenticate the source of applications before communication, which serves as a technical validation step within the deployment lifecycle.], Missing: [Control B lacks requirements for functional testing, quality assurance, or validation of application logic and business rules prior to deployment.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-IA-9 provides technical control capabilities addressing obligations in MAS-6.5.3.d.)
```

> **MAS TRM Clause [MAS-6.5.3.d]**:
> *The Financial Institution must conduct proper testing before deploying end-user developed or acquired applications.*

> **NIST SP 800-53 Control [NIST-IA-9 - Service Identification and Authentication]**:
> *Uniquely identify and authenticate {{ insert: param, ia-09_odp }} before establishing communications with devices, users, or other services or applications.
Services that may require identification and authentication include web applications using digital certificates or services or applications that query a database. Identification and authentication methods for system services and applications include information or code signing, provenance graphs, and electronic signatures that indicate the sources of services. Decisions regarding the validity of identification and authentication claims can be made by services separate from the services acting on those decisions. This can occur in distributed system architectures. In such situations, the identification and authentication decisions (instead of actual identifiers and authentication data) are provided to the services that need to act on those decisions.
{{ insert: param, ia-09_odp }} are uniquely identified and authenticated before establishing communications with devices, users, or other services or applications.
Identification and authentication policy

procedures addressing service identification and authentication

system security plan

system design documentation

security safeguards used to identify and authenticate system services

system configuration settings and associated documentation

system audit records

other relevant documents or records
Organizational personnel with system operations responsibilities

organizational personnel with information security responsibilities

system/network administrators

system developers

organizational personnel with identification and authentication responsibilities
Security safeguards implementing service identification and authentication capabilities*

---

### Sample Match 11: `MAS-7.3.1.a` ⟷ `NIST-SC-51`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.82` | Dense Sim: `0.59`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0291 (Max Dense Sim: 0.59)
* **Defensible Rationale**:
```text
• MAS Requirement: must avoid using outdated and unsupported hardware or software.
• NIST Control: NIST-SC-51 Hardware-based Protection: Employ hardware-based, write-protect for {{ insert: param, sc-51_odp.01 }} ; and.
• Gap Analysis: Covered: [Control B mandates hardware-based write-protect and specific procedures for firmware modification, addressing the security integrity of firmware components.], Missing: [Control B does not address the lifecycle management, obsolescence tracking, or replacement of outdated/unsupported hardware or software beyond firmware.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SC-51 provides technical control capabilities addressing obligations in MAS-7.3.1.a.)
```

> **MAS TRM Clause [MAS-7.3.1.a]**:
> *The Financial Institution must avoid using outdated and unsupported hardware or software.*

> **NIST SP 800-53 Control [NIST-SC-51 - Hardware-based Protection]**:
> *Employ hardware-based, write-protect for {{ insert: param, sc-51_odp.01 }} ; and
Implement specific procedures for {{ insert: param, sc-51_odp.02 }} to manually disable hardware write-protect for firmware modifications and re-enable the write-protect prior to returning to operational mode.
None.
hardware-based write-protect for {{ insert: param, sc-51_odp.01 }} is employed;
specific procedures are implemented for {{ insert: param, sc-51_odp.02 }} to manually disable hardware write-protect for firmware modifications;
specific procedures are implemented for {{ insert: param, sc-51_odp.02 }} to re-enable the write-protect prior to returning to operational mode.
System and communications protection policy

procedures addressing firmware modifications

system design documentation

system configuration settings and associated documentation

system architecture

system audit records

system security plan

other relevant documents or records
System/network administrators

organizational personnel with information security responsibilities

organizational personnel installing, configuring, and/or maintaining the system

system developers/integrators
Organizational processes for modifying system firmware

mechanisms supporting and/or implementing hardware-based write-protection for system firmware*

---

### Sample Match 12: `MAS-7.3.2.c` ⟷ `NIST-SA-20`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.85` | Dense Sim: `0.69`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0583 (Max Dense Sim: 0.69)
* **Defensible Rationale**:
```text
• MAS Requirement: must implement effective risk mitigation measures for hardware and software approaching their end-of-support date.
• NIST Control: NIST-SA-20 Customized Development of Critical Components: Reimplement or custom develop the following critical system components: {{ insert: param, sa-20_odp }}..
• Gap Analysis: Covered: [Control B mandates the reimplementation or custom development of critical components to address unmitigated vulnerabilities and trust issues, which serves as a valid risk mitigation strategy for end-of-support hardware and software.], Missing: [Control B is restricted to components with specific unmitigated threats and lacks requirements for general lifecycle management, patching, or compensating controls for end-of-support items that do not pose immediate critical security failures.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SA-20 provides technical control capabilities addressing obligations in MAS-7.3.2.c.)
```

> **MAS TRM Clause [MAS-7.3.2.c]**:
> *The Financial Institution must implement effective risk mitigation measures for hardware and software approaching their end-of-support date.*

> **NIST SP 800-53 Control [NIST-SA-20 - Customized Development of Critical Components]**:
> *Reimplement or custom develop the following critical system components: {{ insert: param, sa-20_odp }}.
Organizations determine that certain system components likely cannot be trusted due to specific threats to and vulnerabilities in those components for which there are no viable security controls to adequately mitigate risk. Reimplementation or custom development of such components may satisfy requirements for higher assurance and is carried out by initiating changes to system components (including hardware, software, and firmware) such that the standard attacks by adversaries are less likely to succeed. In situations where no alternative sourcing is available and organizations choose not to reimplement or custom develop critical system components, additional controls can be employed. Controls include enhanced auditing, restrictions on source code and system utility access, and protection from deletion of system and application files.
{{ insert: param, sa-20_odp }} are reimplemented or custom-developed.
Supply chain risk management plan

system and services acquisition policy

procedures addressing the customized development of critical system components

system design documentation

system configuration settings and associated documentation

system development life cycle documentation addressing the custom development of critical system components

configuration management records

system audit records

system security plan

other relevant documents or records
Organizational personnel with system and service acquisition responsibilities

organizational personnel with information security responsibilities

organizational personnel with responsibility for the reimplementation or customized development of critical system components
Organizational processes for the reimplementation or customized development of critical system components

mechanisms supporting and/or implementing the reimplementation or customized development of critical system components*

---

### Sample Match 13: `MAS-7.5.7` ⟷ `NIST-MA-2`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.83` | Dense Sim: `0.58`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0344 (Max Dense Sim: 0.58)
* **Defensible Rationale**:
```text
• MAS Requirement: must enable the logging facility to record activities performed during the change process.
• NIST Control: NIST-MA-2 Controlled Maintenance: Schedule, document, and review records of maintenance, repair, and replacement on system components in accordance with manufacturer or vendor specifications and/or organizational requirements;.
• Gap Analysis: Covered: [Control B mandates the documentation and review of maintenance records, which inherently includes logging the activities performed during the change process.], Missing: [Control B is limited to system maintenance and repair, whereas Requirement A applies to the entire change process (including software updates, configuration changes, and patches) and does not explicitly mandate logging for non-maintenance changes.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-MA-2 provides technical control capabilities addressing obligations in MAS-7.5.7.)
```

> **MAS TRM Clause [MAS-7.5.7]**:
> *The Financial Institution must enable the logging facility to record activities performed during the change process.*

> **NIST SP 800-53 Control [NIST-MA-2 - Controlled Maintenance]**:
> *Schedule, document, and review records of maintenance, repair, and replacement on system components in accordance with manufacturer or vendor specifications and/or organizational requirements;
Approve and monitor all maintenance activities, whether performed on site or remotely and whether the system or system components are serviced on site or removed to another location;
Require that {{ insert: param, ma-02_odp.01 }} explicitly approve the removal of the system or system components from organizational facilities for off-site maintenance, repair, or replacement;
Sanitize equipment to remove the following information from associated media prior to removal from organizational facilities for off-site maintenance, repair, or replacement: {{ insert: param, ma-02_odp.02 }};
Check all potentially impacted controls to verify that the controls are still functioning properly following maintenance, repair, or replacement actions; and
Include the following information in organizational maintenance records: {{ insert: param, ma-02_odp.03 }}.
Controlling system maintenance addresses the information security aspects of the system maintenance program and applies to all types of maintenance to system components conducted by local or nonlocal entities. Maintenance includes peripherals such as scanners, copiers, and printers. Information necessary for creating effective maintenance records includes the date and time of maintenance, a description of the maintenance performed, names of the individuals or group performing the maintenance, name of the escort, and system components or equipment that are removed or replaced. Organizations consider supply chain-related risks associated with replacement components for systems.
maintenance, repair, and replacement of system components are scheduled in accordance with manufacturer or vendor specifications and/or organizational requirements;
maintenance, repair, and replacement of system components are documented in accordance with manufacturer or vendor specifications and/or organizational requirements;
records of maintenance, repair, and replacement of system components are reviewed in accordance with manufacturer or vendor specifications and/or organizational requirements;
all maintenance activities, whether performed on site or remotely and whether the system or system components are serviced on site or removed to another location, are approved;
all maintenance activities, whether performed on site or remotely and whether the system or system components are serviced on site or removed to another location, are monitored;
{{ insert: param, ma-02_odp.01 }} is/are required to explicitly approve the removal of the system or system components from organizational facilities for off-site maintenance, repair, or replacement;
equipment is sanitized to remove {{ insert: param, ma-02_odp.02 }} from associated media prior to removal from organizational facilities for off-site maintenance, repair, or replacement;
all potentially impacted controls are checked to verify that the controls are still functioning properly following maintenance, repair, or replacement actions;
{{ insert: param, ma-02_odp.03 }} is included in organizational maintenance records.
Maintenance policy

procedures addressing controlled system maintenance

maintenance records

manufacturer/vendor maintenance specifications

equipment sanitization records

media sanitization records

system security plan

other relevant documents or records
Organizational personnel with system maintenance responsibilities

organizational personnel with information security responsibilities

organizational personnel responsible for media sanitization

system/network administrators
Organizational processes for scheduling, performing, documenting, reviewing, approving, and monitoring maintenance and repairs for the system

organizational processes for sanitizing system components

mechanisms supporting and/or implementing controlled maintenance

mechanisms implementing the sanitization of system components*

---

### Sample Match 14: `MAS-7.7.2` ⟷ `NIST-AU-4`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.83` | Dense Sim: `0.55`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0355 (Max Dense Sim: 0.55)
* **Defensible Rationale**:
```text
• MAS Requirement: must allocate sufficient resources to facilitate and support incident response and recovery.
• NIST Control: NIST-AU-4 Audit Log Storage Capacity: Allocate audit log storage capacity to accommodate {{ insert: param, au-04_odp }}..
• Gap Analysis: Covered: [Control B mandates the allocation of specific technical storage capacity for audit logs to ensure logging continuity.], Missing: [Control B lacks mandates for broader resource allocation required for incident response activities (e.g., personnel, tools, communication channels) and business recovery operations.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-AU-4 provides technical control capabilities addressing obligations in MAS-7.7.2.)
```

> **MAS TRM Clause [MAS-7.7.2]**:
> *The Financial Institution must allocate sufficient resources to facilitate and support incident response and recovery.*

> **NIST SP 800-53 Control [NIST-AU-4 - Audit Log Storage Capacity]**:
> *Allocate audit log storage capacity to accommodate {{ insert: param, au-04_odp }}.
Organizations consider the types of audit logging to be performed and the audit log processing requirements when allocating audit log storage capacity. Allocating sufficient audit log storage capacity reduces the likelihood of such capacity being exceeded and resulting in the potential loss or reduction of audit logging capability.
audit log storage capacity is allocated to accommodate {{ insert: param, au-04_odp }}.
Audit and accountability policy

procedures addressing audit storage capacity

system security plan

privacy plan

system design documentation

system configuration settings and associated documentation

audit record storage requirements

audit record storage capability for system components

system audit records

other relevant documents or records
Organizational personnel with audit and accountability responsibilities

organizational personnel with information security and privacy responsibilities

system/network administrators

system developers
Audit record storage capacity and related configuration settings*

---

### Sample Match 15: `MAS-7.7.3.c` ⟷ `NIST-PS-7`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.85` | Dense Sim: `0.64`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0355 (Max Dense Sim: 0.64)
* **Defensible Rationale**:
```text
• MAS Requirement: must define the roles and responsibilities of staff and external parties involved in incident recording, analysis, escalation, decision-making, resolution, and monitoring within the incident management framework.
• NIST Control: NIST-PS-7 External Personnel Security: Establish personnel security requirements, including security roles and responsibilities for external providers;.
• Gap Analysis: Covered: [Control B mandates defining and documenting security roles/responsibilities for external providers and monitoring their compliance.], Missing: [Control B lacks mandates for internal staff roles, and does not address the full incident management lifecycle (recording, analysis, escalation, decision-making, resolution, monitoring).].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PS-7 provides technical control capabilities addressing obligations in MAS-7.7.3.c.)
```

> **MAS TRM Clause [MAS-7.7.3.c]**:
> *The Financial Institution must define the roles and responsibilities of staff and external parties involved in incident recording, analysis, escalation, decision-making, resolution, and monitoring within the incident management framework.*

> **NIST SP 800-53 Control [NIST-PS-7 - External Personnel Security]**:
> *Establish personnel security requirements, including security roles and responsibilities for external providers;
Require external providers to comply with personnel security policies and procedures established by the organization;
Document personnel security requirements;
Require external providers to notify {{ insert: param, ps-07_odp.01 }} of any personnel transfers or terminations of external personnel who possess organizational credentials and/or badges, or who have system privileges within {{ insert: param, ps-07_odp.02 }} ; and
Monitor provider compliance with personnel security requirements.
External provider refers to organizations other than the organization operating or acquiring the system. External providers include service bureaus, contractors, and other organizations that provide system development, information technology services, testing or assessment services, outsourced applications, and network/security management. Organizations explicitly include personnel security requirements in acquisition-related documents. External providers may have personnel working at organizational facilities with credentials, badges, or system privileges issued by organizations. Notifications of external personnel changes ensure the appropriate termination of privileges and credentials. Organizations define the transfers and terminations deemed reportable by security-related characteristics that include functions, roles, and the nature of credentials or privileges associated with transferred or terminated individuals.
personnel security requirements are established, including security roles and responsibilities for external providers;
external providers are required to comply with personnel security policies and procedures established by the organization;
personnel security requirements are documented;
external providers are required to notify {{ insert: param, ps-07_odp.01 }} of any personnel transfers or terminations of external personnel who possess organizational credentials and/or badges or who have system privileges within {{ insert: param, ps-07_odp.02 }};
provider compliance with personnel security requirements is monitored.
Personnel security policy

procedures addressing external personnel security

list of personnel security requirements

acquisition documents

service-level agreements

compliance monitoring process

system security plan

other relevant documents or records
Organizational personnel with personnel security responsibilities

external providers

system/network administrators

organizational personnel with account management responsibilities

organizational personnel with information security responsibilities
Organizational processes for managing and monitoring external personnel security

mechanisms supporting and/or implementing the monitoring of provider compliance*

---

### Sample Match 16: `MAS-13.5.1` ⟷ `NIST-PM-14`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.83` | Dense Sim: `0.68`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0527 (Max Dense Sim: 0.68)
* **Defensible Rationale**:
```text
• MAS Requirement: must design the threat scenario based on challenging but plausible cyber threats to simulate realistic adversarial attacks during any cyber security assessment.
• NIST Control: NIST-PM-14 Testing, Training, and Monitoring: Implement a process for ensuring that organizational plans for conducting security and privacy testing, training, and monitoring activities associated with organizational systems:.
• Gap Analysis: Covered: [Control B mandates the development, maintenance, and execution of testing plans informed by current threat and vulnerability assessments.], Missing: [Control B lacks the specific mandate to design threat scenarios that are 'challenging but plausible' to simulate 'realistic adversarial attacks' as required by Requirement A.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-14 provides technical control capabilities addressing obligations in MAS-13.5.1.)
```

> **MAS TRM Clause [MAS-13.5.1]**:
> *The Financial Institution must design the threat scenario based on challenging but plausible cyber threats to simulate realistic adversarial attacks during any cyber security assessment.*

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

### Sample Match 17: `MAS-13.6.1.a` ⟷ `NIST-CA-7`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.83` | Dense Sim: `0.60`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0286 (Max Dense Sim: 0.60)
* **Defensible Rationale**:
```text
• MAS Requirement: must perform severity assessment and classification of an issue.
• NIST Control: NIST-CA-7 Continuous Monitoring: Develop a system-level continuous monitoring strategy and implement continuous monitoring in accordance with the organization-level continuous monitoring strategy that includes:.
• Gap Analysis: Covered: [Control B mandates ongoing control assessments and correlation/analysis of monitoring information, which inherently require and facilitate the severity assessment and classification of issues to determine response actions.], Missing: [Control B focuses on continuous monitoring of system controls and metrics rather than a standalone, explicit mandate for the initial severity assessment and classification of specific issues or incidents.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-CA-7 provides technical control capabilities addressing obligations in MAS-13.6.1.a.)
```

> **MAS TRM Clause [MAS-13.6.1.a]**:
> *The Financial Institution must perform severity assessment and classification of an issue.*

> **NIST SP 800-53 Control [NIST-CA-7 - Continuous Monitoring]**:
> *Develop a system-level continuous monitoring strategy and implement continuous monitoring in accordance with the organization-level continuous monitoring strategy that includes:
Establishing the following system-level metrics to be monitored: {{ insert: param, ca-07_odp.01 }};
Establishing {{ insert: param, ca-07_odp.02 }} for monitoring and {{ insert: param, ca-07_odp.03 }} for assessment of control effectiveness;
Ongoing control assessments in accordance with the continuous monitoring strategy;
Ongoing monitoring of system and organization-defined metrics in accordance with the continuous monitoring strategy;
Correlation and analysis of information generated by control assessments and monitoring;
Response actions to address results of the analysis of control assessment and monitoring information; and
Reporting the security and privacy status of the system to {{ insert: param, ca-7_prm_4 }} {{ insert: param, ca-7_prm_5 }}.
Continuous monitoring at the system level facilitates ongoing awareness of the system security and privacy posture to support organizational risk management decisions. The terms "continuous" and "ongoing" imply that organizations assess and monitor their controls and risks at a frequency sufficient to support risk-based decisions. Different types of controls may require different monitoring frequencies. The results of continuous monitoring generate risk response actions by organizations. When monitoring the effectiveness of multiple controls that have been grouped into capabilities, a root-cause analysis may be needed to determine the specific control that has failed. Continuous monitoring programs allow organizations to maintain the authorizations of systems and common controls in highly dynamic environments of operation with changing mission and business needs, threats, vulnerabilities, and technologies. Having access to security and privacy information on a continuing basis through reports and dashboards gives organizational officials the ability to make effective and timely risk management decisions, including ongoing authorization decisions.

Automation supports more frequent updates to hardware, software, and firmware inventories, authorization packages, and other system information. Effectiveness is further enhanced when continuous monitoring outputs are formatted to provide information that is specific, measurable, actionable, relevant, and timely. Continuous monitoring activities are scaled in accordance with the security categories of systems. Monitoring requirements, including the need for specific monitoring, may be referenced in other controls and control enhancements, such as [AC-2g](#ac-2_smt.g), [AC-2(7)](#ac-2.7), [AC-2(12)(a)](#ac-2.12_smt.a), [AC-2(7)(b)](#ac-2.7_smt.b), [AC-2(7)(c)](#ac-2.7_smt.c), [AC-17(1)](#ac-17.1), [AT-4a](#at-4_smt.a), [AU-13](#au-13), [AU-13(1)](#au-13.1), [AU-13(2)](#au-13.2), [CM-3f](#cm-3_smt.f), [CM-6d](#cm-6_smt.d), [CM-11c](#cm-11_smt.c), [IR-5](#ir-5), [MA-2b](#ma-2_smt.b), [MA-3a](#ma-3_smt.a), [MA-4a](#ma-4_smt.a), [PE-3d](#pe-3_smt.d), [PE-6](#pe-6), [PE-14b](#pe-14_smt.b), [PE-16](#pe-16), [PE-20](#pe-20), [PM-6](#pm-6), [PM-23](#pm-23), [PM-31](#pm-31), [PS-7e](#ps-7_smt.e), [SA-9c](#sa-9_smt.c), [SR-4](#sr-4), [SC-5(3)(b)](#sc-5.3_smt.b), [SC-7a](#sc-7_smt.a), [SC-7(24)(b)](#sc-7.24_smt.b), [SC-18b](#sc-18_smt.b), [SC-43b](#sc-43_smt.b) , and [SI-4](#si-4).
a system-level continuous monitoring strategy is developed;
system-level continuous monitoring is implemented in accordance with the organization-level continuous monitoring strategy;
system-level continuous monitoring includes establishment of the following system-level metrics to be monitored: {{ insert: param, ca-07_odp.01 }};
system-level continuous monitoring includes established {{ insert: param, ca-07_odp.02 }} for monitoring;
system-level continuous monitoring includes established {{ insert: param, ca-07_odp.03 }} for assessment of control effectiveness;
system-level continuous monitoring includes ongoing control assessments in accordance with the continuous monitoring strategy;
system-level continuous monitoring includes ongoing monitoring of system and organization-defined metrics in accordance with the continuous monitoring strategy;
system-level continuous monitoring includes correlation and analysis of information generated by control assessments and monitoring;
system-level continuous monitoring includes response actions to address the results of the analysis of control assessment and monitoring information;
system-level continuous monitoring includes reporting the security status of the system to {{ insert: param, ca-07_odp.04 }} {{ insert: param, ca-07_odp.05 }};
system-level continuous monitoring includes reporting the privacy status of the system to {{ insert: param, ca-07_odp.06 }} {{ insert: param, ca-07_odp.07 }}.
Assessment, authorization, and monitoring policy

organizational continuous monitoring strategy

system-level continuous monitoring strategy

procedures addressing continuous monitoring of system controls

procedures addressing configuration management

control assessment report

plan of action and milestones

system monitoring records

configuration management records

impact analyses

status reports

system security plan

privacy plan

other relevant documents or records
Organizational personnel with continuous monitoring responsibilities

organizational personnel with information security and privacy responsibilities

system/network administrators
Mechanisms implementing continuous monitoring

mechanisms supporting response actions to address assessment and monitoring results

mechanisms supporting security and privacy status reporting*

---

### Sample Match 18: `MAS-14.1.2` ⟷ `NIST-SC-8`

* **Semantic Relation**: `EQUIVALENT`
* **Assurance Coverage**: `FULL_COVERAGE` (Dynamic Confidence: `0.85` | Dense Sim: `0.67`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0364 (Max Dense Sim: 0.67)
* **Defensible Rationale**:
```text
• MAS Requirement: must secure its communications channels to protect customer data.
• NIST Control: NIST-SC-8 Transmission Confidentiality and Integrity: Protect the {{ insert: param, sc-08_odp }} of transmitted information..
• Gap Analysis: Covered: [Control B mandates logical protection via encryption techniques to ensure the confidentiality and integrity of transmitted information across all network components.], Missing: [None: Full coverage].
• Assurance Conclusion: FULL_COVERAGE (NIST-SC-8 provides technical control capabilities addressing obligations in MAS-14.1.2.)
```

> **MAS TRM Clause [MAS-14.1.2]**:
> *The Financial Institution must secure its communications channels to protect customer data.*

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

### Sample Match 19: `MAS-14.1.6.a` ⟷ `NIST-SI-4`

* **Semantic Relation**: `SUPERSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.82` | Dense Sim: `0.58`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0301 (Max Dense Sim: 0.58)
* **Defensible Rationale**:
```text
• MAS Requirement: must actively monitor for phishing campaigns targeting the Financial Institution and its customers.
• NIST Control: NIST-SI-4 System Monitoring: Monitor the system to detect:.
• Gap Analysis: Covered: [Control B mandates comprehensive system monitoring for attacks, unauthorized connections, and anomalies, which provides the technical infrastructure to detect phishing-related network traffic and indicators.], Missing: [Control B lacks specific mandates for monitoring external phishing campaigns targeting customers, analyzing email content for social engineering, and implementing user-awareness or reporting mechanisms specific to phishing.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SI-4 provides technical control capabilities addressing obligations in MAS-14.1.6.a.)
```

> **MAS TRM Clause [MAS-14.1.6.a]**:
> *The Financial Institution must actively monitor for phishing campaigns targeting the Financial Institution and its customers.*

> **NIST SP 800-53 Control [NIST-SI-4 - System Monitoring]**:
> *Monitor the system to detect:
Attacks and indicators of potential attacks in accordance with the following monitoring objectives: {{ insert: param, si-04_odp.01 }} ; and
Unauthorized local, network, and remote connections;
Identify unauthorized use of the system through the following techniques and methods: {{ insert: param, si-04_odp.02 }};
Invoke internal monitoring capabilities or deploy monitoring devices:
Strategically within the system to collect organization-determined essential information; and
At ad hoc locations within the system to track specific types of transactions of interest to the organization;
Analyze detected events and anomalies;
Adjust the level of system monitoring activity when there is a change in risk to organizational operations and assets, individuals, other organizations, or the Nation;
Obtain legal opinion regarding system monitoring activities; and
Provide {{ insert: param, si-04_odp.03 }} to {{ insert: param, si-04_odp.04 }} {{ insert: param, si-04_odp.05 }}.
System monitoring includes external and internal monitoring. External monitoring includes the observation of events occurring at external interfaces to the system. Internal monitoring includes the observation of events occurring within the system. Organizations monitor systems by observing audit activities in real time or by observing other system aspects such as access patterns, characteristics of access, and other actions. The monitoring objectives guide and inform the determination of the events. System monitoring capabilities are achieved through a variety of tools and techniques, including intrusion detection and prevention systems, malicious code protection software, scanning tools, audit record monitoring software, and network monitoring software.

Depending on the security architecture, the distribution and configuration of monitoring devices may impact throughput at key internal and external boundaries as well as at other locations across a network due to the introduction of network throughput latency. If throughput management is needed, such devices are strategically located and deployed as part of an established organization-wide security architecture. Strategic locations for monitoring devices include selected perimeter locations and near key servers and server farms that support critical applications. Monitoring devices are typically employed at the managed interfaces associated with controls [SC-7](#sc-7) and [AC-17](#ac-17) . The information collected is a function of the organizational monitoring objectives and the capability of systems to support such objectives. Specific types of transactions of interest include Hypertext Transfer Protocol (HTTP) traffic that bypasses HTTP proxies. System monitoring is an integral part of organizational continuous monitoring and incident response programs, and output from system monitoring serves as input to those programs. System monitoring requirements, including the need for specific types of system monitoring, may be referenced in other controls (e.g., [AC-2g](#ac-2_smt.g), [AC-2(7)](#ac-2.7), [AC-2(12)(a)](#ac-2.12_smt.a), [AC-17(1)](#ac-17.1), [AU-13](#au-13), [AU-13(1)](#au-13.1), [AU-13(2)](#au-13.2), [CM-3f](#cm-3_smt.f), [CM-6d](#cm-6_smt.d), [MA-3a](#ma-3_smt.a), [MA-4a](#ma-4_smt.a), [SC-5(3)(b)](#sc-5.3_smt.b), [SC-7a](#sc-7_smt.a), [SC-7(24)(b)](#sc-7.24_smt.b), [SC-18b](#sc-18_smt.b), [SC-43b](#sc-43_smt.b) ). Adjustments to levels of system monitoring are based on law enforcement information, intelligence information, or other sources of information. The legality of system monitoring activities is based on applicable laws, executive orders, directives, regulations, policies, standards, and guidelines.
the system is monitored to detect attacks and indicators of potential attacks in accordance with {{ insert: param, si-04_odp.01 }};
the system is monitored to detect unauthorized local connections;
the system is monitored to detect unauthorized network connections;
the system is monitored to detect unauthorized remote connections;
unauthorized use of the system is identified through {{ insert: param, si-04_odp.02 }};
internal monitoring capabilities are invoked or monitoring devices are deployed strategically within the system to collect organization-determined essential information;
internal monitoring capabilities are invoked or monitoring devices are deployed at ad hoc locations within the system to track specific types of transactions of interest to the organization;
detected events are analyzed;
detected anomalies are analyzed;
the level of system monitoring activity is adjusted when there is a change in risk to organizational operations and assets, individuals, other organizations, or the Nation;
a legal opinion regarding system monitoring activities is obtained;
{{ insert: param, si-04_odp.03 }} is provided to {{ insert: param, si-04_odp.04 }} {{ insert: param, si-04_odp.05 }}.
System and information integrity policy

system and information integrity procedures

procedures addressing system monitoring tools and techniques

continuous monitoring strategy

facility diagram/layout

system design documentation

system monitoring tools and techniques documentation

locations within the system where monitoring devices are deployed

system configuration settings and associated documentation

system security plan

other relevant documents or records
System/network administrators

organizational personnel with information security responsibilities

organizational personnel installing, configuring, and/or maintaining the system

organizational personnel responsible for monitoring the system
Organizational processes for system monitoring

mechanisms supporting and/or implementing system monitoring capabilities*

---

### Sample Match 20: `MAS-14.2.11.b` ⟷ `NIST-IA-7`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.85` | Dense Sim: `0.67`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0727 (Max Dense Sim: 0.67)
* **Defensible Rationale**:
```text
• MAS Requirement: must implement a process and procedure to revoke and replace authentication credentials and mechanisms that have been compromised.
• NIST Control: NIST-IA-7 Cryptographic Module Authentication: Implement mechanisms for authentication to a cryptographic module that meet the requirements of applicable laws, executive orders, directives, policies, regulations, standards, and guidelines for such authentication..
• Gap Analysis: Covered: [Control B mandates the implementation of authentication mechanisms and associated policies/procedures for cryptographic modules, which provides the foundational technical infrastructure for credential management.], Missing: [Control B lacks explicit mandates for the revocation and replacement of credentials specifically in response to compromise events, focusing instead on initial authentication and role authorization.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-IA-7 provides technical control capabilities addressing obligations in MAS-14.2.11.b.)
```

> **MAS TRM Clause [MAS-14.2.11.b]**:
> *The Financial Institution must implement a process and procedure to revoke and replace authentication credentials and mechanisms that have been compromised.*

> **NIST SP 800-53 Control [NIST-IA-7 - Cryptographic Module Authentication]**:
> *Implement mechanisms for authentication to a cryptographic module that meet the requirements of applicable laws, executive orders, directives, policies, regulations, standards, and guidelines for such authentication.
Authentication mechanisms may be required within a cryptographic module to authenticate an operator accessing the module and to verify that the operator is authorized to assume the requested role and perform services within that role.
mechanisms for authentication to a cryptographic module are implemented that meet the requirements of applicable laws, executive orders, directives, policies, regulations, standards, and guidelines for such authentication.
Identification and authentication policy

system security plan

procedures addressing cryptographic module authentication

system design documentation

system configuration settings and associated documentation

system audit records

other relevant documents or records
Organizational personnel with responsibility for cryptographic module authentication

organizational personnel with information security responsibilities

system/network administrators

system developers
Mechanisms supporting and/or implementing cryptographic module authentication*

---

### Sample Match 21: `MAS-15.1.1` ⟷ `NIST-RA-7`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.83` | Dense Sim: `0.59`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0289 (Max Dense Sim: 0.59)
* **Defensible Rationale**:
```text
• MAS Requirement: must conduct IT audit to provide the board of directors and senior management an independent and objective opinion on the adequacy and effectiveness of risk management, governance, and internal controls relative to existing and emerging technology risks.
• NIST Control: NIST-RA-7 Risk Response: Respond to findings from security and privacy assessments, monitoring, and audits in accordance with organizational risk tolerance..
• Gap Analysis: Covered: [Control B mandates the operational response to audit findings based on risk tolerance, which is a downstream activity of the audit process required by Requirement A.], Missing: [Control B lacks the mandate for the independent audit execution itself, the requirement for an independent opinion, and the specific governance obligation to report to the board and senior management.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-7 provides technical control capabilities addressing obligations in MAS-15.1.1.)
```

> **MAS TRM Clause [MAS-15.1.1]**:
> *The Financial Institution must conduct IT audit to provide the board of directors and senior management an independent and objective opinion on the adequacy and effectiveness of risk management, governance, and internal controls relative to existing and emerging technology risks.*

> **NIST SP 800-53 Control [NIST-RA-7 - Risk Response]**:
> *Respond to findings from security and privacy assessments, monitoring, and audits in accordance with organizational risk tolerance.
Organizations have many options for responding to risk including mitigating risk by implementing new controls or strengthening existing controls, accepting risk with appropriate justification or rationale, sharing or transferring risk, or avoiding risk. The risk tolerance of the organization influences risk response decisions and actions. Risk response addresses the need to determine an appropriate response to risk before generating a plan of action and milestones entry. For example, the response may be to accept risk or reject risk, or it may be possible to mitigate the risk immediately so that a plan of action and milestones entry is not needed. However, if the risk response is to mitigate the risk, and the mitigation cannot be completed immediately, a plan of action and milestones entry is generated.
findings from security assessments are responded to in accordance with organizational risk tolerance;
findings from privacy assessments are responded to in accordance with organizational risk tolerance;
findings from monitoring are responded to in accordance with organizational risk tolerance;
findings from audits are responded to in accordance with organizational risk tolerance.
Risk assessment policy

assessment reports

audit records/event logs

system security plan

privacy plan

other relevant documents or records
Organizational personnel with assessment and auditing responsibilities

system/network administrators

organizational personnel with security and privacy responsibilities
Organizational processes for assessments and audits

mechanisms/tools supporting and/or implementing assessments and auditing*

---

### Sample Match 22: `MAS-15.1.4.a` ⟷ `NIST-AT-1`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.84` | Dense Sim: `0.53`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0274 (Max Dense Sim: 0.53)
* **Defensible Rationale**:
```text
• MAS Requirement: must verify that its IT auditors possess the requisite level of competency and skills to effectively assess and evaluate the adequacy of implemented IT policies, procedures, processes, and controls.
• NIST Control: NIST-AT-1 Policy and Procedures: Develop, document, and disseminate to {{ insert: param, at-1_prm_1 }}:.
• Gap Analysis: Covered: [Control B mandates the development and dissemination of an awareness and training policy, which provides the governance framework for ensuring personnel competency.], Missing: [Control B lacks specific mandates for the verification of individual auditor competency, skills assessment, or evaluation of adequacy, focusing instead on general organizational policy and procedures.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-AT-1 provides technical control capabilities addressing obligations in MAS-15.1.4.a.)
```

> **MAS TRM Clause [MAS-15.1.4.a]**:
> *The Financial Institution must verify that its IT auditors possess the requisite level of competency and skills to effectively assess and evaluate the adequacy of implemented IT policies, procedures, processes, and controls.*

> **NIST SP 800-53 Control [NIST-AT-1 - Policy and Procedures]**:
> *Develop, document, and disseminate to {{ insert: param, at-1_prm_1 }}:
{{ insert: param, at-01_odp.03 }} awareness and training policy that:
Addresses purpose, scope, roles, responsibilities, management commitment, coordination among organizational entities, and compliance; and
Is consistent with applicable laws, executive orders, directives, regulations, policies, standards, and guidelines; and
Procedures to facilitate the implementation of the awareness and training policy and the associated awareness and training controls;
Designate an {{ insert: param, at-01_odp.04 }} to manage the development, documentation, and dissemination of the awareness and training policy and procedures; and
Review and update the current awareness and training:
Policy {{ insert: param, at-01_odp.05 }} and following {{ insert: param, at-01_odp.06 }} ; and
Procedures {{ insert: param, at-01_odp.07 }} and following {{ insert: param, at-01_odp.08 }}.
Awareness and training policy and procedures address the controls in the AT family that are implemented within systems and organizations. The risk management strategy is an important factor in establishing such policies and procedures. Policies and procedures contribute to security and privacy assurance. Therefore, it is important that security and privacy programs collaborate on the development of awareness and training policy and procedures. Security and privacy program policies and procedures at the organization level are preferable, in general, and may obviate the need for mission- or system-specific policies and procedures. The policy can be included as part of the general security and privacy policy or be represented by multiple policies that reflect the complex nature of organizations. Procedures can be established for security and privacy programs, for mission or business processes, and for systems, if needed. Procedures describe how the policies or controls are implemented and can be directed at the individual or role that is the object of the procedure. Procedures can be documented in system security and privacy plans or in one or more separate documents. Events that may precipitate an update to awareness and training policy and procedures include assessment or audit findings, security incidents or breaches, or changes in applicable laws, executive orders, directives, regulations, policies, standards, and guidelines. Simply restating controls does not constitute an organizational policy or procedure.
an awareness and training policy is developed and documented;
the awareness and training policy is disseminated to {{ insert: param, at-01_odp.01 }};
awareness and training procedures to facilitate the implementation of the awareness and training policy and associated access controls are developed and documented;
the awareness and training procedures are disseminated to {{ insert: param, at-01_odp.02 }}.
the {{ insert: param, at-01_odp.03 }} awareness and training policy addresses purpose;
the {{ insert: param, at-01_odp.03 }} awareness and training policy addresses scope;
the {{ insert: param, at-01_odp.03 }} awareness and training policy addresses roles;
the {{ insert: param, at-01_odp.03 }} awareness and training policy addresses responsibilities;
the {{ insert: param, at-01_odp.03 }} awareness and training policy addresses management commitment;
the {{ insert: param, at-01_odp.03 }} awareness and training policy addresses coordination among organizational entities;
the {{ insert: param, at-01_odp.03 }} awareness and training policy addresses compliance; and
the {{ insert: param, at-01_odp.03 }} awareness and training policy is consistent with applicable laws, Executive Orders, directives, regulations, policies, standards, and guidelines; and
the {{ insert: param, at-01_odp.04 }} is designated to manage the development, documentation, and dissemination of the awareness and training policy and procedures;
the current awareness and training policy is reviewed and updated {{ insert: param, at-01_odp.05 }};
the current awareness and training policy is reviewed and updated following {{ insert: param, at-01_odp.06 }};
the current awareness and training procedures are reviewed and updated {{ insert: param, at-01_odp.07 }};
the current awareness and training procedures are reviewed and updated following {{ insert: param, at-01_odp.08 }}.
System security plan

privacy plan

awareness and training policy and procedures

other relevant documents or records
Organizational personnel with awareness and training responsibilities

organizational personnel with information security and privacy responsibilities*

---

### Sample Match 23: `MAS-5.1.2` ⟷ `NIST-IA-5`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.84` | Dense Sim: `0.57`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0379 (Max Dense Sim: 0.57)
* **Defensible Rationale**:
```text
• MAS Requirement: must verify personal devices before permitting network access to ensure they are not jailbroken, rooted, or compromised.
• NIST Control: NIST-IA-5 Authenticator Management: Manage system authenticators by:.
• Gap Analysis: Covered: [Control B mandates the verification of device identity during initial authenticator distribution and requires devices to implement specific controls to protect authenticators.], Missing: [Control B lacks explicit mandates for technical verification of device integrity states (e.g., detecting jailbreaking, rooting, or compromise) prior to granting network access.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-IA-5 provides technical control capabilities addressing obligations in MAS-5.1.2.)
```

> **MAS TRM Clause [MAS-5.1.2]**:
> *The Financial Institution must verify personal devices before permitting network access to ensure they are not jailbroken, rooted, or compromised.*

> **NIST SP 800-53 Control [NIST-IA-5 - Authenticator Management]**:
> *Manage system authenticators by:
Verifying, as part of the initial authenticator distribution, the identity of the individual, group, role, service, or device receiving the authenticator;
Establishing initial authenticator content for any authenticators issued by the organization;
Ensuring that authenticators have sufficient strength of mechanism for their intended use;
Establishing and implementing administrative procedures for initial authenticator distribution, for lost or compromised or damaged authenticators, and for revoking authenticators;
Changing default authenticators prior to first use;
Changing or refreshing authenticators {{ insert: param, ia-05_odp.01 }} or when {{ insert: param, ia-05_odp.02 }} occur;
Protecting authenticator content from unauthorized disclosure and modification;
Requiring individuals to take, and having devices implement, specific controls to protect authenticators; and
Changing authenticators for group or role accounts when membership to those accounts changes.
Authenticators include passwords, cryptographic devices, biometrics, certificates, one-time password devices, and ID badges. Device authenticators include certificates and passwords. Initial authenticator content is the actual content of the authenticator (e.g., the initial password). In contrast, the requirements for authenticator content contain specific criteria or characteristics (e.g., minimum password length). Developers may deliver system components with factory default authentication credentials (i.e., passwords) to allow for initial installation and configuration. Default authentication credentials are often well known, easily discoverable, and present a significant risk. The requirement to protect individual authenticators may be implemented via control [PL-4](#pl-4) or [PS-6](#ps-6) for authenticators in the possession of individuals and by controls [AC-3](#ac-3), [AC-6](#ac-6) , and [SC-28](#sc-28) for authenticators stored in organizational systems, including passwords stored in hashed or encrypted formats or files containing encrypted or hashed passwords accessible with administrator privileges.

Systems support authenticator management by organization-defined settings and restrictions for various authenticator characteristics (e.g., minimum password length, validation time window for time synchronous one-time tokens, and number of allowed rejections during the verification stage of biometric authentication). Actions can be taken to safeguard individual authenticators, including maintaining possession of authenticators, not sharing authenticators with others, and immediately reporting lost, stolen, or compromised authenticators. Authenticator management includes issuing and revoking authenticators for temporary access when no longer needed.
system authenticators are managed through the verification of the identity of the individual, group, role, service, or device receiving the authenticator as part of the initial authenticator distribution;
system authenticators are managed through the establishment of initial authenticator content for any authenticators issued by the organization;
system authenticators are managed to ensure that authenticators have sufficient strength of mechanism for their intended use;
system authenticators are managed through the establishment and implementation of administrative procedures for initial authenticator distribution; lost, compromised, or damaged authenticators; and the revocation of authenticators;
system authenticators are managed through the change of default authenticators prior to first use;
system authenticators are managed through the change or refreshment of authenticators {{ insert: param, ia-05_odp.01 }} or when {{ insert: param, ia-05_odp.02 }} occur;
system authenticators are managed through the protection of authenticator content from unauthorized disclosure and modification;
system authenticators are managed through the requirement for individuals to take specific controls to protect authenticators;
system authenticators are managed through the requirement for devices to implement specific controls to protect authenticators;
system authenticators are managed through the change of authenticators for group or role accounts when membership to those accounts changes.
Identification and authentication policy

system security plan

addressing authenticator management

system design documentation

system configuration settings and associated documentation

list of system authenticator types

change control records associated with managing system authenticators

system audit records

other relevant documents or records
Organizational personnel with authenticator management responsibilities

organizational personnel with information security responsibilities

system/network administrators
Mechanisms supporting and/or implementing authenticator management capability*

---

### Sample Match 24: `MAS-C.1.3` ⟷ `NIST-SI-7`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.83` | Dense Sim: `0.60`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0262 (Max Dense Sim: 0.60)
* **Defensible Rationale**:
```text
• MAS Requirement: must protect private cryptographic keys.
• NIST Control: NIST-SI-7 Software, Firmware, and Information Integrity: Employ integrity verification tools to detect unauthorized changes to the following software, firmware, and information: {{ insert: param, si-7_prm_1 }} ; and.
• Gap Analysis: Covered: [Control B mandates integrity verification tools (e.g., cryptographic hashes) to detect unauthorized changes to software, firmware, and information, which indirectly protects the integrity of the environment hosting private keys.], Missing: [Control B lacks specific mandates for the secure generation, storage, access control, and lifecycle management of private cryptographic keys themselves.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SI-7 provides technical control capabilities addressing obligations in MAS-C.1.3.)
```

> **MAS TRM Clause [MAS-C.1.3]**:
> *The Financial Institution must protect private cryptographic keys.*

> **NIST SP 800-53 Control [NIST-SI-7 - Software, Firmware, and Information Integrity]**:
> *Employ integrity verification tools to detect unauthorized changes to the following software, firmware, and information: {{ insert: param, si-7_prm_1 }} ; and
Take the following actions when unauthorized changes to the software, firmware, and information are detected: {{ insert: param, si-7_prm_2 }}.
Unauthorized changes to software, firmware, and information can occur due to errors or malicious activity. Software includes operating systems (with key internal components, such as kernels or drivers), middleware, and applications. Firmware interfaces include Unified Extensible Firmware Interface (UEFI) and Basic Input/Output System (BIOS). Information includes personally identifiable information and metadata that contains security and privacy attributes associated with information. Integrity-checking mechanisms—including parity checks, cyclical redundancy checks, cryptographic hashes, and associated tools—can automatically monitor the integrity of systems and hosted applications.
integrity verification tools are employed to detect unauthorized changes to {{ insert: param, si-07_odp.01 }};
integrity verification tools are employed to detect unauthorized changes to {{ insert: param, si-07_odp.02 }};
integrity verification tools are employed to detect unauthorized changes to {{ insert: param, si-07_odp.03 }};
{{ insert: param, si-07_odp.04 }} are taken when unauthorized changes to the software, are detected;
{{ insert: param, si-07_odp.05 }} are taken when unauthorized changes to the firmware are detected;
{{ insert: param, si-07_odp.06 }} are taken when unauthorized changes to the information are detected.
System and information integrity policy

system and information integrity procedures

procedures addressing software, firmware, and information integrity

personally identifiable information processing policy

system design documentation

system configuration settings and associated documentation

integrity verification tools and associated documentation

records generated or triggered by integrity verification tools regarding unauthorized software, firmware, and information changes

system audit records

system security plan

privacy plan

other relevant documents or records
Organizational personnel responsible for software, firmware, and/or information integrity

organizational personnel with information security and privacy responsibilities

system/network administrators
Software, firmware, and information integrity verification tools*

---

### Sample Match 25: `MAS-C.1.9` ⟷ `NIST-SI-16`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Dynamic Confidence: `0.85` | Dense Sim: `0.58`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0322 (Max Dense Sim: 0.58)
* **Defensible Rationale**:
```text
• MAS Requirement: must implement device binding to protect the software token from being cloned.
• NIST Control: NIST-SI-16 Memory Protection: Implement the following controls to protect the system memory from unauthorized code execution: {{ insert: param, si-16_odp }}..
• Gap Analysis: Covered: [Control B implements memory protection mechanisms (e.g., DEP, ASLR) that prevent unauthorized code execution, which is a technical prerequisite for securing the memory space where software tokens reside.], Missing: [Control B lacks specific mandates for device binding logic, cryptographic key storage tied to hardware identifiers, and anti-cloning measures specific to the token application layer.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SI-16 provides technical control capabilities addressing obligations in MAS-C.1.9.)
```

> **MAS TRM Clause [MAS-C.1.9]**:
> *The Financial Institution must implement device binding to protect the software token from being cloned.*

> **NIST SP 800-53 Control [NIST-SI-16 - Memory Protection]**:
> *Implement the following controls to protect the system memory from unauthorized code execution: {{ insert: param, si-16_odp }}.
Some adversaries launch attacks with the intent of executing code in non-executable regions of memory or in memory locations that are prohibited. Controls employed to protect memory include data execution prevention and address space layout randomization. Data execution prevention controls can either be hardware-enforced or software-enforced with hardware enforcement providing the greater strength of mechanism.
{{ insert: param, si-16_odp }} are implemented to protect the system memory from unauthorized code execution.
System and information integrity policy

system and information integrity procedures

procedures addressing memory protection for the system

system design documentation

system configuration settings and associated documentation

list of security safeguards protecting system memory from unauthorized code execution

system audit records

system security plan

other relevant documents or records
Organizational personnel responsible for memory protection

organizational personnel with information security responsibilities

system/network administrators

system developer
Automated mechanisms supporting and/or implementing safeguards to protect the system memory from unauthorized code execution*

---

## Section C: Reconciled Regulatory Gap Integrity Analysis

Total True Regulatory Gaps Identified: **4** (4.7%)

### Category A: Unmatched Obligations (0 Candidates Above Relevance Threshold)

*(None: All MAS obligations successfully retrieved candidate relationships from NIST SP 800-53)*

### Category B: Retail Consumer Mandates (Candidates Evaluated as NO_COVERAGE)

#### Regulatory Gap 1: `MAS-14.3.3.a`
> **MAS TRM Statement**:
> *The Financial Institution must notify customers of suspicious activities or funds transfers exceeding a threshold defined by the Financial Institution or the customers.*

* **Assurance Evaluation**: Candidates retrieved (NIST-AU-6, NIST-SI-4), but evaluated as `NO_COVERAGE`.
* **Audit Root Cause**: Direct external customer communication, advisory, or retail consumer protection requirement. NIST SP 800-53 Rev 5 governs federal information systems and has no consumer banking mandate.

---

#### Regulatory Gap 2: `MAS-14.3.3.b`
> **MAS TRM Statement**:
> *The Financial Institution must include meaningful information, such as transaction type and payment amount, along with instructions to report suspicious or unauthorized transactions, in customer notifications.*

* **Assurance Evaluation**: Candidates retrieved (NIST-SI-4), but evaluated as `NO_COVERAGE`.
* **Audit Root Cause**: Direct external customer communication, advisory, or retail consumer protection requirement. NIST SP 800-53 Rev 5 governs federal information systems and has no consumer banking mandate.

---

#### Regulatory Gap 3: `MAS-14.4.2`
> **MAS TRM Statement**:
> *The Financial Institution must alert customers on a timely basis to new cyber threats so they can take precautionary measures.*

* **Assurance Evaluation**: Candidates retrieved (NIST-RA-10, NIST-AT-2, NIST-CA-7, NIST-PM-16), but evaluated as `NO_COVERAGE`.
* **Audit Root Cause**: Direct external customer communication, advisory, or retail consumer protection requirement. NIST SP 800-53 Rev 5 governs federal information systems and has no consumer banking mandate.

---

#### Regulatory Gap 4: `MAS-14.4.3`
> **MAS TRM Statement**:
> *The Financial Institution must advise customers on means to detect unauthorized transactions and to report security issues, suspicious activities, or suspected fraud promptly.*

* **Assurance Evaluation**: Candidates retrieved (NIST-SI-4, NIST-SI-7), but evaluated as `NO_COVERAGE`.
* **Audit Root Cause**: Direct external customer communication, advisory, or retail consumer protection requirement. NIST SP 800-53 Rev 5 governs federal information systems and has no consumer banking mandate.

---

## Section D: 5 Sample MAS Obligations with Multiple Matches (1-to-N Mapping Clusters)

### Cluster 1: `MAS-1.3.a` maps to 14 NIST Controls

> **MAS TRM Statement [MAS-1.3.a]**:
> *The Financial Institution must evaluate its exposure to technology risks.*

#### Control 1: `NIST-RA-6` (Technical Surveillance Countermeasures Survey)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-RA-6 Technical Surveillance Countermeasures Survey: Employ a technical surveillance countermeasures survey at {{ insert: param, ra-06_odp.01 }} {{ insert: param, ra-06_odp.02 }}..
• Gap Analysis: Covered: [Control B provides specific physical and electronic detection of surveillance devices and identifies technical security weaknesses, which constitutes a component of technology risk evaluation.], Missing: [Control B is limited to physical security and counter-surveillance, failing to address the broad spectrum of technology risks such as software vulnerabilities, network architecture, data integrity, and operational continuity required by Requirement A.].
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
• Gap Analysis: Covered: [Control B mandates formal risk analysis and mitigation evaluation for information technology systems, which addresses the 'evaluate' component of technology risk exposure specifically within the context of personally identifiable information (PII) handling.], Missing: [Control B is restricted to privacy and PII-related risks, failing to cover the broader spectrum of technology risks such as operational continuity, cybersecurity, financial fraud, or general IT infrastructure vulnerabilities required by Requirement A.].
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
• Gap Analysis: Covered: [Control B mandates a comprehensive risk assessment process that explicitly identifies threats, vulnerabilities, likelihood, and impact of harm, directly fulfilling the mandate to evaluate technology risk exposure.], Missing: [None: Full coverage].
• Assurance Conclusion: FULL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Conduct a risk assessment, including:
Identifying threats to and vulnerabilities in the system;
Determining the likelihood and magnitude of harm from unauthorized access, use, disclosure, disruption, modification, or destruction of the system, the in...*

#### Control 4: `NIST-SR-6` (Supplier Assessments and Reviews)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-SR-6 Supplier Assessments and Reviews: Assess and review the supply chain-related risks associated with suppliers or contractors and the system, system component, or system service they provide {{ insert: param, sr-06_odp }}..
• Gap Analysis: Covered: [Control B mandates specific supplier and supply chain risk assessments, reviews, and policy documentation, which constitute a specific subset of technology risks.], Missing: [Requirement A requires evaluation of all technology risks (e.g., internal infrastructure, software vulnerabilities, operational failures), whereas Control B is strictly limited to supply chain and third-party supplier risks.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SR-6 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Assess and review the supply chain-related risks associated with suppliers or contractors and the system, system component, or system service they provide {{ insert: param, sr-06_odp }}.
An assessment and review of supplier risk includes security and...*

#### Control 5: `NIST-RA-5` (Vulnerability Monitoring and Scanning)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B implements technical vulnerability scanning, monitoring, and remediation processes which constitute a primary technical component of technology risk evaluation.], Missing: [Control B lacks the broader strategic risk assessment mandates, such as identifying non-technical risks, conducting enterprise-wide risk analysis, and defining risk tolerance, which are required by Requirement A.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;
Employ vulnerability monitoring tools and techniques...*

#### Control 6: `NIST-SR-2` (Supply Chain Risk Management Plan)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.85`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-SR-2 Supply Chain Risk Management Plan: Develop a plan for managing supply chain risks associated with the research and development, design, manufacturing, acquisition, delivery, integration, operations and maintenance, and disposal of the following systems, system components or system services: {{ insert: param, sr-02_odp.01 }};.
• Gap Analysis: Covered: [Control B mandates the development and maintenance of a Supply Chain Risk Management (SCRM) plan, which includes identifying and assessing specific supply chain risks across the system lifecycle.], Missing: [Requirement A requires a broad evaluation of all technology risks, whereas Control B is strictly limited to supply chain risks and does not address other technology risk domains such as internal system vulnerabilities, data privacy, or operational resilience.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SR-2 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Develop a plan for managing supply chain risks associated with the research and development, design, manufacturing, acquisition, delivery, integration, operations and maintenance, and disposal of the following systems, system components or system ser...*

#### Control 7: `NIST-PM-30` (Supply Chain Risk Management Strategy)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-PM-30 Supply Chain Risk Management Strategy: Develop an organization-wide strategy for managing supply chain risks associated with the development, acquisition, maintenance, and disposal of systems, system components, and system services;.
• Gap Analysis: Covered: [Control B mandates an organization-wide strategy and consistent implementation for managing supply chain risks across the full system lifecycle.], Missing: [Requirement A requires a general evaluation of all technology risks, whereas Control B is strictly limited to supply chain risks and does not address other technology risk domains.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-30 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Develop an organization-wide strategy for managing supply chain risks associated with the development, acquisition, maintenance, and disposal of systems, system components, and system services;
Implement the supply chain risk management strategy cons...*

#### Control 8: `NIST-CM-4` (Impact Analyses)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-CM-4 Impact Analyses: Analyze changes to the system to determine potential security and privacy impacts prior to change implementation..
• Gap Analysis: Covered: [Control B mandates pre-implementation impact analyses for system changes to identify specific security and privacy risks.], Missing: [Requirement A requires a comprehensive evaluation of overall technology risk exposure, whereas Control B is limited to analyzing risks arising from specific system changes.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-CM-4 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Analyze changes to the system to determine potential security and privacy impacts prior to change implementation.
Organizational personnel with security or privacy responsibilities conduct impact analyses. Individuals conducting impact analyses posse...*

#### Control 9: `NIST-SC-8` (Transmission Confidentiality and Integrity)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.80`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-SC-8 Transmission Confidentiality and Integrity: Protect the {{ insert: param, sc-08_odp }} of transmitted information..
• Gap Analysis: Covered: [Control B implements technical safeguards (encryption, physical protection) to ensure the confidentiality and integrity of data in transit.], Missing: [Requirement A mandates a broader organizational risk evaluation process, whereas Control B only addresses specific technical controls for data transmission without covering the assessment methodology.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SC-8 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Protect the {{ insert: param, sc-08_odp }} of transmitted information.
Protecting the confidentiality and integrity of transmitted information applies to internal and external networks as well as any system components that can transmit information, i...*

#### Control 10: `NIST-PM-4` (Plan of Action and Milestones Process)
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-PM-4 Plan of Action and Milestones Process: Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:.
• Gap Analysis: Covered: [Control B mandates the development and maintenance of Plans of Action and Milestones (POA&M) to document and track remedial actions for identified risks, including technology risks.], Missing: [Control B focuses on the remediation and tracking of known risks (POA&M) rather than the initial evaluation, identification, or assessment of technology risk exposure.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-4 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:
Are developed and maintained;
Document the remedial information ...*

#### Control 11: `NIST-PM-7` (Enterprise Architecture)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.80`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-PM-7 Enterprise Architecture: Develop and maintain an enterprise architecture with consideration for information security, privacy, and the resulting risk to organizational operations and assets, individuals, other organizations, and the Nation..
• Gap Analysis: Covered: [Control B mandates the development and maintenance of an enterprise architecture that explicitly integrates information security, privacy, and resulting risk considerations.], Missing: [Control B is limited to the enterprise architecture level and does not address technology risk exposure at the individual system, application, or specific technology asset level required by the broader mandate.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-7 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Develop and maintain an enterprise architecture with consideration for information security, privacy, and the resulting risk to organizational operations and assets, individuals, other organizations, and the Nation.
The integration of security and pr...*

#### Control 12: `NIST-SA-2` (Allocation of Resources)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-SA-2 Allocation of Resources: Determine the high-level information security and privacy requirements for the system or system service in mission and business process planning;.
• Gap Analysis: Covered: [Control B mandates the determination, documentation, and allocation of resources for information security and privacy within capital planning and budgeting processes.], Missing: [Control B focuses exclusively on resource allocation and budgeting, whereas Requirement A mandates a broader evaluation of technology risk exposure that includes identification and assessment beyond just financial planning.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SA-2 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Determine the high-level information security and privacy requirements for the system or system service in mission and business process planning;
Determine, document, and allocate the resources required to protect the system or system service as part...*

#### Control 13: `NIST-SI-19` (De-identification)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-SI-19 De-identification: Remove the following elements of personally identifiable information from datasets: {{ insert: param, si-19_odp.01 }} ; and.
• Gap Analysis: Covered: [Control B mandates the evaluation of de-identification effectiveness, which addresses a specific subset of technology risks related to data privacy and Personally Identifiable Information (PII).], Missing: [Requirement A mandates a comprehensive evaluation of all technology risks, whereas Control B is strictly limited to PII de-identification and does not cover other critical technology risk domains such as infrastructure, software, or network security.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SI-19 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Remove the following elements of personally identifiable information from datasets: {{ insert: param, si-19_odp.01 }} ; and
Evaluate {{ insert: param, si-19_odp.02 }} for effectiveness of de-identification.
De-identification is the general term for t...*

#### Control 14: `NIST-PT-4` (Consent)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-PT-4 Consent: Implement {{ insert: param, pt-04_odp }} for individuals to consent to the processing of their personally identifiable information prior to its collection that facilitate individuals’ informed decision-making..
• Gap Analysis: Covered: [Control B addresses technology risk exposure specifically regarding privacy and Personally Identifiable Information (PII) processing by implementing consent mechanisms.], Missing: [Requirement A mandates a comprehensive evaluation of all technology risks, whereas Control B is strictly limited to privacy/PII consent and does not address other technology risk domains such as infrastructure, application security, or operational resilience.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PT-4 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *Implement {{ insert: param, pt-04_odp }} for individuals to consent to the processing of their personally identifiable information prior to its collection that facilitate individuals’ informed decision-making.
Consent allows individuals to participat...*

---

### Cluster 2: `MAS-1.3.b` maps to 15 NIST Controls

> **MAS TRM Statement [MAS-1.3.b]**:
> *The Financial Institution must implement a robust risk management framework to ensure IT and cyber resilience.*

#### Control 1: `NIST-PM-9` (Risk Management Strategy)
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Dyn Conf: `0.86`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-PM-9 Risk Management Strategy: Develops a comprehensive strategy to manage:.
• Gap Analysis: Covered: [Control B mandates the development, organization-wide implementation, and periodic review of a comprehensive risk management strategy that explicitly addresses security and privacy risks to operations, assets, and individuals.], Missing: [None: Full coverage].
• Assurance Conclusion: FULL_COVERAGE (NIST-PM-9 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *Develops a comprehensive strategy to manage:
Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and
Privacy risk to individuals resu...*

#### Control 2: `NIST-SA-24` (Design For Cyber Resiliency)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.88`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-SA-24 Design For Cyber Resiliency: Design organizational systems, system components, or system services to achieve cyber resiliency by:.
• Gap Analysis: Covered: [Control B mandates the design and implementation of specific cyber resiliency goals, objectives, techniques, and principles within the system engineering and acquisition lifecycle.], Missing: [Control B is limited to the design and engineering phase of cyber resiliency, whereas Requirement A demands a comprehensive, organization-wide risk management framework that includes governance, policy, and broader operational resilience beyond system design.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SA-24 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *Design organizational systems, system components, or system services to achieve cyber resiliency by:
Defining the following cyber resiliency goals: {{ insert: param, sa-24_odp.01 }}.
Defining the following cyber resiliency objectives: {{ insert: para...*

#### Control 3: `NIST-PM-4` (Plan of Action and Milestones Process)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.85`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-PM-4 Plan of Action and Milestones Process: Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:.
• Gap Analysis: Covered: [Control B mandates the development, maintenance, and reporting of Plans of Action and Milestones (POA&M) to track and remediate specific security, privacy, and supply chain risks.], Missing: [Control B lacks the mandate for a holistic risk management framework, focusing only on the remediation tracking mechanism (POA&M) rather than the broader governance, strategy, and continuous monitoring components required for IT and cyber resilience.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-4 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:
Are developed and maintained;
Document the remedial information ...*

#### Control 4: `NIST-PM-7` (Enterprise Architecture)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.85`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-PM-7 Enterprise Architecture: Develop and maintain an enterprise architecture with consideration for information security, privacy, and the resulting risk to organizational operations and assets, individuals, other organizations, and the Nation..
• Gap Analysis: Covered: [Control B mandates the development and maintenance of an enterprise architecture that explicitly integrates information security, privacy, and risk considerations, thereby providing the structural foundation for a risk management framework.], Missing: [Control B focuses on architectural design and integration but lacks mandates for operational risk management processes, incident response, business continuity, and the broader governance policies required for a complete 'robust risk management framework' and 'cyber resilience'.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-7 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *Develop and maintain an enterprise architecture with consideration for information security, privacy, and the resulting risk to organizational operations and assets, individuals, other organizations, and the Nation.
The integration of security and pr...*

#### Control 5: `NIST-CP-2` (Contingency Plan)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-CP-2 Contingency Plan: Develop a contingency plan for the system that:.
• Gap Analysis: Covered: [Control B mandates the development, approval, and maintenance of a specific Contingency Plan addressing system restoration, recovery objectives, and roles.], Missing: [Requirement A requires a comprehensive 'robust risk management framework' covering all IT and cyber resilience aspects, whereas Control B is limited to contingency planning and does not address risk assessment, governance, or broader resilience strategies.].
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
• Gap Analysis: Covered: [Control B mandates the execution, documentation, review, and dissemination of risk assessments to identify threats, vulnerabilities, and impacts.], Missing: [Control B lacks requirements for the implementation of specific risk mitigation controls, continuous monitoring, governance structures, and resilience strategies beyond the assessment phase.].
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
• Gap Analysis: Covered: [Control B mandates the development, maintenance, execution, and strategic alignment of testing, training, and monitoring plans, which are core operational components of a risk management framework.], Missing: [Control B lacks mandates for the overarching governance structure, risk identification, assessment methodologies, and continuous improvement cycles required by a robust risk management framework.].
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
• Gap Analysis: Covered: [Control B mandates a structured criticality analysis and functional decomposition to identify mission-critical system components and dependencies.], Missing: [Control B lacks requirements for the broader risk management framework, ongoing risk assessment, mitigation strategies, and governance structures necessary for comprehensive IT and cyber resilience.].
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
• Gap Analysis: Covered: [Control B establishes the governance structure and leadership roles required to oversee risk management.], Missing: [Control B lacks the mandate to implement the actual technical and operational risk management framework and resilience measures.].
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
• Gap Analysis: Covered: [Control B implements specific technical mechanisms for vulnerability scanning, analysis, remediation, and information sharing to identify and address system weaknesses.], Missing: [Control B lacks the broader governance, policy, and strategic framework components required to constitute a comprehensive risk management framework.].
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
• Gap Analysis: Covered: [Control B mandates the operational response to specific assessment findings based on risk tolerance, which is a component of a broader risk management framework.], Missing: [Control B lacks mandates for the overarching framework structure, proactive risk identification, governance, and continuous resilience monitoring required by Requirement A.].
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
• Gap Analysis: Covered: [Control B mandates the development, documentation, and integration of security and privacy architectures, which form the structural foundation of a risk management framework.], Missing: [Control B lacks mandates for operational risk management processes, continuous monitoring, incident response, and governance structures required for a comprehensive risk management framework.].
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
• Gap Analysis: Covered: [Control B implements specific alternate communications protocols and contingency training to support continuity of operations.], Missing: [Control B lacks the broader mandate for a comprehensive risk management framework, covering only the specific domain of communications resilience rather than overall IT and cyber resilience.].
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
• Gap Analysis: Covered: [Control B mandates technical encryption and physical protection mechanisms to secure data in transit, which is a specific technical component of the broader risk management framework required by A.], Missing: [Control B lacks mandates for the overarching governance structure, risk assessment methodologies, incident response planning, and holistic resilience strategies required by the risk management framework in A.].
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
• Gap Analysis: Covered: [Control B mandates the integration of security and privacy risk management processes into the System Development Life Cycle (SDLC), including role definition and personnel identification.], Missing: [Requirement A demands a comprehensive, organization-wide risk management framework for IT and cyber resilience, whereas Control B is limited to the SDLC acquisition and development phase.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SA-3 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *Acquire, develop, and manage the system using {{ insert: param, sa-03_odp }} that incorporates information security and privacy considerations;
Define and document information security and privacy roles and responsibilities throughout the system deve...*

---

### Cluster 3: `MAS-1.4(a).1` maps to 13 NIST Controls

> **MAS TRM Statement [MAS-1.4(a).1]**:
> *The Board of Directors and Senior Management must cultivate a strong risk culture.*

#### Control 1: `NIST-PM-29` (Risk Management Program Leadership Roles)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.86`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-PM-29 Risk Management Program Leadership Roles: Appoint a Senior Accountable Official for Risk Management to align organizational information security and privacy management processes with strategic, operational, and budgetary planning processes; and.
• Gap Analysis: Covered: [Control B mandates the appointment of specific risk leadership roles and aligns risk management with strategic planning, providing a structural foundation for risk culture.], Missing: [Control B lacks explicit mandates for Board/Senior Management to actively cultivate behavioral norms, values, and communication channels that define 'risk culture' beyond administrative alignment.].
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
• Gap Analysis: Covered: [Control B mandates the development, implementation, and review of a formal, documented risk management strategy aligned with strategic and budgetary planning, which operationalizes the risk culture through structured governance.], Missing: [Control B focuses on technical and procedural strategy artifacts but lacks explicit mandates for the behavioral, cultural, and leadership-driven cultivation of risk awareness and values required by Requirement A.].
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
• Gap Analysis: Covered: [Control B mandates the appointment of a senior official with authority and resources to coordinate and manage privacy risks, establishing a governance structure that supports risk culture.], Missing: [Requirement A mandates a broad organizational risk culture cultivated by the Board and Senior Management, whereas Control B is limited to a specific privacy leadership role and does not address general risk culture or board-level oversight.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-19 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Appoint a senior agency official for privacy with the authority, mission, accountability, and resources to coordinate, develop, and implement, applicable privacy requirements and manage privacy risks through the organization-wide privacy program.
The...*

#### Control 4: `NIST-CA-6` (Authorization)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-CA-6 Authorization: Assign a senior official as the authorizing official for the system;.
• Gap Analysis: Covered: [Control B mandates senior management accountability and risk acceptance through formal authorization decisions and continuous monitoring.], Missing: [Control B lacks specific mandates for cultivating a pervasive risk culture, such as training, communication, and behavioral norms.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-CA-6 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Assign a senior official as the authorizing official for the system;
Assign a senior official as the authorizing official for common controls available for inheritance by organizational systems;
Ensure that the authorizing official for the system, be...*

#### Control 5: `NIST-PM-2` (Information Security Program Leadership Role)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.81`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-PM-2 Information Security Program Leadership Role: Appoint a senior agency information security officer with the mission and resources to coordinate, develop, implement, and maintain an organization-wide information security program..
• Gap Analysis: Covered: [Control B mandates the appointment of a senior information security officer with resources to coordinate and maintain an organization-wide information security program.], Missing: [Control B lacks specific mandates for the Board of Directors' active role, the cultivation of a broad organizational risk culture, and the integration of non-information security risks.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-2 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Appoint a senior agency information security officer with the mission and resources to coordinate, develop, implement, and maintain an organization-wide information security program.
The senior agency information security officer is an organizational...*

#### Control 6: `NIST-PM-28` (Risk Framing)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-PM-28 Risk Framing: Identify and document:.
• Gap Analysis: Covered: [Control B mandates the formal identification, documentation, and distribution of risk framing elements (assumptions, constraints, priorities, trade-offs, and tolerance) to stakeholders.], Missing: [Control B lacks explicit mandates for the Board and Senior Management to actively cultivate a 'strong risk culture' through behavioral leadership, tone-at-the-top, and ongoing cultural reinforcement beyond the technical risk framing process.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-28 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Identify and document:
Assumptions affecting risk assessments, risk responses, and risk monitoring;
Constraints affecting risk assessments, risk responses, and risk monitoring;
Priorities and trade-offs considered by the organization for managing ris...*

#### Control 7: `NIST-SA-3` (System Development Life Cycle)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-SA-3 System Development Life Cycle: Acquire, develop, and manage the system using {{ insert: param, sa-03_odp }} that incorporates information security and privacy considerations;.
• Gap Analysis: Covered: [Control B mandates the integration of security and privacy risk management processes into the System Development Life Cycle (SDLC) and defines specific roles, which operationalizes a component of risk culture.], Missing: [Requirement A mandates a broad organizational risk culture cultivated by the Board and Senior Management, whereas Control B is a technical/operational control focused solely on the SDLC process and does not address enterprise-wide cultural cultivation or Board-level governance.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SA-3 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Acquire, develop, and manage the system using {{ insert: param, sa-03_odp }} that incorporates information security and privacy considerations;
Define and document information security and privacy roles and responsibilities throughout the system deve...*

#### Control 8: `NIST-PM-4` (Plan of Action and Milestones Process)
- **Semantic Relation**: `SUPPORTS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-PM-4 Plan of Action and Milestones Process: Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:.
• Gap Analysis: Covered: [Control B establishes formal governance processes for documenting, maintaining, and reporting remedial actions, which provides the structural framework and accountability necessary for management to demonstrate oversight of risk.], Missing: [Control B focuses on procedural compliance and documentation of specific remediation plans, whereas Requirement A mandates the broader cultural cultivation of risk awareness and values by leadership, which is not addressed by administrative processes alone.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-4 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:
Are developed and maintained;
Document the remedial information ...*

#### Control 9: `NIST-PM-30` (Supply Chain Risk Management Strategy)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-PM-30 Supply Chain Risk Management Strategy: Develop an organization-wide strategy for managing supply chain risks associated with the development, acquisition, maintenance, and disposal of systems, system components, and system services;.
• Gap Analysis: Covered: [Control B mandates the development and implementation of an organization-wide strategy with defined risk appetite and roles, which serves as a specific operational component of the broader risk culture required by Requirement A.], Missing: [Control B lacks mandates for the cultural cultivation aspects of Requirement A, such as leadership tone, behavioral norms, training, and the general fostering of risk awareness across the entire organization beyond supply chain specifics.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-30 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Develop an organization-wide strategy for managing supply chain risks associated with the development, acquisition, maintenance, and disposal of systems, system components, and system services;
Implement the supply chain risk management strategy cons...*

#### Control 10: `NIST-PM-14` (Testing, Training, and Monitoring)
- **Semantic Relation**: `SUPPORTS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-PM-14 Testing, Training, and Monitoring: Implement a process for ensuring that organizational plans for conducting security and privacy testing, training, and monitoring activities associated with organizational systems:.
• Gap Analysis: Covered: [Control B mandates the development, maintenance, and execution of security and privacy testing, training, and monitoring plans, which are the primary operational mechanisms for cultivating and demonstrating a risk culture.], Missing: [Control B focuses on procedural execution and plan consistency rather than the Board's direct mandate to cultivate the overarching cultural environment, tone at the top, and behavioral norms required by Requirement A.].
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
• Gap Analysis: Covered: [Control B implements specific insider threat detection, monitoring, and incident response mechanisms that operationalize aspects of a risk-aware culture.], Missing: [Control B lacks mandates for broad cultural cultivation, leadership tone-at-the-top, and general risk governance beyond the specific scope of insider threats.].
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
• Gap Analysis: Covered: [Control B implements specific personnel security mechanisms (position risk designation and screening) that operationalize the 'suitability' and 'integrity' aspects of a risk culture.], Missing: [Control B lacks mandates for Board/Senior Management governance, cultural tone-setting, behavioral expectations, and broader risk awareness training required by Requirement A.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PS-2 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Assign a risk designation to all organizational positions;
Establish screening criteria for individuals filling those positions; and
Review and update position risk designations {{ insert: param, ps-02_odp }}.
Position risk designations reflect Offic...*

#### Control 13: `NIST-PM-31` (Continuous Monitoring Strategy)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must cultivate a strong risk culture.
• NIST Control: NIST-PM-31 Continuous Monitoring Strategy: Develop an organization-wide continuous monitoring strategy and implement continuous monitoring programs that include:.
• Gap Analysis: Covered: [Control B provides the technical infrastructure and reporting mechanisms (metrics, dashboards, response actions) that enable the monitoring and decision-making required to support a risk-aware culture.], Missing: [Control B lacks mandates for cultural cultivation, behavioral norms, leadership tone, and organizational values, focusing instead on technical monitoring and reporting.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-31 provides technical control capabilities addressing obligations in MAS-1.4(a).1.)
```
> *Develop an organization-wide continuous monitoring strategy and implement continuous monitoring programs that include:
Establishing the following organization-wide metrics to be monitored: {{ insert: param, pm-31_odp.01 }};
Establishing {{ insert: pa...*

---

### Cluster 4: `MAS-1.4(a).2` maps to 12 NIST Controls

> **MAS TRM Statement [MAS-1.4(a).2]**:
> *The Board of Directors and Senior Management must establish a sound and robust technology risk management framework.*

#### Control 1: `NIST-PM-29` (Risk Management Program Leadership Roles)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.85`)
- **Rationale**:
```text
• MAS Requirement: must establish a sound and robust technology risk management framework.
• NIST Control: NIST-PM-29 Risk Management Program Leadership Roles: Appoint a Senior Accountable Official for Risk Management to align organizational information security and privacy management processes with strategic, operational, and budgetary planning processes; and.
• Gap Analysis: Covered: [Control B mandates the appointment of specific leadership roles (Senior Accountable Official, Risk Executive) and aligns risk management with strategic planning, which constitutes the governance layer of a risk framework.], Missing: [Control B lacks mandates for the comprehensive structural components of the framework, such as risk identification, assessment methodologies, mitigation strategies, monitoring, and reporting mechanisms.].
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
• Gap Analysis: Covered: [Control B mandates the development, implementation, and maintenance of a comprehensive, organization-wide risk management strategy that explicitly addresses security and privacy risks, aligns with strategic planning, and is overseen by senior accountable officials.], Missing: [None: Full coverage].
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
• Gap Analysis: Covered: [Control B mandates the development, maintenance, and protection of a specific Supply Chain Risk Management (SCRM) plan, addressing governance and risk identification within the supply chain lifecycle.], Missing: [Requirement A mandates a comprehensive technology risk management framework covering all risk domains (e.g., operational, strategic, compliance, cyber), whereas Control B is strictly limited to supply chain risks.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SR-2 provides technical control capabilities addressing obligations in MAS-1.4(a).2.)
```
> *Develop a plan for managing supply chain risks associated with the research and development, design, manufacturing, acquisition, delivery, integration, operations and maintenance, and disposal of the following systems, system components or system ser...*

#### Control 4: `NIST-PM-23` (Data Governance Body)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must establish a sound and robust technology risk management framework.
• NIST Control: NIST-PM-23 Data Governance Body: Establish a Data Governance Body consisting of {{ insert: param, pm-23_odp.01 }} with {{ insert: param, pm-23_odp.02 }}..
• Gap Analysis: Covered: [Establishment of a Data Governance Body with specific executive roles (CIO, Security Officer, Privacy Official) to create policies and standards for data management.], Missing: [Control B is strictly limited to data governance and privacy, whereas Requirement A mandates a comprehensive technology risk management framework covering all IT assets, infrastructure, and broader risk management processes.].
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
• Gap Analysis: Covered: [Control B mandates the development and maintenance of an enterprise architecture that explicitly integrates security, privacy, and risk considerations, providing a structural framework for risk management.], Missing: [Control B lacks mandates for the establishment of the overarching governance structure, the specific composition of the Board/Senior Management, and the general 'sound and robust' operational framework required by Requirement A.].
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
• Gap Analysis: Covered: [Control B mandates the technical execution of risk assessments, including identifying threats, determining likelihood/impact, and documenting results.], Missing: [Control B lacks the governance mandate for the Board and Senior Management to establish the overarching technology risk management framework.].
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
• Gap Analysis: Covered: [Control B mandates the identification, documentation, and distribution of specific risk framing inputs (assumptions, constraints, priorities, trade-offs, and tolerance) which constitute the foundational strategy layer of a risk management framework.], Missing: [Control B lacks mandates for the establishment of the overarching governance structure, the definition of the framework's scope and architecture, and the ongoing operational management of the technology risk program by the Board and Senior Management.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-28 provides technical control capabilities addressing obligations in MAS-1.4(a).2.)
```
> *Identify and document:
Assumptions affecting risk assessments, risk responses, and risk monitoring;
Constraints affecting risk assessments, risk responses, and risk monitoring;
Priorities and trade-offs considered by the organization for managing ris...*

#### Control 8: `NIST-PM-31` (Continuous Monitoring Strategy)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must establish a sound and robust technology risk management framework.
• NIST Control: NIST-PM-31 Continuous Monitoring Strategy: Develop an organization-wide continuous monitoring strategy and implement continuous monitoring programs that include:.
• Gap Analysis: Covered: [Control B implements specific continuous monitoring programs, metrics, and reporting mechanisms that serve as operational components of a broader risk management framework.], Missing: [Control B lacks mandates for the overarching governance structure, policy establishment, and strategic framework design required by Requirement A, focusing instead on execution and monitoring.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-31 provides technical control capabilities addressing obligations in MAS-1.4(a).2.)
```
> *Develop an organization-wide continuous monitoring strategy and implement continuous monitoring programs that include:
Establishing the following organization-wide metrics to be monitored: {{ insert: param, pm-31_odp.01 }};
Establishing {{ insert: pa...*

#### Control 9: `NIST-PM-4` (Plan of Action and Milestones Process)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must establish a sound and robust technology risk management framework.
• NIST Control: NIST-PM-4 Plan of Action and Milestones Process: Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:.
• Gap Analysis: Covered: [Control B mandates the development, maintenance, and reporting of Plans of Action and Milestones (POA&M) to track remedial actions, which serves as a specific operational component of a broader risk management framework.], Missing: [Control B lacks mandates for the overarching establishment of the governance structure, strategic risk appetite, and holistic framework architecture required by Requirement A.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-4 provides technical control capabilities addressing obligations in MAS-1.4(a).2.)
```
> *Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:
Are developed and maintained;
Document the remedial information ...*

#### Control 10: `NIST-PM-1` (Information Security Program Plan)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must establish a sound and robust technology risk management framework.
• NIST Control: NIST-PM-1 Information Security Program Plan: Develop and disseminate an organization-wide information security program plan that:.
• Gap Analysis: Covered: [Control B mandates the development, dissemination, and senior official approval of an organization-wide Information Security Program Plan that explicitly defines roles, responsibilities, management commitment, and coordination, thereby establishing the required framework.], Missing: [None: Full coverage].
• Assurance Conclusion: FULL_COVERAGE (NIST-PM-1 provides technical control capabilities addressing obligations in MAS-1.4(a).2.)
```
> *Develop and disseminate an organization-wide information security program plan that:
Provides an overview of the requirements for the security program and a description of the security program management controls and common controls in place or plann...*

#### Control 11: `NIST-PM-14` (Testing, Training, and Monitoring)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must establish a sound and robust technology risk management framework.
• NIST Control: NIST-PM-14 Testing, Training, and Monitoring: Implement a process for ensuring that organizational plans for conducting security and privacy testing, training, and monitoring activities associated with organizational systems:.
• Gap Analysis: Covered: [Control B mandates the development, maintenance, execution, and strategic alignment of specific testing, training, and monitoring plans.], Missing: [Requirement A mandates the establishment of the overarching technology risk management framework itself, whereas Control B only addresses specific operational activities within that framework.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-14 provides technical control capabilities addressing obligations in MAS-1.4(a).2.)
```
> *Implement a process for ensuring that organizational plans for conducting security and privacy testing, training, and monitoring activities associated with organizational systems:
Are developed and maintained; and
Continue to be executed; and
Review ...*

#### Control 12: `NIST-SR-3` (Supply Chain Controls and Processes)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must establish a sound and robust technology risk management framework.
• NIST Control: NIST-SR-3 Supply Chain Controls and Processes: Establish a process or processes to identify and address weaknesses or deficiencies in the supply chain elements and processes of {{ insert: param, sr-03_odp.01 }} in coordination with {{ insert: param, sr-03_odp.02 }};.
• Gap Analysis: Covered: [Control B mandates specific supply chain risk management processes, including identifying deficiencies, coordinating with personnel, employing protective controls, and documenting these activities.], Missing: [Control B is limited to supply chain risks, whereas Requirement A mandates a comprehensive technology risk management framework covering all technology domains (e.g., infrastructure, software, data, personnel) beyond just supply chain.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SR-3 provides technical control capabilities addressing obligations in MAS-1.4(a).2.)
```
> *Establish a process or processes to identify and address weaknesses or deficiencies in the supply chain elements and processes of {{ insert: param, sr-03_odp.01 }} in coordination with {{ insert: param, sr-03_odp.02 }};
Employ the following controls ...*

---

### Cluster 5: `MAS-1.4(b).1` maps to 15 NIST Controls

> **MAS TRM Statement [MAS-1.4(b).1]**:
> *The Financial Institution must adopt a defence-in-depth approach to strengthen cyber resilience.*

#### Control 1: `NIST-SA-24` (Design For Cyber Resiliency)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-SA-24 Design For Cyber Resiliency: Design organizational systems, system components, or system services to achieve cyber resiliency by:.
• Gap Analysis: Covered: [Control B mandates the definition and implementation of specific cyber resiliency goals, objectives, techniques, approaches, and design principles within the system engineering and risk management processes.], Missing: [Control B lacks the explicit mandate for a 'defence-in-depth' strategy, focusing instead on general cyber resiliency engineering rather than the specific layered security architecture required by Requirement A.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SA-24 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
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
• Gap Analysis: Covered: [Control B implements an active, proactive threat hunting capability to detect and disrupt advanced threats that evade existing controls.], Missing: [Control B lacks mandates for the foundational defensive layers (e.g., firewalls, access controls, segmentation) and the overarching architectural strategy required for a complete defense-in-depth approach.].
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
• Gap Analysis: Covered: [Control B mandates the development, documentation, and integration of security and privacy architectures, which serve as the structural foundation for a defense-in-depth strategy.], Missing: [Control B focuses on architectural design and documentation rather than the implementation of specific technical controls, policies, or operational procedures required to execute the defense-in-depth approach.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PL-8 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *Develop security and privacy architectures for the system that:
Describe the requirements and approach to be taken for protecting the confidentiality, integrity, and availability of organizational information;
Describe the requirements and approach t...*

#### Control 4: `NIST-CP-2` (Contingency Plan)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-CP-2 Contingency Plan: Develop a contingency plan for the system that:.
• Gap Analysis: Covered: [Control B mandates the development of a contingency plan that ensures system restoration and operational continuity following a disruption, which is a specific component of the broader cyber resilience strategy.], Missing: [Requirement A mandates a comprehensive 'defence-in-depth' strategy encompassing prevention, detection, and response controls, whereas Control B is strictly limited to post-incident recovery and continuity planning.].
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
• Gap Analysis: Covered: [Control B mandates the implementation and testing of alternate communications protocols to ensure continuity of operations.], Missing: [Control B is limited to communications continuity and does not address the broader defense-in-depth requirements such as network segmentation, endpoint protection, access controls, or monitoring.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-CP-11 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *Provide the capability to employ {{ insert: param, cp-11_odp }} in support of maintaining continuity of operations.
Contingency plans and the contingency training or testing associated with those plans incorporate an alternate communications protocol...*

#### Control 6: `NIST-IR-8` (Incident Response Plan)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-IR-8 Incident Response Plan: Develop an incident response plan that:.
• Gap Analysis: Covered: [Control B establishes a formalized incident response capability and governance structure, which serves as a critical component of the overall cyber resilience strategy.], Missing: [Control B lacks mandates for proactive defense-in-depth architectural controls, such as network segmentation, access controls, encryption, and continuous monitoring, which are required to strengthen overall cyber resilience.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-IR-8 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *Develop an incident response plan that:
Provides the organization with a roadmap for implementing its incident response capability;
Describes the structure and organization of the incident response capability;
Provides a high-level approach for how t...*

#### Control 7: `NIST-PM-4` (Plan of Action and Milestones Process)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.81`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-PM-4 Plan of Action and Milestones Process: Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:.
• Gap Analysis: Covered: [Control B mandates the development, maintenance, and reporting of Plans of Action and Milestones (POA&M) to track and remediate identified security risks.], Missing: [Control B lacks mandates for the proactive architectural design, layered technical controls, and defense-in-depth strategy required by Requirement A, focusing only on reactive remediation tracking.].
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
• Gap Analysis: Covered: [Control B implements specific deception and tainting mechanisms to detect data exfiltration.], Missing: [Requirement A mandates a comprehensive defense-in-depth strategy (multiple layers of security controls), whereas Control B only addresses post-breach detection via deception.].
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
• Gap Analysis: Covered: [Control B mandates the development of comprehensive security and privacy plans that define system components, operational context, threats, and specific controls, which serves as the foundational documentation for a defense-in-depth strategy.], Missing: [Control B is a planning and documentation control that lacks the technical implementation mandates, specific layered control selection, and active defense mechanisms required to fully satisfy the operational 'defense-in-depth' requirement.].
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
• Gap Analysis: Covered: [Control B mandates the identification of critical system components and functions through criticality analysis and functional decomposition, which serves as the foundational input for prioritizing and implementing specific defense-in-depth protections.], Missing: [Control B lacks mandates for the actual implementation of layered security controls, architectural redundancy, alternate paths, or the specific technical mechanisms required to enforce the defense-in-depth strategy.].
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
• Gap Analysis: Covered: [Control B mandates the development and implementation of a comprehensive, organization-wide risk management strategy that includes security risk mitigation strategies and risk tolerance expressions.], Missing: [Control B lacks specific technical mandates for defense-in-depth architecture (e.g., layered controls, segmentation, redundancy) and focuses on governance rather than the technical resilience mechanisms required by Requirement A.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-PM-9 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *Develops a comprehensive strategy to manage:
Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and
Privacy risk to individuals resu...*

#### Control 12: `NIST-RA-5` (Vulnerability Monitoring and Scanning)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.80`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates specific technical processes for vulnerability monitoring, scanning, analysis, and remediation, which constitute a critical layer of the defense-in-depth strategy.], Missing: [Control B is limited to vulnerability management and does not address other essential defense-in-depth layers such as network segmentation, access control, encryption, or physical security.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;
Employ vulnerability monitoring tools and techniques...*

#### Control 13: `NIST-RA-7` (Risk Response)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.81`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-RA-7 Risk Response: Respond to findings from security and privacy assessments, monitoring, and audits in accordance with organizational risk tolerance..
• Gap Analysis: Covered: [Control B mandates the procedural response to identified risks (mitigation, acceptance, etc.) based on risk tolerance, which is a component of defense-in-depth.], Missing: [Control B lacks the explicit mandate for a layered, multi-tiered architectural strategy (defense-in-depth) and focuses on reactive risk treatment rather than proactive structural resilience design.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-7 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *Respond to findings from security and privacy assessments, monitoring, and audits in accordance with organizational risk tolerance.
Organizations have many options for responding to risk including mitigating risk by implementing new controls or stren...*

#### Control 14: `NIST-IR-9` (Information Spillage Response)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.80`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-IR-9 Information Spillage Response: Respond to information spills by:.
• Gap Analysis: Covered: [Control B mandates specific technical and procedural steps for isolating, eradicating, and communicating about information spills, which constitutes a single layer of defense within a broader strategy.], Missing: [Requirement A mandates a comprehensive 'defence-in-depth' strategy encompassing prevention, detection, and multiple control layers, whereas Control B only addresses the reactive response to a specific type of data contamination.].
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
• Gap Analysis: Covered: [Control B mandates the development and implementation of a continuous monitoring strategy, including metric establishment, ongoing assessments, correlation/analysis, and response actions.], Missing: [Control B lacks the explicit mandate for a 'defence-in-depth' architectural strategy, focusing instead on the operational monitoring of existing controls rather than the multi-layered design of the security infrastructure itself.].
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
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-RA-6 Technical Surveillance Countermeasures Survey: Employ a technical surveillance countermeasures survey at {{ insert: param, ra-06_odp.01 }} {{ insert: param, ra-06_odp.02 }}..
• Gap Analysis: Covered: [Control B provides specific physical and electronic detection of surveillance devices and identifies technical security weaknesses, which constitutes a component of technology risk evaluation.], Missing: [Control B is limited to physical security and counter-surveillance, failing to address the broad spectrum of technology risks such as software vulnerabilities, network architecture, data integrity, and operational continuity required by Requirement A.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-6 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *The Financial Institution must evaluate its exposure to technology risks.*

#### MAS Clause 2: `MAS-15.1.2.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must identify a comprehensive set of auditable areas for technology risk to enable effective risk assessment during audit planning.
• NIST Control: NIST-RA-6 Technical Surveillance Countermeasures Survey: Employ a technical surveillance countermeasures survey at {{ insert: param, ra-06_odp.01 }} {{ insert: param, ra-06_odp.02 }}..
• Gap Analysis: Covered: [Control B provides specific technical surveillance countermeasures (TSCM) surveys that identify physical and electronic security weaknesses, offering input for risk assessments.], Missing: [Requirement A mandates a comprehensive identification of all auditable technology risk areas, whereas Control B is limited to physical/electronic surveillance and does not address broader IT infrastructure, software, or data security audit scopes.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-6 provides technical control capabilities addressing obligations in MAS-15.1.2.a.)
```
> *The Financial Institution must identify a comprehensive set of auditable areas for technology risk to enable effective risk assessment during audit planning.*

---

### Cluster 2: `NIST-RA-8` (Privacy Impact Assessments) addresses 3 MAS Obligations

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
• Gap Analysis: Covered: [Control B mandates formal risk analysis and mitigation evaluation for information technology systems, which addresses the 'evaluate' component of technology risk exposure specifically within the context of personally identifiable information (PII) handling.], Missing: [Control B is restricted to privacy and PII-related risks, failing to cover the broader spectrum of technology risks such as operational continuity, cybersecurity, financial fraud, or general IT infrastructure vulnerabilities required by Requirement A.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-8 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *The Financial Institution must evaluate its exposure to technology risks.*

#### MAS Clause 2: `MAS-13.6.1.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must perform severity assessment and classification of an issue.
• NIST Control: NIST-RA-8 Privacy Impact Assessments: Conduct privacy impact assessments for systems, programs, or other activities before:.
• Gap Analysis: Covered: [Control B mandates a formal analysis to determine and document privacy risks associated with Personally Identifiable Information (PII) handling.], Missing: [Requirement A mandates a general severity assessment and classification for all issues, whereas Control B is strictly limited to privacy risks and PII handling, lacking general severity classification mechanisms.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-8 provides technical control capabilities addressing obligations in MAS-13.6.1.a.)
```
> *The Financial Institution must perform severity assessment and classification of an issue.*

#### MAS Clause 3: `MAS-15.1.2.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must identify a comprehensive set of auditable areas for technology risk to enable effective risk assessment during audit planning.
• NIST Control: NIST-RA-8 Privacy Impact Assessments: Conduct privacy impact assessments for systems, programs, or other activities before:.
• Gap Analysis: Covered: [Control B mandates the identification of auditable areas specifically for privacy risks and Personally Identifiable Information (PII) handling through Privacy Impact Assessments (PIAs).], Missing: [Requirement A mandates a comprehensive set of auditable areas for all technology risks, whereas Control B is strictly limited to privacy and PII-related risks, excluding other technology risk domains.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-8 provides technical control capabilities addressing obligations in MAS-15.1.2.a.)
```
> *The Financial Institution must identify a comprehensive set of auditable areas for technology risk to enable effective risk assessment during audit planning.*

---

### Cluster 3: `NIST-RA-3` (Risk Assessment) addresses 16 MAS Obligations

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
• Gap Analysis: Covered: [Control B mandates a comprehensive risk assessment process that explicitly identifies threats, vulnerabilities, likelihood, and impact of harm, directly fulfilling the mandate to evaluate technology risk exposure.], Missing: [None: Full coverage].
• Assurance Conclusion: FULL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *The Financial Institution must evaluate its exposure to technology risks.*

#### MAS Clause 2: `MAS-1.3.b`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.85`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Control B mandates the execution, documentation, review, and dissemination of risk assessments to identify threats, vulnerabilities, and impacts.], Missing: [Control B lacks requirements for the implementation of specific risk mitigation controls, continuous monitoring, governance structures, and resilience strategies beyond the assessment phase.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *The Financial Institution must implement a robust risk management framework to ensure IT and cyber resilience.*

#### MAS Clause 3: `MAS-1.4(a).2`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must establish a sound and robust technology risk management framework.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Control B mandates the technical execution of risk assessments, including identifying threats, determining likelihood/impact, and documenting results.], Missing: [Control B lacks the governance mandate for the Board and Senior Management to establish the overarching technology risk management framework.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-1.4(a).2.)
```
> *The Board of Directors and Senior Management must establish a sound and robust technology risk management framework.*

#### MAS Clause 4: `MAS-6.5.2`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must establish measures to control and monitor the use of shadow IT within its environment.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Control B mandates the identification of system vulnerabilities and unauthorized access risks, which provides the foundational visibility required to detect and monitor shadow IT assets.], Missing: [Control B lacks specific mandates for the active monitoring, inventory management, or technical controls required to restrict and manage the use of unauthorized IT services and applications.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-6.5.2.)
```
> *The Financial Institution must establish measures to control and monitor the use of shadow IT within its environment.*

#### MAS Clause 5: `MAS-6.5.3.a`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must establish a process to assess the risk of end-user developed or acquired applications.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Control B mandates a comprehensive risk assessment process including threat/vulnerability identification, likelihood/impact determination, and documentation, which technically satisfies the requirement to assess risk.], Missing: [Control B is a general system-level risk assessment framework and does not explicitly mandate the specific scope, methodology, or frequency required for assessing 'end-user developed or acquired applications' as distinct from the broader organizational system.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-6.5.3.a.)
```
> *The Financial Institution must establish a process to assess the risk of end-user developed or acquired applications.*

#### MAS Clause 6: `MAS-7.1.1`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must establish an IT service management framework comprising governance structures, processes, and procedures for IT service management activities.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Control B mandates the execution, documentation, and integration of risk assessments, which serves as a critical input for the governance structures required by Requirement A.], Missing: [Control B lacks mandates for establishing the broader IT service management framework, including governance structures, processes, and procedures for general IT service management activities beyond risk assessment.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-7.1.1.)
```
> *The Financial Institution must establish an IT service management framework comprising governance structures, processes, and procedures for IT service management activities.*

#### MAS Clause 7: `MAS-7.3.2.b`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must conduct a risk assessment for hardware and software approaching their end-of-support date.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Control B mandates a comprehensive, ongoing risk assessment process that includes identifying threats and vulnerabilities, which technically covers the identification of risks associated with end-of-support hardware and software.], Missing: [Control B lacks the specific regulatory mandate to explicitly target or schedule assessments based on 'end-of-support' dates, focusing instead on general system changes and ongoing lifecycle management.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-7.3.2.b.)
```
> *The Financial Institution must conduct a risk assessment for hardware and software approaching their end-of-support date.*

#### MAS Clause 8: `MAS-7.5.6.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must define procedures for assessing, approving, and implementing emergency changes to reduce the risk to the security and stability of the production environment.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Control B mandates the identification of threats and vulnerabilities and the determination of likelihood and impact, which provides the technical risk assessment component required for emergency changes.], Missing: [Control B lacks specific mandates for the procedural workflow of 'approving' and 'implementing' emergency changes, focusing instead on general risk assessment documentation and review.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-7.5.6.a.)
```
> *The Financial Institution must define procedures for assessing, approving, and implementing emergency changes to reduce the risk to the security and stability of the production environment.*

#### MAS Clause 9: `MAS-13.4.1`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must perform an adversarial attack simulation exercise to test and validate the effectiveness of its cyber defence and response plan against prevalent cyber threats.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Control B mandates the identification of threats and vulnerabilities and the determination of likelihood and impact, which provides the foundational threat intelligence required to design and execute an adversarial simulation.], Missing: [Control B lacks the active execution of adversarial attack simulations and the validation of the cyber defense and response plan's operational effectiveness against those attacks.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-13.4.1.)
```
> *The Financial Institution must perform an adversarial attack simulation exercise to test and validate the effectiveness of its cyber defence and response plan against prevalent cyber threats.*

#### MAS Clause 10: `MAS-13.4.2.b`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must conduct the exercise in a controlled manner under close supervision to prevent disruption to its production systems.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Control B mandates the identification of threats and vulnerabilities that could cause system disruption, which is a prerequisite for the controlled exercise required by Requirement A.], Missing: [Control B lacks specific mandates for the operational execution methodology, supervision protocols, and change management controls necessary to prevent disruption during the actual exercise.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-13.4.2.b.)
```
> *The Financial Institution must conduct the exercise in a controlled manner under close supervision to prevent disruption to its production systems.*

#### MAS Clause 11: `MAS-13.5.1`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must design the threat scenario based on challenging but plausible cyber threats to simulate realistic adversarial attacks during any cyber security assessment.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [NIST-RA-3 mandates the identification of threats and vulnerabilities, which is a prerequisite component for designing threat scenarios.], Missing: [Control B lacks the specific mandate to design challenging, plausible threat scenarios for simulating realistic adversarial attacks during security assessments.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-13.5.1.)
```
> *The Financial Institution must design the threat scenario based on challenging but plausible cyber threats to simulate realistic adversarial attacks during any cyber security assessment.*

#### MAS Clause 12: `MAS-13.5.2.a`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must use threat intelligence relevant to its IT environment to identify threat actors most likely to pose a threat.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Control B mandates identifying threats to the system, which encompasses the identification of threat actors, but frames this within a broader risk assessment methodology.], Missing: [Control B lacks the specific mandate to utilize 'threat intelligence' as the primary mechanism for identifying threat actors, focusing instead on general system threats and vulnerabilities.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-13.5.2.a.)
```
> *The Financial Institution must use threat intelligence relevant to its IT environment to identify threat actors most likely to pose a threat.*

#### MAS Clause 13: `MAS-13.6.1.a`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must perform severity assessment and classification of an issue.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Control B mandates the determination of likelihood and impact (magnitude of harm), which constitutes the technical basis for severity assessment.], Missing: [Control B lacks explicit mandates for the formal classification of issues into specific severity levels (e.g., Critical, High, Medium, Low) or the operational triage of issues as distinct from the broader risk assessment process.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-13.6.1.a.)
```
> *The Financial Institution must perform severity assessment and classification of an issue.*

#### MAS Clause 14: `MAS-13.6.1.c`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.85`)
- **Rationale**:
```text
• MAS Requirement: must develop risk assessment and mitigation strategies to manage deviations from the framework.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Control B mandates the technical execution of risk assessments to identify threats, vulnerabilities, and impacts, providing the analytical basis for mitigation.], Missing: [Requirement A explicitly mandates the development of mitigation strategies to manage deviations, whereas Control B is limited to the assessment and documentation of risk without prescribing the mitigation actions.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-13.6.1.c.)
```
> *The Financial Institution must develop risk assessment and mitigation strategies to manage deviations from the framework.*

#### MAS Clause 15: `MAS-15.1.1`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must conduct IT audit to provide the board of directors and senior management an independent and objective opinion on the adequacy and effectiveness of risk management, governance, and internal controls relative to existing and emerging technology risks.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Control B mandates the technical execution of risk assessments to identify threats, vulnerabilities, and impacts, which provides the substantive data required for the audit.], Missing: [Control B lacks the mandate for an independent, objective audit function and the specific requirement to report governance and internal control adequacy to the board and senior management.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-15.1.1.)
```
> *The Financial Institution must conduct IT audit to provide the board of directors and senior management an independent and objective opinion on the adequacy and effectiveness of risk management, governance, and internal controls relative to existing and emerging technology risks.*

#### MAS Clause 16: `MAS-15.1.2.a`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.85`)
- **Rationale**:
```text
• MAS Requirement: must identify a comprehensive set of auditable areas for technology risk to enable effective risk assessment during audit planning.
• NIST Control: NIST-RA-3 Risk Assessment: Conduct a risk assessment, including:.
• Gap Analysis: Covered: [Control B mandates the execution of a comprehensive risk assessment that identifies threats, vulnerabilities, and impacts, which inherently requires the identification of auditable areas for technology risk.], Missing: [Control B focuses on the active execution and documentation of risk assessments rather than the specific planning phase requirement to identify a comprehensive set of auditable areas for audit planning purposes.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-3 provides technical control capabilities addressing obligations in MAS-15.1.2.a.)
```
> *The Financial Institution must identify a comprehensive set of auditable areas for technology risk to enable effective risk assessment during audit planning.*

---

### Cluster 4: `NIST-SR-6` (Supplier Assessments and Reviews) addresses 3 MAS Obligations

> **NIST Control Statement [NIST-SR-6]**:
> *Assess and review the supply chain-related risks associated with suppliers or contractors and the system, system component, or system service they provide {{ insert: param, sr-06_odp }}.
An assessment and review of supplier risk includes security and supply chain risk management processes, foreign o...*

#### MAS Clause 1: `MAS-1.3.a`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-SR-6 Supplier Assessments and Reviews: Assess and review the supply chain-related risks associated with suppliers or contractors and the system, system component, or system service they provide {{ insert: param, sr-06_odp }}..
• Gap Analysis: Covered: [Control B mandates specific supplier and supply chain risk assessments, reviews, and policy documentation, which constitute a specific subset of technology risks.], Missing: [Requirement A requires evaluation of all technology risks (e.g., internal infrastructure, software vulnerabilities, operational failures), whereas Control B is strictly limited to supply chain and third-party supplier risks.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SR-6 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *The Financial Institution must evaluate its exposure to technology risks.*

#### MAS Clause 2: `MAS-6.5.3.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.85`)
- **Rationale**:
```text
• MAS Requirement: must establish a process to assess the risk of end-user developed or acquired applications.
• NIST Control: NIST-SR-6 Supplier Assessments and Reviews: Assess and review the supply chain-related risks associated with suppliers or contractors and the system, system component, or system service they provide {{ insert: param, sr-06_odp }}..
• Gap Analysis: Covered: [Control B mandates supplier risk assessments and reviews, which encompass the evaluation of third-party application development practices and quality control.], Missing: [Control B focuses on the supplier entity and supply chain integrity rather than the specific technical risk assessment of the end-user developed or acquired application code and functionality itself.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SR-6 provides technical control capabilities addressing obligations in MAS-6.5.3.a.)
```
> *The Financial Institution must establish a process to assess the risk of end-user developed or acquired applications.*

#### MAS Clause 3: `MAS-6.5.3.b`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.85`)
- **Rationale**:
```text
• MAS Requirement: must implement appropriate controls and security measures to address identified risks.
• NIST Control: NIST-SR-6 Supplier Assessments and Reviews: Assess and review the supply chain-related risks associated with suppliers or contractors and the system, system component, or system service they provide {{ insert: param, sr-06_odp }}..
• Gap Analysis: Covered: [Control B implements specific supply chain risk management processes, including supplier assessments, due diligence reviews, and integration of security requirements into the acquisition lifecycle.], Missing: [Requirement A mandates a comprehensive set of controls for all identified risks across the entire organization, whereas Control B is strictly limited to supply chain and third-party vendor risks.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-SR-6 provides technical control capabilities addressing obligations in MAS-6.5.3.b.)
```
> *The Financial Institution must implement appropriate controls and security measures to address identified risks.*

---

### Cluster 5: `NIST-RA-5` (Vulnerability Monitoring and Scanning) addresses 24 MAS Obligations

> **NIST Control Statement [NIST-RA-5]**:
> *Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;
Employ vulnerability monitoring tools and techniques that facilitate interoperability among tools and ...*

#### MAS Clause 1: `MAS-1.3.a`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must evaluate its exposure to technology risks.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B implements technical vulnerability scanning, monitoring, and remediation processes which constitute a primary technical component of technology risk evaluation.], Missing: [Control B lacks the broader strategic risk assessment mandates, such as identifying non-technical risks, conducting enterprise-wide risk analysis, and defining risk tolerance, which are required by Requirement A.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-1.3.a.)
```
> *The Financial Institution must evaluate its exposure to technology risks.*

#### MAS Clause 2: `MAS-1.3.b`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must implement a robust risk management framework to ensure IT and cyber resilience.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B implements specific technical mechanisms for vulnerability scanning, analysis, remediation, and information sharing to identify and address system weaknesses.], Missing: [Control B lacks the broader governance, policy, and strategic framework components required to constitute a comprehensive risk management framework.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-1.3.b.)
```
> *The Financial Institution must implement a robust risk management framework to ensure IT and cyber resilience.*

#### MAS Clause 3: `MAS-1.4(b).1`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.80`)
- **Rationale**:
```text
• MAS Requirement: must adopt a defence-in-depth approach to strengthen cyber resilience.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates specific technical processes for vulnerability monitoring, scanning, analysis, and remediation, which constitute a critical layer of the defense-in-depth strategy.], Missing: [Control B is limited to vulnerability management and does not address other essential defense-in-depth layers such as network segmentation, access control, encryption, or physical security.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-1.4(b).1.)
```
> *The Financial Institution must adopt a defence-in-depth approach to strengthen cyber resilience.*

#### MAS Clause 4: `MAS-6.5.2`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must establish measures to control and monitor the use of shadow IT within its environment.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates continuous vulnerability scanning and monitoring of system components, which detects unauthorized or shadow IT assets that expose security vulnerabilities.], Missing: [Control B lacks specific mandates for the governance, inventory, and policy enforcement required to control the procurement and usage of shadow IT, focusing instead on technical vulnerability remediation.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-6.5.2.)
```
> *The Financial Institution must establish measures to control and monitor the use of shadow IT within its environment.*

#### MAS Clause 5: `MAS-6.5.3.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.86`)
- **Rationale**:
```text
• MAS Requirement: must establish a process to assess the risk of end-user developed or acquired applications.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates the technical execution of vulnerability scanning and analysis for hosted applications, which constitutes a primary technical mechanism for assessing application risk.], Missing: [Control B focuses on technical vulnerability identification and remediation, lacking the broader governance framework, risk acceptance processes, and formal risk assessment methodology required by Requirement A.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-6.5.3.a.)
```
> *The Financial Institution must establish a process to assess the risk of end-user developed or acquired applications.*

#### MAS Clause 6: `MAS-6.5.3.d`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.82`)
- **Rationale**:
```text
• MAS Requirement: must conduct proper testing before deploying end-user developed or acquired applications.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates vulnerability scanning and analysis of hosted applications, which serves as a technical testing mechanism for deployed software.], Missing: [Control B lacks explicit requirements for pre-deployment testing of end-user developed applications, formal test procedures/checklists, and the specific governance mandate to test before deployment.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-6.5.3.d.)
```
> *The Financial Institution must conduct proper testing before deploying end-user developed or acquired applications.*

#### MAS Clause 7: `MAS-7.2.2`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must review and verify the configuration information of its hardware and software on a regular basis.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates automated scanning, configuration verification, vulnerability analysis, and remediation of hardware and software flaws.], Missing: [None: Full coverage].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-7.2.2.)
```
> *The Financial Institution must review and verify the configuration information of its hardware and software on a regular basis.*

#### MAS Clause 8: `MAS-7.3.1.a`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must avoid using outdated and unsupported hardware or software.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates continuous vulnerability scanning, patch level monitoring, and remediation of identified flaws, which directly addresses the technical requirement to avoid using unsupported software.], Missing: [Control B focuses on vulnerability remediation and does not explicitly mandate the proactive procurement, inventory management, or decommissioning of outdated and unsupported hardware.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-7.3.1.a.)
```
> *The Financial Institution must avoid using outdated and unsupported hardware or software.*

#### MAS Clause 9: `MAS-7.3.1.b`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.85`)
- **Rationale**:
```text
• MAS Requirement: must closely monitor the end-of-support dates of its hardware and software.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates the use of automated vulnerability scanning tools to detect software flaws and improper configurations, which inherently requires tracking software versions and patch levels to identify known vulnerabilities.], Missing: [Control B lacks explicit mandates for monitoring hardware end-of-support (EOS) dates, managing hardware lifecycle, or addressing hardware-specific obsolescence and support status.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-7.3.1.b.)
```
> *The Financial Institution must closely monitor the end-of-support dates of its hardware and software.*

#### MAS Clause 10: `MAS-7.3.2.b`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.86`)
- **Rationale**:
```text
• MAS Requirement: must conduct a risk assessment for hardware and software approaching their end-of-support date.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates vulnerability scanning and risk-based remediation, which inherently requires identifying software approaching end-of-support as these components are primary sources of unpatched vulnerabilities.], Missing: [Control B lacks an explicit mandate for a proactive risk assessment specifically targeting the 'end-of-support' status of hardware and software, focusing instead on active vulnerability detection and remediation.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-7.3.2.b.)
```
> *The Financial Institution must conduct a risk assessment for hardware and software approaching their end-of-support date.*

#### MAS Clause 11: `MAS-7.3.2.c`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must implement effective risk mitigation measures for hardware and software approaching their end-of-support date.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates the scanning for patch levels and the remediation of legitimate vulnerabilities based on risk assessment, which directly addresses the mitigation of risks associated with unsupported software and hardware.], Missing: [Control B lacks specific mandates for the proactive identification of end-of-support (EOS) dates, the formal risk assessment of unsupported status itself, and the requirement to implement mitigation measures (such as compensating controls or retirement) for systems that cannot be patched.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-7.3.2.c.)
```
> *The Financial Institution must implement effective risk mitigation measures for hardware and software approaching their end-of-support date.*

#### MAS Clause 12: `MAS-7.7.1`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must establish an incident management framework to restore affected IT services or systems to a secure and stable state as quickly as possible, minimizing impact to the business and customers.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates the identification, analysis, and remediation of vulnerabilities, which is a critical technical component of restoring systems to a secure state.], Missing: [Control B lacks requirements for incident response coordination, service restoration procedures, business continuity, and customer impact minimization.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-7.7.1.)
```
> *The Financial Institution must establish an incident management framework to restore affected IT services or systems to a secure and stable state as quickly as possible, minimizing impact to the business and customers.*

#### MAS Clause 13: `MAS-13.4.1`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must perform an adversarial attack simulation exercise to test and validate the effectiveness of its cyber defence and response plan against prevalent cyber threats.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates the use of automated scanning tools, continuous monitoring, and remediation processes to identify and fix technical vulnerabilities.], Missing: [Control B lacks the specific mandate for active adversarial attack simulations (e.g., red teaming, penetration testing) to validate the effectiveness of the cyber defense and response plan against prevalent threats.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-13.4.1.)
```
> *The Financial Institution must perform an adversarial attack simulation exercise to test and validate the effectiveness of its cyber defence and response plan against prevalent cyber threats.*

#### MAS Clause 14: `MAS-13.5.1`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must design the threat scenario based on challenging but plausible cyber threats to simulate realistic adversarial attacks during any cyber security assessment.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates the use of automated scanning tools and analysis of scan reports to identify vulnerabilities, which constitutes a technical component of a security assessment.], Missing: [Control B lacks requirements for designing specific threat scenarios, simulating realistic adversarial attacks, or conducting red team exercises to validate defenses against active threats.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-13.5.1.)
```
> *The Financial Institution must design the threat scenario based on challenging but plausible cyber threats to simulate realistic adversarial attacks during any cyber security assessment.*

#### MAS Clause 15: `MAS-13.5.2.b`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must identify the tactics, techniques, and procedures most likely to be used in such attacks.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates the use of automated scanning tools and analysis to identify software flaws, improper configurations, and known vulnerabilities in systems and applications.], Missing: [Control B focuses on technical vulnerability identification (CVEs, misconfigurations) and lacks the explicit mandate to identify attacker tactics, techniques, and procedures (TTPs) or threat actor methodologies.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-13.5.2.b.)
```
> *The Financial Institution must identify the tactics, techniques, and procedures most likely to be used in such attacks.*

#### MAS Clause 16: `MAS-13.6.1`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.86`)
- **Rationale**:
```text
• MAS Requirement: must establish a comprehensive remediation process to track and resolve issues identified from cyber security assessments or exercises.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates the technical execution of vulnerability scanning, analysis, and remediation of identified flaws, providing the operational mechanism to resolve specific technical issues.], Missing: [Control B lacks the explicit mandate for a comprehensive governance framework to track and resolve non-technical issues or findings from broader cyber security assessments and exercises (e.g., red team exercises, audits, or policy violations) beyond automated vulnerability scanning.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-13.6.1.)
```
> *The Financial Institution must establish a comprehensive remediation process to track and resolve issues identified from cyber security assessments or exercises.*

#### MAS Clause 17: `MAS-13.6.1.b`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.81`)
- **Rationale**:
```text
• MAS Requirement: must define a timeframe to remediate issues of different severity.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates the remediation of legitimate vulnerabilities based on an organizational risk assessment, which inherently requires defining a timeframe for remediation.], Missing: [Control B does not explicitly mandate the definition of specific, distinct remediation timeframes categorized by severity levels, focusing instead on the general risk-based remediation process.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-13.6.1.b.)
```
> *The Financial Institution must define a timeframe to remediate issues of different severity.*

#### MAS Clause 18: `MAS-13.6.1.c`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must develop risk assessment and mitigation strategies to manage deviations from the framework.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates the technical execution of vulnerability scanning, analysis, and remediation based on risk assessment, which constitutes a specific operational subset of the broader risk management strategies required by Requirement A.], Missing: [Control B lacks the mandate for developing comprehensive risk assessment methodologies, strategic mitigation planning beyond immediate remediation, and the governance framework for managing deviations from the overall security framework.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-13.6.1.c.)
```
> *The Financial Institution must develop risk assessment and mitigation strategies to manage deviations from the framework.*

#### MAS Clause 19: `MAS-14.1.3`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must implement adequate measures to minimize exposure of its online financial services to common attack vectors such as code injection attacks, cross-site scripting, man-in-the-middle attacks, DNS hijacking, DDoS, malware, and spoofing attacks.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates continuous vulnerability monitoring, automated scanning, and remediation of software flaws and misconfigurations, which directly addresses the requirement to minimize exposure to code injection, XSS, and malware vectors.], Missing: [Control B lacks explicit mandates for network-layer security controls required to mitigate man-in-the-middle attacks, DNS hijacking, DDoS, and spoofing attacks.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-14.1.3.)
```
> *The Financial Institution must implement adequate measures to minimize exposure of its online financial services to common attack vectors such as code injection attacks, cross-site scripting, man-in-the-middle attacks, DNS hijacking, DDoS, malware, and spoofing attacks.*

#### MAS Clause 20: `MAS-14.1.4`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.83`)
- **Rationale**:
```text
• MAS Requirement: must implement specific measures aimed at addressing the risks unique to mobile applications.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates comprehensive vulnerability monitoring, scanning, and remediation for hosted applications, which addresses the technical risk identification aspect of mobile application security.], Missing: [Control B lacks specific mandates for mobile-specific risks such as insecure data storage, weak cryptography, insecure inter-app communication, and platform-specific API usage.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-14.1.4.)
```
> *The Financial Institution must implement specific measures aimed at addressing the risks unique to mobile applications.*

#### MAS Clause 21: `MAS-14.1.6.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.81`)
- **Rationale**:
```text
• MAS Requirement: must actively monitor for phishing campaigns targeting the Financial Institution and its customers.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates continuous monitoring and scanning of systems and applications for technical vulnerabilities, including the use of automated tools and vulnerability disclosure programs.], Missing: [Control B lacks specific mandates for monitoring external phishing campaigns targeting the institution and its customers, focusing instead on internal system and software vulnerabilities.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-14.1.6.a.)
```
> *The Financial Institution must actively monitor for phishing campaigns targeting the Financial Institution and its customers.*

#### MAS Clause 22: `MAS-14.1.7`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must disallow rooted or jailbroken mobile devices from accessing the Financial Institution’s mobile applications to perform financial transactions unless the application is secured within a sandbox or container that insulates it from tampering and interception by malware.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates vulnerability scanning and remediation for systems and applications, which indirectly addresses the risk of malware on devices by ensuring the backend infrastructure is secure.], Missing: [Control B lacks any mandate for client-side device posture assessment, specifically the detection and blocking of rooted or jailbroken mobile devices.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-14.1.7.)
```
> *The Financial Institution must disallow rooted or jailbroken mobile devices from accessing the Financial Institution’s mobile applications to perform financial transactions unless the application is secured within a sandbox or container that insulates it from tampering and interception by malware.*

#### MAS Clause 23: `MAS-C.1.4`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.86`)
- **Rationale**:
```text
• MAS Requirement: must implement anti-hooking or anti-tampering mechanisms to prevent the injection of malicious code that could alter or monitor application behaviour at runtime.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates vulnerability scanning, static/dynamic analysis, and remediation of software flaws, which indirectly addresses the risk of malicious code injection by identifying and patching exploitable vulnerabilities.], Missing: [Control B lacks specific mandates for runtime anti-hooking or anti-tampering mechanisms to actively prevent code injection or monitor/alter application behavior during execution.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-C.1.4.)
```
> *The Financial Institution must implement anti-hooking or anti-tampering mechanisms to prevent the injection of malicious code that could alter or monitor application behaviour at runtime.*

#### MAS Clause 24: `MAS-C.1.6`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Dyn Conf: `0.84`)
- **Rationale**:
```text
• MAS Requirement: must implement code obfuscation techniques to prevent reverse engineering of the mobile application.
• NIST Control: NIST-RA-5 Vulnerability Monitoring and Scanning: Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;.
• Gap Analysis: Covered: [Control B mandates static and binary analysis of custom software, which can detect reverse engineering risks, but focuses on identifying vulnerabilities rather than implementing obfuscation techniques.], Missing: [Control B lacks specific mandates for code obfuscation techniques to prevent reverse engineering, focusing instead on vulnerability scanning and remediation.].
• Assurance Conclusion: PARTIAL_COVERAGE (NIST-RA-5 provides technical control capabilities addressing obligations in MAS-C.1.6.)
```
> *The Financial Institution must implement code obfuscation techniques to prevent reverse engineering of the mobile application.*

---

