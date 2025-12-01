# Deep Dive: Foundry IQ & Model Router
*Microsoft Ignite 2025 Architecture Update*

This document provides a detailed technical breakdown of the new "Brain" (Foundry IQ) and "Traffic Control" (Model Router) layers of the Microsoft Agent Stack. These components represent a shift away from hard-coded, fragile pipelines toward managed, intelligent infrastructure.

---

## 1. Foundry IQ (Preview)
**The "Agentic RAG" Engine**
*Moves RAG from static retrieval to dynamic reasoning.*

### 🔍 What It Is
Foundry IQ is the managed knowledge layer that sits underneath your agent fleet. It unifies disparate data sources—Microsoft 365 documents (Work IQ), Enterprise Data in Fabric (Fabric IQ), and public web data—into a single, normalized "knowledge graph" endpoint.

Instead of developers building custom ETL pipelines, vector stores, and retrieval logic for each data source, Foundry IQ abstracts this into a managed service that agents can query naturally.

### 🚀 Why It Matters
*   **36% Higher Relevance**: Microsoft benchmarks claim a 36% boost in response accuracy compared to standard RAG implementations.
*   **Agentic Retrieval**: This is the key differentiator. It doesn't just "search." The system dynamically decides *how* to search based on the user's query (e.g., Keyword for specific names, Vector for concepts, Hybrid for mixed queries).
*   **Code Reduction**: It eliminates approximately 40% of the custom RAG boilerplate code (chunking, embedding, re-ranking, indexing) that teams typically maintain.

### ⚙️ Architecture Components
*   **Work IQ**: Native connector to the Microsoft 365 Graph (Teams, SharePoint, Outlook, OneDrive). It respects existing user permissions—agents cannot retrieve data the user couldn't access manually.
*   **Fabric IQ**: Native connector to Microsoft Fabric (OneLake, SQL, Dataverse). Allows agents to query structured enterprise data without complex SQL wrappers.
*   **Automated Indexing**: Handles the chunking, embedding, and re-ranking strategies automatically, optimizing them for the specific data type (e.g., sliding windows for documents, row-based for data).

### 🛠️ Implementation Context
*   **Use Case**: Complex enterprise queries like *"What was the financial impact of Project X mentioned in last week's emails?"*
*   **Workflow**:
    1.  Agent receives query.
    2.  Agent delegates retrieval to Foundry IQ.
    3.  Foundry IQ formulates a search strategy (e.g., "Search Emails for Project X" + "Query SQL for Financials").
    4.  Foundry IQ retrieves, re-ranks, and synthesizes the context.
    5.  Agent generates response based on high-fidelity context.

---

## 2. Model Router (GA)
**The "Smart Traffic Controller"**
*Optimizes token spend and prevents vendor lock-in.*

### 🚦 What It Is
The Model Router is a unified API endpoint that sits between your agent application and the raw model providers. Instead of hard-coding calls to `gpt-4o` or `claude-3-5-sonnet`, your application calls the Router.

### 💎 Why It Matters
*   **Dynamic Routing**: The Router analyzes the prompt complexity and routing rules to select the optimal model in real-time.
*   **Model Lock-In Prevention**: Decouples your application logic from specific model versions. Swapping models becomes a configuration change, not a code rewrite.
*   **Resiliency**: Automatic failover. If a primary model provider experiences high latency or outages, the Router seamlessly redirects traffic to a backup provider without the user noticing.

### 🎛️ Routing Modes
You can configure the Router to prioritize specific business outcomes:

1.  **Optimize for Quality**:
    *   **Goal**: Best possible answer, regardless of cost.
    *   **Behavior**: Routes complex reasoning tasks to frontier models like **GPT-4o** or **Claude 3.5 Sonnet**.
    
2.  **Optimize for Cost**:
    *   **Goal**: Lowest token spend for acceptable quality.
    *   **Behavior**: Routes simple tasks (summarization, classification, basic chat) to efficient models like **GPT-4o-mini**, **Phi-4**, or **Llama 3**.
    
3.  **Optimize for Latency**:
    *   **Goal**: Fastest Time-to-First-Token (TTFT).
    *   **Behavior**: Prioritizes the fastest available model endpoint that meets the task requirements.

### 🌍 The "MaaS" Catalog (Models as a Service)
The Router leverages the expanded Azure Model Catalog, which now treats third-party models as first-class citizens ("MaaS"). This means you can route traffic to:
*   **OpenAI** (GPT-4o, o1)
*   **Anthropic** (Claude 3.5 Sonnet)
*   **Meta** (Llama 3)
*   **Mistral** (Large)
*   **Cohere** (Command R+)
*   **Microsoft** (Phi family)

---

## 🧠 Eve's Strategic Take
> "Foundry IQ is the bigger deal here. Everyone builds a router eventually (or buys one), but Foundry IQ is attempting to solve the 'fragmented context' problem that makes most enterprise agents stupid. If it works as advertised, it kills about 40% of the custom RAG code we usually have to write."

### Summary for Decision Makers
*   **Adopt Foundry IQ** if your agents need to answer questions based on internal company data (SharePoint, SQL, Emails). It solves the "Hallucination" problem by grounding agents in truth.
*   **Adopt Model Router** immediately for all production workloads. It is the easiest way to reduce costs (by offloading simple tasks to cheaper models) and ensure reliability (failover protection).

