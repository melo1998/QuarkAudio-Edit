/* ============================================================
   QuarkAudio-Edit Demo Page · Interaction Logic
   ============================================================ */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    renderOperationDemos();
    renderComplexDemos();
    renderBaselineDemos();
    renderFailureCases();
    renderGallery('mmediting');
    bindTabs();
    bindOperationFilter();
    bindGalleryTabs();
    enforceSingleAudioPlayback();
  });

  /* ---------- Render: 6 Atomic Operations ---------- */
  function renderOperationDemos() {
    const grid = document.getElementById('operations-grid');
    if (!grid || typeof OPERATION_DEMOS === 'undefined') return;

    grid.innerHTML = OPERATION_DEMOS.map(function (demo) {
      return buildDemoCard(demo);
    }).join('');
  }

  function buildDemoCard(demo) {
    const gtSlot = demo.gt ? `
          <div class="audio-slot">
            <div class="slot-label" style="color: #16a34a;">
              <i class="bi bi-check-circle-fill"></i> Ground Truth
            </div>
            <audio controls preload="none">
              <source src="${demo.gt}" type="audio/wav" />
            </audio>
          </div>
    ` : '';

    return `
      <div class="demo-card" data-op="${demo.op}">
        <div class="demo-header">
          <div class="demo-instruction">${escapeHtml(demo.instruction)}</div>
          <span class="op-tag op-${demo.op}">${demo.opLabel}</span>
        </div>
        <div class="demo-body">
          <div class="audio-slot">
            <div class="slot-label src">
              <i class="bi bi-music-note"></i> Source
            </div>
            <audio controls preload="none">
              <source src="${demo.src}" type="audio/wav" />
            </audio>
          </div>
          ${gtSlot}
          <div class="audio-slot">
            <div class="slot-label edited">
              <i class="bi bi-stars"></i> QuarkAudio-Edit
            </div>
            <audio controls preload="none">
              <source src="${demo.edited}" type="audio/wav" />
            </audio>
          </div>
        </div>
      </div>
    `;
  }

  /* ---------- Render: Complex Multi-Step Demos ---------- */
  function renderComplexDemos() {
    const list = document.getElementById('complex-list');
    if (!list || typeof COMPLEX_DEMOS === 'undefined') return;

    list.innerHTML = COMPLEX_DEMOS.map(function (demo) {
      const planChips = demo.plan.map(function (step, idx) {
        const arrow = idx < demo.plan.length - 1
          ? '<span class="arrow">→</span>'
          : '';
        return `<span class="op-tag op-${step.op}">${capitalize(step.op)}</span>
                <span style="font-size:0.83rem; color:var(--c-text-muted);">${escapeHtml(step.text)}</span>${arrow}`;
      }).join(' ');

      // Baseline comparison section
      var baselineSection = '';
      if (demo.baselines && demo.baselines.length > 0) {
        const baselineSlots = demo.baselines.map(function (b) {
          return `
            <div class="audio-slot">
              <div class="slot-label baseline-label">
                <i class="bi bi-diagram-3"></i> ${escapeHtml(b.name)}
              </div>
              <audio controls preload="none">
                <source src="${b.audio}" type="audio/wav" />
              </audio>
            </div>`;
        }).join('');
        baselineSection = `
          <div class="baseline-compare" style="margin-top:12px; padding-top:12px; border-top:1px solid var(--c-border);">
            <div style="font-size:0.78rem; color:var(--c-text-soft); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:8px; font-weight:600;">
              <i class="bi bi-bar-chart-steps"></i> Baseline Comparison
            </div>
            <div class="demo-body" style="flex-wrap:wrap;">
              ${baselineSlots}
            </div>
          </div>
        `;
      }

      return `
        <div class="demo-card">
          <div class="demo-header">
            <div class="demo-instruction">${escapeHtml(demo.instruction)}</div>
            <span class="op-tag" style="background: linear-gradient(135deg, var(--c-primary), var(--c-accent));">
              ${demo.plan.length}-step edit
            </span>
          </div>
          <div class="demo-body">
            <div class="audio-slot">
              <div class="slot-label src">
                <i class="bi bi-music-note"></i> Source
              </div>
              <audio controls preload="none">
                <source src="${demo.src}" type="audio/wav" />
              </audio>
            </div>
            <div class="audio-slot">
              <div class="slot-label edited">
                <i class="bi bi-stars"></i> QuarkAudio-Edit (Ours)
              </div>
              <audio controls preload="none">
                <source src="${demo.edited}" type="audio/wav" />
              </audio>
            </div>
          </div>
          ${baselineSection}
          <div class="cot-trace-mini">
            <strong>CoT Reasoning:</strong> ${escapeHtml(demo.cot)}
          </div>
          <div class="plan-chips">
            <strong style="font-size:0.78rem; color:var(--c-text-soft); text-transform:uppercase; letter-spacing:0.5px; margin-right:6px;">Atomic Plan:</strong>
            ${planChips}
          </div>
        </div>
      `;
    }).join('');
  }

  /* ---------- Render: Speech Demos ---------- */
  function renderSpeechDemos() {
    const grid = document.getElementById('speech-grid');
    if (!grid || typeof SPEECH_DEMOS === 'undefined') return;

    grid.innerHTML = SPEECH_DEMOS.map(function (demo) {
      return `
        <div class="demo-card">
          <div class="demo-header">
            <div class="demo-instruction">${escapeHtml(demo.instruction)}</div>
            <span class="op-tag op-${demo.op}">${demo.opLabel}</span>
          </div>
          <div class="demo-body">
            <div class="audio-slot">
              <div class="slot-label src">
                <i class="bi bi-mic"></i> Source
              </div>
              <audio controls preload="none">
                <source src="${demo.src}" type="audio/wav" />
              </audio>
            </div>
            <div class="audio-slot">
              <div class="slot-label edited">
                <i class="bi bi-stars"></i> Edited
              </div>
              <audio controls preload="none">
                <source src="${demo.edited}" type="audio/wav" />
              </audio>
            </div>
          </div>
        </div>
      `;
    }).join('');
  }

  /* ---------- Render: Baseline Comparisons ---------- */
  function renderBaselineDemos() {
    const container = document.getElementById('baseline-container');
    if (!container || typeof BASELINE_DEMOS === 'undefined') return;

    container.innerHTML = BASELINE_DEMOS.map(function (demo) {
      const outputCells = demo.outputs.map(function (out) {
        return `
          <div class="baseline-cell ${out.ours ? 'ours-cell' : ''}">
            <div class="slot-label">
              ${out.ours ? '<i class="bi bi-stars"></i> ' : ''}${escapeHtml(out.name)}
            </div>
            <audio controls preload="none">
              <source src="${out.path}" type="audio/wav" />
            </audio>
          </div>
        `;
      }).join('');

      const gtCell = demo.gt ? `
          <div class="baseline-cell" style="border-bottom: 1px solid var(--c-border); background: #f0fdf4;">
            <div class="slot-label" style="color: #16a34a;">
              <i class="bi bi-check-circle-fill"></i> Ground Truth
            </div>
            <audio controls preload="none">
              <source src="${demo.gt}" type="audio/wav" />
            </audio>
          </div>
      ` : '';

      return `
        <div class="baseline-row">
          <div class="baseline-header">
            <strong>${escapeHtml(demo.title)}</strong>
            &nbsp;·&nbsp;
            <span style="color:var(--c-text-muted); font-weight:500;">
              &ldquo;${escapeHtml(demo.instruction)}&rdquo;
            </span>
            ${demo.op ? '<span class="op-tag op-' + demo.op + '" style="margin-left:8px;">' + capitalize(demo.op) + '</span>' : ''}
          </div>
          <div class="baseline-cell" style="border-bottom: 1px solid var(--c-border); background: var(--c-bg-alt);">
            <div class="slot-label src">
              <i class="bi bi-music-note"></i> Source Audio
            </div>
            <audio controls preload="none">
              <source src="${demo.src}" type="audio/wav" />
            </audio>
          </div>
          ${gtCell}
          <div class="baseline-grid">
            ${outputCells}
          </div>
        </div>
      `;
    }).join('');
  }

  /* ---------- Render: Failure Cases ----------
     Groups FAILURE_CASES by category, renders each as a diagnostic card
     with source + failed-output audio side-by-side plus a structured
     "Expected / Observed / Diagnosis / Mitigation" breakdown, in the
     spirit of SAO-Instruct's "Failure Cases" section.
  ------------------------------------------------------------ */
  function renderFailureCases() {
    const list = document.getElementById('failure-list');
    if (!list || typeof FAILURE_CASES === 'undefined') return;

    // Group by category, preserving declaration order
    const groups = [];
    const groupIndex = {};
    FAILURE_CASES.forEach(function (item) {
      if (!(item.category in groupIndex)) {
        groupIndex[item.category] = groups.length;
        groups.push({
          category: item.category,
          label: item.categoryLabel,
          items: [],
        });
      }
      groups[groupIndex[item.category]].items.push(item);
    });

    list.innerHTML = groups.map(function (group) {
      const cardsHtml = group.items.map(function (c) {
        return `
          <div class="failure-card">
            <div class="failure-card-head">
              <span class="failure-cat failure-cat-${escapeHtml(c.category)}">
                ${escapeHtml(c.categoryLabel)}
              </span>
              <span class="failure-roadmap">${escapeHtml(c.roadmapRef)}</span>
              <h4 class="failure-title">${escapeHtml(c.title)}</h4>
            </div>

            <div class="failure-caption">
              <span class="cap-label">Caption:</span>
              <span class="cap-text">${escapeHtml(c.caption)}</span>
            </div>
            <div class="failure-instruction">
              <span class="ins-label">Instruction:</span>
              <span class="ins-text">&ldquo;${escapeHtml(c.instruction)}&rdquo;</span>
            </div>

            <div class="failure-audio-row">
              <div class="audio-slot">
                <div class="slot-label src">
                  <i class="bi bi-music-note"></i> Source
                </div>
                <audio controls preload="none">
                  <source src="${c.src}" type="audio/wav" />
                </audio>
              </div>
              <div class="audio-slot">
                <div class="slot-label failed">
                  <i class="bi bi-exclamation-triangle"></i> Failed Output
                </div>
                <audio controls preload="none">
                  <source src="${c.edited}" type="audio/wav" />
                </audio>
              </div>
            </div>

            <dl class="failure-diag">
              <dt><i class="bi bi-bullseye"></i> Expected</dt>
              <dd>${escapeHtml(c.expected)}</dd>
              <dt><i class="bi bi-eye"></i> Observed</dt>
              <dd>${escapeHtml(c.observed)}</dd>
              <dt><i class="bi bi-stethoscope"></i> Diagnosis</dt>
              <dd>${escapeHtml(c.diagnosis)}</dd>
              <dt><i class="bi bi-tools"></i> Mitigation</dt>
              <dd>${escapeHtml(c.mitigation)}</dd>
            </dl>
          </div>
        `;
      }).join('');

      return `
        <div class="failure-group" data-category="${escapeHtml(group.category)}">
          <h3 class="failure-group-title">
            <span class="fg-bar fg-bar-${escapeHtml(group.category)}"></span>
            ${escapeHtml(group.label)}
            <span class="fg-count">${group.items.length} case${group.items.length > 1 ? 's' : ''}</span>
          </h3>
          <div class="failure-group-body">
            ${cardsHtml}
          </div>
        </div>
      `;
    }).join('');
  }

  /* ---------- Tab Switching ---------- */
  function bindTabs() {
    const btns = document.querySelectorAll('.tab-btn');
    const panels = document.querySelectorAll('.tab-panel');

    btns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        const target = btn.dataset.tab;

        btns.forEach(function (b) { b.classList.remove('active'); });
        panels.forEach(function (p) { p.classList.remove('active'); });

        btn.classList.add('active');
        const panel = document.getElementById('tab-' + target);
        if (panel) panel.classList.add('active');

        // Pause all audios when switching tabs
        document.querySelectorAll('audio').forEach(function (a) { a.pause(); });
      });
    });
  }

  /* ---------- Operation Filter Chips ---------- */
  function bindOperationFilter() {
    const chips = document.querySelectorAll('.op-filter .chip');
    const cards = document.querySelectorAll('#operations-grid .demo-card');

    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        const op = chip.dataset.op;
        chips.forEach(function (c) { c.classList.remove('active'); });
        chip.classList.add('active');

        cards.forEach(function (card) {
          if (op === 'all' || card.dataset.op === op) {
            card.style.display = '';
          } else {
            card.style.display = 'none';
          }
        });
      });
    });
  }

  /* ---------- Render: External Baselines Gallery ---------- */
  function renderGallery(sourceKey) {
    const container = document.getElementById('gallery-content');
    if (!container || typeof EXTERNAL_GALLERY === 'undefined') return;

    const source = EXTERNAL_GALLERY[sourceKey];
    if (!source) return;

    const headerHtml = `
      <div class="gallery-source-header">
        <h3 class="gallery-source-title">${escapeHtml(source.label)}</h3>
        <p class="gallery-source-desc">${escapeHtml(source.description)}</p>
        <a href="${escapeHtml(source.url)}" target="_blank" rel="noopener" class="gallery-source-link">
          <i class="bi bi-box-arrow-up-right"></i> Visit Demo Page
        </a>
      </div>
    `;

    const samplesHtml = source.samples.map(function (sample) {
      const systemEntries = Object.entries(sample.systems);
      const audioCards = systemEntries.map(function (entry) {
        const systemName = entry[0];
        const audioPath = entry[1];
        const isSource = systemName.toLowerCase().includes('original') ||
                         systemName.toLowerCase().includes('source') ||
                         systemName.toLowerCase().includes('input') ||
                         systemName.toLowerCase().includes('reference');
        const labelClass = isSource ? 'src' : 'edited';
        const icon = isSource ? 'bi-music-note' : 'bi-stars';
        return `
          <div class="gallery-audio-cell">
            <div class="slot-label ${labelClass}">
              <i class="bi ${icon}"></i> ${escapeHtml(systemName)}
            </div>
            <audio controls preload="none">
              <source src="${escapeHtml(audioPath)}" />
            </audio>
          </div>
        `;
      }).join('');

      const opTag = sample.op
        ? `<span class="op-tag op-${sample.op}">${capitalize(sample.op)}</span>`
        : '';
      const instrLine = sample.instruction
        ? `<div class="gallery-instruction">&ldquo;${escapeHtml(sample.instruction)}&rdquo;</div>`
        : '';

      return `
        <div class="gallery-sample-card">
          <div class="gallery-sample-header">
            <strong>${escapeHtml(sample.title)}</strong>
            ${opTag}
          </div>
          ${instrLine}
          <div class="gallery-audio-grid">
            ${audioCards}
          </div>
        </div>
      `;
    }).join('');

    container.innerHTML = headerHtml + samplesHtml;
  }

  /* ---------- Gallery Tab Switching ---------- */
  function bindGalleryTabs() {
    const tabs = document.querySelectorAll('.gallery-tab');
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        const source = tab.dataset.source;
        tabs.forEach(function (t) { t.classList.remove('active'); });
        tab.classList.add('active');
        renderGallery(source);
        // Pause all audios
        document.querySelectorAll('audio').forEach(function (a) { a.pause(); });
      });
    });
  }

  /* ---------- Enforce Single Audio Playback ----------
     Pause all other audios when one starts playing.
  ------------------------------------------------------ */
  function enforceSingleAudioPlayback() {
    document.addEventListener('play', function (e) {
      const current = e.target;
      if (current.tagName !== 'AUDIO') return;
      document.querySelectorAll('audio').forEach(function (a) {
        if (a !== current) a.pause();
      });
    }, true);
  }

  /* ---------- Utility Helpers ---------- */
  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function capitalize(word) {
    if (!word) return '';
    return word.charAt(0).toUpperCase() + word.slice(1);
  }

  /* ---------- Image error handler (exposed globally) ----------
     When a figure fails to load, replace the <img> with a clearly-labeled
     placeholder that tells the reviewer which figure is missing and where
     to drop the file. This is intentionally *not* a silent hide. */
  window.handleImageError = function (imgEl, figureTitle) {
    if (!imgEl || imgEl.dataset.fallbackApplied === '1') return;
    imgEl.dataset.fallbackApplied = '1';

    const expectedPath = imgEl.getAttribute('src') || '';
    const fallback = document.createElement('div');
    fallback.className = 'figure-fallback';
    fallback.innerHTML =
      '<i class="bi bi-image fallback-icon"></i>' +
      '<div class="fallback-title">' + escapeHtmlPlain(figureTitle || 'Figure') + '</div>' +
      '<div class="fallback-hint">Expected asset: ' + escapeHtmlPlain(expectedPath) + '</div>';

    if (imgEl.parentNode) {
      imgEl.parentNode.replaceChild(fallback, imgEl);
    }
  };

  function escapeHtmlPlain(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  /* ---------- BibTeX Copy (exposed globally) ---------- */
  window.copyBibtex = function () {
    const bib = document.getElementById('bibtex');
    const btn = document.querySelector('.copy-btn');
    if (!bib || !btn) return;

    const text = bib.innerText;
    const finalize = function () {
      btn.innerHTML = '<i class="bi bi-check2"></i> Copied';
      btn.classList.add('copied');
      setTimeout(function () {
        btn.innerHTML = '<i class="bi bi-clipboard"></i> Copy';
        btn.classList.remove('copied');
      }, 1800);
    };

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(finalize).catch(function () {
        fallbackCopy(text, finalize);
      });
    } else {
      fallbackCopy(text, finalize);
    }
  };

  function fallbackCopy(text, finalize) {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch (e) { /* noop */ }
    document.body.removeChild(ta);
    finalize();
  }
})();
