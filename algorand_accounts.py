from algosdk import account, mnemonic
from algosdk.v2client import algod
import json

class AlgorandAccountManager:
    def __init__(self):
        self.algod_address = "https://testnet-api.algonode.cloud"
        self.algod_token = ""
        self.algod_client = algod.AlgodClient(self.algod_token, self.algod_address)
    
    def create_account(self):
        """Create a new Algorand account"""
        private_key, address = account.generate_account()
        passphrase = mnemonic.from_private_key(private_key)
        
        return {
            'address': address,
            'private_key': private_key,
            'mnemonic': passphrase
        }
    
    def get_account_info(self, address):
        """Get account information"""
        try:
            account_info = self.algod_client.account_info(address)
            return account_info
        except Exception as e:
            print(f"Error getting account info: {e}")
            return None
    
    def get_balance(self, address):
        """Get account balance in ALGOs"""
        account_info = self.get_account_info(address)
        if account_info:
            return account_info['amount'] / 1_000_000  # Convert microALGOs to ALGOs
        return 0

if __name__ == "__main__":
    # Test account creation
    manager = AlgorandAccountManager()
    
    # Create test account
    account_data = manager.create_account()
    print("New Account Created:")
    print(f"Address: {account_data['address']}")
    print(f"Mnemonic: {account_data['mnemonic']}")
    
    # Check balance (should be 0)
    balance = manager.get_balance(account_data['address'])
    print(f"Balance: {balance} ALGO")
    
    print("\nTo fund this account, visit:")
    print("https://bank.testnet.algorand.network/")
    print(f"And send TestNet ALGO to: {account_data['address']}")