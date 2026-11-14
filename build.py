#!/usr/bin/env python3
"""Build one self-contained index.html from data/YYYY-MM-DD.json + data/threads.json.

Usage:  python3 build.py                 -> writes index.html
        python3 build.py -o out.html
        python3 build.py --news ../daily-news/data   (default: /workspace/daily-news/data if it exists)
The --news check makes sure every source link exists in that day's (or an earlier day's) news JSON.
"""
import argparse, glob, html, json, os, re, sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
WEEK = "一二三四五六日"
e = lambda s: html.escape(str(s), quote=True)

CSS = r""":root{--bg:#0f1218;--card:#171b23;--ink:#e8e6e1;--mute:#9a9ba3;--line:#2a2f3a;--amber:#e0a458;--teal:#5fb3a1;--violet:#9b8cd6;--link:#e0a458;--serif:Georgia,"Noto Serif TC","PingFang TC",serif;--sans:-apple-system,BlinkMacSystemFont,"PingFang TC","Noto Sans TC","Microsoft JhengHei",sans-serif;--mono:ui-monospace,SFMono-Regular,Consolas,monospace}
@media (prefers-color-scheme:light){:root{--bg:#f5f1e8;--card:#fffdf8;--ink:#23221f;--mute:#6f6a5f;--line:#e0d9c8;--amber:#a8651a;--teal:#2f7d6d;--violet:#6a58b0;--link:#a8651a}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.8 var(--sans);-webkit-text-size-adjust:100%}
a{color:var(--link)}
.wrap{max-width:760px;margin:0 auto;padding:20px 16px 64px}
.nav{position:sticky;top:0;z-index:10;display:flex;gap:8px;justify-content:center;align-items:center;flex-wrap:wrap;padding:10px;background:var(--bg);border-bottom:1px solid var(--line)}
.nav button,.nav select{font:inherit;font-size:.88rem;font-family:var(--mono);color:var(--ink);background:var(--card);border:1px solid var(--line);border-radius:6px;padding:6px 12px;cursor:pointer}
.nav button:disabled{opacity:.4;cursor:default}
.day[hidden]{display:none}
header{padding:36px 0 8px}
header .date{font:600 .8rem var(--mono);letter-spacing:.14em;color:var(--amber);text-transform:uppercase}
header h1{margin:.25em 0 .15em;font:700 2rem/1.25 var(--serif)}
header p{margin:0;color:var(--mute);font-size:.9rem}
.hero{margin:20px 0 34px;padding:2px 0 2px 18px;border-left:4px solid var(--amber)}
.hero h2{margin:0 0 6px;font:600 .75rem var(--mono);letter-spacing:.14em;color:var(--amber);text-transform:uppercase}
.hero p{margin:0 0 10px;font:500 1.2rem/1.75 var(--serif)}
.today{margin:0;padding:0;border:0;background:none;font-size:.95rem;color:var(--mute)}
.today::before{content:"今日學到　";font:600 .75rem var(--mono);letter-spacing:.1em;color:var(--teal)}
.newslink{display:inline-block;margin-top:10px;font:.82rem var(--mono)}
h2.sh{margin:34px 0 14px;font:600 .75rem var(--mono);letter-spacing:.14em;color:var(--mute);text-transform:uppercase;padding-bottom:8px;border-bottom:1px solid var(--line)}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:20px 20px 14px;margin:0 0 18px;scroll-margin-top:70px}
.card:target,.card.flash{border-color:var(--amber)}
.card h3{margin:0 0 10px;font:700 1.18rem/1.5 var(--serif)}
.lbl{display:block;margin:0 0 2px;font:600 .68rem var(--mono);letter-spacing:.14em;color:var(--mute);text-transform:uppercase}
.ana{margin:0 0 16px;font-size:.96rem}
.view,.learn{margin:0 0 14px;padding:2px 0 2px 14px;border:0;border-radius:0;background:none;font-size:.96rem}
.view{border-left:3px solid var(--amber)}
.view .lbl{color:var(--amber)}
.view p{font-family:var(--serif);font-size:1rem}
.learn{border-left:3px solid var(--teal)}
.learn .lbl{color:var(--teal)}
.view p,.learn p{margin:2px 0 0}
.tags{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px}
.tag{font:600 .7rem var(--mono);color:var(--violet);border:1px solid var(--violet);border-radius:4px;padding:1px 8px;text-decoration:none}
.links{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0 12px}
.lnk{font:.8rem var(--mono);color:var(--ink);text-decoration:none;border:1px solid var(--line);border-radius:4px;padding:3px 10px}
.rel{margin:0;padding-left:1.2em;font-size:.88rem}
.rel li{margin:.2em 0}
.rel .d{font-family:var(--mono);color:var(--mute);font-variant-numeric:tabular-nums}
.thread{position:relative;background:none;border:0;border-radius:0;padding:0 0 0 22px;margin:0 0 26px;border-left:2px solid var(--line)}
.thread h3{margin:0 0 4px;font:700 1.02rem var(--serif);color:var(--violet)}
.thread .desc{margin:0 0 8px;color:var(--mute);font-size:.86rem}
.thread ol{list-style:none;margin:0;padding:0;font-size:.9rem}
.thread li{position:relative;margin:.35em 0}
.thread li::before{content:"";position:absolute;left:-28px;top:.62em;width:9px;height:9px;border-radius:50%;background:var(--violet)}
footer{margin-top:36px;padding-top:14px;border-top:1px solid var(--line);color:var(--mute);font:.78rem var(--mono)}
:focus-visible{outline:2px solid var(--amber);outline-offset:2px}
@media (max-width:600px){header h1{font-size:1.6rem}.hero p{font-size:1.08rem}.card{padding:16px 14px 10px}}
"""

JS = r"""
(function(){
  var days=[].slice.call(document.querySelectorAll('.day'));
  var dates=days.map(function(d){return d.dataset.date;});   // newest first
  var sel=document.getElementById('sel'),prev=document.getElementById('prev'),next=document.getElementById('next');
  function parse(h){h=decodeURIComponent(h||'');var p=h.split('--');return {d:p[0],a:p[1]?h:null};}
  function show(dt,anchor,push){
    var i=dates.indexOf(dt); if(i<0){i=0;dt=dates[0];anchor=null;}
    days.forEach(function(d,k){d.hidden=(k!==i);});
    sel.value=dt; prev.disabled=(i>=dates.length-1); next.disabled=(i<=0);
    document.title=days[i].dataset.title;
    var want=anchor||dt;
    if(push!==false && location.hash.slice(1)!==want){history.replaceState(null,'','#'+want);}
    var el=anchor&&document.getElementById(anchor);
    if(el){el.scrollIntoView();el.classList.add('flash');setTimeout(function(){el.classList.remove('flash');},1600);}
    else window.scrollTo(0,0);
  }
  sel.addEventListener('change',function(){show(sel.value);});
  prev.addEventListener('click',function(){var i=dates.indexOf(sel.value);if(i<dates.length-1)show(dates[i+1]);});
  next.addEventListener('click',function(){var i=dates.indexOf(sel.value);if(i>0)show(dates[i-1]);});
  window.addEventListener('hashchange',function(){var p=parse(location.hash.slice(1));show(p.d,p.a,false);});
  document.addEventListener('keydown',function(e){if(/SELECT|INPUT|TEXTAREA/.test(e.target.tagName))return;if(e.key==='ArrowLeft')prev.click();if(e.key==='ArrowRight')next.click();});
  var p0=parse(location.hash.slice(1)); show(p0.d||dates[0],p0.a,false);
  document.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('a.lnk'); if(!a||e.defaultPrevented||e.button!==0||e.ctrlKey||e.metaKey||e.shiftKey)return;
    var w=null; try{w=window.open(a.href,'_blank');}catch(_){w=null;}
    if(w){try{w.opener=null;}catch(_){} e.preventDefault();}
  });
})();
"""

def long_date(d):
    y, m, dd = map(int, d.split("-"))
    return f"{y} 年 {m} 月 {dd} 日 · 週{WEEK[date(y, m, dd).weekday()]}"

def md(d):  # 2026-10-25 -> 10/25
    return f"{int(d[5:7])}/{int(d[8:10])}"

def aid(d, i):
    return f"{d}--{i}"

def load(data_dir):
    with open(os.path.join(data_dir, "threads.json"), encoding="utf-8") as f:
        threads = json.load(f)
    days = []
    for p in sorted(glob.glob(os.path.join(data_dir, "*.json"))):
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.json", os.path.basename(p)):
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
            d.setdefault("date", os.path.basename(p)[:-5])
            days.append(d)
    days.sort(key=lambda d: d["date"])  # oldest first for linking
    return threads, days

def check(threads, days, news_dir):
    errs = []
    tids = {t["id"] for t in threads}
    seen = set()
    for d in days:
        for k in ("verdict", "learned", "insights"):
            if not d.get(k):
                errs.append(f'{d["date"]}: missing "{k}"')
        for it in d.get("insights", []):
            where = f'{d["date"]} {it.get("id")}'
            for k in ("id", "headline", "analysis", "view", "lesson", "sources"):
                if not it.get(k):
                    errs.append(f"{where}: missing {k}")
            if (d["date"], it.get("id")) in seen:
                errs.append(f"{where}: duplicate id")
            seen.add((d["date"], it.get("id")))
            for t in it.get("threads", []):
                if t not in tids:
                    errs.append(f"{where}: unknown thread {t} (add it to threads.json)")
    if news_dir and os.path.isdir(news_dir):
        known = {}
        for p in glob.glob(os.path.join(news_dir, "*.json")):
            dt = os.path.basename(p)[:-5]
            with open(p, encoding="utf-8") as f:
                n = json.load(f)
            known[dt] = {l["href"] for t in n.get("topics", []) for i in t.get("items", []) for l in i.get("links", [])}
        for d in days:
            ok = set().union(*[v for k, v in known.items() if k <= d["date"]] or [set()])
            if d["date"] not in known:
                errs.append(f'{d["date"]}: no news JSON in {news_dir}')
            for it in d.get("insights", []):
                for s in it.get("sources", []):
                    if s["href"] not in ok:
                        errs.append(f'{d["date"]} {it["id"]}: source not in news JSON: {s["href"]}')
    return errs

def build(threads, days):
    tname = {t["id"]: t["name"] for t in threads}
    flat = [(d["date"], it) for d in days for it in d["insights"]]  # chronological
    def linked(dt, it, earlier=True):
        out = []
        for d2, it2 in flat:
            if (d2 < dt) if earlier else (d2 > dt):
                common = [t for t in it.get("threads", []) if t in it2.get("threads", [])]
                if common:
                    out.append((d2, it2, common))
        return out[-4:][::-1] if earlier else out[:4]

    def rel_li(d2, it2, common):
        return (f'<li><span class="d">{md(d2)}</span> <a href="#{aid(d2, it2["id"])}">{e(it2["headline"])}</a>'
                f'（{e("、".join(tname[c] for c in common))}）</li>')

    def card(d, it):
        dt = d["date"]
        tags = "".join(f'<a class="tag" href="#{aid(dt, "threads")}">{e(tname[t])}</a>' for t in it.get("threads", []))
        links = "".join(f'<a class="lnk" href="{e(s["href"])}" rel="noopener noreferrer">{e(s["title"])} ↗</a>' for s in it["sources"])
        prev = [rel_li(*x) for x in linked(dt, it)]
        prev += [f'<li><span class="d">{md(r["date"])}</span> <a href="{e(r["href"]) if r.get("href") else "#" + aid(r["date"], r["id"])}">{e(r.get("title") or r["id"])}</a></li>'
                 for r in it.get("related", [])]
        later = [rel_li(*x) for x in linked(dt, it, earlier=False)]
        rel = ""
        if prev:
            rel += f'<span class="lbl">RELATED · 關聯（之前）</span><ul class="rel">{"".join(prev)}</ul>'
        if later:
            rel += f'<span class="lbl">NEXT · 後續</span><ul class="rel">{"".join(later)}</ul>'
        return (f'<article class="card" id="{aid(dt, it["id"])}"><div class="tags">{tags}</div>'
                f'<h3>{e(it.get("icon", ""))} {e(it["headline"])}</h3>'
                f'<span class="lbl">ANALYSIS · 分析</span><p class="ana">{e(it["analysis"])}</p>'
                f'<div class="view"><span class="lbl">MY VIEW · 我的見解</span><p>{e(it["view"])}</p></div>'
                f'<div class="learn"><span class="lbl">LEARNED · 學到什麼</span><p>{e(it["lesson"])}</p></div>'
                f'<span class="lbl">SOURCES · 依據新聞</span><div class="links">{links}</div>{rel}</article>')

    def thread_block(dt):
        out = []
        for t in threads:
            steps = [(d2, it) for d2, it in flat if d2 <= dt and t["id"] in it.get("threads", [])]
            if not steps:
                continue
            lis = "".join(f'<li><span class="d">{md(d2)}</span> <a href="#{aid(d2, it["id"])}">{e(it["headline"])}</a></li>' for d2, it in steps)
            out.append(f'<div class="thread"><h3>{e(t["name"])}（{len(steps)}）</h3><p class="desc">{e(t["desc"])}</p><ol>{lis}</ol></div>')
        return "".join(out)

    newest = sorted(days, key=lambda d: d["date"], reverse=True)
    body = []
    for d in newest:
        dt = d["date"]
        title = f"Penguin 每日洞察 · {dt}"
        news = d.get("news_url") or f"https://penguin-yeh.github.io/daily-news/#{dt}"
        body.append(
            f'<div class="day" data-date="{e(dt)}" data-title="{e(title)}" hidden>'
            f'<header><div class="date">{e(long_date(dt))}</div><h1>Penguin 每日洞察</h1>'
            f'<p>從每日新聞統整挑出值得關注的點，寫成判讀、見解與學習</p></header>'
            f'<section class="hero"><h2>今日判讀 · 分析觀點</h2><p>{e(d["verdict"])}</p>'
            f'<div class="today">{e(d["learned"])}</div>'
            f'<a class="newslink lnk" href="{e(news)}" rel="noopener noreferrer">看當天完整新聞統整 ↗</a></section>'
            f'<h2 class="sh">今日洞察（{len(d["insights"])}）</h2>'
            + "".join(card(d, it) for it in d["insights"])
            + f'<h2 class="sh" id="{aid(dt, "threads")}">持續追蹤（截至 {md(dt)}）</h2>{thread_block(dt)}'
            + '<footer>「我的見解」「學到什麼」「今日判讀」為分析觀點；事實與數字皆取自當天新聞統整，原始出處見各卡片連結。</footer></div>')
    html_body = "".join(body).replace(" hidden>", ">", 1)
    opts = "".join(f'<option value="{e(d["date"])}">{e(d.get("label") or d["date"])}</option>' for d in newest)
    nav = (f'<nav class="nav"><button id="prev" type="button">◀ 前一天</button>'
           f'<select id="sel" aria-label="選擇日期">{opts}</select>'
           f'<button id="next" type="button">後一天 ▶</button></nav>')
    return ('<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="color-scheme" content="light dark">'
            f'<title>Penguin 每日洞察 · {e(newest[0]["date"])}</title><style>{CSS}</style></head>'
            f'<body>{nav}<div class="wrap">{html_body}</div><script>{JS}</script></body></html>')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(HERE, "data"))
    ap.add_argument("--news", default="/workspace/daily-news/data")
    ap.add_argument("-o", "--out", default=os.path.join(HERE, "index.html"))
    a = ap.parse_args()
    threads, days = load(a.data)
    if not days:
        sys.exit("no data/YYYY-MM-DD.json found")
    errs = check(threads, days, a.news)
    if errs:
        print("\n".join("ERROR " + x for x in errs)); sys.exit(1)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(build(threads, days))
    print(f"wrote {a.out}  ({len(days)} days: {', '.join(d['date'] for d in days)})")

if __name__ == "__main__":
    main()
