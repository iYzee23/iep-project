from web3 import Account
import json

with open("./tests/keys.json", "w") as file:
    json.dump(
        Account.encrypt(
            private_key="0x4657de4f81339a28d3905ef88ae22bc96f726b3c3189e8584be6c1c0238083e6",
            password="iep_project"
        ),
        file
    )
