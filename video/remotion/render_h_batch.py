# -*- coding: utf-8 -*-
"""顺序批渲 20 集横屏到 out_new_h/（当前 src；不动 out/）。断点续渲：已存在的跳过。"""
import shutil
import subprocess
import sys
import time
from pathlib import Path

NPX = shutil.which('npx') or shutil.which('npx.cmd')
if not NPX:
    sys.exit('npx not found on PATH')

BASE = Path(r'D:/Users/monidianlu/analog-circuit-roadmap/video/remotion')
OUT = BASE / 'out_new_h'
OUT.mkdir(exist_ok=True)
LOG = open(OUT / 'render_h.log', 'a', encoding='utf-8', buffering=1)

eps = [f'ep{i:02d}' for i in range(1, 21)]
fails = []
for ep in eps:
    target = OUT / f'{ep}-h.mp4'
    if target.exists() and target.stat().st_size > 1_000_000:
        LOG.write(f'skip {ep} (exists)\n')
        continue
    t0 = time.time()
    LOG.write(f'=== render {ep}-h start {time.strftime("%H:%M:%S")}\n')
    p = subprocess.run(
        [NPX, 'remotion', 'render', 'src/index.ts', f'{ep}-h', str(target)],
        cwd=str(BASE), capture_output=True, text=True, timeout=1800,
    )
    tail = (p.stdout or '')[-500:] + (p.stderr or '')[-500:]
    LOG.write(tail + f'\n--- rc={p.returncode} {time.time()-t0:.0f}s\n')
    if p.returncode != 0 or not target.exists():
        fails.append(ep)
        LOG.write(f'FAIL {ep}\n')

LOG.write(f'DONE fails={fails}\n')
print('DONE fails=', fails)
sys.exit(0 if not fails else 2)
