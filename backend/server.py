"""
StreamFi Backend Server - FIXED VERSION
All issues resolved - Ready for hackathon demo!
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import AssetTransferTxn, AssetOptInTxn, PaymentTxn, wait_for_confirmation
import time

app = Flask(__name__)
CORS(app)

# TestNet Configuration
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""
STRM_ASSET_ID = 749531304

# WALLET 1: Company wallet (has all STRM tokens)
COMPANY_ADDRESS = "ZX2LBXKXNBRCJVECB7AHU22PPMDIDHCRAPKEVZ5UIUSGZF2LISTEG3IPEQ"
COMPANY_MNEMONIC = "cluster coin olympic congress ribbon lamp despair maple dizzy disagree undo inquiry purchase hamster curve nuclear topic shaft evil glide loud soldier talk absent wool"
company_private_key = mnemonic.to_private_key(COMPANY_MNEMONIC)

# WALLET 2: Employee collective wallet (where tokens go when claimed)
# NOW USING YOUR REAL WALLET 2 - IT'S OPTED-IN! ✅
EMPLOYEE_WALLET_ADDRESS = "QZTLJBJSCVDHPCJXT3LQGDCRNBA3IRYVCPLFEA3GWN6YCTNOP4FPH7F4HE"


# Initialize Algod client
algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

# Employee accounts (individual tracking for demo)
EMPLOYEES = {
    "Anirudh": {"designation": "Blockchain Developer", "rate": 2},
    "Saksham": {"designation": "Frontend Engineer", "rate": 3},
    "Harshavardhan": {"designation": "Backend Engineer", "rate": 1.5},
    "Sundaram": {"designation": "Smart Contract Auditor", "rate": 2.5},
    "Shashi": {"designation": "Product Manager", "rate": 4},
    "Sumit": {"designation": "UI/UX Designer", "rate": 1}
}

# Streaming sessions
streaming_sessions = {}

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
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
    Start streaming session for an employee
    """
    try:
        data = request.json
        employee_name = data.get('name')
        
        if employee_name not in EMPLOYEES:
            return jsonify({"error": "Employee not found"}), 404
        
        employee = EMPLOYEES[employee_name]
        
        # Start streaming session
        streaming_sessions[employee_name] = {
            "start_time": time.time(),
            "rate": employee["rate"],
            "total_claimed": 0
        }
        
        print(f"✅ {employee_name} logged in - Streaming started")
        
        return jsonify({
            "success": True,
            "rate": employee["rate"],
            "designation": employee["designation"]
        })
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/balance', methods=['POST'])
def get_balance():
    """
    Calculate claimable balance for an employee
    """
    try:
        data = request.json
        employee_name = data.get('name')
        
        if employee_name not in streaming_sessions:
            return jsonify({"balance": 0})
        
        session = streaming_sessions[employee_name]
        elapsed_time = time.time() - session["start_time"]
        claimable = elapsed_time * session["rate"]
        
        return jsonify({
            "balance": round(claimable, 2),
            "elapsed_seconds": round(elapsed_time, 2)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/claim', methods=['POST'])
def claim_tokens():
    """
    Transfer STRM tokens from Company Wallet to Employee Collective Wallet
    """
    try:
        data = request.json
        employee_name = data.get('name')
        amount = float(data.get('amount', 0))
        
        if employee_name not in EMPLOYEES:
            return jsonify({"error": "Employee not found"}), 404
        
        if amount < 1:
            return jsonify({"error": "Minimum 1 STRM required"}), 400
        
        # Convert STRM to base units (2 decimals)
        amount_base_units = int(amount * 100)
        
        print(f"\n{'='*70}")
        print(f"🪙 CLAIMING TOKENS")
        print(f"{'='*70}")
        print(f"Employee: {employee_name}")
        print(f"Amount: {amount} STRM")
        print(f"From (Company): {COMPANY_ADDRESS[:10]}...{COMPANY_ADDRESS[-10:]}")
        print(f"To (Employee Wallet): {EMPLOYEE_WALLET_ADDRESS[:10]}...{EMPLOYEE_WALLET_ADDRESS[-10:]}")
        
        # Get transaction params
        params = algod_client.suggested_params()
        
        # Create asset transfer transaction
        # Company Wallet → Employee Collective Wallet
        txn = AssetTransferTxn(
            sender=COMPANY_ADDRESS,
            sp=params,
            receiver=EMPLOYEE_WALLET_ADDRESS,
            amt=amount_base_units,
            index=STRM_ASSET_ID
        )
        
        # Sign transaction with company private key
        signed_txn = txn.sign(company_private_key)
        
        # Send transaction
        print("📤 Sending transaction to blockchain...")
        tx_id = algod_client.send_transaction(signed_txn)
        print(f"✅ Transaction ID: {tx_id}")
        
        # Wait for confirmation
        print("⏳ Waiting for confirmation...")
        confirmed_txn = wait_for_confirmation(algod_client, tx_id, 4)
        
        print(f"✅ Confirmed in block: {confirmed_txn['confirmed-round']}")
        print(f"{'='*70}\n")
        
        # Update session
        if employee_name in streaming_sessions:
            streaming_sessions[employee_name]["total_claimed"] += amount
            streaming_sessions[employee_name]["start_time"] = time.time()  # Reset timer
        
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
        print(f"❌ Claim error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """
    End streaming session for an employee
    """
    try:
        data = request.json
        employee_name = data.get('name')
        
        if employee_name in streaming_sessions:
            total_claimed = streaming_sessions[employee_name]["total_claimed"]
            del streaming_sessions[employee_name]
            print(f"✅ {employee_name} logged out - Total claimed: {total_claimed} STRM")
        
        return jsonify({"success": True})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print(" 🚀 STREAMFI BACKEND SERVER - READY FOR DEMO!")
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
    app.run(debug=True, port=5000, use_reloader=False)