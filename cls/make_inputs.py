"""Build classification inputs cls/in_K.jsonl from data4.json + crawl outputs."""
import json, glob, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = json.load(open(f'{R}/data4.json'))['rows']
crawl = {}
for f in sorted(glob.glob(f'{R}/crawl/out_*.jsonl')):
    for l in open(f):
        if l.strip():
            d = json.loads(l); crawl[d['i']] = d
missing = [i for i in range(len(rows)) if i not in crawl]
print('crawl coverage', len(crawl), 'missing', missing[:20])
K = 4
outs = [open(f'{R}/cls/in_{k}.jsonl', 'w') for k in range(K)]
for i, r in enumerate(rows):
    c = crawl.get(i, {})
    d = dict(i=i, curso=r[0], autor=r[1], pacote=r[3], tema=' / '.join(x for x in (r[8], r[9]) if x),
             resumo=r[7], topicos=r[10], competencias=r[11])
    for k in ('n1', 'n2', 'folders1', 'types', 'created_min', 'years_in_names'):
        d[k] = c.get(k)
    d['names'] = [n[:60] for n in (c.get('names') or [])[:25]]
    d['prof'] = c.get('prof', 2)
    outs[i % K].write(json.dumps(d, ensure_ascii=False) + '\n')
