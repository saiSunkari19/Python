from web3 import Web3
import os, dotenv, json
from eth_account.signers.local import LocalAccount
from typing import List, Tuple
from erc20_handler import ERC20Handler

class BondingCurveInteraction:
    def __init__(self, w3: Web3, account: LocalAccount, bonding_curve_address: str, 
                 bonding_curve_abi: dict, erc20_abi: dict, mytoken_address: str):
        self.w3 = w3
        self.account = account
        self.bonding_curve_address = bonding_curve_address
        self.contract = w3.eth.contract(address=bonding_curve_address, abi=bonding_curve_abi)
        self.mytoken = ERC20Handler(w3, mytoken_address, erc20_abi, account)

    def estimate_gas_with_buffer(self, transaction) -> int:
        """
        Estimate gas for a transaction and add a buffer for safety
        
        Args:
            transaction: The transaction to estimate gas for
            
        Returns:
            int: Estimated gas limit with buffer
        """
        try:
            estimated_gas = self.w3.eth.estimate_gas(transaction)
            # Add 20% buffer for safety
            return int(estimated_gas * 1.2)
        except Exception as e:
            print(f"Gas estimation failed: {str(e)}")
            # If estimation fails, return a high default value
            return 3000000  # High default gas limit

    def get_event_from_receipt(self, tx_receipt: dict, event_name: str):
        """
        Safely extract event data from transaction receipt
        
        Args:
            tx_receipt: Transaction receipt
            event_name: Name of the event to look for
            
        Returns:
            Event data if found, None otherwise
        """
        try:
            events = getattr(self.contract.events, event_name)().process_receipt(tx_receipt)
            return events[0]['args'] if events else None
        except Exception as e:
            print(f"Warning: Could not process {event_name} event: {str(e)}")
            return None

    def launch_token(self, name: str, ticker: str, cores: List[int], description: str, 
                    image: str, urls: List[str], purchase_amount: int) -> Tuple[str, str, int]:
        """
        Launch a new token using the bonding curve contract
        """
        # Get launch fee from contract
        launch_fee = self.contract.functions.fee().call()
        total_amount = launch_fee + purchase_amount
     

        # Check and approve MyT tokens if needed
        current_allowance = self.mytoken.allowance(self.account.address, self.bonding_curve_address)
        if current_allowance < total_amount:
            print(f"Approving {Web3.from_wei(total_amount, 'ether')} MyT...")
            if not self.mytoken.approve(self.bonding_curve_address, total_amount):
                raise Exception("Failed to approve MyT tokens")
            print("Approval successful!")

        # Ensure urls list has exactly 4 items
        if len(urls) != 4:
            raise ValueError("URLs must contain exactly 4 items [twitter, telegram, youtube, website]")

        # Build transaction for gas estimation
        launch_tx = self.contract.functions.launch(
            name, ticker, cores, description, image, urls, total_amount
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gasPrice': self.w3.eth.gas_price
        })

        # Estimate gas with buffer
        estimated_gas = self.estimate_gas_with_buffer(launch_tx)
        print(f"Estimated gas with buffer: {estimated_gas}")

        # Update transaction with estimated gas
        launch_tx['gas'] = estimated_gas

        # Sign and send transaction
        signed_txn = self.account.sign_transaction(launch_tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        print(f"Transaction sent: {tx_hash.hex()}")
        
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Transaction status: {'Success' if tx_receipt['status'] else 'Failed'}")

        # Get event data safely
        event_data = self.get_event_from_receipt(tx_receipt, 'Launched')
        if not event_data:
            print("Warning: Launch transaction succeeded but event data not found")
            return None

        return event_data

    def buy_tokens(self, amount_in: int, token_address: str) -> bool:
        """Buy tokens from the bonding curve"""
        # Check and approve MyT tokens if needed
        current_allowance = self.mytoken.allowance(self.account.address, self.bonding_curve_address)
        if current_allowance < amount_in:
            print(f"Approving {Web3.from_wei(amount_in, 'ether')} MyT...")
            if not self.mytoken.approve(self.bonding_curve_address, amount_in):
                raise Exception("Failed to approve MyT tokens")
            print("Approval successful!")

        tx = self.contract.functions.buy(
            amount_in,
            token_address
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price
        })

        signed_txn = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return bool(tx_receipt['status'])

    def sell_tokens(self, amount_in: int, token_address: str) -> bool:
        """Sell tokens back to the bonding curve"""
        # For selling, we need to approve the bonding curve to spend the token we want to sell
        token_to_sell = ERC20Handler(self.w3, token_address, self.erc20_abi, self.account)
        
        current_allowance = token_to_sell.allowance(self.account.address, self.bonding_curve_address)
        if current_allowance < amount_in:
            print(f"Approving {Web3.from_wei(amount_in, 'ether')} tokens for selling...")
            if not token_to_sell.approve(self.bonding_curve_address, amount_in):
                raise Exception("Failed to approve tokens for selling")
            print("Approval successful!")

        tx = self.contract.functions.sell(
            amount_in,
            token_address
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price
        })

        signed_txn = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return bool(tx_receipt['status'])

# Example usage:
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

    # Initialize the bonding curve interaction
    bonding_curve = BondingCurveInteraction(
        w3=w3,
        account=account,
        bonding_curve_address=bonding_curve_address,
        bonding_curve_abi=bonding_curve_abi,
        erc20_abi=erc20_abi,
        mytoken_address=mytoken_address
    )

    # Example: Launch a new token
    token_info = bonding_curve.launch_token(
        name="MyToken",
        ticker="MTK",
        cores=[1, 2, 3],
        description="My test token description",
        image="https://example.com/image.png",
        urls=["https://twitter.com", "https://t.me", "https://youtube.com", "https://example.com"],
        purchase_amount=Web3.to_wei(5, 'ether')
    )
    print(f"Launched token: {token_info}")