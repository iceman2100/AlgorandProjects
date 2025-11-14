# StreamFi — Algorand-Powered Salary Streaming (Hackathon Prototype)

StreamFi is a lightweight decentralized application built on the Algorand TestNet.  
It showcases automated salary streaming using an ARC-20 token, Pera Wallet, and a minimal Flask backend.  
This prototype keeps everything intentionally simple while demonstrating real on-chain interactions.

---

## Features

### Salary Streaming (Prototype Logic)
- A single company wallet funds six employee wallets (same wallet reused for simplicity).
- The backend calculates claimable balance for each employee.
- Employees can click "Claim" to receive ARC-20 tokens.
- Transactions are executed through Pera Wallet on Algorand TestNet.

### Algorand Integration
- Uses a custom ARC-20 token with Asset ID: 749531304.
- Integrated with Pera Wallet via WalletConnect v2.
- Backend uses the Algorand Python SDK for transaction creation and signing.

### Simple Frontend
- Built with HTML, CSS, and vanilla JavaScript.
- Shows employee balance, status, and supports claiming tokens.

### Lightweight Backend
- Flask REST API.
- Handles Algorand logic: balances, claim calculation, transaction signing.
- Designed to stay simple for hackathon use.

---

## Folder Structure
```plaintext

streamfi-simple/
│
├── backend/
│ ├── app.py
│ ├── create_arc20_token.py
│ ├── employees.json
│ └── additional SDK utility scripts
│
├── contracts/
│ ├── create_employees.py
│ ├── test_transaction.py
│ └── experimental contract scripts
│
├── frontend/
│ ├── index.html
│ ├── styles.css
│ ├── script_algorand.js
│ └── assets/
│
└── README.md

yaml
Copy code

---

## Architecture (Hackathon-Simple Overview)

Frontend (HTML, JS)
|
| REST API calls
v
Backend (Flask + Algorand SDK)
|
| Signed transactions
v
Algorand TestNet Blockchain
```
yaml
Copy code

Key points:
- The frontend handles wallet connection and user actions.
- The backend prepares and signs Algorand transactions.
- ARC-20 tokens are transferred from the company wallet to employee wallets.

---

## Local Development

### Backend Setup

cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python app.py

yaml
Copy code

Backend runs at:

http://127.0.0.1:5000

pgsql
Copy code

### Frontend Setup

Option A: VSCode Live Server  
Right-click `index.html` → Open with Live Server

Option B: Python HTTP Server

cd frontend
python -m http.server 8080

arduino
Copy code

Then open:

http://localhost:8080

yaml
Copy code

---

## Deployment Overview

### Backend (Render)

Build Command:
pip install -r requirements.txt

powershell
Copy code

Start Command:
gunicorn app:app

yaml
Copy code

Project Root:
backend

yaml
Copy code

### Frontend (Vercel)

- Select the frontend folder as project root.
- Framework preset: None (Static Site).
- Deploy.

---

## Testing Steps

1. Connect Pera Wallet from the frontend.  
2. Confirm the wallet address is detected.  
3. Wait for backend to compute claimable STRM tokens.  
4. Click "Claim Tokens".  
5. Approve the transaction in Pera Wallet.  
6. Check Algorand TestNet Explorer for transaction confirmation.

---

## Future Improvements

- Real-time continuous streaming instead of fixed claim logic.
- Multiple employees with real independent wallets.
- Persistent database for employee data and claim history.
- Improved dashboard for HR and admin roles.
- Expanded support for more Algorand ARC standards.

---

## Purpose of This Prototype

This is a functional demonstration for learning and hackathon presentation.  
It shows how Algorand can be used for micro-transactions, streaming logic, and transparent salary distribution with minimal infrastructure.

## Output Preview

The StreamFi prototype provides a simple employee dashboard where users can:

- Connect their Pera Wallet
- View their claimable STRM token balance
- Initiate a claim and sign the transaction in Pera Wallet
- View confirmation on Algorand TestNet Explorer

Typical frontend output includes:
- Company wallet address
- Employee address and claimable amount
- Claim button that triggers WalletConnect signing flow
- Success message after the transaction is confirmed

Backend output includes:
- Flask server logs for API calls
- Transaction objects generated for claims
- Debug information for employees and company metadata

For visual understanding, refer to screenshots or browser output when running the frontend and backend locally.

---

## Additional Documentation

For a detailed explanation of the full system architecture, execution flow, API behavior, folder structure, and deployment process, refer to:

**ARCHITECTURE.md**

This file contains the complete breakdown of how StreamFi is designed and how every component interacts with Algorand TestNet.

