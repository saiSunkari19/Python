from web3 import Web3
import os,dotenv, json
dotenv.load_dotenv()



# Connecting to Sepolia Testnet
w3 = Web3(Web3.HTTPProvider(os.getenv("SEPOLIA_TESTNET_RPC")))
print(f"latest block", w3.eth.get_block_number())

# Get Account from Private Key 
account1 = w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))

# Get Account Balance 
balance = w3.eth.get_balance(account=account1.address)
print(f"Account address : {account1.address} - {balance}")


# Load abi
with open("abis/bonding_curve.json", 'r') as abi_file:
    abi = json.load(abi_file)
    
with open("abis/erc20.json", 'r') as abi_file:
    erc20_abi = json.load(abi_file)

bonding_curve = "0xFc1e1fBDB109791C228205AbC40A35132C2Ec0D7"
mytoken = "0x24b14f14442Cf3eA5Ebb085F2A212074042E416E"


# Contract interactions
bonding_curve_instance = w3.eth.contract(address=bonding_curve, abi= abi)

mint_fee = bonding_curve_instance.functions.fee().call()
mint_fee_readable = Web3.from_wei(mint_fee, 'ether')
print(f"mint fee {mint_fee_readable} MyT")


# Get Contract balance of users
mytoken_instance = w3.eth.contract(address=mytoken, abi=erc20_abi)

user_balance = mytoken_instance.functions.balanceOf(account1.address).call()
user_parsed_balance = Web3.from_wei(user_balance, 'ether')
print(f"User mytoken balance - {user_parsed_balance} MyT")


# Create token 
tx = bonding_curve_instance.functions.launch(
    
).transact({
    from: account1
})




