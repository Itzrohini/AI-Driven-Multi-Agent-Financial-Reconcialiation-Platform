# Advanced Scope

**Status:** COMPLETED

## Purpose
Document the advanced scope.

## Findings
Once the MVP is proven, the following features will be added:

1. **Treasury Forecasting Integration:** Activating the Treasury Agent to stream predicted cash deficits/surpluses to a frontend dashboard.
2. **Event Bus (Kafka/Redis):** Moving from a simple background task queue to a robust pub/sub event architecture for massive scale.
3. **UI Dashboard:** A Next.js or React frontend for the "Human-in-the-Loop" analyst interface.
4. **Dynamic LLM Switching:** Abstracting the LLM provider so we can route high-complexity tasks to Gemini 1.5 Pro and low-complexity tasks to Gemini Flash.
