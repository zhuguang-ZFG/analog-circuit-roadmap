/* Optional learning records. All links/titles come from the generated catalog. */
(function () {
  'use strict';
  var catalog = window.ANALOG_LEARNING_CATALOG;
  if (!catalog || !document.currentScript) return;
  var base = new URL('../', document.currentScript.src);
  var key = 'analog-learning:v1:' + base.pathname;
  var chapters = new Map(catalog.chapters.map(function (entry) { return [entry.id, entry]; }));
  var questions = new Map(catalog.questions.map(function (entry) { return [entry.id, entry]; }));
  var temporary = false;
  var current = null;
  var scheduled = false;

  function uniqueKnown(values, index) {
    return Array.isArray(values) ? Array.from(new Set(values.filter(function (id) { return index.has(id); }))) : [];
  }
  function read() {
    var empty = { version: 1, completed: [], bookmarks: [], last: null };
    try {
      var raw = JSON.parse(localStorage.getItem(key) || 'null');
      if (!raw || raw.version !== 1) return empty;
      empty.completed = uniqueKnown(raw.completed, chapters);
      empty.bookmarks = uniqueKnown(raw.bookmarks, questions);
      if (raw.last && chapters.has(raw.last.chapter)) {
        empty.last = { chapter: raw.last.chapter,
          anchor: typeof raw.last.anchor === 'string' ? raw.last.anchor.slice(0,150) : raw.last.chapter };
      }
    } catch (_) { temporary = true; }
    return empty;
  }
  var state = read();
  function save() {
    try { localStorage.setItem(key, JSON.stringify(state)); temporary = false; }
    catch (_) { temporary = true; }
    document.querySelectorAll('.learning-storage-note').forEach(function (note) {
      note.textContent = temporary ? '浏览器无法保存，本次操作仅临时保留。' :
        '记录仅保存在当前浏览器，清除站点数据后会丢失。';
    });
  }
  function element(tag, text, className) {
    var el = document.createElement(tag);
    if (text) el.textContent = text;
    if (className) el.className = className;
    return el;
  }
  function link(entry, anchor) {
    var el = element('a', entry.title);
    var url = new URL(entry.href, base);
    if (anchor) url.hash = anchor;
    el.href = url.href;
    return el;
  }
  function toggle(list, value) {
    var index = list.indexOf(value);
    if (index === -1) list.push(value);
    else list.splice(index, 1);
    save();
    refresh();
  }
  function button(label, handler, className) {
    var el = element('button', label, className);
    el.type = 'button';
    el.addEventListener('click', handler);
    return el;
  }
  function dashboard() {
    var root = document.querySelector('.learning-dashboard');
    if (!root) return;
    var wasOpen = root.querySelector('details');
    var open = wasOpen && wasOpen.open;
    root.replaceChildren();
    root.appendChild(element('h2', '我的学习记录'));
    if (state.last) {
      var resume = link(chapters.get(state.last.chapter), state.last.anchor);
      resume.textContent = '继续上次阅读：' + resume.textContent;
      resume.className = 'learning-resume';
      root.appendChild(resume);
    }
    var label = element('p', '已完成 ' + state.completed.length + ' / ' + catalog.chapters.length + ' 章');
    root.appendChild(label);
    var progress = element('progress');
    progress.max = catalog.chapters.length;
    progress.value = state.completed.length;
    progress.setAttribute('aria-label', '章节完成进度');
    root.appendChild(progress);
    var details = element('details');
    details.open = Boolean(open);
    details.appendChild(element('summary', '错题收藏（' + state.bookmarks.length + '）'));
    if (!state.bookmarks.length) {
      details.appendChild(element('p', '在自测题旁点击“收藏为错题”，下次从这里复习。'));
    } else {
      var list = element('ul');
      state.bookmarks.forEach(function (id) {
        var item = element('li');
        item.appendChild(link(questions.get(id)));
        list.appendChild(item);
      });
      details.appendChild(list);
    }
    root.appendChild(details);
    root.appendChild(element('p', temporary ? '浏览器无法保存，本次操作仅临时保留。' :
      '记录仅保存在当前浏览器，清除站点数据后会丢失。', 'learning-storage-note'));
  }
  function refresh() {
    document.querySelectorAll('.chapter-done-button').forEach(function (el) {
      var done = state.completed.includes(el.dataset.chapter);
      el.setAttribute('aria-pressed', String(done));
      el.textContent = done ? '本章已完成 · 点击撤销' : '标记本章已完成';
    });
    document.querySelectorAll('.question-bookmark').forEach(function (el) {
      var saved = state.bookmarks.includes(el.dataset.question);
      el.setAttribute('aria-pressed', String(saved));
      el.textContent = saved ? '已收藏 · 移出错题' : '收藏为错题';
    });
    dashboard();
  }
  function remember(anchor) {
    if (!current || (state.last && state.last.chapter === current.id && state.last.anchor === anchor)) return;
    state.last = { chapter: current.id, anchor: anchor };
    save();
  }
  function init() {
    current = catalog.chapters.find(function (entry) {
      return new URL(entry.href, base).pathname === location.pathname;
    }) || null;
    if (current) {
      var anchor;
      try { anchor = decodeURIComponent(location.hash.slice(1)); } catch (_) { anchor = ''; }
      var target = document.getElementById(anchor);
      if (!target || !target.classList.contains('legacy-anchor')) remember(anchor || current.id);
      var checkpoint = document.querySelector('.reading-checkpoint');
      if (checkpoint && !checkpoint.querySelector('.chapter-done-button')) {
        var chapterId = current.id;
        var done = button('标记本章已完成', function () { toggle(state.completed, chapterId); }, 'chapter-done-button');
        done.dataset.chapter = chapterId;
        checkpoint.appendChild(done);
        var note = element('p', '', 'learning-storage-note');
        note.setAttribute('role', 'status');
        checkpoint.appendChild(note);
      }
    }
    document.querySelectorAll('a[data-quiz-question]').forEach(function (anchor) {
      if (!questions.has(anchor.id)) return;
      var parent = anchor.closest('li') || anchor.parentElement;
      if (parent.querySelector('.question-bookmark')) return;
      var tools = element('div', '', 'question-tools');
      var mark = button('收藏为错题', function () { toggle(state.bookmarks, anchor.id); }, 'question-bookmark');
      mark.dataset.question = anchor.id;
      mark.setAttribute('aria-label', '错题收藏：' + questions.get(anchor.id).title);
      tools.appendChild(mark);
      parent.appendChild(tools);
    });
    var hero = document.querySelector('.learning-hero');
    if (hero && !document.querySelector('.learning-dashboard')) {
      hero.after(element('section', '', 'learning-dashboard'));
    }
    refresh();
    document.querySelectorAll('.learning-storage-note').forEach(function (note) {
      note.textContent = temporary ? '浏览器无法保存，本次操作仅临时保留。' :
        '记录仅保存在当前浏览器，清除站点数据后会丢失。';
    });
  }
  window.addEventListener('scroll', function () {
    if (!current || scheduled) return;
    scheduled = true;
    requestAnimationFrame(function () {
      scheduled = false;
      if (!current) return;
      var anchor = current.id;
      document.querySelectorAll('.md-content h2[id], .md-content h3[id], .md-content h4[id]').forEach(function (heading) {
        if (heading.getBoundingClientRect().top <= 110) anchor = heading.id;
      });
      remember(anchor);
    });
  }, { passive: true });
  window.addEventListener('storage', function (event) {
    if (event.key === key || event.key === null) { state = read(); refresh(); }
  });
  if (typeof document$ !== 'undefined') document$.subscribe(init);
  else if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
