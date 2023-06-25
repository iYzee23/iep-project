from web3 import Account
import json

with open("./tests/keys.json", "w") as file:
    json.dump(
        Account.encrypt(
            private_key="0x1e69df1911821a62d4a1e65fdcddbf5bc78342b46979277f861c11656c3cc5a2",
            password="iep_project"
        ),
        file
    )
