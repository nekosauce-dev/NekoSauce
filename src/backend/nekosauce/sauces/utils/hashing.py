def hash_to_bits(hash):
    bits = ""
    for row in hash.hash:
        bits += "".join(["1" if bit else "0" for bit in row])
    return bits
