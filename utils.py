# Hash function with mask for first 32 bits
def hash_fn(a):
    return hash(a) & 0xffffffff