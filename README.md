# 🚀 Smart Wallet Tracker & Copy Trader (Free Tier)

> [!CAUTION]
> ### 🚧 Under Construction
> This project is currently in active development. Features may be incomplete, and the implementation details are subject to change. Use at your own risk.

This project provides an architectural blueprint for building a "poor man's version" of a professional copy-trading bot. By combining **Dune Analytics** for historical discovery and **Web3 APIs** for real-time tracking, you can identify and follow profitable wallets without expensive subscription fees.

---

## 🏗️ The Strategy

The application is split into two distinct engines to optimize for performance and API credit usage:

### 1. The Discovery Engine (Slow & Analytical)
* **Goal:** Identifies "smart wallets" based on historical performance (last week, month, or quarter).
* **Tool:** [Dune Analytics API](https://dune.com) (Free tier: 2,500 credits/month).
* **Method:** SQL queries to calculate Realized PnL and Win Rates.

### 2. The Tracking Engine (Fast & Real-time)
* **Goal:** Monitors the discovery list for new transactions to execute copy trades.
* **Tool:** [Web3.py](https://web3py.readthedocs.io/) (via Alchemy/Infura) or [Bitquery](https://bitquery.io/).
* **Method:** Polling or WebSockets to catch DEX swaps (Uniswap, SushiSwap, etc.) as they happen.

---

## 📊 Data Sources

| Provider | Purpose | Benefit | Free Tier Limit |
| :--- | :--- | :--- | :--- |
| **Dune Analytics** | **Discovery** | Custom SQL for PnL calculation. | 2,500 credits/month |
| **Bitquery** | **Tracking** | Easy decoding of complex DEX trades. | Generous point-based tier |
| **Debank** | **Verification** | Best UI for manual portfolio audits. | Manual Use (UI) |

---

## 🛡️ How to Use This Safely

### 1. Find the SQL Logic (Crucial)
The API requires a specific Query ID to fetch data. You can find proven logic on the Dune platform:
1. Search Dune.com for **"Top Traders"**, **"Smart Money"**, or **"DEX Profit"**.
2. Open a dashboard and find a table listing wallet addresses.
3. Click the **Query Title** -> **"Edit Query"**.
4. Copy the SQL code or the **Query ID** from the URL to use in your implementation.

### 2. Manage Rate Limits
* **Discovery:** Do **not** update your smart wallet list every minute. Profitability patterns are long-term; running this once every **24 hours** is sufficient.
* **Tracking:** You can check for trades frequently (e.g., every minute), but monitor your Bitquery/RPC point usage to avoid service interruption.

### 3. Understanding the Risks
* **Front-running:** By the time an API reports a trade, the price may have already moved. You are often "buying the tail" of a pump.
* **Honeypots:** Some "profitable" wallets belong to scammers. They "profit" because they are the only ones allowed to sell a specific token. **Always** check token contracts before buying.
* **Slippage:** High-frequency trading involves high slippage. Ensure your execution logic accounts for price impact.

---

## ⚡ FastAPI Implementation

The backend is designed to serve the wallet list and handle background scheduling for updates.

### Prerequisites
* **Dune API Key:** [Get one here](https://dune.com/settings/developer).
* **Bitquery API Key:** [Get one here](https://bitquery.io/pricing).
* **Python 3.10+**