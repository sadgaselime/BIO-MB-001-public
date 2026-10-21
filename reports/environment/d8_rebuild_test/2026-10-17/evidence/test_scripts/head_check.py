import sys, urllib.request, concurrent.futures as cf
urls=[l.split('#')[0].strip() for l in open(sys.argv[1]) if l.startswith('https')]
def h(u):
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,method='HEAD'),timeout=60)
        return u,r.status,r.headers.get('Content-Length','')
    except Exception as e:
        return u,getattr(e,'code','ERR:'+type(e).__name__),''
with cf.ThreadPoolExecutor(16) as ex: res=list(ex.map(h,urls))
with open(sys.argv[2],'w') as f:
    f.write('status\tcontent_length\turl\n')
    for u,s,c in res: f.write(f'{s}\t{c}\t{u}\n')
from collections import Counter; print(Counter(s for _,s,_ in res)); print('total_bytes',sum(int(c) for _,_,c in res if c))
