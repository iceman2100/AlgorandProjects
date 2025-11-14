# ARCHITECTURE.md
StreamFi — Detailed Architecture and Build Instructions
 
> <img width="1886" height="899" alt="image" src="https://github.com/user-attachments/assets/6d6ab08f-f6e1-45d5-aa87-5c7b99cef70a" />


---

## 0. Purpose of this document
This file documents the full architecture of StreamFi, a hackathon-grade salary-streaming prototype on Algorand TestNet.  
It explains what each component is, how components interact, how to run and deploy the system, and why certain design choices were made. Use this as a single, authoritative reference for development, testing, and deployment.

---

## 1. High-level system summary
StreamFi consists of three logical layers:
1. Frontend — HTML, CSS, JavaScript. Provides UI and wallet integration (PeraWallet).  
2. Backend — Python Flask server. Builds transactions and exposes REST endpoints.  
3. Blockchain — Algorand TestNet with an ARC-20 token (STRM) and a minimal PyTEAL application.

Users interact with the frontend; the frontend calls the backend for data and transactions; the backend prepares transactions and coordinates with the wallet which signs and broadcasts to Algorand TestNet.

---

## 2. Diagram
Embed your diagram image under the title, using the path:

yaml
Copy code
This image should visually match the layers and component boxes described below.

---

## 3. Folder structure (explicit)
streamfi-simple/
│
├── backend/
│ ├── app.py # Main Flask server
│ ├── create_arc20_token.py # Script to create ARC-20 token
│ ├── employees.json # Demo employee data
│ ├── utils.py # Algorand SDK helper functions
│ ├── requirements.txt # Python dependencies (algosdk, flask, flask-cors, gunicorn, etc.)
│ └── README-backend.md # Backend-specific notes (optional)
│
├── contracts/
│ ├── create_employees.py # PyTEAL / contract helper scripts
│ ├── optin_employee_wallet.py
│ └── test_transaction.py
│
├── frontend/
│ ├── index.html
│ ├── styles.css
│ ├── script_algorand.js # Wallet + API + UI logic
│ └── assets/
│ └── image.png # Architecture diagram image referenced above
│
└── README.md

markdown
Copy code

---

## 4. Component responsibilities (detailed)

### 4.1 Frontend
- **Files**: `index.html`, `styles.css`, `script_algorand.js`.
- **Responsibilities**:
  - Render employee dashboard (balances, claim buttons, company info).
  - Provide wallet connect flow using WalletConnect / PeraWallet.
  - Call backend endpoints to fetch `company`, `employees`, and `claim` data.
  - Receive unsigned or partially signed transactions from backend and forward them to PeraWallet for signing and broadcasting.
  - Poll for transaction status or update UI after wallet broadcasts a transaction.

### 4.2 Backend (Flask)
- **Files**: `app.py`, helper modules.
- **Responsibilities**:
  - Store or load company wallet metadata (address, optionally a funded private key on development machine for token creation tasks).
  - Expose REST endpoints:
    - `GET /company` — returns company address and asset ID.
    - `GET /employees` — returns list of employees and their pending/claimable balances.
    - `GET /employee/<id>` — returns a single employee status.
    - `POST /claim` — backend builds transaction payload for a claim and returns it (unsigned or prepared group).
    - `GET /transactions` — optional, returns recent related txns.
  - Construct Algorand transactions (ASA transfer) using `algosdk`.
  - Optionally assemble transaction groups and return JSON representations suitable for WalletConnect signing.
  - (Dev-only) scripts to create ARC-20 token and deploy basic PyTEAL contracts.
  - Provide CORS support to allow frontend origin to call APIs.

### 4.3 Blockchain Layer (Algorand TestNet)
- **Artifacts**:
  - ARC-20 token STRM with Asset ID: `749531304`.
  - Application smart contract ID: `749515555` (example; actual ID from your deploy).
- **Responsibilities**:
  - Ledger for recording token transfers and application state.
  - Validate signatures and application logic.
  - Opt-in by employee accounts for ASA transfers (employee wallets must opt-in to receive STRM).

---

## 5. Execution flows (step-by-step)

### 5.1 Initialization / Token creation (one-time, developer)
1. Developer runs `backend/create_arc20_token.py` or relevant script.
2. Script uses `algosdk` with funded company account to create ARC-20 token. It prints the Asset ID and manager addresses.
3. Optionally deploy PyTEAL app and record its app ID.

**Result**: `STRM` ASA deployed on TestNet. Asset ID available for backend config.

### 5.2 Frontend load (user arrives)
1. Browser loads `index.html`.
2. `script_algorand.js` fetches `GET /company` and `GET /employees`.
3. UI renders employee rows with current claimable amounts.

### 5.3 Claim flow (user action)
1. User clicks "Claim" for a particular employee.
2. Frontend calls `POST /claim` (or `GET /claim/<id>` depending on design).
3. Backend constructs ASA transfer transaction:
   - Sender: company address (or a delegated signer depending on design).
   - Receiver: employee wallet address.
   - Asset ID: `749531304`.
   - Amount: computed claimable amount.
4. Backend returns the unsigned transaction payload (or a signed blob if you use server signing, but recommended: unsigned).
5. Frontend receives the payload and initiates WalletConnect / PeraWallet signing flow.
6. PeraWallet user reviews and signs the transaction on-device.
7. Wallet broadcasts signed transaction to Algorand TestNet.
8. Transaction confirmed; frontend polls for confirmation and updates UI.

### 5.4 Opt-in flow (employee first-time only)
1. If an employee wallet is not opted-in for the ASA, the frontend or backend triggers opt-in flow:
   - Backend returns a prepared opt-in txn for the wallet to sign.
   - Wallet signs and broadcasts the opt-in txn.
2. After confirmation, wallet can receive STRM.

---

## 6. API specification (explicit)

### GET /company
**Response**
```json
{
  "company_address": "SOMEALGOTADDR",
  "asset_id": 749531304,
  "app_id": 749515555
}
GET /employees
Response

json
Copy code
[
  {
    "id": 1,
    "name": "Employee A",
    "address": "EMPLOYEE_ALGO_ADDR",
    "claimable": 1000,
    "opted_in": true
  },
  ...
]
POST /claim
Request

json
Copy code
{
  "employee_id": 1
}
Response

Returns unsigned transaction object or WalletConnect-ready transaction payload. Example:

json
Copy code
{
  "tx_group": "...",        // either raw txns or base64 representation
  "metadata": { ... }
}
GET /transactions
Optional debugging endpoint. Returns recent transaction IDs and statuses.

7. Environment variables and configuration
Place secrets in Render or a .env (never commit secrets).

Typical environment variables:

ini
Copy code
ALGOD_API_URL=https://testnet-algorand.api.purestake.io/ps2
ALGOD_API_KEY=<PURESTAKE_KEY>
INDEXER_URL=https://testnet-algorand.api.purestake.io/idx2
COMPANY_PRIVATE_KEY=<dev-only, keep off client>
COMPANY_ADDRESS=<funded-address>
ASSET_ID=749531304
APP_ID=749515555
FLASK_ENV=production

cd D:\AlgorandProjects\streamfi-simple\backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt
# Make sure requirements.txt has: algosdk, flask, flask-cors, gunicorn (optional), pyteal (if used)
# Set environment variables for testnet or create a local .env and load before running

python app.py
# Expected: Flask starts on http://127.0.0.1:5000
8.2 Frontend
Option 1 — VS Code Live Server: open frontend/index.html with Live Server.
Option 2 — Python HTTP server:

bash
Copy code
cd D:\AlgorandProjects\streamfi-simple\frontend
python -m http.server 8080
# open http://localhost:8080
8.3 Quick sanity checks
GET http://127.0.0.1:5000/company returns company info.

Frontend script_algorand.js endpoints point to http://127.0.0.1:5000.

PeraWallet signing uses WalletConnect; test on mobile or Pera extension.

9. Deployment (detailed, step-by-step)
9.1 Backend → Render (recommended)
Create a Render account and connect GitHub.

New → Web Service → Choose repository AlgorandProjects.

Root Directory: streamfi-simple/backend

Branch: main

Build Command:

nginx
Copy code
pip install -r requirements.txt
Start Command:

nginx
Copy code
gunicorn app:app --bind 0.0.0.0:$PORT
(If not using gunicorn, use python app.py, but gunicorn is recommended.)

Add environment variables in Render dashboard (ALGOD_API_KEY, COMPANY_PRIVATE_KEY, etc).

Deploy and wait for the public URL.

9.2 Frontend → Vercel (recommended) or Render Static
Create Vercel account and connect GitHub.

New Project → select AlgorandProjects.

Project Root: streamfi-simple/frontend

Framework Preset: Static / None.

Build: none. Output dir: .

Deploy. Vercel provides a URL for the frontend.

Update frontend config (script) to use backend production URL instead of localhost.

10. Security considerations
Never store private keys in the frontend or public repo.

Use ephemeral keys and backend-controlled operations only for management tasks.

Prefer user wallet signing via PeraWallet for all user-initiated transactions.

Use HTTPS endpoints for all API calls.

Rate-limit claim endpoints if public.

11. Debugging & common issues
Wallet not connecting: verify WalletConnect version and PeraWallet configuration in script_algorand.js.

Opt-in required: check employee wallet opted-in to the ASA. Backend should flag opted_in=false.

Transaction rejected: inspect transaction group order and fields, ensure fee and first/last valid parameters set.

CORS errors: enable flask_cors.CORS(app) in app.py.

Missing dependency: run pip install -r requirements.txt locally and in deployment.

12. Extension ideas (brief)
Replace claim mining logic with continuous streaming (on-chain TEAL scheduler or time-locked logic).

Add persistent database (Postgres) to store claim history and employee profiles.

Implement role-based admin dashboard for HR to adjust rates.

Add email/SMS notifications on claim or payout.

13. Appendix: Useful commands (copy/paste)
Algorand asset creation (example)
python
Copy code
# run create_arc20_token.py and capture the returned asset id
python create_arc20_token.py
Start Flask with environment variables (Windows PowerShell)
powershell
Copy code
$env:ALGOD_API_KEY="your_key"
$env:COMPANY_PRIVATE_KEY="your_dev_private"
python app.py
