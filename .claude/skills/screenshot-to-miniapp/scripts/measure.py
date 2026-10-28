"""截图像素测量工具：取色、扫描行/列找元素边界、裁剪放大、并排对比。

坐标都用原图像素；--scale 把结果换算成设计稿单位（如 1170 宽截图用 3 得到 pt）。
用法：
  python -I measure.py color  IMG x,y [x,y ...]
  python -I measure.py row    IMG y [--from X0 --to X1] [--th 30]     # 横向扫描，输出颜色变化段
  python -I measure.py col    IMG x [--from Y0 --to Y1] [--th 30]     # 纵向扫描
  python -I measure.py bbox   IMG x0,y0,x1,y1 [--bg #ffffff] [--th 30] # 区域内非背景像素的包围盒
  python -I measure.py crop   IMG x0,y0,x1,y1 OUT [--zoom 2]
  python -I measure.py side   A B OUT [--width 390]                    # 原图和实现截图并排，便于对比
"""
import argparse, sys
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")


def hexc(p):
    return "#%02x%02x%02x" % p[:3]


def dist(a, b):
    return max(abs(a[i] - b[i]) for i in range(3))


def pt(v, s):
    return f"{v}px/{v / s:g}" if s != 1 else str(v)


def segments(pixels, start, th):
    # 把连续相近的颜色合并成段：(起点, 终点, 颜色)
    segs, s0, ref = [], start, pixels[0]
    for i, p in enumerate(pixels[1:], 1):
        if dist(p, ref) > th:
            segs.append((s0, start + i - 1, ref))
            s0, ref = start + i, p
    segs.append((s0, start + len(pixels) - 1, ref))
    return segs


def parse_box(s):
    return tuple(int(v) for v in s.split(","))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("args", nargs="+")
    ap.add_argument("--scale", type=float, default=1)
    ap.add_argument("--th", type=int, default=30)
    ap.add_argument("--from", dest="a", type=int)
    ap.add_argument("--to", dest="b", type=int)
    ap.add_argument("--bg", default="#ffffff")
    ap.add_argument("--zoom", type=float, default=2)
    ap.add_argument("--width", type=int, default=390)
    o = ap.parse_args()
    im = Image.open(o.args[0]).convert("RGB")
    W, H = im.size

    if o.cmd == "color":
        for xy in o.args[1:]:
            x, y = parse_box(xy)
            print(xy, hexc(im.getpixel((x, y))))
    elif o.cmd in ("row", "col"):
        k = int(o.args[1])
        a = o.a or 0
        b = o.b or ((W if o.cmd == "row" else H) - 1)
        px = [im.getpixel((i, k) if o.cmd == "row" else (k, i)) for i in range(a, b + 1)]
        for s, e, c in segments(px, a, o.th):
            print(f"{pt(s, o.scale)} - {pt(e, o.scale)}  len={pt(e - s + 1, o.scale)}  {hexc(c)}")
    elif o.cmd == "bbox":
        x0, y0, x1, y1 = parse_box(o.args[1])
        bg = tuple(int(o.bg[i:i + 2], 16) for i in (1, 3, 5))
        xs, ys = [], []
        for y in range(y0, y1):
            for x in range(x0, x1):
                if dist(im.getpixel((x, y)), bg) > o.th:
                    xs.append(x); ys.append(y)
        if not xs:
            print("区域内没有非背景像素")
        else:
            l, t, r, btm = min(xs), min(ys), max(xs), max(ys)
            print(f"left={pt(l, o.scale)} top={pt(t, o.scale)} right={pt(r, o.scale)} bottom={pt(btm, o.scale)} "
                  f"w={pt(r - l + 1, o.scale)} h={pt(btm - t + 1, o.scale)}")
    elif o.cmd == "crop":
        box, out = parse_box(o.args[1]), o.args[2]
        c = im.crop(box)
        c = c.resize((int(c.width * o.zoom), int(c.height * o.zoom)), Image.LANCZOS)
        c.save(out)
        print(out, c.size)
    elif o.cmd == "side":
        b_im = Image.open(o.args[1]).convert("RGB")
        out = o.args[2]
        imgs = [i.resize((o.width, int(i.height * o.width / i.width))) for i in (im, b_im)]
        h = max(i.height for i in imgs)
        canvas = Image.new("RGB", (o.width * 2 + 10, h), "#ff00ff")
        canvas.paste(imgs[0], (0, 0)); canvas.paste(imgs[1], (o.width + 10, 0))
        canvas.save(out)
        print(out, canvas.size)
    else:
        ap.error("未知命令")


if __name__ == "__main__":
    main()
