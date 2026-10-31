const assert = require('node:assert/strict');
const {test} = require('node:test');
const fs = require('node:fs');
const path = require('node:path');
const ts = require('typescript');
// Match production rendering; this static markup is never hydrated, so React's
// development-only SSR layout-effect warnings do not apply.
process.env.NODE_ENV = 'production';
const {createElement: h} = require('react');
const {renderToStaticMarkup} = require('react-dom/server');
const {Internals} = require('remotion');

for (const ext of ['.ts', '.tsx']) {
  require.extensions[ext] = (module, filename) => {
    const compiled = ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
      compilerOptions: {module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true},
    });
    module._compile(compiled.outputText, filename);
  };
}

const component = (name) => {
  const file = path.join(__dirname, 'src/components', `${name}.tsx`);
  assert.ok(fs.existsSync(file), `${name} must render a real teaching diagram`);
  return require(file);
};

test('independent noise contributions add in quadrature, not amplitude', () => {
  const {rootSumSquares} = component('NoiseRss');
  assert.equal(rootSumSquares([3, 4]), 5);
  assert.equal(rootSumSquares([1, 1, 1, 1]), 2);
  assert.equal(rootSumSquares([0, 0]), 0);
});

test('RSS animation accumulates variance before revealing RMS', () => {
  const {rssStage} = component('NoiseRss');
  assert.deepEqual(rssStage(0, 300), {count: 0, variance: 0, rms: 0, merge: 0});
  const middle = rssStage(110, 300);
  assert.equal(middle.count, 3);
  assert.equal(middle.variance, 3);
  assert.equal(middle.rms, Math.sqrt(3));
  assert.deepEqual(rssStage(299, 300), {count: 4, variance: 4, rms: 2, merge: 1});
  assert.deepEqual(rssStage(308, 300), rssStage(299, 300));
});

test('quiz reveals exactly at the spoken answer, independent of scene tail', () => {
  const {quizRevealFrame} = component('QuizShot');
  assert.equal(typeof quizRevealFrame, 'function', 'quiz must honor measured revealAt');
  assert.equal(quizRevealFrame(450, 30, 8.2), 246);
  assert.equal(quizRevealFrame(300, 30), 210);
  assert.equal(quizRevealFrame(90, 30), 45);
});

// Use real composition/frame contexts rather than mocking Remotion hooks.
const renderScene = (Scene, props, frame, wide) => {
  const config = {
    id: 'teaching-test', component: Scene, durationInFrames: props.durFrames, fps: 30,
    width: wide ? 1920 : 1080, height: wide ? 1080 : 1920, defaultProps: {},
  };
  return renderToStaticMarkup(
    h(Internals.CompositionManager.Provider, {value: {
      compositions: [config], folders: [], currentCompositionMetadata: null,
      currentAssetMetadata: null, canvasContent: {type: 'composition', compositionId: config.id},
    }}, h(Internals.VideoProvider, null,
      h(Internals.TimelineContext.Provider, {value: {
        frame: {[config.id]: frame}, isPlaying: () => false,
        isInsideFreeze: false, audioAndVideoTags: {current: []},
      }}, h(Internals.CanUseRemotionHooksProvider, null, h(Scene, props))))),
  );
};

const renderQuiz = (frame, revealAt, wide = true) => {
  const {QuizShot} = component('QuizShot');
  const markup = renderScene(QuizShot, {durFrames: 300, q: 'Which answer?',
    options: ['One', 'Two', 'Three'], answer: 1, explain: 'Two is correct.', revealAt}, frame, wide);
  const countdown = markup.match(/<div style="([^"]*height:10px[^"]*)"><div style="([^"]*)"><\/div><\/div>/);
  assert.ok(countdown, 'rendered quiz must contain its countdown track and fill');
  assert.doesNotMatch(markup, /NaN|Infinity/);
  return {markup, track: countdown[1], fill: countdown[2]};
};

for (const revealAt of [0, 0.001]) {
  for (const wide of [true, false]) {
    test(`quiz revealAt=${revealAt} renders an empty countdown immediately (${wide ? 'wide' : 'portrait'})`, () => {
      for (const frame of [0, 1, 20, 299]) {
        const {markup, track, fill} = renderQuiz(frame, revealAt, wide);
        assert.match(fill, /^width:0%;/);
        assert.match(track, /opacity:0(?:;|$)/);
        assert.ok(markup.includes('\u2713'), 'correct answer must be marked from frame zero');
      }
    });
  }
}

test('quiz countdown and answer still follow explicit and default reveal frames', () => {
  for (const [revealAt, middle, revealFrame] of [[2, 30, 60], [undefined, 105, 210]]) {
    for (const [frame, width, revealed] of [[0, 100, false], [middle, 50, false],
      [revealFrame, 0, true], [299, 0, true]]) {
      const {markup, track, fill} = renderQuiz(frame, revealAt);
      assert.ok(fill.startsWith(`width:${width}%;`), fill);
      assert.match(track, new RegExp(`opacity:${revealed ? 0 : 1}(?:;|$)`));
      assert.equal(markup.includes('\u2713'), revealed);
    }
  }
});

test('karaoke uses spoken character timestamps and keeps an existing-timeline fallback', () => {
  const {characterFrame} = require('./src/Subtitles.tsx');
  assert.equal(typeof characterFrame, 'function', 'subtitles must use measured character boundaries');
  assert.equal(characterFrame(1, 3, 60, undefined, [0, 17, 39]), 17);
  assert.equal(characterFrame(2, 3, 60, [0, 0.5, 1], [0, 17, 39]), 39);
  assert.equal(characterFrame(0, 2, 40), 8);
  assert.equal(characterFrame(1, 2, 40, [0, 0.5, 1]), 28);
});

for (const wide of [true, false]) {
  test(`noise spectrum stays above subtitles through both zooms (${wide ? 'wide' : 'portrait'})`, () => {
    const {spawnSync} = require('node:child_process');
    const {SvgShot} = component('SvgShot');
    const svg = fs.readFileSync(path.join(__dirname, 'public/svg/noise-budget.svg')).toString('base64');
    const scenes = [27, 120, 239, 248].map(frame => {
      // Img assigns src in a layout effect; static layout uses the same real local asset.
      const markup = renderScene(SvgShot, {durFrames: 240, index: 1, file: 'noise-budget',
        caption: '先认来源，再算贡献'}, frame, wide)
        .replace('<img ', `<img src="data:image/svg+xml;base64,${svg}" `);
      assert.ok(markup.includes(`src="data:image/svg+xml;base64,${svg}"`));
      return {markup, frame, width: wide ? 1920 : 1080, height: wide ? 1080 : 1920};
    });
    const result = spawnSync('python3', ['-c', `
import json, sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    try:
        for scene in json.load(sys.stdin):
            width, height = scene['width'], scene['height']
            page = browser.new_page(viewport={'width':width,'height':height})
            page.set_content('<body style="margin:0"><div style="position:relative;width:%spx;height:%spx">%s</div>' % (width,height,scene['markup']))
            image = page.locator('img')
            image.evaluate('(img) => img.decode()')
            bounds = image.evaluate('(img) => {const r=img.getBoundingClientRect();return {top:r.top,bottom:r.bottom,left:r.left,right:r.right}}')
            top = height - 215 if width > height else 1425
            assert bounds['bottom'] <= top - 24, (scene['frame'], 'spectrum overlaps subtitles', bounds)
            assert bounds['top'] >= 0, (scene['frame'], 'spectrum cropped at top', bounds)
            background_bottom = image.evaluate('(img) => {let e=img.parentElement;while(getComputedStyle(e).backgroundImage === "none") e=e.parentElement;return e.getBoundingClientRect().bottom}')
            assert background_bottom >= height, (scene['frame'], 'scene background stops before the bottom', background_bottom)
            page.close()
    finally:
        browser.close()
`], {input: JSON.stringify(scenes), encoding: 'utf8', timeout: 60000, maxBuffer: 4 * 1024 * 1024});
    assert.ifError(result.error);
    assert.equal(result.status, 0, result.stderr || result.stdout);
  });
}
