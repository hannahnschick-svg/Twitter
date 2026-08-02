/* Chronogene Institute — Board Console renderer.
   Renders the console entirely from a state object with the schema in
   web/data/console.json. Load order:
     1. window.CONSOLE_DATA  (data/console.js, works from file://)
     2. fetch('data/console.json')  (when served over http)
   The backend regenerates both files each cycle. */

const el = (tag, cls, html) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (html != null) n.innerHTML = html;
  return n;
};

// Minimal, safe inline markup: escape everything, then re-enable **bold** and \n.
const fmt = (s) => {
  if (s == null) return "";
  const esc = String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  return esc.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
};

const slug = (s) => String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

function sectionHead(title, meta) {
  const h = el("div", "section-head");
  h.appendChild(el("h2", null, fmt(title)));
  if (meta) h.appendChild(el("span", "meta", fmt(meta)));
  return h;
}

function renderMasthead(d) {
  const m = el("header", "masthead");
  m.appendChild(el("h1", null, `${fmt(d.institute)} <span class="sub">${fmt(d.subtitle)}</span>`));
  m.appendChild(el("span", "clock", fmt(d.generated_at)));
  return m;
}

function renderDirector(n) {
  const c = el("section", "director");
  const top = el("div", "director-top");
  top.appendChild(el("div", "avatar", fmt(n.avatar)));
  const id = el("div", "director-id");
  id.appendChild(el("div", "name", fmt(n.name)));
  id.appendChild(el("div", "subtitle", fmt(n.subtitle)));
  top.appendChild(id);
  c.appendChild(top);
  const body = el("div", "director-body");
  (n.paragraphs || []).forEach((p) => body.appendChild(el("p", null, fmt(p))));
  c.appendChild(body);
  return c;
}

function renderDecision(dec) {
  const c = el("section", "decision");
  const badges = el("div", "badges");
  badges.appendChild(el("span", "pill pill-needs", `<span class="dot">●</span>${fmt(dec.status)}`));
  if (dec.tag) badges.appendChild(el("span", "pill pill-tag", fmt(dec.tag)));
  if (dec.waiting) badges.appendChild(el("span", "waiting", fmt(dec.waiting)));
  c.appendChild(badges);
  c.appendChild(el("h3", null, fmt(dec.title)));
  c.appendChild(el("p", "lead", fmt(dec.description)));

  const opts = el("div", "options");
  (dec.options || []).forEach((o) => {
    const row = el("div", "option");
    row.appendChild(el("span", "key", fmt(o.key)));
    row.appendChild(el("span", "otext", fmt(o.text)));
    opts.appendChild(row);
  });
  c.appendChild(opts);

  if (dec.if_nothing) {
    c.appendChild(el("div", "if-nothing", `<strong>If you do nothing:</strong> ${fmt(dec.if_nothing)}`));
  }

  const actions = el("div", "actions");
  (dec.actions || []).forEach((a) => {
    const b = el("button", "btn" + (a.primary ? " btn-primary" : ""), fmt(a.label));
    b.type = "button";
    actions.appendChild(b);
  });
  c.appendChild(actions);
  return c;
}

function renderStat(s) {
  const c = el("div", "stat");
  c.appendChild(el("div", "label", fmt(s.label)));
  const isPct = s.suffix === "%";
  const val = el("div", "value" + (s.value === "7" ? " teal" : ""));
  val.innerHTML = fmt(s.value) +
    (isPct ? '<span class="pct">%</span>' : (s.suffix ? ` <span class="suffix">${fmt(s.suffix)}</span>` : ""));
  c.appendChild(val);
  if (s.desc) c.appendChild(el("div", "desc", fmt(s.desc)));
  if (typeof s.bar === "number") {
    const bar = el("div", "bar");
    bar.appendChild(el("span", null)).style.width = Math.round(s.bar * 100) + "%";
    c.appendChild(bar);
  }
  return c;
}

function renderBarChart(ch) {
  const p = el("div", "panel");
  p.appendChild(el("h3", null, fmt(ch.title)));
  if (ch.subtitle) p.appendChild(el("p", "sub", fmt(ch.subtitle)));

  const max = Math.max(...ch.bars.map((b) => b.value), 1);
  // Round the axis top up to a "nice" number.
  const top = Math.ceil(max / 5) * 5 || max;
  const chart = el("div", "chart");
  const yaxis = el("div", "yaxis");
  [top, Math.round(top * 0.66), Math.round(top * 0.33), 0].forEach((v) =>
    yaxis.appendChild(el("div", null, String(v))));
  chart.appendChild(yaxis);

  const plot = el("div", "plot");
  ch.bars.forEach((b, i) => {
    const hot = ch.highlight_last && i === ch.bars.length - 1;
    const col = el("div", "col" + (hot ? " hot" : ""));
    col.appendChild(el("div", "num", String(b.value)));
    const fill = el("div", "fill");
    fill.style.height = Math.max(4, Math.round((b.value / top) * 100)) + "%";
    col.appendChild(fill);
    col.appendChild(el("div", "xl", fmt(b.label)));
    plot.appendChild(col);
  });
  chart.appendChild(plot);
  p.appendChild(chart);
  return p;
}

function renderEvidence(ev) {
  const p = el("div", "panel");
  p.appendChild(el("h3", null, fmt(ev.title)));
  if (ev.subtitle) p.appendChild(el("p", "sub", fmt(ev.subtitle)));

  const total = ev.segments.reduce((a, s) => a + s.count, 0) || 1;
  const bar = el("div", "evbar");
  ev.segments.forEach((s) => {
    const seg = el("div", "seg");
    seg.style.flex = `${s.count} 0 0`;
    bar.appendChild(seg);
  });
  p.appendChild(bar);

  const legend = el("div", "evlegend");
  ev.segments.forEach((s) => {
    const row = el("div", "evrow");
    row.appendChild(el("span", "chip"));
    row.appendChild(el("span", "cnt", String(s.count)));
    row.appendChild(el("span", "txt", fmt(s.label)));
    legend.appendChild(row);
  });
  p.appendChild(legend);
  return p;
}

function renderFinding(f) {
  const c = el("article", "finding");
  const badges = el("div", "finding-badges");
  const confirmed = /confirm/i.test(f.badge);
  badges.appendChild(el("span", "tag " + (confirmed ? "tag-confirmed" : "tag-ruled"),
    `<span class="dot">●</span>${fmt(f.badge)}`));
  if (f.strength) badges.appendChild(el("span", "tag tag-strength", fmt(f.strength)));
  badges.appendChild(el("time", null, fmt(f.time)));
  c.appendChild(badges);
  c.appendChild(el("h4", null, fmt(f.title)));
  if (f.desc) c.appendChild(el("p", null, fmt(f.desc)));
  if (f.caveat) c.appendChild(el("div", "caveat", fmt(f.caveat)));
  return c;
}

function renderPaper(p) {
  const c = el("article", "paper");
  const top = el("div", "paper-top");
  const statusCls = /waiting on you/i.test(p.status) ? "waiting-on-you" : "neutral";
  top.appendChild(el("span", "pill-status " + statusCls, `<span class="dot">●</span>${fmt(p.status)}`));
  if (p.meta) top.appendChild(el("time", null, fmt(p.meta)));
  c.appendChild(top);
  c.appendChild(el("h4", null, fmt(p.title)));

  const stages = el("div", "stages");
  (p.stages || []).forEach((st, i) => {
    if (i > 0) stages.appendChild(el("span", "chev", "›"));
    stages.appendChild(el("span", "stage stage-" + (st.state || "pending"), fmt(st.name)));
  });
  c.appendChild(stages);
  if (p.desc) c.appendChild(el("p", "note", fmt(p.desc)));
  return c;
}

function renderCost(card) {
  const c = el("div", "cost" + (card.accent ? " accent" : ""));
  c.appendChild(el("div", "label", fmt(card.label)));
  const val = el("div", "value");
  val.innerHTML = fmt(card.value) + (card.suffix ? ` <span class="suffix">${fmt(card.suffix)}</span>` : "");
  c.appendChild(val);
  if (card.desc) c.appendChild(el("div", "desc", fmt(card.desc)));
  if (typeof card.bar === "number") {
    const bar = el("div", "bar");
    bar.appendChild(el("span", null)).style.width = Math.round(card.bar * 100) + "%";
    c.appendChild(bar);
  }
  return c;
}

function renderTeam(t) {
  const c = el("div", "team");
  const body = el("div", "body");
  body.appendChild(el("span", "tdot " + (t.dot || "green")));
  const txt = el("div");
  txt.appendChild(el("div", "name", fmt(t.name)));
  txt.appendChild(el("div", "desc", fmt(t.desc)));
  body.appendChild(txt);
  c.appendChild(body);
  c.appendChild(el("span", "status-badge " + slug(t.status), `<span class="dot">●</span>${fmt(t.status)}`));
  return c;
}

function render(d) {
  const app = document.getElementById("app");
  app.innerHTML = "";
  app.appendChild(renderMasthead(d));
  if (d.sample_banner) app.appendChild(el("div", "sample-banner", fmt(d.sample_banner)));

  if (d.director_note) app.appendChild(renderDirector(d.director_note));

  if (d.decisions && d.decisions.length) {
    app.appendChild(sectionHead("What needs you today", d.decisions_meta));
    d.decisions.forEach((dec) => app.appendChild(renderDecision(dec)));
  }

  if (d.numbers) {
    app.appendChild(sectionHead(d.numbers.title, d.numbers.meta));
    const grid = el("div", "stat-grid");
    d.numbers.stats.forEach((s) => grid.appendChild(renderStat(s)));
    app.appendChild(grid);
  }

  if (d.answers_chart || d.evidence) {
    const charts = el("div", "charts");
    charts.style.marginTop = "26px";
    if (d.answers_chart) charts.appendChild(renderBarChart(d.answers_chart));
    if (d.evidence) charts.appendChild(renderEvidence(d.evidence));
    app.appendChild(charts);
  }

  if (d.learned) {
    app.appendChild(sectionHead(d.learned.title, d.learned.meta));
    d.learned.items.forEach((f) => app.appendChild(renderFinding(f)));
  }

  if (d.papers) {
    app.appendChild(sectionHead(d.papers.title, d.papers.meta));
    d.papers.items.forEach((p) => app.appendChild(renderPaper(p)));
  }

  if (d.costs) {
    app.appendChild(sectionHead(d.costs.title, d.costs.meta));
    const grid = el("div", "cost-grid");
    d.costs.cards.forEach((c) => grid.appendChild(renderCost(c)));
    app.appendChild(grid);
  }

  if (d.lab) {
    app.appendChild(sectionHead(d.lab.title, d.lab.meta));
    const grid = el("div", "lab-grid");
    d.lab.teams.forEach((t) => grid.appendChild(renderTeam(t)));
    app.appendChild(grid);
  }

  if (d.footer) app.appendChild(el("footer", "foot", fmt(d.footer)));
}

function fail(msg) {
  document.getElementById("app").innerHTML =
    `<p style="font-family:var(--mono);color:var(--amber-soft)">${msg}</p>`;
}

(function boot() {
  if (window.CONSOLE_DATA) { render(window.CONSOLE_DATA); return; }
  fetch("data/console.json")
    .then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(render)
    .catch(() => fail("Could not load console state (data/console.json). Run the backend to generate it, or serve this directory over http."));
})();
