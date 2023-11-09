from web3 import Web3
from uniswap_universal_router_decoder.router_codec import RouterCodec

# Connect to an Ethereum node
w3 = Web3(Web3.HTTPProvider('https://ethereum-sepolia.publicnode.com'))

codec = RouterCodec(w3)
# text_file = open("Output.txt", "w")

# # Router address
# router = '3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD'

# def get_transaction_info(transaction_hash):
#     try:
#         # Retrieve the transaction details
#         transaction = w3.eth.get_transaction(transaction_hash)
#         if transaction and transaction['to'][-40:] == router:
#             print("Detected\n")
#             text_file.write("\n-------------------------------------\n")
#             text_file.write("Transaction Information:\n")
#             text_file.write(f"Hash: {transaction.hash.hex()}\n")
#             text_file.write(f"From: {transaction['from']}\n")
#             text_file.write(f"To: {transaction['to'][-40:]}\n")
#             text_file.write(f"Value: {w3.from_wei(transaction['value'], 'ether')} ETH\n")
#             text_file.write(f"Gas Price: {w3.from_wei(transaction['gasPrice'], 'ether')} ETH\n")
#             text_file.write(f"Gas Limit: {transaction['gas']}\n")
#             text_file.write("-------------------------------------\n\n")
#     except:
#         pass

# def get_pending_transaction_events():
#     # Create a filter for pending transaction events
#     filter = w3.eth.filter('pending')

#     # Keep the program running and wait for events
#     while True:
#         hashes = w3.eth.get_filter_changes(filter.filter_id)
#         for hash in hashes:
#             get_transaction_info(hash)

# # Example usage
# get_pending_transaction_events()