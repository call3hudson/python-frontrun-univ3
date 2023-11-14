import os
from dotenv import load_dotenv
from web3 import Web3
from uniswap_universal_router_decoder import FunctionRecipient, RouterCodec
from utils import *
from constant import *

load_dotenv()

# Account information
private_key = os.getenv('PRIVATE_KEY')
public_key = os.getenv('PUBLIC_KEY')

# Connect to an Ethereum node
w3 = Web3(Web3.WebsocketProvider('wss://ethereum-sepolia.publicnode.com'))
codec = RouterCodec(w3=w3)

def swap_exact_amount_in(swap_path, deadline, amount_in, priority_fee):
    data, signable_message = codec.create_permit2_signable_message(
        swap_path[0],
        amount_in,
        deadline,
        w3.eth.get_transaction_count(public_key),
        router,
        deadline,
        chain_id,
    )
    signed_message = w3.eth.account.sign_message(signable_message, private_key=private_key)
    print(signed_message)
    encoded_data = (
        codec
        .encode
        .chain()
        .permit2_permit(data, signed_message)
        .v3_swap_exact_in(
            FunctionRecipient.SENDER,
            amount_in,
            0,
            swap_path,
        )
        .build(deadline)
    )
    transaction = {
        'from': public_key,
        'to': router,
        'value': 0,
        'nonce': w3.eth.get_transaction_count(public_key),
        'gas': 200000,
        'maxPriorityFeePerGas': priority_fee,
        'data': encoded_data
    }
    signed = w3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    tx = w3.eth.get_transaction(tx_hash)

    assert tx['from'] == public_key
    
def swap_exact_amount_out(swap_path, deadline, amount_in, priority_fee):
    data, signable_message = codec.create_permit2_signable_message(
        swap_path[2],
        amount_in,
        deadline,
        w3.eth.get_transaction_count(public_key) + 1,
        router,
        deadline,
        chain_id,
    )
    signed_message = w3.eth.account.sign_message(signable_message, private_key=private_key)
    print(signed_message)
    encoded_data = (
        codec
        .encode
        .chain()
        .permit2_permit(data, signed_message)
        .v3_swap_exact_out(
            FunctionRecipient.SENDER,
            amount_in,
            0,
            swap_path,
        )
        .build(deadline)
    )
    transaction = {
        'from': public_key,
        'to': router,
        'value': 0,
        'nonce': w3.eth.get_transaction_count(public_key),
        'gas': 200000,
        'maxPriorityFeePerGas': priority_fee,
        'data': encoded_data
    }
    signed = w3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    tx = w3.eth.get_transaction(tx_hash)

    assert tx['from'] == public_key

def sandwich_swap(tx, call, swap_path, deadline):

    print(f"Gas Priority Fee: {tx['maxPriorityFeePerGas']}")

    priority_fee = tx['maxPriorityFeePerGas']
    if (call[0].__str__() == swap_exact_in_code):
        amount_in = call[1]['amountIn'] * frontrun_threshold / 1000
        amount_out_min = call[1]['amountOutMin']
        swap_exact_amount_in(swap_path, deadline, amount_in, priority_fee * frontrun_fee / 1000)
        swap_exact_amount_out(swap_path, deadline, amount_out_min, priority_fee * backrun_fee / 1000)
    if (call[0].__str__() == swap_exact_out_code):
        amount_in_max = call[1]['amountInMax']
        amount_out = call[1]['amountOut'] * frontrun_threshold / 1000
        swap_exact_amount_out(swap_path, deadline, amount_out, priority_fee * frontrun_fee / 1000)
        swap_exact_amount_in(swap_path, deadline, amount_in_max, priority_fee * backrun_fee / 1000)
    return

def parse_pure_tx(pure_tx, swap_input):
    # Manipulate with the second vale of tuple
    assert(swap_input[0].__str__() == exec_code)

    tx_info = swap_input[1]
    tx_calls = tx_info['inputs']
    block_deadline = tx_info['deadline']
    for tx_call in tx_calls:
        if (tx_call[0].__str__() == swap_exact_in_code or tx_call[0].__str__() == swap_exact_out_code):
            fn_name = take_fn_name(tx_call[0].__str__())
            swap_path = codec.decode.v3_path(fn_name, tx_call[1]['path'])
            if validate_token_path(swap_path) == True:
                sandwich_swap(pure_tx, tx_call, swap_path, block_deadline)
                return

def filter_univ3_transaction(transaction_hash):
    try:
        # Retrieve the transaction details
        transaction = w3.eth.get_transaction(transaction_hash)
        
        if transaction == 0:
            return
        if transaction['to'] != router:
            return
        
        print("filtered")
        if transaction['from'] == public_key:
            return

        print("filtered")

        decoded_trx_input = codec.decode.function_input(transaction['input'])

        print("\n-------------------------------------\n")
        print("Transaction Information:\n")
        print(f"Hash: {transaction.hash.hex()}\n")
        print(f"From: {transaction['from']}\n")
        print(f"To: {transaction['to']}\n")
        print(f"Value: {w3.from_wei(transaction['value'], 'ether')} ETH\n")
        print(f"Gas Price: {w3.from_wei(transaction['gasPrice'], 'ether')} ETH\n")
        print(f"Gas Limit: {transaction['gas']}\n")
        print("Transaction Input:")
        print("-------------------------------------\n\n")
        
        parse_pure_tx(transaction, decoded_trx_input)

    except:
        pass

def get_pending_transaction_events():
    # Create a filter for pending transaction events
    filter = w3.eth.filter('pending')

    # Keep the program running and wait for events
    while True:
        hashes = w3.eth.get_filter_changes(filter.filter_id)
        for hash in hashes:
            filter_univ3_transaction(hash)

# Example usage
get_pending_transaction_events()