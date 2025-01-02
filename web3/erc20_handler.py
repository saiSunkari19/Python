from web3 import Web3
from eth_account.signers.local import LocalAccount
from typing import Dict, Any

class ERC20Handler:
    def __init__(self, w3: Web3, token_address: str, abi: Dict[str, Any], account: LocalAccount):
        self.w3 = w3
        self.token_address = token_address
        self.account = account
        self.contract = w3.eth.contract(address=token_address, abi=abi)

    def allowance(self, owner: str, spender: str) -> int:
        """
        Get the current allowance for a spender
        
        Args:
            owner: Address of the token owner
            spender: Address of the spender
            
        Returns:
            int: Current allowance in wei
        """
        return self.contract.functions.allowance(owner, spender).call()

    def approve(self, spender: str, amount: int) -> bool:
        """
        Approve tokens for spending
        
        Args:
            spender: Address to approve for spending
            amount: Amount to approve in wei
            
        Returns:
            bool: True if successful
        """
        try:
            approve_tx = self.contract.functions.approve(
                spender,
                amount
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price
            })

            signed_txn = self.account.sign_transaction(approve_tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return bool(tx_receipt['status'])
        except Exception as e:
            print(f"Approval failed: {str(e)}")
            return False

    def balance_of(self, address: str) -> int:
        """
        Get token balance of an address
        
        Args:
            address: Address to check balance for
            
        Returns:
            int: Token balance in wei
        """
        return self.contract.functions.balanceOf(address).call()

    def token_name(self) -> str:
        """Get token name"""
        return self.contract.functions.name().call()

    def token_symbol(self) -> str:
        """Get token symbol"""
        return self.contract.functions.symbol().call()

    def token_decimals(self) -> int:
        """Get token decimals"""
        return self.contract.functions.decimals().call()

    def total_supply(self) -> int:
        """Get total supply"""
        return self.contract.functions.totalSupply().call()