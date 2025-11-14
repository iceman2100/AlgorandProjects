from pyteal import *

def approval_program():
    # Global state keys
    employer_key = Bytes("employer")
    worker_key = Bytes("worker")
    rate_key = Bytes("rate")
    start_time_key = Bytes("start")
    last_claim_key = Bytes("last_claim")
    total_claimed_key = Bytes("claimed")
    
    # Initialize stream
    on_create = Seq([
        App.globalPut(employer_key, Txn.sender()),
        App.globalPut(worker_key, Txn.application_args[0]),
        App.globalPut(rate_key, Btoi(Txn.application_args[1])),
        App.globalPut(start_time_key, Global.latest_timestamp()),
        App.globalPut(last_claim_key, Global.latest_timestamp()),
        App.globalPut(total_claimed_key, Int(0)),
        Approve()
    ])
    
    # Get claimable balance
    get_claimable = Seq([
        App.globalPut(Bytes("temp_time"), Minus(Global.latest_timestamp(), App.globalGet(last_claim_key))),
        App.globalPut(Bytes("temp_claimable"), Mul(App.globalGet(Bytes("temp_time")), App.globalGet(rate_key))),
        Approve()
    ])
    
    # Worker claims tokens
    claim_tokens = Seq([
        Assert(Txn.sender() == App.globalGet(worker_key)),
        App.globalPut(Bytes("time_elapsed"), Minus(Global.latest_timestamp(), App.globalGet(last_claim_key))),
        App.globalPut(Bytes("claimable"), Mul(App.globalGet(Bytes("time_elapsed")), App.globalGet(rate_key))),
        Assert(App.globalGet(Bytes("claimable")) > Int(0)),
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.receiver: App.globalGet(worker_key),
            TxnField.amount: App.globalGet(Bytes("claimable")),
            TxnField.fee: Int(0)
        }),
        InnerTxnBuilder.Submit(),
        App.globalPut(last_claim_key, Global.latest_timestamp()),
        App.globalPut(total_claimed_key, Add(App.globalGet(total_claimed_key), App.globalGet(Bytes("claimable")))),
        Approve()
    ])
    
    # Fund contract
    fund_contract = Seq([
        Assert(Txn.sender() == App.globalGet(employer_key)),
        Approve()
    ])
    
    # Router
    program = Cond(
        [Txn.application_id() == Int(0), on_create],
        [Txn.application_args[0] == Bytes("get_claimable"), get_claimable],
        [Txn.application_args[0] == Bytes("claim"), claim_tokens],
        [Txn.application_args[0] == Bytes("fund"), fund_contract],
    )
    
    return program

def clear_program():
    return Approve()

if __name__ == "__main__":
    with open("streamfi_approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=8)
        f.write(compiled)
    
    with open("streamfi_clear.teal", "w") as f:
        compiled = compileTeal(clear_program(), mode=Mode.Application, version=8)
        f.write(compiled)
    
    print("✅ Contracts compiled to TEAL!")
