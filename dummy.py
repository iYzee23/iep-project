from web3 import Account
import json

with open("./tests/keys.json", "w") as file:
    json.dump(
        Account.encrypt(
            private_key="0x219638b363ed5c438bb04e32f5b540eb8acf20c39b72925bf66384c692f5e51f",
            password="iep_project"
        ),
        file
    )
