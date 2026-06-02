# Backend Automation & Scripting Samples

This repository contains clean, modular, and production-ready code samples demonstrating my approach to software architecture, error resilience, and data handling. It is designed to give clients an honest, transparent look into my coding standards.

All examples focus on stability, strict error catching, and secure data isolation.

---

## 📂 Project Modules

### 1. Crypto API Execution Layer (Python / CCXT)
A lightweight, asynchronous microservice designed to ingest incoming JSON webhook payloads and safely route order execution across major exchanges.
* **Core Focus:** Strict exception handling during network volatility, edge-case validation for order sizing, and secure credential isolation via environment variables.
* **Architecture:** Uses `asyncio` for non-blocking concurrent request handling to minimize execution delays.

### 2. Robust Data Extraction Pipeline (Node.js / Axios)
A modular script built to handle complex data parsing and extraction workflows from third-party endpoints.
* **Core Focus:** Native proxy rotation structures, graceful rate-limit handling, and checkpoint-saving logic to prevent data loss if the network drops.
* **Architecture:** Divided into isolated modules (Fetcher, Parser, Storage) ensuring high maintainability.

#### 🖥️ Execution Log Example:
```text
[2026-06-02 21:53:23] [INFO] Initializing asynchronous data extraction pipeline...
[2026-06-02 21:53:23] [INFO] Configuration successfully verified.
[2026-06-02 21:53:23] [INFO] Dispatched 4 concurrent API tasks. Executing...
[2026-06-02 21:53:23] [INFO] === Processed Data Pipeline Results ===
[2026-06-02 21:53:23] [INFO] Asset: BTCUSDT    | Current Market Price: 67237.01000000
[2026-06-02 21:53:23] [INFO] Asset: ETHUSDT    | Current Market Price: 1908.50000000
[2026-06-02 21:53:23] [INFO] Asset: SOLUSDT    | Current Market Price: 76.10000000
[2026-06-02 21:53:23] [INFO] Asset: LINKUSDT   | Current Market Price: 8.53200000
[2026-06-02 21:53:23] [INFO] Pipeline finished. Successfully processed 4/4 metrics.
text```

### 3. Protected Telegram Daemon & Control Interface (PM2)
A backend script acting as a lightweight, secure control panel for managing remote automation tasks via a Telegram interface.
* **Core Focus:** Strict user authorization using encrypted identifier filtering, defensive input validation, and deployment structures optimized for long-term stability.
* **Architecture:** Managed via PM2 process daemons to guarantee automatic recovery and maximum runtime stability on remote cloud servers.

---

## 🛠️ General Coding Standards
* **No Magic Numbers:** All configurations, request limits, and timing intervals are clearly defined in a central configuration layer.
* **Fail-Safe Mindset:** Code is written with the assumption that external APIs and third-party servers will occasionally fail. Fallback mechanics and informative logging are always present.
* **Clean Separation of Concerns:** Database interactions, external API layers, and core business logic are strictly separated into dedicated directories rather than piled into a single monolithic script.
