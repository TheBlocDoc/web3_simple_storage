from solcx import compile_standard, install_solc
import json
from web3.main import Web3
import os
from dotenv import load_dotenv

load_dotenv()

install_solc("0.6.0")

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# Compile Our Solidity

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

    # before deploying the contract, we'll need to get the bytecode

    bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
        "bytecode"
    ]["object"]

    # Next, you'll need to get the abi
    abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

    # for connecting to ganache
    w3 = Web3(
        Web3.HTTPProvider(
            "https://mainnet.infura.io/v3/69243604536b4cc5aad1cf9390c8237f"
        )
    )
    chain_id = 4
    my_address = "0x1295B0Cd85eBC253B0f626f72737bc2B2e20Ea48"
    private_key = os.getenv("PRIVATE_KEY")

    # Create the contract in python
    SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
    # Get the latest transaction
    nonce = w3.eth.getTransactionCount(my_address)
    print(nonce)
    # 1. Build a transaction
    # 2. Sign a transaction
    # 3. Send a transaction
    transaction = SimpleStorage.constructor().buildTransaction(
        {
            "chainId": chain_id,
            "gasPrice": w3.eth.gas_price,
            "from": my_address,
            "nonce": nonce,
        }
    )
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    # Send this signed transaction
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    # When working with the contract:
    # We will need the contract address
    # We will also need the contract abi
    simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
    # When making transactions on the Blockchain there are two ways we can interact with them.
    # We can do either a Call -> Simulate making the call and getting a return value, nothing on the Blockchain changes.
    # Or we can do a Transact -> Actually make a state change. This is when we build a transaction and send a transaction.
    print(simple_storage.functions.retrieve().call())
    print(simple_storage.functions.store(15).call())
