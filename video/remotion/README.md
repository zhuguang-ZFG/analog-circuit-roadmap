# remotion/ —— 竖屏成片产线（EP01–EP20）

程序化短视频产线：`samples/<name>-final.mp4`（抖音竖屏 1080×1920@30）由本目录产出。
替代旧管线（`../master.py`）的竖屏部分；横屏 `-final-h.mp4` 仍走旧管线。

## 一次性安装

```bash
cd video/remotion
npm ci
```

## 换一集（四步，零手改框架）

```bash
# 前提：video/samples/ 有 <name>-timeline.json 和 <name>-vo-narr.wav
python make_subs.py <name>     # 1. 字幕窗生成（切句+折行+字数比例分窗）+ RMS 能量分位注入
python remix.py <name>         # 2. 口播 + 平和 BGM(72BPM) + riser 母带 → public/audio/<name>-remix.wav
cp ../samples/<name>-timeline.json src/data/epNN.json   # 3. board 数据
python gen_registry.py        # 4. 重建 episodes.ts（生成文件，勿手改）
```

字幕窗算法与旧管线 `master.py` 的 subtitle_filters 同源（对账过 16/16 逐块一致）；
`env` 分位驱动卡拉OK扫字，静音段不占扫字时间。

## 渲染

```bash
npx remotion compositions src/index.ts          # 列出全部组合
npx remotion render src/index.ts epNN out/xxx.mp4   # 全片（约 3 分钟/集）
npx remotion still src/index.ts epNN out/xxx.png --frame=900   # 抽帧检查
```

成片入仓：`cp out/xxx.mp4 ../samples/<name>-final.mp4`（git 跟踪约定见 ../README.md）。

## 定制戏眼（可选）

通用幕型：intro / card / svg / num，全数据驱动。某集需要专属动画时：
1. `src/components/` 写组件（参考 DividerDemo / DividerCollapse）；
2. `gen_registry.py` 的 `CUSTOM` 表挂 `{view名: 组件}`；
3. board JSON 里该幕加 `"view": "组件名"`。

## 验证

- `npx tsc --noEmit`；
- CI 闸（`.github/workflows/tests.yml` remotion-smoke）：tsc + ep04 单帧实渲；
- 抽帧像素探针：`std > 8` 判内容在位（视觉 QA 通道对本机模型不可用时的替代）。
