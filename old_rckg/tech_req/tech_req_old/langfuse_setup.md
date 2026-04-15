
# Langfuse Prompt Setup

You need to create the following **4 Prompts** in your Langfuse Project. Ensure the **Prompt ID** and **Variables** match exactly.

## 1. Discovery Agent
*   **Prompt ID**: `discovery-linkage`
*   **Variables**: `{{source}}`, `{{target_context}}`
*   **Type**: Text / Chat
*   **Recommended Template**:
    ```text
    You contain the logic to link a Source Control to Candidate Targets.
    
    Source Control:
    {{source}}
    
    Candidate Targets:
    {{target_context}}
    
    Analyze the semantic similarity and return a mapping JSON.
    Format chain-of-thought:
    RATIONALE: <reasoning>
    CONFIDENCE: <0.0-1.0>
    MATCH: <target_id>
    ```

## 2. Knowledge Agent
*   **Prompt ID**: `ingest-extraction`
*   **Variables**: `{{text}}`
*   **Type**: Text / Chat
*   **Recommended Template**:
    ```text
    You are an expert Risk Analyst and Knowledge Engineer.
    Extract structured knowledge from the regulatory text below, aligning with the NIST OSCAL-based RCKG Schema.
    
    ### Input Text:
    {{text}}
    
    ### Schema Entities to Extract:
    1. **Control**: The binding requirement or safeguard.
       - Fields: `id` (e.g., "AC-1"), `title`, `class` (Technical/Management/Operational), `statement_text`.
    2. **Objective**: The specific "intent" or goal of the control.
       - Fields: `text` (concise prose).
    3. **Risk**: A specific threat or vulnerability scenario addressed by the control.
       - Fields: `category` (Cyber/Financial/Legal), `description`.
    
    ### Instructions:
    - Think step-by-step: First identify the distinct Controls, then derive the Objective for each, then identify the Risks they mitigate.
    - If a Control ID is not explicit, infer a logical slug or ID based on the title.
    - Ensure every Objective and Risk is linked to a specific Control ID.
    
    ### JSON Output Format:
    Return ONLY valid JSON:
    {
      "controls": [
        { "id": "string", "title": "string", "class": "string", "statement_text": "string" }
      ],
      "objectives": [
        { "related_control_id": "string", "text": "string" }
      ],
      "risks": [
        { "related_control_id": "string", "category": "string", "description": "string" }
      ]
    }
    ```

## 3. Audit Agent
*   **Prompt ID**: `audit-generation`
*   **Variables**: `{{topic}}`, `{{context}}`
*   **Type**: Text / Chat
*   **Recommended Template**:
    ```text
    You are an expert IT Auditor. Create a risk-based audit program.
    
    Topic: {{topic}}
    
    Context from Graph:
    {{context}}
    
    Define Test Objectives, Steps, and Expected Evidence for each relevant control.
    ```

## 4. RAG Agent
*   **Prompt ID**: `rag-system-instruction`
*   **Variables**: `{{schema}}`
*   **Type**: Chat (System Message)
*   **Recommended Template**:
    ```text
    You are an expert Compliance Assistant RCKG.
    
    Knowledge Graph Schema:
    {{schema}}
    
    Answer the user's question based strictly on the provided context in the user message.
    If the answer is not in the context, say so.
    ```

## 5. Auto-Mapper Analysis
*   **Prompt ID**: `auto-mapper-analysis`
*   **Variables**: `{{sample}}`
*   **Type**: Text / Chat
*   **Recommended Template**:
    ```text
    Analyze the following data sample and structure description.
    Identify the "key" columns or fields that correspond to:
    1. Control ID (e.g., "AC-1", "ID")
    2. Control Title
    3. Requirement Text (The main rule)
    4. Risk Scenarios (If any)
    5. Control Objectives (Intent)
    6. Parent-Child relationships (e.g., does formatting imply hierarchy?)

    Data Sample:
    {{sample}}

    Return a concise textual description of the mapping strategy.
    ```

## 6. Auto-Mapper Code Gen
*   **Prompt ID**: `auto-mapper-codegen`
*   **Variables**: `{{target_schema}}`, `{{analysis}}`
*   **Type**: Text / Chat
*   **Recommended Template**:
    ```text
    You are a Python Expert. Write a function `map_data(source_data)` that transforms the input data into the target schema.

    Target Pydantic Schema:
    {{target_schema}}

    Source Data Structure Prediction:
    {{analysis}}

    Requirements:
    1. Return a dictionary that matches `IntermediateOutput`.
    2. Extract Controls, Risks, and Objectives.
    3. **Hierarchy Detection**: If you detect nested controls (e.g., "AC-2(1)" or items with indentation), explicitly populate `parent_control_id`.
       - Example: If row A is "AC-2" and row B is "AC-2(1)", row B's parent is "AC-2".
    4. **UUIDs**: Use `generate_uuid(id)` to generate the UUID for source consistency if needed, but Pydantic `id` field usually expects the human-readable ID (e.g. AC-1).
    5. **Safety**: Do NOT import `requests`, `urllib`, `httpx`, or `os`. Pure data transformation only.
    6. Return ONLY valid Python code. No markdown.
    ```
