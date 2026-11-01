import csv, re, glob, sys, unicodedata

PACKS = {
    # SUPER Extra são gravados já com o nome do pacote em raw.tsv
    '1zzQeGBdLf3PWumyogdhjOlJPjhhDVLzm': 'DRIVE 06',
    '1H3qyaEWYpaU7xf8qIGThZ8zbyoZ2OM_Z': 'DRIVE 07',
    '1o1szlz6RHnMIn2tiJ_uAqsc3fHOLNm8Y': 'DRIVE 08',
    '1InaZ_bJGzH343yaefp2h5KC_vpA49q6D': 'DRIVE 09',
    '1erqrcydsqOnxYxPadiHZC2fYvBQUbtBO': 'DRIVE 10',
    '1CIr8a0ATM1YpZHIHoLS9KitfCPplmdl2': 'DRIVE 11',
    '19f74K5xYBjJtYczUDXjKXUvK_h2IDN3x': 'DRIVE 12',
    '1X8u1qP1n_lhgIzGx8Ns4aswP5ZWfCQh2': 'DRIVE 13',
    '1focEt7RUogsYfdutaCWG0ySk7mYS_wKs': 'DRIVE 14',
    '1ahcNi45ngQmUzx5U_kKXXyUF7SS-sWfo': 'Cursos Extras (Saulo)',
    '1CTdhtyE6PpOzNbgfXVEdZ1N3ZLyP1peC': 'Cursos Extras (premium009)',
    '12xFAqwZZw_Ygh25rss0At5-E6Bp_bf9i': 'Pack Ful 2026',
    '1JVVJ4F6XCjLGoGzl7dzup8u5zc5MytiM': 'EXTRA PREMIUM 2',
    '1rbgF2JLhnPmW-tcb9WWwe3EGDlmY9D4r': 'Extra (digital101)',
}

SKIP = re.compile(r'IMPORTANTE|LEIA|PERDEU SEU ACESSO|^\s*$', re.I)
CONTAINER = re.compile(r'SUPER \[Extra|^Pack|^DRIVE|Cursos Extras|EXTRA PREMIUM|CURSOS GRINGOS', re.I)


def strip_lead(s):
    # remove emojis/símbolos e pontuação do começo
    i = 0
    while i < len(s):
        c = s[i]
        cat = unicodedata.category(c)
        if c.isalnum() or c in '[(@':
            break
        i += 1
    return s[i:].strip()


def clean(s):
    s = re.sub(r'\s+', ' ', s).strip(' -–—_.')
    return s


def titlecase_if_shouting(s):
    letters = [c for c in s if c.isalpha()]
    if letters and sum(c.isupper() for c in letters) / len(letters) > 0.8 and len(letters) > 4:
        small = {'de', 'da', 'do', 'das', 'dos', 'e', 'a', 'o', 'na', 'no', 'em', 'com', 'para', 'ao', 'aos'}
        words = s.lower().split(' ')
        out = []
        for i, w in enumerate(words):
            if i and w in small:
                out.append(w)
            elif re.fullmatch(r'[ivx]+', w) or re.fullmatch(r'[a-z]{1,3}\d*', w) and w in {'ia', 'ugc', 'vsl', 'g4', 'tiktok', 'mvs', 'cvd', 'sme', 'dtc', 'ltv', 'plr', 'mfm', 'fva', 'abr', 'evo', 'gpa', 'msa', 'fq', '3ls', 'fpv'}:
                out.append(w.upper())
            else:
                out.append(w[:1].upper() + w[1:])
        return ' '.join(out)
    return s


YEAR = re.compile(r'\s*[\[(](?:20\d\d|novo|atualizad[oa][^\])]*)[\])]\s*', re.I)


def split(title):
    t = strip_lead(title)
    t = clean(t)
    # separadores: " - ", " – ", " — "
    parts = re.split(r'\s+[-–—]\s+|(?<=\S)-(?=[A-ZÁÉÍÓÚ][a-z])', t)
    parts = [clean(p) for p in parts if clean(p)]
    # tira partes que são só ano
    yearish = [p for p in parts if re.fullmatch(r'20\d\d', p)]
    parts = [p for p in parts if not re.fullmatch(r'20\d\d', p)]
    if len(parts) >= 2:
        author = parts[-1]
        course = ' - '.join(parts[:-1])
        # "Curso Criador Bergamo (2026)" etc: se o "autor" parece título, troca
        if len(author.split()) > 5:
            course, author = t, ''
    else:
        course, author = (parts[0] if parts else t), ''
        m = re.search(r'\(([^)]*@[^)]*)\)\s*$', course)
        if m:
            author = m.group(1)
            course = course[:m.start()].strip()
    # autor entre parênteses no fim do autor: "Copini (AlphaLife)" fica
    course = YEAR.sub(' ', course)
    author = YEAR.sub(' ', author)
    course = re.sub(r'\s*\[20\d\d\]|\s*\(20\d\d\)', '', course)
    author = re.sub(r'\s*\[20\d\d\]|\s*\(20\d\d\)', '', author)
    return titlecase_if_shouting(clean(course)), titlecase_if_shouting(clean(author))


MANUAL = {
    'Formacao em Suporte Ativo - Icaro de Carvalho O Novo Mercado': ('Formação em Suporte Ativo (O Novo Mercado)', 'Ícaro de Carvalho'),
    '[vip] bastidores @dougdemarco': ('[VIP] Bastidores', 'Doug Demarco'),
    'Curso de Ingles Mairo Vergara 5.0': ('Curso de Inglês 5.0', 'Mairo Vergara'),
    'Curso Online de Desenho Realista com Alexandre Porto': ('Curso Online de Desenho Realista', 'Alexandre Porto'),
    'Treinamentos do Dailtinho': ('Treinamentos do Dailtinho', 'Dailtinho'),
    'Pablo Marçal': ('Pablo Marçal (pacote)', 'Pablo Marçal'),
    'Berman Investimentos': ('Berman Investimentos', 'Berman'),
    'MFM 1.0 [concluido ✅]': ('MFM 1.0', ''),
    'Formação G4': ('Formação G4 – Gestão 4.0', 'G4 Educação'),
    'Pablo Spyer': ('Touro de Ouro (Completo)', 'Pablo Spyer'),
}
CONTAINERISH = re.compile(r'^Pasta \d+$|^Cursos Gringos$', re.I)


def fix(c, a, title):
    EXTRA = {
        'Brian Moran': ('5 Minute VSL', 'Brian Moran'),
        'Robby Blanchard - Clickbank': ('Spark 200 Level Course (Clickbank)', 'Robby Blanchard'),
        'Gerardo Perez – How to Run TikTok Ads by Foundr': ('How to Run TikTok Ads (Foundr)', 'Gerardo Perez'),
        'Todd Brown': ('A-Z Copywriting Workshop', 'Todd Brown'),
        'Rmbc Method': ('RMBC Method', 'Stefan Georgi'),
        'Entregando Ouro': ('Entregando Ouro – Imersão Tio do Digital', 'Tio do Digital'),
        'Método GDF': ('Método GDF (Emagrecimento)', ''),
        'Leitura Dinâmica- Elias maman': ('Leitura Dinâmica', 'Elias Maman'),
        'Fórmula de Lançamento 2023': ('Fórmula de Lançamento 2023', 'Erico Rocha'),
        'Sites Lucrativos': ('Sites Lucrativos', 'Escola de Sites'),
    }
    if c in EXTRA:
        return EXTRA[c]
    if c in MANUAL:
        return MANUAL[c]
    if (c + ' - ' + a) in MANUAL:
        return MANUAL[c + ' - ' + a]
    if c == 'Curso de Ingles' and a.startswith('Mairo'):
        return 'Curso de Inglês 5.0', 'Mairo Vergara'
    m = re.match(r'^(.*?)\s*\(([^)]*)\)$', a)
    if c == 'CF' and m:
        return f'Close Friends ({m.group(2)})', m.group(1)
    if c == 'CF':
        return 'Close Friends', a
    if c.startswith('CF - '):
        m2 = re.match(r'^CF - (.*?)\s*\((.*)\)$', c)
        if m2:
            return f'Close Friends ({m2.group(2)})', m2.group(1)
    for pat, tr in [(r'^Jota Trader - (.*)$', 'Jota Trader'), (r'^Only Shot Trader - (.*)$', 'Only Shot Trader')]:
        mm = re.match(pat, c)
        if mm:
            return mm.group(1), tr
    a = re.sub(r'\s+20\d\d(/\d\d)?$', '', a)          # "Fê Alves 2023"
    a = re.sub(r'\s*\((Completo|Copywriting|Infoprodutos.*|Dropshipping|Biohacking|3 Temporada|Especialista.*)\)$', '', a)
    if CONTAINERISH.search(c):
        a = '(pasta sem subpastas)'
    return c, a


def main():
    rows = []
    for line in open('/home/claude/idx/raw.tsv', encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        if len(p) == 3:
            rows.append((p[0], p[1], p[2]))
    for f in ['/home/claude/idx/raw2.tsv'] + sorted(glob.glob('/home/claude/idx/agent_*.tsv')):
        for line in open(f, encoding='utf-8'):
            p = line.rstrip('\n').split('\t')
            if len(p) != 3:
                continue
            pack = PACKS.get(p[0], p[0])
            rows.append((pack, p[1], p[2]))
    # pacotes-container expandidos pelo agente D: nomear pelo título
    ids_title = {r[2]: r[1] for r in rows}
    seen, out, containers = set(), [], []
    for pack, title, fid in rows:
        if fid in seen:
            continue
        seen.add(fid)
        if pack in ids_title:  # filho de um container
            pack = clean(strip_lead(ids_title[pack]))
        if SKIP.search(title):
            continue
        if CONTAINER.search(title):
            containers.append(title)
            continue
        c, a = fix(*split(title), title)
        out.append((c, a, f'https://drive.google.com/drive/folders/{fid}', pack, title))
    with open('/home/claude/idx/cursos.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['Curso', 'Autor', 'Link da pasta', 'Pacote', 'Nome original'])
        w.writerows(out)
    print(len(out), 'cursos;', len(containers), 'containers ignorados')


if __name__ == '__main__':
    main()
