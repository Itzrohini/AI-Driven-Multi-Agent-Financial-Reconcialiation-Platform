# FinTech Research

**Status:** COMPLETED

## Company 1: Stripe
* Company: Stripe
* Problem solved: Real-time payments fraud detection and prevention.
* Product: Stripe Radar
* AI/ML capability: Real-time machine learning scoring over 1,000 signals per transaction in under 100ms.
* GenAI capability: None explicitly for transaction scoring, relies on predictive ML.
* Agentic capability: Adaptive rules engine that automatically adjusts based on global network feedback.
* Financial workflow: Real-time payment authorization and blocking.
* Technology pattern: "Payments Foundation Model" trained on tens of billions of transactions. Network-effect learning.
* Business value: Reduces chargebacks and fraud losses while minimizing false positives for legitimate customers.
* Official evidence: Stripe Radar documentation and engineering blogs.
* Lessons for Deluxe: High-frequency financial decisions (like risk scoring) must use fast, predictive ML models, not slow LLMs. We should use traditional ML for our Risk Agent's initial score.
* URL: https://stripe.com/radar

## Company 2: BILL
* Company: BILL (formerly Bill.com)
* Problem solved: Manual, paper-based Accounts Payable and Accounts Receivable workflows.
* Product: BILL AP/AR Automation
* AI/ML capability: Intelligent data capture and automated routing.
* GenAI capability: Moving towards "autonomous" workflows leveraging broader AI.
* Agentic capability: Embedding AI agents across AP to handle tasks with increasing independence.
* Financial workflow: Invoice ingestion, approval routing, and payment execution.
* Technology pattern: Document AI combined with rigid digital workflows transitioning to flexible agentic workflows.
* Business value: Significant reduction in time spent on manual invoice queues and reconciliation.
* Official evidence: BILL platform documentation.
* Lessons for Deluxe: The industry is moving from *automation* (rigid rules) to *autonomy* (flexible agents). Our prototype must demonstrate this leap.
* URL: https://www.bill.com/

## Company 3: Capital One
* Company: Capital One
* Problem solved: Secure, scalable, and proprietary AI integration across all banking operations.
* Product: Eno (Virtual Assistant), Fraud Systems, Agentic Customer Service
* AI/ML capability: Enterprise-wide ML for fraud, AML, and credit risk.
* GenAI capability: Customizing open-weight foundation models with proprietary data.
* Agentic capability: "AI Factory" model deploying agentic AI capable of reasoning and independent action.
* Financial workflow: Fraud detection, customer servicing, operational efficiency.
* Technology pattern: Cloud-native foundation with a strong emphasis on "Explainable AI (XAI)" and "Responsible AI".
* Business value: Competitive advantage through proprietary intelligence and enhanced customer experience.
* Official evidence: Capital One Applied AI Research program publications.
* Lessons for Deluxe: In highly regulated environments, AI must be explainable. Our Decision Agent must output its reasoning and cite policies (via RAG) to ensure auditability.
* URL: https://www.capitalone.com/tech/machine-learning/

## Company 4: JPMorgan Chase
* Company: JPMorgan Chase
* Problem solved: Inefficient, manual document processing and reactive treasury management.
* Product: LLM Suite, docLLM, Predictive Treasury
* AI/ML capability: Predictive ML for cash forecasting and behavioral analysis.
* GenAI capability: "LLM Suite" used internally by thousands of employees for summarization and insight generation. docLLM for visually complex financial documents.
* Agentic capability: Evolving toward multi-step agentic systems for investment research and advisory.
* Financial workflow: Treasury forecasting, document extraction, investment memos.
* Technology pattern: Secure, internally hosted generative AI platforms to maintain data privacy.
* Business value: Shifts treasury from reactive batch processing to real-time, forward-looking decision-making.
* Official evidence: Annual reports and executive technology statements.
* Lessons for Deluxe: Multi-agent systems can bridge the gap between operations (AR/AP) and strategy (Treasury). Our prototype must include a Treasury Agent that predicts cash flow impacts.
* URL: https://www.jpmorgan.com/
