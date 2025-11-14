from flask import Flask, request, jsonify
from flask_cors import CORS
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import AssetTransferTxn, AssetOptInTxn, PaymentTxn, wait_for_confirmation
import time

app = Flask(__name__)
CORS(app)  # Enable CORS so frontend hosted elsewhere can call these endpoints

# TestNet Configuration
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"  # Public TestNet RPC endpoint
ALGOD_TOKEN = ""  # No token needed for public Algonode endpoints
STRM_ASSET_ID = 749531304  # ARC-20 token asset id used by this demo

# WALLET 1: Company wallet (holds STRM tokens that will be streamed / claimed)
COMPANY_ADDRESS = "ZX2LBXKXNBRCJVECB7AHU22PPMDIDHCRAPKEVZ5UIUSGZF2LISTEG3IPEQ"
COMPANY_MNEMONIC = "cluster coin olympic congress ribbon lamp despair maple dizzy disagree undo inquiry purchase hamster curve nuclear topic shaft evil glide loud soldier talk absent wool"
# Convert mnemonic phrase into a private key that can sign transactions
company_private_key = mnemonic.to_private_key(COMPANY_MNEMONIC)

# WALLET 2: Employee collective wallet (where tokens are transferred when claimed)
# For demo simplicity, this single wallet acts as the recipient for all employee claims
EMPLOYEE_WALLET_ADDRESS = "QZTLJBJSCVDHPCJXT3LQGDCRNBA3IRYVCPLFEA3GWN6YCTNOP4FPH7F4HE"

# Initialize Algod client to communicate with Algorand TestNet
algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

# Employee definitions for the demo. Each has a name, role, and streaming rate (STRM per second)
EMPLOYEES = {
    "Anirudh": {"designation": "Blockchain Developer", "rate": 2},
    "Saksham": {"designation": "Frontend Engineer", "rate": 3},
    "Harshavardhan": {"designation": "Backend Engineer", "rate": 1.5},
    "Sundaram": {"designation": "Smart Contract Auditor", "rate": 2.5},
    "Shashi": {"designation": "Product Manager", "rate": 4},
    "Sumit": {"designation": "UI/UX Designer", "rate": 1}
}

# Tracks active streaming sessions per employee. Each entry stores start_time, rate, and total_claimed
streaming_sessions = {}

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint.
    Returns basic runtime metadata so frontend or CI can validate the service is online.
    """
    return jsonify({
        "status": "ok",
        "network": "testnet",
        "company_wallet": COMPANY_ADDRESS,
        "employee_wallet": EMPLOYEE_WALLET_ADDRESS,
        "asset_id": STRM_ASSET_ID
    })

@app.route('/api/login', methods=['POST'])
def login():
    """
    Start streaming session for an employee.
    Expects JSON payload with 'name'. If the employee exists, create a streaming session
    storing start_time, rate, and total_claimed.
    """
    try:
        data = request.json
        employee_name = data.get('name')
        
        if employee_name not in EMPLOYEES:
            # Employee not known in demo dataset
            return jsonify({"error": "Employee not found"}), 404
        
        employee = EMPLOYEES[employee_name]
        
        # Start a new streaming session for the employee
        streaming_sessions[employee_name] = {
            "start_time": time.time(),
            "rate": employee["rate"],
            "total_claimed": 0
        }
        
        # Log for server-side debugging during demo
        print(f"✅ {employee_name} logged in - Streaming started")
        
        # Return basic session metadata to the frontend
        return jsonify({
            "success": True,
            "rate": employee["rate"],
            "designation": employee["designation"]
        })
        
    except Exception as e:
        # Unexpected error while starting a session
        print(f"❌ Login error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/balance', methods=['POST'])
def get_balance():
    """
    Calculate and return the current claimable balance for an employee.
    The balance is computed as elapsed_seconds * rate from the streaming session.
    Returns rounded balance and elapsed_seconds for UI display.
    """
    try:
        data = request.json
        employee_name = data.get('name')
        
        if employee_name not in streaming_sessions:
            # No active session, nothing is claimable
            return jsonify({"balance": 0})
        
        session = streaming_sessions[employee_name]
        elapsed_time = time.time() - session["start_time"]
        claimable = elapsed_time * session["rate"]
        
        # Return human-friendly numbers (rounded)
        return jsonify({
            "balance": round(claimable, 2),
            "elapsed_seconds": round(elapsed_time, 2)
        })
        
    except Exception as e:
        # Return error info to the caller if anything goes wrong
        return jsonify({"error": str(e)}), 500

@app.route('/api/claim', methods=['POST'])
def claim_tokens():
    """
    Transfer STRM tokens from Company Wallet to Employee Collective Wallet.
    Expects JSON with 'name' and 'amount'. Validates employee exists and amount is >= 1 STRM.
    Constructs an Algorand AssetTransferTxn, signs it with the company private key,
    submits it to the network, waits for confirmation, and updates session totals.
    """
    try:
        data = request.json
        employee_name = data.get('name')
        amount = float(data.get('amount', 0))
        
        if employee_name not in EMPLOYEES:
            return jsonify({"error": "Employee not found"}), 404
        
        # Enforce a minimum claim amount for demo
        if amount < 1:
            return jsonify({"error": "Minimum 1 STRM required"}), 400
        
        # Convert STRM to base units. This demo assumes 2 decimals -> multiply by 100
        amount_base_units = int(amount * 100)
        
        # Print informative logs for the operator during demo
        print(f"\n{'='*70}")
        print(f"🪙 CLAIMING TOKENS")
        print(f"{'='*70}")
        print(f"Employee: {employee_name}")
        print(f"Amount: {amount} STRM")
        print(f"From (Company): {COMPANY_ADDRESS[:10]}...{COMPANY_ADDRESS[-10:]}")
        print(f"To (Employee Wallet): {EMPLOYEE_WALLET_ADDRESS[:10]}...{EMPLOYEE_WALLET_ADDRESS[-10:]}")
        
        # Fetch recommended transaction params from the algod node (fees, first/last valid rounds)
        params = algod_client.suggested_params()
        
        # Build the ASA transfer transaction object
        # This will transfer the asset STRM from the company to the employee collective wallet
        txn = AssetTransferTxn(
            sender=COMPANY_ADDRESS,
            sp=params,
            receiver=EMPLOYEE_WALLET_ADDRESS,
            amt=amount_base_units,
            index=STRM_ASSET_ID
        )
        
        # Sign the transaction using the company's private key (server-side signing for demo)
        signed_txn = txn.sign(company_private_key)
        
        # Send the signed transaction to the network
        print("📤 Sending transaction to blockchain...")
        tx_id = algod_client.send_transaction(signed_txn)
        print(f"✅ Transaction ID: {tx_id}")
        
        # Wait for transaction confirmation for up to a small number of rounds (blocking)
        print("⏳ Waiting for confirmation...")
        confirmed_txn = wait_for_confirmation(algod_client, tx_id, 4)
        
        print(f"✅ Confirmed in block: {confirmed_txn['confirmed-round']}")
        print(f"{'='*70}\n")
        
        # If the employee has an active session, update their total claimed and reset timer
        if employee_name in streaming_sessions:
            streaming_sessions[employee_name]["total_claimed"] += amount
            streaming_sessions[employee_name]["start_time"] = time.time()  # Reset the streaming timer
        
        # Return transaction details for frontend display and explorer linking
        return jsonify({
            "success": True,
            "transaction_id": tx_id,
            "amount": amount,
            "block": confirmed_txn['confirmed-round'],
            "from": COMPANY_ADDRESS,
            "to": EMPLOYEE_WALLET_ADDRESS,
            "explorer_url": f"https://testnet.explorer.perawallet.app/tx/{tx_id}"
        })
        
    except Exception as e:
        # Log and return errors to the caller
        print(f"❌ Claim error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """
    End streaming session for an employee.
    Removes their session entry and reports the total claimed amount in server logs.
    """
    try:
        data = request.json
        employee_name = data.get('name')
        
        if employee_name in streaming_sessions:
            total_claimed = streaming_sessions[employee_name]["total_claimed"]
            # Remove the session data to stop streaming
            del streaming_sessions[employee_name]
            print(f"✅ {employee_name} logged out - Total claimed: {total_claimed} STRM")
        
        return jsonify({"success": True})
        
    except Exception as e:
        # Return any error encountered during logout
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Startup banner prints useful runtime info for the demo operator
    print("\n" + "=" * 70)
    print(" STREAMFI BACKEND SERVER - READY FOR DEMO!")
    print("=" * 70)
    print(f" Company Wallet: {COMPANY_ADDRESS}")
    print(f" Employee Wallet: {EMPLOYEE_WALLET_ADDRESS}")
    print(f" STRM Asset ID: {STRM_ASSET_ID}")
    print(f" Network: Algorand TestNet")
    print(f" Employees: {len(EMPLOYEES)}")
    print("=" * 70)
    print(f"\n Flow: Company Wallet → Employee Collective Wallet")
    print(f" (Same wallet for demo - both already opted-in!)")
    print("\n ✅ Server running on http://localhost:5000\n")
    print(" Press CTRL+C to stop\n")
    # Run the Flask development server on port 5000 for local demos
    app.run(debug=True, port=5000, use_reloader=False)
