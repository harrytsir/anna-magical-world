import math, random
W, H = 2400, 1700
R = random.Random(9)
out = []
def add(s): out.append(s)

INK = '#4a3420'; INK2 = '#6e5236'; LAND = '#efe2bf'; SEA = '#cfd3c0'; SEA2 = '#b9bfa8'
RED = '#9c2f22'; GOLD = '#a8741a'

# ---------- helpers ----------
def fractal(pts, depth=6, rough=0.22, closed=True):
    P = pts[:] + ([pts[0]] if closed else [])
    for d in range(depth):
        N = []
        for i in range(len(P) - 1):
            (x1, y1), (x2, y2) = P[i], P[i + 1]
            L = math.hypot(x2 - x1, y2 - y1)
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            nx, ny = -(y2 - y1) / (L or 1), (x2 - x1) / (L or 1)
            off = R.uniform(-1, 1) * L * rough
            N += [(x1, y1), (mx + nx * off, my + ny * off)]
        N.append(P[-1]); P = N
    return P
def path(P, closed=True):
    s = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in P)
    return s + ('Z' if closed else '')
def smooth(P):
    # catmull-rom to cubic
    s = f'M{P[0][0]:.1f},{P[0][1]:.1f}'
    for i in range(len(P) - 1):
        p0 = P[i - 1] if i else P[i]; p1 = P[i]; p2 = P[i + 1]; p3 = P[i + 2] if i + 2 < len(P) else P[i + 1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        s += f' C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}'
    return s
def wiggle(P, amt=8, depth=3):
    return fractal(P, depth, 0.12, closed=False)
def esc(t): return t.replace('&', '&amp;').replace('<', '&lt;')
def text(x, y, t, size=20, fam='GFS Baskerville', anchor='middle', fill=INK, ls=0, style='', weight='normal', halo=True, rot=0, op=1):
    tr = f' transform="rotate({rot} {x} {y})"' if rot else ''
    h = f' stroke="{LAND}" stroke-width="{max(3,size/5):.1f}" stroke-linejoin="round" paint-order="stroke"' if halo else ''
    add(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" letter-spacing="{ls}" font-style="{style or "normal"}" font-weight="{weight}" opacity="{op}"{h}{tr}>{esc(t)}</text>')
def note(x, y, lines, size=15, anchor='middle', fill=INK2):
    for i, l in enumerate(lines):
        text(x, y + i * size * 1.2, l, size, 'GFS Porson', anchor, fill, halo=True)
def inside_ellipse(cx, cy, rx, ry, n, minsep, jitter=1.0):
    pts = []; tries = 0
    while len(pts) < n and tries < n * 60:
        tries += 1
        a = R.random() * 2 * math.pi; r = math.sqrt(R.random())
        x = cx + math.cos(a) * rx * r; y = cy + math.sin(a) * ry * r
        if all(math.hypot(x - px, y - py) > minsep for px, py in pts): pts.append((x, y))
    return sorted(pts, key=lambda p: p[1])
def mountain(x, y, s, snow=False, dark=False, red=False):
    h = s * R.uniform(1.0, 1.5); w = s * R.uniform(0.9, 1.2)
    fillc = '#3a3330' if dark else ('#d9b49a' if red else '#e6d6b0')
    add(f'<path d="M{x-w:.1f},{y:.1f} L{x-w*0.15:.1f},{y-h:.1f} L{x+w*0.1:.1f},{y-h*0.92:.1f} L{x+w:.1f},{y:.1f}Z" fill="{fillc}" stroke="none"/>')
    shade = '#2a2421' if dark else ('#b4806a' if red else '#c9b48a')
    add(f'<path d="M{x-w*0.15:.1f},{y-h:.1f} L{x+w*0.1:.1f},{y-h*0.92:.1f} L{x+w:.1f},{y:.1f} L{x+w*0.15:.1f},{y:.1f}Z" fill="{shade}"/>')
    if snow:
        add(f'<path d="M{x-w*0.42:.1f},{y-h*0.62:.1f} L{x-w*0.15:.1f},{y-h:.1f} L{x+w*0.1:.1f},{y-h*0.92:.1f} L{x+w*0.36:.1f},{y-h*0.6:.1f} L{x+w*0.1:.1f},{y-h*0.66:.1f} L{x-w*0.1:.1f},{y-h*0.55:.1f}Z" fill="#fbf8ef"/>')
    sc = '#1d1916' if dark else INK
    add(f'<path d="M{x-w:.1f},{y:.1f} L{x-w*0.15:.1f},{y-h:.1f} L{x+w*0.1:.1f},{y-h*0.92:.1f} L{x+w:.1f},{y:.1f}" fill="none" stroke="{sc}" stroke-width="1.6" stroke-linejoin="round"/>')
    for k in range(3):
        t = 0.3 + k * 0.2
        add(f'<path d="M{x+w*(0.1+t*0.6):.1f},{y-h*0.92*(1-t):.1f} l{-w*0.25:.1f},{h*0.18:.1f}" stroke="{sc}" stroke-width="0.9" opacity=".6"/>')
def range_(cx, cy, rx, ry, n, s, sep, **kw):
    for x, y in inside_ellipse(cx, cy, rx, ry, n, sep): mountain(x, y, s * R.uniform(0.75, 1.2), **kw)
def tree(x, y, s, kind='round', col='#9aa36a', dark=False):
    sc = INK
    if kind == 'fir':
        c = '#5f6b45' if dark else '#7f8c58'
        add(f'<path d="M{x:.1f},{y-s*2.1:.1f} L{x+s*0.75:.1f},{y:.1f} L{x-s*0.75:.1f},{y:.1f}Z" fill="{c}" stroke="{sc}" stroke-width="1"/>')
        add(f'<path d="M{x:.1f},{y:.1f} v{s*0.4:.1f}" stroke="{sc}" stroke-width="1.2"/>')
    else:
        c = '#5c6a43' if dark else col
        add(f'<path d="M{x:.1f},{y:.1f} v{s*0.5:.1f}" stroke="{sc}" stroke-width="1.2"/>')
        add(f'<circle cx="{x:.1f}" cy="{y-s*0.5:.1f}" r="{s*0.75:.1f}" fill="{c}" stroke="{sc}" stroke-width="1"/>')
        add(f'<path d="M{x-s*0.35:.1f},{y-s*0.7:.1f} a{s*0.4:.1f},{s*0.4:.1f} 0 0 1 {s*0.5:.1f},-{s*0.3:.1f}" stroke="{sc}" stroke-width=".7" fill="none" opacity=".6"/>')
def forest(cx, cy, rx, ry, n, s, sep, **kw):
    for x, y in inside_ellipse(cx, cy, rx, ry, n, sep): tree(x, y, s * R.uniform(0.8, 1.15), **kw)
def town(x, y, label, size=17, dx=0, dy=-14, anchor='middle', big=False):
    if big:
        add(f'<circle cx="{x}" cy="{y}" r="9" fill="{LAND}" stroke="{INK}" stroke-width="2"/><circle cx="{x}" cy="{y}" r="4.5" fill="{RED}"/>')
    else:
        add(f'<circle cx="{x}" cy="{y}" r="5" fill="{INK}" stroke="{LAND}" stroke-width="1.5"/>')
    if label: text(x + dx, y + dy, label, size, anchor=anchor)
def tower(x, y, s=1, col=INK):
    add(f'<g transform="translate({x},{y}) scale({s})"><path d="M-6,0 L-5,-26 L5,-26 L6,0Z" fill="{LAND}" stroke="{col}" stroke-width="1.6"/><path d="M-7,-26 h14 v-5 h-3 v3 h-2.5 v-3 h-3 v3 h-2.5 v-3 h-3Z" fill="{LAND}" stroke="{col}" stroke-width="1.4"/><rect x="-1.5" y="-18" width="3" height="5" fill="{col}"/></g>')
def shard(x, y, n):
    pts = []
    for i in range(16):
        r = 15 if i % 2 == 0 else 6.5
        a = -math.pi / 2 + i * math.pi / 8
        pts.append((x + r * math.cos(a), y + r * math.sin(a)))
    add(f'<path d="{path(pts)}" fill="{GOLD}" stroke="{INK}" stroke-width="1.2"/>')
    add(f'<circle cx="{x}" cy="{y}" r="8.5" fill="{LAND}" stroke="{INK}" stroke-width="1"/>')
    text(x, y + 5, str(n), 13, 'GFS Baskerville', fill=INK, weight='bold', halo=False)

# ---------- canvas & sea ----------
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
add('<defs>'
    '<filter id="rough"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="3"/><feColorMatrix values="0 0 0 0 .3  0 0 0 0 .22  0 0 0 0 .12  0 0 0 .09 0"/><feComposite in2="SourceGraphic" operator="in"/></filter>'
    '<filter id="paper" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".012" numOctaves="4" seed="8"/><feColorMatrix values="0 0 0 0 .45  0 0 0 0 .33  0 0 0 0 .16  0 0 0 .22 0"/></filter>'
    '<filter id="blur8"><feGaussianBlur stdDeviation="8"/></filter><filter id="blur18"><feGaussianBlur stdDeviation="18"/></filter><filter id="blur3"><feGaussianBlur stdDeviation="3"/></filter>'
    f'<pattern id="waves" width="46" height="26" patternUnits="userSpaceOnUse"><path d="M3,15 q6,-6 12,0 t12,0" fill="none" stroke="{SEA2}" stroke-width="1.3"/></pattern>'
    '<pattern id="dunes" width="34" height="22" patternUnits="userSpaceOnUse"><path d="M2,14 q8,-8 16,0" fill="none" stroke="#a5653a" stroke-width="1.2" opacity=".55"/><circle cx="26" cy="6" r=".9" fill="#a5653a" opacity=".5"/></pattern>'
    '<radialGradient id="vign" cx="50%" cy="50%" r="75%"><stop offset="60%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#3b2a14" stop-opacity=".35"/></radialGradient>'
    '</defs>')
add(f'<rect width="{W}" height="{H}" fill="{SEA}"/>')
add(f'<rect width="{W}" height="{H}" fill="url(#waves)" opacity=".7"/>')

# ---------- land ----------
continent = [(130,170),(400,120),(700,95),(1000,110),(1300,90),(1600,105),(1900,80),(2200,95),(2560,40),(2560,1150),
             (2250,1160),(2050,1230),(1880,1290),(1700,1300),(1520,1250),(1420,1290),(1330,1300),(1300,1245),(1240,1300),(1150,1270),
             (1040,1240),(990,1205),(930,1130),(820,1095),(700,1088),(610,1090),(520,1070),(450,1100),(430,1230),(455,1360),
             (390,1470),(260,1520),(150,1470),(95,1300),(120,1080),(80,880),(110,640),(70,420)]
C = fractal(continent, 6, 0.18)
isle_s = fractal([(610,1395),(650,1375),(695,1395),(700,1430),(660,1450),(615,1440)], 4, 0.25)
alfel = fractal([(1555,1505),(1610,1485),(1660,1500),(1655,1530),(1600,1545),(1560,1530)], 4, 0.22)
# coastal ripple lines (sea side)
for k, (w, op) in enumerate([(28, .25), (16, .35), (7, .5)]):
    for poly in (C, isle_s):
        add(f'<path d="{path(poly)}" fill="none" stroke="{SEA2}" stroke-width="{w}" stroke-linejoin="round" opacity="{op}"/>')
add(f'<path d="{path(C)}" fill="{LAND}"/>')
add(f'<path d="{path(isle_s)}" fill="#ddd6c0"/>')

# kingdom tints
tints = [(640,270,330,170,'#c9c2b2'),(560,700,420,330,'#e9d6a2'),(1250,560,270,360,'#c6cf9d'),(1080,890,130,110,'#a8b08a'),
         (1910,560,290,470,'#d8c9a6'),(2320,600,140,560,'#8f8a86'),(250,1280,220,230,'#e3b98c'),(1250,1190,330,110,'#d7d9a8'),(1880,1180,170,90,'#e8e8e4')]
add(f'<clipPath id="landclip"><path d="{path(C)}"/></clipPath><g clip-path="url(#landclip)">')
for cx, cy, rx, ry, c in tints:
    add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{c}" opacity=".55" filter="url(#blur18)"/>')
add('</g>')
add(f'<path d="{path(C)}" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linejoin="round"/>')
add(f'<path d="{path(isle_s)}" fill="none" stroke="{INK}" stroke-width="2"/>')

# desert
desert = fractal([(130,1090),(420,1080),(440,1230),(455,1360),(390,1460),(260,1505),(160,1460),(110,1300)], 4, 0.12)
add(f'<path d="{path(desert)}" fill="#e6bf8f" opacity=".75"/><path d="{path(desert)}" fill="url(#dunes)"/>')

# borders (dashed)
def border(P):
    add(f'<path d="{smooth(wiggle(P))}" fill="none" stroke="{INK2}" stroke-width="1.8" stroke-dasharray="2 7" stroke-linecap="round" opacity=".8"/>')
border([(140,420),(400,410),(700,420),(980,380),(1150,180),(1200,110)])           # Kardor south
border([(990,1150),(1010,980),(960,800),(1010,600),(1000,420)])                     # Farongwest | Eldamor
border([(1660,120),(1640,400),(1620,620),(1640,900),(1600,1150),(1560,1250)])     # Eldamor | Mithloria (west of Silver mts? Silver mts belong to the march)
border([(1050,1235),(1150,1110),(1350,1080),(1550,1120),(1650,1160)])             # Aktilia north
border([(455,1080),(300,1060),(140,1060)])                                         # desert | Farongwest
border([(1700,1290),(1760,1150),(1980,1080),(2150,1120)])                          # Ourania

# ---------- rivers ----------
def river(P, w=3.2):
    d = smooth(wiggle(P))
    add(f'<path d="{d}" fill="none" stroke="{LAND}" stroke-width="{w+3}" stroke-linecap="round"/>')
    add(f'<path d="{d}" fill="none" stroke="#7b8a8c" stroke-width="{w}" stroke-linecap="round"/>')
river([(650,330),(645,430),(600,540),(615,640),(660,705),(720,760),(705,850),(660,940),(640,1010),(615,1088)], 4)  # Arneth
river([(760,560),(720,640),(690,700)], 2)
river([(1870,330),(1890,400),(1880,460),(1905,520)], 2.6)  # Golden river
river([(930,990),(950,1060),(985,1130),(995,1200)], 2.2)   # waterfall stream
river([(1300,300),(1240,420),(1200,560),(1140,700),(1060,760),(1000,820)], 2)  # elf river

# lake Mavrolimni
lake = fractal([(1880,535),(1930,515),(1990,530),(2010,565),(1975,600),(1915,605),(1870,580)], 4, 0.2)
add(f'<path d="{path(lake)}" fill="#a9b3ab" stroke="{INK}" stroke-width="1.8"/>')
add(f'<path d="{path(lake)}" fill="url(#waves)" opacity=".8"/>')
# dragon lake
add(f'<ellipse cx="1866" cy="322" rx="13" ry="9" fill="#a9b3ab" stroke="{INK}" stroke-width="1.4"/>')
# star lake


# ---------- mountains & forests ----------
range_(640, 255, 300, 130, 70, 26, 34, snow=True)                 # Kardor
range_(1880, 175, 180, 60, 26, 22, 30, snow=True)                 # Frozen mountains
range_(1800, 330, 120, 70, 14, 22, 32)                            # northern mts / Sleeper
mountain(2025, 345, 34, snow=True)                                # the Sleeper
range_(1560, 720, 55, 170, 24, 26, 30)                            # Silver mts
mountain(1560, 575, 40, dark=True)                                # Petrofteros peak
range_(2050, 420, 80, 110, 14, 20, 30)                            # Mithloria E
range_(1790, 760, 90, 60, 10, 18, 30)                             # Mithloria SW hills
range_(1805, 905, 70, 45, 10, 20, 28)                             # Solitude mts (grey)
range_(2190, 620, 45, 380, 44, 28, 26, dark=True)                 # Shadow mountains
range_(905, 930, 80, 55, 13, 22, 26, red=True)                    # Pyrovouna
range_(905, 650, 65, 70, 9, 17, 28)                               # Last Guard hills
mountain(470, 960, 22); mountain(560, 955, 24)                    # Aetochori's two mountains
range_(1890, 1170, 150, 70, 20, 28, 34, snow=True)                # Ourania mts
range_(2330, 380, 70, 200, 12, 18, 34, dark=True)                 # Skiochora ridges

forest(1240, 520, 235, 305, 520, 8.5, 14, col='#97a462')
forest(1240, 520, 200, 260, 90, 8, 22, col='#7f9150')           # Eldamor
forest(1085, 890, 115, 85, 55, 12, 18, dark=True)                 # Moonforest
forest(1720, 640, 55, 85, 22, 11, 17, kind='fir', dark=True)      # Nyktofyllo
forest(2010, 720, 70, 45, 22, 11, 17, kind='fir')                 # Wind forest
forest(2040, 498, 48, 32, 16, 9, 14, kind='fir')                  # Star forest
add(f'<circle cx="2040" cy="502" r="8" fill="#a9b3ab" stroke="{INK}" stroke-width="1.2"/>')  # star lake inside the forest
forest(1420, 900, 70, 40, 14, 9, 18, kind='fir', dark=True)       # rusted woods
forest(2315, 760, 60, 90, 12, 9, 20, kind='fir', dark=True)       # leafless trees of Skiochora
# mist over Nyktofyllo & Alfeloria
add(f'<ellipse cx="1720" cy="640" rx="85" ry="110" fill="#f6f2e6" opacity=".55" filter="url(#blur8)"/>')

for (cx,cy,rx,ry,n) in [(560,560,330,170,60),(700,960,250,80,30),(1300,1180,240,60,30),(1150,240,120,80,14),(1400,1000,140,60,16)]:
    for x,y in inside_ellipse(cx,cy,rx,ry,n,26):
        add(f'<path d="M{x-5:.0f},{y:.0f} l2,-6 M{x:.0f},{y:.0f} l0,-8 M{x+5:.0f},{y:.0f} l-2,-6" stroke="{INK2}" stroke-width="1" opacity=".55"/>')
for x,y in inside_ellipse(820,520,140,90,7,60)+inside_ellipse(380,860,120,70,6,60)+inside_ellipse(1500,1180,90,40,4,60):
    mountain(x, y, 11)
# ---------- seas ----------
# storm wall
for i in range(26):
    x = 480 + i * 18 + R.uniform(-6, 6); y = 1250 + R.uniform(-22, 22)
    add(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{R.uniform(16,30):.0f}" fill="#4d4a48" opacity=".55" filter="url(#blur3)"/>')
for i in range(5):
    x = 520 + i * 90
    add(f'<path d="M{x},{1240} l12,22 l-9,2 l14,26" fill="none" stroke="#f2e9a0" stroke-width="2.2"/>')
# mists (south sea)
for cx, cy, rx in [(1608, 1515, 120), (1840, 1575, 110), (1720, 1580, 90)]:
    add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{rx*0.45}" fill="#f8f5ec" opacity=".75" filter="url(#blur18)"/>')
# Alfeloria floating
add(f'<path d="{path(alfel)}" fill="#e3e9cf" stroke="{INK}" stroke-width="1.8" transform="translate(0,-14)"/>')
add(f'<ellipse cx="1608" cy="1535" rx="52" ry="7" fill="#7b7f70" opacity=".35"/>')
forest(1608, 1500, 32, 10, 6, 7, 11, col='#b9c98e')
add(f'<ellipse cx="1840" cy="1575" rx="46" ry="20" fill="none" stroke="{INK2}" stroke-width="1.6" stroke-dasharray="5 6"/>')
text(1840, 1583, '?', 26, halo=False, fill=INK2)
# sea serpents
def serpent(x, y, s=1):
    add(f'<g transform="translate({x},{y}) scale({s})" fill="none" stroke="{INK}" stroke-width="2.2"><path d="M0,0 q14,-26 28,0 q14,26 28,0 q14,-26 28,0"/><path d="M84,0 q10,-14 22,-10 l-4,6 6,2" /><circle cx="101" cy="-9" r="1.6" fill="{INK}"/></g>')
serpent(760, 1500, 0.9); serpent(470, 1630, 0.7); serpent(1150, 1420, 0.6)
# ships
def ship(x, y, s=1):
    add(f'<g transform="translate({x},{y}) scale({s})"><path d="M-22,0 q22,12 44,0 l-5,-6 h-34Z" fill="#c8a675" stroke="{INK}" stroke-width="1.6"/><path d="M0,-6 v-38" stroke="{INK}" stroke-width="1.6"/><path d="M1,-42 q16,14 0,30Z" fill="#f6efdc" stroke="{INK}" stroke-width="1.3"/></g>')
ship(1360, 1360, 1.0); ship(1030, 1330, 0.8)

# ---------- route of the Stones ----------
route = [(1935,500),(1830,600),(1720,640),(1640,690),(1575,700),(1560,600),(1575,700),(1545,830),(1520,905),(1380,905),(1210,890),(1085,890),
         (980,915),(905,930),(940,1000),(960,1060),(985,1140),(1000,1190),(900,1260),(760,1320),(690,1390),(640,1420),(540,1360),(440,1320),
         (300,1270),(330,1150),(420,1040),(515,955),(640,850),(800,700),(900,650),(820,690),(735,720)]
add(f'<path d="{smooth(route)}" fill="none" stroke="{LAND}" stroke-width="7" stroke-linecap="round" opacity=".7"/>')
add(f'<path d="{smooth(route)}" fill="none" stroke="{RED}" stroke-width="3" stroke-dasharray="11 8" stroke-linecap="round"/>')

# ---------- places ----------
# Farongwest
tower(708, 712, 1.25); town(690, 728, '', big=True)
text(700, 766, 'Η Πόλη', 22, weight='bold')
note(700, 788, ['επτά κύκλοι από άσπρη πέτρα', 'ο Πύργος & η Κρύπτη των Φυλάκων'], 14)
town(515, 955, 'Αετοχώρι', 17, dy=24)
town(900, 650, 'Η Τελευταία Φρουρά', 16, dy=-18)
text(395, 640, 'ΦΑΡΟΝΓΟΥΕΣΤ', 50, ls=10)
text(395, 678, 'το παλαιότερο βασίλειο · η πεδιάδα του Άρνεθ', 17, 'GFS Porson', fill=INK2)
text(612, 560, 'Άρνεθ', 17, 'GFS Porson', style='italic', rot=-62, fill='#4f6466')
# Kardor
add(f'<path d="M628,300 a14,14 0 0 1 28,0 v8 h-28Z" fill="#2c2620" stroke="{INK}" stroke-width="1.4"/>')
text(640, 145, 'ΚΑΡΝΤΟΡ', 46, ls=10)
note(642, 332, ['η πόλη των νάνων μέσα στο βουνό', 'το βουνό που τραγουδά'], 14)
text(660, 390, 'οι πηγές του Άρνεθ', 13, 'GFS Porson', fill='#4f6466')
# Eldamor
text(1250, 330, 'ΕΛΝΤΑΜΟΡ', 46, ls=10)
note(1250, 362, ['το απέραντο δάσος των ξωτικών'], 16)
add(f'<g transform="translate(1255,505)"><path d="M0,0 v-30" stroke="{INK}" stroke-width="3"/><circle cx="0" cy="-44" r="24" fill="#e9e3a8" stroke="{INK}" stroke-width="1.6"/><circle cx="0" cy="-44" r="34" fill="#fff6c8" opacity=".45" filter="url(#blur8)"/></g>')
text(1255, 528, 'η Ελφάνια', 17, weight='bold')
text(1085, 772, 'Φεγγαρόδασος', 19)
note(1085, 990, ['ο Τάφος της Ελεάνας'], 14)
# Pyrovouna & waterfall
text(825, 905, 'Πυρόβουνα', 19, anchor='end')
note(840, 1000, ['η Οικία του Θρόνταρ'], 14, anchor='end')
add(f'<path d="M958,1048 v18" stroke="#6c8a94" stroke-width="5"/>')
note(975, 1060, ['ο καταρράκτης', 'του Πετροφύλακα'], 13, anchor='start')
# Silver mountains
text(1490, 640, 'Βουνά του Αργύρου', 18, rot=-90)
note(1575, 520, ['Κορυφή του Πετρόφτερου'], 14)
note(1588, 762, ['Βράχος των Ανέμων', '(ο Αργυροφτέρης)'], 13, anchor='start')
note(1500, 950, ['Στενωπός των Μεταλλόραμφων'], 14)
note(1420, 860, ['δάση της σκουριάς'], 13)
# Mithloria
add(f'<g transform="translate(1935,498)">' + ''.join(f'<path d="M{dx-7},0 l7,-9 l7,9Z" fill="{GOLD}" stroke="{INK}" stroke-width="1"/>' for dx in (-16, -2, 12)) + '</g>')
town(1937, 506, '', big=True)
text(1945, 470, 'Μιθλόρια', 22, weight='bold')
note(1945, 487, ['η πόλη με τις χρυσές στέγες'], 13)
text(1945, 586, 'Μαυρολίμνη', 15, 'GFS Porson', fill='#3f5456')
tower(1995, 600, 0.7); note(2020, 622, ['πύργος του λιμανιού'], 12, anchor='start')
text(1900, 235, 'ΜΙΘΛΟΡΙΑ', 50, ls=10)
note(1900, 120, ['Τα Παγωμένα Βουνά', '(οι καλικάντζαροι)'], 15)
note(2055, 300, ['το Κοιμισμένο'], 14, anchor='start'); town(2045, 365, '', ); note(2056, 380, ['Ψηλολίβαδο'], 13, anchor='start')
note(1860, 300, ['η λίμνη του Χρυσόλεπου'], 13, anchor='end')
text(1860, 425, 'Χρυσός Ποταμός', 13, 'GFS Porson', fill='#4f6466', rot=78)
town(1955, 445, '', ); note(1965, 440, ['λόφος του Κρίνου'], 12, anchor='start')
note(2040, 545, ['Δάσος των Αστεριών', '(η Λίμνη του Άστρου)'], 12)
note(1712, 530, ['Νυκτόφυλλο', '(το δάσος που θυμάται)'], 14)
town(1835, 640, 'Λευκόβρυση', 14, dy=18)
note(2010, 668, ['Δάσος των Ανέμων'], 14)
town(2060, 795, 'το χωριό των παππούδων', 14, dy=20)
tower(1805, 900, 0.7); note(1805, 960, ['Βουνά της Μοναξιάς'], 14)
# Shadow mountains & Skiochora
text(2140, 640, 'ΒΟΥΝΑ ΤΗΣ ΣΚΙΑΣ', 22, ls=6, rot=-90, fill='#2b2422')
add(f'<path d="M2196,520 v34" stroke="#1d1d22" stroke-width="5"/><rect x="2186" y="556" width="20" height="16" rx="8" fill="#1d1916" stroke="{RED}" stroke-width="1.5"/>')
note(2200, 595, ['η Πόρτα', 'στο Βουνό'], 13)
for tx, ty in [(2305, 470), (2345, 690), (2290, 930)]:
    add(f'<g transform="translate({tx},{ty})"><path d="M-5,0 L-3,-34 L0,-44 L3,-34 L5,0Z" fill="#2a2522" stroke="#000" stroke-width="1"/><rect x="-1.5" y="-26" width="3" height="4" fill="#e8913a"/></g>')
text(2330, 560, 'ΣΚΙΟΧΩΡΑ', 34, ls=8, rot=90, fill='#2b2422')
note(2330, 1010, ['οι νεκρομάντες', '· τα περάσματα', 'κλειστά από', 'την Πτώση'], 13)
# Ourania
add(f'<ellipse cx="1890" cy="1135" rx="150" ry="22" fill="#ffffff" opacity=".85" filter="url(#blur8)"/>')
add(f'<g transform="translate(1890,1100)"><path d="M-30,10 v-22 l6,-14 l6,14 v-6 l6,-18 l6,18 v-4 l6,-12 l6,12 v22Z" fill="#fbfaf3" stroke="{INK}" stroke-width="1.5"/></g>')
text(1890, 1030, 'ΟΥΡΑΝΙΑ ΠΟΛΙΤΕΙΑ', 28, ls=6)
note(1890, 1052, ['το κάστρο πάνω από τα σύννεφα · οι μάντισσες'], 14)
# Aktilia
town(1300, 1230, '', big=True)
text(1300, 1210, 'το χρυσό λιμάνι', 16, weight='bold')
text(1260, 1140, 'ΑΚΤΗΛΙΑ', 40, ls=10)
town(1000, 1190, 'Αλμυρίδα', 16, dx=10, dy=-6, anchor='start')
note(1012, 1210, ['το τελευταίο ψαροχώρι'], 12, anchor='start')
# Storm sea & isle & desert
text(690, 1555, 'Θάλασσα των Θυελλών', 26, 'GFS Porson', fill='#3e4a48', halo=False)
note(655, 1475, ['Νησί της Σιωπής'], 15)
text(280, 1170, 'Έρημος της Απελπισίας', 22, 'GFS Porson', fill='#7a3b1e')
note(300, 1300, ['ο θαμμένος ναός'], 13)
# south sea kingdoms
text(1608, 1580, 'ΑΛΦΕΛΟΡΙΑ', 24, ls=6)
note(1608, 1600, ['το νησί που κρέμεται', 'πάνω από το νερό'], 13)
text(1840, 1625, 'ΑΛΦΑΤΑ', 24, ls=6, op=.8)
note(1840, 1645, ['κρυμμένη στις ομίχλες'], 13)

# shards
for (x, y, n) in [(1560, 548, 1), (1085, 935, 2), (950, 1030, 3), (775, 1330, 4), (655, 1420, 5), (300, 1250, 6), (735, 690, 7)]:
    shard(x, y, n)

# ---------- cartouche, compass, legend ----------
def compass(x, y, r):
    g = f'<g transform="translate({x},{y})">'
    g += f'<circle r="{r}" fill="{LAND}" stroke="{INK}" stroke-width="2"/><circle r="{r*0.82}" fill="none" stroke="{INK}" stroke-width="1"/>'
    for i in range(8):
        a = i * math.pi / 4; L = r * (0.95 if i % 2 == 0 else 0.6); w = r * 0.13
        tip = (L * math.sin(a), -L * math.cos(a)); l = (w * math.cos(a), w * math.sin(a))
        g += f'<path d="M0,0 L{l[0]:.1f},{l[1]:.1f} L{tip[0]:.1f},{tip[1]:.1f}Z" fill="{INK}"/><path d="M0,0 L{-l[0]:.1f},{-l[1]:.1f} L{tip[0]:.1f},{tip[1]:.1f}Z" fill="{LAND}" stroke="{INK}" stroke-width="1"/>'
    g += '</g>'; add(g)
    for t, dx, dy in [('Β', 0, -r - 10), ('Ν', 0, r + 26), ('Α', r + 18, 8), ('Δ', -r - 18, 8)]:
        text(x + dx, y + dy, t, 22, weight='bold', halo=False)
compass(2280, 1250 + 0, 0) if False else None
compass(330, 1595, 50)  # south-west sea
# title cartouche
add(f'<g transform="translate(1180,1570)"><rect x="-250" y="-58" width="500" height="112" rx="10" fill="{LAND}" stroke="{INK}" stroke-width="2.4"/><rect x="-241" y="-49" width="482" height="94" rx="7" fill="none" stroke="{INK}" stroke-width="1"/></g>')
text(1180, 1565, 'Τα Εννέα Βασίλεια', 44, halo=False)
text(1180, 1600, 'ο κόσμος της Άννας, του Έαρον και της Κατιάννας', 16, 'GFS Porson', fill=INK2, halo=False)
# legend
lx, ly = 1990, 1330
add(f'<rect x="{lx}" y="{ly}" width="390" height="230" rx="8" fill="{LAND}" stroke="{INK}" stroke-width="2" opacity=".96"/>')
text(lx + 195, ly + 32, 'Υπόμνημα', 22, halo=False)
add(f'<path d="M{lx+22},{ly+60} h50" stroke="{RED}" stroke-width="3" stroke-dasharray="11 8"/>'); text(lx + 85, ly + 66, 'ο δρόμος της Αναζήτησης (Οι Πέτρες)', 15, 'GFS Porson', 'start', halo=False)
shard(lx + 47, ly + 96, 1); text(lx + 85, ly + 101, 'τα επτά θραύσματα της Πέτρας', 15, 'GFS Porson', 'start', halo=False)
add(f'<circle cx="{lx+47}" cy="{ly+132}" r="9" fill="{LAND}" stroke="{INK}" stroke-width="2"/><circle cx="{lx+47}" cy="{ly+132}" r="4.5" fill="{RED}"/>'); text(lx + 85, ly + 137, 'πόλη / πρωτεύουσα', 15, 'GFS Porson', 'start', halo=False)
add(f'<circle cx="{lx+47}" cy="{ly+164}" r="5" fill="{INK}"/>'); text(lx + 85, ly + 169, 'χωριό ή τόπος', 15, 'GFS Porson', 'start', halo=False)
add(f'<path d="M{lx+22},{ly+196} h50" stroke="{INK2}" stroke-width="1.8" stroke-dasharray="2 7" stroke-linecap="round"/>'); text(lx + 85, ly + 201, 'σύνορα βασιλείων (κατά προσέγγιση)', 15, 'GFS Porson', 'start', halo=False)

# paper texture, vignette, frame
add(f'<rect width="{W}" height="{H}" filter="url(#paper)" opacity=".9"/>')
add(f'<rect width="{W}" height="{H}" fill="url(#vign)"/>')
add(f'<rect x="10" y="10" width="{W-20}" height="{H-20}" fill="none" stroke="{INK}" stroke-width="5"/><rect x="22" y="22" width="{W-44}" height="{H-44}" fill="none" stroke="{INK}" stroke-width="1.5"/>')
add('</svg>')
open('/tmp/claude-0/-home-claude/a779f8b5-5410-586a-94ff-db2fef3b8cc0/scratchpad/map/map.svg', 'w', encoding='utf-8').write('\n'.join(out))
print('ok', len(out))
