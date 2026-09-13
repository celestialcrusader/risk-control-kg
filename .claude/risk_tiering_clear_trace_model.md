# Refined AI Risk Tiering (The RCKG-Tiering Model)

This model applies "Minimum Viable Governance" by condensing risk assessment into a high-density, scannable engine. 

Reversibility is subsumed into Business Impact.
Threat Landscape is subsumed into Facing.
Lifecycle is discarded as a procedural gate.
Complexity/Explainability (black-box nature) is treated as a **Conditional Control**, not a primary "Risk Scorer".

## 1. The 5 Core Dimensions (The Scorer)

| Dimension | Low (1 pt) | Med (3 pts) | High (5 pts) |
| --- | --- | --- | --- |
| **1. Facing** | Fully Internal (Finance/Security) | Public-Facing but Internal Ops (HR/Loan) | Full Public Interaction (External Users) |
| **2. Jurisdiction** | No specific AI laws (General IT) | Standard Privacy (GDPR/CCPA) | Strict AI Law (EU AI Act/China/FedRAMP) |
| **3. Agency** | Pure Generation (Drafts) | Human-in-the-loop (Approve/Reject) | Full Autonomous Operation |
| **4. Biz Impact** | Inconvenience / Low Productivity | Operational Breakdown / Moderate Fine | Financial Ruin / Life & Safety / Legal |
| **5. Data Nature** | Public / Non-PII | Internal / CUI / PII | Top Secret / Biometrics / Facial Rec |

## 2. The Logic: "The Complexity Toggle"

Instead of Complexity (Angle 6) adding points, we use it as a **Control Trigger**.

* **The Rule:** If the system is **Tier 2 (Med)** or **Tier 1 (High)** AND the model is a **"Black Box"** (LLM/Deep Learning), then the **Explainability Control** (SHAP, LIME, or Model Cards) becomes **Mandatory**.
* **The Benefit:** E.g., for a "Code Auto-complete" tool, even though it's an LLM (Black Box), its **Facing** is Internal and **Biz Impact** is Low. Therefore, the score stays low, and the "Explainability" requirement is never triggered.

## 3. Tiering & Controls Mapping

Once the score is calculated, **Wukongtai** can propose controls based on the AI Principle.

| Tier | Score Range | Primary Controls | AI Principle Addressed |
| --- | --- | --- | --- |
| **Tier 1 (Critical)** | **20 - 25** | Red Teaming + **Mandatory Explainability** + Third Party Audit | **Safety & Robustness** |
| **Tier 2 (High)** | **12 - 19** | Bias Testing + Human-in-the-loop + Data Lineage | **Fairness & Accountability** |
| **Tier 3 (Standard)** | **5 - 11** | Basic Vulnerability Scan + Usage Policy | **Security** |

## GRC Engineering Benefits
1. **Scannability:** An engineer can fill this out in 60 seconds.
2. **Dynamic Rigor:** It scales dynamically. A "Loan Approval" AI gets hit with Bias and Explainability controls because of its **Facing** and **Impact**, while a "Log Summarizer" for the SOC stays in Tier 3.
3. **Wukongtai Integration:** This is easily representable as a vector. A simple distance or weighted sum function can trigger the control set.
