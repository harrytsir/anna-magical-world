import sys, copy, re, glob, os
import docx
from docx.oxml.ns import qn

tmpl, srcdir, out = sys.argv[1], sys.argv[2], sys.argv[3]
d = docx.Document(tmpl)
body = d.element.body
ps = list(d.paragraphs)
T_TITLE = copy.deepcopy(ps[0]._p)
T_EMPTY = copy.deepcopy(ps[1]._p)
T_DROP = copy.deepcopy(ps[2]._p)
T_BODY = copy.deepcopy(ps[3]._p)

# remove all existing paragraphs/tables from body (keep sectPr)
for el in list(body):
    if el.tag != qn('w:sectPr'):
        body.remove(el)
sect = body.find(qn('w:sectPr'))

def clean_runs(p):
    for r in p.findall(qn('w:r')):
        p.remove(r)
    for r in p.findall(qn('w:hyperlink')):
        p.remove(r)

def base_run(p_tmpl):
    r = p_tmpl.find(qn('w:r'))
    return copy.deepcopy(r)

RUN_TITLE = base_run(T_TITLE)
RUN_DROP = base_run(T_DROP)
RUN_BODY = base_run(T_BODY)

def mk_run(rtmpl, text, italic=False):
    r = copy.deepcopy(rtmpl)
    for t in r.findall(qn('w:t')): r.remove(t)
    for b in r.findall(qn('w:br')): r.remove(b)
    rpr = r.find(qn('w:rPr'))
    if italic:
        i = rpr.makeelement(qn('w:i'), {})
        rpr.insert(1, i)
    t = r.makeelement(qn('w:t'), {})
    t.text = text
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    r.append(t)
    return r

def add_inline(p, rtmpl, text, base_italic=False):
    parts = re.split(r'(\*[^*]+\*)', text)
    for part in parts:
        if not part: continue
        if part.startswith('*') and part.endswith('*') and len(part) > 2:
            p.append(mk_run(rtmpl, part[1:-1], italic=not base_italic))
        else:
            p.append(mk_run(rtmpl, part, italic=base_italic))

def set_center(p):
    ppr = p.find(qn('w:pPr'))
    jc = ppr.find(qn('w:jc'))
    jc.set(qn('w:val'), 'center')

def append(p):
    sect.addprevious(p)

files = sorted(glob.glob(os.path.join(srcdir, '*.md')))
for fi, f in enumerate(files):
    lines = open(f, encoding='utf-8').read().split('\n')
    title = lines[0][2:].strip()
    paras = []
    buf = []
    for l in lines[1:]:
        if l.strip() == '':
            if buf: paras.append(' '.join(buf)); buf = []
        else:
            buf.append(l.strip())
    if buf: paras.append(' '.join(buf))
    age = paras.pop(0)  # *Η Άννα ήταν ...*
    # title
    p = copy.deepcopy(T_TITLE); clean_runs(p); add_inline(p, RUN_TITLE, title); append(p)
    # age line (italic, centered) using empty-para formatting
    p = copy.deepcopy(T_EMPTY); clean_runs(p); set_center(p); add_inline(p, RUN_BODY, age.strip('*'), base_italic=True); append(p)
    first = True
    for i, text in enumerate(paras):
        is_last = (i == len(paras) - 1)
        if text.replace(' ', '') == '***':
            p = copy.deepcopy(T_BODY); clean_runs(p); set_center(p); p.append(mk_run(RUN_BODY, '*   *   *')); append(p)
            continue
        if first:
            first = False
            m = re.match(r'^([«]?\w)', text)
            letter = m.group(1)
            rest = text[len(letter):]
            p = copy.deepcopy(T_DROP); clean_runs(p); p.append(mk_run(RUN_DROP, letter)); append(p)
            p = copy.deepcopy(T_BODY); clean_runs(p); add_inline(p, RUN_BODY, rest); append(p)
        else:
            p = copy.deepcopy(T_BODY); clean_runs(p); add_inline(p, RUN_BODY, text); append(p)
        if is_last and fi < len(files) - 1:
            r = copy.deepcopy(RUN_BODY)
            for t in r.findall(qn('w:t')): r.remove(t)
            br = r.makeelement(qn('w:br'), {qn('w:type'): 'page'})
            r.append(br)
            p.append(r)

d.core_properties.title = 'Οι Ιστορίες της Άννας'
d.save(out)
print('stories', len(files))
