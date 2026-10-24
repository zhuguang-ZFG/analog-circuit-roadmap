# -*- coding: utf-8 -*-
"""顺序批渲 ep02-ep20 竖屏到 out_new/（不改 out/，最后统一交换）。"""
import shutil
import subprocess
import sys
import time
from pathlib import Path

NPX = shutil.which('npx') or shutil.which('npx.cmd')
if not NPX:
    sys.exit('npx not found on PATH')

BASE = Path(r'D:/Users/monidianlu/analog-circuit-roadmap/video/remotion')
OUT = BASE / 'out_new'
OUT.mkdir(exist_ok=True)
LOG = open(BASE / 'out_new' / 'render_batch.log', 'a', encoding='utf-8', buffering=1)

eps = [f'ep{i:02d}' for i in range(2, 21)]
fails = []
for ep in eps:
    target = OUT / f'{ep}-v.mp4'
    if target.exists() and target.stat().st_size > 1_000_000:
        LOG.write(f'skip {ep} (exists)\n')
        continue
    t0 = time.time()
    LOG.write(f'=== render {ep} start {time.strftime("%H:%M:%S")}\n')
    p = subprocess.run(
        [NPX, 'remotion', 'render', 'src/index.ts', ep, str(target)],
        cwd=str(BASE), capture_output=True, text=True, timeout=900,
    )
    tail = (p.stdout or '')[-600:] + (p.stderr or '')[-600:]
    LOG.write(tail + f'\n--- rc={p.returncode} {time.time()-t0:.0f}s\n')
    if p.returncode != 0 or not target.exists():
        fails.append(ep)
        LOG.write(f'FAIL {ep}\n')

LOG.write(f'DONE fails={fails}\n')
print('DONE fails=', fails)
sys.exit(0 if not fails else 2)
