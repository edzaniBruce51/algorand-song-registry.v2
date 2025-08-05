import base64
import json
from algosdk.v2client import algod
from algosdk import account, mnemonic
from algosdk.transaction import ApplicationCreateTxn, wait_for_confirmation
from algosdk.transaction import StateSchema, OnComplete

class ContractDeployer:
    def __init__(self):
        self.algod_address = "https://testnet-api.algonode.cloud"
        self.algod_token = ""
        self.algod_client = algod.AlgodClient(self.algod_token, self.algod_address)
    
    def load_account(self, mnemonic_phrase):
        """Load account from mnemonic"""
        # Clean and validate mnemonic
        words = mnemonic_phrase.strip().split()
        print(f"Mnemonic has {len(words)} words")
        
        if len(words) not in [12, 15, 18, 21, 24, 25]:
            raise ValueError(f"Invalid mnemonic length: {len(words)} words")
        
        try:
            private_key = mnemonic.to_private_key(mnemonic_phrase)
            address = account.address_from_private_key(private_key)
            return private_key, address
        except Exception as e:
            raise ValueError(f"Invalid mnemonic: {e}")
    
    def compile_program(self, source_code):
        """Compile TEAL source code"""
        compile_response = self.algod_client.compile(source_code)
        return base64.b64decode(compile_response['result'])
    
    def deploy_contract(self, creator_mnemonic):
        """Deploy the song registry contract"""
        # Load creator account
        private_key, creator_address = self.load_account(creator_mnemonic)
        
        # Read compiled TEAL programs
        with open("song_registry_approval.teal", "r") as f:
            approval_program_source = f.read()
        
        with open("song_registry_clear.teal", "r") as f:
            clear_program_source = f.read()
        
        # Compile programs
        approval_program = self.compile_program(approval_program_source)
        clear_program = self.compile_program(clear_program_source)
        
        # Define schema
        global_schema = StateSchema(num_uints=32, num_byte_slices=32)
        local_schema = StateSchema(num_uints=0, num_byte_slices=0)
        
        # Get suggested parameters
        params = self.algod_client.suggested_params()
        
        # Create application transaction
        txn = ApplicationCreateTxn(
            sender=creator_address,
            sp=params,
            on_complete=OnComplete.NoOpOC,
            approval_program=approval_program,
            clear_program=clear_program,
            global_schema=global_schema,
            local_schema=local_schema
        )
        
        # Sign transaction
        signed_txn = txn.sign(private_key)
        
        # Submit transaction
        tx_id = self.algod_client.send_transaction(signed_txn)
        print(f"Transaction ID: {tx_id}")
        
        # Wait for confirmation
        confirmed_txn = wait_for_confirmation(self.algod_client, tx_id, 4)
        
        # Get application ID
        app_id = confirmed_txn["application-index"]
        print(f"Contract deployed successfully!")
        print(f"Application ID: {app_id}")
        
        # Save deployment info
        deployment_info = {
            "app_id": app_id,
            "creator_address": creator_address,
            "tx_id": tx_id
        }
        
        with open("deployment_info.json", "w") as f:
            json.dump(deployment_info, f, indent=2)
        
        return app_id

if __name__ == "__main__":
    deployer = ContractDeployer()
    
    # You'll need to provide your funded account's mnemonic
    print("Enter your funded account mnemonic (25 words):")
    creator_mnemonic = input().strip()
    
    try:
        app_id = deployer.deploy_contract(creator_mnemonic)
        print(f"\n Deployment successful!")
        print(f" Application ID: {app_id}")
        print(f" Details saved to deployment_info.json")
    except Exception as e:
        print(f" Deployment failed: {e}")
