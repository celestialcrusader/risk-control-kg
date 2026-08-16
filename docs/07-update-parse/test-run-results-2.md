# Production Crosswalk Evaluation Results (MAS TRM 2021 ⟷ NIST SP 800-53 Rev 5)

**Retrieval Architecture**: Dense Neural Embeddings (BAAI/bge-small-en-v1.5) with Strict 5-kNN  
**Reasoning Engine**: Qwen 35B Dual-Judge Set-Theory NLI  
**Database Dual-Write**: PostgreSQL (`obligation_framework_mappings`) & Memgraph (`:CROSSWALKS_TO`)  
**Execution Date**: 2026-08-16  

---

## Section A: Match Statistics

| Metric | Value |
|---|---|
| **Total MAS TRM Obligations** | `85` |
| **Total NIST SP 800-53 Control Objectives** | `324` |
| **Total Active Crosswalk Links Formed** | `115` |
| **MAS Obligations Mapped ($\ge 1$ match)** | `51` (60.0%) |
| **MAS Obligations Unmapped (0 matches)** | `34` (40.0%) |

### Set-Theory Relationship Distribution

| Set Theory Relationship | Edge Count | Percentage |
|---|---|---|
| `SUPERSET_OF` | 89 | 77.4% |
| `SUBSET_OF` | 16 | 13.9% |
| `INTERSECTS_WITH` | 8 | 7.0% |
| `EQUIVALENT_TO` | 2 | 1.7% |

---

## Section B: 25 Sample Crosswalk Matches (Complete Verbatim Text)

### Sample Match 1: `MAS-1.3.a` ⟷ `NIST-RA-3`

* **Relation**: `SUPERSET_OF` (Confidence: `0.90` | Dense Cosine Sim: `0.63`)
* **Rationale**: Control B (RA-03) mandates a comprehensive, ongoing risk assessment process covering threats, vulnerabilities, likelihood, impact, and documentation, which fully encompasses the high-level obligation in Requirement A to evaluate technology risk exposure.

> **MAS TRM Clause [MAS-1.3.a]**:
> *The Financial Institution must evaluate its exposure to technology risks.*

> **NIST SP 800-53 Control [NIST-RA-3 - Risk Assessment]**:
> *Conduct a risk assessment, including:
> Identifying threats to and vulnerabilities in the system;
> Determining the likelihood and magnitude of harm from unauthorized access, use, disclosure, disruption, modification, or destruction of the system, the information it processes, stores, or transmits, and any related information; and
> Determining the likelihood and impact of adverse effects on individuals arising from the processing of personally identifiable information;
> Integrate risk assessment results and risk management decisions from the organization and mission or business process perspectives with system-level risk assessments;
> Document risk assessment results in {{ insert: param, ra-03_odp.01 }};
> Review risk assessment results {{ insert: param, ra-03_odp.03 }};
> Disseminate risk assessment*

---

### Sample Match 2: `MAS-1.3.a` ⟷ `NIST-RA-4`

* **Relation**: `SUPERSET_OF` (Confidence: `0.85` | Dense Cosine Sim: `0.62`)
* **Rationale**: Requirement A mandates a comprehensive evaluation of technology risk exposure, which is a specific component of the broader 'Risk Assessment Update' control. The control likely encompasses the requirement but also includes other risk assessment activities beyond just technology risks.

> **MAS TRM Clause [MAS-1.3.a]**:
> *The Financial Institution must evaluate its exposure to technology risks.*

> **NIST SP 800-53 Control [NIST-RA-4 - Risk Assessment Update]**:
> **

---

### Sample Match 3: `MAS-1.3.a` ⟷ `NIST-RA-7`

* **Relation**: `SUBSET_OF` (Confidence: `0.85` | Dense Cosine Sim: `0.61`)
* **Rationale**: Requirement A mandates the evaluation of technology risk exposure, which is a prerequisite step. Control B describes the subsequent action of responding to findings from assessments (which include risk evaluations) based on risk tolerance, making Control B a broader set of obligations that includes but extends beyond the initial evaluation.

> **MAS TRM Clause [MAS-1.3.a]**:
> *The Financial Institution must evaluate its exposure to technology risks.*

> **NIST SP 800-53 Control [NIST-RA-7 - Risk Response]**:
> *Respond to findings from security and privacy assessments, monitoring, and audits in accordance with organizational risk tolerance.
> Organizations have many options for responding to risk including mitigating risk by implementing new controls or strengthening existing controls, accepting risk with appropriate justification or rationale, sharing or transferring risk, or avoiding risk. The risk tolerance of the organization influences risk response decisions and actions. Risk response addresses the need to determine an appropriate response to risk before generating a plan of action and milestones entry. For example, the response may be to accept risk or reject risk, or it may be possible to mitigate the risk immediately so that a plan of action and milestones entry is not needed. However, if *

---

### Sample Match 4: `MAS-1.3.a` ⟷ `NIST-PM-28`

* **Relation**: `SUPERSET_OF` (Confidence: `0.85` | Dense Cosine Sim: `0.62`)
* **Rationale**: LLM Semantic Evaluation

> **MAS TRM Clause [MAS-1.3.a]**:
> *The Financial Institution must evaluate its exposure to technology risks.*

> **NIST SP 800-53 Control [NIST-PM-28 - Risk Framing]**:
> *Identify and document:
> Assumptions affecting risk assessments, risk responses, and risk monitoring;
> Constraints affecting risk assessments, risk responses, and risk monitoring;
> Priorities and trade-offs considered by the organization for managing risk; and
> Organizational risk tolerance;
> Distribute the results of risk framing activities to {{ insert: param, pm-28_odp.01 }} ; and
> Review and update risk framing considerations {{ insert: param, pm-28_odp.02 }}.
> Risk framing is most effective when conducted at the organization level and in consultation with stakeholders throughout the organization including mission, business, and system owners. The assumptions, constraints, risk tolerance, priorities, and trade-offs identified as part of the risk framing process inform the risk management strat*

---

### Sample Match 5: `MAS-1.3.a` ⟷ `NIST-SR-6`

* **Relation**: `INTERSECTS_WITH` (Confidence: `0.75` | Dense Cosine Sim: `0.62`)
* **Rationale**: Requirement A mandates a general evaluation of technology risks, while Control B specifically addresses supply chain risks associated with suppliers. Since supply chain risks are a subset of technology risks, the control intersects with the broader requirement but does not fully encompass it.

> **MAS TRM Clause [MAS-1.3.a]**:
> *The Financial Institution must evaluate its exposure to technology risks.*

> **NIST SP 800-53 Control [NIST-SR-6 - Supplier Assessments and Reviews]**:
> *Assess and review the supply chain-related risks associated with suppliers or contractors and the system, system component, or system service they provide {{ insert: param, sr-06_odp }}.
> An assessment and review of supplier risk includes security and supply chain risk management processes, foreign ownership, control or influence (FOCI), and the ability of the supplier to effectively assess subordinate second-tier and third-tier suppliers and contractors. The reviews may be conducted by the organization or by an independent third party. The reviews consider documented processes, documented controls, all-source intelligence, and publicly available information related to the supplier or contractor. Organizations can use open-source information to monitor for indications of stolen information,*

---

### Sample Match 6: `MAS-1.3.b` ⟷ `NIST-PM-29`

* **Relation**: `SUPERSET_OF` (Confidence: `0.85` | Dense Cosine Sim: `0.64`)
* **Rationale**: Control B details specific governance roles and processes (Senior Accountable Official, Risk Executive) that constitute a subset of the broader 'robust risk management framework' required by Requirement A. Requirement A is a high-level mandate, while Control B provides specific implementation steps that fall under that mandate.

> **MAS TRM Clause [MAS-1.3.b]**:
> *The Financial Institution must implement a robust risk management framework to ensure IT and cyber resilience.*

> **NIST SP 800-53 Control [NIST-PM-29 - Risk Management Program Leadership Roles]**:
> *Appoint a Senior Accountable Official for Risk Management to align organizational information security and privacy management processes with strategic, operational, and budgetary planning processes; and
> Establish a Risk Executive (function) to view and analyze risk from an organization-wide perspective and ensure management of risk is consistent across the organization.
> The senior accountable official for risk management leads the risk executive (function) in organization-wide risk management activities.
> a Senior Accountable Official for Risk Management is appointed;
> a Senior Accountable Official for Risk Management aligns information security and privacy management processes with strategic, operational, and budgetary planning processes;
> a Risk Executive (function) is established;
> a Risk E*

---

### Sample Match 7: `MAS-1.3.b` ⟷ `NIST-PM-9`

* **Relation**: `SUPERSET_OF` (Confidence: `0.90` | Dense Cosine Sim: `0.66`)
* **Rationale**: Control B (NIST PM-09) defines a comprehensive, organization-wide risk management strategy that explicitly includes security and privacy risks, which inherently covers IT and cyber resilience. Requirement A is a specific subset of this broader mandate, focusing solely on the IT/cyber aspect of the resilience framework.

> **MAS TRM Clause [MAS-1.3.b]**:
> *The Financial Institution must implement a robust risk management framework to ensure IT and cyber resilience.*

> **NIST SP 800-53 Control [NIST-PM-9 - Risk Management Strategy]**:
> *Develops a comprehensive strategy to manage:
> Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and
> Privacy risk to individuals resulting from the authorized processing of personally identifiable information;
> Implement the risk management strategy consistently across the organization; and
> Review and update the risk management strategy {{ insert: param, pm-09_odp }} or as required, to address organizational changes.
> An organization-wide risk management strategy includes an expression of the security and privacy risk tolerance for the organization, security and privacy risk mitigation strategies, acceptable risk assessment methodologies, a process for evaluating security and *

---

### Sample Match 8: `MAS-1.3.b` ⟷ `NIST-SA-24`

* **Relation**: `SUPERSET_OF` (Confidence: `0.85` | Dense Cosine Sim: `0.63`)
* **Rationale**: Control B provides a detailed, a comprehensive, prescriptive framework for designing cyber resiliency (goals, objectives, techniques, etc.) and integrating it into risk management processes, which fully encompasses the high-level obligation in Requirement A to implement a robust risk management framework for IT and cyber resilience.

> **MAS TRM Clause [MAS-1.3.b]**:
> *The Financial Institution must implement a robust risk management framework to ensure IT and cyber resilience.*

> **NIST SP 800-53 Control [NIST-SA-24 - Design For Cyber Resiliency]**:
> *Design organizational systems, system components, or system services to achieve cyber resiliency by:
> Defining the following cyber resiliency goals: {{ insert: param, sa-24_odp.01 }}.
> Defining the following cyber resiliency objectives: {{ insert: param, sa-24_odp.02 }}.
> Defining the following cyber resiliency techniques: {{ insert: param, sa-24_odp.03 }}.
> Defining the following cyber resiliency implementation approaches: {{ insert: param, sa-24_odp.04 }}.
> Defining the following cyber resiliency design principles: {{ insert: param, sa-24_odp.05 }}.
> Implement the selected cyber resiliency goals, objectives, techniques, implementation approaches, and design principles as part of an organizational risk management process or systems security engineering process.
> Cyber resiliency is critical to e*

---

### Sample Match 9: `MAS-1.3.b` ⟷ `NIST-PM-14`

* **Relation**: `SUPERSET_OF` (Confidence: `0.85` | Dense Cosine Sim: `0.62`)
* **Rationale**: LLM Semantic Evaluation

> **MAS TRM Clause [MAS-1.3.b]**:
> *The Financial Institution must implement a robust risk management framework to ensure IT and cyber resilience.*

> **NIST SP 800-53 Control [NIST-PM-14 - Testing, Training, and Monitoring]**:
> *Implement a process for ensuring that organizational plans for conducting security and privacy testing, training, and monitoring activities associated with organizational systems:
> Are developed and maintained; and
> Continue to be executed; and
> Review testing, training, and monitoring plans for consistency with the organizational risk management strategy and organization-wide priorities for risk response actions.
> A process for organization-wide security and privacy testing, training, and monitoring helps ensure that organizations provide oversight for testing, training, and monitoring activities and that those activities are coordinated. With the growing importance of continuous monitoring programs, the implementation of information security and privacy across the three levels of the risk ma*

---

### Sample Match 10: `MAS-1.3.b` ⟷ `NIST-RA-7`

* **Relation**: `SUPERSET_OF` (Confidence: `0.85` | Dense Cosine Sim: `0.62`)
* **Rationale**: LLM Semantic Evaluation

> **MAS TRM Clause [MAS-1.3.b]**:
> *The Financial Institution must implement a robust risk management framework to ensure IT and cyber resilience.*

> **NIST SP 800-53 Control [NIST-RA-7 - Risk Response]**:
> *Respond to findings from security and privacy assessments, monitoring, and audits in accordance with organizational risk tolerance.
> Organizations have many options for responding to risk including mitigating risk by implementing new controls or strengthening existing controls, accepting risk with appropriate justification or rationale, sharing or transferring risk, or avoiding risk. The risk tolerance of the organization influences risk response decisions and actions. Risk response addresses the need to determine an appropriate response to risk before generating a plan of action and milestones entry. For example, the response may be to accept risk or reject risk, or it may be possible to mitigate the risk immediately so that a plan of action and milestones entry is not needed. However, if *

---

### Sample Match 11: `MAS-1.4(a).1` ⟷ `NIST-PM-29`

* **Relation**: `SUPERSET_OF` (Confidence: `0.85` | Dense Cosine Sim: `0.69`)
* **Rationale**: Control B defines specific structural roles (Senior Accountable Official, Risk Executive) and processes to manage risk, which are risk, which serves as a concrete implementation mechanism for the broader cultural and leadership obligation described in Requirement A. While Control B is more specific, it does not fully capture the holistic 'cultivation of risk culture' aspect, making Requirement A the superset.

> **MAS TRM Clause [MAS-1.4(a).1]**:
> *The Board of Directors and Senior Management must cultivate a strong risk culture.*

> **NIST SP 800-53 Control [NIST-PM-29 - Risk Management Program Leadership Roles]**:
> *Appoint a Senior Accountable Official for Risk Management to align organizational information security and privacy management processes with strategic, operational, and budgetary planning processes; and
> Establish a Risk Executive (function) to view and analyze risk from an organization-wide perspective and ensure management of risk is consistent across the organization.
> The senior accountable official for risk management leads the risk executive (function) in organization-wide risk management activities.
> a Senior Accountable Official for Risk Management is appointed;
> a Senior Accountable Official for Risk Management aligns information security and privacy management processes with strategic, operational, and budgetary planning processes;
> a Risk Executive (function) is established;
> a Risk E*

---

### Sample Match 12: `MAS-1.4(a).1` ⟷ `NIST-PM-9`

* **Relation**: `SUPERSET_OF` (Confidence: `0.85` | Dense Cosine Sim: `0.60`)
* **Rationale**: Control B details the comprehensive development, implementation, and maintenance of a risk management strategy, which is the primary mechanism for cultivating the strong risk culture mandated by Requirement A. While Requirement A focuses on the cultural aspect driven by leadership, Control B provides the specific procedural framework and artifacts that operationalize this cultural obligation.

> **MAS TRM Clause [MAS-1.4(a).1]**:
> *The Board of Directors and Senior Management must cultivate a strong risk culture.*

> **NIST SP 800-53 Control [NIST-PM-9 - Risk Management Strategy]**:
> *Develops a comprehensive strategy to manage:
> Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and
> Privacy risk to individuals resulting from the authorized processing of personally identifiable information;
> Implement the risk management strategy consistently across the organization; and
> Review and update the risk management strategy {{ insert: param, pm-09_odp }} or as required, to address organizational changes.
> An organization-wide risk management strategy includes an expression of the security and privacy risk tolerance for the organization, security and privacy risk mitigation strategies, acceptable risk assessment methodologies, a process for evaluating security and *

---

### Sample Match 13: `MAS-1.4(a).2` ⟷ `NIST-PM-29`

* **Relation**: `SUPERSET_OF` (Confidence: `0.90` | Dense Cosine Sim: `0.65`)
* **Rationale**: Control B provides specific implementation details (appointing a Senior Accountable Official and establishing a Risk Executive function) that constitute the necessary components to fulfill the high-level obligation in Requirement A to establish a robust technology risk management framework.

> **MAS TRM Clause [MAS-1.4(a).2]**:
> *The Board of Directors and Senior Management must establish a sound and robust technology risk management framework.*

> **NIST SP 800-53 Control [NIST-PM-29 - Risk Management Program Leadership Roles]**:
> *Appoint a Senior Accountable Official for Risk Management to align organizational information security and privacy management processes with strategic, operational, and budgetary planning processes; and
> Establish a Risk Executive (function) to view and analyze risk from an organization-wide perspective and ensure management of risk is consistent across the organization.
> The senior accountable official for risk management leads the risk executive (function) in organization-wide risk management activities.
> a Senior Accountable Official for Risk Management is appointed;
> a Senior Accountable Official for Risk Management aligns information security and privacy management processes with strategic, operational, and budgetary planning processes;
> a Risk Executive (function) is established;
> a Risk E*

---

### Sample Match 14: `MAS-1.4(a).2` ⟷ `NIST-PM-9`

* **Relation**: `SUPERSET_OF` (Confidence: `0.90` | Dense Cosine Sim: `0.60`)
* **Rationale**: Control B details a comprehensive risk management strategy that includes security and privacy risks, implementation, and updates, which fully encompasses the high-level requirement in Requirement A for establishing a robust technology risk management framework. Control B provides the specific mechanisms and scope (including privacy and supply chain) that satisfy the general obligation in Requirement A.

> **MAS TRM Clause [MAS-1.4(a).2]**:
> *The Board of Directors and Senior Management must establish a sound and robust technology risk management framework.*

> **NIST SP 800-53 Control [NIST-PM-9 - Risk Management Strategy]**:
> *Develops a comprehensive strategy to manage:
> Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and
> Privacy risk to individuals resulting from the authorized processing of personally identifiable information;
> Implement the risk management strategy consistently across the organization; and
> Review and update the risk management strategy {{ insert: param, pm-09_odp }} or as required, to address organizational changes.
> An organization-wide risk management strategy includes an expression of the security and privacy risk tolerance for the organization, security and privacy risk mitigation strategies, acceptable risk assessment methodologies, a process for evaluating security and *

---

### Sample Match 15: `MAS-1.4(a).2` ⟷ `NIST-PM-4`

* **Relation**: `SUPERSET_OF` (Confidence: `0.85` | Dense Cosine Sim: `0.57`)
* **Rationale**: Control B describes a specific operational process (Plans of Action and Milestones) for tracking and remediating risks, which is a component of the broader 'sound and robust technology risk management framework' mandated by Requirement A. Requirement A establishes the overarching governance obligation, while Control B implements a specific mechanism within that framework.

> **MAS TRM Clause [MAS-1.4(a).2]**:
> *The Board of Directors and Senior Management must establish a sound and robust technology risk management framework.*

> **NIST SP 800-53 Control [NIST-PM-4 - Plan of Action and Milestones Process]**:
> *Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:
> Are developed and maintained;
> Document the remedial information security, privacy, and supply chain risk management actions to adequately respond to risk to organizational operations and assets, individuals, other organizations, and the Nation; and
> Are reported in accordance with established reporting requirements.
> Review plans of action and milestones for consistency with the organizational risk management strategy and organization-wide priorities for risk response actions.
> The plan of action and milestones is a key organizational document and is subject to reporting requirements established by the Office *

---

### Sample Match 16: `MAS-1.4(a).2` ⟷ `NIST-RA-7`

* **Relation**: `SUPERSET_OF` (Confidence: `0.85` | Dense Cosine Sim: `0.56`)
* **Rationale**: Requirement A mandates the establishment of a comprehensive technology risk management framework, which is a high-level governance obligation. Control B describes specific operational procedures for responding to risk findings within that framework. Therefore, Control B represents a subset of activities that would be governed by the framework required in Requirement A.

> **MAS TRM Clause [MAS-1.4(a).2]**:
> *The Board of Directors and Senior Management must establish a sound and robust technology risk management framework.*

> **NIST SP 800-53 Control [NIST-RA-7 - Risk Response]**:
> *Respond to findings from security and privacy assessments, monitoring, and audits in accordance with organizational risk tolerance.
> Organizations have many options for responding to risk including mitigating risk by implementing new controls or strengthening existing controls, accepting risk with appropriate justification or rationale, sharing or transferring risk, or avoiding risk. The risk tolerance of the organization influences risk response decisions and actions. Risk response addresses the need to determine an appropriate response to risk before generating a plan of action and milestones entry. For example, the response may be to accept risk or reject risk, or it may be possible to mitigate the risk immediately so that a plan of action and milestones entry is not needed. However, if *

---

### Sample Match 17: `MAS-1.4(b).1` ⟷ `NIST-SA-24`

* **Relation**: `SUPERSET_OF` (Confidence: `0.90` | Dense Cosine Sim: `0.66`)
* **Rationale**: Control B provides a comprehensive framework for designing and implementing cyber resiliency, which inherently includes the defense-in-depth approach mandated by Requirement A. Requirement A is a specific strategic principle that is fully covered and operationalized by the detailed design and implementation steps in Control B.

> **MAS TRM Clause [MAS-1.4(b).1]**:
> *The Financial Institution must adopt a defence-in-depth approach to strengthen cyber resilience.*

> **NIST SP 800-53 Control [NIST-SA-24 - Design For Cyber Resiliency]**:
> *Design organizational systems, system components, or system services to achieve cyber resiliency by:
> Defining the following cyber resiliency goals: {{ insert: param, sa-24_odp.01 }}.
> Defining the following cyber resiliency objectives: {{ insert: param, sa-24_odp.02 }}.
> Defining the following cyber resiliency techniques: {{ insert: param, sa-24_odp.03 }}.
> Defining the following cyber resiliency implementation approaches: {{ insert: param, sa-24_odp.04 }}.
> Defining the following cyber resiliency design principles: {{ insert: param, sa-24_odp.05 }}.
> Implement the selected cyber resiliency goals, objectives, techniques, implementation approaches, and design principles as part of an organizational risk management process or systems security engineering process.
> Cyber resiliency is critical to e*

---

### Sample Match 18: `MAS-1.4(b).1` ⟷ `NIST-SA-12`

* **Relation**: `SUPERSET_OF` (Confidence: `0.85` | Dense Cosine Sim: `0.62`)
* **Rationale**: The 'defence-in-depth' approach in Requirement A is a comprehensive security strategy that encompasses multiple layers of protection, including but not limited to supply chain security. Therefore, Requirement A is a broader concept that includes the specific obligation of 'Supply Chain Protection' found in Control B.

> **MAS TRM Clause [MAS-1.4(b).1]**:
> *The Financial Institution must adopt a defence-in-depth approach to strengthen cyber resilience.*

> **NIST SP 800-53 Control [NIST-SA-12 - Supply Chain Protection]**:
> **

---

### Sample Match 19: `MAS-1.4(b).1` ⟷ `NIST-RA-7`

* **Relation**: `INTERSECTS_WITH` (Confidence: `0.75` | Dense Cosine Sim: `0.62`)
* **Rationale**: Requirement A mandates a specific strategic approach (defense-in-depth) for cyber resilience, while Control B describes a general process for responding to assessment findings based on risk tolerance. While defense-in-depth is a valid risk mitigation strategy covered by Control B, Control B is broader and does not explicitly require the defense-in-depth approach.

> **MAS TRM Clause [MAS-1.4(b).1]**:
> *The Financial Institution must adopt a defence-in-depth approach to strengthen cyber resilience.*

> **NIST SP 800-53 Control [NIST-RA-7 - Risk Response]**:
> *Respond to findings from security and privacy assessments, monitoring, and audits in accordance with organizational risk tolerance.
> Organizations have many options for responding to risk including mitigating risk by implementing new controls or strengthening existing controls, accepting risk with appropriate justification or rationale, sharing or transferring risk, or avoiding risk. The risk tolerance of the organization influences risk response decisions and actions. Risk response addresses the need to determine an appropriate response to risk before generating a plan of action and milestones entry. For example, the response may be to accept risk or reject risk, or it may be possible to mitigate the risk immediately so that a plan of action and milestones entry is not needed. However, if *

---

### Sample Match 20: `MAS-1.4(b).1` ⟷ `NIST-PM-8`

* **Relation**: `SUPERSET_OF` (Confidence: `0.85` | Dense Cosine Sim: `0.61`)
* **Rationale**: Control B mandates the development, documentation, and updating of a Critical Infrastructure Protection Plan that addresses information security and privacy issues, which is a specific implementation of the broader 'defence-in-depth' and 'cyber resilience' strategy required by Requirement A. Control B is more specific in scope (critical infrastructure plans) while Requirement A is a general strategic obligation.

> **MAS TRM Clause [MAS-1.4(b).1]**:
> *The Financial Institution must adopt a defence-in-depth approach to strengthen cyber resilience.*

> **NIST SP 800-53 Control [NIST-PM-8 - Critical Infrastructure Plan]**:
> *Address information security and privacy issues in the development, documentation, and updating of a critical infrastructure and key resources protection plan.
> Protection strategies are based on the prioritization of critical assets and resources. The requirement and guidance for defining critical infrastructure and key resources and for preparing an associated critical infrastructure protection plan are found in applicable laws, executive orders, directives, policies, regulations, standards, and guidelines.
> information security issues are addressed in the development of a critical infrastructure and key resources protection plan;
> information security issues are addressed in the documentation of a critical infrastructure and key resources protection plan;
> information security issues are ad*

---

### Sample Match 21: `MAS-1.4(b).2` ⟷ `NIST-PM-17`

* **Relation**: `SUPERSET_OF` (Confidence: `0.85` | Dense Cosine Sim: `0.66`)
* **Rationale**: Control B is a specific implementation of Requirement A, focusing exclusively on the latter being a broad mandate for general IT security while the former details specific policies for protecting Controlled Unclassified Information on external systems.

> **MAS TRM Clause [MAS-1.4(b).2]**:
> *The Financial Institution must establish IT processes and controls to preserve the confidentiality, integrity, and availability of data and IT systems.*

> **NIST SP 800-53 Control [NIST-PM-17 - Protecting Controlled Unclassified Information on External Systems]**:
> *Establish policy and procedures to ensure that requirements for the protection of controlled unclassified information that is processed, stored or transmitted on external systems, are implemented in accordance with applicable laws, executive orders, directives, policies, regulations, and standards; and
> Review and update the policy and procedures {{ insert: param, pm-17_prm_1 }}.
> Controlled unclassified information is defined by the National Archives and Records Administration along with the safeguarding and dissemination requirements for such information and is codified in [32 CFR 2002](#91f992fb-f668-4c91-a50f-0f05b95ccee3) and, specifically for systems external to the federal organization, [32 CFR 2002.14h](https://www.govinfo.gov/content/pkg/CFR-2017-title32-vol6/xml/CFR-2017-title32-vo*

---

### Sample Match 22: `MAS-1.4(b).2` ⟷ `NIST-PM-7`

* **Relation**: `SUPERSET_OF` (Confidence: `0.85` | Dense Cosine Sim: `0.65`)
* **Rationale**: Control B (Enterprise Architecture) is a specific structural and governance mechanism that implements that inherently supports and encompasses the general IT process and control requirements for confidentiality, integrity, and availability outlined in Requirement A. Requirement A is a broad objective, while Control B provides the detailed architectural framework to achieve it.

> **MAS TRM Clause [MAS-1.4(b).2]**:
> *The Financial Institution must establish IT processes and controls to preserve the confidentiality, integrity, and availability of data and IT systems.*

> **NIST SP 800-53 Control [NIST-PM-7 - Enterprise Architecture]**:
> *Develop and maintain an enterprise architecture with consideration for information security, privacy, and the resulting risk to organizational operations and assets, individuals, other organizations, and the Nation.
> The integration of security and privacy requirements and controls into the enterprise architecture helps to ensure that security and privacy considerations are addressed throughout the system development life cycle and are explicitly related to the organization’s mission and business processes. The process of security and privacy requirements integration also embeds into the enterprise architecture and the organization’s security and privacy architectures consistent with the organizational risk management strategy. For PM-7, security and privacy architectures are developed at a*

---

### Sample Match 23: `MAS-1.4(b).2` ⟷ `NIST-SA-9`

* **Relation**: `SUPERSET_OF` (Confidence: `0.85` | Dense Cosine Sim: `0.65`)
* **Rationale**: Control B (SA-09) is a specific implementation of the general obligation in Requirement A, focusing exclusively on the security and privacy controls for external system service providers. Control B encompasses the establishment of processes and controls for confidentiality, integrity, and availability as required by A, but adds specific requirements for oversight, role definition, and ongoing monitoring of third-party providers.

> **MAS TRM Clause [MAS-1.4(b).2]**:
> *The Financial Institution must establish IT processes and controls to preserve the confidentiality, integrity, and availability of data and IT systems.*

> **NIST SP 800-53 Control [NIST-SA-9 - External System Services]**:
> *Require that providers of external system services comply with organizational security and privacy requirements and employ the following controls: {{ insert: param, sa-09_odp.01 }};
> Define and document organizational oversight and user roles and responsibilities with regard to external system services; and
> Employ the following processes, methods, and techniques to monitor control compliance by external service providers on an ongoing basis: {{ insert: param, sa-09_odp.02 }}.
> External system services are provided by an external provider, and the organization has no direct control over the implementation of the required controls or the assessment of control effectiveness. Organizations establish relationships with external service providers in a variety of ways, including through business pa*

---

### Sample Match 24: `MAS-1.4(b).2` ⟷ `NIST-SA-2`

* **Relation**: `SUPERSET_OF` (Confidence: `0.85` | Dense Cosine Sim: `0.64`)
* **Rationale**: Control B details specific resource allocation and budgeting processes required to support information security and privacy, which are essential components of the broader IT processes and controls mandated by Requirement A. Requirement A is a high-level obligation that encompasses the specific implementation steps outlined in Control B.

> **MAS TRM Clause [MAS-1.4(b).2]**:
> *The Financial Institution must establish IT processes and controls to preserve the confidentiality, integrity, and availability of data and IT systems.*

> **NIST SP 800-53 Control [NIST-SA-2 - Allocation of Resources]**:
> *Determine the high-level information security and privacy requirements for the system or system service in mission and business process planning;
> Determine, document, and allocate the resources required to protect the system or system service as part of the organizational capital planning and investment control process; and
> Establish a discrete line item for information security and privacy in organizational programming and budgeting documentation.
> Resource allocation for information security and privacy includes funding for system and services acquisition, sustainment, and supply chain-related risks throughout the system development life cycle.
> the high-level information security requirements for the system or system service are determined in mission and business process planning;
> the hig*

---

### Sample Match 25: `MAS-1.4(b).2` ⟷ `NIST-PL-8`

* **Relation**: `SUPERSET_OF` (Confidence: `0.90` | Dense Cosine Sim: `0.62`)
* **Rationale**: Control B (PL-8) mandates the development of comprehensive security and privacy architectures that explicitly include protecting confidentiality, integrity, and availability, which is the core obligation of Requirement A. Control B is a supersedes Requirement A by adding extensive requirements for privacy, enterprise architecture integration, and lifecycle management.

> **MAS TRM Clause [MAS-1.4(b).2]**:
> *The Financial Institution must establish IT processes and controls to preserve the confidentiality, integrity, and availability of data and IT systems.*

> **NIST SP 800-53 Control [NIST-PL-8 - Security and Privacy Architectures]**:
> *Develop security and privacy architectures for the system that:
> Describe the requirements and approach to be taken for protecting the confidentiality, integrity, and availability of organizational information;
> Describe the requirements and approach to be taken for processing personally identifiable information to minimize privacy risk to individuals;
> Describe how the architectures are integrated into and support the enterprise architecture; and
> Describe any assumptions about, and dependencies on, external systems and services;
> Review and update the architectures {{ insert: param, pl-08_odp }} to reflect changes in the enterprise architecture; and
> Reflect planned architecture changes in security and privacy plans, Concept of Operations (CONOPS), criticality analysis, organizational procedur*

---

## Section C: Unmatched MAS TRM Obligations (Gaps & True Non-Matches)

Total Unmatched Clauses: **34**

### Unmatched Clause 1: `MAS-6.5.1`

> **MAS TRM Statement**:
> *The Financial Institution must manage shadow IT as part of its information assets.*

* **Action Verb**: `manage`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 2: `MAS-6.5.2`

> **MAS TRM Statement**:
> *The Financial Institution must establish measures to control and monitor the use of shadow IT within its environment.*

* **Action Verb**: `establish`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 3: `MAS-6.5.3.c`

> **MAS TRM Statement**:
> *The Financial Institution must obtain approval before using end-user developed or acquired applications.*

* **Action Verb**: `obtain`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 4: `MAS-7.3.1.a`

> **MAS TRM Statement**:
> *The Financial Institution must avoid using outdated and unsupported hardware or software.*

* **Action Verb**: `avoid`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 5: `MAS-7.3.2.a`

> **MAS TRM Statement**:
> *The Financial Institution must develop a technology refresh plan for the replacement of hardware and software before they reach end-of-support.*

* **Action Verb**: `develop`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 6: `MAS-7.5.6.a`

> **MAS TRM Statement**:
> *The Financial Institution must define procedures for assessing, approving, and implementing emergency changes to reduce the risk to the security and stability of the production environment.*

* **Action Verb**: `define`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 7: `MAS-7.6.2`

> **MAS TRM Statement**:
> *The Financial Institution must implement controls to maintain traceability and integrity for all software codes moved between IT environments.*

* **Action Verb**: `implement`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 8: `MAS-13.4.2.b`

> **MAS TRM Statement**:
> *The Financial Institution must conduct the exercise in a controlled manner under close supervision to prevent disruption to its production systems.*

* **Action Verb**: `conduct`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 9: `MAS-13.5.1`

> **MAS TRM Statement**:
> *The Financial Institution must design the threat scenario based on challenging but plausible cyber threats to simulate realistic adversarial attacks during any cyber security assessment.*

* **Action Verb**: `design`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 10: `MAS-13.5.2.b`

> **MAS TRM Statement**:
> *The Financial Institution must identify the tactics, techniques, and procedures most likely to be used in such attacks.*

* **Action Verb**: `identify`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 11: `MAS-13.6.1.b`

> **MAS TRM Statement**:
> *The Financial Institution must define a timeframe to remediate issues of different severity.*

* **Action Verb**: `define`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 12: `MAS-14.1.3`

> **MAS TRM Statement**:
> *The Financial Institution must implement adequate measures to minimize exposure of its online financial services to common attack vectors such as code injection attacks, cross-site scripting, man-in-the-middle attacks, DNS hijacking, DDoS, malware, and spoofing attacks.*

* **Action Verb**: `implement`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 13: `MAS-14.1.6.c`

> **MAS TRM Statement**:
> *The Financial Institution must alert its customers of phishing campaigns and advise them of security measures to adopt to protect against phishing.*

* **Action Verb**: `alert`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 14: `MAS-14.2.11.a`

> **MAS TRM Statement**:
> *The Financial Institution must store authentication credentials, including biometric templates and passwords, in a form resistant to reverse engineering to safeguard their confidentiality.*

* **Action Verb**: `store`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 15: `MAS-14.3.2`

> **MAS TRM Statement**:
> *The Financial Institution must establish a process to investigate suspicious transactions or payments and ensure issues are adequately and promptly addressed.*

* **Action Verb**: `establish`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 16: `MAS-14.3.3.a`

> **MAS TRM Statement**:
> *The Financial Institution must notify customers of suspicious activities or funds transfers exceeding a threshold defined by the Financial Institution or the customers.*

* **Action Verb**: `notify`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 17: `MAS-14.3.3.b`

> **MAS TRM Statement**:
> *The Financial Institution must include meaningful information, such as transaction type and payment amount, along with instructions to report suspicious or unauthorized transactions, in customer notifications.*

* **Action Verb**: `include`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 18: `MAS-14.4.1.a`

> **MAS TRM Statement**:
> *The Financial Institution must inform customers of security best practices to adopt when using online financial services.*

* **Action Verb**: `inform`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 19: `MAS-14.4.1.b`

> **MAS TRM Statement**:
> *The Financial Institution must inform customers of measures to secure electronic devices used to access online financial services.*

* **Action Verb**: `inform`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 20: `MAS-14.4.2`

> **MAS TRM Statement**:
> *The Financial Institution must alert customers on a timely basis to new cyber threats so they can take precautionary measures.*

* **Action Verb**: `alert`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 21: `MAS-14.4.3`

> **MAS TRM Statement**:
> *The Financial Institution must advise customers on means to detect unauthorized transactions and to report security issues, suspicious activities, or suspected fraud promptly.*

* **Action Verb**: `advise`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 22: `MAS-15.1.1`

> **MAS TRM Statement**:
> *The Financial Institution must conduct IT audit to provide the board of directors and senior management an independent and objective opinion on the adequacy and effectiveness of risk management, governance, and internal controls relative to existing and emerging technology risks.*

* **Action Verb**: `conduct`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 23: `MAS-15.1.3`

> **MAS TRM Statement**:
> *The Financial Institution must set the frequency of IT audits to be commensurate with the criticality and risk posed by the IT information asset, function, or process.*

* **Action Verb**: `set`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 24: `MAS-15.1.4`

> **MAS TRM Statement**:
> *The Financial Institution must verify that IT auditors possess the requisite level of competency and skills to effectively assess and evaluate the adequacy of implemented IT policies, procedures, processes, and controls.*

* **Action Verb**: `verify`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 25: `MAS-15.1.2.b`

> **MAS TRM Statement**:
> *The Financial Institution must include all IT operations, functions, and processes within the auditable areas.*

* **Action Verb**: `include`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 26: `MAS-15.1.3.a`

> **MAS TRM Statement**:
> *The Financial Institution must set the frequency of IT audits commensurate with the criticality and risk posed by the IT information asset, function, or process.*

* **Action Verb**: `set`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 27: `MAS-15.1.4.a`

> **MAS TRM Statement**:
> *The Financial Institution must verify that its IT auditors possess the requisite level of competency and skills to effectively assess and evaluate the adequacy of implemented IT policies, procedures, processes, and controls.*

* **Action Verb**: `verify`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 28: `MAS-5.1.2`

> **MAS TRM Statement**:
> *The Financial Institution must verify personal devices before permitting network access to ensure they are not jailbroken, rooted, or compromised.*

* **Action Verb**: `verify`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 29: `MAS-5.1.3`

> **MAS TRM Statement**:
> *The Financial Institution must enable strict security policies within the virtual environment to restrict the copying and use of peripheral devices and prevent data leakage.*

* **Action Verb**: `enable`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 30: `MAS-C.1.1`

> **MAS TRM Statement**:
> *The Financial Institution must prevent storing or caching data in the mobile application to mitigate the risk of data compromise on the device.*

* **Action Verb**: `prevent`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 31: `MAS-C.1.5`

> **MAS TRM Statement**:
> *The Financial Institution must implement appropriate application integrity checks to verify the authenticity and integrity of the application.*

* **Action Verb**: `implement`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 32: `MAS-C.1.8`

> **MAS TRM Statement**:
> *The Financial Institution must implement a secure in-app keypad to mitigate against malware that captures keystrokes.*

* **Action Verb**: `implement`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 33: `MAS-C.1.9`

> **MAS TRM Statement**:
> *The Financial Institution must implement device binding to protect the software token from being cloned.*

* **Action Verb**: `implement`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

### Unmatched Clause 34: `MAS-OBL-01`

> **MAS TRM Statement**:
> *The organization must enforce MFA.*

* **Action Verb**: `enforce`
* **Audit Analysis**: Evaluated against top 5 nearest NIST candidates. All evaluated candidates were rejected by the Dual-Judge NLI (evaluated as NO_RELATIONSHIP or confidence < 0.70).

---

## Section D: 5 Sample MAS Obligations with Multiple Framework Matches (1-to-N)

### 1-to-N Case 1: `MAS-1.3.a` (5 Linked NIST Controls)

> **MAS TRM Statement**:
> *The Financial Institution must evaluate its exposure to technology risks.*

| Target NIST Control | Title | Relation | Confidence |
|---|---|---|---|
| `NIST-RA-3` | Risk Assessment | `SUPERSET_OF` | `0.90` |
| `NIST-RA-4` | Risk Assessment Update | `SUPERSET_OF` | `0.85` |
| `NIST-RA-7` | Risk Response | `SUBSET_OF` | `0.85` |
| `NIST-PM-28` | Risk Framing | `SUPERSET_OF` | `0.85` |
| `NIST-SR-6` | Supplier Assessments and Reviews | `INTERSECTS_WITH` | `0.75` |

#### Control Detail: `NIST-RA-3` (Risk Assessment)
* **Relation**: `SUPERSET_OF` (Conf: `0.90`)
> *Conduct a risk assessment, including:
> Identifying threats to and vulnerabilities in the system;
> Determining the likelihood and magnitude of harm from unauthorized access, use, disclosure, disruption, modification, or destruction of the system, the information it processes, stores, or transmits, and any related information; and
> Determining the likelihood and impact of adverse effects on individuals arising from the processing of personally identifiable information;
> Integrate risk assessment resul*

#### Control Detail: `NIST-RA-4` (Risk Assessment Update)
* **Relation**: `SUPERSET_OF` (Conf: `0.85`)
> **

#### Control Detail: `NIST-RA-7` (Risk Response)
* **Relation**: `SUBSET_OF` (Conf: `0.85`)
> *Respond to findings from security and privacy assessments, monitoring, and audits in accordance with organizational risk tolerance.
> Organizations have many options for responding to risk including mitigating risk by implementing new controls or strengthening existing controls, accepting risk with appropriate justification or rationale, sharing or transferring risk, or avoiding risk. The risk tolerance of the organization influences risk response decisions and actions. Risk response addresses the*

#### Control Detail: `NIST-PM-28` (Risk Framing)
* **Relation**: `SUPERSET_OF` (Conf: `0.85`)
> *Identify and document:
> Assumptions affecting risk assessments, risk responses, and risk monitoring;
> Constraints affecting risk assessments, risk responses, and risk monitoring;
> Priorities and trade-offs considered by the organization for managing risk; and
> Organizational risk tolerance;
> Distribute the results of risk framing activities to {{ insert: param, pm-28_odp.01 }} ; and
> Review and update risk framing considerations {{ insert: param, pm-28_odp.02 }}.
> Risk framing is most effective when co*

#### Control Detail: `NIST-SR-6` (Supplier Assessments and Reviews)
* **Relation**: `INTERSECTS_WITH` (Conf: `0.75`)
> *Assess and review the supply chain-related risks associated with suppliers or contractors and the system, system component, or system service they provide {{ insert: param, sr-06_odp }}.
> An assessment and review of supplier risk includes security and supply chain risk management processes, foreign ownership, control or influence (FOCI), and the ability of the supplier to effectively assess subordinate second-tier and third-tier suppliers and contractors. The reviews may be conducted by the organ*

---

### 1-to-N Case 2: `MAS-1.3.b` (5 Linked NIST Controls)

> **MAS TRM Statement**:
> *The Financial Institution must implement a robust risk management framework to ensure IT and cyber resilience.*

| Target NIST Control | Title | Relation | Confidence |
|---|---|---|---|
| `NIST-PM-29` | Risk Management Program Leadership Roles | `SUPERSET_OF` | `0.85` |
| `NIST-PM-9` | Risk Management Strategy | `SUPERSET_OF` | `0.90` |
| `NIST-SA-24` | Design For Cyber Resiliency | `SUPERSET_OF` | `0.85` |
| `NIST-PM-14` | Testing, Training, and Monitoring | `SUPERSET_OF` | `0.85` |
| `NIST-RA-7` | Risk Response | `SUPERSET_OF` | `0.85` |

#### Control Detail: `NIST-PM-29` (Risk Management Program Leadership Roles)
* **Relation**: `SUPERSET_OF` (Conf: `0.85`)
> *Appoint a Senior Accountable Official for Risk Management to align organizational information security and privacy management processes with strategic, operational, and budgetary planning processes; and
> Establish a Risk Executive (function) to view and analyze risk from an organization-wide perspective and ensure management of risk is consistent across the organization.
> The senior accountable official for risk management leads the risk executive (function) in organization-wide risk management ac*

#### Control Detail: `NIST-PM-9` (Risk Management Strategy)
* **Relation**: `SUPERSET_OF` (Conf: `0.90`)
> *Develops a comprehensive strategy to manage:
> Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and
> Privacy risk to individuals resulting from the authorized processing of personally identifiable information;
> Implement the risk management strategy consistently across the organization; and
> Review and update the risk management strategy {{ insert: param, pm-09_odp }} or as required*

#### Control Detail: `NIST-SA-24` (Design For Cyber Resiliency)
* **Relation**: `SUPERSET_OF` (Conf: `0.85`)
> *Design organizational systems, system components, or system services to achieve cyber resiliency by:
> Defining the following cyber resiliency goals: {{ insert: param, sa-24_odp.01 }}.
> Defining the following cyber resiliency objectives: {{ insert: param, sa-24_odp.02 }}.
> Defining the following cyber resiliency techniques: {{ insert: param, sa-24_odp.03 }}.
> Defining the following cyber resiliency implementation approaches: {{ insert: param, sa-24_odp.04 }}.
> Defining the following cyber resiliency d*

#### Control Detail: `NIST-PM-14` (Testing, Training, and Monitoring)
* **Relation**: `SUPERSET_OF` (Conf: `0.85`)
> *Implement a process for ensuring that organizational plans for conducting security and privacy testing, training, and monitoring activities associated with organizational systems:
> Are developed and maintained; and
> Continue to be executed; and
> Review testing, training, and monitoring plans for consistency with the organizational risk management strategy and organization-wide priorities for risk response actions.
> A process for organization-wide security and privacy testing, training, and monitorin*

#### Control Detail: `NIST-RA-7` (Risk Response)
* **Relation**: `SUPERSET_OF` (Conf: `0.85`)
> *Respond to findings from security and privacy assessments, monitoring, and audits in accordance with organizational risk tolerance.
> Organizations have many options for responding to risk including mitigating risk by implementing new controls or strengthening existing controls, accepting risk with appropriate justification or rationale, sharing or transferring risk, or avoiding risk. The risk tolerance of the organization influences risk response decisions and actions. Risk response addresses the*

---

### 1-to-N Case 3: `MAS-1.4(a).1` (2 Linked NIST Controls)

> **MAS TRM Statement**:
> *The Board of Directors and Senior Management must cultivate a strong risk culture.*

| Target NIST Control | Title | Relation | Confidence |
|---|---|---|---|
| `NIST-PM-29` | Risk Management Program Leadership Roles | `SUPERSET_OF` | `0.85` |
| `NIST-PM-9` | Risk Management Strategy | `SUPERSET_OF` | `0.85` |

#### Control Detail: `NIST-PM-29` (Risk Management Program Leadership Roles)
* **Relation**: `SUPERSET_OF` (Conf: `0.85`)
> *Appoint a Senior Accountable Official for Risk Management to align organizational information security and privacy management processes with strategic, operational, and budgetary planning processes; and
> Establish a Risk Executive (function) to view and analyze risk from an organization-wide perspective and ensure management of risk is consistent across the organization.
> The senior accountable official for risk management leads the risk executive (function) in organization-wide risk management ac*

#### Control Detail: `NIST-PM-9` (Risk Management Strategy)
* **Relation**: `SUPERSET_OF` (Conf: `0.85`)
> *Develops a comprehensive strategy to manage:
> Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and
> Privacy risk to individuals resulting from the authorized processing of personally identifiable information;
> Implement the risk management strategy consistently across the organization; and
> Review and update the risk management strategy {{ insert: param, pm-09_odp }} or as required*

---

### 1-to-N Case 4: `MAS-1.4(a).2` (4 Linked NIST Controls)

> **MAS TRM Statement**:
> *The Board of Directors and Senior Management must establish a sound and robust technology risk management framework.*

| Target NIST Control | Title | Relation | Confidence |
|---|---|---|---|
| `NIST-PM-29` | Risk Management Program Leadership Roles | `SUPERSET_OF` | `0.90` |
| `NIST-PM-9` | Risk Management Strategy | `SUPERSET_OF` | `0.90` |
| `NIST-PM-4` | Plan of Action and Milestones Process | `SUPERSET_OF` | `0.85` |
| `NIST-RA-7` | Risk Response | `SUPERSET_OF` | `0.85` |

#### Control Detail: `NIST-PM-29` (Risk Management Program Leadership Roles)
* **Relation**: `SUPERSET_OF` (Conf: `0.90`)
> *Appoint a Senior Accountable Official for Risk Management to align organizational information security and privacy management processes with strategic, operational, and budgetary planning processes; and
> Establish a Risk Executive (function) to view and analyze risk from an organization-wide perspective and ensure management of risk is consistent across the organization.
> The senior accountable official for risk management leads the risk executive (function) in organization-wide risk management ac*

#### Control Detail: `NIST-PM-9` (Risk Management Strategy)
* **Relation**: `SUPERSET_OF` (Conf: `0.90`)
> *Develops a comprehensive strategy to manage:
> Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and
> Privacy risk to individuals resulting from the authorized processing of personally identifiable information;
> Implement the risk management strategy consistently across the organization; and
> Review and update the risk management strategy {{ insert: param, pm-09_odp }} or as required*

#### Control Detail: `NIST-PM-4` (Plan of Action and Milestones Process)
* **Relation**: `SUPERSET_OF` (Conf: `0.85`)
> *Implement a process to ensure that plans of action and milestones for the information security, privacy, and supply chain risk management programs and associated organizational systems:
> Are developed and maintained;
> Document the remedial information security, privacy, and supply chain risk management actions to adequately respond to risk to organizational operations and assets, individuals, other organizations, and the Nation; and
> Are reported in accordance with established reporting requirement*

#### Control Detail: `NIST-RA-7` (Risk Response)
* **Relation**: `SUPERSET_OF` (Conf: `0.85`)
> *Respond to findings from security and privacy assessments, monitoring, and audits in accordance with organizational risk tolerance.
> Organizations have many options for responding to risk including mitigating risk by implementing new controls or strengthening existing controls, accepting risk with appropriate justification or rationale, sharing or transferring risk, or avoiding risk. The risk tolerance of the organization influences risk response decisions and actions. Risk response addresses the*

---

### 1-to-N Case 5: `MAS-1.4(b).1` (4 Linked NIST Controls)

> **MAS TRM Statement**:
> *The Financial Institution must adopt a defence-in-depth approach to strengthen cyber resilience.*

| Target NIST Control | Title | Relation | Confidence |
|---|---|---|---|
| `NIST-SA-24` | Design For Cyber Resiliency | `SUPERSET_OF` | `0.90` |
| `NIST-SA-12` | Supply Chain Protection | `SUPERSET_OF` | `0.85` |
| `NIST-RA-7` | Risk Response | `INTERSECTS_WITH` | `0.75` |
| `NIST-PM-8` | Critical Infrastructure Plan | `SUPERSET_OF` | `0.85` |

#### Control Detail: `NIST-SA-24` (Design For Cyber Resiliency)
* **Relation**: `SUPERSET_OF` (Conf: `0.90`)
> *Design organizational systems, system components, or system services to achieve cyber resiliency by:
> Defining the following cyber resiliency goals: {{ insert: param, sa-24_odp.01 }}.
> Defining the following cyber resiliency objectives: {{ insert: param, sa-24_odp.02 }}.
> Defining the following cyber resiliency techniques: {{ insert: param, sa-24_odp.03 }}.
> Defining the following cyber resiliency implementation approaches: {{ insert: param, sa-24_odp.04 }}.
> Defining the following cyber resiliency d*

#### Control Detail: `NIST-SA-12` (Supply Chain Protection)
* **Relation**: `SUPERSET_OF` (Conf: `0.85`)
> **

#### Control Detail: `NIST-RA-7` (Risk Response)
* **Relation**: `INTERSECTS_WITH` (Conf: `0.75`)
> *Respond to findings from security and privacy assessments, monitoring, and audits in accordance with organizational risk tolerance.
> Organizations have many options for responding to risk including mitigating risk by implementing new controls or strengthening existing controls, accepting risk with appropriate justification or rationale, sharing or transferring risk, or avoiding risk. The risk tolerance of the organization influences risk response decisions and actions. Risk response addresses the*

#### Control Detail: `NIST-PM-8` (Critical Infrastructure Plan)
* **Relation**: `SUPERSET_OF` (Conf: `0.85`)
> *Address information security and privacy issues in the development, documentation, and updating of a critical infrastructure and key resources protection plan.
> Protection strategies are based on the prioritization of critical assets and resources. The requirement and guidance for defining critical infrastructure and key resources and for preparing an associated critical infrastructure protection plan are found in applicable laws, executive orders, directives, policies, regulations, standards, an*

---

## Section E: 5 Sample NIST Controls with Multiple MAS Matches (N-to-1)

### N-to-1 Case 1: `NIST-RA-3` - Risk Assessment (6 MAS Obligations)

> **NIST Control Specification**:
> *Conduct a risk assessment, including:
> Identifying threats to and vulnerabilities in the system;
> Determining the likelihood and magnitude of harm from unauthorized access, use, disclosure, disruption, modification, or destruction of the system, the information it processes, stores, or transmits, and any related information; and
> Determining the likelihood and impact of adverse effects on individuals arising from the processing of personally identifiable information;
> Integrate risk assessment results and risk management decisions from the organization and mission or business process perspectives *

| Source MAS Clause | MAS Requirement Summary | Relation | Confidence |
|---|---|---|---|
| `MAS-1.3.a` | The Financial Institution must evaluate its exposure to technology risks. | `SUPERSET_OF` | `0.90` |
| `MAS-6.5.3.a` | The Financial Institution must establish a process to assess the risk of end-use... | `SUBSET_OF` | `0.85` |
| `MAS-7.3.2.b` | The Financial Institution must conduct a risk assessment for hardware and softwa... | `SUPERSET_OF` | `0.90` |
| `MAS-13.6.1.a` | The Financial Institution must perform severity assessment and classification of... | `INTERSECTS_WITH` | `0.85` |
| `MAS-13.6.1.c` | The Financial Institution must develop risk assessment and mitigation strategies... | `SUPERSET_OF` | `0.85` |
| `MAS-15.1.2.a` | The Financial Institution must identify a comprehensive set of auditable areas f... | `SUBSET_OF` | `0.85` |

---

### N-to-1 Case 2: `NIST-RA-7` - Risk Response (5 MAS Obligations)

> **NIST Control Specification**:
> *Respond to findings from security and privacy assessments, monitoring, and audits in accordance with organizational risk tolerance.
> Organizations have many options for responding to risk including mitigating risk by implementing new controls or strengthening existing controls, accepting risk with appropriate justification or rationale, sharing or transferring risk, or avoiding risk. The risk tolerance of the organization influences risk response decisions and actions. Risk response addresses the need to determine an appropriate response to risk before generating a plan of action and milestones*

| Source MAS Clause | MAS Requirement Summary | Relation | Confidence |
|---|---|---|---|
| `MAS-1.3.a` | The Financial Institution must evaluate its exposure to technology risks. | `SUBSET_OF` | `0.85` |
| `MAS-1.3.b` | The Financial Institution must implement a robust risk management framework to e... | `SUPERSET_OF` | `0.85` |
| `MAS-1.4(a).2` | The Board of Directors and Senior Management must establish a sound and robust t... | `SUPERSET_OF` | `0.85` |
| `MAS-1.4(b).1` | The Financial Institution must adopt a defence-in-depth approach to strengthen c... | `INTERSECTS_WITH` | `0.75` |
| `MAS-13.6.1.c` | The Financial Institution must develop risk assessment and mitigation strategies... | `SUPERSET_OF` | `0.85` |

---

### N-to-1 Case 3: `NIST-PM-28` - Risk Framing (2 MAS Obligations)

> **NIST Control Specification**:
> *Identify and document:
> Assumptions affecting risk assessments, risk responses, and risk monitoring;
> Constraints affecting risk assessments, risk responses, and risk monitoring;
> Priorities and trade-offs considered by the organization for managing risk; and
> Organizational risk tolerance;
> Distribute the results of risk framing activities to {{ insert: param, pm-28_odp.01 }} ; and
> Review and update risk framing considerations {{ insert: param, pm-28_odp.02 }}.
> Risk framing is most effective when conducted at the organization level and in consultation with stakeholders throughout the organization *

| Source MAS Clause | MAS Requirement Summary | Relation | Confidence |
|---|---|---|---|
| `MAS-1.3.a` | The Financial Institution must evaluate its exposure to technology risks. | `SUPERSET_OF` | `0.85` |
| `MAS-13.6.1.c` | The Financial Institution must develop risk assessment and mitigation strategies... | `SUPERSET_OF` | `0.85` |

---

### N-to-1 Case 4: `NIST-PM-29` - Risk Management Program Leadership Roles (5 MAS Obligations)

> **NIST Control Specification**:
> *Appoint a Senior Accountable Official for Risk Management to align organizational information security and privacy management processes with strategic, operational, and budgetary planning processes; and
> Establish a Risk Executive (function) to view and analyze risk from an organization-wide perspective and ensure management of risk is consistent across the organization.
> The senior accountable official for risk management leads the risk executive (function) in organization-wide risk management activities.
> a Senior Accountable Official for Risk Management is appointed;
> a Senior Accountable Offic*

| Source MAS Clause | MAS Requirement Summary | Relation | Confidence |
|---|---|---|---|
| `MAS-1.3.b` | The Financial Institution must implement a robust risk management framework to e... | `SUPERSET_OF` | `0.85` |
| `MAS-1.4(a).1` | The Board of Directors and Senior Management must cultivate a strong risk cultur... | `SUPERSET_OF` | `0.85` |
| `MAS-1.4(a).2` | The Board of Directors and Senior Management must establish a sound and robust t... | `SUPERSET_OF` | `0.90` |
| `MAS-6.5.3.b` | The Financial Institution must implement appropriate controls and security measu... | `SUPERSET_OF` | `0.85` |
| `MAS-14.1.1` | The Financial Institution must implement security and control measures commensur... | `SUPERSET_OF` | `0.85` |

---

### N-to-1 Case 5: `NIST-PM-9` - Risk Management Strategy (6 MAS Obligations)

> **NIST Control Specification**:
> *Develops a comprehensive strategy to manage:
> Security risk to organizational operations and assets, individuals, other organizations, and the Nation associated with the operation and use of organizational systems; and
> Privacy risk to individuals resulting from the authorized processing of personally identifiable information;
> Implement the risk management strategy consistently across the organization; and
> Review and update the risk management strategy {{ insert: param, pm-09_odp }} or as required, to address organizational changes.
> An organization-wide risk management strategy includes an expre*

| Source MAS Clause | MAS Requirement Summary | Relation | Confidence |
|---|---|---|---|
| `MAS-1.3.b` | The Financial Institution must implement a robust risk management framework to e... | `SUPERSET_OF` | `0.90` |
| `MAS-1.4(a).1` | The Board of Directors and Senior Management must cultivate a strong risk cultur... | `SUPERSET_OF` | `0.85` |
| `MAS-1.4(a).2` | The Board of Directors and Senior Management must establish a sound and robust t... | `SUPERSET_OF` | `0.90` |
| `MAS-6.5.3.b` | The Financial Institution must implement appropriate controls and security measu... | `SUPERSET_OF` | `0.90` |
| `MAS-13.6.1.c` | The Financial Institution must develop risk assessment and mitigation strategies... | `SUPERSET_OF` | `0.85` |
| `MAS-14.1.4` | The Financial Institution must implement specific measures aimed at addressing t... | `SUBSET_OF` | `0.85` |

---

