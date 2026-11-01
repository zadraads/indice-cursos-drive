"""Aggregate raw crawl logs (crawl/raw_*.tsv) into per-course JSON lines per crawl/brief.txt.
raw TSV columns: id, parentId, mimeType, createdTime, modifiedTime, title
"""
import json, glob, re, sys, os
base = os.path.dirname(os.path.abspath(__file__))
FOLDER = 'application/vnd.google-apps.folder'
items = {}
for f in sorted(glob.glob(os.path.join(base, 'raw_*.tsv'))):
    for line in open(f, encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        if len(p) < 6 or not p[0].strip():
            continue
        fid, par, mime, cr, mo = [x.strip() for x in p[:5]]
        title = '\t'.join(p[5:]).strip()
        items[fid] = dict(id=fid, par=par, mime=mime, cr=cr, mo=mo, t=title)
kids = {}
for it in items.values():
    kids.setdefault(it['par'], []).append(it)

def kind(it):
    m, t = it['mime'].lower(), it['t'].lower()
    ext = t.rsplit('.', 1)[-1] if '.' in t else ''
    if m == FOLDER: return 'pasta'
    if m.startswith('video/') or ext in ('mp4', 'mkv', 'mov', 'ts', 'avi', 'webm', 'm4v'): return 'video'
    if 'pdf' in m or ext == 'pdf': return 'pdf'
    if 'spreadsheet' in m or 'excel' in m or ext in ('xlsx', 'xls', 'csv'): return 'planilha'
    if 'document' in m or 'msword' in m or ext in ('docx', 'doc'): return 'doc'
    if m.startswith('text/') or ext in ('txt', 'md'): return 'texto'
    if m.startswith('image/'): return 'imagem'
    if m.startswith('audio/') or ext in ('mp3', 'm4a', 'wav', 'ogg'): return 'audio'
    if 'zip' in m or 'rar' in m or ext in ('zip', 'rar', '7z'): return 'zip'
    return 'outro'

out = []
todo = [json.loads(l) for f in sorted(glob.glob(os.path.join(base, 'todo_*.jsonl'))) for l in open(f) if l.strip()]
seen_i = set()
for c in todo:
    if c['i'] in seen_i: continue
    seen_i.add(c['i'])
    l1 = sorted(kids.get(c['fid'], []), key=lambda x: x['t'])
    f1 = [x for x in l1 if x['mime'] == FOLDER]
    l2 = [y for x in f1 for y in sorted(kids.get(x['id'], []), key=lambda z: z['t'])]
    allit = l1 + l2
    types = dict.fromkeys(['video', 'pdf', 'planilha', 'doc', 'texto', 'imagem', 'audio', 'zip', 'pasta', 'outro'], 0)
    for x in allit: types[kind(x)] += 1
    names = [x['t'] for x in l1] + [x['t'] for x in l2 if x['mime'] == FOLDER] + [x['t'] for x in l2 if x['mime'] != FOLDER]
    names = [n[:80] for n in names[:60]]
    crs = [x['cr'][:10] for x in allit if x['cr']]
    mos = [x['mo'][:10] for x in allit if x['mo']]
    years = sorted({int(y) for x in allit for y in re.findall(r'(?<!\d)(20[1-2]\d)(?!\d)', x['t']) if 2010 <= int(y) <= 2026})
    out.append(dict(i=c['i'], n1=len(l1), n2=len(l2), folders1=len(f1), types=types if allit else {}, names=names,
                    created_min=min(crs) if crs else '', created_max=max(crs) if crs else '',
                    modified_max=max(mos) if mos else '', years_in_names=years))
with open(os.path.join(base, 'out_new.jsonl'), 'w', encoding='utf-8') as f:
    for d in out: f.write(json.dumps(d, ensure_ascii=False) + '\n')
print('courses', len(out), 'empty', sum(1 for d in out if d['n1'] == 0), 'raw items', len(items))
