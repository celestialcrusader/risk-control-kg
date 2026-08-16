# Production Two-Dimensional Regulatory Crosswalk Results (Sprint L)

**Retrieval Architecture**: Hybrid Candidate Retrieval (BAAI/bge-small-en-v1.5 + BM25 Okapi) with **Top-15 Recall Funnel**  
**Catalog Scoping**: Withdrawn & Blank Rev 5 Controls Purged (`RA-4`, `SA-12`, etc.)  
**Reasoning Engine**: Qwen 35B Two-Dimensional Dual-Judge (Semantic Relation + Assurance Coverage)  
**Database Dual-Write**: PostgreSQL (`obligation_framework_mappings`) & Memgraph (`:CROSSWALKS_TO`)  
**Execution Date**: 2026-08-16  

---

## Section A: Two-Dimensional Crosswalk Statistics

| Metric | Value |
|---|---|
| **Total MAS TRM Obligations** | `85` |
| **Active NIST SP 800-53 Control Objectives** | `294` |
| **Total Active Crosswalk Links Formed** | `743` |
| **MAS Obligations Mapped (>= 1 match)** | `70` (82.4%) |
| **MAS Obligations Unmapped (0 matches)** | `15` (17.6%) |

### Dimension 1: Semantic Relationship Distribution (Source $\rightarrow$ Target Perspective)

| Semantic Relationship | Description | Edge Count | Percentage |
|---|---|---|---|
| `EQUIVALENT` | 1-to-1 Identical Scope & Intent | 365 | 49.1% |
| `SUBSET_OF` | Target NIST control completely satisfies MAS (MAS $\subseteq$ NIST) | 91 | 12.2% |
| `SUPERSET_OF` | MAS obligation is broader; NIST control covers a sub-part | 80 | 10.8% |
| `OVERLAPS` | Material conceptual overlap without strict containment | 152 | 20.5% |
| `SUPPORTS` | Target control enables/supports MAS without satisfying it | 55 | 7.4% |

### Dimension 2: Assurance Coverage Distribution (Audit Defensibility)

| Assurance Coverage Level | Meaning | Edge Count | Percentage |
|---|---|---|---|
| `FULL_COVERAGE` | NIST evidence completely satisfies MAS obligation for audit | 456 | 61.4% |
| `PARTIAL_COVERAGE` | NIST evidence satisfies material part; remaining gaps | 226 | 30.4% |
| `NO_COVERAGE` | NIST evidence does NOT satisfy MAS (enabling / supporting only) | 61 | 8.2% |

---

## Section B: 25 Sample Two-Dimensional Matches (Complete Verbatim Text)

### Sample Match 1: `MAS-1.3.a` ⟷ `NIST-RA-8`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.59`)
* **Retrieval Trace**: RRF: 0.0393 (Dense Sim: 0.59, BM25: 17.35)
* **Defensible Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.

> **MAS TRM Clause [MAS-1.3.a]**:
> *The Financial Institution must evaluate its exposure to technology risks.*

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

### Sample Match 2: `MAS-1.3.b` ⟷ `NIST-SA-3`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `FULL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.56`)
* **Retrieval Trace**: RRF: 0.0280 (Dense Sim: 0.56, BM25: 12.35)
* **Defensible Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.

> **MAS TRM Clause [MAS-1.3.b]**:
> *The Financial Institution must implement a robust risk management framework to ensure IT and cyber resilience.*

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

### Sample Match 3: `MAS-1.4(a).2` ⟷ `NIST-SR-3`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `FULL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.54`)
* **Retrieval Trace**: RRF: 0.0287 (Dense Sim: 0.54, BM25: 14.92)
* **Defensible Rationale**: LLM Cross-Framework Semantic Evaluation

> **MAS TRM Clause [MAS-1.4(a).2]**:
> *The Board of Directors and Senior Management must establish a sound and robust technology risk management framework.*

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

### Sample Match 4: `MAS-1.4(b).3` ⟷ `NIST-PM-11`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `FULL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.53`)
* **Retrieval Trace**: RRF: 0.0338 (Dense Sim: 0.53, BM25: 29.53)
* **Defensible Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.

> **MAS TRM Clause [MAS-1.4(b).3]**:
> *The Financial Institution must continuously improve IT processes and controls to preserve the confidentiality, integrity, and availability of data and IT systems.*

> **NIST SP 800-53 Control [NIST-PM-11 - Mission and Business Process Definition]**:
> *Define organizational mission and business processes with consideration for information security and privacy and the resulting risk to organizational operations, organizational assets, individuals, other organizations, and the Nation; and
Determine information protection and personally identifiable information processing needs arising from the defined mission and business processes; and
Review and revise the mission and business processes {{ insert: param, pm-11_odp }}.
Protection needs are technology-independent capabilities that are required to counter threats to organizations, individuals, systems, and the Nation through the compromise of information (i.e., loss of confidentiality, integrity, availability, or privacy). Information protection and personally identifiable information processing needs are derived from the mission and business needs defined by organizational stakeholders, the mission and business processes designed to meet those needs, and the organizational risk management strategy. Information protection and personally identifiable information processing needs determine the required controls for the organization and the systems. Inherent to defining protection and personally identifiable information processing needs is an understanding of the adverse impact that could result if a compromise or breach of information occurs. The categorization process is used to make such potential impact determinations. Privacy risks to individuals can arise from the compromise of personally identifiable information, but they can also arise as unintended consequences or a byproduct of the processing of personally identifiable information at any stage of the information life cycle. Privacy risk assessments are used to prioritize the risks that are created for individuals from system processing of personally identifiable information. These risk assessments enable the selection of the required privacy controls for the organization and systems. Mission and business process definitions and the associated protection requirements are documented in accordance with organizational policies and procedures.
organizational mission and business processes are defined with consideration for information security;
organizational mission and business processes are defined with consideration for privacy;
organizational mission and business processes are defined with consideration for the resulting risk to organizational operations, organizational assets, individuals, other organizations, and the Nation;
information protection needs arising from the defined mission and business processes are determined;
personally identifiable information processing needs arising from the defined mission and business processes are determined;
the mission and business processes are reviewed and revised {{ insert: param, pm-11_odp }}.
Information security program plan

privacy program plan

risk management strategy

procedures for determining mission and business protection needs

information security and privacy risk assessment results relevant to the determination of mission and business protection needs

personally identifiable information processing policy

personally identifiable information inventory

other relevant documents or records
Organizational personnel with information security and privacy program planning and plan implementation responsibilities

organizational personnel responsible for enterprise risk management

organizational personnel responsible for determining information protection needs for mission and business processes

organizational personnel with information security and privacy responsibilities
Organizational processes for defining mission and business processes and their information protection needs*

---

### Sample Match 5: `MAS-6.5.2` ⟷ `NIST-CA-2`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.55`)
* **Retrieval Trace**: RRF: 0.0246 (Dense Sim: 0.55, BM25: 23.43)
* **Defensible Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.

> **MAS TRM Clause [MAS-6.5.2]**:
> *The Financial Institution must establish measures to control and monitor the use of shadow IT within its environment.*

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

### Sample Match 6: `MAS-6.5.3.b` ⟷ `NIST-CA-6`

* **Semantic Relation**: `SUPERSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.57`)
* **Retrieval Trace**: RRF: 0.0231 (Dense Sim: 0.57, BM25: 17.59)
* **Defensible Rationale**: Evaluated semantic relationship as SUPERSET_OF with PARTIAL_COVERAGE assurance level.

> **MAS TRM Clause [MAS-6.5.3.b]**:
> *The Financial Institution must implement appropriate controls and security measures to address identified risks.*

> **NIST SP 800-53 Control [NIST-CA-6 - Authorization]**:
> *Assign a senior official as the authorizing official for the system;
Assign a senior official as the authorizing official for common controls available for inheritance by organizational systems;
Ensure that the authorizing official for the system, before commencing operations:
Accepts the use of common controls inherited by the system; and
Authorizes the system to operate;
Ensure that the authorizing official for common controls authorizes the use of those controls for inheritance by organizational systems;
Update the authorizations {{ insert: param, ca-06_odp }}.
Authorizations are official management decisions by senior officials to authorize operation of systems, authorize the use of common controls for inheritance by organizational systems, and explicitly accept the risk to organizational operations and assets, individuals, other organizations, and the Nation based on the implementation of agreed-upon controls. Authorizing officials provide budgetary oversight for organizational systems and common controls or assume responsibility for the mission and business functions supported by those systems or common controls. The authorization process is a federal responsibility, and therefore, authorizing officials must be federal employees. Authorizing officials are both responsible and accountable for security and privacy risks associated with the operation and use of organizational systems. Nonfederal organizations may have similar processes to authorize systems and senior officials that assume the authorization role and associated responsibilities.

Authorizing officials issue ongoing authorizations of systems based on evidence produced from implemented continuous monitoring programs. Robust continuous monitoring programs reduce the need for separate reauthorization processes. Through the employment of comprehensive continuous monitoring processes, the information contained in authorization packages (i.e., security and privacy plans, assessment reports, and plans of action and milestones) is updated on an ongoing basis. This provides authorizing officials, common control providers, and system owners with an up-to-date status of the security and privacy posture of their systems, controls, and operating environments. To reduce the cost of reauthorization, authorizing officials can leverage the results of continuous monitoring processes to the maximum extent possible as the basis for rendering reauthorization decisions.
a senior official is assigned as the authorizing official for the system;
a senior official is assigned as the authorizing official for common controls available for inheritance by organizational systems;
before commencing operations, the authorizing official for the system accepts the use of common controls inherited by the system;
before commencing operations, the authorizing official for the system authorizes the system to operate;
the authorizing official for common controls authorizes the use of those controls for inheritance by organizational systems;
the authorizations are updated {{ insert: param, ca-06_odp }}.
Assessment, authorization, and monitoring policy

procedures addressing authorization

system security plan, privacy plan, assessment report, plan of action and milestones

authorization statement

other relevant documents or records
Organizational personnel with authorization responsibilities

organizational personnel with information security and privacy responsibilities
Mechanisms that facilitate authorizations and updates*

---

### Sample Match 7: `MAS-7.2.1` ⟷ `NIST-SA-10`

* **Semantic Relation**: `SUPERSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.62`)
* **Retrieval Trace**: RRF: 0.0286 (Dense Sim: 0.62, BM25: 15.57)
* **Defensible Rationale**: LLM Cross-Framework Semantic Evaluation

> **MAS TRM Clause [MAS-7.2.1]**:
> *The Financial Institution must implement a configuration management process to maintain accurate information regarding its hardware and software.*

> **NIST SP 800-53 Control [NIST-SA-10 - Developer Configuration Management]**:
> *Require the developer of the system, system component, or system service to:
Perform configuration management during system, component, or service {{ insert: param, sa-10_odp.01 }};
Document, manage, and control the integrity of changes to {{ insert: param, sa-10_odp.02 }};
Implement only organization-approved changes to the system, component, or service;
Document approved changes to the system, component, or service and the potential security and privacy impacts of such changes; and
Track security flaws and flaw resolution within the system, component, or service and report findings to {{ insert: param, sa-10_odp.03 }}.
Organizations consider the quality and completeness of configuration management activities conducted by developers as direct evidence of applying effective security controls. Controls include protecting the master copies of material used to generate security-relevant portions of the system hardware, software, and firmware from unauthorized modification or destruction. Maintaining the integrity of changes to the system, system component, or system service requires strict configuration control throughout the system development life cycle to track authorized changes and prevent unauthorized changes.

The configuration items that are placed under configuration management include the formal model; the functional, high-level, and low-level design specifications; other design data; implementation documentation; source code and hardware schematics; the current running version of the object code; tools for comparing new versions of security-relevant hardware descriptions and source code with previous versions; and test fixtures and documentation. Depending on the mission and business needs of organizations and the nature of the contractual relationships in place, developers may provide configuration management support during the operations and maintenance stage of the system development life cycle.
the developer of the system, system component, or system service is required to perform configuration management during system, component, or service {{ insert: param, sa-10_odp.01 }};
the developer of the system, system component, or system service is required to document the integrity of changes to {{ insert: param, sa-10_odp.02 }};
the developer of the system, system component, or system service is required to manage the integrity of changes to {{ insert: param, sa-10_odp.02 }};
the developer of the system, system component, or system service is required to control the integrity of changes to {{ insert: param, sa-10_odp.02 }};
the developer of the system, system component, or system service is required to implement only organization-approved changes to the system, component, or service;
the developer of the system, system component, or system service is required to document approved changes to the system, component, or service;
the developer of the system, system component, or system service is required to document the potential security impacts of approved changes;
the developer of the system, system component, or system service is required to document the potential privacy impacts of approved changes;
the developer of the system, system component, or system service is required to track security flaws within the system, component, or service;
the developer of the system, system component, or system service is required to track security flaw resolutions within the system, component, or service;
the developer of the system, system component, or system service is required to report findings to {{ insert: param, sa-10_odp.03 }}.
System and services acquisition policy

procedures addressing system developer configuration management

solicitation documentation

acquisition documentation

service level agreements

acquisition contracts for the system, system component, or system service

system developer configuration management plan

security flaw and flaw resolution tracking records

system change authorization records

change control records

configuration management records

system security plan

other relevant documents or records
Organizational personnel with system and service acquisition responsibilities

organizational personnel with information security responsibilities

organizational personnel with configuration management responsibilities

system developers
Organizational processes for monitoring developer configuration management

mechanisms supporting and/or implementing the monitoring of developer configuration management*

---

### Sample Match 8: `MAS-7.3.1.b` ⟷ `NIST-SR-4`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.55`)
* **Retrieval Trace**: RRF: 0.0324 (Dense Sim: 0.55, BM25: 16.67)
* **Defensible Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.

> **MAS TRM Clause [MAS-7.3.1.b]**:
> *The Financial Institution must closely monitor the end-of-support dates of its hardware and software.*

> **NIST SP 800-53 Control [NIST-SR-4 - Provenance]**:
> *Document, monitor, and maintain valid provenance of the following systems, system components, and associated data: {{ insert: param, sr-04_odp }}.
Every system and system component has a point of origin and may be changed throughout its existence. Provenance is the chronology of the origin, development, ownership, location, and changes to a system or system component and associated data. It may also include personnel and processes used to interact with or make modifications to the system, component, or associated data. Organizations consider developing procedures (see [SR-1](#sr-1) ) for allocating responsibilities for the creation, maintenance, and monitoring of provenance for systems and system components; transferring provenance documentation and responsibility between organizations; and preventing and monitoring for unauthorized changes to the provenance records. Organizations have methods to document, monitor, and maintain valid provenance baselines for systems, system components, and related data. These actions help track, assess, and document any changes to the provenance, including changes in supply chain elements or configuration, and help ensure non-repudiation of provenance information and the provenance change records. Provenance considerations are addressed throughout the system development life cycle and incorporated into contracts and other arrangements, as appropriate.
valid provenance is documented for {{ insert: param, sr-04_odp }};
valid provenance is monitored for {{ insert: param, sr-04_odp }};
valid provenance is maintained for {{ insert: param, sr-04_odp }}.
Supply chain risk management policy

supply chain risk management procedures

supply chain risk management plan

documentation of critical systems, critical system components, and associated data

documentation showing the history of ownership, custody, and location of and changes to critical systems or critical system components

system architecture

inter-organizational agreements and procedures

contracts

system security plan

privacy plan

personally identifiable information processing policy

other relevant documents or records
Organizational personnel with acquisition responsibilities

organizational personnel with information security and privacy responsibilities

organizational personnel with supply chain risk management responsibilities
Organizational processes for identifying the provenance of critical systems and critical system components

mechanisms used to document, monitor, or maintain provenance*

---

### Sample Match 9: `MAS-7.3.2.c` ⟷ `NIST-PM-30`

* **Semantic Relation**: `SUPERSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.59`)
* **Retrieval Trace**: RRF: 0.0308 (Dense Sim: 0.59, BM25: 12.25)
* **Defensible Rationale**: Evaluated semantic relationship as SUPERSET_OF with PARTIAL_COVERAGE assurance level.

> **MAS TRM Clause [MAS-7.3.2.c]**:
> *The Financial Institution must implement effective risk mitigation measures for hardware and software approaching their end-of-support date.*

> **NIST SP 800-53 Control [NIST-PM-30 - Supply Chain Risk Management Strategy]**:
> *Develop an organization-wide strategy for managing supply chain risks associated with the development, acquisition, maintenance, and disposal of systems, system components, and system services;
Implement the supply chain risk management strategy consistently across the organization; and
Review and update the supply chain risk management strategy on {{ insert: param, pm-30_odp }} or as required, to address organizational changes.
An organization-wide supply chain risk management strategy includes an unambiguous expression of the supply chain risk appetite and tolerance for the organization, acceptable supply chain risk mitigation strategies or controls, a process for consistently evaluating and monitoring supply chain risk, approaches for implementing and communicating the supply chain risk management strategy, and the associated roles and responsibilities. Supply chain risk management includes considerations of the security and privacy risks associated with the development, acquisition, maintenance, and disposal of systems, system components, and system services. The supply chain risk management strategy can be incorporated into the organization’s overarching risk management strategy and can guide and inform supply chain policies and system-level supply chain risk management plans. In addition, the use of a risk executive function can facilitate a consistent, organization-wide application of the supply chain risk management strategy. The supply chain risk management strategy is implemented at the organization and mission/business levels, whereas the supply chain risk management plan (see [SR-2](#sr-2) ) is implemented at the system level.
an organization-wide strategy for managing supply chain risks is developed;
the supply chain risk management strategy addresses risks associated with the development of systems;
the supply chain risk management strategy addresses risks associated with the development of system components;
the supply chain risk management strategy addresses risks associated with the development of system services;
the supply chain risk management strategy addresses risks associated with the acquisition of systems;
the supply chain risk management strategy addresses risks associated with the acquisition of system components;
the supply chain risk management strategy addresses risks associated with the acquisition of system services;
the supply chain risk management strategy addresses risks associated with the maintenance of systems;
the supply chain risk management strategy addresses risks associated with the maintenance of system components;
the supply chain risk management strategy addresses risks associated with the maintenance of system services;
the supply chain risk management strategy addresses risks associated with the disposal of systems;
the supply chain risk management strategy addresses risks associated with the disposal of system components;
the supply chain risk management strategy addresses risks associated with the disposal of system services;
the supply chain risk management strategy is implemented consistently across the organization;
the supply chain risk management strategy is reviewed and updated {{ insert: param, pm-30_odp }} or as required to address organizational changes.
Supply chain risk management strategy

organizational risk management strategy

enterprise risk management documents

other relevant documents or records
Organizational personnel with supply chain risk management responsibilities

organizational personnel with information security responsibilities

organizational personnel with acquisition responsibilities

organizational personnel with enterprise risk management responsibilities*

---

### Sample Match 10: `MAS-7.5.7` ⟷ `NIST-AU-4`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `FULL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.58`)
* **Retrieval Trace**: RRF: 0.0391 (Dense Sim: 0.58, BM25: 24.46)
* **Defensible Rationale**: LLM Cross-Framework Semantic Evaluation

> **MAS TRM Clause [MAS-7.5.7]**:
> *The Financial Institution must enable the logging facility to record activities performed during the change process.*

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

### Sample Match 11: `MAS-7.7.1` ⟷ `NIST-SA-2`

* **Semantic Relation**: `SUPPORTS`
* **Assurance Coverage**: `NO_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.54`)
* **Retrieval Trace**: RRF: 0.0298 (Dense Sim: 0.54, BM25: 31.59)
* **Defensible Rationale**: Evaluated semantic relationship as SUPPORTS with NO_COVERAGE assurance level.

> **MAS TRM Clause [MAS-7.7.1]**:
> *The Financial Institution must establish an incident management framework to restore affected IT services or systems to a secure and stable state as quickly as possible, minimizing impact to the business and customers.*

> **NIST SP 800-53 Control [NIST-SA-2 - Allocation of Resources]**:
> *Determine the high-level information security and privacy requirements for the system or system service in mission and business process planning;
Determine, document, and allocate the resources required to protect the system or system service as part of the organizational capital planning and investment control process; and
Establish a discrete line item for information security and privacy in organizational programming and budgeting documentation.
Resource allocation for information security and privacy includes funding for system and services acquisition, sustainment, and supply chain-related risks throughout the system development life cycle.
the high-level information security requirements for the system or system service are determined in mission and business process planning;
the high-level privacy requirements for the system or system service are determined in mission and business process planning;
the resources required to protect the system or system service are determined and documented as part of the organizational capital planning and investment control process;
the resources required to protect the system or system service are allocated as part of the organizational capital planning and investment control process;
a discrete line item for information security is established in organizational programming and budgeting documentation;
a discrete line item for privacy is established in organizational programming and budgeting documentation.
System and services acquisition policy

system and services acquisition procedures

system and services acquisition strategy and plans

procedures addressing the allocation of resources to information security and privacy requirements

procedures addressing capital planning and investment control

organizational programming and budgeting documentation

system security plan

privacy plan

supply chain risk management policy

other relevant documents or records
Organizational personnel with capital planning, investment control, organizational programming, and budgeting responsibilities

organizational personnel with information security and privacy responsibilities

organizational personnel with supply chain risk management responsibilities
Organizational processes for determining information security and privacy requirements

organizational processes for capital planning, programming, and budgeting

mechanisms supporting and/or implementing organizational capital planning, programming, and budgeting*

---

### Sample Match 12: `MAS-7.7.3.a` ⟷ `NIST-IR-2`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `FULL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.59`)
* **Retrieval Trace**: RRF: 0.0323 (Dense Sim: 0.59, BM25: 20.90)
* **Defensible Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.

> **MAS TRM Clause [MAS-7.7.3.a]**:
> *The Financial Institution must include processes and procedures for handling IT incidents, including cyber-related incidents, in the incident management framework.*

> **NIST SP 800-53 Control [NIST-IR-2 - Incident Response Training]**:
> *Provide incident response training to system users consistent with assigned roles and responsibilities:
Within {{ insert: param, ir-02_odp.01 }} of assuming an incident response role or responsibility or acquiring system access;
When required by system changes; and
{{ insert: param, ir-02_odp.02 }} thereafter; and
Review and update incident response training content {{ insert: param, ir-02_odp.03 }} and following {{ insert: param, ir-02_odp.04 }}.
Incident response training is associated with the assigned roles and responsibilities of organizational personnel to ensure that the appropriate content and level of detail are included in such training. For example, users may only need to know who to call or how to recognize an incident; system administrators may require additional training on how to handle incidents; and incident responders may receive more specific training on forensics, data collection techniques, reporting, system recovery, and system restoration. Incident response training includes user training in identifying and reporting suspicious activities from external and internal sources. Incident response training for users may be provided as part of [AT-2](#at-2) or [AT-3](#at-3) . Events that may precipitate an update to incident response training content include, but are not limited to, incident response plan testing or response to an actual incident (lessons learned), assessment or audit findings, or changes in applicable laws, executive orders, directives, regulations, policies, standards, and guidelines.
incident response training is provided to system users consistent with assigned roles and responsibilities within {{ insert: param, ir-02_odp.01 }} of assuming an incident response role or responsibility or acquiring system access;
incident response training is provided to system users consistent with assigned roles and responsibilities when required by system changes;
incident response training is provided to system users consistent with assigned roles and responsibilities {{ insert: param, ir-02_odp.02 }} thereafter;
incident response training content is reviewed and updated {{ insert: param, ir-02_odp.03 }};
incident response training content is reviewed and updated following {{ insert: param, ir-02_odp.04 }}.
Incident response policy

procedures addressing incident response training

incident response training curriculum

incident response training materials

privacy plan

incident response plan

incident response training records

system security plan

privacy plan

other relevant documents or records
Organizational personnel with incident response training and operational responsibilities

organizational personnel with information security and privacy responsibilities*

---

### Sample Match 13: `MAS-7.7.3.c` ⟷ `NIST-IR-6`

* **Semantic Relation**: `EQUIVALENT`
* **Assurance Coverage**: `FULL_COVERAGE` (Confidence: `0.89` | Dense Sim: `0.69`)
* **Retrieval Trace**: RRF: 0.0356 (Dense Sim: 0.69, BM25: 31.23)
* **Defensible Rationale**: Shared domain concepts (incident) with token overlap ratio of 0.25.

> **MAS TRM Clause [MAS-7.7.3.c]**:
> *The Financial Institution must define the roles and responsibilities of staff and external parties involved in incident recording, analysis, escalation, decision-making, resolution, and monitoring within the incident management framework.*

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

### Sample Match 14: `MAS-13.5.1` ⟷ `NIST-SA-20`

* **Semantic Relation**: `EQUIVALENT`
* **Assurance Coverage**: `FULL_COVERAGE` (Confidence: `0.91` | Dense Sim: `0.54`)
* **Retrieval Trace**: RRF: 0.0275 (Dense Sim: 0.54, BM25: 16.70)
* **Defensible Rationale**: Shared domain concepts (risk) with token overlap ratio of 0.30.

> **MAS TRM Clause [MAS-13.5.1]**:
> *The Financial Institution must design the threat scenario based on challenging but plausible cyber threats to simulate realistic adversarial attacks during any cyber security assessment.*

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

### Sample Match 15: `MAS-13.6.1.a` ⟷ `NIST-AU-16`

* **Semantic Relation**: `EQUIVALENT`
* **Assurance Coverage**: `FULL_COVERAGE` (Confidence: `0.89` | Dense Sim: `0.57`)
* **Retrieval Trace**: RRF: 0.0284 (Dense Sim: 0.57, BM25: 11.27)
* **Defensible Rationale**: Shared domain concepts (risk) with token overlap ratio of 0.25.

> **MAS TRM Clause [MAS-13.6.1.a]**:
> *The Financial Institution must perform severity assessment and classification of an issue.*

> **NIST SP 800-53 Control [NIST-AU-16 - Cross-organizational Audit Logging]**:
> *Employ {{ insert: param, au-16_odp.01 }} for coordinating {{ insert: param, au-16_odp.02 }} among external organizations when audit information is transmitted across organizational boundaries.
When organizations use systems or services of external organizations, the audit logging capability necessitates a coordinated, cross-organization approach. For example, maintaining the identity of individuals who request specific services across organizational boundaries may often be difficult, and doing so may prove to have significant performance and privacy ramifications. Therefore, it is often the case that cross-organizational audit logging simply captures the identity of individuals who issue requests at the initial system, and subsequent systems record that the requests originated from authorized individuals. Organizations consider including processes for coordinating audit information requirements and protection of audit information in information exchange agreements.
{{ insert: param, au-16_odp.01 }} for coordinating {{ insert: param, au-16_odp.02 }} among external organizations when audit information is transmitted across organizational boundaries are employed.
Audit and accountability policy

system security plan

privacy plan

procedures addressing methods for coordinating audit information among external organizations

system design documentation

system configuration settings and associated documentation

system audit records

other relevant documents or records
Organizational personnel with responsibilities for coordinating audit information among external organizations

organizational personnel with information security and privacy responsibilities
Mechanisms implementing cross-organizational auditing*

---

### Sample Match 16: `MAS-14.1.1` ⟷ `NIST-SC-16`

* **Semantic Relation**: `EQUIVALENT`
* **Assurance Coverage**: `FULL_COVERAGE` (Confidence: `0.95` | Dense Sim: `0.58`)
* **Retrieval Trace**: RRF: 0.0269 (Dense Sim: 0.58, BM25: 28.64)
* **Defensible Rationale**: Shared domain concepts (risk) with token overlap ratio of 0.47.

> **MAS TRM Clause [MAS-14.1.1]**:
> *The Financial Institution must implement security and control measures commensurate with the risk involved to ensure the security of data and online services.*

> **NIST SP 800-53 Control [NIST-SC-16 - Transmission of Security and Privacy Attributes]**:
> *Associate {{ insert: param, sc-16_prm_1 }} with information exchanged between systems and between system components.
Security and privacy attributes can be explicitly or implicitly associated with the information contained in organizational systems or system components. Attributes are abstractions that represent the basic properties or characteristics of an entity with respect to protecting information or the management of personally identifiable information. Attributes are typically associated with internal data structures, including records, buffers, and files within the system. Security and privacy attributes are used to implement access control and information flow control policies; reflect special dissemination, management, or distribution instructions, including permitted uses of personally identifiable information; or support other aspects of the information security and privacy policies. Privacy attributes may be used independently or in conjunction with security attributes.
{{ insert: param, sc-16_odp.01 }} are associated with information exchanged between systems;
{{ insert: param, sc-16_odp.01 }} are associated with information exchanged between system components;
{{ insert: param, sc-16_odp.02 }} are associated with information exchanged between systems;
{{ insert: param, sc-16_odp.02 }} are associated with information exchanged between system components.
System and communications protection policy

procedures addressing the transmission of security and privacy attributes

access control policy and procedures

information flow control policy

system design documentation

system configuration settings and associated documentation

system audit records

system security plan

privacy plan

other relevant documents or records
System/network administrators

organizational personnel with information security and privacy responsibilities
Mechanisms supporting and/or implementing the transmission of security and privacy attributes between systems*

---

### Sample Match 17: `MAS-14.1.7` ⟷ `NIST-MP-7`

* **Semantic Relation**: `EQUIVALENT`
* **Assurance Coverage**: `FULL_COVERAGE` (Confidence: `0.90` | Dense Sim: `0.60`)
* **Retrieval Trace**: RRF: 0.0309 (Dense Sim: 0.60, BM25: 32.16)
* **Defensible Rationale**: Shared domain concepts (access) with token overlap ratio of 0.27.

> **MAS TRM Clause [MAS-14.1.7]**:
> *The Financial Institution must disallow rooted or jailbroken mobile devices from accessing the Financial Institution’s mobile applications to perform financial transactions unless the application is secured within a sandbox or container that insulates it from tampering and interception by malware.*

> **NIST SP 800-53 Control [NIST-MP-7 - Media Use]**:
> *{{ insert: param, mp-07_odp.02 }} the use of {{ insert: param, mp-07_odp.01 }} on {{ insert: param, mp-07_odp.03 }} using {{ insert: param, mp-07_odp.04 }} ; and
Prohibit the use of portable storage devices in organizational systems when such devices have no identifiable owner.
System media includes both digital and non-digital media. Digital media includes diskettes, magnetic tapes, flash drives, compact discs, digital versatile discs, and removable hard disk drives. Non-digital media includes paper and microfilm. Media use protections also apply to mobile devices with information storage capabilities. In contrast to [MP-2](#mp-2) , which restricts user access to media, MP-7 restricts the use of certain types of media on systems, for example, restricting or prohibiting the use of flash drives or external hard disk drives. Organizations use technical and nontechnical controls to restrict the use of system media. Organizations may restrict the use of portable storage devices, for example, by using physical cages on workstations to prohibit access to certain external ports or disabling or removing the ability to insert, read, or write to such devices. Organizations may also limit the use of portable storage devices to only approved devices, including devices provided by the organization, devices provided by other approved organizations, and devices that are not personally owned. Finally, organizations may restrict the use of portable storage devices based on the type of device, such as by prohibiting the use of writeable, portable storage devices and implementing this restriction by disabling or removing the capability to write to such devices. Requiring identifiable owners for storage devices reduces the risk of using such devices by allowing organizations to assign responsibility for addressing known vulnerabilities in the devices.
the use of {{ insert: param, mp-07_odp.01 }} is {{ insert: param, mp-07_odp.02 }} on {{ insert: param, mp-07_odp.03 }} using {{ insert: param, mp-07_odp.04 }};
the use of portable storage devices in organizational systems is prohibited when such devices have no identifiable owner.
System media protection policy

system use policy

procedures addressing media usage restrictions

rules of behavior

system design documentation

system configuration settings and associated documentation

audit records

system security plan

other relevant documents or records
Organizational personnel with system media use responsibilities

organizational personnel with information security responsibilities

system/network administrators
Organizational processes for media use

mechanisms restricting or prohibiting the use of system media on systems or system components*

---

### Sample Match 18: `MAS-14.2.11.b` ⟷ `NIST-IA-5`

* **Semantic Relation**: `EQUIVALENT`
* **Assurance Coverage**: `FULL_COVERAGE` (Confidence: `0.95` | Dense Sim: `0.60`)
* **Retrieval Trace**: RRF: 0.0393 (Dense Sim: 0.60, BM25: 31.91)
* **Defensible Rationale**: Shared domain concepts (mfa) with token overlap ratio of 0.53.

> **MAS TRM Clause [MAS-14.2.11.b]**:
> *The Financial Institution must implement a process and procedure to revoke and replace authentication credentials and mechanisms that have been compromised.*

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

### Sample Match 19: `MAS-14.3.1` ⟷ `NIST-CA-6`

* **Semantic Relation**: `SUPPORTS`
* **Assurance Coverage**: `NO_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.47`)
* **Retrieval Trace**: RRF: 0.0238 (Dense Sim: 0.47, BM25: 19.11)
* **Defensible Rationale**: Resource allocation and budgeting enable organizational security programs but do not satisfy technical operational mandates.

> **MAS TRM Clause [MAS-14.3.1]**:
> *The Financial Institution must implement real-time fraud monitoring systems to identify and block suspicious or fraudulent online transactions.*

> **NIST SP 800-53 Control [NIST-CA-6 - Authorization]**:
> *Assign a senior official as the authorizing official for the system;
Assign a senior official as the authorizing official for common controls available for inheritance by organizational systems;
Ensure that the authorizing official for the system, before commencing operations:
Accepts the use of common controls inherited by the system; and
Authorizes the system to operate;
Ensure that the authorizing official for common controls authorizes the use of those controls for inheritance by organizational systems;
Update the authorizations {{ insert: param, ca-06_odp }}.
Authorizations are official management decisions by senior officials to authorize operation of systems, authorize the use of common controls for inheritance by organizational systems, and explicitly accept the risk to organizational operations and assets, individuals, other organizations, and the Nation based on the implementation of agreed-upon controls. Authorizing officials provide budgetary oversight for organizational systems and common controls or assume responsibility for the mission and business functions supported by those systems or common controls. The authorization process is a federal responsibility, and therefore, authorizing officials must be federal employees. Authorizing officials are both responsible and accountable for security and privacy risks associated with the operation and use of organizational systems. Nonfederal organizations may have similar processes to authorize systems and senior officials that assume the authorization role and associated responsibilities.

Authorizing officials issue ongoing authorizations of systems based on evidence produced from implemented continuous monitoring programs. Robust continuous monitoring programs reduce the need for separate reauthorization processes. Through the employment of comprehensive continuous monitoring processes, the information contained in authorization packages (i.e., security and privacy plans, assessment reports, and plans of action and milestones) is updated on an ongoing basis. This provides authorizing officials, common control providers, and system owners with an up-to-date status of the security and privacy posture of their systems, controls, and operating environments. To reduce the cost of reauthorization, authorizing officials can leverage the results of continuous monitoring processes to the maximum extent possible as the basis for rendering reauthorization decisions.
a senior official is assigned as the authorizing official for the system;
a senior official is assigned as the authorizing official for common controls available for inheritance by organizational systems;
before commencing operations, the authorizing official for the system accepts the use of common controls inherited by the system;
before commencing operations, the authorizing official for the system authorizes the system to operate;
the authorizing official for common controls authorizes the use of those controls for inheritance by organizational systems;
the authorizations are updated {{ insert: param, ca-06_odp }}.
Assessment, authorization, and monitoring policy

procedures addressing authorization

system security plan, privacy plan, assessment report, plan of action and milestones

authorization statement

other relevant documents or records
Organizational personnel with authorization responsibilities

organizational personnel with information security and privacy responsibilities
Mechanisms that facilitate authorizations and updates*

---

### Sample Match 20: `MAS-15.1.3` ⟷ `NIST-PM-9`

* **Semantic Relation**: `SUPPORTS`
* **Assurance Coverage**: `NO_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.58`)
* **Retrieval Trace**: RRF: 0.0321 (Dense Sim: 0.58, BM25: 31.81)
* **Defensible Rationale**: Resource allocation and budgeting enable organizational security programs but do not satisfy technical operational mandates.

> **MAS TRM Clause [MAS-15.1.3]**:
> *The Financial Institution must set the frequency of IT audits to be commensurate with the criticality and risk posed by the IT information asset, function, or process.*

> **NIST SP 800-53 Control [NIST-PM-9 - Risk Management Strategy]**:
> *Develops a comprehensive strategy to manage:
Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and
Privacy risk to individuals resulting from the authorized processing of personally identifiable information;
Implement the risk management strategy consistently across the organization; and
Review and update the risk management strategy {{ insert: param, pm-09_odp }} or as required, to address organizational changes.
An organization-wide risk management strategy includes an expression of the security and privacy risk tolerance for the organization, security and privacy risk mitigation strategies, acceptable risk assessment methodologies, a process for evaluating security and privacy risk across the organization with respect to the organization’s risk tolerance, and approaches for monitoring risk over time. The senior accountable official for risk management (agency head or designated official) aligns information security management processes with strategic, operational, and budgetary planning processes. The risk executive function, led by the senior accountable official for risk management, can facilitate consistent application of the risk management strategy organization-wide. The risk management strategy can be informed by security and privacy risk-related inputs from other sources, both internal and external to the organization, to ensure that the strategy is broad-based and comprehensive. The supply chain risk management strategy described in [PM-30](#pm-30) can also provide useful inputs to the organization-wide risk management strategy.
a comprehensive strategy is developed to manage security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems;
a comprehensive strategy is developed to manage privacy risk to individuals resulting from the authorized processing of personally identifiable information;
the risk management strategy is implemented consistently across the organization;
the risk management strategy is reviewed and updated {{ insert: param, pm-09_odp }} or as required to address organizational changes.
Information security program plan

privacy program plan

risk management strategy

supply chain risk management strategy

procedures addressing the development, implementation, review, and update of the risk management strategy

risk assessment results relevant to the risk management strategy

other relevant documents or records
Organizational personnel with information security and privacy program planning and plan implementation responsibilities

organizational personnel responsible for the development, implementation, review, and update of the risk management strategy

organizational personnel with information security and privacy responsibilities
Organizational processes for the development, implementation, review, and update of the risk management strategy

mechanisms supporting the development, implementation, review, and update of the risk management strategy*

---

### Sample Match 21: `MAS-15.1.2.b` ⟷ `NIST-CA-6`

* **Semantic Relation**: `SUPPORTS`
* **Assurance Coverage**: `NO_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.51`)
* **Retrieval Trace**: RRF: 0.0246 (Dense Sim: 0.51, BM25: 18.29)
* **Defensible Rationale**: Resource allocation and budgeting enable organizational security programs but do not satisfy technical operational mandates.

> **MAS TRM Clause [MAS-15.1.2.b]**:
> *The Financial Institution must include all IT operations, functions, and processes within the auditable areas.*

> **NIST SP 800-53 Control [NIST-CA-6 - Authorization]**:
> *Assign a senior official as the authorizing official for the system;
Assign a senior official as the authorizing official for common controls available for inheritance by organizational systems;
Ensure that the authorizing official for the system, before commencing operations:
Accepts the use of common controls inherited by the system; and
Authorizes the system to operate;
Ensure that the authorizing official for common controls authorizes the use of those controls for inheritance by organizational systems;
Update the authorizations {{ insert: param, ca-06_odp }}.
Authorizations are official management decisions by senior officials to authorize operation of systems, authorize the use of common controls for inheritance by organizational systems, and explicitly accept the risk to organizational operations and assets, individuals, other organizations, and the Nation based on the implementation of agreed-upon controls. Authorizing officials provide budgetary oversight for organizational systems and common controls or assume responsibility for the mission and business functions supported by those systems or common controls. The authorization process is a federal responsibility, and therefore, authorizing officials must be federal employees. Authorizing officials are both responsible and accountable for security and privacy risks associated with the operation and use of organizational systems. Nonfederal organizations may have similar processes to authorize systems and senior officials that assume the authorization role and associated responsibilities.

Authorizing officials issue ongoing authorizations of systems based on evidence produced from implemented continuous monitoring programs. Robust continuous monitoring programs reduce the need for separate reauthorization processes. Through the employment of comprehensive continuous monitoring processes, the information contained in authorization packages (i.e., security and privacy plans, assessment reports, and plans of action and milestones) is updated on an ongoing basis. This provides authorizing officials, common control providers, and system owners with an up-to-date status of the security and privacy posture of their systems, controls, and operating environments. To reduce the cost of reauthorization, authorizing officials can leverage the results of continuous monitoring processes to the maximum extent possible as the basis for rendering reauthorization decisions.
a senior official is assigned as the authorizing official for the system;
a senior official is assigned as the authorizing official for common controls available for inheritance by organizational systems;
before commencing operations, the authorizing official for the system accepts the use of common controls inherited by the system;
before commencing operations, the authorizing official for the system authorizes the system to operate;
the authorizing official for common controls authorizes the use of those controls for inheritance by organizational systems;
the authorizations are updated {{ insert: param, ca-06_odp }}.
Assessment, authorization, and monitoring policy

procedures addressing authorization

system security plan, privacy plan, assessment report, plan of action and milestones

authorization statement

other relevant documents or records
Organizational personnel with authorization responsibilities

organizational personnel with information security and privacy responsibilities
Mechanisms that facilitate authorizations and updates*

---

### Sample Match 22: `MAS-15.1.3.a` ⟷ `NIST-PL-2`

* **Semantic Relation**: `EQUIVALENT`
* **Assurance Coverage**: `FULL_COVERAGE` (Confidence: `0.95` | Dense Sim: `0.54`)
* **Retrieval Trace**: RRF: 0.0268 (Dense Sim: 0.54, BM25: 27.61)
* **Defensible Rationale**: Shared domain concepts (audit, risk) with token overlap ratio of 0.43.

> **MAS TRM Clause [MAS-15.1.3.a]**:
> *The Financial Institution must set the frequency of IT audits commensurate with the criticality and risk posed by the IT information asset, function, or process.*

> **NIST SP 800-53 Control [NIST-PL-2 - System Security and Privacy Plans]**:
> *Develop security and privacy plans for the system that:
Are consistent with the organization’s enterprise architecture;
Explicitly define the constituent system components;
Describe the operational context of the system in terms of mission and business processes;
Identify the individuals that fulfill system roles and responsibilities;
Identify the information types processed, stored, and transmitted by the system;
Provide the security categorization of the system, including supporting rationale;
Describe any specific threats to the system that are of concern to the organization;
Provide the results of a privacy risk assessment for systems processing personally identifiable information;
Describe the operational environment for the system and any dependencies on or connections to other systems or system components;
Provide an overview of the security and privacy requirements for the system;
Identify any relevant control baselines or overlays, if applicable;
Describe the controls in place or planned for meeting the security and privacy requirements, including a rationale for any tailoring decisions;
Include risk determinations for security and privacy architecture and design decisions;
Include security- and privacy-related activities affecting the system that require planning and coordination with {{ insert: param, pl-02_odp.01 }} ; and
Are reviewed and approved by the authorizing official or designated representative prior to plan implementation.
Distribute copies of the plans and communicate subsequent changes to the plans to {{ insert: param, pl-02_odp.02 }};
Review the plans {{ insert: param, pl-02_odp.03 }};
Update the plans to address changes to the system and environment of operation or problems identified during plan implementation or control assessments; and
Protect the plans from unauthorized disclosure and modification.
System security and privacy plans are scoped to the system and system components within the defined authorization boundary and contain an overview of the security and privacy requirements for the system and the controls selected to satisfy the requirements. The plans describe the intended application of each selected control in the context of the system with a sufficient level of detail to correctly implement the control and to subsequently assess the effectiveness of the control. The control documentation describes how system-specific and hybrid controls are implemented and the plans and expectations regarding the functionality of the system. System security and privacy plans can also be used in the design and development of systems in support of life cycle-based security and privacy engineering processes. System security and privacy plans are living documents that are updated and adapted throughout the system development life cycle (e.g., during capability determination, analysis of alternatives, requests for proposal, and design reviews). [Section 2.1](#c3397cc9-83c6-4459-adb2-836739dc1b94) describes the different types of requirements that are relevant to organizations during the system development life cycle and the relationship between requirements and controls.

Organizations may develop a single, integrated security and privacy plan or maintain separate plans. Security and privacy plans relate security and privacy requirements to a set of controls and control enhancements. The plans describe how the controls and control enhancements meet the security and privacy requirements but do not provide detailed, technical descriptions of the design or implementation of the controls and control enhancements. Security and privacy plans contain sufficient information (including specifications of control parameter values for selection and assignment operations explicitly or by reference) to enable a design and implementation that is unambiguously compliant with the intent of the plans and subsequent determinations of risk to organizational operations and assets, individuals, other organizations, and the Nation if the plan is implemented.

Security and privacy plans need not be single documents. The plans can be a collection of various documents, including documents that already exist. Effective security and privacy plans make extensive use of references to policies, procedures, and additional documents, including design and implementation specifications where more detailed information can be obtained. The use of references helps reduce the documentation associated with security and privacy programs and maintains the security- and privacy-related information in other established management and operational areas, including enterprise architecture, system development life cycle, systems engineering, and acquisition. Security and privacy plans need not contain detailed contingency plan or incident response plan information but can instead provide—explicitly or by reference—sufficient information to define what needs to be accomplished by those plans.

Security- and privacy-related activities that may require coordination and planning with other individuals or groups within the organization include assessments, audits, inspections, hardware and software maintenance, acquisition and supply chain risk management, patch management, and contingency plan testing. Planning and coordination include emergency and nonemergency (i.e., planned or non-urgent unplanned) situations. The process defined by organizations to plan and coordinate security- and privacy-related activities can also be included in other documents, as appropriate.
a security plan for the system is developed that is consistent with the organization’s enterprise architecture;
a privacy plan for the system is developed that is consistent with the organization’s enterprise architecture;
a security plan for the system is developed that explicitly defines the constituent system components;
a privacy plan for the system is developed that explicitly defines the constituent system components;
a security plan for the system is developed that describes the operational context of the system in terms of mission and business processes;
a privacy plan for the system is developed that describes the operational context of the system in terms of mission and business processes;
a security plan for the system is developed that identifies the individuals that fulfill system roles and responsibilities;
a privacy plan for the system is developed that identifies the individuals that fulfill system roles and responsibilities;
a security plan for the system is developed that identifies the information types processed, stored, and transmitted by the system;
a privacy plan for the system is developed that identifies the information types processed, stored, and transmitted by the system;
a security plan for the system is developed that provides the security categorization of the system, including supporting rationale;
a privacy plan for the system is developed that provides the security categorization of the system, including supporting rationale;
a security plan for the system is developed that describes any specific threats to the system that are of concern to the organization;
a privacy plan for the system is developed that describes any specific threats to the system that are of concern to the organization;
a security plan for the system is developed that provides the results of a privacy risk assessment for systems processing personally identifiable information;
a privacy plan for the system is developed that provides the results of a privacy risk assessment for systems processing personally identifiable information;
a security plan for the system is developed that describes the operational environment for the system and any dependencies on or connections to other systems or system components;
a privacy plan for the system is developed that describes the operational environment for the system and any dependencies on or connections to other systems or system components;
a security plan for the system is developed that provides an overview of the security requirements for the system;
a privacy plan for the system is developed that provides an overview of the privacy requirements for the system;
a security plan for the system is developed that identifies any relevant control baselines or overlays, if applicable;
a privacy plan for the system is developed that identifies any relevant control baselines or overlays, if applicable;
a security plan for the system is developed that describes the controls in place or planned for meeting the security requirements, including rationale for any tailoring decisions;
a privacy plan for the system is developed that describes the controls in place or planned for meeting the privacy requirements, including rationale for any tailoring decisions;
a security plan for the system is developed that includes risk determinations for security architecture and design decisions;
a privacy plan for the system is developed that includes risk determinations for privacy architecture and design decisions;
a security plan for the system is developed that includes security-related activities affecting the system that require planning and coordination with {{ insert: param, pl-02_odp.01 }};
a privacy plan for the system is developed that includes privacy-related activities affecting the system that require planning and coordination with {{ insert: param, pl-02_odp.01 }};
a security plan for the system is developed that is reviewed and approved by the authorizing official or designated representative prior to plan implementation;
a privacy plan for the system is developed that is reviewed and approved by the authorizing official or designated representative prior to plan implementation.
copies of the plans are distributed to {{ insert: param, pl-02_odp.02 }};
subsequent changes to the plans are communicated to {{ insert: param, pl-02_odp.02 }};
plans are reviewed {{ insert: param, pl-02_odp.03 }};
plans are updated to address changes to the system and environment of operations;
plans are updated to address problems identified during the plan implementation;
plans are updated to address problems identified during control assessments;
plans are protected from unauthorized disclosure;
plans are protected from unauthorized modification.
Security and privacy planning policy

procedures addressing system security and privacy plan development and implementation

procedures addressing security and privacy plan reviews and updates

enterprise architecture documentation

system security plan

privacy plan

records of system security and privacy plan reviews and updates

security and privacy architecture and design documentation

risk assessments

risk assessment results

control assessment documentation

other relevant documents or records
Organizational personnel with system security and privacy planning and plan implementation responsibilities

system developers

organizational personnel with information security and privacy responsibilities
Organizational processes for system security and privacy plan development, review, update, and approval

mechanisms supporting the system security and privacy plan*

---

### Sample Match 23: `MAS-Annex B.B.1.a` ⟷ `NIST-PM-20`

* **Semantic Relation**: `EQUIVALENT`
* **Assurance Coverage**: `FULL_COVERAGE` (Confidence: `0.92` | Dense Sim: `0.58`)
* **Retrieval Trace**: RRF: 0.0305 (Dense Sim: 0.58, BM25: 16.33)
* **Defensible Rationale**: Shared domain concepts (access) with token overlap ratio of 0.33.

> **MAS TRM Clause [MAS-Annex B.B.1.a]**:
> *The Financial Institution must implement data loss prevention measures on personal computing or mobile devices used to access its information assets.*

> **NIST SP 800-53 Control [NIST-PM-20 - Dissemination of Privacy Program Information]**:
> *Maintain a central resource webpage on the organization’s principal public website that serves as a central source of information about the organization’s privacy program and that:
Ensures that the public has access to information about organizational privacy activities and can communicate with its senior agency official for privacy;
Ensures that organizational privacy practices and reports are publicly available; and
Employs publicly facing email addresses and/or phone lines to enable the public to provide feedback and/or direct questions to privacy offices regarding privacy practices.
For federal agencies, the webpage is located at www.[agency].gov/privacy. Federal agencies include public privacy impact assessments, system of records notices, computer matching notices and agreements, [PRIVACT](#18e71fec-c6fd-475a-925a-5d8495cf8455) exemption and implementation rules, privacy reports, privacy policies, instructions for individuals making an access or amendment request, email addresses for questions/complaints, blogs, and periodic publications.
a central resource webpage is maintained on the organization’s principal public website;
the webpage serves as a central source of information about the organization’s privacy program;
the webpage ensures that the public has access to information about organizational privacy activities;
the webpage ensures that the public can communicate with its senior agency official for privacy;
the webpage ensures that organizational privacy practices are publicly available;
the webpage ensures that organizational privacy reports are publicly available;
the webpage employs publicly facing email addresses and/or phone numbers to enable the public to provide feedback and/or direct questions to privacy offices regarding privacy practices.
Public website

publicly posted privacy program documents, including policies, procedures, plans, and reports

position description of the senior agency official for privacy

public privacy notices, including Federal Register notices

privacy impact assessments

privacy risk assessments

Privacy Act statements and system of records notices

computer matching agreements and notices

other relevant documents or records
Organizational personnel with privacy program information dissemination responsibilities

organizational personnel with privacy responsibilities
Location, access, availability, and functionality of privacy resource webpage*

---

### Sample Match 24: `MAS-C.1.1` ⟷ `NIST-AC-19`

* **Semantic Relation**: `EQUIVALENT`
* **Assurance Coverage**: `FULL_COVERAGE` (Confidence: `0.95` | Dense Sim: `0.59`)
* **Retrieval Trace**: RRF: 0.0410 (Dense Sim: 0.59, BM25: 36.66)
* **Defensible Rationale**: Shared domain concepts (risk) with token overlap ratio of 0.47.

> **MAS TRM Clause [MAS-C.1.1]**:
> *The Financial Institution must prevent storing or caching data in the mobile application to mitigate the risk of data compromise on the device.*

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

### Sample Match 25: `MAS-C.1.7` ⟷ `NIST-SC-12`

* **Semantic Relation**: `EQUIVALENT`
* **Assurance Coverage**: `FULL_COVERAGE` (Confidence: `0.89` | Dense Sim: `0.63`)
* **Retrieval Trace**: RRF: 0.0337 (Dense Sim: 0.63, BM25: 12.62)
* **Defensible Rationale**: Shared domain concepts (encryption) with token overlap ratio of 0.27.

> **MAS TRM Clause [MAS-C.1.7]**:
> *The Financial Institution must implement certificate or public key pinning to protect against man-in-the-middle attacks.*

> **NIST SP 800-53 Control [NIST-SC-12 - Cryptographic Key Establishment and Management]**:
> *Establish and manage cryptographic keys when cryptography is employed within the system in accordance with the following key management requirements: {{ insert: param, sc-12_odp }}.
Cryptographic key management and establishment can be performed using manual procedures or automated mechanisms with supporting manual procedures. Organizations define key management requirements in accordance with applicable laws, executive orders, directives, regulations, policies, standards, and guidelines and specify appropriate options, parameters, and levels. Organizations manage trust stores to ensure that only approved trust anchors are part of such trust stores. This includes certificates with visibility external to organizational systems and certificates related to the internal operations of systems. [NIST CMVP](#1acdc775-aafb-4d11-9341-dc6a822e9d38) and [NIST CAVP](#84dc1b0c-acb7-4269-84c4-00dbabacd78c) provide additional information on validated cryptographic modules and algorithms that can be used in cryptographic key management and establishment.
cryptographic keys are established when cryptography is employed within the system in accordance with {{ insert: param, sc-12_odp }};
cryptographic keys are managed when cryptography is employed within the system in accordance with {{ insert: param, sc-12_odp }}.
System and communications protection policy

procedures addressing cryptographic key establishment and management

system design documentation

cryptographic mechanisms

system configuration settings and associated documentation

system audit records

system security plan

other relevant documents or records
System/network administrators

organizational personnel with information security responsibilities

organizational personnel with responsibilities for cryptographic key establishment and/or management
Mechanisms supporting and/or implementing cryptographic key establishment and management*

---

## Section C: Unmatched MAS Obligations (True Regulatory Gaps)

Total unmapped clauses: **15** (17.6%)

### Unmatched Clause 1: `MAS-13.4.1`

> **MAS TRM Statement**:
> *The Financial Institution must perform an adversarial attack simulation exercise to test and validate the effectiveness of its cyber defence and response plan against prevalent cyber threats.*

* **Audit Analysis**: Evaluated against top 15 hybrid candidates. All candidates rejected by 2D Dual-Judge as `NONE` or below confidence threshold (0.70).

---

### Unmatched Clause 2: `MAS-13.5.2.a`

> **MAS TRM Statement**:
> *The Financial Institution must use threat intelligence relevant to its IT environment to identify threat actors most likely to pose a threat.*

* **Audit Analysis**: Evaluated against top 15 hybrid candidates. All candidates rejected by 2D Dual-Judge as `NONE` or below confidence threshold (0.70).

---

### Unmatched Clause 3: `MAS-13.5.2.b`

> **MAS TRM Statement**:
> *The Financial Institution must identify the tactics, techniques, and procedures most likely to be used in such attacks.*

* **Audit Analysis**: Evaluated against top 15 hybrid candidates. All candidates rejected by 2D Dual-Judge as `NONE` or below confidence threshold (0.70).

---

### Unmatched Clause 4: `MAS-14.1.2`

> **MAS TRM Statement**:
> *The Financial Institution must secure its communications channels to protect customer data.*

* **Audit Analysis**: Evaluated against top 15 hybrid candidates. All candidates rejected by 2D Dual-Judge as `NONE` or below confidence threshold (0.70).

---

### Unmatched Clause 5: `MAS-14.1.3`

> **MAS TRM Statement**:
> *The Financial Institution must implement adequate measures to minimize exposure of its online financial services to common attack vectors such as code injection attacks, cross-site scripting, man-in-the-middle attacks, DNS hijacking, DDoS, malware, and spoofing attacks.*

* **Audit Analysis**: Evaluated against top 15 hybrid candidates. All candidates rejected by 2D Dual-Judge as `NONE` or below confidence threshold (0.70).

---

### Unmatched Clause 6: `MAS-14.1.6.a`

> **MAS TRM Statement**:
> *The Financial Institution must actively monitor for phishing campaigns targeting the Financial Institution and its customers.*

* **Audit Analysis**: Evaluated against top 15 hybrid candidates. All candidates rejected by 2D Dual-Judge as `NONE` or below confidence threshold (0.70).

---

### Unmatched Clause 7: `MAS-14.3.3.a`

> **MAS TRM Statement**:
> *The Financial Institution must notify customers of suspicious activities or funds transfers exceeding a threshold defined by the Financial Institution or the customers.*

* **Audit Analysis**: Evaluated against top 15 hybrid candidates. All candidates rejected by 2D Dual-Judge as `NONE` or below confidence threshold (0.70).

---

### Unmatched Clause 8: `MAS-14.4.1.a`

> **MAS TRM Statement**:
> *The Financial Institution must inform customers of security best practices to adopt when using online financial services.*

* **Audit Analysis**: Evaluated against top 15 hybrid candidates. All candidates rejected by 2D Dual-Judge as `NONE` or below confidence threshold (0.70).

---

### Unmatched Clause 9: `MAS-14.4.2`

> **MAS TRM Statement**:
> *The Financial Institution must alert customers on a timely basis to new cyber threats so they can take precautionary measures.*

* **Audit Analysis**: Evaluated against top 15 hybrid candidates. All candidates rejected by 2D Dual-Judge as `NONE` or below confidence threshold (0.70).

---

### Unmatched Clause 10: `MAS-14.4.3`

> **MAS TRM Statement**:
> *The Financial Institution must advise customers on means to detect unauthorized transactions and to report security issues, suspicious activities, or suspected fraud promptly.*

* **Audit Analysis**: Evaluated against top 15 hybrid candidates. All candidates rejected by 2D Dual-Judge as `NONE` or below confidence threshold (0.70).

---

### Unmatched Clause 11: `MAS-5.1.3`

> **MAS TRM Statement**:
> *The Financial Institution must enable strict security policies within the virtual environment to restrict the copying and use of peripheral devices and prevent data leakage.*

* **Audit Analysis**: Evaluated against top 15 hybrid candidates. All candidates rejected by 2D Dual-Judge as `NONE` or below confidence threshold (0.70).

---

### Unmatched Clause 12: `MAS-C.1.2`

> **MAS TRM Statement**:
> *The Financial Institution must store data in a protected and trusted area of the mobile device.*

* **Audit Analysis**: Evaluated against top 15 hybrid candidates. All candidates rejected by 2D Dual-Judge as `NONE` or below confidence threshold (0.70).

---

### Unmatched Clause 13: `MAS-C.1.4`

> **MAS TRM Statement**:
> *The Financial Institution must implement anti-hooking or anti-tampering mechanisms to prevent the injection of malicious code that could alter or monitor application behaviour at runtime.*

* **Audit Analysis**: Evaluated against top 15 hybrid candidates. All candidates rejected by 2D Dual-Judge as `NONE` or below confidence threshold (0.70).

---

### Unmatched Clause 14: `MAS-C.1.5`

> **MAS TRM Statement**:
> *The Financial Institution must implement appropriate application integrity checks to verify the authenticity and integrity of the application.*

* **Audit Analysis**: Evaluated against top 15 hybrid candidates. All candidates rejected by 2D Dual-Judge as `NONE` or below confidence threshold (0.70).

---

### Unmatched Clause 15: `MAS-C.1.6`

> **MAS TRM Statement**:
> *The Financial Institution must implement code obfuscation techniques to prevent reverse engineering of the mobile application.*

* **Audit Analysis**: Evaluated against top 15 hybrid candidates. All candidates rejected by 2D Dual-Judge as `NONE` or below confidence threshold (0.70).

---

## Section D: 5 Sample MAS Obligations with Multiple Matches (1-to-N Mapping Clusters)

### Cluster 1: `MAS-1.3.a` maps to 15 NIST Controls

> **MAS TRM Statement [MAS-1.3.a]**:
> *The Financial Institution must evaluate its exposure to technology risks.*

#### Control 1: `NIST-RA-8` (Privacy Impact Assessments)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *Conduct privacy impact assessments for systems, programs, or other activities before:
Developing or procuring information technology that processes personally identifiable information; and
Initiating a new collection of personally identifiable inform...*

#### Control 2: `NIST-RA-6` (Technical Surveillance Countermeasures Survey)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Employ a technical surveillance countermeasures survey at {{ insert: param, ra-06_odp.01 }} {{ insert: param, ra-06_odp.02 }}.
A technical surveillance countermeasures survey is a service provided by qualified personnel to detect the presence of tech...*

#### Control 3: `NIST-SR-2` (Supply Chain Risk Management Plan)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Develop a plan for managing supply chain risks associated with the research and development, design, manufacturing, acquisition, delivery, integration, operations and maintenance, and disposal of the following systems, system components or system ser...*

#### Control 4: `NIST-RA-5` (Vulnerability Monitoring and Scanning)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;
Employ vulnerability monitoring tools and techniques...*

#### Control 5: `NIST-SI-20` (Tainting)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *Embed data or capabilities in the following systems or system components to determine if organizational data has been exfiltrated or improperly removed from the organization: {{ insert: param, si-20_odp }}.
Many cyber-attacks target organizational in...*

#### Control 6: `NIST-SR-6` (Supplier Assessments and Reviews)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Assess and review the supply chain-related risks associated with suppliers or contractors and the system, system component, or system service they provide {{ insert: param, sr-06_odp }}.
An assessment and review of supplier risk includes security and...*

#### Control 7: `NIST-RA-3` (Risk Assessment)
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as EQUIVALENT with FULL_COVERAGE assurance level.
> *Conduct a risk assessment, including:
Identifying threats to and vulnerabilities in the system;
Determining the likelihood and magnitude of harm from unauthorized access, use, disclosure, disruption, modification, or destruction of the system, the in...*

#### Control 8: `NIST-PM-30` (Supply Chain Risk Management Strategy)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Develop an organization-wide strategy for managing supply chain risks associated with the development, acquisition, maintenance, and disposal of systems, system components, and system services;
Implement the supply chain risk management strategy cons...*

#### Control 9: `NIST-CM-4` (Impact Analyses)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Analyze changes to the system to determine potential security and privacy impacts prior to change implementation.
Organizational personnel with security or privacy responsibilities conduct impact analyses. Individuals conducting impact analyses posse...*

#### Control 10: `NIST-PM-4` (Plan of Action and Milestones Process)
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUPERSET_OF with PARTIAL_COVERAGE assurance level.
> *Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:
Are developed and maintained;
Document the remedial information ...*

#### Control 11: `NIST-PM-7` (Enterprise Architecture)
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUPERSET_OF with PARTIAL_COVERAGE assurance level.
> *Develop and maintain an enterprise architecture with consideration for information security, privacy, and the resulting risk to organizational operations and assets, individuals, other organizations, and the Nation.
The integration of security and pr...*

#### Control 12: `NIST-SC-8` (Transmission Confidentiality and Integrity)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *Protect the {{ insert: param, sc-08_odp }} of transmitted information.
Protecting the confidentiality and integrity of transmitted information applies to internal and external networks as well as any system components that can transmit information, i...*

#### Control 13: `NIST-SA-2` (Allocation of Resources)
- **Semantic Relation**: `SUPPORTS` | **Assurance Coverage**: `NO_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUPPORTS with NO_COVERAGE assurance level.
> *Determine the high-level information security and privacy requirements for the system or system service in mission and business process planning;
Determine, document, and allocate the resources required to protect the system or system service as part...*

#### Control 14: `NIST-PT-4` (Consent)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *Implement {{ insert: param, pt-04_odp }} for individuals to consent to the processing of their personally identifiable information prior to its collection that facilitate individuals’ informed decision-making.
Consent allows individuals to participat...*

#### Control 15: `NIST-SI-19` (De-identification)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *Remove the following elements of personally identifiable information from datasets: {{ insert: param, si-19_odp.01 }} ; and
Evaluate {{ insert: param, si-19_odp.02 }} for effectiveness of de-identification.
De-identification is the general term for t...*

---

### Cluster 2: `MAS-1.3.b` maps to 15 NIST Controls

> **MAS TRM Statement [MAS-1.3.b]**:
> *The Financial Institution must implement a robust risk management framework to ensure IT and cyber resilience.*

#### Control 1: `NIST-SA-24` (Design For Cyber Resiliency)
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUPERSET_OF with PARTIAL_COVERAGE assurance level.
> *Design organizational systems, system components, or system services to achieve cyber resiliency by:
Defining the following cyber resiliency goals: {{ insert: param, sa-24_odp.01 }}.
Defining the following cyber resiliency objectives: {{ insert: para...*

#### Control 2: `NIST-PM-9` (Risk Management Strategy)
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUPERSET_OF with PARTIAL_COVERAGE assurance level.
> *Develops a comprehensive strategy to manage:
Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and
Privacy risk to individuals resu...*

#### Control 3: `NIST-CP-2` (Contingency Plan)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Develop a contingency plan for the system that:
Identifies essential mission and business functions and associated contingency requirements;
Provides recovery objectives, restoration priorities, and metrics;
Addresses contingency roles, responsibilit...*

#### Control 4: `NIST-PM-4` (Plan of Action and Milestones Process)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:
Are developed and maintained;
Document the remedial information ...*

#### Control 5: `NIST-PM-7` (Enterprise Architecture)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Develop and maintain an enterprise architecture with consideration for information security, privacy, and the resulting risk to organizational operations and assets, individuals, other organizations, and the Nation.
The integration of security and pr...*

#### Control 6: `NIST-RA-3` (Risk Assessment)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Conduct a risk assessment, including:
Identifying threats to and vulnerabilities in the system;
Determining the likelihood and magnitude of harm from unauthorized access, use, disclosure, disruption, modification, or destruction of the system, the in...*

#### Control 7: `NIST-PM-14` (Testing, Training, and Monitoring)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Implement a process for ensuring that organizational plans for conducting security and privacy testing, training, and monitoring activities associated with organizational systems:
Are developed and maintained; and
Continue to be executed; and
Review ...*

#### Control 8: `NIST-PM-29` (Risk Management Program Leadership Roles)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Appoint a Senior Accountable Official for Risk Management to align organizational information security and privacy management processes with strategic, operational, and budgetary planning processes; and
Establish a Risk Executive (function) to view a...*

#### Control 9: `NIST-RA-9` (Criticality Analysis)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Identify critical system components and functions by performing a criticality analysis for {{ insert: param, ra-09_odp.01 }} at {{ insert: param, ra-09_odp.02 }}.
Not all system components, functions, or services necessarily require significant prote...*

#### Control 10: `NIST-RA-5` (Vulnerability Monitoring and Scanning)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;
Employ vulnerability monitoring tools and techniques...*

#### Control 11: `NIST-CP-11` (Alternate Communications Protocols)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Provide the capability to employ {{ insert: param, cp-11_odp }} in support of maintaining continuity of operations.
Contingency plans and the contingency training or testing associated with those plans incorporate an alternate communications protocol...*

#### Control 12: `NIST-PL-8` (Security and Privacy Architectures)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Develop security and privacy architectures for the system that:
Describe the requirements and approach to be taken for protecting the confidentiality, integrity, and availability of organizational information;
Describe the requirements and approach t...*

#### Control 13: `NIST-RA-7` (Risk Response)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Respond to findings from security and privacy assessments, monitoring, and audits in accordance with organizational risk tolerance.
Organizations have many options for responding to risk including mitigating risk by implementing new controls or stren...*

#### Control 14: `NIST-SC-8` (Transmission Confidentiality and Integrity)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Protect the {{ insert: param, sc-08_odp }} of transmitted information.
Protecting the confidentiality and integrity of transmitted information applies to internal and external networks as well as any system components that can transmit information, i...*

#### Control 15: `NIST-SA-3` (System Development Life Cycle)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Acquire, develop, and manage the system using {{ insert: param, sa-03_odp }} that incorporates information security and privacy considerations;
Define and document information security and privacy roles and responsibilities throughout the system deve...*

---

### Cluster 3: `MAS-1.4(a).1` maps to 14 NIST Controls

> **MAS TRM Statement [MAS-1.4(a).1]**:
> *The Board of Directors and Senior Management must cultivate a strong risk culture.*

#### Control 1: `NIST-PM-29` (Risk Management Program Leadership Roles)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Appoint a Senior Accountable Official for Risk Management to align organizational information security and privacy management processes with strategic, operational, and budgetary planning processes; and
Establish a Risk Executive (function) to view a...*

#### Control 2: `NIST-PM-9` (Risk Management Strategy)
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUPERSET_OF with PARTIAL_COVERAGE assurance level.
> *Develops a comprehensive strategy to manage:
Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and
Privacy risk to individuals resu...*

#### Control 3: `NIST-PM-19` (Privacy Program Leadership Role)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Appoint a senior agency official for privacy with the authority, mission, accountability, and resources to coordinate, develop, and implement, applicable privacy requirements and manage privacy risks through the organization-wide privacy program.
The...*

#### Control 4: `NIST-PM-28` (Risk Framing)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Identify and document:
Assumptions affecting risk assessments, risk responses, and risk monitoring;
Constraints affecting risk assessments, risk responses, and risk monitoring;
Priorities and trade-offs considered by the organization for managing ris...*

#### Control 5: `NIST-CA-6` (Authorization)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *Assign a senior official as the authorizing official for the system;
Assign a senior official as the authorizing official for common controls available for inheritance by organizational systems;
Ensure that the authorizing official for the system, be...*

#### Control 6: `NIST-PM-4` (Plan of Action and Milestones Process)
- **Semantic Relation**: `SUPPORTS` | **Assurance Coverage**: `NO_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUPPORTS with NO_COVERAGE assurance level.
> *Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:
Are developed and maintained;
Document the remedial information ...*

#### Control 7: `NIST-PM-2` (Information Security Program Leadership Role)
- **Semantic Relation**: `SUPPORTS` | **Assurance Coverage**: `NO_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUPPORTS with NO_COVERAGE assurance level.
> *Appoint a senior agency information security officer with the mission and resources to coordinate, develop, implement, and maintain an organization-wide information security program.
The senior agency information security officer is an organizational...*

#### Control 8: `NIST-SA-3` (System Development Life Cycle)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *Acquire, develop, and manage the system using {{ insert: param, sa-03_odp }} that incorporates information security and privacy considerations;
Define and document information security and privacy roles and responsibilities throughout the system deve...*

#### Control 9: `NIST-PM-30` (Supply Chain Risk Management Strategy)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *Develop an organization-wide strategy for managing supply chain risks associated with the development, acquisition, maintenance, and disposal of systems, system components, and system services;
Implement the supply chain risk management strategy cons...*

#### Control 10: `NIST-PM-14` (Testing, Training, and Monitoring)
- **Semantic Relation**: `SUPPORTS` | **Assurance Coverage**: `NO_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUPPORTS with NO_COVERAGE assurance level.
> *Implement a process for ensuring that organizational plans for conducting security and privacy testing, training, and monitoring activities associated with organizational systems:
Are developed and maintained; and
Continue to be executed; and
Review ...*

#### Control 11: `NIST-PM-12` (Insider Threat Program)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *Implement an insider threat program that includes a cross-discipline insider threat incident handling team.
Organizations that handle classified information are required, under Executive Order 13587 [EO 13587](#0af071a6-cf8e-48ee-8c82-fe91efa20f94) a...*

#### Control 12: `NIST-PM-31` (Continuous Monitoring Strategy)
- **Semantic Relation**: `SUPPORTS` | **Assurance Coverage**: `NO_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUPPORTS with NO_COVERAGE assurance level.
> *Develop an organization-wide continuous monitoring strategy and implement continuous monitoring programs that include:
Establishing the following organization-wide metrics to be monitored: {{ insert: param, pm-31_odp.01 }};
Establishing {{ insert: pa...*

#### Control 13: `NIST-PS-2` (Position Risk Designation)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *Assign a risk designation to all organizational positions;
Establish screening criteria for individuals filling those positions; and
Review and update position risk designations {{ insert: param, ps-02_odp }}.
Position risk designations reflect Offic...*

#### Control 14: `NIST-SR-2` (Supply Chain Risk Management Plan)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *Develop a plan for managing supply chain risks associated with the research and development, design, manufacturing, acquisition, delivery, integration, operations and maintenance, and disposal of the following systems, system components or system ser...*

---

### Cluster 4: `MAS-1.4(a).2` maps to 12 NIST Controls

> **MAS TRM Statement [MAS-1.4(a).2]**:
> *The Board of Directors and Senior Management must establish a sound and robust technology risk management framework.*

#### Control 1: `NIST-PM-29` (Risk Management Program Leadership Roles)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Appoint a Senior Accountable Official for Risk Management to align organizational information security and privacy management processes with strategic, operational, and budgetary planning processes; and
Establish a Risk Executive (function) to view a...*

#### Control 2: `NIST-PM-9` (Risk Management Strategy)
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as EQUIVALENT with FULL_COVERAGE assurance level.
> *Develops a comprehensive strategy to manage:
Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and
Privacy risk to individuals resu...*

#### Control 3: `NIST-RA-3` (Risk Assessment)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Conduct a risk assessment, including:
Identifying threats to and vulnerabilities in the system;
Determining the likelihood and magnitude of harm from unauthorized access, use, disclosure, disruption, modification, or destruction of the system, the in...*

#### Control 4: `NIST-SR-2` (Supply Chain Risk Management Plan)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Develop a plan for managing supply chain risks associated with the research and development, design, manufacturing, acquisition, delivery, integration, operations and maintenance, and disposal of the following systems, system components or system ser...*

#### Control 5: `NIST-PM-23` (Data Governance Body)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Establish a Data Governance Body consisting of {{ insert: param, pm-23_odp.01 }} with {{ insert: param, pm-23_odp.02 }}.
A Data Governance Body can help ensure that the organization has coherent policies and the ability to balance the utility of data...*

#### Control 6: `NIST-PM-7` (Enterprise Architecture)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Develop and maintain an enterprise architecture with consideration for information security, privacy, and the resulting risk to organizational operations and assets, individuals, other organizations, and the Nation.
The integration of security and pr...*

#### Control 7: `NIST-PM-28` (Risk Framing)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Identify and document:
Assumptions affecting risk assessments, risk responses, and risk monitoring;
Constraints affecting risk assessments, risk responses, and risk monitoring;
Priorities and trade-offs considered by the organization for managing ris...*

#### Control 8: `NIST-PM-31` (Continuous Monitoring Strategy)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Develop an organization-wide continuous monitoring strategy and implement continuous monitoring programs that include:
Establishing the following organization-wide metrics to be monitored: {{ insert: param, pm-31_odp.01 }};
Establishing {{ insert: pa...*

#### Control 9: `NIST-PM-1` (Information Security Program Plan)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Develop and disseminate an organization-wide information security program plan that:
Provides an overview of the requirements for the security program and a description of the security program management controls and common controls in place or plann...*

#### Control 10: `NIST-PM-4` (Plan of Action and Milestones Process)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:
Are developed and maintained;
Document the remedial information ...*

#### Control 11: `NIST-PM-14` (Testing, Training, and Monitoring)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Implement a process for ensuring that organizational plans for conducting security and privacy testing, training, and monitoring activities associated with organizational systems:
Are developed and maintained; and
Continue to be executed; and
Review ...*

#### Control 12: `NIST-SR-3` (Supply Chain Controls and Processes)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: LLM Cross-Framework Semantic Evaluation
> *Establish a process or processes to identify and address weaknesses or deficiencies in the supply chain elements and processes of {{ insert: param, sr-03_odp.01 }} in coordination with {{ insert: param, sr-03_odp.02 }};
Employ the following controls ...*

---

### Cluster 5: `MAS-1.4(b).1` maps to 15 NIST Controls

> **MAS TRM Statement [MAS-1.4(b).1]**:
> *The Financial Institution must adopt a defence-in-depth approach to strengthen cyber resilience.*

#### Control 1: `NIST-SA-24` (Design For Cyber Resiliency)
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as EQUIVALENT with FULL_COVERAGE assurance level.
> *Design organizational systems, system components, or system services to achieve cyber resiliency by:
Defining the following cyber resiliency goals: {{ insert: param, sa-24_odp.01 }}.
Defining the following cyber resiliency objectives: {{ insert: para...*

#### Control 2: `NIST-RA-10` (Threat Hunting)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Establish and maintain a cyber threat hunting capability to:
Search for indicators of compromise in organizational systems; and
Detect, track, and disrupt threats that evade existing controls; and
Employ the threat hunting capability {{ insert: param...*

#### Control 3: `NIST-PL-8` (Security and Privacy Architectures)
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUPERSET_OF with PARTIAL_COVERAGE assurance level.
> *Develop security and privacy architectures for the system that:
Describe the requirements and approach to be taken for protecting the confidentiality, integrity, and availability of organizational information;
Describe the requirements and approach t...*

#### Control 4: `NIST-CP-11` (Alternate Communications Protocols)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Provide the capability to employ {{ insert: param, cp-11_odp }} in support of maintaining continuity of operations.
Contingency plans and the contingency training or testing associated with those plans incorporate an alternate communications protocol...*

#### Control 5: `NIST-CP-2` (Contingency Plan)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Develop a contingency plan for the system that:
Identifies essential mission and business functions and associated contingency requirements;
Provides recovery objectives, restoration priorities, and metrics;
Addresses contingency roles, responsibilit...*

#### Control 6: `NIST-IR-8` (Incident Response Plan)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Develop an incident response plan that:
Provides the organization with a roadmap for implementing its incident response capability;
Describes the structure and organization of the incident response capability;
Provides a high-level approach for how t...*

#### Control 7: `NIST-PM-4` (Plan of Action and Milestones Process)
- **Semantic Relation**: `SUPPORTS` | **Assurance Coverage**: `NO_COVERAGE` (Conf: `0.85`)
- **Rationale**: LLM Cross-Framework Semantic Evaluation
> *Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:
Are developed and maintained;
Document the remedial information ...*

#### Control 8: `NIST-SI-20` (Tainting)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Embed data or capabilities in the following systems or system components to determine if organizational data has been exfiltrated or improperly removed from the organization: {{ insert: param, si-20_odp }}.
Many cyber-attacks target organizational in...*

#### Control 9: `NIST-PL-2` (System Security and Privacy Plans)
- **Semantic Relation**: `SUPPORTS` | **Assurance Coverage**: `NO_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUPPORTS with NO_COVERAGE assurance level.
> *Develop security and privacy plans for the system that:
Are consistent with the organization’s enterprise architecture;
Explicitly define the constituent system components;
Describe the operational context of the system in terms of mission and busine...*

#### Control 10: `NIST-RA-9` (Criticality Analysis)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Identify critical system components and functions by performing a criticality analysis for {{ insert: param, ra-09_odp.01 }} at {{ insert: param, ra-09_odp.02 }}.
Not all system components, functions, or services necessarily require significant prote...*

#### Control 11: `NIST-PM-9` (Risk Management Strategy)
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUPERSET_OF with PARTIAL_COVERAGE assurance level.
> *Develops a comprehensive strategy to manage:
Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and
Privacy risk to individuals resu...*

#### Control 12: `NIST-RA-5` (Vulnerability Monitoring and Scanning)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;
Employ vulnerability monitoring tools and techniques...*

#### Control 13: `NIST-RA-7` (Risk Response)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *Respond to findings from security and privacy assessments, monitoring, and audits in accordance with organizational risk tolerance.
Organizations have many options for responding to risk including mitigating risk by implementing new controls or stren...*

#### Control 14: `NIST-IR-9` (Information Spillage Response)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Respond to information spills by:
Assigning {{ insert: param, ir-09_odp.01 }} with responsibility for responding to information spills;
Identifying the specific information involved in the system contamination;
Alerting {{ insert: param, ir-09_odp.02...*

#### Control 15: `NIST-CA-7` (Continuous Monitoring)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *Develop a system-level continuous monitoring strategy and implement continuous monitoring in accordance with the organization-level continuous monitoring strategy that includes:
Establishing the following system-level metrics to be monitored: {{ inse...*

---

## Section E: 5 Sample NIST Controls with Multiple Matches (N-to-1 Mapping Clusters)

### Cluster 1: `NIST-RA-8` (Privacy Impact Assessments) addresses 6 MAS Obligations

> **NIST Control Statement [NIST-RA-8]**:
> *Conduct privacy impact assessments for systems, programs, or other activities before:
Developing or procuring information technology that processes personally identifiable information; and
Initiating a new collection of personally identifiable information that:
Will be processed using information te...*

#### MAS Clause 1: `MAS-1.3.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *The Financial Institution must evaluate its exposure to technology risks.*

#### MAS Clause 2: `MAS-7.3.2.b`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `NO_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with NO_COVERAGE assurance level.
> *The Financial Institution must conduct a risk assessment for hardware and software approaching their end-of-support date.*

#### MAS Clause 3: `MAS-13.6.1.a`
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.95`)
- **Rationale**: Shared domain concepts (vulnerability, risk) with token overlap ratio of 0.42.
> *The Financial Institution must perform severity assessment and classification of an issue.*

#### MAS Clause 4: `MAS-15.1.3`
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.95`)
- **Rationale**: Shared domain concepts (audit, risk) with token overlap ratio of 0.52.
> *The Financial Institution must set the frequency of IT audits to be commensurate with the criticality and risk posed by the IT information asset, function, or process.*

#### MAS Clause 5: `MAS-15.1.2.a`
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.95`)
- **Rationale**: Shared domain concepts (audit, vulnerability, risk) with token overlap ratio of 0.38.
> *The Financial Institution must identify a comprehensive set of auditable areas for technology risk to enable effective risk assessment during audit planning.*

#### MAS Clause 6: `MAS-15.1.3.a`
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.95`)
- **Rationale**: Shared domain concepts (audit, risk) with token overlap ratio of 0.48.
> *The Financial Institution must set the frequency of IT audits commensurate with the criticality and risk posed by the IT information asset, function, or process.*

---

### Cluster 2: `NIST-RA-6` (Technical Surveillance Countermeasures Survey) addresses 2 MAS Obligations

> **NIST Control Statement [NIST-RA-6]**:
> *Employ a technical surveillance countermeasures survey at {{ insert: param, ra-06_odp.01 }} {{ insert: param, ra-06_odp.02 }}.
A technical surveillance countermeasures survey is a service provided by qualified personnel to detect the presence of technical surveillance devices and hazards and to iden...*

#### MAS Clause 1: `MAS-1.3.a`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *The Financial Institution must evaluate its exposure to technology risks.*

#### MAS Clause 2: `MAS-15.1.2.a`
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.95`)
- **Rationale**: Shared domain concepts (audit, vulnerability, risk) with token overlap ratio of 0.43.
> *The Financial Institution must identify a comprehensive set of auditable areas for technology risk to enable effective risk assessment during audit planning.*

---

### Cluster 3: `NIST-SR-2` (Supply Chain Risk Management Plan) addresses 9 MAS Obligations

> **NIST Control Statement [NIST-SR-2]**:
> *Develop a plan for managing supply chain risks associated with the research and development, design, manufacturing, acquisition, delivery, integration, operations and maintenance, and disposal of the following systems, system components or system services: {{ insert: param, sr-02_odp.01 }};
Review a...*

#### MAS Clause 1: `MAS-1.3.a`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *The Financial Institution must evaluate its exposure to technology risks.*

#### MAS Clause 2: `MAS-1.4(a).1`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *The Board of Directors and Senior Management must cultivate a strong risk culture.*

#### MAS Clause 3: `MAS-1.4(a).2`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *The Board of Directors and Senior Management must establish a sound and robust technology risk management framework.*

#### MAS Clause 4: `MAS-6.5.3.b`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: LLM Cross-Framework Semantic Evaluation
> *The Financial Institution must implement appropriate controls and security measures to address identified risks.*

#### MAS Clause 5: `MAS-7.3.2.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *The Financial Institution must develop a technology refresh plan for the replacement of hardware and software before they reach end-of-support.*

#### MAS Clause 6: `MAS-7.3.2.b`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *The Financial Institution must conduct a risk assessment for hardware and software approaching their end-of-support date.*

#### MAS Clause 7: `MAS-7.3.2.c`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *The Financial Institution must implement effective risk mitigation measures for hardware and software approaching their end-of-support date.*

#### MAS Clause 8: `MAS-13.6.1.c`
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.95`)
- **Rationale**: Shared domain concepts (risk) with token overlap ratio of 0.53.
> *The Financial Institution must develop risk assessment and mitigation strategies to manage deviations from the framework.*

#### MAS Clause 9: `MAS-14.1.4`
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.92`)
- **Rationale**: Shared domain concepts (risk) with token overlap ratio of 0.33.
> *The Financial Institution must implement specific measures aimed at addressing the risks unique to mobile applications.*

---

### Cluster 4: `NIST-RA-5` (Vulnerability Monitoring and Scanning) addresses 17 MAS Obligations

> **NIST Control Statement [NIST-RA-5]**:
> *Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;
Employ vulnerability monitoring tools and techniques that facilitate interoperability among tools and ...*

#### MAS Clause 1: `MAS-1.3.a`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *The Financial Institution must evaluate its exposure to technology risks.*

#### MAS Clause 2: `MAS-1.3.b`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *The Financial Institution must implement a robust risk management framework to ensure IT and cyber resilience.*

#### MAS Clause 3: `MAS-1.4(b).1`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *The Financial Institution must adopt a defence-in-depth approach to strengthen cyber resilience.*

#### MAS Clause 4: `MAS-6.5.2`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *The Financial Institution must establish measures to control and monitor the use of shadow IT within its environment.*

#### MAS Clause 5: `MAS-6.5.3.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *The Financial Institution must establish a process to assess the risk of end-user developed or acquired applications.*

#### MAS Clause 6: `MAS-6.5.3.d`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *The Financial Institution must conduct proper testing before deploying end-user developed or acquired applications.*

#### MAS Clause 7: `MAS-7.2.2`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUPERSET_OF with PARTIAL_COVERAGE assurance level.
> *The Financial Institution must review and verify the configuration information of its hardware and software on a regular basis.*

#### MAS Clause 8: `MAS-7.3.1.a`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUPERSET_OF with PARTIAL_COVERAGE assurance level.
> *The Financial Institution must avoid using outdated and unsupported hardware or software.*

#### MAS Clause 9: `MAS-7.3.1.b`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *The Financial Institution must closely monitor the end-of-support dates of its hardware and software.*

#### MAS Clause 10: `MAS-7.3.2.b`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *The Financial Institution must conduct a risk assessment for hardware and software approaching their end-of-support date.*

#### MAS Clause 11: `MAS-7.3.2.c`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: LLM Cross-Framework Semantic Evaluation
> *The Financial Institution must implement effective risk mitigation measures for hardware and software approaching their end-of-support date.*

#### MAS Clause 12: `MAS-7.7.1`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *The Financial Institution must establish an incident management framework to restore affected IT services or systems to a secure and stable state as quickly as possible, minimizing impact to the business and customers.*

#### MAS Clause 13: `MAS-13.6.1`
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.95`)
- **Rationale**: Shared domain concepts (vulnerability, risk) with token overlap ratio of 0.57.
> *The Financial Institution must establish a comprehensive remediation process to track and resolve issues identified from cyber security assessments or exercises.*

#### MAS Clause 14: `MAS-13.6.1.c`
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.95`)
- **Rationale**: Shared domain concepts (vulnerability, risk) with token overlap ratio of 0.47.
> *The Financial Institution must develop risk assessment and mitigation strategies to manage deviations from the framework.*

#### MAS Clause 15: `MAS-14.1.4`
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.89`)
- **Rationale**: Shared domain concepts (risk) with token overlap ratio of 0.27.
> *The Financial Institution must implement specific measures aimed at addressing the risks unique to mobile applications.*

#### MAS Clause 16: `MAS-14.1.7`
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.93`)
- **Rationale**: Shared domain concepts (access) with token overlap ratio of 0.36.
> *The Financial Institution must disallow rooted or jailbroken mobile devices from accessing the Financial Institution’s mobile applications to perform financial transactions unless the application is secured within a sandbox or container that insulates it from tampering and interception by malware.*

#### MAS Clause 17: `MAS-14.3.1`
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.94`)
- **Rationale**: Shared domain concepts (incident) with token overlap ratio of 0.39.
> *The Financial Institution must implement real-time fraud monitoring systems to identify and block suspicious or fraudulent online transactions.*

---

### Cluster 5: `NIST-SI-20` (Tainting) addresses 7 MAS Obligations

> **NIST Control Statement [NIST-SI-20]**:
> *Embed data or capabilities in the following systems or system components to determine if organizational data has been exfiltrated or improperly removed from the organization: {{ insert: param, si-20_odp }}.
Many cyber-attacks target organizational information, or information that the organization ho...*

#### MAS Clause 1: `MAS-1.3.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.
> *The Financial Institution must evaluate its exposure to technology risks.*

#### MAS Clause 2: `MAS-1.4(b).1`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Evaluated semantic relationship as SUBSET_OF with FULL_COVERAGE assurance level.
> *The Financial Institution must adopt a defence-in-depth approach to strengthen cyber resilience.*

#### MAS Clause 3: `MAS-1.4(b).2`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: LLM Cross-Framework Semantic Evaluation
> *The Financial Institution must establish IT processes and controls to preserve the confidentiality, integrity, and availability of data and IT systems.*

#### MAS Clause 4: `MAS-13.5.1`
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.91`)
- **Rationale**: Shared domain concepts (risk) with token overlap ratio of 0.30.
> *The Financial Institution must design the threat scenario based on challenging but plausible cyber threats to simulate realistic adversarial attacks during any cyber security assessment.*

#### MAS Clause 5: `MAS-15.1.3`
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.95`)
- **Rationale**: Shared domain concepts (risk) with token overlap ratio of 0.43.
> *The Financial Institution must set the frequency of IT audits to be commensurate with the criticality and risk posed by the IT information asset, function, or process.*

#### MAS Clause 6: `MAS-15.1.3.a`
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.93`)
- **Rationale**: Shared domain concepts (risk) with token overlap ratio of 0.38.
> *The Financial Institution must set the frequency of IT audits commensurate with the criticality and risk posed by the IT information asset, function, or process.*

#### MAS Clause 7: `MAS-C.1.1`
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.93`)
- **Rationale**: Shared domain concepts (risk) with token overlap ratio of 0.37.
> *The Financial Institution must prevent storing or caching data in the mobile application to mitigate the risk of data compromise on the device.*

---

