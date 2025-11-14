from algosdk import account, mnemonic

print("=" * 70)
print(" CREATING EMPLOYEE ACCOUNTS")
print("=" * 70)

for i in range(3):  # Create 3 employees
    private_key, address = account.generate_account()
    mn = mnemonic.from_private_key(private_key)
    
    print(f"\n**Employee {i+1}:**")
    print(f"Address: {address}")
    print(f"Mnemonic: {mn}")
    print(f"(Save this mnemonic!)")
    print("-" * 70)