from solcx import compile_standard, install_solc
import json
from web3 import Web3

import os
from dotenv import load_dotenv
load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    # print(simple_storage_file)


# Complied Our Solidity

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        }
    },
    solc_version="0.8.0"
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# for connecting to ganache
w3 = Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/a5611199d0164a57a28bb3d764b2f6a7"))
chain_id = 5
my_address = "0x6968D6b222639f98994b83080bB45efa8995cea9"
private_key = os.getenv("PRIVATE_KEY")

#  Create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the lastest transaction count
nonce = w3.eth.getTransactionCount(my_address)

# # 1. Build a transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {"gasPrice": w3.eth.gas_price, "chainId": chain_id, "from": my_address, "nonce": nonce})

# 2. Sign a transaction
signed_txn = w3.eth.account.sign_transaction(
    transaction, private_key=private_key)


# 3. Send a transaction
txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
print(txn_hash)


# Working with contracts, You need the:
# Contract ABI
# Contract ADDRESS
simple_storage = w3.eth.contract(address=txn_receipt.contractAddress, abi=abi)
# Call -> Simulate  making the call and getting a return value
# Transact -> Actually make a state change

# Initial value of favorite number
print(simple_storage.functions.retrieve().call())
print("updating contract")
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {"gasPrice": w3.eth.gas_price, "chainId": chain_id, "from": my_address, "nonce": nonce + 1}
)

signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("updated contract")
print(simple_storage.functions.retrieve().call())
