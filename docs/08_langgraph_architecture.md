# LangGraph Architecture

**Status:** COMPLETED

## Purpose
Document the state graph and workflows.

## Findings
The system uses LangGraph to define a cyclic, stateful workflow.

### Nodes
- **ReceiveEvent:** Initializes the graph state.
- **Node_Payment, Node_AR, Node_Risk, Node_Treasury, Node_Policy:** The specialized agent nodes that append their findings to the state.
- **Node_Decision:** The final reasoning step.
- **Node_HumanReview:** A breakpoint node where the graph halts execution until a human provides input.

### Edges
- The Investigation Agent acts as the router, creating conditional edges (`if task == 'check_risk', route to Node_Risk`).
- All agent nodes route back to the Investigation Agent until the Investigation Agent determines all data is gathered, at which point it routes to `Node_Decision`.
