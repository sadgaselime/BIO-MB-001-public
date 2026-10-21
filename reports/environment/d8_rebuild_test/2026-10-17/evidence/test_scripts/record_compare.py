"""Compare per-file (path, sha256) rows of each dist-info RECORD between two site-packages dirs, read-only."""
import csv, glob, os, sys, hashlib, json
a_sp, b_sp, out = sys.argv[1:4]
def recs(sp):
    r = {}
    for d in glob.glob(os.path.join(sp, '*.dist-info')):
        meta = open(os.path.join(d, 'METADATA'), encoding='utf-8').read().split('\n')
        name = next(l.split(':', 1)[1].strip() for l in meta if l.startswith('Name:'))
        rows = list(csv.reader(open(os.path.join(d, 'RECORD'), encoding='utf-8')))
        r[name.lower()] = (d, rows)
    return r
A, B = recs(a_sp), recs(b_sp)
EXCL_SUFFIX = ('.pyc',)
EXCL_NAMES = {'INSTALLER', 'REQUESTED', 'direct_url.json', 'RECORD'}
res = {}
for n in sorted(set(A) | set(B)):
    if n not in A or n not in B:
        res[n] = {'status': 'only_in_' + ('original' if n in A else 'rebuilt')}; continue
    def keep(rows):
        return {(p, h) for p, h, *_ in rows if h and not p.endswith(EXCL_SUFFIX) and os.path.basename(p) not in EXCL_NAMES and not p.startswith('../../../bin/')}
    ka, kb = keep(A[n][1]), keep(B[n][1])
    # also re-hash the actual files on disk in the rebuilt env against its own RECORD
    bad = 0
    for p, h in kb:
        alg, val = h.split('=', 1)
        import base64
        dig = base64.urlsafe_b64encode(hashlib.new(alg, open(os.path.join(b_sp, p), 'rb').read()).digest()).rstrip(b'=').decode()
        bad += dig != val
    res[n] = {'hashed_files_compared': len(ka), 'identical': ka == kb, 'only_original': len(ka - kb), 'only_rebuilt': len(kb - ka), 'rebuilt_files_failing_own_RECORD': bad}
json.dump(res, open(out, 'w'), indent=1)
for n, v in res.items(): print(n, v)
