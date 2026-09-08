# Agent-to-Agent Financial Collaboration Platform

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green.svg)
![React](https://img.shields.io/badge/React-18.0%2B-blue.svg)

## Overview

The **Agent-to-Agent Financial Collaboration Platform** is an AI-driven, event-based system designed to autonomously resolve complex Accounts Receivable (AR) and Accounts Payable (AP) exceptions. By orchestrating domain-specific Large Language Model (LLM) agents, this platform significantly reduces manual investigation time and accelerates cash flow.

It leverages a hybrid architecture that combines traditional machine learning for fast anomaly detection with advanced LangGraph agent workflows and Retrieval-Augmented Generation (RAG) to ensure financial decisions are auditable and strictly grounded in corporate policies.

## 🌟 Key Features

* **Multi-Agent Orchestration:** Utilizes LangGraph to coordinate specialized LLM agents (Payment Matching, AR Ledger, Risk Scoring, Policy Retrieval).
* **Policy-Grounded Decisions (RAG):** Integrates with a Qdrant vector database to retrieve specific corporate financial policies, ensuring all automated resolutions are compliant and auditable.
* **Real-time Anomaly Detection:** Applies traditional ML models (e.g., scikit-learn Isolation Forests) to flag suspicious transactions instantly.
* **Human-in-the-Loop (HITL):** Seamlessly routes highly complex or edge-case exceptions to a human review queue.
* **Event-Driven Architecture:** Asynchronous webhook ingestion managed by FastAPI and stored in MongoDB.

## 🏗️ Architecture & Tech Stack

* **Backend Framework:** FastAPI (Python)
* **Orchestration:** LangGraph / LangChain
* **Vector Database (RAG):** Qdrant
* **Operational Database:** MongoDB
* **Machine Learning:** Scikit-learn
* **Frontend:** React + Vite
* **Containerization:** Docker & Docker Compose

## 📁 Project Structure

```
├── backend/            # FastAPI application, workflows, and agents
├── frontend/           # React + Vite web application
├── docs/               # Architecture documents and research
├── docker/             # Dockerfiles for various services
├── architecture/       # System architecture diagrams (Mermaid)
├── data/               # Mock data, storage, and policies
├── ml/                 # Machine learning models and scripts
├── rag/                # Embeddings and vector DB ingestion
├── policies/           # Corporate financial policy markdowns
└── tests/              # Unit, integration, and workflow tests
```

## 🚀 Getting Started

### Prerequisites
* Docker and Docker Compose
* Python 3.10+
* Node.js (for frontend development)

### Running the Application

The easiest way to spin up the entire platform is using Docker Compose:

```bash
docker-compose up --build
```

This will start:
* **API Gateway:** `http://localhost:8000`
* **Frontend UI:** `http://localhost:5173`
* **MongoDB:** `localhost:27017`
* **Qdrant Vector DB:** `localhost:6333`

## 📄 License

This project is licensed under the MIT License.
