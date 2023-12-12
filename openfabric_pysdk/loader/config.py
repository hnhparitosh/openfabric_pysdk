import os
from openfabric_pysdk.store import KeyValueDB

# State configuration
state_config: KeyValueDB = KeyValueDB(f"state", path=f"{os.getcwd()}/config", autodump=True)

# Manifest configuration
manifest: KeyValueDB = KeyValueDB(f"manifest", path=f"{os.getcwd()}/config", autodump=True)

# Execution configuration
execution: KeyValueDB = KeyValueDB(f"execution", path=f"{os.getcwd()}/config", autodump=True)
