import json, sys, os, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import igsig
now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
for d in sys.argv[1:]:
    p = os.path.join(d, 'resource.json')
    r = json.load(open(p))
    r['attributes']['lastModification'] = {'actor': 'admin', 'timestamp': now}
    r['attributes']['lastModificationSignature'] = ''
    json.dump(r, open(p, 'w'), indent=2)
    r['attributes']['lastModificationSignature'] = igsig.digest(d, 1, lambda k: k != 'lastModificationSignature')
    json.dump(r, open(p, 'w'), indent=2)
    print(r['attributes']['lastModificationSignature'], d.split('/views/')[1])
