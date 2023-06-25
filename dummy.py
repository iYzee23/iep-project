from web3 import Account
import json

with open("./tests/keys.json", "w") as file:
    json.dump(
        Account.encrypt(
            private_key="0x3d48edbfdb6a43c1c59e5221357e6b8c26d465d1cae3e4121cd40851b925763b",
            password="iep_project"
        ),
        file
    )
