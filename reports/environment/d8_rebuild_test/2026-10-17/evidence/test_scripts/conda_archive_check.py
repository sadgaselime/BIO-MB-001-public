import json,glob,hashlib,os,sys
pk,meta,out=sys.argv[1:4]
rec={}
for f in glob.glob(os.path.join(meta,'*.json')):
    d=json.load(open(f)); 
    if d.get('fn'): rec[d['fn']]=d
rows=[];ok=mis=nosha=0
for fn in sorted(rec):
    p=os.path.join(pk,fn)
    if not os.path.exists(p): rows.append((fn,'MISSING_ARCHIVE','','','')); mis+=1; continue
    b=open(p,'rb').read(); s=hashlib.sha256(b).hexdigest(); m=hashlib.md5(b).hexdigest()
    exp=rec[fn].get('sha256','')
    st='sha256_match' if exp==s else ('no_recorded_sha256' if not exp else 'SHA256_MISMATCH')
    if st=='sha256_match': ok+=1
    elif st=='no_recorded_sha256': nosha+=1
    else: mis+=1
    rows.append((fn,st,s,m,str(m==rec[fn].get('md5'))))
with open(out,'w') as f:
    f.write('archive\tstatus_vs_base_conda_meta_sha256\tsha256\tmd5\tmd5_matches_base_record\n')
    for r in rows: f.write('\t'.join(r)+'\n')
print('archives',len(rows),'sha256_match',ok,'no_recorded_sha256',nosha,'mismatch_or_missing',mis)
