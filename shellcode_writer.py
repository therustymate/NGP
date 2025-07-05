test_shellcode = b""

with open("shell.bin", "wb") as fp:
    fp.write(test_shellcode)
fp.close()