# Assistant Behavior

For tool operations: respond directly without reasoning.

For requirements and architecture: think step-by-step, but limit 
reasoning to under 800 tokens. Focus on decisions, tradeoffs, and 
structured outputs rather than verbose exploration.

# Memory Management
- Run /compact when context feels repetitive or a full feature is complete
- Do NOT re-read files already in context
- Do NOT repeat previously shown code unless it changed
- Summarize completed work in 3 bullets before moving to the next story

# Context management
Compact your context after each major step. Summarize completed work and drop file contents from context before moving on.