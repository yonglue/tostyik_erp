import glob, os
from PIL import Image

print(f"{'文件':<30} {'尺寸':<14} {'白块%':>8}  说明")
print("-" * 70)
for p in sorted(glob.glob('test-results/dark-audit/*.png')):
    img = Image.open(p).convert('RGB')
    w, h = img.size
    small = img.resize((max(1, w // 4), max(1, h // 4)))
    pixels = list(small.getdata())
    total = len(pixels)
    whiteish = sum(1 for r, g, b in pixels if r > 220 and g > 220 and b > 220)
    ratio = whiteish / total * 100
    flag = "🚨 明显白块" if ratio > 15 else ("⚠️  局部白块" if ratio > 5 else "✅ 基本正常")
    print(f"{os.path.basename(p):<30} {w}x{h:<10} {ratio:>7.2f}%  {flag}")
