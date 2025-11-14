"""
Opt-In Employee Wallet to STRM Token
This is a ONE-TIME setup script
"""

from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import AssetOptInTxn, PaymentTxn, wait_for_confirmation

# TestNet Configuration
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""
STRM_ASSET_ID = 749531304

# Company wallet (to fund employee wallet with ALGO)
COMPANY_MNEMONIC = "cluster coin olympic congress ribbon lamp despair maple dizzy disagree undo inquiry purchase hamster curve nuclear topic shaft evil glide loud soldier talk absent wool"
company_private_key = mnemonic.to_private_key(COMPANY_MNEMONIC)
company_address = account.address_from_private_key(company_private_key)

# Employee collective wallet
EMPLOYEE_WALLET_ADDRESS = "QZTLJBJSCVDHPCJXT3LQGDCRNBA3IRYVCPLFEA3GWN6YCTNOP4FPH7F4HE"

# You need the mnemonic for employee wallet!
# If you don't have it, we'll need to use your company wallet instead
# For now, let me show you both options:

print("=" * 70)
print(" 🔧 EMPLOYEE WALLET OPT-IN TO STRM TOKEN")
print("=" * 70)
print(f" Employee Wallet: {EMPLOYEE_WALLET_ADDRESS}")
print(f" STRM Asset ID: {STRM_ASSET_ID}")
print("=" * 70)

# Initialize Algod client
algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

def check_and_fund_employee_wallet():
    """
    Check if employee wallet has ALGO, if not fund it
    """
    try:
        account_info = algod_client.account_info(EMPLOYEE_WALLET_ADDRESS)
        balance = account_info.get('amount', 0) / 1_000_000
        print(f"\n📊 Employee Wallet ALGO Balance: {balance:.2f} ALGO")
        
        if balance < 0.2:
            print(f"\n💰 Funding employee wallet with 0.5 ALGO for fees...")
            params = algod_client.suggested_params()
            
            txn = PaymentTxn(
                sender=company_address,
                sp=params,
                receiver=EMPLOYEE_WALLET_ADDRESS,
                amt=500000  # 0.5 ALGO
            )
            
            signed_txn = txn.sign(company_private_key)
            tx_id = algod_client.send_transaction(signed_txn)
            
            print(f"📤 Funding transaction sent: {tx_id}")
            wait_for_confirmation(algod_client, tx_id, 4)
            print(f"✅ Employee wallet funded!")
            
    except Exception as e:
        print(f"\n💰 Creating and funding employee wallet...")
        params = algod_client.suggested_params()
        
        txn = PaymentTxn(
            sender=company_address,
            sp=params,
            receiver=EMPLOYEE_WALLET_ADDRESS,
            amt=500000  # 0.5 ALGO
        )
        
        signed_txn = txn.sign(company_private_key)
        tx_id = algod_client.send_transaction(signed_txn)
        
        print(f"📤 Funding transaction sent: {tx_id}")
        wait_for_confirmation(algod_client, tx_id, 4)
        print(f"✅ Employee wallet created and funded!")

def optin_to_strm():
    """
    Opt-in employee wallet to STRM token
    """
    print("\n" + "=" * 70)
    print(" IMPORTANT: I NEED EMPLOYEE WALLET MNEMONIC")
    print("=" * 70)
    print("\n Do you have the 25-word mnemonic for this wallet:")
    print(f" {EMPLOYEE_WALLET_ADDRESS}")
    print("\n If YES:")
    print("   1. Paste it below when prompted")
    print("\n If NO:")
    print("   1. We'll use company wallet as employee wallet instead")
    print("=" * 70)
    
    has_mnemonic = input("\nDo you have the employee wallet mnemonic? (yes/no): ").strip().lower()
    
    if has_mnemonic == 'yes':
        employee_mnemonic = input("\nPaste employee wallet 25-word mnemonic: ").strip()
        
        try:
            employee_private_key = mnemonic.to_private_key(employee_mnemonic)
            employee_address = account.address_from_private_key(employee_private_key)
            
            if employee_address != EMPLOYEE_WALLET_ADDRESS:
                print(f"\n❌ ERROR: Mnemonic doesn't match employee wallet address!")
                print(f"   Expected: {EMPLOYEE_WALLET_ADDRESS}")
                print(f"   Got: {employee_address}")
                return False
            
            print(f"\n✅ Mnemonic verified!")
            
            # Opt-in to STRM
            print(f"\n🔓 Opting in to STRM token...")
            params = algod_client.suggested_params()
            
            txn = AssetOptInTxn(
                sender=employee_address,
                sp=params,
                index=STRM_ASSET_ID
            )
            
            signed_txn = txn.sign(employee_private_key)
            tx_id = algod_client.send_transaction(signed_txn)
            
            print(f"📤 Opt-in transaction sent: {tx_id}")
            wait_for_confirmation(algod_client, tx_id, 4)
            
            print(f"\n{'='*70}")
            print(f" ✅ SUCCESS! EMPLOYEE WALLET OPTED IN TO STRM!")
            print(f"{'='*70}")
            print(f" View on Explorer:")
            print(f" https://testnet.explorer.perawallet.app/tx/{tx_id}")
            print(f"{'='*70}\n")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return False
    else:
        print(f"\n⚠️  NO PROBLEM! Let's use Company Wallet as Employee Wallet instead!")
        print(f"\n   Company Wallet: {company_address}")
        print(f"   This wallet already has STRM tokens and is opted-in!")
        print(f"\n   Update your backend server.py:")
        print(f"   Change EMPLOYEE_WALLET_ADDRESS to: {company_address}")
        return False

if __name__ == "__main__":
    try:
        # Step 1: Check and fund employee wallet
        check_and_fund_employee_wallet()
        
        # Step 2: Opt-in to STRM
        optin_to_strm()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")