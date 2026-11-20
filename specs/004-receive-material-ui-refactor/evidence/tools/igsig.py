"""Recompute Ignition 8.3 resource lastModificationSignature (Resource.calculateContentDigest)."""
import hashlib, json, os, struct, sys

def gson(v):
    return json.dumps(v, separators=(',', ':'), ensure_ascii=False)

def digest(resdir, scopeInt, attrKeysFilter):
    r = json.load(open(os.path.join(resdir, 'resource.json')))
    d = hashlib.sha256()
    d.update(struct.pack('>i', scopeInt))
    if r.get('documentation') is not None:
        d.update(r['documentation'].encode('utf-8'))
    d.update(struct.pack('>i', r.get('version', 1)))
    d.update(b'\x00')  # isUnary false for views
    d.update(b'\x01' if r.get('restricted') else b'\x00')
    d.update(b'\x01' if r.get('overridable') else b'\x00')
    for key in sorted(r['files']):
        d.update(key.encode('utf-8'))
        d.update(hashlib.sha256(open(os.path.join(resdir, key), 'rb').read()).hexdigest().encode())
    attrs = r.get('attributes', {})
    for k in sorted(k for k in attrs if attrKeysFilter(k)):
        d.update(k.encode('utf-8'))
        d.update(gson(attrs[k]).encode('utf-8'))
    return d.hexdigest()

SCOPES = {'G': 7, 'A': 7}

def compute(resdir):
    r = json.load(open(os.path.join(resdir, 'resource.json')))
    return digest(resdir, scopeFor(r['scope']), lambda k: k != 'lastModificationSignature')

def scopeFor(s):
    return SCOPES.get(s, 7)

if __name__ == '__main__':
    for p in sys.argv[1:]:
        print(compute(p), p)
