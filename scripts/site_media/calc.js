/* 🧮 就地算：正文算例旁的可调参数小计算器。
 *
 * docs/ 里只放一个空容器 `<div class="calc" data-calc="型号"></div>`，
 * 这里在客户端把输入项和结果行画出来。铁律：**每个型号的默认值 = 正文里
 * 那笔算例的原数**，输出口径与正文一致——读者改参数前后，书上的数永远
 * 能对上（test_calcs.py 用正文算例的数逐项回归）。
 * JavaScript 关掉时容器是空的，无害：紧挨着的那条 🧮 算一笔就是兜底算例。
 */
(function () {
  'use strict';

  function fmt(v, d) {
    if (!isFinite(v)) return '—';
    var m = Math.pow(10, d);
    return (Math.round(v * m) / m).toFixed(d);
  }

  var CALCS = {
    divider: {
      name: '分压器带载',
      note: '带载 = 给 R2 并联一只 RL：先算 R2∥RL，再代回分压式。空载公式只在空载成立。',
      inputs: [
        { key: 'vin', label: '输入电压', unit: 'V', value: 10, step: 0.5, min: 0 },
        { key: 'r1', label: 'R1', unit: 'kΩ', value: 10, step: 1, min: 0.1 },
        { key: 'r2', label: 'R2', unit: 'kΩ', value: 10, step: 1, min: 0.1 },
        { key: 'rl', label: '负载 RL', unit: 'kΩ', value: 10, step: 1, min: 0.1 }
      ],
      compute: function (x) {
        var vz = x.vin * x.r2 / (x.r1 + x.r2);
        var r2p = (x.r2 * x.rl) / (x.r2 + x.rl);
        var vl = x.vin * r2p / (x.r1 + r2p);
        var sag = vz > 0 ? (1 - vl / vz) * 100 : 0;
        return [
          { label: '空载输出', value: fmt(vz, 2), unit: 'V' },
          { label: '带载输出', value: fmt(vl, 2), unit: 'V' },
          { label: '塌陷', value: fmt(sag, 1), unit: '%' }
        ];
      }
    },
    electrolyte: {
      name: '电解电容寿命',
      note: '10℃ 翻倍法则：环境每比额定低 10℃，寿命翻一倍（阿伦尼乌斯的粗口径，纹波发热另算）。',
      inputs: [
        { key: 'hours', label: '额定寿命', unit: 'h', value: 2000, step: 500, min: 100 },
        { key: 't0', label: '额定温度', unit: '℃', value: 105, step: 5, min: 25 },
        { key: 'ta', label: '工作温度', unit: '℃', value: 65, step: 5, min: 0 }
      ],
      compute: function (x) {
        var life = x.hours * Math.pow(2, (x.t0 - x.ta) / 10);
        return [
          { label: '预期寿命', value: fmt(life, 0), unit: 'h' },
          { label: '约合', value: fmt(life / 8760, 1), unit: '年（连续通电）' }
        ];
      }
    },
    hysteresis: {
      name: '迟滞窗口',
      note: '开集电极比较器的双阈值：VTH± = VREF(1+R1/R2) − (R1/R2)·VOL/OH，窗口 = (R1/R2)(VOH−VOL)。',
      inputs: [
        { key: 'vref', label: '基准 VREF', unit: 'V', value: 2.5, step: 0.1, min: 0 },
        { key: 'r1', label: 'R1', unit: 'kΩ', value: 1, step: 0.5, min: 0.1 },
        { key: 'r2', label: 'R2', unit: 'kΩ', value: 100, step: 10, min: 0.1 },
        { key: 'voh', label: 'VOH', unit: 'V', value: 10, step: 1, min: 0 },
        { key: 'vol', label: 'VOL', unit: 'V', value: 0, step: 0.1, min: 0 }
      ],
      compute: function (x) {
        var k = x.r1 / x.r2;
        var vthp = x.vref * (1 + k) - k * x.vol;
        var vthm = x.vref * (1 + k) - k * x.voh;
        return [
          { label: '上门槛 VTH+', value: fmt(vthp, 3), unit: 'V' },
          { label: '下门槛 VTH−', value: fmt(vthm, 3), unit: 'V' },
          { label: '窗口 ΔV', value: fmt(vthp - vthm, 3), unit: 'V' }
        ];
      }
    },
    probe: {
      name: '探头负载',
      note: '×1 = 1MΩ∥100pF，×10 = 10MΩ∥10pF：源阻越大被分走越多，带宽被 RC 拖垮。',
      inputs: [
        { key: 'rs', label: '源阻抗', unit: 'kΩ', value: 100, step: 10, min: 0.1 },
        { key: 'mode', label: '探头档位', type: 'select', value: 'x1',
          options: [['x1', '×1 档'], ['x10', '×10 档']] }
      ],
      compute: function (x) {
        var zin = x.mode === 'x10' ? 10e6 : 1e6;
        var cap = x.mode === 'x10' ? 10e-12 : 100e-12;
        var rs = x.rs * 1e3;
        var ratio = zin / (zin + rs);
        var fc = 1 / (2 * Math.PI * rs * cap);
        return [
          { label: '分压系数', value: fmt(ratio, 3), unit: '' },
          { label: '幅度误差', value: fmt((1 - ratio) * 100, 1), unit: '%' },
          { label: '带宽截止', value: fmt(fc / 1e3, 1), unit: 'kHz' }
        ];
      }
    }
  };

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function build(root, key) {
    var spec = CALCS[key];
    if (!spec) return;
    root.dataset.calcReady = '1';
    var box = el('div', 'calc-box');
    box.setAttribute('role', 'group');
    box.setAttribute('aria-label', '就地算：' + spec.name);

    var title = el('p', 'calc-title', '🧮 就地算 · ' + spec.name);
    box.appendChild(title);

    var inputs = el('div', 'calc-inputs');
    var values = {};
    spec.inputs.forEach(function (input) {
      var label = el('label', 'calc-field');
      label.appendChild(el('span', 'calc-field-label', input.label));
      var widget;
      if (input.type === 'select') {
        widget = document.createElement('select');
        widget.setAttribute('aria-label', input.label);
        input.options.forEach(function (opt) {
          var option = document.createElement('option');
          option.value = opt[0];
          option.textContent = opt[1];
          if (opt[0] === input.value) option.selected = true;
          widget.appendChild(option);
        });
      } else {
        widget = document.createElement('input');
        widget.type = 'number';
        widget.value = input.value;
        widget.step = input.step;
        if (input.min !== undefined) widget.min = input.min;
        widget.setAttribute('aria-label', input.label + '（' + input.unit + '）');
      }
      widget.addEventListener('input', render);
      widget.addEventListener('change', render);
      values[input.key] = { input: input, widget: widget };
      label.appendChild(widget);
      label.appendChild(el('span', 'calc-unit', input.unit || ''));
      inputs.appendChild(label);
    });
    box.appendChild(inputs);

    var outputs = el('div', 'calc-outputs');
    box.appendChild(outputs);
    box.appendChild(el('p', 'calc-note', spec.note));
    root.appendChild(box);

    function read() {
      var x = {};
      Object.keys(values).forEach(function (key) {
        var entry = values[key];
        if (entry.input.type === 'select') {
          x[key] = entry.widget.value;
        } else {
          var v = parseFloat(entry.widget.value);
          x[key] = isNaN(v) ? 0 : v;
        }
      });
      return x;
    }

    function render() {
      var rows = spec.compute(read());
      outputs.textContent = '';
      rows.forEach(function (row) {
        var chip = el('span', 'calc-out');
        var value = el('b', null, row.value);
        chip.appendChild(value);
        chip.appendChild(el('span', 'calc-out-unit', row.unit ? ' ' + row.unit : ''));
        chip.appendChild(el('span', 'calc-out-label', row.label));
        outputs.appendChild(chip);
      });
    }

    render();
  }

  function init() {
    document.querySelectorAll('.calc[data-calc]').forEach(function (root) {
      if (root.isConnected && !root.dataset.calcReady) {
        build(root, root.dataset.calc);
      }
    });
  }

  if (typeof document$ !== 'undefined') { document$.subscribe(init); }
  else if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', init); }
  else { init(); }
}());
