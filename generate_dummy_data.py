import os
import random
import string

ROOT = os.path.dirname(os.path.abspath(__file__))
BENIGN_DIR = os.path.join(ROOT, "dataset", "benign")
MALICIOUS_DIR = os.path.join(ROOT, "dataset", "malicious")

os.makedirs(BENIGN_DIR, exist_ok=True)
os.makedirs(MALICIOUS_DIR, exist_ok=True)

def make_text_file(path, lines=10):
    with open(path, "w", encoding="utf-8") as f:
        for i in range(lines):
            f.write(f"This is a benign test file line {i+1}.\n")

def make_image_like_file(path, size_kb=10):
    # small pseudo-image (not a valid real image) but binary content
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")  # PNG header bytes
        f.write(os.urandom(size_kb * 1024 - 8))

def make_low_entropy_binary(path, size_kb=10):
    # repeated pattern => low entropy
    with open(path, "wb") as f:
        pattern = b"ABCD" * 256
        written = 0
        while written < size_kb * 1024:
            f.write(pattern)
            written += len(pattern)

def make_high_entropy_binary(path, size_kb=20):
    # random bytes => high entropy (simulate packed/obfuscated)
    with open(path, "wb") as f:
        f.write(os.urandom(size_kb * 1024))

def random_name(ext):
    name = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{name}{ext}"

# Create benign files
print("Creating benign files...")
make_text_file(os.path.join(BENIGN_DIR, "benign_readme.txt"))
make_text_file(os.path.join(BENIGN_DIR, "notes.txt"), lines=25)
make_image_like_file(os.path.join(BENIGN_DIR, "sample_image.png"), size_kb=12)
make_low_entropy_binary(os.path.join(BENIGN_DIR, "lib_low_entropy.bin"), size_kb=16)

# Create a few small benign .exe-named files but with low entropy (so model learns extension alone isn't everything)
with open(os.path.join(BENIGN_DIR, "harmless_tool.exe"), "wb") as f:
    f.write(b"NOTREALEXE" * 100)  # clearly not a real exe; just for testing

# Create malicious-like files
print("Creating malicious (dummy) files...")
for i in range(6):
    fname = random_name(".exe")
    make_high_entropy_binary(os.path.join(MALICIOUS_DIR, fname), size_kb=30)

# Add some other suspicious extensions
for ext in [".dll", ".scr", ".bat", ".js"]:
    fname = f"suspicious_{ext.strip('.')}{random.randint(1,999)}{ext}"
    make_high_entropy_binary(os.path.join(MALICIOUS_DIR, fname), size_kb=16)

# Also add a few tiny high-entropy text files to simulate obfuscated scripts
for i in range(3):
    with open(os.path.join(MALICIOUS_DIR, f"mal_script_{i+1}.js"), "wb") as f:
        f.write(os.urandom(2048))  # 2 KB random bytes

print("Done. Created files in:")
print("  Benign:", BENIGN_DIR)
print("  Malicious:", MALICIOUS_DIR)
