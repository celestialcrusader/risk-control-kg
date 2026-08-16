# Production Two-Dimensional Regulatory Crosswalk Results (Sprint M: Audit-Defensible Engine)

**Retrieval Architecture**: Multi-Intent Clause Decompounding + Hybrid Candidate Retrieval (bge-small + BM25 Okapi) with **Top-15 Recall Funnel**  
**Catalog Scoping**: Withdrawn & Blank Rev 5 Controls Purged (`RA-4`, `SA-12`, etc.)  
**Reasoning Engine**: Qwen 35B Two-Dimensional Dual-Judge with **Strict Anti-Heuristic Gatekeeper & Rationale Sanitizer**  
**Database Dual-Write**: PostgreSQL (`obligation_framework_mappings`) & Memgraph (`:CROSSWALKS_TO`)  
**Execution Date**: 2026-08-16  

---

## Section A: Two-Dimensional Crosswalk Statistics

| Metric | Value |
|---|---|
| **Total MAS TRM Obligations** | `85` |
| **Active NIST SP 800-53 Control Objectives** | `294` |
| **Total Active Crosswalk Links Formed** | `833` |
| **MAS Obligations Mapped (>= 1 match)** | `84` (98.8%) |
| **MAS Obligations Unmapped (0 matches)** | `1` (1.2%) |

### Dimension 1: Semantic Relationship Distribution (Source $\rightarrow$ Target Perspective)

| Semantic Relationship | Description | Edge Count | Percentage |
|---|---|---|---|
| `EQUIVALENT` | 1-to-1 Identical Scope & Intent | 35 | 4.2% |
| `SUBSET_OF` | Target NIST control completely satisfies MAS (MAS $\subseteq$ NIST) | 300 | 36.0% |
| `SUPERSET_OF` | MAS obligation is broader; NIST control covers a sub-part | 135 | 16.2% |
| `OVERLAPS` | Material conceptual overlap without strict containment | 343 | 41.2% |
| `SUPPORTS` | Target control enables/supports MAS without satisfying it | 20 | 2.4% |

### Dimension 2: Assurance Coverage Distribution (Audit Defensibility)

| Assurance Coverage Level | Meaning | Edge Count | Percentage |
|---|---|---|---|
| `FULL_COVERAGE` | NIST evidence completely satisfies MAS obligation for audit | 52 | 6.2% |
| `PARTIAL_COVERAGE` | NIST evidence satisfies material part; remaining gaps | 719 | 86.3% |
| `NO_COVERAGE` | NIST evidence does NOT satisfy MAS (enabling / supporting only) | 62 | 7.4% |

---

## Section B: 25 Sample Two-Dimensional Matches (Complete Verbatim Text & Defensible Rationales)

### Sample Match 1: `MAS-1.3.a` ⟷ `NIST-RA-8`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.59`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0393 (Max Dense Sim: 0.59)
* **Defensible Rationale**: Control B mandates Privacy Impact Assessments specifically for Personally Identifiable Information (PII) processing, which is a subset of technology risks. It does not address broader technology risks such as operational, financial, or non-PII data security vulnerabilities required by Requirement A.

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

### Sample Match 2: `MAS-1.4(a).1` ⟷ `NIST-CA-6`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.48`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0336 (Max Dense Sim: 0.48)
* **Defensible Rationale**: Control B mandates specific technical and administrative actions for risk acceptance and system authorization by senior officials, which operationalizes the 'risk culture' requirement by establishing accountability. However, Control B is limited to information security authorization processes, whereas Requirement A encompasses a broader organizational risk culture that includes non-technical domains and general behavioral expectations.

> **MAS TRM Clause [MAS-1.4(a).1]**:
> *The Board of Directors and Senior Management must cultivate a strong risk culture.*

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

### Sample Match 3: `MAS-1.4(b).1` ⟷ `NIST-RA-9`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.57`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0306 (Max Dense Sim: 0.57)
* **Defensible Rationale**: Control B mandates a specific analytical process (criticality analysis) to identify and prioritize system components, which is a foundational prerequisite for implementing a defense-in-depth strategy. However, Control B does not enforce the actual deployment of layered technical safeguards or the holistic architectural design required by Requirement A.

> **MAS TRM Clause [MAS-1.4(b).1]**:
> *The Financial Institution must adopt a defence-in-depth approach to strengthen cyber resilience.*

> **NIST SP 800-53 Control [NIST-RA-9 - Criticality Analysis]**:
> *Identify critical system components and functions by performing a criticality analysis for {{ insert: param, ra-09_odp.01 }} at {{ insert: param, ra-09_odp.02 }}.
Not all system components, functions, or services necessarily require significant protections. For example, criticality analysis is a key tenet of supply chain risk management and informs the prioritization of protection activities. The identification of critical system components and functions considers applicable laws, executive orders, regulations, directives, policies, standards, system functionality requirements, system and component interfaces, and system and component dependencies. Systems engineers conduct a functional decomposition of a system to identify mission-critical functions and components. The functional decomposition includes the identification of organizational missions supported by the system, decomposition into the specific functions to perform those missions, and traceability to the hardware, software, and firmware components that implement those functions, including when the functions are shared by many components within and external to the system.

The operational environment of a system or a system component may impact the criticality, including the connections to and dependencies on cyber-physical systems, devices, system-of-systems, and outsourced IT services. System components that allow unmediated access to critical system components or functions are considered critical due to the inherent vulnerabilities that such components create. Component and function criticality are assessed in terms of the impact of a component or function failure on the organizational missions that are supported by the system that contains the components and functions.

Criticality analysis is performed when an architecture or design is being developed, modified, or upgraded. If such analysis is performed early in the system development life cycle, organizations may be able to modify the system design to reduce the critical nature of these components and functions, such as by adding redundancy or alternate paths into the system design. Criticality analysis can also influence the protection measures required by development contractors. In addition to criticality analysis for systems, system components, and system services, criticality analysis of information is an important consideration. Such analysis is conducted as part of security categorization in [RA-2](#ra-2).
critical system components and functions are identified by performing a criticality analysis for {{ insert: param, ra-09_odp.01 }} at {{ insert: param, ra-09_odp.02 }}.
Risk assessment policy

assessment reports

criticality analysis/finalized criticality for each component/subcomponent

audit records/event logs

analysis reports

system security plan

other relevant documents or records
Organizational personnel with assessment and auditing responsibilities

organizational personnel with criticality analysis responsibilities

system/network administrators

organizational personnel with security responsibilities
Organizational processes for assessments and audits

mechanisms/tools supporting and/or implementing assessments and auditing*

---

### Sample Match 4: `MAS-6.5.1` ⟷ `NIST-PM-7`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.63`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0382 (Max Dense Sim: 0.63)
* **Defensible Rationale**: Control B mandates the integration of security and privacy into the Enterprise Architecture, which serves as the structural framework for managing information assets, but it does not explicitly mandate the specific operational governance of 'shadow IT' (unauthorized or unsanctioned IT resources) required by Requirement A.

> **MAS TRM Clause [MAS-6.5.1]**:
> *The Financial Institution must manage shadow IT as part of its information assets.*

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

### Sample Match 5: `MAS-6.5.3.b` ⟷ `NIST-SR-3`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.60`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0363 (Max Dense Sim: 0.60)
* **Defensible Rationale**: Control B implements specific supply chain risk management processes, whereas Requirement A mandates a broader set of controls to address all identified risks across the entire financial institution. Control B is a necessary component but does not encompass the full scope of general risk mitigation required by Requirement A.

> **MAS TRM Clause [MAS-6.5.3.b]**:
> *The Financial Institution must implement appropriate controls and security measures to address identified risks.*

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

### Sample Match 6: `MAS-7.1.1` ⟷ `NIST-PM-23`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.62`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0395 (Max Dense Sim: 0.62)
* **Defensible Rationale**: Requirement A mandates a comprehensive IT Service Management (ITSM) framework covering all IT service activities, whereas Control B establishes a Data Governance Body focused specifically on data policy, quality, and privacy. While the Data Governance Body provides a governance structure, it does not address the broader operational processes and procedures required for general IT service management.

> **MAS TRM Clause [MAS-7.1.1]**:
> *The Financial Institution must establish an IT service management framework comprising governance structures, processes, and procedures for IT service management activities.*

> **NIST SP 800-53 Control [NIST-PM-23 - Data Governance Body]**:
> *Establish a Data Governance Body consisting of {{ insert: param, pm-23_odp.01 }} with {{ insert: param, pm-23_odp.02 }}.
A Data Governance Body can help ensure that the organization has coherent policies and the ability to balance the utility of data with security and privacy requirements. The Data Governance Body establishes policies, procedures, and standards that facilitate data governance so that data, including personally identifiable information, is effectively managed and maintained in accordance with applicable laws, executive orders, directives, regulations, policies, standards, and guidance. Responsibilities can include developing and implementing guidelines that support data modeling, quality, integrity, and the de-identification needs of personally identifiable information across the information life cycle as well as reviewing and approving applications to release data outside of the organization, archiving the applications and the released data, and performing post-release monitoring to ensure that the assumptions made as part of the data release continue to be valid. Members include the chief information officer, senior agency information security officer, and senior agency official for privacy. Federal agencies are required to establish a Data Governance Body with specific roles and responsibilities in accordance with the [EVIDACT](#511da9ca-604d-43f7-be41-b862085420a9) and policies set forth under [OMB M-19-23](#d886c141-c832-4ad7-ac6d-4b94f4b550d3).
a Data Governance Body consisting of {{ insert: param, pm-23_odp.01 }} with {{ insert: param, pm-23_odp.02 }} is established.
Privacy program plan

documentation relating to the Data Governance Body, including documents establishing such a body, its charter of operations, and any plans and reports

records of board meetings and decisions

records of requests to review data

policies, procedures, and standards that facilitate data governance
Officials serving on the Data Governance Body (e.g., chief information officer, senior agency information security officer, and senior agency official for privacy)*

---

### Sample Match 7: `MAS-7.3.1.a` ⟷ `NIST-RA-5`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.58`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0361 (Max Dense Sim: 0.58)
* **Defensible Rationale**: Control B mandates active vulnerability scanning, analysis, and remediation of software flaws, which inherently addresses the 'unsupported software' aspect of Requirement A. However, Control B lacks explicit mandates for the physical lifecycle management or replacement of 'outdated hardware,' leaving that specific component of Requirement A unaddressed.

> **MAS TRM Clause [MAS-7.3.1.a]**:
> *The Financial Institution must avoid using outdated and unsupported hardware or software.*

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

### Sample Match 8: `MAS-7.3.2.b` ⟷ `NIST-MA-3`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.59`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0567 (Max Dense Sim: 0.59)
* **Defensible Rationale**: Control B mandates the approval, control, and monitoring of maintenance tools (including hardware/software) and their periodic review to withdraw support for outdated items, which partially addresses the requirement. However, Control B focuses on the security governance of the tools themselves rather than conducting a comprehensive risk assessment of the end-of-support status of the organization's broader hardware and software portfolio.

> **MAS TRM Clause [MAS-7.3.2.b]**:
> *The Financial Institution must conduct a risk assessment for hardware and software approaching their end-of-support date.*

> **NIST SP 800-53 Control [NIST-MA-3 - Maintenance Tools]**:
> *Approve, control, and monitor the use of system maintenance tools; and
Review previously approved system maintenance tools {{ insert: param, ma-03_odp }}.
Approving, controlling, monitoring, and reviewing maintenance tools address security-related issues associated with maintenance tools that are not within system authorization boundaries and are used specifically for diagnostic and repair actions on organizational systems. Organizations have flexibility in determining roles for the approval of maintenance tools and how that approval is documented. A periodic review of maintenance tools facilitates the withdrawal of approval for outdated, unsupported, irrelevant, or no-longer-used tools. Maintenance tools can include hardware, software, and firmware items and may be pre-installed, brought in with maintenance personnel on media, cloud-based, or downloaded from a website. Such tools can be vehicles for transporting malicious code, either intentionally or unintentionally, into a facility and subsequently into systems. Maintenance tools can include hardware and software diagnostic test equipment and packet sniffers. The hardware and software components that support maintenance and are a part of the system (including the software implementing utilities such as "ping," "ls," "ipconfig," or the hardware and software implementing the monitoring port of an Ethernet switch) are not addressed by maintenance tools.
the use of system maintenance tools is approved;
the use of system maintenance tools is controlled;
the use of system maintenance tools is monitored;
previously approved system maintenance tools are reviewed {{ insert: param, ma-03_odp }}.
Maintenance policy

procedures addressing system maintenance tools

system maintenance tools and associated documentation

maintenance records

system security plan

other relevant documents or records
Organizational personnel with system maintenance responsibilities

organizational personnel with information security responsibilities
Organizational processes for approving, controlling, and monitoring maintenance tools

mechanisms supporting and/or implementing the approval, control, and/or monitoring of maintenance tools*

---

### Sample Match 9: `MAS-7.5.6.a` ⟷ `NIST-RA-3`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.57`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0288 (Max Dense Sim: 0.57)
* **Defensible Rationale**: Control B mandates a comprehensive, ongoing risk assessment process covering threats, vulnerabilities, and impacts, but lacks the specific procedural mandates for the approval and implementation of emergency changes required by Requirement A. While B provides the necessary risk analysis component, it does not address the change management workflow (approval/implementation) for emergency scenarios.

> **MAS TRM Clause [MAS-7.5.6.a]**:
> *The Financial Institution must define procedures for assessing, approving, and implementing emergency changes to reduce the risk to the security and stability of the production environment.*

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

### Sample Match 10: `MAS-7.6.2` ⟷ `NIST-SC-8`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.56`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0343 (Max Dense Sim: 0.56)
* **Defensible Rationale**: Control B mandates technical integrity protection for data in transit across networks, which supports the integrity aspect of Requirement A, but it does not address the specific requirement for maintaining traceability (audit trails) of software code movements between environments.

> **MAS TRM Clause [MAS-7.6.2]**:
> *The Financial Institution must implement controls to maintain traceability and integrity for all software codes moved between IT environments.*

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

### Sample Match 11: `MAS-7.7.3.a` ⟷ `NIST-IR-4`

* **Semantic Relation**: `EQUIVALENT`
* **Assurance Coverage**: `FULL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.72`)
* **Retrieval Trace**: Multi-Intent RRF: 0.1166 (Max Dense Sim: 0.72)
* **Defensible Rationale**: Control B (NIST-IR-4) mandates a comprehensive incident handling capability covering the full lifecycle (preparation, detection, containment, etc.) and explicitly requires coordination with contingency planning and integration of lessons learned, which fully satisfies the Source Requirement A's mandate for IT and cyber incident handling processes within the incident management framework.

> **MAS TRM Clause [MAS-7.7.3.a]**:
> *The Financial Institution must include processes and procedures for handling IT incidents, including cyber-related incidents, in the incident management framework.*

> **NIST SP 800-53 Control [NIST-IR-4 - Incident Handling]**:
> *Implement an incident handling capability for incidents that is consistent with the incident response plan and includes preparation, detection and analysis, containment, eradication, and recovery;
Coordinate incident handling activities with contingency planning activities;
Incorporate lessons learned from ongoing incident handling activities into incident response procedures, training, and testing, and implement the resulting changes accordingly; and
Ensure the rigor, intensity, scope, and results of incident handling activities are comparable and predictable across the organization.
Organizations recognize that incident response capabilities are dependent on the capabilities of organizational systems and the mission and business processes being supported by those systems. Organizations consider incident response as part of the definition, design, and development of mission and business processes and systems. Incident-related information can be obtained from a variety of sources, including audit monitoring, physical access monitoring, and network monitoring; user or administrator reports; and reported supply chain events. An effective incident handling capability includes coordination among many organizational entities (e.g., mission or business owners, system owners, authorizing officials, human resources offices, physical security offices, personnel security offices, legal departments, risk executive [function], operations personnel, procurement offices). Suspected security incidents include the receipt of suspicious email communications that can contain malicious code. Suspected supply chain incidents include the insertion of counterfeit hardware or malicious code into organizational systems or system components. For federal agencies, an incident that involves personally identifiable information is considered a breach. A breach results in unauthorized disclosure, the loss of control, unauthorized acquisition, compromise, or a similar occurrence where a person other than an authorized user accesses or potentially accesses personally identifiable information or an authorized user accesses or potentially accesses such information for other than authorized purposes.
an incident handling capability for incidents is implemented that is consistent with the incident response plan;
the incident handling capability for incidents includes preparation;
the incident handling capability for incidents includes detection and analysis;
the incident handling capability for incidents includes containment;
the incident handling capability for incidents includes eradication;
the incident handling capability for incidents includes recovery;
incident handling activities are coordinated with contingency planning activities;
lessons learned from ongoing incident handling activities are incorporated into incident response procedures, training, and testing;
the changes resulting from the incorporated lessons learned are implemented accordingly;
the rigor of incident handling activities is comparable and predictable across the organization;
the intensity of incident handling activities is comparable and predictable across the organization;
the scope of incident handling activities is comparable and predictable across the organization;
the results of incident handling activities are comparable and predictable across the organization.
Incident response policy

contingency planning policy

procedures addressing incident handling

incident response plan

contingency plan

system security plan

privacy plan

other relevant documents or records
Organizational personnel with incident handling responsibilities

organizational personnel with contingency planning responsibilities

organizational personnel with information security and privacy responsibilities
Incident handling capability for the organization*

---

### Sample Match 12: `MAS-7.7.3.c` ⟷ `NIST-CP-2`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.60`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0324 (Max Dense Sim: 0.60)
* **Defensible Rationale**: Control B defines roles and responsibilities specifically for contingency operations and system restoration, whereas Requirement A mandates a broader scope covering the entire incident management lifecycle including recording, analysis, escalation, and monitoring. Control B addresses only the resolution/monitoring subset of the required incident management framework.

> **MAS TRM Clause [MAS-7.7.3.c]**:
> *The Financial Institution must define the roles and responsibilities of staff and external parties involved in incident recording, analysis, escalation, decision-making, resolution, and monitoring within the incident management framework.*

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

### Sample Match 13: `MAS-13.4.2.b` ⟷ `NIST-SC-24`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.50`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0234 (Max Dense Sim: 0.50)
* **Defensible Rationale**: Control B implements a specific technical mechanism (fail in known state) that ensures system availability and prevents disruption, directly satisfying the 'controlled manner' aspect of Requirement A. However, Requirement A mandates a broader governance and operational exercise under 'close supervision,' which Control B does not explicitly address as it focuses solely on the technical failure mode.

> **MAS TRM Clause [MAS-13.4.2.b]**:
> *The Financial Institution must conduct the exercise in a controlled manner under close supervision to prevent disruption to its production systems.*

> **NIST SP 800-53 Control [NIST-SC-24 - Fail in Known State]**:
> *Fail to a {{ insert: param, sc-24_odp.02 }} for the following failures on the indicated components while preserving {{ insert: param, sc-24_odp.03 }} in failure: {{ insert: param, sc-24_odp.01 }}.
Failure in a known state addresses security concerns in accordance with the mission and business needs of organizations. Failure in a known state prevents the loss of confidentiality, integrity, or availability of information in the event of failures of organizational systems or system components. Failure in a known safe state helps to prevent systems from failing to a state that may cause injury to individuals or destruction to property. Preserving system state information facilitates system restart and return to the operational mode with less disruption of mission and business processes.
{{ insert: param, sc-24_odp.01 }} fail to a {{ insert: param, sc-24_odp.02 }} while preserving {{ insert: param, sc-24_odp.03 }} in failure.
System and communications protection policy

procedures addressing system failure to known state

system design documentation

system configuration settings and associated documentation

list of failures requiring system to fail in a known state

state information to be preserved in system failure

system audit records

system security plan

other relevant documents or records
System/network administrators

organizational personnel with information security responsibilities

system developer
Mechanisms supporting and/or implementing the fail in known state capability

mechanisms preserving system state information in the event of a system failure*

---

### Sample Match 14: `MAS-13.6.1` ⟷ `NIST-SA-24`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.57`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0359 (Max Dense Sim: 0.57)
* **Defensible Rationale**: Requirement A mandates a remediation process for tracking and resolving issues from security assessments, whereas Control B focuses on the proactive design of cyber resiliency goals and principles during system development. While both address risk management, Control B does not provide the specific operational mechanisms for post-assessment issue tracking and resolution required by Requirement A.

> **MAS TRM Clause [MAS-13.6.1]**:
> *The Financial Institution must establish a comprehensive remediation process to track and resolve issues identified from cyber security assessments or exercises.*

> **NIST SP 800-53 Control [NIST-SA-24 - Design For Cyber Resiliency]**:
> *Design organizational systems, system components, or system services to achieve cyber resiliency by:
Defining the following cyber resiliency goals: {{ insert: param, sa-24_odp.01 }}.
Defining the following cyber resiliency objectives: {{ insert: param, sa-24_odp.02 }}.
Defining the following cyber resiliency techniques: {{ insert: param, sa-24_odp.03 }}.
Defining the following cyber resiliency implementation approaches: {{ insert: param, sa-24_odp.04 }}.
Defining the following cyber resiliency design principles: {{ insert: param, sa-24_odp.05 }}.
Implement the selected cyber resiliency goals, objectives, techniques, implementation approaches, and design principles as part of an organizational risk management process or systems security engineering process.
Cyber resiliency is critical to ensuring the survivability of mission critical systems and high value assets. Cyber resiliency focuses on limiting the damage from adversity or the conditions that can cause a loss of assets. Damage can affect: (1) organizations (e.g., loss of reputation, increased existential risk); (2) missions or business functions (e.g., decreased capability to complete current missions and to accomplish future missions); (3) security (e.g., decreased capability to achieve security objectives or to prevent, detect, and respond to cyber incidents); (4) systems (e.g., unauthorized use of system resources or decreased capability to meet system requirements); or (5) specific system elements (e.g., physical destruction; corruption, modification, or fabrication of information).

Cyber resiliency goals are intended to help organizations maintain a state of informed preparedness for adversity, continue essential mission or business functions despite adversity, restore mission or business functions during and after adversity, and modify mission or business functions and their supporting capabilities in response to predicted changes in technical, operational, or threat environments.

NIST SP 800-160, Volume 2 provides additional information on the Cyber Resiliency Engineering Framework to include detailed descriptions of cyber resiliency goals, objectives, techniques, implementation approaches, and design principles. NIST SP 800-160, Vol 1 provides additional information on achieving cyber resiliency as an emergent property of an engineered system.
Determine if:
organizational systems, system components, or system services achieve cyber resiliency through {{ insert: param, sa-24_odp.01 }};
organizational systems, system components, or system services achieve cyber resiliency through {{ insert: param, sa-24_odp.02 }};
organizational systems, system components, or system services achieve cyber resiliency through {{ insert: param, sa-24_odp.03 }};
organizational systems, system components, or system services achieve cyber resiliency through {{ insert: param, sa-24_odp.04 }};
organizational systems, system components, or system services achieve cyber resiliency through {{ insert: param, sa-24_odp.05 }};
selected cyber resiliency goals are implemented as part of an organizational risk management process of systems security engineering process;
selected cyber resiliency objectives are implemented as part of an organizational risk management process of systems security engineering process;
selected cyber resiliency techniques are implemented as part of an organizational risk management process of systems security engineering process;
selected cyber resiliency implementation approaches are implemented as part of an organizational risk management process of systems security engineering process;
selected cyber resiliency design principles are implemented as part of an organizational risk management process of systems security engineering process.
System and services acquisition policy;

system and services acquisition procedures;

assessment and authorization procedures; 

procedures addressing cyber resiliency goals, objectives, techniques, implementation approaches, and design principles used in the specification, design, development, implementation, and modification of the system; 

system design documentation; 

security and privacy requirements and specifications for the system; 

system security plan;

privacy plan; 

privacy impact assessment; 

privacy risk assessment documentation.
Organizational personnel with acquisition/contracting responsibilities; 

organizational personnel with information security and privacy responsibilities; 

organizational personnel with system specification, design, development, implementation, and modification responsibilities; 

system developers.
Organizational processes for applying cyber resiliency principles in system specification, design, development, implementation, and modification;

mechanisms supporting the application of cyber resiliency principles in system specification, design, development, implementation, and modification.*

---

### Sample Match 15: `MAS-13.6.1.c` ⟷ `NIST-SR-2`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.59`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0374 (Max Dense Sim: 0.59)
* **Defensible Rationale**: Control B mandates a specific Supply Chain Risk Management Plan covering the full system lifecycle, which is a distinct subset of the broad 'risk assessment and mitigation strategies' required by Requirement A. While Control B satisfies the mandate for supply chain deviations, it does not address risk management for other operational, financial, or strategic deviations implied by the general scope of Requirement A.

> **MAS TRM Clause [MAS-13.6.1.c]**:
> *The Financial Institution must develop risk assessment and mitigation strategies to manage deviations from the framework.*

> **NIST SP 800-53 Control [NIST-SR-2 - Supply Chain Risk Management Plan]**:
> *Develop a plan for managing supply chain risks associated with the research and development, design, manufacturing, acquisition, delivery, integration, operations and maintenance, and disposal of the following systems, system components or system services: {{ insert: param, sr-02_odp.01 }};
Review and update the supply chain risk management plan {{ insert: param, sr-02_odp.02 }} or as required, to address threat, organizational or environmental changes; and
Protect the supply chain risk management plan from unauthorized disclosure and modification.
The dependence on products, systems, and services from external providers, as well as the nature of the relationships with those providers, present an increasing level of risk to an organization. Threat actions that may increase security or privacy risks include unauthorized production, the insertion or use of counterfeits, tampering, theft, insertion of malicious software and hardware, and poor manufacturing and development practices in the supply chain. Supply chain risks can be endemic or systemic within a system element or component, a system, an organization, a sector, or the Nation. Managing supply chain risk is a complex, multifaceted undertaking that requires a coordinated effort across an organization to build trust relationships and communicate with internal and external stakeholders. Supply chain risk management (SCRM) activities include identifying and assessing risks, determining appropriate risk response actions, developing SCRM plans to document response actions, and monitoring performance against plans. The SCRM plan (at the system-level) is implementation specific, providing policy implementation, requirements, constraints and implications. It can either be stand-alone, or incorporated into system security and privacy plans. The SCRM plan addresses managing, implementation, and monitoring of SCRM controls and the development/sustainment of systems across the SDLC to support mission and business functions.

Because supply chains can differ significantly across and within organizations, SCRM plans are tailored to the individual program, organizational, and operational contexts. Tailored SCRM plans provide the basis for determining whether a technology, service, system component, or system is fit for purpose, and as such, the controls need to be tailored accordingly. Tailored SCRM plans help organizations focus their resources on the most critical mission and business functions based on mission and business requirements and their risk environment. Supply chain risk management plans include an expression of the supply chain risk tolerance for the organization, acceptable supply chain risk mitigation strategies or controls, a process for consistently evaluating and monitoring supply chain risk, approaches for implementing and communicating the plan, a description of and justification for supply chain risk mitigation measures taken, and associated roles and responsibilities. Finally, supply chain risk management plans address requirements for developing trustworthy, secure, privacy-protective, and resilient system components and systems, including the application of the security design principles implemented as part of life cycle-based systems security engineering processes (see [SA-8](#sa-8)).
a plan for managing supply chain risks is developed;
the supply chain risk management plan addresses risks associated with the research and development of {{ insert: param, sr-02_odp.01 }};
the supply chain risk management plan addresses risks associated with the design of {{ insert: param, sr-02_odp.01 }};
the supply chain risk management plan addresses risks associated with the manufacturing of {{ insert: param, sr-02_odp.01 }};
the supply chain risk management plan addresses risks associated with the acquisition of {{ insert: param, sr-02_odp.01 }};
the supply chain risk management plan addresses risks associated with the delivery of {{ insert: param, sr-02_odp.01 }};
the supply chain risk management plan addresses risks associated with the integration of {{ insert: param, sr-02_odp.01 }};
the supply chain risk management plan addresses risks associated with the operation and maintenance of {{ insert: param, sr-02_odp.01 }};
the supply chain risk management plan addresses risks associated with the disposal of {{ insert: param, sr-02_odp.01 }};
the supply chain risk management plan is reviewed and updated {{ insert: param, sr-02_odp.02 }} or as required to address threat, organizational, or environmental changes;
the supply chain risk management plan is protected from unauthorized disclosure;
the supply chain risk management plan is protected from unauthorized modification.
Supply chain risk management policy

supply chain risk management procedures

supply chain risk management plan

system and services acquisition policy

system and services acquisition procedures

procedures addressing supply chain protection

procedures for protecting the supply chain risk management plan from unauthorized disclosure and modification

system development life cycle procedures

procedures addressing the integration of information security and privacy requirements into the acquisition process

acquisition documentation

service level agreements

acquisition contracts for the system, system component, or system service

list of supply chain threats

list of safeguards to be taken against supply chain threats

system life cycle documentation

inter-organizational agreements and procedures

system security plan

privacy plan

privacy program plan

other relevant documents or records
Organizational personnel with acquisition responsibilities

organizational personnel with information security and privacy responsibilities

organizational personnel with supply chain risk management responsibilities
Organizational processes for defining and documenting the system development life cycle (SDLC)

organizational processes for identifying SDLC roles and responsibilities

organizational processes for integrating supply chain risk management into the SDLC

mechanisms supporting and/or implementing the SDLC*

---

### Sample Match 16: `MAS-14.1.2` ⟷ `NIST-SC-13`

* **Semantic Relation**: `EQUIVALENT`
* **Assurance Coverage**: `FULL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.58`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0261 (Max Dense Sim: 0.58)
* **Defensible Rationale**: Control B (NIST SC-13) mandates the specific implementation of cryptographic standards (e.g., FIPS-validated) to secure communications, which is the technical mechanism required to satisfy the general obligation in Requirement A to protect customer data during transmission.

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

### Sample Match 17: `MAS-14.1.5` ⟷ `NIST-SC-8`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.54`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0328 (Max Dense Sim: 0.54)
* **Defensible Rationale**: Requirement A mandates secure distribution channels (e.g., official app stores) to prevent tampering during software delivery, whereas Control B focuses on protecting data confidentiality and integrity during network transmission (e.g., encryption). While both address security, A targets the distribution mechanism and supply chain integrity, while B targets the communication channel security.

> **MAS TRM Clause [MAS-14.1.5]**:
> *The Financial Institution must distribute mobile applications or software to customers only through official mobile application stores or other secure delivery channels.*

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

### Sample Match 18: `MAS-14.2.1` ⟷ `NIST-IA-6`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.61`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0662 (Max Dense Sim: 0.61)
* **Defensible Rationale**: Requirement A mandates the deployment of multi-factor authentication (MFA) as a specific technical control, whereas Control B addresses the general security of the authentication feedback mechanism (e.g., obscuring input) without specifying the number of factors required. Control B supports the secure implementation of authentication but does not fulfill the specific MFA mandate.

> **MAS TRM Clause [MAS-14.2.1]**:
> *The Financial Institution must deploy multi-factor authentication at login for online financial services to secure the customer authentication process.*

> **NIST SP 800-53 Control [NIST-IA-6 - Authentication Feedback]**:
> *Obscure feedback of authentication information during the authentication process to protect the information from possible exploitation and use by unauthorized individuals.
Authentication feedback from systems does not provide information that would allow unauthorized individuals to compromise authentication mechanisms. For some types of systems, such as desktops or notebooks with relatively large monitors, the threat (referred to as shoulder surfing) may be significant. For other types of systems, such as mobile devices with small displays, the threat may be less significant and is balanced against the increased likelihood of typographic input errors due to small keyboards. Thus, the means for obscuring authentication feedback is selected accordingly. Obscuring authentication feedback includes displaying asterisks when users type passwords into input devices or displaying feedback for a very limited time before obscuring it.
the feedback of authentication information is obscured during the authentication process to protect the information from possible exploitation and use by unauthorized individuals.
Identification and authentication policy

system security plan

procedures addressing authenticator feedback

system design documentation

system configuration settings and associated documentation

system audit records

other relevant documents or records
Organizational personnel with information security responsibilities

system/network administrators

system developers
Mechanisms supporting and/or implementing the obscuring of feedback of authentication information during authentication*

---

### Sample Match 19: `MAS-14.3.3.a` ⟷ `NIST-SI-4`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.54`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0254 (Max Dense Sim: 0.54)
* **Defensible Rationale**: Control B mandates the technical detection and analysis of suspicious activities and unauthorized transactions, which serves as the necessary input for identifying the events described in Requirement A. However, Control B lacks the explicit procedural mandate to notify customers, focusing solely on internal system monitoring rather than external customer communication.

> **MAS TRM Clause [MAS-14.3.3.a]**:
> *The Financial Institution must notify customers of suspicious activities or funds transfers exceeding a threshold defined by the Financial Institution or the customers.*

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

### Sample Match 20: `MAS-15.1.4` ⟷ `NIST-CA-2`

* **Semantic Relation**: `EQUIVALENT`
* **Assurance Coverage**: `FULL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.58`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0400 (Max Dense Sim: 0.58)
* **Defensible Rationale**: Control B explicitly mandates that organizations ensure control assessors possess required skills, technical expertise, and comprehensive knowledge of system components, which directly satisfies the competency verification requirement of Source A. The control's structured selection and planning processes provide the necessary evidence to audit the adequacy of the IT auditors' qualifications.

> **MAS TRM Clause [MAS-15.1.4]**:
> *The Financial Institution must verify that IT auditors possess the requisite level of competency and skills to effectively assess and evaluate the adequacy of implemented IT policies, procedures, processes, and controls.*

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

### Sample Match 21: `MAS-15.1.4.a` ⟷ `NIST-CA-2`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.57`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0397 (Max Dense Sim: 0.57)
* **Defensible Rationale**: Control B explicitly mandates that assessors possess required skills and technical expertise, directly satisfying the competency verification aspect of Requirement A. However, Control B focuses on the selection and qualification of the assessment team rather than establishing a comprehensive, ongoing competency management program for all IT auditors, leaving the broader scope of Requirement A only partially addressed.

> **MAS TRM Clause [MAS-15.1.4.a]**:
> *The Financial Institution must verify that its IT auditors possess the requisite level of competency and skills to effectively assess and evaluate the adequacy of implemented IT policies, procedures, processes, and controls.*

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

### Sample Match 22: `MAS-5.1.1` ⟷ `NIST-SC-28`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.56`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0292 (Max Dense Sim: 0.56)
* **Defensible Rationale**: Control B mandates cryptographic protection for information at rest on system components, which is a specific technical implementation of the broader data loss prevention requirement in A. However, Control B does not explicitly address mobile devices or the prevention of unauthorized exfiltration (loss), focusing instead on confidentiality and integrity of stored data.

> **MAS TRM Clause [MAS-5.1.1]**:
> *The Financial Institution must implement data loss prevention measures on personal computing or mobile devices used to access information assets.*

> **NIST SP 800-53 Control [NIST-SC-28 - Protection of Information at Rest]**:
> *Protect the {{ insert: param, sc-28_odp.01 }} of the following information at rest: {{ insert: param, sc-28_odp.02 }}.
Information at rest refers to the state of information when it is not in process or in transit and is located on system components. Such components include internal or external hard disk drives, storage area network devices, or databases. However, the focus of protecting information at rest is not on the type of storage device or frequency of access but rather on the state of the information. Information at rest addresses the confidentiality and integrity of information and covers user information and system information. System-related information that requires protection includes configurations or rule sets for firewalls, intrusion detection and prevention systems, filtering routers, and authentication information. Organizations may employ different mechanisms to achieve confidentiality and integrity protections, including the use of cryptographic mechanisms and file share scanning. Integrity protection can be achieved, for example, by implementing write-once-read-many (WORM) technologies. When adequate protection of information at rest cannot otherwise be achieved, organizations may employ other controls, including frequent scanning to identify malicious code at rest and secure offline storage in lieu of online storage.
the {{ insert: param, sc-28_odp.01 }} of {{ insert: param, sc-28_odp.02 }} is/are protected.
System and communications protection policy

procedures addressing the protection of information at rest

system design documentation

system configuration settings and associated documentation

cryptographic mechanisms and associated configuration documentation

list of information at rest requiring confidentiality and integrity protections

system security plan

other relevant documents or records
System/network administrators

organizational personnel with information security responsibilities

system developer
Mechanisms supporting and/or implementing confidentiality and integrity protections for information at rest*

---

### Sample Match 23: `MAS-C.1.2` ⟷ `NIST-AC-11`

* **Semantic Relation**: `OVERLAPS`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.60`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0347 (Max Dense Sim: 0.60)
* **Defensible Rationale**: Control B mandates session locking to prevent unauthorized access during user absence, which protects data in transit but does not enforce the specific requirement to store data within a protected, trusted area (e.g., secure enclave or encrypted storage) at rest.

> **MAS TRM Clause [MAS-C.1.2]**:
> *The Financial Institution must store data in a protected and trusted area of the mobile device.*

> **NIST SP 800-53 Control [NIST-AC-11 - Device Lock]**:
> *Prevent further access to the system by {{ insert: param, ac-11_odp.01 }} ; and
Retain the device lock until the user reestablishes access using established identification and authentication procedures.
Device locks are temporary actions taken to prevent logical access to organizational systems when users stop work and move away from the immediate vicinity of those systems but do not want to log out because of the temporary nature of their absences. Device locks can be implemented at the operating system level or at the application level. A proximity lock may be used to initiate the device lock (e.g., via a Bluetooth-enabled device or dongle). User-initiated device locking is behavior or policy-based and, as such, requires users to take physical action to initiate the device lock. Device locks are not an acceptable substitute for logging out of systems, such as when organizations require users to log out at the end of workdays.
further access to the system is prevented by {{ insert: param, ac-11_odp.01 }};
device lock is retained until the user re-establishes access using established identification and authentication procedures.
Access control policy

procedures addressing session lock

procedures addressing identification and authentication

system design documentation

system configuration settings and associated documentation

security plan

system security plan

other relevant documents or records
System/network administrators

organizational personnel with information security responsibilities

system developers
Mechanisms implementing access control policy for session lock*

---

### Sample Match 24: `MAS-C.1.5` ⟷ `NIST-SI-1`

* **Semantic Relation**: `SUPPORTS`
* **Assurance Coverage**: `NO_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.59`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0347 (Max Dense Sim: 0.59)
* **Defensible Rationale**: Requirement A mandates specific technical application integrity checks, whereas Control B establishes only the organizational governance framework (policy and procedures) for system integrity without implementing the required technical verification mechanisms.

> **MAS TRM Clause [MAS-C.1.5]**:
> *The Financial Institution must implement appropriate application integrity checks to verify the authenticity and integrity of the application.*

> **NIST SP 800-53 Control [NIST-SI-1 - Policy and Procedures]**:
> *Develop, document, and disseminate to {{ insert: param, si-1_prm_1 }}:
{{ insert: param, si-01_odp.03 }} system and information integrity policy that:
Addresses purpose, scope, roles, responsibilities, management commitment, coordination among organizational entities, and compliance; and
Is consistent with applicable laws, executive orders, directives, regulations, policies, standards, and guidelines; and
Procedures to facilitate the implementation of the system and information integrity policy and the associated system and information integrity controls;
Designate an {{ insert: param, si-01_odp.04 }} to manage the development, documentation, and dissemination of the system and information integrity policy and procedures; and
Review and update the current system and information integrity:
Policy {{ insert: param, si-01_odp.05 }} and following {{ insert: param, si-01_odp.06 }} ; and
Procedures {{ insert: param, si-01_odp.07 }} and following {{ insert: param, si-01_odp.08 }}.
System and information integrity policy and procedures address the controls in the SI family that are implemented within systems and organizations. The risk management strategy is an important factor in establishing such policies and procedures. Policies and procedures contribute to security and privacy assurance. Therefore, it is important that security and privacy programs collaborate on the development of system and information integrity policy and procedures. Security and privacy program policies and procedures at the organization level are preferable, in general, and may obviate the need for mission- or system-specific policies and procedures. The policy can be included as part of the general security and privacy policy or be represented by multiple policies that reflect the complex nature of organizations. Procedures can be established for security and privacy programs, for mission or business processes, and for systems, if needed. Procedures describe how the policies or controls are implemented and can be directed at the individual or role that is the object of the procedure. Procedures can be documented in system security and privacy plans or in one or more separate documents. Events that may precipitate an update to system and information integrity policy and procedures include assessment or audit findings, security incidents or breaches, or changes in applicable laws, executive orders, directives, regulations, policies, standards, and guidelines. Simply restating controls does not constitute an organizational policy or procedure.
a system and information integrity policy is developed and documented;
the system and information integrity policy is disseminated to {{ insert: param, si-01_odp.01 }};
system and information integrity procedures to facilitate the implementation of the system and information integrity policy and associated system and information integrity controls are developed and documented;
the system and information integrity procedures are disseminated to {{ insert: param, si-01_odp.02 }};
the {{ insert: param, si-01_odp.03 }} system and information integrity policy addresses purpose;
the {{ insert: param, si-01_odp.03 }} system and information integrity policy addresses scope;
the {{ insert: param, si-01_odp.03 }} system and information integrity policy addresses roles;
the {{ insert: param, si-01_odp.03 }} system and information integrity policy addresses responsibilities;
the {{ insert: param, si-01_odp.03 }} system and information integrity policy addresses management commitment;
the {{ insert: param, si-01_odp.03 }} system and information integrity policy addresses coordination among organizational entities;
the {{ insert: param, si-01_odp.03 }} system and information integrity policy addresses compliance;
the {{ insert: param, si-01_odp.03 }} system and information integrity policy is consistent with applicable laws, Executive Orders, directives, regulations, policies, standards, and guidelines;
the {{ insert: param, si-01_odp.04 }} is designated to manage the development, documentation, and dissemination of the system and information integrity policy and procedures;
the current system and information integrity policy is reviewed and updated {{ insert: param, si-01_odp.05 }};
the current system and information integrity policy is reviewed and updated following {{ insert: param, si-01_odp.06 }};
the current system and information integrity procedures are reviewed and updated {{ insert: param, si-01_odp.07 }};
the current system and information integrity procedures are reviewed and updated following {{ insert: param, si-01_odp.08 }}.
System and information integrity policy

system and information integrity procedures

system security plan

privacy plan

other relevant documents or records
Organizational personnel with system and information integrity responsibilities

organizational personnel with information security and privacy responsibilities*

---

### Sample Match 25: `MAS-C.1.9` ⟷ `NIST-SC-13`

* **Semantic Relation**: `SUBSET_OF`
* **Assurance Coverage**: `PARTIAL_COVERAGE` (Confidence: `0.85` | Dense Sim: `0.57`)
* **Retrieval Trace**: Multi-Intent RRF: 0.0277 (Max Dense Sim: 0.57)
* **Defensible Rationale**: Control B mandates general cryptographic protection mechanisms, which are the technical means to achieve device binding, but it does not explicitly require the specific 'device binding' logic or anti-cloning measures for software tokens. Requirement A is a specific application of cryptographic protection, making Control B a broader, enabling control that partially satisfies the mandate.

> **MAS TRM Clause [MAS-C.1.9]**:
> *The Financial Institution must implement device binding to protect the software token from being cloned.*

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

## Section C: Unmatched MAS Obligations (True Regulatory Gaps)

Total unmapped clauses: **1** (1.2%)

### Unmatched Clause 1: `MAS-14.3.3.b`

> **MAS TRM Statement**:
> *The Financial Institution must include meaningful information, such as transaction type and payment amount, along with instructions to report suspicious or unauthorized transactions, in customer notifications.*

* **Audit Analysis**: Evaluated against top 15 hybrid candidates. All candidates rejected by 2D Dual-Judge as `NONE` or below confidence threshold (0.70).

---

## Section D: 5 Sample MAS Obligations with Multiple Matches (1-to-N Mapping Clusters)

### Cluster 1: `MAS-1.3.a` maps to 15 NIST Controls

> **MAS TRM Statement [MAS-1.3.a]**:
> *The Financial Institution must evaluate its exposure to technology risks.*

#### Control 1: `NIST-RA-8` (Privacy Impact Assessments)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates Privacy Impact Assessments specifically for Personally Identifiable Information (PII) processing, which is a subset of technology risks. It does not address broader technology risks such as operational, financial, or non-PII data security vulnerabilities required by Requirement A.
> *Conduct privacy impact assessments for systems, programs, or other activities before:
Developing or procuring information technology that processes personally identifiable information; and
Initiating a new collection of personally identifiable inform...*

#### Control 2: `NIST-RA-6` (Technical Surveillance Countermeasures Survey)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates a specific physical/electronic counter-surveillance survey, which is a narrow technical activity. Requirement A requires a broad evaluation of all technology risks, meaning Control B only satisfies a small subset of the required risk assessment scope.
> *Employ a technical surveillance countermeasures survey at {{ insert: param, ra-06_odp.01 }} {{ insert: param, ra-06_odp.02 }}.
A technical surveillance countermeasures survey is a service provided by qualified personnel to detect the presence of tech...*

#### Control 3: `NIST-RA-3` (Risk Assessment)
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates a comprehensive risk assessment process that explicitly identifies threats, vulnerabilities, and likelihood/impact of harm, which directly fulfills the requirement to evaluate technology risk exposure. The control's inclusion of organizational, mission, and system-level perspectives ensures the evaluation covers the full scope of technology risks.
> *Conduct a risk assessment, including:
Identifying threats to and vulnerabilities in the system;
Determining the likelihood and magnitude of harm from unauthorized access, use, disclosure, disruption, modification, or destruction of the system, the in...*

#### Control 4: `NIST-SI-20` (Tainting)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements a specific technical mechanism (data tainting) for post-breach detection, which is a narrow component of the broader mandate in Requirement A to evaluate overall technology risk exposure. Requirement A necessitates a comprehensive risk assessment framework, whereas Control B only addresses one specific vector (data exfiltration) without covering other technology risks.
> *Embed data or capabilities in the following systems or system components to determine if organizational data has been exfiltrated or improperly removed from the organization: {{ insert: param, si-20_odp }}.
Many cyber-attacks target organizational in...*

#### Control 5: `NIST-SR-6` (Supplier Assessments and Reviews)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements a specific subset of technology risk evaluation focused exclusively on supply chain and supplier risks, whereas Requirement A mandates a comprehensive evaluation of all technology risks. Consequently, while B satisfies the supply chain component, it does not address other critical technology risk domains such as internal infrastructure, software vulnerabilities, or operational resilience.
> *Assess and review the supply chain-related risks associated with suppliers or contractors and the system, system component, or system service they provide {{ insert: param, sr-06_odp }}.
An assessment and review of supplier risk includes security and...*

#### Control 6: `NIST-RA-5` (Vulnerability Monitoring and Scanning)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates specific technical vulnerability scanning and remediation processes, which constitute a subset of the broader 'technology risk exposure' evaluation required by Requirement A. While Control B addresses technical vulnerabilities, it does not encompass the full spectrum of technology risks (e.g., operational, strategic, or third-party risks) required for a comprehensive exposure evaluation.
> *Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;
Employ vulnerability monitoring tools and techniques...*

#### Control 7: `NIST-SR-2` (Supply Chain Risk Management Plan)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates a specific plan for managing supply chain risks across the system lifecycle, which is a distinct subset of the broader 'technology risks' required by Requirement A. While Control B satisfies the mandate to evaluate risks related to external providers and supply chain integrity, it does not address other technology risk domains such as internal infrastructure, software vulnerabilities, or operational resilience.
> *Develop a plan for managing supply chain risks associated with the research and development, design, manufacturing, acquisition, delivery, integration, operations and maintenance, and disposal of the following systems, system components or system ser...*

#### Control 8: `NIST-PM-30` (Supply Chain Risk Management Strategy)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates a comprehensive strategy for supply chain risks (a specific subset of technology risks), whereas Requirement A requires a broader evaluation of all technology risk exposures. Implementing Control B satisfies the supply chain component but leaves other technology risk domains (e.g., infrastructure, software, operational) unevaluated.
> *Develop an organization-wide strategy for managing supply chain risks associated with the development, acquisition, maintenance, and disposal of systems, system components, and system services;
Implement the supply chain risk management strategy cons...*

#### Control 9: `NIST-CM-4` (Impact Analyses)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates impact analyses specifically for system changes, which is a subset of the broad, ongoing technology risk exposure evaluation required by Requirement A. While B provides evidence for change-related risks, it does not cover the full spectrum of technology risks (e.g., legacy systems, third-party vendors, or strategic technology adoption) required by A.
> *Analyze changes to the system to determine potential security and privacy impacts prior to change implementation.
Organizational personnel with security or privacy responsibilities conduct impact analyses. Individuals conducting impact analyses posse...*

#### Control 10: `NIST-SC-8` (Transmission Confidentiality and Integrity)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements specific technical safeguards for data transmission confidentiality and integrity, which is a single component of the broader, strategic mandate in Requirement A to evaluate overall technology risk exposure. Requirement A necessitates a comprehensive risk assessment process, whereas Control B only addresses one specific technical vector (transmission security) without fulfilling the evaluation mandate.
> *Protect the {{ insert: param, sc-08_odp }} of transmitted information.
Protecting the confidentiality and integrity of transmitted information applies to internal and external networks as well as any system components that can transmit information, i...*

#### Control 11: `NIST-PM-4` (Plan of Action and Milestones Process)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates the development and maintenance of remedial Plans of Action and Milestones (POAMs) based on risk findings, which is a downstream execution step. Requirement A requires the initial evaluation of technology risk exposure itself, a prerequisite activity not explicitly covered by the POAM process.
> *Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:
Are developed and maintained;
Document the remedial information ...*

#### Control 12: `NIST-PM-7` (Enterprise Architecture)
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Requirement A mandates a general evaluation of technology risk exposure, whereas Control B (NIST PM-7) specifically requires developing and maintaining an Enterprise Architecture that integrates security, privacy, and risk considerations. Control B provides the structural framework and artifacts (e.g., risk assessments of the EA) to address the mandate, but does not explicitly cover all non-architectural technology risk evaluations (e.g., operational or vendor-specific risks) required by the broader source obligation.
> *Develop and maintain an enterprise architecture with consideration for information security, privacy, and the resulting risk to organizational operations and assets, individuals, other organizations, and the Nation.
The integration of security and pr...*

#### Control 13: `NIST-SA-2` (Allocation of Resources)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates resource allocation and budgeting for information security and privacy, which is a necessary operational component of evaluating technology risk exposure. However, it does not encompass the broader analytical, identification, and assessment methodologies required to fully evaluate the institution's overall technology risk profile.
> *Determine the high-level information security and privacy requirements for the system or system service in mission and business process planning;
Determine, document, and allocate the resources required to protect the system or system service as part...*

#### Control 14: `NIST-PT-4` (Consent)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements specific consent mechanisms for PII processing, which addresses a subset of technology risks related to privacy and data handling. However, it does not satisfy the broad mandate of Requirement A to evaluate the institution's overall exposure to technology risks, which encompasses infrastructure, cybersecurity, and operational vulnerabilities beyond PII.
> *Implement {{ insert: param, pt-04_odp }} for individuals to consent to the processing of their personally identifiable information prior to its collection that facilitate individuals’ informed decision-making.
Consent allows individuals to participat...*

#### Control 15: `NIST-SI-19` (De-identification)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements a specific technical mandate for de-identifying PII, which is a subset of the broad, strategic obligation to evaluate overall technology risk exposure. While B satisfies the requirement to assess one specific technology risk (privacy/data integrity), it does not cover the full spectrum of technology risks (e.g., infrastructure, application, or network security) required by A.
> *Remove the following elements of personally identifiable information from datasets: {{ insert: param, si-19_odp.01 }} ; and
Evaluate {{ insert: param, si-19_odp.02 }} for effectiveness of de-identification.
De-identification is the general term for t...*

---

### Cluster 2: `MAS-1.3.b` maps to 15 NIST Controls

> **MAS TRM Statement [MAS-1.3.b]**:
> *The Financial Institution must implement a robust risk management framework to ensure IT and cyber resilience.*

#### Control 1: `NIST-PM-9` (Risk Management Strategy)
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B (NIST PM-9) mandates the development, implementation, and maintenance of a comprehensive, organization-wide risk management strategy that explicitly addresses security and privacy risks, directly fulfilling the requirement for a robust framework ensuring IT and cyber resilience.
> *Develops a comprehensive strategy to manage:
Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and
Privacy risk to individuals resu...*

#### Control 2: `NIST-SA-24` (Design For Cyber Resiliency)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates specific technical design and engineering processes for cyber resiliency, which is a core component of the broader 'robust risk management framework' required by Requirement A. However, Control B does not address the full scope of a risk management framework, such as governance, policy, or non-technical risk assessment activities.
> *Design organizational systems, system components, or system services to achieve cyber resiliency by:
Defining the following cyber resiliency goals: {{ insert: param, sa-24_odp.01 }}.
Defining the following cyber resiliency objectives: {{ insert: para...*

#### Control 3: `NIST-PM-4` (Plan of Action and Milestones Process)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B establishes a specific administrative process for documenting and tracking remedial actions (POA&M), which is a component of a broader risk management framework. Requirement A mandates a comprehensive, robust framework for IT and cyber resilience, encompassing prevention, detection, and response, whereas Control B only addresses the remediation tracking aspect.
> *Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:
Are developed and maintained;
Document the remedial information ...*

#### Control 4: `NIST-PM-7` (Enterprise Architecture)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B (NIST PM-7) mandates the development and maintenance of an enterprise architecture that integrates security and privacy considerations, which is a specific structural component of a broader risk management framework. Requirement A requires a comprehensive risk management framework for IT/cyber resilience, which encompasses PM-7 but also includes additional mandates such as incident response, business continuity, and active risk treatment beyond architectural planning.
> *Develop and maintain an enterprise architecture with consideration for information security, privacy, and the resulting risk to organizational operations and assets, individuals, other organizations, and the Nation.
The integration of security and pr...*

#### Control 5: `NIST-CP-2` (Contingency Plan)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements specific contingency planning and recovery procedures, which constitute only the 'resilience' component of the Source Requirement A's broader mandate for a comprehensive 'risk management framework' that must also include identification, assessment, and mitigation of risks.
> *Develop a contingency plan for the system that:
Identifies essential mission and business functions and associated contingency requirements;
Provides recovery objectives, restoration priorities, and metrics;
Addresses contingency roles, responsibilit...*

#### Control 6: `NIST-RA-3` (Risk Assessment)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates specific risk assessment activities (identification, analysis, documentation, and review), which constitute a critical component of Requirement A's broader 'robust risk management framework' that also requires implementation of controls, monitoring, and response strategies.
> *Conduct a risk assessment, including:
Identifying threats to and vulnerabilities in the system;
Determining the likelihood and magnitude of harm from unauthorized access, use, disclosure, disruption, modification, or destruction of the system, the in...*

#### Control 7: `NIST-PM-14` (Testing, Training, and Monitoring)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates specific processes for testing, training, and monitoring plans, which are operational components of a risk management framework. However, it does not encompass the full scope of a 'robust framework' required by Requirement A, such as risk identification, assessment, mitigation strategies, and governance structures.
> *Implement a process for ensuring that organizational plans for conducting security and privacy testing, training, and monitoring activities associated with organizational systems:
Are developed and maintained; and
Continue to be executed; and
Review ...*

#### Control 8: `NIST-RA-9` (Criticality Analysis)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates a specific technical activity (criticality analysis) that serves as a foundational input for risk management, whereas Requirement A demands a comprehensive, overarching risk management framework. Implementing Control B satisfies only the component identification aspect of the framework, leaving other critical mandates like risk assessment, mitigation, and monitoring unaddressed.
> *Identify critical system components and functions by performing a criticality analysis for {{ insert: param, ra-09_odp.01 }} at {{ insert: param, ra-09_odp.02 }}.
Not all system components, functions, or services necessarily require significant prote...*

#### Control 9: `NIST-PM-29` (Risk Management Program Leadership Roles)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B establishes specific governance roles and alignment mechanisms (Senior Accountable Official, Risk Executive) but does not mandate the comprehensive technical and operational components of a full risk management framework required by Requirement A.
> *Appoint a Senior Accountable Official for Risk Management to align organizational information security and privacy management processes with strategic, operational, and budgetary planning processes; and
Establish a Risk Executive (function) to view a...*

#### Control 10: `NIST-RA-5` (Vulnerability Monitoring and Scanning)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements specific technical vulnerability scanning and remediation mandates, which constitute a critical component of the broader 'robust risk management framework' required by Requirement A. However, Control B does not address other essential framework elements such as governance, policy, or comprehensive risk assessment methodologies.
> *Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;
Employ vulnerability monitoring tools and techniques...*

#### Control 11: `NIST-RA-7` (Risk Response)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements a specific risk response mechanism for assessment findings, which is a necessary component of a robust framework, but it does not encompass the broader scope of IT and cyber resilience mandates (e.g., architecture, continuity, or proactive resilience strategies) required by Requirement A.
> *Respond to findings from security and privacy assessments, monitoring, and audits in accordance with organizational risk tolerance.
Organizations have many options for responding to risk including mitigating risk by implementing new controls or stren...*

#### Control 12: `NIST-PL-8` (Security and Privacy Architectures)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates the development and maintenance of specific security and privacy architectures, which constitute a technical component of a broader risk management framework. Requirement A requires a comprehensive framework to ensure IT and cyber resilience, encompassing governance, operational procedures, and continuous monitoring beyond just architectural design.
> *Develop security and privacy architectures for the system that:
Describe the requirements and approach to be taken for protecting the confidentiality, integrity, and availability of organizational information;
Describe the requirements and approach t...*

#### Control 13: `NIST-CP-11` (Alternate Communications Protocols)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements a specific technical mechanism (alternate communications protocols) for continuity, which is a necessary component of the broader IT and cyber resilience framework mandated by Requirement A. However, Control B does not address other critical resilience pillars such as data backup, recovery site availability, or comprehensive risk assessment, leaving the full scope of Requirement A unmet.
> *Provide the capability to employ {{ insert: param, cp-11_odp }} in support of maintaining continuity of operations.
Contingency plans and the contingency training or testing associated with those plans incorporate an alternate communications protocol...*

#### Control 14: `NIST-SC-8` (Transmission Confidentiality and Integrity)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements a specific technical safeguard (transmission confidentiality and integrity) that is a necessary component of the broader, holistic risk management framework mandated by Requirement A. While B satisfies the technical resilience aspect of data in transit, it does not address the comprehensive governance, policy, and organizational structure required by the source framework.
> *Protect the {{ insert: param, sc-08_odp }} of transmitted information.
Protecting the confidentiality and integrity of transmitted information applies to internal and external networks as well as any system components that can transmit information, i...*

#### Control 15: `NIST-SA-3` (System Development Life Cycle)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates specific SDLC integration of security and privacy roles, which is a necessary component of a risk management framework, but it does not address the broader organizational governance, strategy, or continuous monitoring required by Requirement A's 'robust risk management framework' for overall IT and cyber resilience.
> *Acquire, develop, and manage the system using {{ insert: param, sa-03_odp }} that incorporates information security and privacy considerations;
Define and document information security and privacy roles and responsibilities throughout the system deve...*

---

### Cluster 3: `MAS-1.4(a).1` maps to 14 NIST Controls

> **MAS TRM Statement [MAS-1.4(a).1]**:
> *The Board of Directors and Senior Management must cultivate a strong risk culture.*

#### Control 1: `NIST-PM-29` (Risk Management Program Leadership Roles)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates specific structural roles (Senior Accountable Official, Risk Executive) and alignment with strategic planning, which are necessary components of a risk culture but do not fully capture the broader cultural cultivation and behavioral expectations required by Requirement A.
> *Appoint a Senior Accountable Official for Risk Management to align organizational information security and privacy management processes with strategic, operational, and budgetary planning processes; and
Establish a Risk Executive (function) to view a...*

#### Control 2: `NIST-PM-9` (Risk Management Strategy)
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates the development and implementation of a formal, documented risk management strategy with specific technical and procedural components, whereas Requirement A requires the broader, ongoing cultivation of a 'risk culture' by leadership. While Control B provides the structural foundation for risk management, it does not explicitly address the cultural, behavioral, or educational aspects necessary to fully satisfy the mandate of cultivating a strong risk culture.
> *Develops a comprehensive strategy to manage:
Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and
Privacy risk to individuals resu...*

#### Control 3: `NIST-PM-19` (Privacy Program Leadership Role)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates specific privacy leadership and risk management structures, which constitutes a subset of the broad, organization-wide risk culture required by Requirement A. While Control B provides a concrete governance mechanism, it does not address the holistic cultural cultivation across all risk domains required by the Source.
> *Appoint a senior agency official for privacy with the authority, mission, accountability, and resources to coordinate, develop, and implement, applicable privacy requirements and manage privacy risks through the organization-wide privacy program.
The...*

#### Control 4: `NIST-CA-6` (Authorization)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates specific technical and administrative actions for risk acceptance and system authorization by senior officials, which operationalizes the 'risk culture' requirement by establishing accountability. However, Control B is limited to information security authorization processes, whereas Requirement A encompasses a broader organizational risk culture that includes non-technical domains and general behavioral expectations.
> *Assign a senior official as the authorizing official for the system;
Assign a senior official as the authorizing official for common controls available for inheritance by organizational systems;
Ensure that the authorizing official for the system, be...*

#### Control 5: `NIST-PM-28` (Risk Framing)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements specific technical risk framing activities (documenting assumptions, constraints, and tolerance) which are necessary components of a risk culture, but it does not address the broader cultural cultivation, behavioral norms, or leadership tone required by Requirement A.
> *Identify and document:
Assumptions affecting risk assessments, risk responses, and risk monitoring;
Constraints affecting risk assessments, risk responses, and risk monitoring;
Priorities and trade-offs considered by the organization for managing ris...*

#### Control 6: `NIST-PM-2` (Information Security Program Leadership Role)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates the appointment and resourcing of a specific security officer to manage the technical information security program, which is a structural component of risk culture. However, Requirement A requires a broader cultural cultivation by the Board and Senior Management, encompassing behavioral norms and governance tone that Control B does not address.
> *Appoint a senior agency information security officer with the mission and resources to coordinate, develop, implement, and maintain an organization-wide information security program.
The senior agency information security officer is an organizational...*

#### Control 7: `NIST-PM-4` (Plan of Action and Milestones Process)
- **Semantic Relation**: `SUPPORTS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B establishes a formalized administrative process for documenting and tracking remedial actions (POA&M), which operationalizes risk management activities. However, it does not address the broader cultural mandate of Requirement A, which requires cultivating an organizational risk culture through leadership behavior, communication, and values rather than just procedural compliance.
> *Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:
Are developed and maintained;
Document the remedial information ...*

#### Control 8: `NIST-SA-3` (System Development Life Cycle)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements specific technical and procedural mandates for integrating security/privacy into the System Development Life Cycle (SDLC), which is a tangible manifestation of risk culture. However, Requirement A demands a broader organizational cultural cultivation by the Board and Senior Management, which Control B does not fully address as it focuses on operational execution rather than high-level cultural governance.
> *Acquire, develop, and manage the system using {{ insert: param, sa-03_odp }} that incorporates information security and privacy considerations;
Define and document information security and privacy roles and responsibilities throughout the system deve...*

#### Control 9: `NIST-PM-30` (Supply Chain Risk Management Strategy)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates a specific supply chain risk management strategy, which is a narrow subset of the broad 'risk culture' required by Requirement A. While Control B addresses technical supply chain risk governance, it does not fulfill the broader cultural mandate of cultivating organization-wide risk awareness and behavior across all business functions.
> *Develop an organization-wide strategy for managing supply chain risks associated with the development, acquisition, maintenance, and disposal of systems, system components, and system services;
Implement the supply chain risk management strategy cons...*

#### Control 10: `NIST-PM-12` (Insider Threat Program)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements specific technical and procedural mechanisms (monitoring, incident handling, training) that operationalize aspects of a risk culture, but Requirement A mandates a broader, holistic cultural cultivation by leadership that extends beyond the scope of an insider threat program.
> *Implement an insider threat program that includes a cross-discipline insider threat incident handling team.
Organizations that handle classified information are required, under Executive Order 13587 [EO 13587](#0af071a6-cf8e-48ee-8c82-fe91efa20f94) a...*

#### Control 11: `NIST-PM-14` (Testing, Training, and Monitoring)
- **Semantic Relation**: `SUPPORTS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B establishes operational processes for testing, training, and monitoring, which are essential mechanisms for executing a risk management strategy. However, it does not mandate the specific governance actions required by Requirement A, such as the Board and Senior Management actively cultivating the cultural environment and tone at the top.
> *Implement a process for ensuring that organizational plans for conducting security and privacy testing, training, and monitoring activities associated with organizational systems:
Are developed and maintained; and
Continue to be executed; and
Review ...*

#### Control 12: `NIST-PS-2` (Position Risk Designation)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements specific personnel security mechanisms (position risk designation and screening) that support the operational foundation of a risk culture, but it does not address the broader cultural cultivation, leadership tone, or behavioral mandates required by Requirement A.
> *Assign a risk designation to all organizational positions;
Establish screening criteria for individuals filling those positions; and
Review and update position risk designations {{ insert: param, ps-02_odp }}.
Position risk designations reflect Offic...*

#### Control 13: `NIST-PM-31` (Continuous Monitoring Strategy)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements specific technical and procedural mechanisms for continuous monitoring and reporting, which serve as operational evidence for risk management decisions. However, Requirement A mandates a broader cultural cultivation by leadership, which encompasses behavioral norms and governance beyond the scope of the technical monitoring strategy defined in Control B.
> *Develop an organization-wide continuous monitoring strategy and implement continuous monitoring programs that include:
Establishing the following organization-wide metrics to be monitored: {{ insert: param, pm-31_odp.01 }};
Establishing {{ insert: pa...*

#### Control 14: `NIST-SR-2` (Supply Chain Risk Management Plan)
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Requirement A mandates a broad organizational risk culture driven by leadership, whereas Control B implements a specific technical and procedural supply chain risk management plan. Control B addresses only one vertical of risk management (supply chain) rather than the holistic cultural mandate.
> *Develop a plan for managing supply chain risks associated with the research and development, design, manufacturing, acquisition, delivery, integration, operations and maintenance, and disposal of the following systems, system components or system ser...*

---

### Cluster 4: `MAS-1.4(a).2` maps to 13 NIST Controls

> **MAS TRM Statement [MAS-1.4(a).2]**:
> *The Board of Directors and Senior Management must establish a sound and robust technology risk management framework.*

#### Control 1: `NIST-PM-29` (Risk Management Program Leadership Roles)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates specific leadership roles and alignment with strategic planning, which constitutes a necessary component of a robust framework, but it does not encompass the full scope of framework establishment (e.g., risk assessment methodologies, monitoring, and reporting) required by Requirement A.
> *Appoint a Senior Accountable Official for Risk Management to align organizational information security and privacy management processes with strategic, operational, and budgetary planning processes; and
Establish a Risk Executive (function) to view a...*

#### Control 2: `NIST-PM-9` (Risk Management Strategy)
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B (NIST PM-9) mandates the development, implementation, and maintenance of a comprehensive, organization-wide risk management strategy, which directly operationalizes the requirement for a sound and robust technology risk management framework. The control's specific mechanisms for strategy alignment, risk tolerance definition, and consistent execution satisfy the structural and governance mandates of Requirement A.
> *Develops a comprehensive strategy to manage:
Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and
Privacy risk to individuals resu...*

#### Control 3: `NIST-SR-2` (Supply Chain Risk Management Plan)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements a specific Supply Chain Risk Management (SCRM) plan, which is a single component of the broader Technology Risk Management Framework mandated by Requirement A. While SCRM is a critical element of technology risk, Requirement A necessitates a holistic framework covering all risk domains (e.g., operational, financial, strategic, compliance), not just supply chain.
> *Develop a plan for managing supply chain risks associated with the research and development, design, manufacturing, acquisition, delivery, integration, operations and maintenance, and disposal of the following systems, system components or system ser...*

#### Control 4: `NIST-PM-23` (Data Governance Body)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B establishes a specific Data Governance Body to manage data utility, security, and privacy, which is a necessary component of a technology risk framework. However, Requirement A mandates a comprehensive framework covering all technology risks, whereas Control B is limited to data governance and does not address broader IT infrastructure, operational, or strategic technology risks.
> *Establish a Data Governance Body consisting of {{ insert: param, pm-23_odp.01 }} with {{ insert: param, pm-23_odp.02 }}.
A Data Governance Body can help ensure that the organization has coherent policies and the ability to balance the utility of data...*

#### Control 5: `NIST-PM-7` (Enterprise Architecture)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements a specific technical artifact (Enterprise Architecture) that supports risk management, whereas Requirement A mandates the broader governance framework established by the Board and Senior Management. Control B addresses the technical integration of security into architecture but does not satisfy the overarching governance and strategic mandate of the full technology risk management framework.
> *Develop and maintain an enterprise architecture with consideration for information security, privacy, and the resulting risk to organizational operations and assets, individuals, other organizations, and the Nation.
The integration of security and pr...*

#### Control 6: `NIST-RA-3` (Risk Assessment)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates specific technical risk assessment procedures (NIST RA-3), which is a core component of a technology risk management framework, but it does not address the broader governance, policy establishment, and organizational structure requirements for the framework itself mandated by Requirement A.
> *Conduct a risk assessment, including:
Identifying threats to and vulnerabilities in the system;
Determining the likelihood and magnitude of harm from unauthorized access, use, disclosure, disruption, modification, or destruction of the system, the in...*

#### Control 7: `NIST-PM-28` (Risk Framing)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B (NIST PM-28) implements the specific 'Risk Framing' activity, which is a foundational component of a technology risk management framework, but it does not encompass the full scope of establishing a 'sound and robust' framework, which requires additional elements like risk assessment, response, and monitoring controls.
> *Identify and document:
Assumptions affecting risk assessments, risk responses, and risk monitoring;
Constraints affecting risk assessments, risk responses, and risk monitoring;
Priorities and trade-offs considered by the organization for managing ris...*

#### Control 8: `NIST-PS-2` (Position Risk Designation)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements specific personnel security mechanisms (position risk designation and screening) which are a necessary component of a technology risk management framework, but it does not encompass the broader strategic governance, policy establishment, and comprehensive risk management mandates required by Requirement A.
> *Assign a risk designation to all organizational positions;
Establish screening criteria for individuals filling those positions; and
Review and update position risk designations {{ insert: param, ps-02_odp }}.
Position risk designations reflect Offic...*

#### Control 9: `NIST-PM-31` (Continuous Monitoring Strategy)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements a specific technical mechanism (continuous monitoring) that supports the broader mandate of Requirement A to establish a comprehensive technology risk management framework. While B provides the operational data and feedback loop necessary for risk management, it does not encompass the full scope of framework establishment, such as governance structure, policy definition, or resource allocation.
> *Develop an organization-wide continuous monitoring strategy and implement continuous monitoring programs that include:
Establishing the following organization-wide metrics to be monitored: {{ insert: param, pm-31_odp.01 }};
Establishing {{ insert: pa...*

#### Control 10: `NIST-PM-4` (Plan of Action and Milestones Process)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements a specific operational process for Plans of Action and Milestones (POA&M), which is a component of risk response, whereas Requirement A mandates the establishment of the entire sound and robust technology risk management framework. Control B addresses the remediation and tracking aspect of the framework but does not encompass the broader governance, strategy, or comprehensive structure required by Requirement A.
> *Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:
Are developed and maintained;
Document the remedial information ...*

#### Control 11: `NIST-PM-14` (Testing, Training, and Monitoring)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements specific operational processes for testing, training, and monitoring, which are components of a risk management framework, but it does not address the broader mandate for the Board and Senior Management to establish the overarching governance structure and strategic framework required by Requirement A.
> *Implement a process for ensuring that organizational plans for conducting security and privacy testing, training, and monitoring activities associated with organizational systems:
Are developed and maintained; and
Continue to be executed; and
Review ...*

#### Control 12: `NIST-PM-1` (Information Security Program Plan)
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B (NIST PM-1) mandates the development, dissemination, and senior official approval of an organization-wide information security program plan, which structurally constitutes the 'sound and robust technology risk management framework' required by Source A. The control's specific requirements for management commitment, role assignment, and coordination directly operationalize the governance mandate of Source A.
> *Develop and disseminate an organization-wide information security program plan that:
Provides an overview of the requirements for the security program and a description of the security program management controls and common controls in place or plann...*

#### Control 13: `NIST-SR-3` (Supply Chain Controls and Processes)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements specific supply chain risk management processes, which constitute a single domain within the broader 'sound and robust technology risk management framework' mandated by Requirement A. While Control B satisfies the supply chain component, it does not address other critical framework elements such as general IT governance, operational security, or enterprise-wide risk assessment.
> *Establish a process or processes to identify and address weaknesses or deficiencies in the supply chain elements and processes of {{ insert: param, sr-03_odp.01 }} in coordination with {{ insert: param, sr-03_odp.02 }};
Employ the following controls ...*

---

### Cluster 5: `MAS-1.4(b).1` maps to 15 NIST Controls

> **MAS TRM Statement [MAS-1.4(b).1]**:
> *The Financial Institution must adopt a defence-in-depth approach to strengthen cyber resilience.*

#### Control 1: `NIST-SA-24` (Design For Cyber Resiliency)
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates the systematic design and implementation of cyber resiliency goals, objectives, and principles, which constitutes the specific technical execution of the 'defence-in-depth' strategy required by Requirement A. By integrating these resiliency mechanisms into the systems security engineering process, Control B fully satisfies the mandate to strengthen cyber resilience.
> *Design organizational systems, system components, or system services to achieve cyber resiliency by:
Defining the following cyber resiliency goals: {{ insert: param, sa-24_odp.01 }}.
Defining the following cyber resiliency objectives: {{ insert: para...*

#### Control 2: `NIST-RA-10` (Threat Hunting)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Requirement A mandates a comprehensive 'defence-in-depth' strategy encompassing all layers of security controls, whereas Control B implements only the specific 'threat hunting' component, which is a single active defense layer within that broader framework.
> *Establish and maintain a cyber threat hunting capability to:
Search for indicators of compromise in organizational systems; and
Detect, track, and disrupt threats that evade existing controls; and
Employ the threat hunting capability {{ insert: param...*

#### Control 3: `NIST-PL-8` (Security and Privacy Architectures)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: NIST-PL-8 mandates the development of formal security and privacy architecture documentation and their integration with enterprise architecture, which is a specific structural component of the broader 'defence-in-depth' strategy required by Requirement A. However, PL-8 focuses on architectural design and documentation rather than the comprehensive implementation of layered technical controls (e.g., network segmentation, defense mechanisms) necessary to fully satisfy the operational resilience aspect of defence-in-depth.
> *Develop security and privacy architectures for the system that:
Describe the requirements and approach to be taken for protecting the confidentiality, integrity, and availability of organizational information;
Describe the requirements and approach t...*

#### Control 4: `NIST-CP-2` (Contingency Plan)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Requirement A mandates a comprehensive 'defence-in-depth' strategy encompassing prevention, detection, and response controls, whereas Control B is strictly limited to contingency planning and recovery operations. While Control B addresses the resilience aspect of defence-in-depth, it does not implement the broader preventive and detective layers required by the source obligation.
> *Develop a contingency plan for the system that:
Identifies essential mission and business functions and associated contingency requirements;
Provides recovery objectives, restoration priorities, and metrics;
Addresses contingency roles, responsibilit...*

#### Control 5: `NIST-CP-11` (Alternate Communications Protocols)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements a specific technical mechanism (alternate communications protocols) for continuity, which is a single component of the broader 'defence-in-depth' strategy mandated by Requirement A. Requirement A necessitates a multi-layered security architecture, whereas Control B only addresses the resilience of communication channels.
> *Provide the capability to employ {{ insert: param, cp-11_odp }} in support of maintaining continuity of operations.
Contingency plans and the contingency training or testing associated with those plans incorporate an alternate communications protocol...*

#### Control 6: `NIST-IR-8` (Incident Response Plan)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: The Source Requirement mandates a comprehensive 'defence-in-depth' strategy encompassing prevention, detection, and response controls, whereas Control B is strictly limited to the 'Incident Response' component of that broader security architecture.
> *Develop an incident response plan that:
Provides the organization with a roadmap for implementing its incident response capability;
Describes the structure and organization of the incident response capability;
Provides a high-level approach for how t...*

#### Control 7: `NIST-PM-4` (Plan of Action and Milestones Process)
- **Semantic Relation**: `SUPPORTS` | **Assurance Coverage**: `NO_COVERAGE` (Conf: `0.85`)
- **Rationale**: Requirement A mandates a specific technical architecture (defence-in-depth) for cyber resilience, whereas Control B establishes a governance process for documenting and tracking remedial actions (POA&M) without defining the technical security controls themselves.
> *Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:
Are developed and maintained;
Document the remedial information ...*

#### Control 8: `NIST-SI-20` (Tainting)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Requirement A mandates a comprehensive defence-in-depth strategy encompassing prevention, detection, and response layers, whereas Control B implements only a specific deception-based detection mechanism (tainting) to identify data exfiltration, which is a single component of the broader resilience framework.
> *Embed data or capabilities in the following systems or system components to determine if organizational data has been exfiltrated or improperly removed from the organization: {{ insert: param, si-20_odp }}.
Many cyber-attacks target organizational in...*

#### Control 9: `NIST-PL-2` (System Security and Privacy Plans)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: NIST-PL-2 mandates the development of a formal security and privacy plan, which is a specific administrative component of a broader defense-in-depth strategy. While the plan documents the controls, it does not itself implement the technical, physical, and administrative layers required for comprehensive cyber resilience.
> *Develop security and privacy plans for the system that:
Are consistent with the organization’s enterprise architecture;
Explicitly define the constituent system components;
Describe the operational context of the system in terms of mission and busine...*

#### Control 10: `NIST-RA-9` (Criticality Analysis)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates a specific analytical process (criticality analysis) to identify and prioritize system components, which is a foundational prerequisite for implementing a defense-in-depth strategy. However, Control B does not enforce the actual deployment of layered technical safeguards or the holistic architectural design required by Requirement A.
> *Identify critical system components and functions by performing a criticality analysis for {{ insert: param, ra-09_odp.01 }} at {{ insert: param, ra-09_odp.02 }}.
Not all system components, functions, or services necessarily require significant prote...*

#### Control 11: `NIST-PM-9` (Risk Management Strategy)
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B establishes a comprehensive, organization-wide risk management strategy covering security, privacy, and supply chain risks, which is a broader governance framework than the specific technical mandate of 'defence-in-depth' in Requirement A. While the strategy provides the necessary policy foundation, it does not explicitly mandate the implementation of specific layered technical controls required for defence-in-depth.
> *Develops a comprehensive strategy to manage:
Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and
Privacy risk to individuals resu...*

#### Control 12: `NIST-RA-5` (Vulnerability Monitoring and Scanning)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements a specific technical component (vulnerability monitoring and remediation) of the broader 'defence-in-depth' strategy mandated by Requirement A. While B satisfies the vulnerability management aspect, it does not encompass the full scope of defence-in-depth, which also requires network segmentation, access controls, and other layered security mechanisms.
> *Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;
Employ vulnerability monitoring tools and techniques...*

#### Control 13: `NIST-RA-7` (Risk Response)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B defines a procedural framework for responding to specific assessment findings based on risk tolerance, which is a component of defense-in-depth. However, it does not mandate the architectural implementation of layered security controls required by the broader 'defense-in-depth' scope of Requirement A.
> *Respond to findings from security and privacy assessments, monitoring, and audits in accordance with organizational risk tolerance.
Organizations have many options for responding to risk including mitigating risk by implementing new controls or stren...*

#### Control 14: `NIST-IR-9` (Information Spillage Response)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements a specific technical response mechanism for information spills, which is a single component of the broader 'defence-in-depth' strategy mandated by Requirement A. While B satisfies the containment aspect of resilience, it does not address the comprehensive, multi-layered preventive and detective controls required by A.
> *Respond to information spills by:
Assigning {{ insert: param, ir-09_odp.01 }} with responsibility for responding to information spills;
Identifying the specific information involved in the system contamination;
Alerting {{ insert: param, ir-09_odp.02...*

#### Control 15: `NIST-CA-7` (Continuous Monitoring)
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Requirement A mandates a broad 'defence-in-depth' strategy encompassing multiple layers of security controls, whereas Control B (NIST CA-7) specifically implements only the continuous monitoring component of that strategy. Control B provides the necessary ongoing assessment mechanism but does not address the other layers (e.g., access control, physical security) required for a complete defence-in-depth posture.
> *Develop a system-level continuous monitoring strategy and implement continuous monitoring in accordance with the organization-level continuous monitoring strategy that includes:
Establishing the following system-level metrics to be monitored: {{ inse...*

---

## Section E: 5 Sample NIST Controls with Multiple Matches (N-to-1 Mapping Clusters)

### Cluster 1: `NIST-RA-8` (Privacy Impact Assessments) addresses 4 MAS Obligations

> **NIST Control Statement [NIST-RA-8]**:
> *Conduct privacy impact assessments for systems, programs, or other activities before:
Developing or procuring information technology that processes personally identifiable information; and
Initiating a new collection of personally identifiable information that:
Will be processed using information te...*

#### MAS Clause 1: `MAS-1.3.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates Privacy Impact Assessments specifically for Personally Identifiable Information (PII) processing, which is a subset of technology risks. It does not address broader technology risks such as operational, financial, or non-PII data security vulnerabilities required by Requirement A.
> *The Financial Institution must evaluate its exposure to technology risks.*

#### MAS Clause 2: `MAS-7.3.2.b`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `NO_COVERAGE` (Conf: `0.85`)
- **Rationale**: Requirement A mandates a general risk assessment for hardware/software nearing end-of-support, whereas Control B restricts assessments to privacy impacts of Personally Identifiable Information (PII) processing. Control B does not address the technical security risks or operational continuity associated with end-of-support lifecycle states.
> *The Financial Institution must conduct a risk assessment for hardware and software approaching their end-of-support date.*

#### MAS Clause 3: `MAS-13.6.1.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates Privacy Impact Assessments (PIAs) which include privacy risk analysis, but is strictly scoped to Personally Identifiable Information (PII) and privacy compliance. Requirement A requires a general severity assessment and classification for all issues, which is a broader operational mandate not fully covered by the specific privacy-focused scope of Control B.
> *The Financial Institution must perform severity assessment and classification of an issue.*

#### MAS Clause 4: `MAS-15.1.2.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates Privacy Impact Assessments (PIAs) specifically for Personally Identifiable Information (PII) handling, which constitutes only a subset of the broad 'technology risk' domain required by Source A. While PIAs provide auditable evidence for privacy-related technology risks, they do not address the comprehensive set of non-privacy technology risks (e.g., infrastructure, application security, availability) required for a full technology risk assessment.
> *The Financial Institution must identify a comprehensive set of auditable areas for technology risk to enable effective risk assessment during audit planning.*

---

### Cluster 2: `NIST-RA-3` (Risk Assessment) addresses 16 MAS Obligations

> **NIST Control Statement [NIST-RA-3]**:
> *Conduct a risk assessment, including:
Identifying threats to and vulnerabilities in the system;
Determining the likelihood and magnitude of harm from unauthorized access, use, disclosure, disruption, modification, or destruction of the system, the information it processes, stores, or transmits, and ...*

#### MAS Clause 1: `MAS-1.3.a`
- **Semantic Relation**: `EQUIVALENT` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates a comprehensive risk assessment process that explicitly identifies threats, vulnerabilities, and likelihood/impact of harm, which directly fulfills the requirement to evaluate technology risk exposure. The control's inclusion of organizational, mission, and system-level perspectives ensures the evaluation covers the full scope of technology risks.
> *The Financial Institution must evaluate its exposure to technology risks.*

#### MAS Clause 2: `MAS-1.3.b`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates specific risk assessment activities (identification, analysis, documentation, and review), which constitute a critical component of Requirement A's broader 'robust risk management framework' that also requires implementation of controls, monitoring, and response strategies.
> *The Financial Institution must implement a robust risk management framework to ensure IT and cyber resilience.*

#### MAS Clause 3: `MAS-1.4(a).2`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates specific technical risk assessment procedures (NIST RA-3), which is a core component of a technology risk management framework, but it does not address the broader governance, policy establishment, and organizational structure requirements for the framework itself mandated by Requirement A.
> *The Board of Directors and Senior Management must establish a sound and robust technology risk management framework.*

#### MAS Clause 4: `MAS-6.5.2`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates a comprehensive risk assessment process to identify threats and vulnerabilities, which is a prerequisite for managing shadow IT, but it does not explicitly mandate the specific technical controls or monitoring mechanisms required to actively control and monitor unauthorized IT usage.
> *The Financial Institution must establish measures to control and monitor the use of shadow IT within its environment.*

#### MAS Clause 5: `MAS-6.5.3.a`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates a comprehensive, system-wide risk assessment framework covering threats, vulnerabilities, and privacy impacts, which is broader than Requirement A's specific focus on end-user applications. While Control B's scope encompasses the general risk assessment process, it does not explicitly isolate or mandate the specific procedural controls for 'end-user developed or acquired applications' required by Requirement A.
> *The Financial Institution must establish a process to assess the risk of end-user developed or acquired applications.*

#### MAS Clause 6: `MAS-7.1.1`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates specific technical risk assessment activities (identifying threats/vulnerabilities, determining likelihood/impact), which are a subset of the broader IT service management framework required by Requirement A. Requirement A necessitates a comprehensive governance structure and operational processes for IT service management, whereas Control B focuses exclusively on the risk assessment component without addressing the full scope of IT service delivery, governance, or procedural management.
> *The Financial Institution must establish an IT service management framework comprising governance structures, processes, and procedures for IT service management activities.*

#### MAS Clause 7: `MAS-7.3.2.b`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates a comprehensive, ongoing risk assessment framework covering organizational, mission, and system levels, whereas Requirement A specifically targets the narrower scope of hardware and software approaching end-of-support. While Control B's broad threat and vulnerability identification mechanisms can encompass end-of-support risks, it does not explicitly mandate the specific lifecycle trigger required by Requirement A.
> *The Financial Institution must conduct a risk assessment for hardware and software approaching their end-of-support date.*

#### MAS Clause 8: `MAS-7.5.6.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates a comprehensive, ongoing risk assessment process covering threats, vulnerabilities, and impacts, but lacks the specific procedural mandates for the approval and implementation of emergency changes required by Requirement A. While B provides the necessary risk analysis component, it does not address the change management workflow (approval/implementation) for emergency scenarios.
> *The Financial Institution must define procedures for assessing, approving, and implementing emergency changes to reduce the risk to the security and stability of the production environment.*

#### MAS Clause 9: `MAS-13.4.1`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `NO_COVERAGE` (Conf: `0.85`)
- **Rationale**: Requirement A mandates a specific technical validation activity (adversarial attack simulation) to test defense effectiveness, whereas Control B defines a broader, continuous governance process for identifying threats and vulnerabilities without requiring active exploitation or simulation testing.
> *The Financial Institution must perform an adversarial attack simulation exercise to test and validate the effectiveness of its cyber defence and response plan against prevalent cyber threats.*

#### MAS Clause 10: `MAS-13.4.2.b`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates the identification of threats and vulnerabilities causing disruption, but Requirement A specifically requires the execution of the exercise under 'close supervision' to prevent operational disruption. Control B addresses the analytical scope of risk but lacks the procedural mandate for supervised execution to ensure production stability.
> *The Financial Institution must conduct the exercise in a controlled manner under close supervision to prevent disruption to its production systems.*

#### MAS Clause 11: `MAS-13.5.1`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: NIST-RA-3 mandates a comprehensive risk assessment covering threat identification, vulnerability analysis, and impact determination, which inherently includes designing threat scenarios. However, Requirement A specifically targets the 'design of threat scenarios' for 'simulating realistic adversarial attacks' (implying active testing/simulation), whereas NIST-RA-3 is a broader, passive risk analysis control that does not explicitly mandate the active simulation component.
> *The Financial Institution must design the threat scenario based on challenging but plausible cyber threats to simulate realistic adversarial attacks during any cyber security assessment.*

#### MAS Clause 12: `MAS-13.5.2.a`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates a comprehensive risk assessment that includes identifying threats, whereas Requirement A specifically requires the use of threat intelligence to identify threat actors. While Control B covers the identification of threats, it does not explicitly mandate the utilization of external threat intelligence sources, which is a specific technical mechanism required by Requirement A.
> *The Financial Institution must use threat intelligence relevant to its IT environment to identify threat actors most likely to pose a threat.*

#### MAS Clause 13: `MAS-13.6.1.a`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates a comprehensive risk assessment that inherently includes the identification of threats and vulnerabilities, which necessitates the severity assessment and classification of issues required by Requirement A. Control B's scope is broader, covering likelihood, magnitude of harm, and integration with organizational perspectives, thereby fully satisfying the specific mandate of Requirement A.
> *The Financial Institution must perform severity assessment and classification of an issue.*

#### MAS Clause 14: `MAS-13.6.1.c`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates the execution and documentation of risk assessments but does not explicitly require the development of mitigation strategies to manage deviations, which is a distinct mandate in Requirement A. Therefore, Control B satisfies the identification and analysis components but leaves the mitigation strategy development unaddressed.
> *The Financial Institution must develop risk assessment and mitigation strategies to manage deviations from the framework.*

#### MAS Clause 15: `MAS-15.1.1`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates technical risk assessment activities (identifying threats/vulnerabilities, determining likelihood/impact), which are a necessary component of the internal controls evaluated in Requirement A. However, Control B lacks the specific mandate for an independent, objective IT audit function and the formal reporting mechanism to the board and senior management required by Requirement A.
> *The Financial Institution must conduct IT audit to provide the board of directors and senior management an independent and objective opinion on the adequacy and effectiveness of risk management, governance, and internal controls relative to existing and emerging technology risks.*

#### MAS Clause 16: `MAS-15.1.2.a`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates a comprehensive, ongoing risk assessment process covering threats, vulnerabilities, and impacts, which inherently includes identifying auditable areas. However, Requirement A specifically targets the pre-planning phase of identifying these areas for audit purposes, whereas Control B is a broader operational control that does not explicitly mandate the creation of an 'auditable areas' inventory for audit planning.
> *The Financial Institution must identify a comprehensive set of auditable areas for technology risk to enable effective risk assessment during audit planning.*

---

### Cluster 3: `NIST-SI-20` (Tainting) addresses 6 MAS Obligations

> **NIST Control Statement [NIST-SI-20]**:
> *Embed data or capabilities in the following systems or system components to determine if organizational data has been exfiltrated or improperly removed from the organization: {{ insert: param, si-20_odp }}.
Many cyber-attacks target organizational information, or information that the organization ho...*

#### MAS Clause 1: `MAS-1.3.a`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements a specific technical mechanism (data tainting) for post-breach detection, which is a narrow component of the broader mandate in Requirement A to evaluate overall technology risk exposure. Requirement A necessitates a comprehensive risk assessment framework, whereas Control B only addresses one specific vector (data exfiltration) without covering other technology risks.
> *The Financial Institution must evaluate its exposure to technology risks.*

#### MAS Clause 2: `MAS-1.4(b).1`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Requirement A mandates a comprehensive defence-in-depth strategy encompassing prevention, detection, and response layers, whereas Control B implements only a specific deception-based detection mechanism (tainting) to identify data exfiltration, which is a single component of the broader resilience framework.
> *The Financial Institution must adopt a defence-in-depth approach to strengthen cyber resilience.*

#### MAS Clause 3: `MAS-1.4(b).2`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements a specific technical mechanism (data tainting) to detect data exfiltration, which addresses the 'integrity' and 'availability' aspects of Requirement A. However, it does not cover the broader mandates for establishing comprehensive IT processes, controls, or mechanisms for preserving 'confidentiality' and general system integrity.
> *The Financial Institution must establish IT processes and controls to preserve the confidentiality, integrity, and availability of data and IT systems.*

#### MAS Clause 4: `MAS-14.1.2`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `NO_COVERAGE` (Conf: `0.85`)
- **Rationale**: Requirement A mandates proactive security measures for communication channels to prevent data exposure, whereas Control B implements post-breach detection mechanisms (tainting) to identify data that has already been exfiltrated. Control B does not secure the channels themselves, leaving the primary mandate of Requirement A unaddressed.
> *The Financial Institution must secure its communications channels to protect customer data.*

#### MAS Clause 5: `MAS-14.1.6.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Requirement A mandates proactive monitoring for phishing campaigns targeting the institution and its customers, whereas Control B implements data tainting specifically to detect post-exfiltration data compromise. While both address information security, Control B focuses on detecting data theft after a breach rather than actively monitoring for the phishing campaigns themselves.
> *The Financial Institution must actively monitor for phishing campaigns targeting the Financial Institution and its customers.*

#### MAS Clause 6: `MAS-Annex B.B.1.a`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements a specific technical mechanism (data tainting) for post-exfiltration detection, which is a subset of the broader mandate in Requirement A to implement comprehensive data loss prevention measures. Requirement A necessitates proactive prevention controls, whereas Control B only addresses reactive detection of data that has already been removed.
> *The Financial Institution must implement data loss prevention measures on personal computing or mobile devices used to access its information assets.*

---

### Cluster 4: `NIST-SR-6` (Supplier Assessments and Reviews) addresses 4 MAS Obligations

> **NIST Control Statement [NIST-SR-6]**:
> *Assess and review the supply chain-related risks associated with suppliers or contractors and the system, system component, or system service they provide {{ insert: param, sr-06_odp }}.
An assessment and review of supplier risk includes security and supply chain risk management processes, foreign o...*

#### MAS Clause 1: `MAS-1.3.a`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements a specific subset of technology risk evaluation focused exclusively on supply chain and supplier risks, whereas Requirement A mandates a comprehensive evaluation of all technology risks. Consequently, while B satisfies the supply chain component, it does not address other critical technology risk domains such as internal infrastructure, software vulnerabilities, or operational resilience.
> *The Financial Institution must evaluate its exposure to technology risks.*

#### MAS Clause 2: `MAS-6.5.3.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates supply chain risk assessments for external suppliers, which is a specific subset of the broader requirement to assess risks for all end-user developed or acquired applications. It does not cover internally developed applications or non-supplier acquisition channels, leaving residual regulatory requirements unmet.
> *The Financial Institution must establish a process to assess the risk of end-user developed or acquired applications.*

#### MAS Clause 3: `MAS-6.5.3.b`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements specific supply chain risk management processes (NIST SR-6), which is a distinct subset of the broad, organization-wide risk controls mandated by Requirement A. While B addresses a critical risk vector, it does not cover the full spectrum of identified risks required by A.
> *The Financial Institution must implement appropriate controls and security measures to address identified risks.*

#### MAS Clause 4: `MAS-15.1.1`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements a specific technical mandate for supply chain risk assessment, which is a single component of the broad, independent IT audit required by Requirement A to evaluate overall risk management, governance, and internal controls.
> *The Financial Institution must conduct IT audit to provide the board of directors and senior management an independent and objective opinion on the adequacy and effectiveness of risk management, governance, and internal controls relative to existing and emerging technology risks.*

---

### Cluster 5: `NIST-RA-5` (Vulnerability Monitoring and Scanning) addresses 23 MAS Obligations

> **NIST Control Statement [NIST-RA-5]**:
> *Monitor and scan for vulnerabilities in the system and hosted applications {{ insert: param, ra-5_prm_1 }} and when new vulnerabilities potentially affecting the system are identified and reported;
Employ vulnerability monitoring tools and techniques that facilitate interoperability among tools and ...*

#### MAS Clause 1: `MAS-1.3.a`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates specific technical vulnerability scanning and remediation processes, which constitute a subset of the broader 'technology risk exposure' evaluation required by Requirement A. While Control B addresses technical vulnerabilities, it does not encompass the full spectrum of technology risks (e.g., operational, strategic, or third-party risks) required for a comprehensive exposure evaluation.
> *The Financial Institution must evaluate its exposure to technology risks.*

#### MAS Clause 2: `MAS-1.3.b`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements specific technical vulnerability scanning and remediation mandates, which constitute a critical component of the broader 'robust risk management framework' required by Requirement A. However, Control B does not address other essential framework elements such as governance, policy, or comprehensive risk assessment methodologies.
> *The Financial Institution must implement a robust risk management framework to ensure IT and cyber resilience.*

#### MAS Clause 3: `MAS-1.4(b).1`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B implements a specific technical component (vulnerability monitoring and remediation) of the broader 'defence-in-depth' strategy mandated by Requirement A. While B satisfies the vulnerability management aspect, it does not encompass the full scope of defence-in-depth, which also requires network segmentation, access controls, and other layered security mechanisms.
> *The Financial Institution must adopt a defence-in-depth approach to strengthen cyber resilience.*

#### MAS Clause 4: `MAS-6.5.2`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates technical vulnerability scanning and remediation for known system flaws, which is a component of shadow IT monitoring, but it lacks the specific governance, inventory, and access control measures required to identify and restrict unauthorized IT assets (shadow IT) themselves.
> *The Financial Institution must establish measures to control and monitor the use of shadow IT within its environment.*

#### MAS Clause 5: `MAS-6.5.3.a`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates specific technical vulnerability scanning and remediation processes, which constitute a subset of the broader risk assessment process required by Requirement A. Control B does not address the full scope of risk assessment for end-user applications, such as business logic evaluation or non-technical risk factors.
> *The Financial Institution must establish a process to assess the risk of end-user developed or acquired applications.*

#### MAS Clause 6: `MAS-6.5.3.d`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates continuous vulnerability scanning and remediation for existing systems, whereas Requirement A specifically targets pre-deployment testing for end-user developed or acquired applications. While Control B's mention of static/dynamic analysis for custom software provides some technical overlap, it does not fully satisfy the specific pre-deployment validation mandate for end-user applications.
> *The Financial Institution must conduct proper testing before deploying end-user developed or acquired applications.*

#### MAS Clause 7: `MAS-7.2.2`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `FULL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates comprehensive vulnerability monitoring, scanning, and remediation of hardware/software configurations, which inherently fulfills the requirement to review and verify configuration information. Control B extends beyond simple verification by requiring active scanning, risk-based remediation, and continuous monitoring processes.
> *The Financial Institution must review and verify the configuration information of its hardware and software on a regular basis.*

#### MAS Clause 8: `MAS-7.3.1.a`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates active vulnerability scanning, analysis, and remediation of software flaws, which inherently addresses the 'unsupported software' aspect of Requirement A. However, Control B lacks explicit mandates for the physical lifecycle management or replacement of 'outdated hardware,' leaving that specific component of Requirement A unaddressed.
> *The Financial Institution must avoid using outdated and unsupported hardware or software.*

#### MAS Clause 9: `MAS-7.3.1.b`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates comprehensive vulnerability monitoring, scanning, and remediation processes, which inherently require tracking software end-of-support dates to identify unpatched flaws, but it extends far beyond this single requirement to include hardware scanning, risk-based remediation, and external disclosure programs.
> *The Financial Institution must closely monitor the end-of-support dates of its hardware and software.*

#### MAS Clause 10: `MAS-7.3.2.b`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates continuous vulnerability monitoring and scanning for active flaws, which is a distinct technical process from Requirement A's specific mandate to assess hardware and software nearing end-of-support dates. While EoS status is a risk factor, Control B does not explicitly require the proactive identification or risk assessment of assets based on their support lifecycle status.
> *The Financial Institution must conduct a risk assessment for hardware and software approaching their end-of-support date.*

#### MAS Clause 11: `MAS-7.3.2.c`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates active vulnerability scanning and remediation of identified flaws, which addresses the security risks of end-of-support software, but it does not explicitly require the proactive lifecycle management, decommissioning, or replacement strategies necessary to mitigate the inherent risks of unsupported hardware and software.
> *The Financial Institution must implement effective risk mitigation measures for hardware and software approaching their end-of-support date.*

#### MAS Clause 12: `MAS-7.7.1`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B (NIST RA-5) focuses on proactive vulnerability identification and remediation, whereas Requirement A mandates a reactive incident management framework for restoring services post-incident. While vulnerability remediation is a component of incident response, Control B lacks the comprehensive incident handling, containment, and recovery procedures required by Requirement A.
> *The Financial Institution must establish an incident management framework to restore affected IT services or systems to a secure and stable state as quickly as possible, minimizing impact to the business and customers.*

#### MAS Clause 13: `MAS-13.4.1`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates systematic vulnerability scanning and remediation, which is a component of defense validation, but it lacks the specific requirement for active adversarial attack simulations (e.g., red teaming or penetration testing) to validate the cyber defense and response plan's effectiveness against prevalent threats.
> *The Financial Institution must perform an adversarial attack simulation exercise to test and validate the effectiveness of its cyber defence and response plan against prevalent cyber threats.*

#### MAS Clause 14: `MAS-13.5.1`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates technical vulnerability scanning and remediation, which is a component of threat simulation, but lacks the explicit requirement to design and execute comprehensive, scenario-based adversarial attack simulations (e.g., red teaming) required by Requirement A.
> *The Financial Institution must design the threat scenario based on challenging but plausible cyber threats to simulate realistic adversarial attacks during any cyber security assessment.*

#### MAS Clause 15: `MAS-13.5.2.b`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Requirement A mandates the identification of attacker tactics, techniques, and procedures (TTPs), whereas Control B focuses on technical vulnerability scanning and remediation. While identifying vulnerabilities is a component of understanding attack surfaces, Control B does not explicitly address the broader identification of adversary TTPs required by Requirement A.
> *The Financial Institution must identify the tactics, techniques, and procedures most likely to be used in such attacks.*

#### MAS Clause 16: `MAS-13.6.1`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates the technical remediation of specific vulnerabilities identified via automated scanning and monitoring, which satisfies the 'resolve issues' aspect of Requirement A. However, Control B is limited to vulnerability management and does not encompass the broader 'comprehensive remediation process' required for all issues identified from diverse sources like cyber security assessments or exercises.
> *The Financial Institution must establish a comprehensive remediation process to track and resolve issues identified from cyber security assessments or exercises.*

#### MAS Clause 17: `MAS-13.6.1.b`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates the remediation of vulnerabilities based on an organizational risk assessment, which inherently requires defining timeframes for different severity levels. However, Control B is a comprehensive vulnerability management framework that includes scanning, monitoring, and sharing, whereas Requirement A is strictly limited to the definition of remediation timeframes.
> *The Financial Institution must define a timeframe to remediate issues of different severity.*

#### MAS Clause 18: `MAS-13.6.1.c`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates specific technical vulnerability scanning, analysis, and remediation workflows, which constitute a subset of the broader 'risk assessment and mitigation strategies' required by Requirement A. While Control B addresses technical deviations (vulnerabilities), it does not cover the full scope of risk assessment strategies for non-technical or framework-level deviations.
> *The Financial Institution must develop risk assessment and mitigation strategies to manage deviations from the framework.*

#### MAS Clause 19: `MAS-14.1.3`
- **Semantic Relation**: `SUBSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates comprehensive vulnerability scanning and remediation, which directly addresses specific attack vectors like code injection and XSS mentioned in Requirement A. However, Requirement A explicitly includes network-level threats (DDoS, DNS hijacking, man-in-the-middle) that are not covered by the vulnerability scanning scope of Control B.
> *The Financial Institution must implement adequate measures to minimize exposure of its online financial services to common attack vectors such as code injection attacks, cross-site scripting, man-in-the-middle attacks, DNS hijacking, DDoS, malware, and spoofing attacks.*

#### MAS Clause 20: `MAS-14.1.4`
- **Semantic Relation**: `SUPERSET_OF` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates comprehensive vulnerability monitoring and scanning for all systems and hosted applications, which inherently includes mobile applications, but does not explicitly address the unique risks specific to the mobile platform (e.g., device management, app store distribution, or mobile-specific data storage). Requirement A specifically targets mobile-unique risks, which Control B addresses only as a subset of general application security.
> *The Financial Institution must implement specific measures aimed at addressing the risks unique to mobile applications.*

#### MAS Clause 21: `MAS-14.1.6.a`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates technical vulnerability monitoring and scanning for system infrastructure and applications, whereas Requirement A specifically targets phishing campaigns targeting the institution and its customers. While both involve threat monitoring, Control B does not address the social engineering aspect or customer-facing phishing vectors required by Requirement A.
> *The Financial Institution must actively monitor for phishing campaigns targeting the Financial Institution and its customers.*

#### MAS Clause 22: `MAS-C.1.4`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates vulnerability scanning and remediation for known flaws, which indirectly addresses runtime risks, but it lacks the specific technical mandate for anti-hooking or anti-tampering mechanisms required by Requirement A to prevent active code injection and runtime monitoring.
> *The Financial Institution must implement anti-hooking or anti-tampering mechanisms to prevent the injection of malicious code that could alter or monitor application behaviour at runtime.*

#### MAS Clause 23: `MAS-C.1.6`
- **Semantic Relation**: `OVERLAPS` | **Assurance Coverage**: `PARTIAL_COVERAGE` (Conf: `0.85`)
- **Rationale**: Control B mandates vulnerability scanning and remediation for systems and applications, which may incidentally detect obfuscation weaknesses, but it does not explicitly require the implementation of code obfuscation techniques to prevent reverse engineering as mandated by Requirement A.
> *The Financial Institution must implement code obfuscation techniques to prevent reverse engineering of the mobile application.*

---

