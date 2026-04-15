# Evaluation and Trust Strategy

## 1. Core Philosophy
We utilize **LLM-as-a-Judge** to evaluate the quality of our AI agents. This allows for scalable, automated testing of subjective outputs, ensuring high trust in the "Autonomous" system.

## 2. The Judges (The "Auditor" Layer)
To ensure trust, every critical action is verified by a "Higher Reasoning" model.

### 2.1 Logic Judge
*   **Model**: **Llama 3.3 (70B)**
*   **Role**: Evaluates policy-to-control objective mappings for semantic faithfulness. Checks if the intent is preserved during transformation.
*   **Threshold**: Score < 0.95 triggers "Human-in-the-Loop" notification.

### 2.2 Technical Judge
*   **Model**: **DeepSeek-R1 (70B)**
*   **Role**: Audits technical parameter extraction. Verifies mathematical and logical consistency (e.g., verifying if "Hourly" matches "3600 seconds").
*   **Threshold**: Strict exact match or logical equivalence required.

## 3. Metrics

| Metric | Agent | Description | Scorer |
| :--- | :--- | :--- | :--- |
| **Faithfulness** | Reconciliation | Does the flattened record match the NIST Full OSCAL catalog? | `LogicJudge` |
| **Precision** | Ingestion | Are the extracted parameters (e.g., frequency) technically correct? | `TechnicalJudge` |
| **Hallucination** | RAG / Audit | Does the answer contain info not present in the context? | `HallucinationScore` |
| **Completeness** | Grooming | Did the agent find all relevant cross-walks? | `RecallScore` |

## 4. Implementation Plan

1.  **Golden Datasets**: Created in Langfuse (Input -> Expected Output) for each agent capability.
2.  **Automated Audits**: The Judges run asynchronously on the "Audit Trail" in PostgreSQL.
3.  **Human Review**: Any item flagged by a Judge is routed to the User Dashboard for manual approval/correction.

## 5. Feedback Loop
1.  **Trace**: Log every production generation to Langfuse.
2.  **Judge**: The 70B models score the traces.
3.  **Refine**: Low scores are added to the "Action Layer" fine-tuning dataset to correct the local model behaviors (DPO/RLHF loop).
