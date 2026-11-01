"""Etapas C e E: junta classificação (cls/out_*.jsonl), marca duplicatas, carrega trilhas
(trilhas.json) e gera data5.json, indice-cursos.html e Indice-Cursos-Drive.xlsx.

Linhas de data5.json = 16 campos de data4.json mais:
16 ano | 17 ano_base | 18 atualidade | 19 ferramentas | 20 alerta | 21 integridade |
22 aulas | 23 volume | 24 materiais | 25 grupo de duplicata (int ou None) |
26 cópia principal (True/False/None) | 27 nº de cópias no grupo |
28 profundidade da varredura (2 = dois níveis, 1 = só o nível 1)
"""
import json, glob, re, unicodedata, os
R = os.path.dirname(os.path.abspath(__file__))
d4 = json.load(open(f'{R}/data4.json'))
rows = d4['rows']

cls = {}
for f in sorted(glob.glob(f'{R}/cls/out_*.jsonl')):
    for l in open(f, encoding='utf-8'):
        l = l.strip()
        if not l:
            continue
        d = json.loads(l)
        cls[d['i']] = d
missing = [i for i in range(len(rows)) if i not in cls]
assert not missing, f'classificação faltando: {missing}'

crawl = {}
for f in sorted(glob.glob(f'{R}/crawl/out_*.jsonl')):
    for l in open(f, encoding='utf-8'):
        if l.strip():
            d = json.loads(l)
            crawl[d['i']] = d

def volume(n):
    return '—' if not n else 'Curto' if n < 15 else 'Médio' if n <= 60 else 'Extenso'

for i, r in enumerate(rows):
    c, w = cls[i], crawl.get(i, {})
    aulas = (w.get('types') or {}).get('video', 0)
    r[16:] = [c.get('ano'), c.get('ano_base', '—'), c.get('atualidade', ''), c.get('ferramentas') or [],
              c.get('alerta') or [], c.get('integridade', 'Indeterminado'), aulas,
              volume(aulas) if w.get('prof', 2) == 2 or aulas > 60 else '—', c.get('materiais') or [], None, None, 1, w.get('prof', 2)]

# Etapa C: duplicatas por curso+autor normalizados (edições de anos diferentes ficam no mesmo grupo)
def nz(s):
    s = unicodedata.normalize('NFD', s or '').encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'^\s*\d+\s*[.\-)]\s*', '', s)
    s = re.sub(r'\b(20\d\d|completo|atualizado|novo)\b', '', s)
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()

groups = {}
for i, r in enumerate(rows):
    groups.setdefault((nz(r[0]), nz(r[1])), []).append(i)
dup_groups = [v for v in groups.values() if len(v) > 1]
for g, members in enumerate(dup_groups, 1):
    best = sorted(members, key=lambda i: (-(rows[i][22] or 0), rows[i][21] != 'Completo', -(rows[i][16] or 0), i))[0]
    for i in members:
        rows[i][25], rows[i][26], rows[i][27] = g, i == best, len(members)

trilhas = json.load(open(f'{R}/trilhas.json', encoding='utf-8')) if os.path.exists(f'{R}/trilhas.json') else []
for t in trilhas:
    for it in t['itens']:
        r = rows[it['i']]
        assert not r[20], f"trilha com alerta: {it['i']}"
        assert r[26] in (None, True), f"trilha com cópia não principal: {it['i']}"

out = {'rows': rows, 'packs': d4['packs'], 'trilhas': trilhas}
json.dump(out, open(f'{R}/data5.json', 'w', encoding='utf-8'), ensure_ascii=False)
head = open(f'{R}/page_head5.html', encoding='utf-8').read()
payload = json.dumps(out, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
open(f'{R}/indice-cursos.html', 'w', encoding='utf-8').write(head.replace('__DATA__', payload))

# Planilha
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
wb = Workbook()
ws = wb.active
ws.title = 'Cursos'
hdr = ['Curso', 'Autor', 'Tema macro', 'Tema secundário', 'Resumo', 'Tópicos', 'Competências',
       'Nível (dificuldade)', 'O que precisa saber antes', 'Formato', 'Link da pasta', 'Pacote',
       'Origem do autor', 'Base do perfil',
       'Ano estimado', 'Base do ano', 'Atualidade', 'Ferramentas e plataformas', 'Alerta',
       'Integridade', 'Aulas (vídeos, 2 níveis)', 'Volume', 'Materiais de apoio',
       'Grupo de duplicata', 'Cópia principal', 'Varredura']
widths = [46, 26, 24, 20, 60, 50, 50, 16, 40, 16, 22, 20, 14, 12, 10, 10, 12, 40, 30, 16, 10, 10, 36, 10, 10, 14]
ws.append(hdr)
for r in rows:
    ws.append([r[0], r[1], r[8], r[9], r[7], '; '.join(r[10] or []), '\n'.join(r[11] or []), r[12], r[15], r[13],
               f'https://drive.google.com/drive/folders/{r[2]}', r[3], r[4], r[14],
               r[16], r[17], r[18], '; '.join(r[19]), '; '.join(r[20]), r[21], r[22], r[23], '; '.join(r[24]),
               r[25], ('sim' if r[26] else 'não') if r[25] else '', '2 níveis' if r[28] == 2 else 'só nível 1'])
for c in ws[1]:
    c.font = Font(bold=True)
    c.alignment = Alignment(vertical='top', wrap_text=True)
for k, w in enumerate(widths, 1):
    ws.column_dimensions[get_column_letter(k)].width = w
ws.freeze_panes = 'B2'
ws.auto_filter.ref = ws.dimensions
for row in ws.iter_rows(min_row=2):
    for c in row:
        c.alignment = Alignment(vertical='top', wrap_text=True)
    row[10].hyperlink = row[10].value

wt = wb.create_sheet('Trilhas')
wt.append(['Trilha', 'Tema', 'Ordem', 'Curso', 'Autor', 'Nível', 'Por que nesta posição', 'Link da pasta'])
for t in trilhas:
    for k, it in enumerate(t['itens'], 1):
        r = rows[it['i']]
        wt.append([t['titulo'], t['tema'], k, r[0], r[1], r[12], it['porque'], f'https://drive.google.com/drive/folders/{r[2]}'])
for c in wt[1]:
    c.font = Font(bold=True)
for k, w in enumerate([30, 26, 7, 46, 26, 12, 70, 22], 1):
    wt.column_dimensions[get_column_letter(k)].width = w
wt.freeze_panes = 'A2'

wd = wb.create_sheet('Duplicatas')
wd.append(['Grupo', 'Curso', 'Autor', 'Pacote', 'Aulas', 'Integridade', 'Ano', 'Cópia principal', 'Link da pasta'])
for g in range(1, len(dup_groups) + 1):
    for i in dup_groups[g - 1]:
        r = rows[i]
        wd.append([g, r[0], r[1], r[3], r[22], r[21], r[16], 'sim' if r[26] else 'não', f'https://drive.google.com/drive/folders/{r[2]}'])
for c in wd[1]:
    c.font = Font(bold=True)
for k, w in enumerate([7, 46, 26, 22, 8, 16, 8, 12, 22], 1):
    wd.column_dimensions[get_column_letter(k)].width = w
wb.save(f'{R}/Indice-Cursos-Drive.xlsx')

from collections import Counter
print('cursos', len(rows), '| grupos de duplicata', len(dup_groups), '| trilhas', len(trilhas))
print('atualidade', Counter(r[18] for r in rows))
print('integridade', Counter(r[21] for r in rows))
print('com alerta', sum(1 for r in rows if r[20]))
