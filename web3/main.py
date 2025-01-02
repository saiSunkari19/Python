from web3 import Web3
import os, dotenv, json
from eth_account.signers.local import LocalAccount
from typing import List, Tuple
from erc20_handler import ERC20Handler
from bonding_curve import BondingCurveInteraction

if __name__ == "__main__":
    # Initialize Web3 and load environment variables

    dotenv.load_dotenv()
    w3 = Web3(Web3.HTTPProvider(os.getenv("SEPOLIA_TESTNET_RPC")))
    account = w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))

    # Load ABIs
    with open("abis/bonding_curve.json", 'r') as f:
        bonding_curve_abi = json.load(f)
    with open("abis/erc20.json", 'r') as f:
        erc20_abi = json.load(f)
    

    # Contract addresses
    bonding_curve_address = "0xFc1e1fBDB109791C228205AbC40A35132C2Ec0D7"
    mytoken_address = "0x24b14f14442Cf3eA5Ebb085F2A212074042E416E"


    # First, initialize the ERC20Handler (can be used independently)
    mytoken = ERC20Handler(
            w3=w3,
            token_address=mytoken_address,
            abi=erc20_abi,
            account=account
    )

    # Initialize the bonding curve interaction
    bonding_curve = BondingCurveInteraction(
            w3=w3,
            account=account,
            bonding_curve_address=bonding_curve_address,
            bonding_curve_abi=bonding_curve_abi,
            erc20_abi=erc20_abi,
            mytoken_address=mytoken_address
    )
    purchase_amount = Web3.to_wei(1, 'ether')

    # Check allowance
    allowance = mytoken.allowance(account.address, bonding_curve_address)

    # Example: Launch a new token
    # token_info = bonding_curve.launch_token(
    #     name="D",
    #     ticker="AIDEPIN",
    #     cores=[1, 2, 3],
    #     description="My test token description",
    #     image="https://clutch.blob.core.windows.net/clutch-main/20241228_072631_NiAaclc7jQCW22_image.webp",
    #     urls=["https://twitter.com", "https://t.me", "https://youtube.com", "https://example.com"],
    #     purchase_amount=purchase_amount
    # )
    # print(f"Launched token: {token_info}")

    # Buy tokens
    success = bonding_curve.buy_tokens(purchase_amount, mytoken_address)
    print(f"Buy tokens: {success}") 




