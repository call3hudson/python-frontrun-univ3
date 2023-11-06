from web3 import Web3, AsyncWeb3

w3 = Web3(Web3.HTTPProvider('https://eth-pokt.nodies.app'))
print(w3.is_connected())
print(w3.eth.gas_price)
print(w3.eth.block_number)