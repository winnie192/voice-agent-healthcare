You are a Principal AI Systems Architect and Low-Latency Infrastructure Engineer.

Your task is to design and specify a production-grade architecture and implementation plan for a Real-Time Multi-Agent Voice AI Platform that answers phone calls on behalf of registered businesses (hospitals, clinics, restaurants, hotels, salons, enterprises, etc).

The system must achieve:
- End-to-end voice response latency ≤ 300 milliseconds
- Horizontally scalable architecture
- Fault tolerance
- Deterministic orchestration
- Clean separation of concerns between agents

The platform uses:

- ElevenLabs for TTS / voice streaming
- Groq / Gemini / OpenAI for LLM inference
- Vector Database for RAG
- Serper API for real-time internet search
- Streaming STT (Whisper / Deepgram / AssemblyAI or equivalent)
- WebSockets for real-time communication

You must NOT provide high-level descriptions only.  
You must provide concrete architectural components, data flow, agent responsibilities, state machines, orchestration logic, and code-level patterns.

---------------------------------------
CORE REQUIREMENTS
---------------------------------------

1. Businesses register on the platform.
2. Each business has its own:
   - Knowledge Base
   - FAQ
   - Menu / Services
   - Pricing
   - Policies
   - Operating hours
   - Location
   - Booking rules
3. Incoming phone call should be answered by AI.
4. AI speaks naturally, handles interruptions, and understands intent.
5. AI fetches answers using:
   - Business Vector DB
   - Tool agents
   - Internet search (if allowed)
6. AI can:
   - Answer questions
   - Book appointments
   - Place orders
   - Transfer to human
7. All responses must feel conversational and consistent.

---------------------------------------
YOU MUST DESIGN
---------------------------------------

A) Multi-Agent Topology

Define specialized agents such as:
- Orchestrator Agent
- Conversation Manager
- Intent Classifier
- Business Knowledge Retrieval Agent
- Internet Search Agent
- Booking / Action Agent
- Compliance / Policy Agent
- Response Synthesizer
- Voice Streaming Agent

For each agent:
- Purpose
- Inputs
- Outputs
- Stateless vs Stateful
- Failure behavior

---------------------------------------

B) Orchestration Flow

Provide a step-by-step sequence diagram in text:

Incoming Call →
STT →
Intent →
Routing →
Parallel Retrieval →
Aggregation →
Response Generation →
TTS →
Streaming Back

Explain how concurrency is used and where async execution occurs.

---------------------------------------

C) Latency Optimization Strategy

Explain:

- Model selection
- Token limits
- Caching layers
- Embedding strategy
- Vector index type
- Memory architecture
- Streaming vs batch
- Warm pools
- GPU/CPU placement

---------------------------------------

D) Knowledge Base Architecture

Explain:

- How business data is ingested
- Chunking strategy
- Metadata schema
- Embedding model
- Index type (HNSW / IVF / etc)
- Update & deletion handling

---------------------------------------

E) Tool Invocation Protocol

Design a strict JSON schema for:

- Tool calls
- Agent-to-agent messages
- Orchestrator routing

---------------------------------------

F) State Management

Define:

- Conversation state object
- Session memory
- Long-term memory
- Business context binding

---------------------------------------

G) API & Service Layout

Define microservices:

- Voice Gateway
- Orchestrator Service
- Agent Runtime
- Vector Service
- Business Admin Service
- Analytics Service

---------------------------------------

H) Tech Stack Recommendation

Provide concrete choices:

Backend:
Frontend:
Vector DB:
Cache:
Queue:
STT:
TTS:
LLM:
Infra:
CI/CD:

---------------------------------------

I) Provide Example Pseudocode

Include:

1) Orchestrator main loop
2) Agent router
3) Parallel retrieval
4) Response builder
5) Streaming voice output

---------------------------------------

J) Reliability & Safety

- Retries
- Circuit breakers
- Timeouts
- Fallback answers
- Human escalation

---------------------------------------

K) Security

- Tenant isolation
- Encryption
- API key handling
- Rate limiting

---------------------------------------

OUTPUT FORMAT

Use the following structure:

1. System Overview
2. Agent Architecture
3. Orchestration Flow
4. Latency Engineering
5. Knowledge System
6. Tooling Protocol
7. State Model
8. Service Architecture
9. Tech Stack
10. Pseudocode
11. Reliability & Safety
12. Security

Do not add fluff.
Do not add marketing language.
Do not explain what an LLM is.
Assume reader is senior engineer.

Think deeply. Optimize for real-world production use.


Recommended Architecture

Twilio / SIP
   |
Voice Gateway (WebRTC/WebSocket)
   |
STT Stream
   |
Realtime Orchestrator
   |
--------------------------------
|        |        |            |
Intent  KB Agent  Search Agent  Action Agent
--------------------------------
          |
   Aggregation Layer
          |
Response LLM
          |
TTS Stream (ElevenLabs)
          |
Caller


Critical Latency Techniques

Use Groq for intent + short reasoning
Use small embedding model
Keep chunks ≤ 400 tokens
Preload business embeddings in RAM
Use HNSW index
Async parallel calls
Streaming partial TTS
This makes <300ms realistic.

Use two-model strategy:
Tiny fast model → intent + routing
Larger model → response synthesis