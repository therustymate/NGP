from argparse import ArgumentParser
import hashlib
import os
import sys
import mmap
import json

NGP_VER = "3.0"
EXTENSION_DICT = {
    "EXE": "Executable",
    "DLL": "Dynamic Link Library",
    "SYS": "System Driver",
    "COM": "Legacy DOS Executable",
    "BIN": "Raw Binary File",
}

# -----------------------------------------------------------------

TARGET_SHELLCODE_PATH : str = ""
TARGET_SCAN_PATH : str      = ""
TARGET_EXTENSIONS : str     = ""
SCAN_FILES = []

# -----------------------------------------------------------------

def get_size_unit(size_bytes):
    for unit in ['bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
        if size_bytes < 1024:
            return f"{size_bytes:,.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:,.2f} EiB"

def read_shellcode(path : str):
    if not os.path.exists(path):
        print(f"[!] The specified shellcode binary '{path}' does not exist.")
        sys.exit(1)
    
    FILE_HANDLER = open(file=path, mode="rb")
    shellcode = FILE_HANDLER.read()
    FILE_HANDLER.close()

    return shellcode

def get_extensions(option_string : str):
    extensions = []

    for extension in option_string.split(","):
        extensions.append(extension)

    return extensions

def check_scanpath(path : str):
    if not os.path.exists(path):
        print(f"[!] The specified scan target path '{TARGET_SCAN_PATH}' does not exist.")
        sys.exit(1)

    return path

def parse_chunk(file : str, shellcode_bytes : bytes):
    with open(file, "rb") as FILE_HANDLER:
        with mmap.mmap(FILE_HANDLER.fileno(), 0, access=mmap.ACCESS_READ) as MMAP_HANDLER:
            max_len = 0
            max_offset = -1
            max_chunk = b""

            for length in range(1, len(shellcode_bytes) + 1):
                chunk = shellcode_bytes[:length]
                position = MMAP_HANDLER.find(chunk)
                if position == -1:
                    break
                else:
                    max_len = length
                    max_offset = position
                    max_chunk = chunk

            if max_len > 0:
                return {
                    "offset": max_offset,
                    "length": max_len,
                    "chunk": max_chunk
                }

def map_shellcode(shellcode_bytes: bytes, scan_files: list):
    idx = 0
    chunks = []

    while idx < len(shellcode_bytes):
        found = None

        for file in scan_files:
            metadata = parse_chunk(file, shellcode_bytes[idx:])
            if metadata and metadata["length"] > 1:
                found = metadata
                found["file"] = file
                break

        if found:
            chunks.append(found)
            idx += found["length"]
        else:
            print(f"[-] Unmapped bytes at index {idx}: {shellcode_bytes[idx:].hex()}")
            break

    return chunks

def start():
    print()

    shellcode_bytes = read_shellcode(TARGET_SHELLCODE_PATH)
    print(f"[+] Shellcode Binary: [{TARGET_SHELLCODE_PATH}]")

    shellcode_string = f"{shellcode_bytes.hex()[:30]}...{shellcode_bytes.hex()[-5:]}"
    if len(shellcode_bytes) <= 18: shellcode_string = shellcode_bytes.hex()
    print(f"[+] Shellcode Bytes: {shellcode_string} ({len(shellcode_bytes)} bytes)")

    print("[+] Shellcode Hashes:")
    width = 10

    print(f"\t* {'MD5:':<{width}}\t{hashlib.md5(shellcode_bytes).hexdigest()}")
    print(f"\t* {'SHA1:':<{width}}\t{hashlib.sha1(shellcode_bytes).hexdigest()}")
    print(f"\t* {'SHA256:':<{width}}\t{hashlib.sha256(shellcode_bytes).hexdigest()}")

    print()

    # -----------------------------------------------------------------

    extensions = get_extensions(TARGET_EXTENSIONS)
    print(f"[+] Specified Extensions:")
    for extension in extensions:
        extension = str(extension).upper().split(".")[1]
        print(f"\t* {extension} ({EXTENSION_DICT.get(extension, 'Custom')})")

    print()

    scan_path = check_scanpath(TARGET_SCAN_PATH)

    # -----------------------------------------------------------------

    print(f"[+] Detecting Files For Scanning:")
    file_cnt = 0
    total_size = 0

    ext_width = 8
    count_width = 15
    size_width = 20

    for extension in extensions:
        ext = str(extension).upper().split(".")[1]
        count = 0
        size_sum = 0
        for root, dirs, files in os.walk(scan_path):
            for file in files:
                if file.upper().endswith(ext):
                    count += 1
                    file_cnt += 1
                    try:
                        filepath = os.path.join(root, file)
                        size_sum += os.path.getsize(filepath)
                        total_size += os.path.getsize(filepath)
                        SCAN_FILES.append(filepath)
                    except OSError:
                        pass
        print(f"\t* {ext:<{ext_width}} {count:>{count_width},} files {size_sum:>{size_width},} bytes ({get_size_unit(size_sum)})")
    
    print(f"\t* {'Total:':<{ext_width}} {file_cnt:>{count_width},} files {total_size:>{size_width},} bytes ({get_size_unit(total_size)})\n")

    print()

    # -----------------------------------------------------------------

    print(f"[+] Checking File Access Permissions:")

    failed = []

    for file in SCAN_FILES:
        try:
            fp = open(file, "rb")
            fp.close()
        except:
            failed.append(file)

    for file in failed:
        SCAN_FILES.remove(file)

    print(f"\t* Accessible: {len(SCAN_FILES):>12,} files")
    print(f"\t* Inaccessible: {len(failed):>10,} files")

    print()

    # -----------------------------------------------------------------

    mapped_chunks = map_shellcode(shellcode_bytes, SCAN_FILES)

    print("\n=== Final Mapped Chunks ===")
    print(f"{'File Path':<80} {'Offset':>8} {'Length':>8}  Chunk (hex)")
    print("-" * 120)

    found_shellcode = ""

    for chunk in mapped_chunks:
        path = chunk["file"]
        offset = chunk["offset"]
        length = chunk["length"]
        hex_chunk = chunk["chunk"].hex()
        print(f"{path:<80} {offset:>8} {length:>8}  {hex_chunk}")
        found_shellcode += hex_chunk

    print()

    found_shellcode_bytes = bytes.fromhex(found_shellcode)

    print("[+] Found Shellcode Hashes:")
    label_width= 10
    hash_width = 70

    original_md5    = hashlib.md5(shellcode_bytes).hexdigest()
    original_sha1   = hashlib.sha1(shellcode_bytes).hexdigest()
    original_sha256 = hashlib.sha256(shellcode_bytes).hexdigest()

    found_md5    = hashlib.md5(found_shellcode_bytes).hexdigest()
    found_sha1   = hashlib.sha1(found_shellcode_bytes).hexdigest()
    found_sha256 = hashlib.sha256(found_shellcode_bytes).hexdigest()

    print(f"\t* {'MD5:':<{label_width}} {found_md5:<{hash_width}} {'[MATCH]' if found_md5 == original_md5 else ''}")
    print(f"\t* {'SHA1:':<{label_width}} {found_sha1:<{hash_width}} {'[MATCH]' if found_sha1 == original_sha1 else ''}")
    print(f"\t* {'SHA256:':<{label_width}} {found_sha256:<{hash_width}} {'[MATCH]' if found_sha256 == original_sha256 else ''}")

    print()

    print("[+] JSON List:")

    print("[")
    for i, chunk in enumerate(mapped_chunks):
        item = {
            "file": chunk["file"].replace("\\", "/"),
            "offset": chunk["offset"],
            "length": chunk["length"],
            "chunk": chunk["chunk"].hex()
        }
        comma = "," if i < len(mapped_chunks) - 1 else ""
        print(f"  {json.dumps(item)}{comma}")
    print("]")

def main():
    global TARGET_SHELLCODE_PATH
    global TARGET_SCAN_PATH
    global TARGET_EXTENSIONS

    parser = ArgumentParser(
        prog="NGP Compiler",
        description=f"Native Gadget Programming Compiler"
                    " - Shell Chunk Loader for the NGP Technology",
        epilog="Usage: npg.py -t shellcode.bin -p C:\\Windows\\System32 --extensions .dll,.exe"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s v{NGP_VER}"
    )

    parser.add_argument(
        "-t", "--target",
        help="target raw shellcode binary",
        required=True,
        type=str
    )
    parser.add_argument(
        "-p", "--path",
        help="path to scan for matching gadget chunks (e.g. System32)",
        required=True,
        type=str
    )
    parser.add_argument(
        "--extensions",
        help="specify file extensions to scan (comma separated, default: .dll,.exe,.sys,.com,.bin)",
        type=str,
        default=".dll,.exe,.sys,.com,.bin"
    )

    args = parser.parse_args()

    TARGET_SHELLCODE_PATH   = os.path.join(os.getcwd(), str(args.target))
    TARGET_SCAN_PATH        = str(args.path)
    TARGET_EXTENSIONS       = str(args.extensions)

    start()

if __name__ == "__main__":
    main()