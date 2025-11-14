"""
StreamFi TestNet Transaction Demo
Simple STRM token transfer - Perfect for hackathon demo!
"""

from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import AssetTransferTxn, wait_for_confirmation

# TestNet Configuration
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""

# Your creator account
CREATOR_MNEMONIC = "cluster coin olympic congress ribbon lamp despair maple dizzy disagree undo inquiry purchase hamster curve nuclear topic shaft evil glide loud soldier talk absent wool"

# STRM Token Asset ID
STRM_ASSET_ID = 749531304

# Your creator address (sender)
CREATOR_ADDRESS = "ZX2LBXKXNBRCJVECB7AHU22PPMDIDHCRAPKEVZ5UIUSGZF2LISTEG3IPEQ"

# Send to yourself (simplest demo - no opt-in needed!)
RECEIVER_ADDRESS = "ZX2LBXKXNBRCJVECB7AHU22PPMDIDHCRAPKEVZ5UIUSGZF2LISTEG3IPEQ"

def send_strm_tokens():
    """
    Send STRM tokens on TestNet
    """
    try:
        print("=" * 70)
        print(" 🚀 STREAMFI TESTNET TRANSACTION")
        print("=" * 70)
        print()
        
        # Initialize Algod client
        algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
        
        # Get private key
        sender_private_key = mnemonic.to_private_key(CREATOR_MNEMONIC)
        
        # Check balance
        print("📊 Checking Account Info...")
        account_info = algod_client.account_info(CREATOR_ADDRESS)
        algo_balance = account_info.get('amount') / 1_000_000
        
        # Find STRM token balance
        assets = account_info.get('assets', [])
        strm_balance = 0
        for asset in assets:
            if asset['asset-id'] == STRM_ASSET_ID:
                strm_balance = asset['amount'] / 100  # 2 decimals
                break
        
        print(f"   Address: {CREATOR_ADDRESS[:10]}...{CREATOR_ADDRESS[-10:]}")
        print(f"   ALGO Balance: {algo_balance:.2f} ALGO")
        print(f"   STRM Balance: {strm_balance:,.0f} STRM")
        print()
        
        # Prepare transaction
        amount_to_send = 100  # 100 STRM tokens
        amount_base_units = int(amount_to_send * 100)  # Convert to base units
        
        print(f"💸 Preparing Transaction...")
        print(f"   From: {CREATOR_ADDRESS[:10]}...{CREATOR_ADDRESS[-10:]}")
        print(f"   To: {RECEIVER_ADDRESS[:10]}...{RECEIVER_ADDRESS[-10:]}")
        print(f"   Amount: {amount_to_send} STRM")
        print(f"   Asset ID: {STRM_ASSET_ID}")
        print()
        
        # Get suggested params
        params = algod_client.suggested_params()
        
        # Create asset transfer transaction
        txn = AssetTransferTxn(
            sender=CREATOR_ADDRESS,
            sp=params,
            receiver=RECEIVER_ADDRESS,
            amt=amount_base_units,
            index=STRM_ASSET_ID
        )
        
        # Sign transaction
        signed_txn = txn.sign(sender_private_key)
        
        # Send transaction
        print("📤 Sending transaction to blockchain...")
        tx_id = algod_client.send_transaction(signed_txn)
        print(f"✅ Transaction ID: {tx_id}")
        print()
        
        # Wait for confirmation
        print("⏳ Waiting for confirmation (4-5 seconds)...")
        confirmed_txn = wait_for_confirmation(algod_client, tx_id, 4)
        
        # Success!
        print()
        print("=" * 70)
        print(" ✅ TRANSACTION CONFIRMED!")
        print("=" * 70)
        print()
        print(f"📝 Transaction Details:")
        print(f"   Transaction ID: {tx_id}")
        print(f"   Block: {confirmed_txn['confirmed-round']}")
        print(f"   Amount: {amount_to_send} STRM")
        print()
        print(f"🔍 View on Pera Explorer:")
        print(f"   Transaction: https://testnet.explorer.perawallet.app/tx/{tx_id}")
        print(f"   Token: https://testnet.explorer.perawallet.app/asset/{STRM_ASSET_ID}")
        print(f"   Account: https://testnet.explorer.perawallet.app/address/{CREATOR_ADDRESS}")
        print()
        print("🎤 READY FOR HACKATHON DEMO!")
        print("=" * 70)
        
        return tx_id
        
    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        print()
        print("💡 Troubleshooting:")
        print("   1. Check internet connection")
        print("   2. Verify you have enough ALGO for fees (~0.001 ALGO)")
        print("   3. Confirm Asset ID is correct: 749531304")
        print()
        return None

if __name__ == "__main__":
    print()
    send_strm_tokens()
    print()