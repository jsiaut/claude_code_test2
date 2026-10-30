"""Vérification minisign (Ed25519, prehash BLAKE2b-512 pour l'algorithme « ED »), clé publique de ziglang.org.
Usage : python3 -I minisign_verify.py FICHIER... (signature attendue dans FICHIER.minisig)"""
import base64, hashlib, sys
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

PUB = "RWSGOq2NVecA2UPNdBUZykf1CCb147pkmdtYxgb3Ti+JO/wCYvhbAb/U"


def verify(path, sigpath):
    pk = base64.b64decode(PUB)
    assert pk[:2] == b"Ed"
    keyid, key = pk[2:10], Ed25519PublicKey.from_public_bytes(pk[10:42])
    lines = open(sigpath).read().splitlines()
    sig = base64.b64decode(lines[1])
    alg, sid, s = sig[:2], sig[2:10], sig[10:74]
    assert sid == keyid, "clé différente"
    data = open(path, "rb").read()
    msg = hashlib.blake2b(data, digest_size=64).digest() if alg == b"ED" else data
    key.verify(s, msg)  # lève une exception si invalide
    tc = lines[2][len("trusted comment: "):]
    key.verify(base64.b64decode(lines[3]), s + tc.encode())
    return alg.decode(), tc


for f in sys.argv[1:]:
    print(f, *verify(f, f + ".minisig"))
