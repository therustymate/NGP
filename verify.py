import json
import os

json_file_path = input("JSON File: ")

try:
    with open(json_file_path, "r", encoding="utf-8") as f:
        data_list = json.load(f)
except Exception as e:
    print(f"Failed to load JSON file '{json_file_path}': {e}")
    exit(1)

def verify_chunk_exists(item):
    file_path = os.path.normpath(item["file"])
    offset = item["offset"]
    length = item["length"]
    expected_chunk = bytes.fromhex(item["chunk"])

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False

    try:
        with open(file_path, "rb") as f:
            f.seek(offset)
            data = f.read(length)
            if data == expected_chunk:
                return True
            else:
                print(f"Mismatch in file {file_path} at offset {offset}: expected {expected_chunk.hex()}, found {data.hex()}")
                return False
    except Exception as e:
        print(f"Failed to open/read {file_path}: {e}")
        return False

all_match = True
for entry in data_list:
    if not verify_chunk_exists(entry):
        all_match = False

if all_match:
    print("[+] All chunks verified successfully.")
else:
    print("[-] Some chunks did not match or could not be verified.")
