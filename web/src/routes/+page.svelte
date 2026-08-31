<script lang="ts">
  import { onMount } from 'svelte';
  import { base } from '$app/paths';
  import { GROUPS, GROUP_ICON_STRING, BRAND_SYMBOLS } from '$lib/groups';

  const FAMILY = 'MIT Media Lab Font';
  const PS = 'MITMediaLabFont';
  const MIT_MARK = BRAND_SYMBOLS[0].icon;
  const ML_MARK = BRAND_SYMBOLS[1].icon;

  const WEIGHTS = [
    { name: 'Thin',    w: 100 },
    { name: 'Light',   w: 300 },
    { name: 'Regular', w: 400 },
    { name: 'Medium',  w: 500 },
    { name: 'Bold',    w: 700 },
    { name: 'Black',   w: 900 },
  ];

  const CHARSET =
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' +
    '.,:;!?-_/()[]{}<>+=*&@#"\'`$%^|~' +
    '·×©‘’“”–—−…•°±÷≤≥≠≈¹²³µπ′″' +
    '®™€£¿¡§←→↑↓∞√∑∏∂½¼¾' +
    'áéíóúàèùäëïöüñçÁÉÍÓÚÄÖÜÑßæœÆŒ';

  const SPECIMEN = [
    { label: 'Pangram', text: 'The quick brown fox jumps over the lazy dog.' },
    { label: 'Accents', text: 'ÁÉÍÓÚÑ äëïöü ñ ç ß æ œ — café résumé naïve' },
    { label: 'Science', text: 'T = 25°C  ±0.1  π ≈ 3.1416  ∑x²  √2  ∞  ≤ ≥ ≠' },
    { label: 'Figures', text: '0123456789  $98.50  ½ ¼ ¾  10×20÷5' },
  ];

  let sample = $state(`${String.fromCodePoint(0xE030)} MEDIA LAB`);
  let size = $state(120);
  let weight = $state(700);
  let tracking = $state(0);
  let groupWeight = $state(700);
  let copied: string | null = $state(null);

  type Theme = 'light' | 'dark' | 'system';
  let theme: Theme = $state('system');

  onMount(() => {
    const stored = (localStorage.getItem('mlf-theme') as Theme | null) ?? 'system';
    theme = stored;
  });

  function setTheme(next: Theme) {
    theme = next;
    document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem('mlf-theme', next); } catch (_) {}
  }

  async function copyText(text: string, key: string) {
    try {
      await navigator.clipboard.writeText(text);
      copied = key;
      setTimeout(() => { if (copied === key) copied = null; }, 1600);
    } catch (_) {}
  }

  function loadGroupSample(g: (typeof GROUPS)[number]) {
    sample = `${g.icon}  ${g.name.toUpperCase()}`;
  }

  const CITE_APA =
    'Kosmyna, N., & Hauptmann, E. (2026). MIT Media Lab Font [Typeface]. MIT Media Lab. https://creativecommons.org/licenses/by-nc-sa/4.0/';

  const CITE_CHICAGO =
    'Kosmyna, Nataliya, and Eugene Hauptmann. 2026. MIT Media Lab Font. Typeface. MIT Media Lab. Licensed under CC BY-NC-SA 4.0.';

  const CITE_BIBTEX = `@software{kosmyna2026mlfont,
  author       = {Kosmyna, Nataliya and Hauptmann, Eugene},
  title        = {{MIT Media Lab Font}},
  year         = {2026},
  organization = {MIT Media Lab},
  license      = {CC BY-NC-SA 4.0},
  url          = {https://creativecommons.org/licenses/by-nc-sa/4.0/},
  note         = {7×7 grid typeface; non-commercial use}
}`;

  const CITE_ATTRIBUTION =
    'MIT Media Lab Font © 2026 Nataliya Kosmyna & Eugene Hauptmann, MIT Media Lab. Licensed under CC BY-NC-SA 4.0.';
</script>

<div class="page-bg" aria-hidden="true">
  <div class="page-bg-mosaic">
    {#each [0, 1, 2] as _}
      {#each GROUPS as g}
        <span class:mit-fit={g.slug === 'mit'}>{g.icon}</span>
      {/each}
    {/each}
  </div>
  <div class="page-bg-fade"></div>
</div>

<main>
  <header class="masthead">
    <div class="masthead-row">
      <div class="mark" aria-hidden="true" title="MIT Media Lab">
        <svg viewBox="0 0 7 7" role="img">
          <defs>
            <mask id="ml-mark-mask">
              <rect width="7" height="7" fill="#fff"/>
              <rect x="0" y="0" width="4" height="1" fill="#000"/>
              <rect x="3" y="1" width="1" height="2" fill="#000"/>
              <rect x="3" y="3" width="4" height="1" fill="#000"/>
              <rect x="6" y="3" width="1" height="4" fill="#000"/>
              <rect x="0" y="3" width="1" height="4" fill="#000"/>
              <rect x="0" y="6" width="4" height="1" fill="#000"/>
            </mask>
          </defs>
          <rect width="7" height="7" fill="currentColor" mask="url(#ml-mark-mask)"/>
        </svg>
      </div>
      <h1>
        <span class="brand-inline mit-text" aria-hidden="true">{MIT_MARK}</span>
        <span class="sr-only">MIT </span>
        <span class="title-text">Media Lab Font</span>
      </h1>
      <div class="masthead-actions">
        <div class="theme-toggle" role="group" aria-label="Theme">
          <button
            type="button"
            class:active={theme === 'light'}
            aria-pressed={theme === 'light'}
            onclick={() => setTheme('light')}
          >Light</button>
          <button
            type="button"
            class:active={theme === 'dark'}
            aria-pressed={theme === 'dark'}
            onclick={() => setTheme('dark')}
          >Dark</button>
          <button
            type="button"
            class:active={theme === 'system'}
            aria-pressed={theme === 'system'}
            onclick={() => setTheme('system')}
          >System</button>
        </div>
        <a class="download-all" href="{base}/{PS}.zip" download>
          <span class="dl-arrow">↓</span>
          <span class="dl-stack">
            <span class="dl-title">Download font</span>
            <span class="dl-sub">all 6 weights · TTF + OTF · zip</span>
          </span>
        </a>
      </div>
    </div>
    <p class="tag">A 7&times;7 grid typeface in the spirit of the Media Lab generative identity.</p>
  </header>

  <section class="hero">
    <div class="hero-brands" aria-label="Brand marks">
      <div class="hero-brand">
        <span class="hero-mark mit-fit">{MIT_MARK}</span>
        <div class="hero-brand-meta">
          <span class="hero-brand-label">MIT</span>
          <span class="hero-brand-cp">U+E030</span>
        </div>
      </div>
      <div class="hero-brand">
        <span class="hero-mark">{ML_MARK}</span>
        <div class="hero-brand-meta">
          <span class="hero-brand-label">Media Lab</span>
          <span class="hero-brand-cp">U+E031</span>
        </div>
      </div>
    </div>
    <div class="hero-text">
      <span class="hero-line hero-line-mit" aria-label="MIT">{MIT_MARK}</span>
      <span class="hero-line hero-line-media">MEDIA</span>
      <span class="hero-line hero-line-lab">LAB</span>
    </div>
  </section>

  <section class="controls">
    <label>
      <span>sample</span>
      <input type="text" bind:value={sample} />
    </label>
    <label>
      <span>size {size}px</span>
      <input type="range" min="70" max="220" step="10" bind:value={size} />
    </label>
    <label>
      <span>weight {weight}</span>
      <input type="range" min="100" max="900" step="100" bind:value={weight} />
    </label>
    <label>
      <span>tracking {tracking}</span>
      <input type="range" min="-2" max="40" step="1" bind:value={tracking} />
    </label>
  </section>

  <section class="playground">
    <div
      class="play-text"
      style="font-size: {size}px; font-weight: {weight}; letter-spacing: {tracking / 100}em;"
    >
      {sample || ' '}
    </div>
  </section>

  <section class="weights">
    <h2>Weights</h2>
    {#each WEIGHTS as w}
      <div class="weight-row">
        <div class="meta">
          <div class="meta-name">{w.name}</div>
          <div class="meta-num">{w.w}</div>
        </div>
        <div class="weight-sample" style="font-weight: {w.w};">
          THE QUICK BROWN FOX
        </div>
      </div>
    {/each}
  </section>

  <section class="sizes">
    <h2>Sizes</h2>
    {#each [12, 18, 24, 36, 56, 84, 128] as s}
      <div class="size-row" style="font-size: {s}px;">
        <span class="size-label">{s}</span>
        ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789
      </div>
    {/each}
  </section>

  <section class="groups">
    <h2>Research group symbols</h2>
    <p class="meta-line">
      Brand marks <span class="brand-inline mit-text">{MIT_MARK}</span> (U+E030, full wordmark) and <strong>Media Lab</strong> (U+E031),
      then all 24 research group square <strong>icons</strong> (U+E000–U+E017),
      traced from each group&rsquo;s
      <a href="https://www.media.mit.edu/research/?filter=groups_centers">overview page</a>.
    </p>

    <div class="group-toolbar">
      <label>
        <span>symbol weight {groupWeight}</span>
        <input type="range" min="100" max="900" step="100" bind:value={groupWeight} />
      </label>
      <div class="toolbar-actions">
        <button type="button" onclick={() => copyText(GROUP_ICON_STRING, 'all-icons')}>
          {copied === 'all-icons' ? 'Copied icons' : 'Copy all icons'}
        </button>
      </div>
    </div>

    <h3 class="subhead">Icon mosaic</h3>
    <div class="mosaic" style="font-weight: {groupWeight};" aria-label="All group icons">
      {#each GROUPS as g, i}
        <span class="mosaic-cell" class:mit-fit={i === 0} title={g.name}>{g.icon}</span>
      {/each}
    </div>

    <h3 class="subhead">Each group</h3>
    <div class="group-list">
      {#each GROUPS as g}
        <article class="group-row">
          <div class="group-mark">
            <div
              class="group-icon"
              class:mit-fit={g.slug === 'mit'}
              style="font-weight: {groupWeight};"
              title={g.name}
            >{g.icon}</div>
          </div>
          <div class="group-copy">
            <h4 class="group-title">
              <a href={g.url} target="_blank" rel="noopener noreferrer">{g.name}</a>
            </h4>
            <p class="group-tagline">{g.tagline}</p>
            <div class="code-row">
              <span class="code-label">Icon</span>
              <code>{g.iconCp}</code>
              <button type="button" onclick={() => copyText(g.icon, g.slug + '-icon')}>
                {copied === g.slug + '-icon' ? 'Copied' : 'Copy'}
              </button>
            </div>
            <button type="button" class="try-btn" onclick={() => loadGroupSample(g)}>
              Try in playground
            </button>
          </div>
        </article>
      {/each}
    </div>
  </section>

  <section class="specimen">
    <h2>Specimen</h2>
    <div class="specimen-list">
      {#each SPECIMEN as row}
        <div class="specimen-row">
          <div class="specimen-label">{row.label}</div>
          <div class="specimen-text" style="font-weight: {weight};">{row.text}</div>
        </div>
      {/each}
    </div>
  </section>

  <section class="charset">
    <h2>Character set</h2>
    <div class="grid">
      {#each [...CHARSET] as ch}
        <div class="cell">
          <div class="glyph">{ch}</div>
          <div class="cp">U+{ch.charCodeAt(0).toString(16).padStart(4, '0').toUpperCase()}</div>
        </div>
      {/each}
    </div>
  </section>

  <section class="downloads">
    <h2>Downloads</h2>
    <p class="meta-line">
      Grab the full family as a single archive, or pick individual weights below.
      Each weight ships as both <strong>TTF</strong> and <strong>OTF</strong>.
    </p>
    <div class="dl-bundle">
      <a class="bundle-link" href="{base}/{PS}.zip" download="{PS}.zip">
        <span class="bundle-name"><span class="mit-text">{MIT_MARK}</span><span>Media Lab Font.zip</span></span>
        <span class="bundle-meta">all 6 weights · TTF + OTF</span>
      </a>
    </div>
    <div class="dl-grid">
      {#each WEIGHTS as w}
        <div class="dl-card">
          <div class="dl-name" style="font-weight: {Math.max(w.w, 400)};">
            <span class="mit-text">{MIT_MARK}</span>
            <span>Media Lab Font {w.name}</span>
          </div>
          <div class="dl-links">
            <a href="{base}/fonts/{PS}-{w.name}.ttf" download>TTF</a>
            <a href="{base}/fonts/{PS}-{w.name}.otf" download>OTF</a>
          </div>
        </div>
      {/each}
    </div>
  </section>

  <section class="about">
    <h2>Authors &amp; license</h2>
    <div class="about-grid">
      <article class="about-card">
        <h3>Authors</h3>
        <ul class="about-authors">
          <li>
            <a href="mailto:nkosmyna@mit.edu">Nataliya Kosmyna</a>
            <span class="about-meta"><span class="brand-inline mit-text">{MIT_MARK}</span> Media Lab</span>
          </li>
          <li>
            <a href="mailto:eugenehp@mit.edu">Eugene Hauptmann</a>
            <span class="about-meta"><span class="brand-inline mit-text">{MIT_MARK}</span> Media Lab</span>
          </li>
        </ul>
      </article>
      <article class="about-card">
        <h3>License</h3>
        <p class="about-license">
          <a href="{base}/LICENSE.txt">CC BY-NC-SA 4.0</a>
          — Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International.
          Free to share and adapt with attribution; non-commercial use only; derivatives must use the same license.
        </p>
        <p class="about-year">&copy; 2026 Nataliya Kosmyna &amp; Eugene Hauptmann</p>
      </article>
    </div>
  </section>

  <section class="cite">
    <h2>How to cite</h2>
    <p class="meta-line">
      This work is licensed
      <a href="{base}/LICENSE.txt">CC BY-NC-SA 4.0</a>
      (attribution required; non-commercial; share-alike).
      Use one of the forms below in papers, theses, software, or other works.
    </p>

    <div class="cite-list">
      <article class="cite-card">
        <div class="cite-head">
          <h3>APA</h3>
          <button type="button" onclick={() => copyText(CITE_APA, 'cite-apa')}>
            {copied === 'cite-apa' ? 'Copied' : 'Copy'}
          </button>
        </div>
        <pre class="cite-block">{CITE_APA}</pre>
      </article>

      <article class="cite-card">
        <div class="cite-head">
          <h3>Chicago</h3>
          <button type="button" onclick={() => copyText(CITE_CHICAGO, 'cite-chicago')}>
            {copied === 'cite-chicago' ? 'Copied' : 'Copy'}
          </button>
        </div>
        <pre class="cite-block">{CITE_CHICAGO}</pre>
      </article>

      <article class="cite-card">
        <div class="cite-head">
          <h3>BibTeX</h3>
          <button type="button" onclick={() => copyText(CITE_BIBTEX, 'cite-bibtex')}>
            {copied === 'cite-bibtex' ? 'Copied' : 'Copy'}
          </button>
        </div>
        <pre class="cite-block">{CITE_BIBTEX}</pre>
      </article>

      <article class="cite-card">
        <div class="cite-head">
          <h3>Short attribution</h3>
          <button type="button" onclick={() => copyText(CITE_ATTRIBUTION, 'cite-attr')}>
            {copied === 'cite-attr' ? 'Copied' : 'Copy'}
          </button>
        </div>
        <pre class="cite-block">{CITE_ATTRIBUTION}</pre>
        <p class="cite-note">
          For acknowledgments, colophons, README files, figure captions, or UI credits
          when the font or its symbols appear in another project.
        </p>
      </article>
    </div>
  </section>

  <footer>
    <p class="foot-line">
      <a href="{base}/LICENSE.txt">CC BY-NC-SA 4.0</a>
      &nbsp;&middot;&nbsp; &copy; 2026
      <a href="mailto:nkosmyna@mit.edu">Nataliya Kosmyna</a>
      &amp;
      <a href="mailto:eugenehp@mit.edu">Eugene Hauptmann</a>
      &nbsp;&middot;&nbsp; <span class="brand-inline mit-text">{MIT_MARK}</span> Media Lab
    </p>
  </footer>
</main>

<style>
  .page-bg {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    overflow: hidden;
  }
  /* Layer 1 — group glyphs */
  .page-bg-mosaic {
    display: grid;
    grid-template-columns: repeat(13, minmax(0, 1fr));
    gap: 32px 28px;
    justify-items: center;
    align-items: center;
    padding: 48px 40px;
    width: 100%;
    min-height: 100%;
    font-family: 'MIT Media Lab Font', monospace;
    font-size: clamp(40px, 5.5vw, 68px);
    font-weight: 700;
    line-height: 1;
    color: var(--fg);
    opacity: 0.18;
    -webkit-font-smoothing: none;
    user-select: none;
  }
  /* Layer 2 — gradient between mosaic and page content (must stay behind main) */
  .page-bg-fade {
    position: absolute;
    inset: 0;
    background:
      linear-gradient(
        90deg,
        transparent 0%,
        color-mix(in srgb, var(--bg) 40%, transparent) 10%,
        color-mix(in srgb, var(--bg) 92%, transparent) 22%,
        color-mix(in srgb, var(--bg) 96%, transparent) 50%,
        color-mix(in srgb, var(--bg) 92%, transparent) 78%,
        color-mix(in srgb, var(--bg) 40%, transparent) 90%,
        transparent 100%
      ),
      linear-gradient(
        180deg,
        color-mix(in srgb, var(--bg) 70%, transparent) 0%,
        color-mix(in srgb, var(--bg) 25%, transparent) 14%,
        transparent 28%,
        transparent 72%,
        color-mix(in srgb, var(--bg) 50%, transparent) 88%,
        color-mix(in srgb, var(--bg) 92%, transparent) 100%
      );
  }

  main {
    position: relative;
    z-index: 1;
    max-width: 1100px;
    width: 100%;
    margin: 0 auto;
    padding: 48px 32px 96px;
    overflow-x: hidden;
  }
  .masthead {
    --masthead-title: 36px;
    --masthead-gap: 16px;
    --masthead-mark: calc(var(--masthead-title) * 0.7);
    padding: 0 0 28px;
    border-bottom: 1px solid var(--line);
    min-width: 0;
  }
  .masthead-row {
    display: flex;
    align-items: center;
    gap: var(--masthead-gap);
    min-width: 0;
  }
  .mark {
    width: var(--masthead-mark);
    height: var(--masthead-mark);
    color: var(--fg);
    flex-shrink: 0;
  }
  .mark svg {
    width: 100%;
    height: 100%;
    display: block;
    shape-rendering: crispEdges;
  }
  .masthead h1 {
    flex: 1;
    min-width: 0;
    font-size: var(--masthead-title);
    font-weight: 900;
    letter-spacing: 0.04em;
    margin: 0;
    display: flex;
    align-items: baseline;
    flex-wrap: wrap;
    column-gap: 0.28em;
    row-gap: 0.08em;
    line-height: 1;
  }
  .masthead h1 .brand-inline {
    letter-spacing: 0;
  }
  .masthead h1 .mit-text {
    line-height: 1;
    flex: 0 0 auto;
    margin-inline-end: 0.04em;
  }
  .masthead h1 .title-text {
    letter-spacing: inherit;
  }
  .tag {
    margin: 8px 0 0 calc(var(--masthead-mark) + var(--masthead-gap));
    color: var(--muted);
    font-weight: 400;
    font-size: 13px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    line-height: 1.35;
    max-width: 42em;
  }
  .masthead-actions {
    display: flex;
    align-items: center;
    gap: 14px;
    flex-shrink: 0;
    margin-left: auto;
  }
  .theme-toggle {
    display: inline-flex;
    border: 1px solid var(--line);
    background: var(--surface);
  }
  .theme-toggle button {
    appearance: none;
    background: transparent;
    border: 0;
    border-left: 1px solid var(--line);
    padding: 8px 12px;
    font-family: ui-monospace, monospace;
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    cursor: pointer;
  }
  .theme-toggle button:first-child { border-left: 0; }
  .theme-toggle button:hover { color: var(--fg); }
  .theme-toggle button.active {
    background: var(--accent);
    color: #ffffff;
  }
  .download-all {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 8px 14px;
    background: var(--accent);
    color: #ffffff;
    border: 1px solid var(--accent);
    text-decoration: none;
    transition: background 120ms ease, border-color 120ms ease;
  }
  .download-all:hover { background: var(--accent-hover); border-color: var(--accent-hover); text-decoration: none; }
  .dl-arrow { font-size: 18px; line-height: 1; font-weight: 700; }
  .dl-stack { display: flex; flex-direction: column; line-height: 1.1; }
  .dl-title { font-size: 12px; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; }
  .dl-sub {
    font-family: ui-monospace, monospace;
    font-size: 10px;
    opacity: 0.7;
    letter-spacing: 0.05em;
  }

  .hero {
    position: relative;
    padding: 64px 0 56px;
    display: grid;
    grid-template-columns: auto minmax(0, 1fr);
    align-items: start;
    gap: 40px 56px;
    min-width: 0;
  }
  .hero-brands {
    --mark-ink-h: clamp(48px, 7vw, 80px);
    --mark-slot-w: calc(var(--mark-ink-h) * 119 / 63);
    display: flex;
    flex-direction: column;
    gap: 36px;
    min-width: 0;
    padding-top: 0.055em;
  }
  .hero-brand {
    display: grid;
    grid-template-columns: var(--mark-slot-w) minmax(0, 1fr);
    column-gap: 22px;
    align-items: center;
  }
  .hero-mark {
    grid-column: 1;
    grid-row: 1;
    font-family: 'MIT Media Lab Font', monospace;
    font-weight: 900;
    line-height: 1;
    color: var(--fg);
    -webkit-font-smoothing: none;
    display: block;
    justify-self: start;
  }
  /* Square Media Lab mark — ink height = cap (0.7 em) */
  .hero-mark:not(.mit-fit) {
    font-size: calc(var(--mark-ink-h) / 0.7);
    line-height: 0.7;
  }
  /* MIT wordmark — same ink height as square mark */
  .hero-mark.mit-fit {
    font-size: calc(var(--mark-ink-h) / 0.88);
    line-height: 0.88;
  }
  .hero-brand-meta {
    grid-column: 2;
    grid-row: 1;
    display: flex;
    flex-direction: column;
    gap: 5px;
    min-width: 5.5em;
  }
  .hero-brand-label {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    line-height: 1.25;
  }
  .hero-brand-cp {
    font-family: ui-monospace, monospace;
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 0.04em;
    line-height: 1.25;
  }
  .hero-text {
    display: grid;
    grid-template-columns: minmax(0, max-content);
    row-gap: 0.06em;
    font-size: clamp(48px, 9.2vw, 128px);
    font-weight: 900;
    line-height: 1;
    color: var(--fg);
    min-width: 0;
    max-width: 100%;
    padding-top: 0.055em;
    padding-inline-end: 0.06em;
  }
  .hero-line {
    display: block;
    line-height: 1;
    letter-spacing: 0.02em;
  }
  .hero-line-mit {
    letter-spacing: 0;
  }
  .brand-inline {
    font-weight: 900;
    letter-spacing: 0;
  }
  .mit-text {
    display: inline-block;
    font-size: 1em;
    font-weight: 900;
    line-height: 1;
    letter-spacing: 0;
    vertical-align: -0.05em;
  }
  .mosaic-cell.mit-fit {
    font-size: calc(48px * 63 / 119);
  }
  .group-icon.mit-fit {
    font-size: calc(64px * 63 / 119);
  }
  .page-bg-mosaic .mit-fit {
    font-size: calc(1em * 63 / 119);
  }
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }

  .controls {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    gap: 18px;
    padding: 24px;
    background: var(--surface);
    border: 1px solid var(--line);
    margin-bottom: 24px;
  }
  .controls label {
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-family: ui-monospace, monospace;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
  }
  .controls input[type='text'] {
    font-family: 'MIT Media Lab Font', monospace;
    font-size: 16px;
    padding: 8px 10px;
    border: 1px solid var(--line);
    background: var(--bg);
    color: var(--fg);
  }
  .controls input[type='range'] { accent-color: var(--accent); }

  .playground {
    padding: 32px 24px;
    background: var(--surface);
    border: 1px solid var(--line);
    overflow-x: auto;
    margin-bottom: 48px;
    min-height: 220px;
    display: flex;
    align-items: center;
  }
  .play-text {
    line-height: 1;
    white-space: nowrap;
    -webkit-font-smoothing: none;
    font-smooth: never;
    text-rendering: geometricPrecision;
  }

  section h2 {
    font-family: ui-monospace, monospace;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: var(--muted);
    margin: 48px 0 16px;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--line);
  }
  h3.subhead {
    font-family: ui-monospace, monospace;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--muted);
    margin: 28px 0 12px;
    font-weight: 400;
  }

  .weight-row {
    display: grid;
    grid-template-columns: 120px 1fr;
    align-items: baseline;
    gap: 16px;
    padding: 12px 0;
    border-bottom: 1px solid var(--line);
  }
  .meta {
    font-family: ui-monospace, monospace;
    font-size: 11px;
    color: var(--muted);
  }
  .meta-name {
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--fg);
  }
  .meta-num { color: var(--muted); }
  .weight-sample {
    font-size: 36px;
    letter-spacing: 0.02em;
    line-height: 1;
    min-width: 0;
    overflow: hidden;
  }

  .size-row {
    padding: 10px 0;
    border-bottom: 1px solid var(--line);
    line-height: 1.1;
    display: flex;
    align-items: baseline;
    gap: 16px;
    font-weight: 400;
    min-width: 0;
    overflow-x: auto;
  }
  .size-label {
    font-family: ui-monospace, monospace;
    font-size: 11px;
    color: var(--muted);
    flex: 0 0 36px;
    text-align: right;
  }

  .specimen-list {
    display: flex;
    flex-direction: column;
    gap: 0;
  }
  .specimen-row {
    display: grid;
    grid-template-columns: 88px 1fr;
    gap: 16px;
    align-items: baseline;
    padding: 18px 0;
    border-bottom: 1px solid var(--line);
  }
  .specimen-label {
    font-family: ui-monospace, monospace;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
  }
  .specimen-text {
    font-size: clamp(22px, 3.2vw, 36px);
    line-height: 1.25;
    letter-spacing: 0.01em;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(72px, 1fr));
    gap: 1px;
    background: var(--line);
    border: 1px solid var(--line);
  }
  .cell {
    background: var(--surface);
    aspect-ratio: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    padding: 8px 4px;
  }
  .glyph {
    font-size: 36px;
    font-weight: 700;
    line-height: 1;
  }
  .cp {
    font-family: ui-monospace, monospace;
    font-size: 9px;
    color: var(--muted);
  }

  .group-toolbar {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    justify-content: space-between;
    gap: 16px;
    padding: 16px 18px;
    background: var(--surface);
    border: 1px solid var(--line);
    margin-bottom: 8px;
  }
  .group-toolbar label {
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-family: ui-monospace, monospace;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    min-width: 200px;
  }
  .group-toolbar input[type='range'] { accent-color: var(--accent); width: 100%; }
  .toolbar-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  .toolbar-actions button,
  .code-row button,
  .try-btn {
    appearance: none;
    font-family: ui-monospace, monospace;
    font-size: 10px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 8px 12px;
    border: 1px solid var(--line);
    background: var(--surface);
    color: var(--fg);
    cursor: pointer;
  }
  .toolbar-actions button:hover,
  .code-row button:hover,
  .try-btn:hover {
    border-color: var(--accent);
    color: var(--accent);
  }

  .mosaic {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(56px, 1fr));
    gap: 1px;
    background: var(--line);
    border: 1px solid var(--line);
    padding: 0;
    margin-bottom: 8px;
    font-family: 'MIT Media Lab Font', monospace;
  }
  .mosaic-cell {
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--surface);
    font-size: 48px;
    line-height: 1;
    aspect-ratio: 1;
    padding: 8px;
    font-family: inherit;
  }

  .group-list {
    display: flex;
    flex-direction: column;
    gap: 1px;
    background: var(--line);
    border: 1px solid var(--line);
  }
  .group-row {
    display: grid;
    grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr);
    gap: 0;
    background: var(--surface);
  }
  .group-mark {
    display: flex;
    align-items: center;
    padding: 20px 18px;
    border-right: 1px solid var(--line);
    min-width: 0;
    font-family: 'MIT Media Lab Font', monospace;
  }
  .group-icon {
    font-size: 64px;
    line-height: 1;
    width: fit-content;
    font-family: inherit;
  }
  .group-copy {
    padding: 20px 18px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    min-width: 0;
  }
  .group-title {
    margin: 0;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    line-height: 1.2;
  }
  .group-title a {
    color: var(--fg);
    text-decoration: none;
  }
  .group-title a:hover { color: var(--accent); text-decoration: underline; }
  .group-tagline {
    margin: 0;
    font-family: ui-monospace, monospace;
    font-size: 11px;
    line-height: 1.5;
    color: var(--muted);
    white-space: pre-line;
  }
  .code-row {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    font-family: ui-monospace, monospace;
    font-size: 11px;
  }
  .code-label {
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    min-width: 48px;
  }
  .code-row code {
    color: var(--fg);
    background: var(--bg);
    border: 1px solid var(--line);
    padding: 4px 8px;
  }
  .try-btn {
    align-self: flex-start;
    margin-top: 4px;
  }

  .meta-line {
    font-family: ui-monospace, monospace;
    font-size: 12px;
    color: var(--muted);
    margin: 0 0 16px;
    line-height: 1.5;
  }
  .dl-bundle { margin-bottom: 18px; }
  .bundle-link {
    display: inline-flex;
    flex-direction: column;
    justify-content: center;
    padding: 18px 22px;
    background: var(--accent);
    color: #ffffff;
    border: 1px solid var(--accent);
    text-decoration: none;
    gap: 6px;
    transition: background 120ms ease, border-color 120ms ease;
  }
  .bundle-link:hover { background: var(--accent-hover); border-color: var(--accent-hover); text-decoration: none; }
  .bundle-name {
    font-family: 'MIT Media Lab Font', monospace;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 0.02em;
    display: flex;
    align-items: center;
    gap: 0.35em;
    line-height: 1;
  }
  .bundle-meta {
    font-family: ui-monospace, monospace;
    font-size: 10px;
    opacity: 0.7;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }
  .dl-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 12px;
  }
  .dl-card {
    background: var(--surface);
    border: 1px solid var(--line);
    padding: 18px 20px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .dl-name {
    font-size: 22px;
    line-height: 1;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.35em;
  }
  .dl-name .mit-text,
  .bundle-name .mit-text {
    flex-shrink: 0;
  }
  .dl-links {
    display: flex;
    gap: 12px;
    font-family: ui-monospace, monospace;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }

  .about-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
  }
  .about-card {
    background: var(--surface);
    border: 1px solid var(--line);
    padding: 22px 24px;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }
  .about-card h3 {
    margin: 0;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
  }
  .about-authors {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }
  .about-authors li {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .about-authors a {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.02em;
    color: var(--fg);
  }
  .about-authors a:hover { color: var(--accent); }
  .about-meta {
    font-family: ui-monospace, monospace;
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }
  .about-license {
    margin: 0;
    font-size: 14px;
    line-height: 1.55;
    color: var(--fg);
  }
  .about-year {
    margin: 0;
    font-family: ui-monospace, monospace;
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 0.04em;
  }

  .cite-list {
    display: flex;
    flex-direction: column;
    gap: 14px;
  }
  .cite-card {
    background: var(--surface);
    border: 1px solid var(--line);
    padding: 18px 20px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .cite-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }
  .cite-head h3 {
    margin: 0;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }
  .cite-block {
    margin: 0;
    padding: 14px 16px;
    background: var(--bg);
    border: 1px solid var(--line);
    font-family: ui-monospace, monospace;
    font-size: 12px;
    line-height: 1.55;
    white-space: pre-wrap;
    word-break: break-word;
    color: var(--fg);
  }
  .cite-note {
    margin: 0;
    font-family: ui-monospace, monospace;
    font-size: 11px;
    color: var(--muted);
    line-height: 1.5;
  }

  footer {
    margin-top: 80px;
    padding-top: 24px;
    border-top: 1px solid var(--line);
    font-family: ui-monospace, monospace;
    font-size: 12px;
    color: var(--muted);
  }
  .foot-line {
    margin: 0;
    color: var(--muted);
    text-align: center;
    letter-spacing: 0.04em;
  }
  .foot-line a { color: var(--fg); }

  @media (max-width: 720px) {
    .masthead-row {
      flex-wrap: wrap;
      row-gap: 12px;
    }
    .masthead h1 {
      flex: 1 1 calc(100% - var(--masthead-mark) - var(--masthead-gap));
    }
    .masthead-actions {
      width: 100%;
      margin-left: 0;
      flex-wrap: wrap;
    }
    .tag {
      margin-left: 0;
    }
    .hero {
      grid-template-columns: 1fr;
      gap: 28px;
      padding: 40px 0 32px;
    }
    .hero-brands {
      flex-direction: row;
      flex-wrap: wrap;
      gap: 24px 32px;
      --mark-ink-h: 56px;
      padding-top: 0;
    }
    .hero-brand {
      flex: 1 1 200px;
    }
    .hero-text {
      font-size: clamp(64px, 17vw, 96px);
      padding-top: 0;
      padding-inline-end: 0;
    }
    .controls { grid-template-columns: 1fr 1fr; }
    .weight-row { grid-template-columns: 80px 1fr; }
    .weight-sample { font-size: 24px; }
    .group-row { grid-template-columns: 1fr; }
    .group-mark { border-right: 0; border-bottom: 1px solid var(--line); }
    .group-icon { font-size: 48px; }
    .group-icon.mit-fit { font-size: calc(48px * 63 / 119); }
    .about-grid { grid-template-columns: 1fr; }
    .page-bg-mosaic {
      grid-template-columns: repeat(8, minmax(0, 1fr));
      gap: 22px 16px;
      font-size: 40px;
      opacity: 0.16;
    }
  }
</style>
