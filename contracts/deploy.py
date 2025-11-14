from algosdk.v2client import algod
from algosdk import account, mnemonic, transaction
from algosdk.transaction import ApplicationCreateTxn, OnComplete, StateSchema
import base64

# TestNet connection
algod_address = "https://testnet-api.algonode.cloud"
algod_client = algod.AlgodClient("", algod_address)

# Use your funded account
passphrase = "cluster coin olympic congress ribbon lamp despair maple dizzy disagree undo inquiry purchase hamster curve nuclear topic shaft evil glide loud soldier talk absent wool"
private_key = mnemonic.to_private_key(passphrase)
address = account.address_from_private_key(private_key)

print(f" Deploying from: {address}")

# Read TEAL files
with open("streamfi_approval.teal", "r") as f:
    approval_program = f.read()

with open("streamfi_clear.teal", "r") as f:
    clear_program = f.read()

# Compile programs
approval_result = algod_client.compile(approval_program)
approval_binary = base64.b64decode(approval_result["result"])

clear_result = algod_client.compile(clear_program)
clear_binary = base64.b64decode(clear_result["result"])

# Define app schema
global_schema = StateSchema(num_uints=5, num_byte_slices=2)
local_schema = StateSchema(num_uints=0, num_byte_slices=0)

# Get suggested params
params = algod_client.suggested_params()

# Worker address (replace with actual worker for production)
worker_address = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY5HFKQ"
rate_per_second = 1000  # 1000 microAlgos per second

# Create application
txn = ApplicationCreateTxn(
    sender=address,
    sp=params,
    on_complete=OnComplete.NoOpOC,
    approval_program=approval_binary,
    clear_program=clear_binary,
    global_schema=global_schema,
    local_schema=local_schema,
    app_args=[worker_address.encode(), rate_per_second.to_bytes(8, 'big')]
)

# Sign and send
signed_txn = txn.sign(private_key)
tx_id = algod_client.send_transaction(signed_txn)

print(f"\n Transaction ID: {tx_id}")
print("⏳ Waiting for confirmation...")

# Wait for confirmation
transaction.wait_for_confirmation(algod_client, tx_id, 4)

# Get app ID
ptx = algod_client.pending_transaction_info(tx_id)
app_id = ptx["application-index"]

print(f"\n StreamFI Contract Deployed!")
print(f" App ID: {app_id}")
print(f" View on AlgoExplorer: https://testnet.algoexplorer.io/application/{app_id}")
