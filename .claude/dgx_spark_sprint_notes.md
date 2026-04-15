# Clear Trace (CT) & DGX Spark Sprint Reference

## 1. Product Overview: The "Provable Governance" Control Tower (Demo MVP)
Clear Trace (CT) is a comprehensive AI Governance suite designed for CIOs, CISOs, and Compliance Officers. It aims to solve the "Checklist Governance" problem where executives rely on manual surveys or attestations by bridging high-level organizational principles (e.g., "AI must be Fair") directly to automated, executable technical tests (e.g., DeepEval metric results). It aims to transition the UI from a "technical testkit" to an "Executive Control Tower."

**Key Differentiator:** Replacing paper-based GRC (Governance, Risk, and Compliance) with "Provable Governance" linked directly to actual code and evaluation tools (DeepEval).

### The UI - "Tri-Panel Copilot"
The Demo MVP centers around an Agentic approach with a Tri-Panel UX:
*   **Chat:** Natural language interaction for querying compliance states.
*   **Reasoning Trace:** Showing the step-by-step logic of the agent.
*   **Generative Canvas:** Rendering highly-structured, board-ready compliance reports (e.g., NIST AI RMF mapping) using data fetched from the DB, rendered using Vercel AI SDK streams.

## 2. Infrastructure Goal: DGX Spark Setup
To run the high-throughput demo efficiently (and prove to the user that the compliance testing is *live*), the suite needs to be deployed on an NVIDIA DGX Spark box.

The current sprint (Sprint 0 / Sprint 4 in the roadmap) calls for establishing the core bare-metal foundation and automated deployment pipelines *first* so that development iterations are rapid.

### Key DGX Spark Sprint Requirements (Epics/Stories)
The infrastructure must be configured as follows because manual testing on the DGX is a recognized critical bottleneck:

1.  **[STORY-00 / STORY-007_A] Bare-Metal DGX Foundation:**
    *   **OS:** Flash the DGX Spark with the ARM64 flavor of Ubuntu 24.04.
    *   **GPU Toolkit:** Install NVIDIA CUDA Toolkit 13.0.
    *   **Containerization:** Install the NVIDIA Container Toolkit and latest Docker Engine.
2.  **[STORY-00A / STORY-008_A] Native vLLM Inference Engine on ARM64:**
    *   Compile and deploy **vLLM natively** on the ARM64/CUDA DGX Spark environment so that it can host local Llama models (specifically Llama-3.1-Nemotron-70B) for inference without kernel panics. The agent relies heavily on local inferencing for the demo.
3.  **[STORY-00B / STORY-011_C] CI/CD Automated SSH Deployment:**
    *   Configure an internal CI/CD pipeline (GitLab or Jenkins) that has line-of-sight to the DGX server.
    *   Upon a push to `main` and successful test/build run, the pipeline must **automatically SSH into the DGX**, pull the updated docker images, and execute `docker-compose up -d --build` for a rolling deploy.

## 3. Immediate Next Steps / Status
The underlying backend utilizes a dual-write architecture (PostgreSQL and Memgraph) but the fundamental blocker is the infrastructure rollout. 

Currently waiting to assist the user on the DGX Spark environment provisioning (OS flashing, drivers, and CI/CD setup).
