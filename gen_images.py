#!/usr/bin/env python3
"""Generate SVG diagrams for math_game puzzles and add image fields to JSON files."""
import os, json, math

BASE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(BASE, 'puzzles', 'images')
os.makedirs(OUT, exist_ok=True)

W, H = 240, 200

# ── Color palette (dark-theme) ───────────────────────────────
SK = "#9daacc"                    # shape stroke
LB = "#c8d0e8"                    # label text
AC = "#5c8aff"                    # accent blue
FI = "rgba(92,138,255,0.13)"      # shape fill
OG = "#f0a033"                    # orange highlight
DM = "#445566"                    # dim / grid lines
FI2 = "rgba(240,160,51,0.18)"    # orange fill

# ── SVG primitives ───────────────────────────────────────────
def hdr():
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">'

def ftr():
    return '</svg>'

def tx(x, y, s, col=LB, sz=11, anch="middle", fw="normal"):
    return (f'<text x="{x:.0f}" y="{y:.0f}" fill="{col}" font-size="{sz}" '
            f'text-anchor="{anch}" font-family="sans-serif" font-weight="{fw}">{s}</text>')

def ln(x1, y1, x2, y2, col=SK, w=1.5, dash=""):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
            f'stroke="{col}" stroke-width="{w}"{da}/>')

def ci(cx, cy, r, fi="none", col=SK, w=1.5):
    return (f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" '
            f'fill="{fi}" stroke="{col}" stroke-width="{w}"/>')

def pg(pts, fi=FI, col=SK, w=1.5):
    p = " ".join(f"{x:.0f},{y:.0f}" for x, y in pts)
    return f'<polygon points="{p}" fill="{fi}" stroke="{col}" stroke-width="{w}"/>'

def pl(pts, col=SK, w=1.5, dash=""):
    p = " ".join(f"{x:.0f},{y:.0f}" for x, y in pts)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<polyline points="{p}" fill="none" stroke="{col}" stroke-width="{w}"{da}/>'

def arc_seg(cx, cy, r, a1, a2, col=OG, w=1.5, fi="none"):
    """Arc from a1 to a2 degrees (math convention: CCW, y-up). sweep=0=CCW in SVG."""
    ra1, ra2 = math.radians(a1), math.radians(a2)
    x1 = cx + r * math.cos(ra1); y1 = cy - r * math.sin(ra1)
    x2 = cx + r * math.cos(ra2); y2 = cy - r * math.sin(ra2)
    span = (a2 - a1) % 360
    lg = 1 if span > 180 else 0
    return (f'<path d="M{x1:.0f},{y1:.0f} A{r:.0f},{r:.0f} 0 {lg},0 {x2:.0f},{y2:.0f}" '
            f'fill="{fi}" stroke="{col}" stroke-width="{w}"/>')

def sector_path(cx, cy, r, a_deg, fi=FI2, col=OG, w=1.5):
    """Filled sector from 0° to a_deg (CCW)."""
    a_rad = math.radians(a_deg)
    ex = cx + r * math.cos(a_rad); ey = cy - r * math.sin(a_rad)
    lg = 1 if a_deg > 180 else 0
    d = f"M{cx:.0f},{cy:.0f} L{cx+r:.0f},{cy:.0f} A{r:.0f},{r:.0f} 0 {lg},0 {ex:.0f},{ey:.0f} Z"
    return f'<path d="{d}" fill="{fi}" stroke="{col}" stroke-width="{w}"/>'

def pth(d, fi="none", col=SK, w=1.5):
    return f'<path d="{d}" fill="{fi}" stroke="{col}" stroke-width="{w}"/>'

def ra_mark(x, y, sz=7):
    """Right-angle marker at (x,y): one leg right (+x), one leg up (-y in SVG)."""
    return pl([(x, y-sz), (x+sz, y-sz), (x+sz, y)], col=AC, w=1.5)

def save(name, parts):
    content = hdr() + "".join(parts) + ftr()
    with open(os.path.join(OUT, name), 'w') as f:
        f.write(content)

# ── Hover-hotspot helpers ────────────────────────────────────
def hs(label, *parts):
    """Wrap SVG elements in a named hotspot group (data-label triggers JS tooltip)."""
    return f'<g data-label="{label}" style="cursor:crosshair">{"".join(parts)}</g>'

def hitln(x1, y1, x2, y2, w=14):
    """Transparent wide line — makes thin strokes easy to hover over."""
    return (f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
            f'stroke="transparent" stroke-width="{w}"/>')

def hitring(cx, cy, r, w=14):
    """Transparent ring hit area around a circle arc."""
    return (f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" '
            f'fill="none" stroke="transparent" stroke-width="{w}"/>')

def hitdot(cx, cy, r=16):
    """Transparent filled circle — makes a dot / point easy to hover over."""
    return f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="transparent"/>'

def pt(mx, my, ox, oy, sx, sy):
    """Math coords to SVG coords."""
    return (ox + mx*sx, oy - my*sy)

# ════════════════════════════════════════════════════════════
# GEOMETRY SHAPES
# ════════════════════════════════════════════════════════════

def right_triangle(a, b, c, label_a=None, label_b=None, label_c=None):
    sc = min(110/max(a,b), 13)
    pw = a*sc; ph = b*sc
    x0 = (W-pw)/2; y0 = H/2+ph/2
    x1 = x0+pw; y1 = y0
    x2 = x0;   y2 = y0-ph
    la = label_a or f'a={a}'
    lb = label_b or f'b={b}'
    lc = label_c or f'c={c}'
    mx = (x1+x2)/2; my = (y1+y2)/2
    return [pg([(x0,y0),(x1,y1),(x2,y2)]), ra_mark(x0,y0),
            tx((x0+x1)/2, y0+16, la), tx(x0-18, (y0+y2)/2, lb, anch="end"),
            tx(mx+16, my, lc)]

def square_shape(s):
    side = min(120, s*15)
    x0 = (W-side)/2; y0 = (H-side)/2
    return [pg([(x0,y0),(x0+side,y0),(x0+side,y0+side),(x0,y0+side)]),
            tx(W/2, y0-9, f's = {s}'),
            pl([(x0+7,y0),(x0+7,y0+7),(x0,y0+7)], col=DM, w=1),
            pl([(x0+side-7,y0),(x0+side-7,y0+7),(x0+side,y0+7)], col=DM, w=1)]

def rect_shape(l, w):
    sc = min(120/l, 80/w, 13)
    rw = l*sc; rh = w*sc
    x0 = (W-rw)/2; y0 = (H-rh)/2
    return [pg([(x0,y0),(x0+rw,y0),(x0+rw,y0+rh),(x0,y0+rh)]),
            tx(W/2, y0-9, f'l = {l}'), tx(x0-9, H/2, f'w = {w}', anch="end")]

def triangle_bh(b, h):
    sc = min(110/b, 90/h, 12)
    bw = b*sc; bh = h*sc
    x0 = (W-bw)/2; y0 = H/2+bh/2
    ax = x0+bw*0.38; ay = y0-bh
    return [pg([(x0,y0),(x0+bw,y0),(ax,ay)]),
            ln(ax, ay, ax, y0, col=AC, w=1.2, dash="4,3"),
            tx((x0+x0+bw)/2, y0+16, f'b = {b}'),
            tx(ax-13, (y0+ay)/2, f'h = {h}', anch="end"),
            pl([(ax-5,y0),(ax-5,y0-5),(ax,y0-5)], col=AC, w=1.2)]

def triangle_angles_shape(a1, a2, a3, labels=None):
    x0,y0 = 32,170; x1,y1 = 208,170; x2,y2 = 100,50
    la = labels or [f'{a1}°', f'{a2}°', f'{a3}°']
    return [pg([(x0,y0),(x1,y1),(x2,y2)]),
            arc_seg(x0,y0,20, 0, a1, col=OG, w=1.3),
            arc_seg(x1,y1,20, 180-a2, 180, col=OG, w=1.3),
            arc_seg(x2,y2,18, 250, 250+a3, col=OG, w=1.3),
            tx(x0+14, y0-14, la[0], sz=10, col=OG),
            tx(x1-14, y1-14, la[1], sz=10, col=OG, anch="end"),
            tx(x2, y2-13, la[2], sz=10, col=OG)]

def triangle_angle_sum():
    x0,y0 = 32,170; x1,y1 = 208,170; x2,y2 = 100,50
    return [pg([(x0,y0),(x1,y1),(x2,y2)]),
            arc_seg(x0,y0,20, 0, 55, col=OG, w=1.3),
            arc_seg(x1,y1,20, 115, 180, col=OG, w=1.3),
            arc_seg(x2,y2,18, 245, 305, col=OG, w=1.3),
            tx(W/2, H-8, 'A + B + C = 180°', col=LB, sz=11)]

def circle_shape(r_val, label="r", extra=""):
    cr = 65; cx,cy = W/2,H/2
    return [ci(cx,cy,cr), ci(cx,cy,2,fi=AC,col=AC),
            ln(cx,cy, cx+cr,cy, col=AC, w=1.5),
            tx(cx+cr/2, cy-9, f'{label} = {r_val}', col=AC),
            tx(cx, cy+cr+16, extra, sz=10)] if extra else \
           [ci(cx,cy,cr), ci(cx,cy,2,fi=AC,col=AC),
            ln(cx,cy, cx+cr,cy, col=AC, w=1.5),
            tx(cx+cr/2, cy-9, f'{label} = {r_val}', col=AC)]

def cube_shape(s, label=""):
    side = 58; dx,dy = 38,-20
    x0,y0 = 55,155
    ff = [(x0,y0),(x0+side,y0),(x0+side,y0-side),(x0,y0-side)]
    rf = [(x0+side,y0),(x0+side+dx,y0+dy),(x0+side+dx,y0+dy-side),(x0+side,y0-side)]
    tf = [(x0,y0-side),(x0+side,y0-side),(x0+side+dx,y0+dy-side),(x0+dx,y0+dy-side)]
    return [pg(ff),pg(rf),pg(tf),
            tx(x0+side/2, y0+16, label or f's = {s}', sz=11)]

def box_shape(l, w, h):
    sc = 55/max(l,w,h)
    fl=l*sc; fw=w*sc; fh=h*sc
    dx=fw*0.65; dy=-fw*0.32
    x0=(W-fl-dx)/2; y0=H/2+fh/2-dy/2
    ff=[(x0,y0),(x0+fl,y0),(x0+fl,y0-fh),(x0,y0-fh)]
    rf=[(x0+fl,y0),(x0+fl+dx,y0+dy),(x0+fl+dx,y0+dy-fh),(x0+fl,y0-fh)]
    tf=[(x0,y0-fh),(x0+fl,y0-fh),(x0+fl+dx,y0+dy-fh),(x0+dx,y0+dy-fh)]
    return [pg(ff),pg(rf),pg(tf),
            tx(x0+fl/2, y0+14, f'l={l}', sz=10),
            tx(x0+fl+dx/2+10, y0+dy/2, f'w={w}', sz=10, anch="start"),
            tx(x0-7, y0-fh/2, f'h={h}', anch="end", sz=10)]

def cone_shape(r, h):
    sc = min(80/h, 55/r)
    rr=r*sc; rh=h*sc
    cx=W/2; by=H/2+rh/2; ty=by-rh
    ry=10
    return [pth(f"M{cx-rr:.0f},{by:.0f} A{rr:.0f},{ry} 0 1,0 {cx+rr:.0f},{by:.0f}", fi=FI, col=SK),
            pth(f"M{cx-rr:.0f},{by:.0f} A{rr:.0f},{ry} 0 0,0 {cx+rr:.0f},{by:.0f}", fi="none", col=DM, w=1),
            ln(cx-rr,by, cx,ty), ln(cx+rr,by, cx,ty),
            ln(cx,ty, cx,by, col=AC, dash="4,3", w=1.2),
            tx(cx+8,(by+ty)/2, f'h={h}', anch="start", sz=10),
            ln(cx,by+ry, cx+rr,by+ry, col=AC, w=1.2),
            tx(cx+rr/2, by+ry+13, f'r={r}', sz=10)]

def sphere_shape(r=None):
    cx,cy,cr = W/2,H/2,68
    lbl = f'r = {r}' if r else ''
    return [ci(cx,cy,cr),
            pth(f"M{cx-cr:.0f},{cy:.0f} A{cr:.0f},25 0 1,0 {cx+cr:.0f},{cy:.0f}", fi="none", col=SK, w=1),
            pth(f"M{cx-cr:.0f},{cy:.0f} A{cr:.0f},25 0 0,0 {cx+cr:.0f},{cy:.0f}", fi="none", col=DM, w=1),
            ci(cx,cy,2,fi=AC,col=AC),
            ln(cx,cy, cx+cr,cy, col=AC, w=1.5),
            tx(cx+cr/2, cy-9, lbl, col=AC, sz=10)]

def cylinder_shape(r, h):
    sc = min(60/h, 45/r)
    rr=r*sc; rh=h*sc
    cx=W/2; ty=H/2-rh/2; by=H/2+rh/2; ry=11
    return [pg([(cx-rr,ty),(cx+rr,ty),(cx+rr,by),(cx-rr,by)], fi=FI),
            pth(f"M{cx-rr:.0f},{ty:.0f} A{rr:.0f},{ry} 0 1,0 {cx+rr:.0f},{ty:.0f}", fi=FI, col=SK),
            pth(f"M{cx-rr:.0f},{ty:.0f} A{rr:.0f},{ry} 0 0,0 {cx+rr:.0f},{ty:.0f}", fi="none", col=SK),
            pth(f"M{cx-rr:.0f},{by:.0f} A{rr:.0f},{ry} 0 1,0 {cx+rr:.0f},{by:.0f}", fi=FI, col=SK),
            pth(f"M{cx-rr:.0f},{by:.0f} A{rr:.0f},{ry} 0 0,0 {cx+rr:.0f},{by:.0f}", fi="none", col=DM, w=1),
            ln(cx+rr+8,ty, cx+rr+8,by, col=AC, w=1.2),
            tx(cx+rr+20, H/2, f'h={h}', anch="start", sz=10),
            ln(cx,by+ry, cx+rr,by+ry, col=AC, w=1.2),
            tx(cx+rr/2, by+ry+13, f'r={r}', sz=10)]

def hexagon_shape():
    cx,cy,r = W/2,H/2,65
    pts = [(cx+r*math.cos(math.radians(i*60-30)), cy+r*math.sin(math.radians(i*60-30))) for i in range(6)]
    parts = [pg(pts)]
    for i in range(6):
        px = cx+(r+20)*math.cos(math.radians(i*60-30))
        py = cy+(r+20)*math.sin(math.radians(i*60-30))
        parts.append(tx(px, py, '120°', sz=8, col=OG))
    return parts

def rhombus_shape(d1, d2):
    sc = min(90/d1, 80/d2, 10)
    rw=d1*sc/2; rh=d2*sc/2
    cx,cy = W/2,H/2
    return [pg([(cx,cy-rh),(cx+rw,cy),(cx,cy+rh),(cx-rw,cy)]),
            ln(cx-rw,cy, cx+rw,cy, col=AC, w=1.8),
            ln(cx,cy-rh, cx,cy+rh, col=AC, w=1.8),
            tx(cx+rw/2, cy-9, f'd₁={d1}', col=AC, sz=10),
            tx(cx+9, cy-rh/2, f'd₂={d2}', col=AC, sz=10, anch="start")]

def trapezoid_shape(b1, b2, h):
    sc = min(130/b2, 90/h, 11)
    tw=b1*sc; bw=b2*sc; rh=h*sc
    cx=W/2
    x0=cx-bw/2; y0=H/2+rh/2
    off = (bw-tw)/2
    x3=x0+off; y3=y0-rh; x2=x3+tw; y2=y3
    return [pg([(x0,y0),(x0+bw,y0),(x2,y2),(x3,y3)]),
            tx((x0+x0+bw)/2, y0+16, f'b₂={b2}'), tx((x2+x3)/2, y2-9, f'b₁={b1}'),
            ln(cx,y0, cx,y2, col=AC, dash="4,3", w=1.2),
            tx(cx+9, H/2, f'h={h}', anch="start", sz=10),
            pl([(cx-4,y0),(cx-4,y0-5),(cx,y0-5)], col=AC, w=1.2)]

def equilateral_shape(s):
    hh = s*math.sqrt(3)/2
    sc = min(110/s, 90/hh, 12)
    sw=s*sc; sh=hh*sc
    cy = H/2+sh*0.1; yb=cy+sh/2
    x0=W/2-sw/2; x1=W/2+sw/2
    return [pg([(x0,yb),(x1,yb),(W/2,yb-sh)]),
            tx(W/2, yb+16, f's = {s}'),
            tx(x0-13, yb-sh/2, f's = {s}', anch="end"),
            tx(x1+13, yb-sh/2, f's = {s}', anch="start")]

def sas_triangle(a, b, C_deg):
    C = math.radians(C_deg)
    sc = 90/max(a,b)
    bsc=b*sc; asc=a*sc
    cx,cy = W/2,H/2+20
    P0=(cx-bsc/2, cy); P1=(cx+bsc/2, cy)
    P2=(P0[0]+asc*math.cos(C), P0[1]-asc*math.sin(C))
    return [pg([P0,P1,P2]),
            arc_seg(P0[0],P0[1], 24, 0, C_deg, col=OG, w=1.3),
            tx(P0[0]+30, P0[1]-12, f'C={C_deg}°', sz=10, col=OG),
            tx((P0[0]+P1[0])/2, P0[1]+16, f'b={b}'),
            tx((P0[0]+P2[0])/2-14, (P0[1]+P2[1])/2, f'a={a}', anch="end")]

def rect_diagonal(l, w):
    sc = min(120/l, 80/w, 12)
    rw=l*sc; rh=w*sc
    x0=(W-rw)/2; y0=(H-rh)/2
    return [pg([(x0,y0),(x0+rw,y0),(x0+rw,y0+rh),(x0,y0+rh)]),
            ln(x0,y0+rh, x0+rw,y0, col=OG, w=2),
            tx(W/2, y0+rh+16, f'l={l}'),
            tx(x0-9, H/2, f'w={w}', anch="end"),
            tx((x0+x0+rw)/2+12, (y0+rh+y0)/2-8, 'd=?', col=OG, sz=10)]

def circle_arc_shape(r, angle_deg):
    cx,cy,cr = W/2,H/2,68
    ex = cx+cr*math.cos(math.radians(angle_deg))
    ey = cy-cr*math.sin(math.radians(angle_deg))
    return [ci(cx,cy,cr),
            arc_seg(cx,cy,cr, 0,angle_deg, col=OG, w=3.5),
            ln(cx,cy, cx+cr,cy, col=SK, w=1.2),
            ln(cx,cy, ex,ey, col=SK, w=1.2),
            arc_seg(cx,cy,22, 0,angle_deg, col=AC, w=1.3),
            tx(cx+30, cy-10, f'θ={angle_deg}°', col=AC, sz=10),
            tx(cx+cr/2, cy+16, f'r={r}', sz=10),
            ci(cx,cy,2,fi=AC,col=AC)]

def circle_sector_shape(r, angle_deg):
    cx,cy,cr = W/2,H/2,68
    ex = cx+cr*math.cos(math.radians(angle_deg))
    ey = cy-cr*math.sin(math.radians(angle_deg))
    return [ci(cx,cy,cr),
            sector_path(cx,cy,cr, angle_deg),
            ln(cx,cy, cx+cr,cy, col=SK, w=1.2),
            ln(cx,cy, ex,ey, col=SK, w=1.2),
            arc_seg(cx,cy,22, 0,angle_deg, col=AC, w=1.3),
            tx(cx+30, cy-12, f'θ={angle_deg}°', col=AC, sz=10),
            tx(cx+cr/2+5, cy+16, f'r={r}', sz=10),
            ci(cx,cy,2,fi=AC,col=AC)]

def pyramid_shape(s, h):
    sc = min(70/s, 70/h, 10)
    bs=s*sc; bh=h*sc
    cx,cy = W/2, H/2
    bx0=cx-bs/2; by0=cy+bh/2
    bpts=[(bx0,by0),(bx0+bs,by0),(bx0+bs+22,by0-16),(bx0+22,by0-16)]
    ax,ay = cx+11, by0-bh
    return [pg(bpts),
            pg([(bx0,by0),(bx0+bs,by0),(ax,ay)]),
            pg([(bx0+bs,by0),(bx0+bs+22,by0-16),(ax,ay)], fi="rgba(92,138,255,0.07)"),
            ln(ax,ay, ax,by0-10, col=AC, dash="4,3", w=1.2),
            pl([(ax-4,by0-10),(ax-4,by0-15),(ax,by0-15)], col=AC, w=1),
            tx(ax+9, (ay+by0)/2, f'h={h}', anch="start", sz=10),
            tx(cx, by0+14, f's={s}', sz=10)]

# ════════════════════════════════════════════════════════════
# TRIGONOMETRY SHAPES
# ════════════════════════════════════════════════════════════

def unit_circle_shape(angle_deg, extra_label="", multi_pts=None):
    cr=70; cx=120; cy=103
    r_ang = math.radians(angle_deg)
    px = cx+cr*math.cos(r_ang); py = cy-cr*math.sin(r_ang)
    LABELS = {0:"cos=1  sin=0", 30:"cos=√3/2  sin=1/2", 45:"cos=√2/2  sin=√2/2",
              60:"cos=1/2  sin=√3/2", 90:"cos=0  sin=1", 120:"cos=-1/2  sin=√3/2",
              135:"cos=-√2/2  sin=√2/2", 150:"cos=-√3/2  sin=1/2",
              180:"cos=-1  sin=0"}
    SIN = {0:"0", 30:"1/2", 45:"√2/2", 60:"√3/2", 90:"1", 120:"√3/2", 135:"√2/2", 150:"1/2", 180:"0"}
    COS = {0:"1", 30:"√3/2", 45:"√2/2", 60:"1/2", 90:"0", 120:"-1/2", 135:"-√2/2", 150:"-√3/2", 180:"-1"}
    sin_lbl = SIN.get(angle_deg, "sin θ")
    cos_lbl = COS.get(angle_deg, "cos θ")
    lbl = extra_label or LABELS.get(angle_deg, f'{angle_deg}°')
    parts = [
        # Axes
        hs("x-axis",
            ln(cx-cr-15,cy, cx+cr+15,cy, col=DM, w=1),
            tx(cx+cr+17, cy+4, 'x', col=DM, sz=9),
            hitln(cx-cr-15,cy, cx+cr+15,cy, 10)),
        hs("y-axis",
            ln(cx,cy+cr+15, cx,cy-cr-15, col=DM, w=1),
            tx(cx+4, cy-cr-16, 'y', col=DM, sz=9),
            hitln(cx,cy+cr+15, cx,cy-cr-15, 10)),
        # Unit circle
        hs("Unit circle — radius = 1",
            ci(cx,cy,cr),
            hitring(cx,cy,cr, 16)),
        # Angle arc
        hs(f"Angle θ = {angle_deg}°",
            arc_seg(cx,cy, 22, 0, angle_deg, col=OG, w=1.5),
            tx(cx+32, cy-10, f'{angle_deg}°', col=OG, sz=10),
            hitdot(cx, cy, 32)),
        # Unit radius (hypotenuse)
        hs("Radius = 1  (hypotenuse of right triangle)",
            ln(cx,cy, px,py, col=AC, w=2.2),
            hitln(cx,cy, px,py, 12)),
        # sin line — vertical dashed
        hs(f"sin θ = {sin_lbl}  (vertical leg — distance from point to x-axis)",
            ln(px,py, px,cy, col=AC, w=1, dash="4,3"),
            hitln(px,py, px,cy, 12)),
        # cos line — horizontal dashed
        hs(f"cos θ = {cos_lbl}  (horizontal leg — distance from point to y-axis)",
            ln(px,py, cx,py, col=AC, w=1, dash="4,3"),
            hitln(px,py, cx,py, 12)),
        # Point on circle
        hs(f"Point (cos θ, sin θ) = ({cos_lbl}, {sin_lbl})",
            ci(px,py, 4.5, fi=OG, col=OG, w=0),
            hitdot(px, py, 12)),
        ci(cx,cy, 2, fi=AC, col=AC),
        tx(cx, cy+cr+18, lbl, sz=9),
    ]
    if multi_pts:
        for ang, col in multi_pts:
            ra = math.radians(ang)
            qx = cx+cr*math.cos(ra); qy = cy-cr*math.sin(ra)
            parts.append(ci(qx,qy, 4, fi=col, col=col, w=0))
    return parts

def trig_30_60_90_shape():
    x0,y0 = 48,165; x1,y1 = 192,165; x2,y2 = 48,80
    return [pg([(x0,y0),(x1,y1),(x2,y2)]),
            ra_mark(x0,y0),
            arc_seg(x1,y1, 22, 148,180, col=OG, w=1.3),
            arc_seg(x2,y2, 18, 270,300, col=OG, w=1.3),
            tx((x0+x1)/2, y0+16, '√3'),
            tx(x0-16, (y0+y2)/2, '1', anch="end"),
            tx((x1+x2)/2+22, (y1+y2)/2, '2'),
            tx(x1-26, y1-15, '30°', sz=10, col=OG),
            tx(x2+20, y2+26, '60°', sz=10, col=OG),
            # Hotspot overlays
            hs("Adjacent leg = √3  (bottom, opposite the 60° angle)", hitln(x0,y0,x1,y1)),
            hs("Opposite leg = 1  (left side, opposite the 30° angle)", hitln(x0,y0,x2,y2)),
            hs("Hypotenuse = 2  (longest side)", hitln(x1,y1,x2,y2)),
            hs("30° angle", hitdot(x1,y1, 26)),
            hs("60° angle", hitdot(x2,y2, 22)),
            hs("90° right angle", hitdot(x0,y0, 18))]

def trig_45_45_90_shape():
    x0,y0 = 55,165; x1,y1 = 185,165; x2,y2 = 55,35
    return [pg([(x0,y0),(x1,y1),(x2,y2)]),
            ra_mark(x0,y0),
            arc_seg(x1,y1, 22, 145,180, col=OG, w=1.3),
            arc_seg(x2,y2, 18, 270,315, col=OG, w=1.3),
            tx((x0+x1)/2, y0+16, '1'),
            tx(x0-16, (y0+y2)/2, '1', anch="end"),
            tx((x1+x2)/2+24, (y1+y2)/2, '√2'),
            tx(x1-26, y1-16, '45°', sz=10, col=OG),
            tx(x2+20, y2+28, '45°', sz=10, col=OG),
            # Hotspot overlays
            hs("Adjacent leg = 1  (bottom)", hitln(x0,y0,x1,y1)),
            hs("Opposite leg = 1  (left side)", hitln(x0,y0,x2,y2)),
            hs("Hypotenuse = √2  (longest side)", hitln(x1,y1,x2,y2)),
            hs("45° angle", hitdot(x1,y1, 26)),
            hs("45° angle", hitdot(x2,y2, 22)),
            hs("90° right angle", hitdot(x0,y0, 18))]

def trig_labeled_shape():
    x0,y0 = 48,165; x1,y1 = 192,165; x2,y2 = 48,70
    return [pg([(x0,y0),(x1,y1),(x2,y2)]),
            ra_mark(x0,y0),
            arc_seg(x1,y1, 24, 148,180, col=OG, w=1.3),
            tx((x0+x1)/2, y0+16, 'adjacent', sz=9),
            tx(x0-9, (y0+y2)/2, 'opposite', anch="end", sz=9),
            tx((x1+x2)/2+32, (y1+y2)/2, 'hypotenuse', sz=9),
            tx(x1-24, y1-17, 'θ', sz=13, col=OG, fw="bold"),
            # Hotspot overlays
            hs("Adjacent side — the leg next to angle θ (base)", hitln(x0,y0,x1,y1)),
            hs("Opposite side — the leg across from angle θ", hitln(x0,y0,x2,y2)),
            hs("Hypotenuse — the longest side, opposite the right angle", hitln(x1,y1,x2,y2)),
            hs("Angle θ — the reference angle for sin, cos, tan", hitdot(x1,y1, 28)),
            hs("90° right angle", hitdot(x0,y0, 18))]

def trig_3_4_5_shape():
    a,b,c = 4,3,5
    sc = min(110/max(a,b), 13)
    pw = a*sc; ph = b*sc
    x0 = (W-pw)/2; y0 = H/2+ph/2
    x1 = x0+pw; y1 = y0; x2 = x0; y2 = y0-ph
    return [pg([(x0,y0),(x1,y1),(x2,y2)]), ra_mark(x0,y0),
            tx((x0+x1)/2, y0+16, 'adj=4'),
            tx(x0-18, (y0+y2)/2, 'opp=3', anch="end"),
            tx((x1+x2)/2+16, (y1+y2)/2, 'hyp=5'),
            # Hotspot overlays
            hs("Adjacent leg = 4  (base, next to the reference angle)", hitln(x0,y0,x1,y1)),
            hs("Opposite leg = 3  (vertical side, across from reference angle)", hitln(x0,y0,x2,y2)),
            hs("Hypotenuse = 5  (longest side;  3² + 4² = 5²)", hitln(x1,y1,x2,y2)),
            hs("90° right angle", hitdot(x0,y0, 18))]

def trig_sec_shape():
    x0,y0 = 48,165; x1,y1 = 192,165; x2,y2 = 48,90
    return [pg([(x0,y0),(x1,y1),(x2,y2)]),
            ra_mark(x0,y0),
            arc_seg(x1,y1, 22, 148,180, col=OG, w=1.3),
            tx((x0+x1)/2, y0+16, 'adj'),
            tx(x0-9, (y0+y2)/2, 'opp', anch="end"),
            tx((x1+x2)/2+24, (y1+y2)/2, 'hyp'),
            tx(x1-26, y1-15, 'θ', sz=12, col=OG, fw="bold"),
            tx(W/2, 20, 'sec(θ) = hyp/adj = 1/cos(θ)', sz=9, col=LB),
            # Hotspot overlays
            hs("Adjacent (adj) — leg next to θ;  cos θ = adj/hyp", hitln(x0,y0,x1,y1)),
            hs("Opposite (opp) — leg across from θ;  sin θ = opp/hyp", hitln(x0,y0,x2,y2)),
            hs("Hypotenuse (hyp) — longest side;  sec θ = hyp/adj", hitln(x1,y1,x2,y2)),
            hs("Angle θ — reference angle;  sec θ = 1/cos θ", hitdot(x1,y1, 26)),
            hs("90° right angle", hitdot(x0,y0, 18))]

def trig_law_sines_shape(a, A_deg, B_deg):
    C_deg = 180 - A_deg - B_deg
    A = math.radians(A_deg); B = math.radians(B_deg); C = math.radians(C_deg)
    # Compute triangle using law of sines, side a opposite A
    b = a * math.sin(B) / math.sin(A)
    c = a * math.sin(C) / math.sin(A)
    sc = 90/max(a,b,c)
    # Place triangle: P0 at bottom-left, P1 at bottom-right (side c between them)
    csc = c*sc
    cx,cy = W/2,H/2+20
    P0 = (cx-csc/2, cy); P1 = (cx+csc/2, cy)
    P2 = (P0[0]+b*sc*math.cos(A), P0[1]-b*sc*math.sin(A))
    return [pg([P0,P1,P2]),
            arc_seg(P0[0],P0[1], 20, 0, A_deg, col=OG, w=1.3),
            arc_seg(P1[0],P1[1], 20, 180-B_deg, 180, col=OG, w=1.3),
            tx(P0[0]+26, P0[1]-12, f'A={A_deg}°', sz=10, col=OG),
            tx(P1[0]-26, P1[1]-12, f'B={B_deg}°', sz=10, col=OG, anch="end"),
            tx((P0[0]+P2[0])/2-16, (P0[1]+P2[1])/2, f'b=?', col=AC, anch="end", sz=11),
            tx((P0[0]+P1[0])/2, P0[1]+16, f'(c)', sz=10),
            tx((P1[0]+P2[0])/2+14, (P1[1]+P2[1])/2, f'a={a}', sz=10),
            # Hotspot overlays
            hs(f"Side b (unknown) — opposite angle B={B_deg}°;  b/sin B = a/sin A", hitln(P0[0],P0[1],P2[0],P2[1])),
            hs(f"Side c — opposite angle C={C_deg}°;  c/sin C = a/sin A", hitln(P0[0],P0[1],P1[0],P1[1])),
            hs(f"Side a = {a} — opposite angle A={A_deg}°", hitln(P1[0],P1[1],P2[0],P2[1])),
            hs(f"Angle A = {A_deg}°  (at left vertex)", hitdot(P0[0],P0[1], 26)),
            hs(f"Angle B = {B_deg}°  (at right vertex)", hitdot(P1[0],P1[1], 26))]

def sine_wave_shape(A, period_pi):
    ox,oy = 30,100; sx=170; sy=50
    pts = []
    for i in range(101):
        x = 2*math.pi * i/100
        svg_x = ox + x/(2*math.pi) * sx
        svg_y = oy - A/A * math.sin(2*math.pi/period_pi * x) * 45
        pts.append((svg_x, svg_y))
    return [
        hs("x-axis  (y = 0 baseline)",
            ln(ox,oy, ox+sx,oy, col=DM, w=1),
            hitln(ox,oy, ox+sx,oy, 10)),
        hs("y-axis",
            ln(ox,oy-55, ox,oy+55, col=DM, w=1),
            hitln(ox,oy-55, ox,oy+55, 10)),
        hs(f"Sine curve  y = {A}·sin(x / {period_pi}) — one complete period shown",
            pl(pts, col=OG, w=2)),
        hs(f"Amplitude = {A}  (peak height above x-axis)",
            ln(ox,oy-45, ox+6,oy-45, col=AC, w=1.2),
            tx(ox+22, oy-45, f'A={A}', col=AC, sz=10, anch="start"),
            hitln(ox,oy-45, ox+50,oy-45, 14)),
        hs(f"Period = {period_pi}π  (horizontal length of one full cycle)",
            tx(W/2, H-10, f'Period = {period_pi}π', sz=10, col=LB),
            hitdot(W/2, H-10, 40)),
    ]

# ════════════════════════════════════════════════════════════
# CALCULUS GRAPHS
# ════════════════════════════════════════════════════════════

def axes_shape(ox=120, oy=155, xr=85, yr=130):
    return [
        hs("x-axis  (horizontal axis — independent variable x)",
            ln(ox-xr,oy, ox+xr,oy, col=DM, w=1),
            pg([(ox+xr,oy-3),(ox+xr+8,oy),(ox+xr,oy+3)], fi=DM, col=DM, w=0),
            tx(ox+xr+12, oy+4, 'x', col=DM, sz=9),
            hitln(ox-xr,oy, ox+xr+8,oy, 10)),
        hs("y-axis  (vertical axis — dependent variable y = f(x))",
            ln(ox,oy+25, ox,oy-yr, col=DM, w=1),
            pg([(ox-3,oy-yr),(ox,oy-yr-8),(ox+3,oy-yr)], fi=DM, col=DM, w=0),
            tx(ox+4, oy-yr-10, 'y', col=DM, sz=9),
            hitln(ox,oy+25, ox,oy-yr, 10)),
    ]

def curve_pts(f, x_lo, x_hi, n=80):
    return [(x_lo + (x_hi-x_lo)*i/n, f(x_lo + (x_hi-x_lo)*i/n)) for i in range(n+1)]

def math_to_svg(pts, ox, oy, sx, sy, y_clip=None):
    result = []
    for mx, my in pts:
        sx_p = ox + mx*sx; sy_p = oy - my*sy
        if y_clip and sy_p < y_clip:
            sy_p = y_clip
        result.append((sx_p, sy_p))
    return result

def graph_power(n, tangent_at_x=1):
    ox,oy = 120,155; sx=22; sy=8 if n<=2 else 5
    if n==2: x_lo,x_hi = -3,3
    elif n==3: x_lo,x_hi = -2.7,2.7
    else: x_lo,x_hi = -2.3,2.3
    pts = curve_pts(lambda x: x**n, x_lo, x_hi)
    svg_pts = math_to_svg(pts, ox, oy, sx, sy, y_clip=oy-130)
    y0t = tangent_at_x**n
    slope = n * tangent_at_x**(n-1)
    tang_pts = [(tangent_at_x-1.5, y0t-slope*1.5), (tangent_at_x+1.5, y0t+slope*1.5)]
    t_svg = math_to_svg(tang_pts, ox, oy, sx, sy)
    dot_x = ox+tangent_at_x*sx; dot_y = oy-y0t*sy
    return axes_shape(ox,oy) + [
        hs(f"Curve y = x^{n} — power function",
            pl(svg_pts, col=OG, w=2.2)),
        hs(f"Tangent line at x={tangent_at_x}  (slope = {slope:.0f} = the derivative there)",
            pl(t_svg, col=AC, w=2),
            hitln(t_svg[0][0],t_svg[0][1],t_svg[-1][0],t_svg[-1][1], 12)),
        hs(f"Point ({tangent_at_x}, {y0t:.0f}) — where the tangent touches the curve",
            ci(dot_x,dot_y, 3.5, fi=OG, col=OG, w=0),
            hitdot(dot_x, dot_y, 14)),
        hs(f"Power rule: d/dx[x^{n}] = {n}·x^{n-1}",
            tx(W/2, 16, f"d/dx[x^{n}] = {n}x^{n-1}", sz=10, col=LB),
            hitdot(W/2, 16, 65)),
    ]

def graph_linear_fn(m, label=""):
    ox,oy = 120,140; sx=22; sy=10
    pts = [(-3, -3*m), (3, 3*m)]
    svg_pts = math_to_svg(pts, ox, oy, sx, sy)
    lbl = label or f"f(x) = {m}x"
    return axes_shape(ox,oy,xr=90,yr=120) + [
        hs(f"Line f(x) = {m}x — constant slope {m} everywhere",
            pl(svg_pts, col=OG, w=2.2),
            hitln(svg_pts[0][0],svg_pts[0][1],svg_pts[-1][0],svg_pts[-1][1], 12)),
        hs(f"Derivative = {m}  (the slope is constant — d/dx[{m}x] = {m})",
            tx(W/2, 16, lbl, sz=10, col=LB),
            hitdot(W/2, 16, 65)),
    ]

def graph_constant(c, label=""):
    ox,oy = 120,140; sy=10
    y_svg = oy - c*sy
    lbl = label or f"f(x) = {c}  →  derivative = 0"
    return axes_shape(ox,oy,xr=90,yr=120) + [
        hs(f"Horizontal line f(x) = {c} — slope is zero everywhere",
            ln(30, y_svg, 210, y_svg, col=OG, w=2.2),
            hitln(30, y_svg, 210, y_svg, 12)),
        hs("Derivative = 0  (constant functions never rise or fall)",
            tx(W/2, 16, lbl, sz=10, col=LB),
            hitdot(W/2, 16, 65)),
    ]

def graph_with_area(f, f_label, x_lo, x_hi, ox=50, oy=155, sx=None, sy=10, y_max=None):
    if sx is None:
        sx = min(150/(x_hi+0.5), 30)
    shade_pts = [(ox + x_lo*sx, oy)]
    n = 60
    for i in range(n+1):
        x = x_lo + (x_hi-x_lo)*i/n
        y = f(x)
        shade_pts.append((ox+x*sx, oy-y*sy))
    shade_pts.append((ox+x_hi*sx, oy))
    p = " ".join(f"{x:.0f},{y:.0f}" for x,y in shade_pts)
    curve_x_lo = 0; curve_x_hi = x_hi + 0.5
    full_pts = []
    for i in range(81):
        x = curve_x_lo + (curve_x_hi-curve_x_lo)*i/80
        full_pts.append((ox+x*sx, oy - min(f(x),y_max or 999)*sy))
    lx = ox+x_lo*sx; rx = ox+x_hi*sx
    return [
        hs("x-axis  (horizontal axis — independent variable x)",
            ln(ox-10,oy, ox+(x_hi+1)*sx,oy, col=DM, w=1),
            hitln(ox-10,oy, ox+(x_hi+1)*sx,oy, 10)),
        hs("y-axis  (vertical axis — dependent variable y = f(x))",
            ln(ox,oy+10, ox,oy-120, col=DM, w=1),
            hitln(ox,oy+10, ox,oy-120, 10)),
        hs(f"Shaded area = ∫ from {x_lo} to {x_hi} of {f_label} dx  (the definite integral)",
            f'<polygon points="{p}" fill="{FI2}" stroke="{OG}" stroke-width="1.5"/>'),
        hs(f"Curve f(x) = {f_label}  (the integrand — function being integrated)",
            pl(full_pts, col=OG, w=2)),
        hs(f"Left bound x = {x_lo}  (lower limit of integration)",
            ln(lx,oy, lx,oy-5, col=DM, w=1),
            tx(lx, oy+12, str(x_lo), sz=9, col=DM),
            hitln(lx,oy-5, lx,oy+12, 14)),
        hs(f"Right bound x = {x_hi}  (upper limit of integration)",
            ln(rx,oy, rx,oy-5, col=DM, w=1),
            tx(rx, oy+12, str(x_hi), sz=9, col=DM),
            hitln(rx,oy-5, rx,oy+12, 14)),
        hs(f"∫ {f_label} dx  (antiderivative — find a function whose derivative is {f_label})",
            tx(W/2, 16, f"∫ {f_label} dx", sz=11, col=LB),
            hitdot(W/2, 16, 60)),
    ]

def graph_limit(f, x_to, label, ox=120, oy=155, x_lo=-3, x_hi=3, sx=22, sy=8):
    pts = curve_pts(f, x_lo, x_hi)
    svg_pts = math_to_svg(pts, ox, oy, sx, sy, y_clip=oy-130)
    dot_x = ox+x_to*sx; dot_y = oy-f(x_to)*sy
    lim_val = f(x_to)
    return axes_shape(ox,oy) + [
        hs("Curve f(x)  (the function whose limit is being evaluated)",
            pl(svg_pts, col=OG, w=2.2)),
        hs(f"x → {x_to}  (vertical dashed line — x approaches this value from both sides)",
            ln(dot_x,oy, dot_x,dot_y, col=AC, w=1.5, dash="4,3"),
            tx(dot_x, oy+14, f'x→{x_to}', sz=9, col=AC),
            hitln(dot_x,oy, dot_x,dot_y, 14)),
        hs(f"Limit point — f(x) approaches {lim_val:.4g} as x → {x_to}",
            ci(dot_x,dot_y, 4, fi=OG, col=OG, w=0),
            hitdot(dot_x, dot_y, 14)),
        hs(f"Limit: {label}",
            tx(W/2, 16, label, sz=10, col=LB),
            hitdot(W/2, 16, 65)),
    ]

def graph_exp():
    ox,oy = 60,155; sx=22; sy=12
    pts = curve_pts(lambda x: math.exp(x), -2, 3)
    svg_pts = [(ox+mx*sx, max(oy-my*sy, 10)) for mx,my in pts]
    yi_x = ox; yi_y = oy - 1*sy  # y-intercept at (0, e^0=1)
    return axes_shape(ox,oy, xr=150, yr=140) + [
        hs("Curve f(x) = eˣ — grows without bound; always positive",
            pl(svg_pts, col=OG, w=2.2)),
        hs("y-intercept at (0, 1) — because e⁰ = 1",
            ci(yi_x, yi_y, 4, fi=AC, col=AC, w=0),
            hitdot(yi_x, yi_y, 14)),
        hs("d/dx[eˣ] = eˣ  (eˣ is its own derivative)",
            tx(W/2, 16, "f(x) = eˣ", sz=11, col=LB),
            hitdot(W/2, 16, 45)),
    ]

def graph_ln():
    ox,oy = 60,155; sx=22; sy=22
    pts = [(0.1+(3.5-0.1)*i/80, 0) for i in range(81)]
    pts = [(x, math.log(x)) for x,_ in pts]
    svg_pts = math_to_svg(pts, ox, oy, sx, sy, y_clip=oy-140)
    xi_x = ox+1*sx; xi_y = oy  # x-intercept at (1, 0)
    return axes_shape(ox,oy, xr=150, yr=140) + [
        hs("Curve f(x) = ln(x) — defined only for x > 0; negative for 0 < x < 1",
            pl(svg_pts, col=OG, w=2.2)),
        hs("x-intercept at (1, 0) — because ln(1) = 0",
            ci(xi_x, xi_y, 4, fi=AC, col=AC, w=0),
            hitdot(xi_x, xi_y, 14)),
        hs("d/dx[ln(x)] = 1/x  (inverse of eˣ)",
            tx(W/2, 16, "f(x) = ln(x)", sz=11, col=LB),
            hitdot(W/2, 16, 45)),
    ]

def graph_sinx():
    ox,oy = 40,110; sx=25; sy=45
    pts = curve_pts(lambda x: math.sin(x), -math.pi, 2*math.pi)
    svg_pts = math_to_svg(pts, ox, oy, sx, sy)
    t_pts = [(-0.8, -0.8), (0.8, 0.8)]
    t_svg = math_to_svg(t_pts, ox, oy, sx, sy)
    return axes_shape(ox,oy, xr=190, yr=80) + [
        hs("Curve y = sin(x) — oscillates between −1 and +1",
            pl(svg_pts, col=OG, w=2.2)),
        hs("Tangent at x=0  (slope = cos(0) = 1 — the steepest point)",
            pl(t_svg, col=AC, w=2),
            hitln(t_svg[0][0],t_svg[0][1],t_svg[-1][0],t_svg[-1][1], 12)),
        hs("Origin (0, 0) — sin(0) = 0; tangent touches here",
            ci(ox,oy, 3.5, fi=OG, col=OG, w=0),
            hitdot(ox, oy, 14)),
        hs("d/dx[sin(x)] = cos(x)  (derivative of sine is cosine)",
            tx(W/2, 16, "d/dx[sin(x)] = cos(x)", sz=10, col=LB),
            hitdot(W/2, 16, 65)),
    ]

def graph_sinx_area():
    ox,oy = 40,115; sx=28; sy=50
    pts = curve_pts(lambda x: math.sin(x), 0, math.pi)
    shade_pts = [(ox,oy)] + [(ox+x*sx, oy-math.sin(x)*sy) for x,_ in pts] + [(ox+math.pi*sx,oy)]
    p = " ".join(f"{x:.0f},{y:.0f}" for x,y in shade_pts)
    full_pts = curve_pts(lambda x: math.sin(x), -0.2, math.pi+0.2)
    svg_full = math_to_svg(full_pts, ox, oy, sx, sy)
    pi_x = ox+math.pi*sx
    return [
        hs("x-axis  (baseline — integral is area above this line)",
            ln(ox-10,oy, ox+130,oy, col=DM, w=1),
            hitln(ox-10,oy, ox+130,oy, 10)),
        hs("y-axis",
            ln(ox,oy+20, ox,oy-60, col=DM, w=1),
            hitln(ox,oy+20, ox,oy-60, 10)),
        hs("Shaded area = ∫₀^π sin(x) dx = 2  (one full arch above x-axis)",
            f'<polygon points="{p}" fill="{FI2}" stroke="{OG}" stroke-width="1.5"/>'),
        hs("Curve y = sin(x)",
            pl(svg_full, col=OG, w=2.2)),
        hs("Left bound x = 0  (sin starts at zero here)",
            hitdot(ox, oy, 12)),
        hs("Right bound x = π  (sin returns to zero at π)",
            hitdot(pi_x, oy, 12)),
        hs("∫ sin(x) dx = −cos(x) + C  (antiderivative of sin is −cos)",
            tx(W/2, 16, "∫ sin(x) dx = −cos(x) + C", sz=10, col=LB),
            hitdot(W/2, 16, 65)),
    ]

def graph_1_over_x():
    ox,oy = 120,120; sx=22; sy=20
    pts_pos = curve_pts(lambda x: 1/x, 0.3, 3.5)
    pts_neg = curve_pts(lambda x: 1/x, -3.5, -0.3)
    s1 = math_to_svg(pts_pos, ox, oy, sx, sy, y_clip=oy-110)
    s2 = math_to_svg(pts_neg, ox, oy, sx, sy)
    s2 = [(x, max(y, oy-110)) for x,y in s2]
    return axes_shape(ox,oy) + [
        hs("f(x) = 1/x for x > 0  — positive, decreasing; approaches 0 as x→∞",
            pl(s1, col=OG, w=2.2)),
        hs("f(x) = 1/x for x < 0  — negative, increasing; vertical asymptote at x = 0",
            pl(s2, col=OG, w=2.2)),
        hs("f(x) = 1/x  — undefined at x = 0 (vertical asymptote);  d/dx[1/x] = −1/x²",
            tx(W/2, 16, "f(x) = 1/x", sz=11, col=LB),
            hitdot(W/2, 16, 45)),
    ]

def graph_1_over_x_area():
    ox,oy = 60,155; sx=38; sy=50
    pts = curve_pts(lambda x: 1/x, 1, math.e)
    shade_pts = [(ox+1*sx,oy)] + [(ox+x*sx, oy-y*sy) for x,y in pts] + [(ox+math.e*sx,oy)]
    p = " ".join(f"{x:.0f},{y:.0f}" for x,y in shade_pts)
    full_pts = curve_pts(lambda x: 1/x, 0.5, math.e+0.3)
    svg_full = math_to_svg(full_pts, ox, oy, sx, sy, y_clip=oy-130)
    lx = ox+1*sx; rx = ox+math.e*sx
    return [
        hs("x-axis  (horizontal axis)",
            ln(ox-10,oy, ox+(math.e+0.5)*sx,oy, col=DM, w=1),
            hitln(ox-10,oy, ox+(math.e+0.5)*sx,oy, 10)),
        hs("y-axis",
            ln(ox,oy+10, ox,oy-140, col=DM, w=1),
            hitln(ox,oy+10, ox,oy-140, 10)),
        hs("Shaded area = ∫₁ᵉ (1/x) dx = ln(e) − ln(1) = 1",
            f'<polygon points="{p}" fill="{FI2}" stroke="{OG}" stroke-width="1.5"/>'),
        hs("Curve f(x) = 1/x  (the integrand)",
            pl(svg_full, col=OG, w=2.2)),
        hs("Left bound x = 1  (lower limit of integration)",
            ln(lx,oy, lx,oy-6, col=DM, w=1),
            tx(lx, oy+12, '1', sz=9, col=DM),
            hitln(lx,oy-6, lx,oy+12, 14)),
        hs("Right bound x = e ≈ 2.718  (upper limit of integration)",
            ln(rx,oy, rx,oy-6, col=DM, w=1),
            tx(rx, oy+12, 'e', sz=9, col=DM),
            hitln(rx,oy-6, rx,oy+12, 14)),
        hs("∫₁ᵉ (1/x) dx = ln(e)−ln(1) = 1  (fundamental theorem of calculus)",
            tx(W/2, 16, "∫₁ᵉ (1/x) dx = ln(e)−ln(1) = 1", sz=9, col=LB),
            hitdot(W/2, 16, 65)),
    ]

def graph_sin_over_x():
    ox,oy = 120,130; sx=25; sy=80
    def f(x):
        return math.sin(x)/x if abs(x) > 0.001 else 1.0
    pts = [(x_lo/10, f(x_lo/10)) for x_lo in range(-35,36) if abs(x_lo) > 1] + [(0, 1)]
    pts.sort()
    svg_pts = math_to_svg(pts, ox, oy, sx, sy, y_clip=oy-110)
    lim_y = oy-sy
    return axes_shape(ox,oy) + [
        hs("Curve f(x) = sin(x)/x — oscillates and decays away from x=0",
            pl(svg_pts, col=OG, w=2.2)),
        hs("Limit value = 1  (filled dot — function approaches 1 from both sides as x→0)",
            ci(ox,lim_y, 4.5, fi=OG, col=OG, w=0),
            hitdot(ox, lim_y, 14)),
        hs("Removable discontinuity at x=0  (circle outline — sin(0)/0 is undefined, but limit = 1)",
            ci(ox,lim_y, 6.5, fi="none", col=AC, w=1.5),
            tx(ox+18, lim_y-8, 'limit=1', sz=10, col=AC),
            hitdot(ox, lim_y, 20)),
        hs("lim(sin x/x) as x→0 = 1  (a fundamental limit in calculus)",
            tx(W/2, 16, "lim(sinx/x) as x→0 = 1", sz=10, col=LB),
            hitdot(W/2, 16, 65)),
    ]

def graph_chain_rule():
    cpts = math_to_svg(curve_pts(lambda x: min((x**2+1)**3/30, 12), -2.5, 2.5), 120, 155, 22, 8, y_clip=15)
    return axes_shape() + [
        hs("Curve y = (x²+1)³  — outer function (cube) applied to inner function (x²+1)",
            pl(cpts, col=OG, w=2.2)),
        hs("Chain rule: d/dx[(x²+1)³] = 3(x²+1)²·2x  (outer' × inner')",
            tx(W/2, 16, "d/dx[(x²+1)³] = 3(x²+1)²·2x", sz=9, col=LB),
            hitdot(W/2, 16, 65)),
    ]

def graph_product_rule():
    cpts = math_to_svg(curve_pts(lambda x: x**2*math.sin(x), -3, 3), 120, 155, 22, 12, y_clip=10)
    return axes_shape() + [
        hs("Curve y = x²·sin(x)  — product of two functions: x² and sin(x)",
            pl(cpts, col=OG, w=2.2)),
        hs("Product rule: d/dx[x²sinx] = 2x sinx + x²cosx  (u'v + uv')",
            tx(W/2, 16, "d/dx[x²sinx] = 2x sinx + x²cosx", sz=9, col=LB),
            hitdot(W/2, 16, 65)),
    ]

def graph_quotient_rule():
    def f(x):
        if abs(math.sin(x)) < 0.3: return None
        return x**2/math.sin(x) if abs(x**2/math.sin(x)) < 8 else None
    pts = [(0.1*i-3, f(0.1*i-3)) for i in range(61) if f(0.1*i-3) is not None]
    if not pts: return axes_shape() + [tx(W/2, 100, 'x²/sin(x)', sz=11)]
    svg_pts = math_to_svg(pts, 120, 130, 22, 15)
    return axes_shape(120,130) + [
        hs("Curve y = x²/sin(x)  — quotient of two functions (undefined where sin(x) = 0)",
            pl(svg_pts, col=OG, w=2)),
        hs("Quotient rule: d/dx[x²/sinx] = (2x sinx − x²cosx)/sin²x  ((u'v − uv')/v²)",
            tx(W/2, 16, "d/dx[x²/sinx] = (2x sinx - x²cosx)/sin²x", sz=8, col=LB),
            hitdot(W/2, 16, 65)),
    ]

def graph_ibp():
    ox,oy = 60,155; sx=22; sy=18
    pts = curve_pts(lambda x: x*math.exp(x), 0, 2.5)
    shade_pts = [(ox,oy)] + [(ox+x*sx, max(oy-y*sy, 10)) for x,y in pts] + [(ox+2.5*sx,oy)]
    p = " ".join(f"{x:.0f},{y:.0f}" for x,y in shade_pts)
    svg_pts = [(ox+x*sx, max(oy-y*sy,10)) for x,y in pts]
    return [
        hs("x-axis  (horizontal axis)",
            ln(ox-10,oy, ox+80,oy, col=DM, w=1),
            hitln(ox-10,oy, ox+80,oy, 10)),
        hs("y-axis",
            ln(ox,oy+10, ox,oy-145, col=DM, w=1),
            hitln(ox,oy+10, ox,oy-145, 10)),
        hs("Shaded area = ∫₀^2.5 x·eˣ dx  (evaluated using integration by parts)",
            f'<polygon points="{p}" fill="{FI2}" stroke="none"/>'),
        hs("Curve f(x) = x·eˣ  — grows rapidly; faster than eˣ alone",
            pl(svg_pts, col=OG, w=2.2)),
        hs("∫ x eˣ dx = xeˣ − eˣ + C  (integration by parts: u=x, dv=eˣ dx)",
            tx(W/2, 16, "∫ x eˣ dx = xeˣ − eˣ + C", sz=10, col=LB),
            hitdot(W/2, 16, 65)),
    ]

def graph_ex_minus_1_x():
    ox,oy = 120,130; sx=30; sy=80
    def f(x):
        return (math.exp(x)-1)/x if abs(x) > 0.001 else 1.0
    pts = [(0.1*i-2.5, f(0.1*i-2.5)) for i in range(51)]
    svg_pts = math_to_svg(pts, ox, oy, sx, sy, y_clip=20)
    lim_y = oy-sy
    return axes_shape(ox,oy) + [
        hs("Curve f(x) = (eˣ−1)/x  — undefined at x=0; limit exists",
            pl(svg_pts, col=OG, w=2.2)),
        hs("Limit value = 1  (filled dot — (eˣ−1)/x → 1 as x→0)",
            ci(ox,lim_y, 4.5, fi=OG, col=OG, w=0),
            hitdot(ox, lim_y, 14)),
        hs("Removable discontinuity at x=0  (function undefined here, but limit = 1)",
            ci(ox,lim_y, 6.5, fi="none", col=AC, w=1.5),
            tx(ox+22, lim_y-8, 'limit=1', sz=10, col=AC),
            hitdot(ox, lim_y, 22)),
        hs("lim((eˣ−1)/x) as x→0 = 1  (related to the definition of e)",
            tx(W/2, 16, "lim((eˣ-1)/x) as x→0 = 1", sz=9, col=LB),
            hitdot(W/2, 16, 65)),
    ]

def graph_xx():
    ox,oy = 60,155; sx=30; sy=40
    pts = [(0.05*i, (0.05*i)**(0.05*i) if 0.05*i > 0 else 1) for i in range(1, 61)]
    svg_pts = [(ox+x*sx, oy-y*sy) for x,y in pts]
    return axes_shape(ox,oy, xr=170, yr=140) + [
        hs("Curve f(x) = xˣ  — defined for x > 0; minimum near x = 1/e ≈ 0.37",
            pl(svg_pts, col=OG, w=2.2)),
        hs("d/dx[xˣ] = xˣ(ln x + 1)  (use logarithmic differentiation)",
            tx(W/2, 16, "d/dx[xˣ] = xˣ(ln x + 1)", sz=10, col=LB),
            hitdot(W/2, 16, 65)),
    ]

def graph_sinx_cosx():
    ox,oy = 120,120; sx=28; sy=60
    pts = curve_pts(lambda x: math.sin(x)*math.cos(x), -math.pi, math.pi)
    svg_pts = math_to_svg(pts, ox, oy, sx, sy)
    return axes_shape(ox,oy) + [
        hs("Curve y = sin(x)·cos(x) = ½sin(2x)  — double-frequency sine wave",
            pl(svg_pts, col=OG, w=2.2)),
        hs("∫ sinx cosx dx = sin²x/2 + C  (use substitution u = sin x)",
            tx(W/2, 16, "∫ sinx cosx dx = sin²x/2 + C", sz=9, col=LB),
            hitdot(W/2, 16, 65)),
    ]

def graph_x4_poly():
    ox,oy = 120,155; sx=18; sy=5
    pts = curve_pts(lambda x: x**4 - 3*x**2 + 2, -2.3, 2.3)
    svg_pts = math_to_svg(pts, ox, oy, sx, sy, y_clip=15)
    return axes_shape(ox,oy) + [
        hs("Curve y = x⁴−3x²+2  — degree-4 polynomial with two local minima and one local max",
            pl(svg_pts, col=OG, w=2.2)),
        hs("y'' = 12x²−6 — second derivative; set to 0 to find inflection points (x = ±1/√2)",
            tx(W/2, 16, "y = x⁴−3x²+2  →  y'' = 12x²−6", sz=9, col=LB),
            hitdot(W/2, 16, 65)),
    ]

def graph_e_x2():
    ox,oy = 120,160; sx=28; sy=12
    pts = curve_pts(lambda x: math.exp(x**2), -1.8, 1.8)
    svg_pts = math_to_svg(pts, ox, oy, sx, sy, y_clip=15)
    return axes_shape(ox,oy) + [
        hs("Curve f(x) = e^(x²)  — symmetric about y-axis; grows faster than eˣ",
            pl(svg_pts, col=OG, w=2.2)),
        hs("Chain rule: d/dx[e^(x²)] = 2x·e^(x²)  (outer' = eˣ, inner' = 2x)",
            tx(W/2, 16, "d/dx[e^(x²)] = 2x e^(x²)", sz=10, col=LB),
            hitdot(W/2, 16, 65)),
    ]

def graph_def_integral_x2():
    return graph_with_area(lambda x: x**2, "x²", 0, 1, ox=60, oy=155, sx=110, sy=90, y_max=1.2)

def graph_def_integral_2x1():
    return graph_with_area(lambda x: 2*x+1, "2x+1", 0, 2, ox=60, oy=155, sx=55, sy=30, y_max=6)

# ════════════════════════════════════════════════════════════
# GENERATE ALL IMAGES
# ════════════════════════════════════════════════════════════

print("Generating geometry images...")
save("geo-e-001.svg", right_triangle(3,4,5))
save("geo-e-002.svg", square_shape(7))
save("geo-e-003.svg", triangle_bh(10,6))
save("geo-e-004.svg", rect_shape(8,5))
save("geo-e-005.svg", rect_shape(9,4))
save("geo-e-006.svg", circle_shape(3, extra="C = 2πr"))
save("geo-e-007.svg", cube_shape(4))
save("geo-e-008.svg", triangle_angle_sum())
save("geo-e-009.svg", circle_shape(2, extra="A = πr²"))
save("geo-e-010.svg", right_triangle(5,12,13))
save("geo-m-001.svg", circle_shape(5, extra="A = πr²"))
save("geo-m-002.svg", cone_shape(3,7))
save("geo-m-003.svg", sphere_shape(3))
save("geo-m-004.svg", triangle_angles_shape(65,75,40))
save("geo-m-005.svg", rhombus_shape(8,6))
save("geo-m-006.svg", box_shape(5,4,3))
save("geo-m-007.svg", trapezoid_shape(5,9,4))
save("geo-m-008.svg", sas_triangle(7,8,60))
save("geo-m-009.svg", equilateral_shape(6))
save("geo-m-010.svg", cube_shape(5, "SA = 6s²"))
save("geo-h-001.svg", right_triangle(8,15,17))
save("geo-h-002.svg", circle_shape("?", label="r", extra="A = 50π  →  r = ?"))
save("geo-h-003.svg", rect_diagonal(5,12))
save("geo-h-004.svg", cylinder_shape(4,10))
save("geo-h-005.svg", cylinder_shape(3,8))
save("geo-h-006.svg", hexagon_shape())
save("geo-h-007.svg", pyramid_shape(6,8))
save("geo-h-008.svg", circle_arc_shape(10,60))
save("geo-h-009.svg", sphere_shape(6))
save("geo-h-010.svg", circle_sector_shape(9,120))

print("Generating trigonometry images...")
save("trig-e-001.svg", unit_circle_shape(30))
save("trig-e-002.svg", unit_circle_shape(60))
save("trig-e-003.svg", trig_45_45_90_shape())
save("trig-e-004.svg", unit_circle_shape(90))
save("trig-e-005.svg", unit_circle_shape(0))
save("trig-e-006.svg", trig_45_45_90_shape())
save("trig-e-007.svg", unit_circle_shape(90))
save("trig-e-008.svg", trig_30_60_90_shape())
save("trig-e-009.svg", trig_30_60_90_shape())
save("trig-e-010.svg", unit_circle_shape(0))
save("trig-m-001.svg", unit_circle_shape(45, extra_label="sin²θ + cos²θ = 1"))
save("trig-m-002.svg", trig_labeled_shape())
save("trig-m-003.svg", unit_circle_shape(60, extra_label="sin(2×30°) = sin(60°)"))
save("trig-m-004.svg", trig_3_4_5_shape())
save("trig-m-005.svg", unit_circle_shape(90, extra_label="cos(2×45°) = cos(90°)"))
save("trig-m-006.svg", unit_circle_shape(135))
save("trig-m-007.svg", unit_circle_shape(150))
save("trig-m-008.svg", unit_circle_shape(90, extra_label="sin(30°+60°) = sin(90°) = 1"))
save("trig-m-009.svg", trig_sec_shape())
save("trig-m-010.svg", trig_30_60_90_shape())
save("trig-h-001.svg", unit_circle_shape(45, extra_label="Cross-multiply to verify identity"))
save("trig-h-002.svg", unit_circle_shape(15, extra_label="π/12 = π/4 − π/6"))
save("trig-h-003.svg", unit_circle_shape(90, extra_label="Solutions: x=π/2, 7π/6, 11π/6",
     multi_pts=[(90,OG),(210,AC),(330,AC)]))
save("trig-h-004.svg", unit_circle_shape(45, extra_label="cos(2x) = cos²x − sin²x"))
save("trig-h-005.svg", sine_wave_shape(3, 1))
save("trig-h-006.svg", trig_law_sines_shape(7, 45, 60))
save("trig-h-007.svg", unit_circle_shape(0, extra_label="sin(3x)=0: x=0, π/3, 2π/3, π",
     multi_pts=[(0,OG),(60,OG),(120,OG),(180,OG)]))
save("trig-h-008.svg", trig_sec_shape())
save("trig-h-009.svg", unit_circle_shape(45, extra_label="1−cos²x = sin²x  →  sin²x/sinx = sinx"))
save("trig-h-010.svg", unit_circle_shape(22, extra_label="sin(π/8) = sin(22.5°)"))

print("Generating calculus images...")
save("calc-e-001.svg", graph_power(2))
save("calc-e-002.svg", graph_power(3))
save("calc-e-003.svg", graph_linear_fn(5, "f(x) = 5x  →  d/dx = 5"))
save("calc-e-004.svg", graph_constant(7))
save("calc-e-005.svg", graph_with_area(lambda x: 2*x, "2x", 0, 3, ox=60, oy=155, sx=35, sy=18))
save("calc-e-006.svg", graph_power(4))
save("calc-e-007.svg", graph_with_area(lambda x: 3, "3", 0, 3, ox=60, oy=155, sx=40, sy=30))
save("calc-e-008.svg", graph_limit(lambda x: x**2, 2, "lim(x→2) x² = 4"))
save("calc-e-009.svg", axes_shape() + [
     hs("Curve y = x²+3x  — a parabola shifted left and down",
         pl(math_to_svg(curve_pts(lambda x: x**2+3*x, -4,1.5), 120,155,22,10,y_clip=10), col=OG, w=2.2)),
     hs("Power rule + sum rule: d/dx[x²+3x] = 2x+3",
         tx(W/2, 16, "d/dx[x²+3x] = 2x+3", sz=10, col=LB),
         hitdot(W/2, 16, 65))])
save("calc-e-010.svg", graph_def_integral_x2())
save("calc-m-001.svg", graph_product_rule())
save("calc-m-002.svg", graph_quotient_rule())
save("calc-m-003.svg", graph_chain_rule())
save("calc-m-004.svg", graph_def_integral_x2())
save("calc-m-005.svg", graph_exp())
save("calc-m-006.svg", graph_ln())
save("calc-m-007.svg", graph_with_area(lambda x: math.exp(x), "eˣ", 0, 2, ox=60, oy=155, sx=40, sy=20))
save("calc-m-008.svg", graph_sin_over_x())
save("calc-m-009.svg", graph_sinx())
save("calc-m-010.svg", graph_def_integral_2x1())
save("calc-h-001.svg", graph_sinx() )  # chain rule ln(sin(x))
save("calc-h-002.svg", graph_ibp())
save("calc-h-003.svg", graph_ex_minus_1_x())
save("calc-h-004.svg", graph_1_over_x())
save("calc-h-005.svg", graph_x4_poly())
save("calc-h-006.svg", graph_sinx_area())
save("calc-h-007.svg", graph_e_x2())
save("calc-h-008.svg", graph_1_over_x_area())
save("calc-h-009.svg", graph_xx())
save("calc-h-010.svg", graph_sinx_cosx())

print(f"\nGenerated 90 SVG files in {OUT}")

# ════════════════════════════════════════════════════════════
# UPDATE JSON FILES — add "image" field to each puzzle
# ════════════════════════════════════════════════════════════

def add_image_fields(json_path):
    with open(json_path) as f:
        puzzles = json.load(f)
    for p in puzzles:
        p['image'] = f"{p['id']}.svg"
    with open(json_path, 'w') as f:
        json.dump(puzzles, f, indent=2, ensure_ascii=False)
    print(f"Updated {os.path.basename(json_path)} ({len(puzzles)} puzzles)")

print("\nUpdating JSON files...")
add_image_fields(os.path.join(BASE, 'puzzles', 'geometry.json'))
add_image_fields(os.path.join(BASE, 'puzzles', 'trigonometry.json'))
add_image_fields(os.path.join(BASE, 'puzzles', 'calculus.json'))

print("\nDone! Run server and reload to see images.")
