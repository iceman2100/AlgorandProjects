# StreamFi Architecture Documentation

This document describes the complete technical architecture of the StreamFi prototype. It covers system layers, execution flows, API details, environment setup, deployment paths, and design .

---

## 1. System Overview

StreamFi is a lightweight salary-streaming prototype built on Algorand TestNet.  
The system is composed of three tightly connected layers:

1. **Frontend Layer**  
   HTML, CSS, JavaScript. Handles user interface, API calls, and PeraWallet interactions.

2. **Backend Layer**  
   Python Flask server. Builds Algorand transactions, exposes REST APIs, and connects frontend with Algorand TestNet.

3. **Blockchain Layer**  
   Algorand TestNet. Contains the STRM ARC-20 token and a simple PyTEAL-based application for demonstration.

Users interact with the frontend.The frontend calls the backend for employee and claim information.The backend prepares transaction payloads, which the wallet signs and broadcasts on-chain.

---

## 2. Architecture Diagram

<img width="1886" height="899" alt="image" src="https://github.com/user-attachments/assets/bb74c104-e22c-4090-9b94-9cce7898127f" />

---

## 3. Folder Structure

```plaintext
streamfi-simple/
│
├── backend/
│   ├── app.py                  # Flask API service
│   ├── create_arc20_token.py   # Script for ARC-20 creation
│   ├── employees.json          # Demo employee data
│   ├── utils.py                # Helper functions
│   ├── requirements.txt        # Python dependencies
│   └── README-backend.md
│
├── contracts/
│   ├── create_employees.py
│   ├── optin_employee_wallet.py
│   └── test_transaction.py
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── script_algorand.js
│   └── assets/
│       └── image.png
│
└── README.md
```
---
## 4. Component Responsibilities
4.1 Frontend
- Renders UI and employee dashboard
- Fetches company and employee data from backend
- Triggers claim functions
- Integrates PeraWallet using WalletConnect
- Displays transaction results to the user

4.2 Backend (Flask)
- Stores company metadata (address, ASA ID)
- Prepares ARC-20 transfer transactions
- Exposes REST APIs:
    GET /company
    GET /employees
    GET /employee/<id>
    POST /claim
    GET /transactions
- Builds unsigned Algorand transactions
- Supports CORS for frontend communication

4.3 Blockchain Layer
STRM ARC-20 Token: Asset ID 749531304
App ID: 749515555 (example)
Validates signatures, holds balances, ensures ledger state integrity
Employees must opt-in to receive STRM tokens

---
## 5. Execution Flows
5.1 Token Initialization (Developer Only)
1. Run create_arc20_token.py
2. Token STRM is created on TestNet
3. Asset ID is stored in backend config

5.2 Frontend Load
1. index.html loads
2. script_algorand.js calls:
       GET /company
       GET /employees
3. UI displays employee claimable amounts

5.3 Claim Flow
1. User clicks “Claim”
2. Frontend calls POST /claim
3. Backend prepares ARC-20 transfer txn
4. Returns unsigned transaction payload
5. Frontend sends payload to PeraWallet
6. Wallet signs and broadcasts
7. Frontend updates UI after confirmation

5.4 Opt-in Flow
Employees must opt-in to STRM ASA.
Backend can prepare opt-in txn when required.
Wallet signs → broadcasts → employee can now receive tokens.

---
### Wallet Architecture (Prototype Simplification)

StreamFi uses a minimal wallet architecture to keep the prototype simple and fast for demo use:

- **Company Wallet**  
  A single funded Algorand TestNet wallet.  
  It holds STRM tokens and signs outgoing ARC-20 transfers when an employee claims.

- **Employee Wallet (Shared Address)**  
  All employee profiles use the same Algorand address.  
  This drastically simplifies:
  - ASA opt-ins  
  - balancing testnet funds  
  - repeating claims for demo purposes  

Although simplified, the backend still performs real ARC-20 transfers and real TestNet transactions.

In a production-grade system, each employee would have a unique wallet address.

---
## 6. API Specification
GET /company
{
  "company_address": "SOMEALGOTADDR",
  "asset_id": 749531304,
  "app_id": 749515555
}

GET /employees
[
  {
    "id": 1,
    "name": "Employee A",
    "address": "EMPLOYEE_ALGO_ADDR",
    "claimable": 1000,
    "opted_in": true
  }
]

POST /claim

Request:

{
  "employee_id": 1
}


Response example:

{
  "tx_group": "BASE64_GROUP_DATA",
  "metadata": {
    "employee_id": 1
  }
}

GET /transactions
Returns recent transaction IDs and statuses.

---


---
## 7. Running the System Locally
7.1 Backend
cd streamfi-simple/backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python app.py


Expected:

http://127.0.0.1:5000

7.2 Frontend

Python static server:

cd streamfi-simple/frontend
python -m http.server 8080


Open:

http://localhost:8080


Or use VS Code Live Server.

---
## 8. Deployment
"need to be updated"


Update script_algorand.js to point to Render backend URL.

---
## 9. Security Notes
- Never expose private keys to frontend
- Backend should sign only admin-level transactions
- User-initiated transactions must be signed in PeraWallet
- Always use HTTPS endpoints

---
## 10. Debugging
Wallet failing to connect → check WalletConnect version
Opt-in failure → ensure employee opted_in=true
Transaction rejected → verify fees, validity rounds
CORS errors → ensure flask_cors enabled
Deployment issues → check environment variables on Render

---
## 11. Extension Ideas
- Continuous automated token streaming
- Admin HR dashboards
- Postgres database for persistence
- Notification system for claim events

---
## 12. Useful Commands

Create token:

python create_arc20_token.py


Run backend with variables:

$env:ALGOD_API_KEY="key"
$env:COMPANY_PRIVATE_KEY="private"
python app.py
