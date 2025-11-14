"""
ARC-20 Token Creation for StreamFi
Hackathon Requirement: Demonstrate ARC standard usage
"""

from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import AssetConfigTxn, wait_for_confirmation
import json

# TestNet Configuration
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""

# Your deployer mnemonic
DEPLOYER_MNEMONIC = "cluster coin olympic congress ribbon lamp despair maple dizzy disagree undo inquiry purchase hamster curve nuclear topic shaft evil glide loud soldier talk absent wool"

def create_arc20_token():
    """
    Create ARC-20 compliant fungible token for StreamFi
    
    ARC-20 Standard Requirements:
    - Fungible asset (divisible)
    - Manager address (for reconfiguration)
    - Reserve address (for token supply management)
    - Proper metadata (name, unit name, URL)
    """
    
    try:
        # Initialize Algod client
        algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
        
        # Get deployer account
        private_key = mnemonic.to_private_key(DEPLOYER_MNEMONIC)
        creator_address = account.address_from_private_key(private_key)
        
        print(f" Creator Address: {creator_address}")
        
        # Check balance - FIXED METHOD NAME
        account_info = algod_client.account_info(creator_address)
        balance = account_info.get('amount') / 1_000_000
        print(f" Balance: {balance} ALGO")
        
        if balance < 0.5:
            print(" Insufficient balance! Need at least 0.5 ALGO for token creation.")
            print("   Fund your account at: https://bank.testnet.algorand.network/")
            return None
        
        # Get transaction parameters
        params = algod_client.suggested_params()
        
        # ARC-20 Token Configuration
        token_config = {
            "total": 1_000_000 * 100,  # 1 million tokens (with 2 decimals = 100M base units)
            "decimals": 2,              # 2 decimal places
            "default_frozen": False,    # Tokens not frozen by default
            "unit_name": "STRM",        # Ticker symbol (3-8 characters)
            "asset_name": "StreamFi Payment Token",  # Full name
            "url": "https://streamfi.algorand.network/token",  # Metadata URL
            "manager": creator_address,   # Can reconfigure asset
            "reserve": creator_address,   # Holds uncirculated tokens
            "freeze": creator_address,    # Can freeze accounts
            "clawback": creator_address   # Can revoke tokens
        }
        
        print(f"\n Creating ARC-20 Token:")
        print(f"   Name: {token_config['asset_name']}")
        print(f"   Unit: {token_config['unit_name']}")
        print(f"   Total Supply: {token_config['total'] / 100:,.0f} STRM")
        print(f"   Decimals: {token_config['decimals']}")
        
        # Create asset transaction
        txn = AssetConfigTxn(
            sender=creator_address,
            sp=params,
            **token_config
        )
        
        # Sign transaction
        signed_txn = txn.sign(private_key)
        
        # Submit transaction
        print("\n Submitting transaction to TestNet...")
        txid = algod_client.send_transaction(signed_txn)
        print(f"   Transaction ID: {txid}")
        
        # Wait for confirmation
        print(" Waiting for confirmation...")
        wait_for_confirmation(algod_client, txid, 4)
        
        # Get asset ID
        ptx = algod_client.pending_transaction_info(txid)
        asset_id = ptx["asset-index"]
        
        print(f"\n SUCCESS! ARC-20 Token Created!")
        print(f"   Asset ID: {asset_id}")
        print(f"   Explorer: https://testnet.explorer.perawallet.app/asset/{asset_id}")
        
        # Save token info
        token_info = {
            "asset_id": asset_id,
            "asset_name": token_config["asset_name"],
            "unit_name": token_config["unit_name"],
            "total_supply": token_config["total"],
            "decimals": token_config["decimals"],
            "creator": creator_address,
            "txid": txid
        }
        
        with open("arc20_token_info.json", "w") as f:
            json.dump(token_info, f, indent=2)
        
        print("\n Token info saved to: arc20_token_info.json")
        
        return asset_id
        
    except Exception as e:
        print(f"\n Error creating token: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print(" StreamFi ARC-20 Token Creator")
    print("   Hackathon Compliance: ARC Standard Implementation")
    print("=" * 60 + "\n")
    
    asset_id = create_arc20_token()
    
    if asset_id:
        print("\n" + "=" * 60)
        print("Token creation complete!")
        print("   Use this Asset ID in your smart contract")
        print("=" * 60)
