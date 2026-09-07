# -*- coding: utf-8 -*-
"""Полигональная сетка лица: точки-ориентиры + триангуляция Боуэра-Ватсона."""
import io, math, random

W = H = 200
CX, CY = 100.0, 100.0
RX, RY = 46.0, 62.0          # овал лица


def on_oval(t, k=1.0):
    """точка на овале лица; t в долях окружности"""
    a = -math.pi / 2 + t * 2 * math.pi
    # подбородок уже лба: сжимаем нижнюю половину
    r = 1.0 - 0.16 * max(0.0, math.sin(a))
    return (CX + RX * k * r * math.cos(a), CY + RY * k * math.sin(a))


pts = []
# контур
for i in range(18):
    pts.append(on_oval(i / 18.0))
# два внутренних кольца
for i in range(14):
    pts.append(on_oval(i / 14.0 + 0.02, 0.68))
for i in range(9):
    pts.append(on_oval(i / 9.0 + 0.05, 0.34))
# черты: глаза, нос, рот, брови
feat = [(78, 88), (92, 86), (108, 86), (122, 88),          # брови
        (82, 97), (95, 97), (105, 97), (118, 97),          # глаза
        (100, 92), (100, 108), (100, 120),                 # переносица-нос
        (92, 122), (108, 122),                             # крылья носа
        (88, 136), (100, 134), (112, 136), (100, 142),     # рот
        (70, 112), (130, 112),                             # скулы
        (100, 155)]                                        # подбородок
pts += [(float(x), float(y)) for x, y in feat]

# убираем совпадающие
uniq = []
for p in pts:
    if all(abs(p[0] - q[0]) > 0.6 or abs(p[1] - q[1]) > 0.6 for q in uniq):
        uniq.append(p)
pts = uniq


# ---------- Боуэр-Ватсон ----------
def circumcircle(a, b, c):
    ax, ay = a; bx, by = b; cx, cy = c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-12:
        return None
    ux = ((ax*ax + ay*ay) * (by - cy) + (bx*bx + by*by) * (cy - ay) + (cx*cx + cy*cy) * (ay - by)) / d
    uy = ((ax*ax + ay*ay) * (cx - bx) + (bx*bx + by*by) * (ax - cx) + (cx*cx + cy*cy) * (bx - ax)) / d
    return (ux, uy, math.hypot(ax - ux, ay - uy))


def triangulate(points):
    big = [(-1000.0, -1000.0), (1000.0, -1000.0), (0.0, 1000.0)]
    tris = [tuple(big)]
    for p in points:
        bad, edges = [], []
        for t in tris:
            cc = circumcircle(*t)
            if cc and math.hypot(p[0] - cc[0], p[1] - cc[1]) <= cc[2] + 1e-9:
                bad.append(t)
        for t in bad:
            for e in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
                edges.append(e)
        # рёбра, встречающиеся один раз, образуют полость
        hole = []
        for e in edges:
            if sum(1 for f in edges if f == e or f == (e[1], e[0])) == 1:
                hole.append(e)
        tris = [t for t in tris if t not in bad]
        for e in hole:
            tris.append((e[0], e[1], p))
    return [t for t in tris if not any(v in big for v in t)]


tris = triangulate(pts)

# выкидываем треугольники, чей центр вне овала
def inside(p):
    return ((p[0] - CX) / (RX * 1.02)) ** 2 + ((p[1] - CY) / (RY * 1.02)) ** 2 <= 1.0

keep = []
for t in tris:
    c = (sum(v[0] for v in t) / 3.0, sum(v[1] for v in t) / 3.0)
    if inside(c):
        keep.append(t)

# уникальные рёбра
edges = set()
for t in keep:
    for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
        edges.add(tuple(sorted([a, b])))

f = lambda v: ('%.1f' % v).rstrip('0').rstrip('.')
d = ''.join('M%s %sL%s %s' % (f(a[0]), f(a[1]), f(b[0]), f(b[1])) for a, b in sorted(edges))
dots = ''.join('<circle cx="%s" cy="%s" r="1.7"/>' % (f(p[0]), f(p[1])) for p in pts)

print('точек:', len(pts), '| треугольников:', len(keep), '| рёбер:', len(edges))
print('длина path:', len(d))
io.open('mesh_out.txt', 'w', encoding='utf-8').write(d + '\n@@@\n' + dots)

html = ('<style>body{background:#080a08;margin:0;padding:24px}svg{background:#101410;'
        'border:1px solid #2a2f28;border-radius:14px}</style>'
        '<svg width="380" height="380" viewBox="0 0 200 200">'
        '<path d="%s" fill="none" stroke="rgba(181,244,45,.30)" stroke-width=".7"/>'
        '<g fill="#b5f42d">%s</g></svg>' % (d, dots))
io.open('mesh.html', 'w', encoding='utf-8').write(html)
