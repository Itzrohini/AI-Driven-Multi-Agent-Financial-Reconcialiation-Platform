# FinTech Research

**Status:** COMPLETED

## Purpose
Document research on FinTech companies using AI and extract lessons for the Deluxe prototype.

## Questions this document will answer
- How are top FinTechs using AI today?
- Are they using LLMs, Traditional ML, or Agentic AI?
- What patterns can we apply to our Agent-to-Agent architecture?

## Findings

### 1. Stripe (Radar)
**Use Case:** Real-time payments fraud detection.
**Technology:** "Payments Foundation Model" using traditional ML to evaluate 1,000+ signals per transaction in under 100ms.
**Lesson:** Fast, high-stakes financial decisions (like risk scoring) require traditional ML, not slow LLMs. Our architecture must include an ML-based Risk Agent, not just an LLM.

### 2. BILL
**Use Case:** AP Automation and Intelligent Capture.
**Technology:** Document AI combined with digital approval workflows.
**Lesson:** The industry is actively shifting from rigid, rules-based automated workflows to flexible, "autonomous" AI agents. Our prototype must demonstrate this agentic autonomy.

### 3. Capital One
**Use Case:** Enterprise-wide AI Factory and Customer Servicing (Eno).
**Technology:** Cloud-native integration of proprietary models, heavily emphasizing "Explainable AI (XAI)" and "Responsible AI."
**Lesson:** In finance, AI decisions must be explainable. Our agents must output clear reasoning and cite policies (via RAG) to ensure auditability and human trust.

### 4. JPMorgan Chase
**Use Case:** Predictive Treasury and Document Analysis.
**Technology:** Internal "LLM Suite" and specialized models like "docLLM." Evolving toward multi-step agentic systems for investment research.
**Lesson:** AI is moving treasury from reactive to predictive. Our prototype should include a Treasury Agent that calculates the real-time cash flow impact of AR exceptions, linking operations directly to liquidity forecasting.
