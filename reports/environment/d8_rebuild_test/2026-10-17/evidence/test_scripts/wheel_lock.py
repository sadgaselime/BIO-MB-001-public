"""Resolve each recorded (name, version, wheel tag) to exactly one PyPI file; download; verify sha256 against PyPI's published digest."""
import json, sys, hashlib, urllib.request, os
checks, wheeldir, out_tsv, out_lock = sys.argv[1:5]
d = json.load(open(checks))
rows, lock = [], []
for p in d['packages']:
    name, ver, tags = p['name'], p['version'], p['wheel_tags']
    if name == 'biomarker-project':
        rows.append((name, ver, '.'.join(tags), 'NOT_LOCKED_local_editable_project', '', '', '')); continue
    meta = json.load(urllib.request.urlopen(f'https://pypi.org/pypi/{name}/{ver}/json', timeout=60))
    want = '.'.join(tags) if len(tags) == 1 else 'py2.py3-none-any'
    want_parts = set(want.split('-')[-1:])
    cands = []
    for f in meta['urls']:
        fn = f['filename']
        if not fn.endswith('.whl'): continue
        tag = '-'.join(fn[:-4].split('-')[-3:])
        # recorded tags come from the installed WHEEL file; build the same set from the filename
        py, abi, plat = tag.split('-')
        fset = {f'{a}-{b}-{c}' for a in py.split('.') for b in abi.split('.') for c in plat.split('.')}
        if fset == set(tags): cands.append(f)
    if len(cands) != 1:
        rows.append((name, ver, '|'.join(tags), f'FAIL_{len(cands)}_candidates', '', '', '')); continue
    f = cands[0]; pub = f['digests']['sha256']
    dest = os.path.join(wheeldir, f['filename'])
    if not os.path.exists(dest):
        urllib.request.urlretrieve(f['url'], dest)
    got = hashlib.sha256(open(dest, 'rb').read()).hexdigest()
    st = 'sha256_match' if got == pub else 'SHA256_MISMATCH'
    rows.append((name, ver, '|'.join(tags), st, f['filename'], pub, f['url']))
    if st == 'sha256_match': lock.append(f'{name}=={ver} \\\n    --hash=sha256:{pub}')
with open(out_tsv, 'w') as fh:
    fh.write('name\tversion\trecorded_wheel_tags\tstatus\twheel_filename\tpypi_published_sha256\turl\n')
    for r in rows: fh.write('\t'.join(r) + '\n')
with open(out_lock, 'w') as fh:
    fh.write('# BIO-MB-001 D8 rebuild test 2026-10-17: TEST ARTIFACT, not an approved lock.\n')
    fh.write('# Versions from reports/environment/python_lock/v1/requirements.snapshot.txt; one wheel per package selected by the\n')
    fh.write('# installed wheel tag recorded in reports/environment/d8_readonly_checks/v1; hashes = PyPI-published sha256, re-verified on download.\n')
    fh.write('# Local project biomarker-project==0.1.0 is not included (editable install from the source tree).\n')
    fh.write('\n'.join(lock) + '\n')
for r in rows: print(r[0], r[1], r[3], r[4])
