# 每日洞察網站風格規範：「深夜書房」

> 給負責產生本 repo 頁面的 bot（Grok bot）：**修改 `build.py` 或產生 `index.html` 之前，先完整讀完這份文件並嚴格遵守。**
>
> 與 `daily-news`（晨間電訊、全行內 CSS）不同：這是網站，不是信件，**`build.py` 裡的 `CSS` 常數可以是單一 `<style>`**，因為需要用 CSS 變數與 `prefers-color-scheme` 做深淺色。除此之外維持「自含單檔、不載外部資源」。
>
> `build.py` 目前的 `CSS` 還是舊樣式（淺色優先、漸層 hero、彩色填滿方框）。本文件是新的目標樣式，不一致時**以本文件為準**，並同步修改 `build.py`。資料格式（`data/*.json`、`threads.json`）與 README 的更新流程、連結行為都**不變**。

## 0. 設計方向

這裡不是新聞，是「寫給自己的判斷」。所以版面像深夜書桌上的筆記：**深色優先、襯線標題、琥珀色代表「我的判斷」、青綠色代表「學到的東西」**。少裝飾，靠字體層次與左側色線分層，不靠色塊。

## 1. 硬性規則

1. 單檔自含：CSS、JS 都寫在 `index.html` 裡，不載外部字型、圖片、CDN。
2. **深色優先**：`:root` 定義深色，`@media (prefers-color-scheme: light)` 覆蓋成淺色。
3. 不准：漸層、陰影（含 `box-shadow`）、`backdrop-filter`、大於 8px 的圓角（頭像或圓點用 `50%` 除外）、hover 位移動畫。
4. 色彩只能用第 2 節的變數；元件裡不要直接寫色碼。
5. 手機優先，無橫向捲軸；內容欄寬上限 **760px**（舊版 920px 太寬，行長過長）。
6. 外部連結維持 README 的規定：純 `<a href rel="noopener noreferrer">`，不加 `target`；JS 只在允許彈窗時改開新分頁。
7. 保留既有功能：日期下拉、前後一天、鍵盤 ← →、`#YYYY-MM-DD` 與 `#YYYY-MM-DD--i3` 錨點、「持續追蹤」主線。

## 2. 設計 token（寫進 `CSS` 常數）

```css
:root{
  --bg:#0f1218; --card:#171b23; --ink:#e8e6e1; --mute:#9a9ba3; --line:#2a2f3a;
  --amber:#e0a458;   /* 我的見解、重點 */
  --teal:#5fb3a1;    /* 學到什麼 */
  --violet:#9b8cd6;  /* 主線、關聯 */
  --link:#e0a458;
  --serif:Georgia,"Noto Serif TC","PingFang TC",serif;
  --sans:-apple-system,BlinkMacSystemFont,"PingFang TC","Noto Sans TC","Microsoft JhengHei",sans-serif;
  --mono:ui-monospace,SFMono-Regular,Consolas,monospace;
}
@media (prefers-color-scheme:light){:root{
  --bg:#f5f1e8; --card:#fffdf8; --ink:#23221f; --mute:#6f6a5f; --line:#e0d9c8;
  --amber:#a8651a; --teal:#2f7d6d; --violet:#6a58b0; --link:#a8651a;
}}
```

字型分工：標題、判讀、「我的見解」用 `--serif`；內文、分析用 `--sans`；日期、編號、標籤用 `--mono`。

## 3. 元件寫法

下面保留舊的 class 名稱，改的是樣式，這樣 `build.py` 的 HTML 結構幾乎不用動。

### 3.1 頁首與導覽

```css
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.8 var(--sans);-webkit-text-size-adjust:100%}
a{color:var(--link)}
.wrap{max-width:760px;margin:0 auto;padding:20px 16px 64px}
.nav{position:sticky;top:0;z-index:10;display:flex;gap:8px;justify-content:center;align-items:center;flex-wrap:wrap;padding:10px;background:var(--bg);border-bottom:1px solid var(--line)}
.nav button,.nav select{font:inherit;font-size:.88rem;font-family:var(--mono);color:var(--ink);background:var(--card);border:1px solid var(--line);border-radius:6px;padding:6px 12px;cursor:pointer}
.nav button:disabled{opacity:.4;cursor:default}
header{padding:36px 0 8px}
header .date{font:600 .8rem var(--mono);letter-spacing:.14em;color:var(--amber);text-transform:uppercase}
header h1{margin:.25em 0 .15em;font:700 2rem/1.25 var(--serif)}
header p{margin:0;color:var(--mute);font-size:.9rem}
```

頁首標題固定為「Penguin 每日洞察」，不加企鵝 emoji。

### 3.2 今日判讀（hero）

不要漸層與外框，改成「引言」：

```css
.hero{margin:20px 0 34px;padding:2px 0 2px 18px;border-left:4px solid var(--amber)}
.hero h2{margin:0 0 6px;font:600 .75rem var(--mono);letter-spacing:.14em;color:var(--amber);text-transform:uppercase}
.hero p{margin:0 0 10px;font:500 1.2rem/1.75 var(--serif)}
.today{margin:0;padding:0;border:0;background:none;font-size:.95rem;color:var(--mute)}
.today::before{content:"今日學到　";font:600 .75rem var(--mono);letter-spacing:.1em;color:var(--teal)}
.newslink{display:inline-block;margin-top:10px;font:.82rem var(--mono)}
```

### 3.3 洞察卡

卡片是一張安靜的紙，分三層（分析／我的見解／學到什麼），**用左側色線分層，不用填滿色塊**：

```css
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
```

標籤字樣：分析 → `ANALYSIS · 分析`，見解 → `MY VIEW · 我的見解`，學到 → `LEARNED · 學到什麼`。卡片標題前保留 `icon` emoji（資料欄位），其他位置不加 emoji。

### 3.4 標籤、連結、關聯

```css
.tags{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px}
.tag{font:600 .7rem var(--mono);color:var(--violet);border:1px solid var(--violet);border-radius:4px;padding:1px 8px;text-decoration:none}
.links{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0 12px}
.lnk{font:.8rem var(--mono);color:var(--ink);text-decoration:none;border:1px solid var(--line);border-radius:4px;padding:3px 10px}
.rel{margin:0;padding-left:1.2em;font-size:.88rem}
.rel .d{font-family:var(--mono);color:var(--mute);font-variant-numeric:tabular-nums}
```

### 3.5 持續追蹤（主線）：時間軸

主線改成垂直時間軸，點代表某一天出現過：

```css
.thread{position:relative;background:none;border:0;border-radius:0;padding:0 0 0 22px;margin:0 0 26px;border-left:2px solid var(--line)}
.thread h3{margin:0 0 4px;font:700 1.02rem var(--serif);color:var(--violet)}
.thread .desc{margin:0 0 8px;color:var(--mute);font-size:.86rem}
.thread ol{list-style:none;margin:0;padding:0;font-size:.9rem}
.thread li{position:relative;margin:.35em 0}
.thread li::before{content:"";position:absolute;left:-28px;top:.62em;width:9px;height:9px;border-radius:50%;background:var(--violet)}
```

### 3.6 其他

```css
*{box-sizing:border-box}
.day[hidden]{display:none}
footer{margin-top:36px;padding-top:14px;border-top:1px solid var(--line);color:var(--mute);font:.78rem var(--mono)}
:focus-visible{outline:2px solid var(--amber);outline-offset:2px}
@media (max-width:600px){header h1{font-size:1.6rem}.hero p{font-size:1.08rem}.card{padding:16px 14px 10px}}
```

## 4. 內容撰寫與版面的配合

- `analysis`：2–4 句，事實與數字只取自新聞 JSON。
- `view`：第一人稱、有立場，是整頁最有個性的部分，用襯線字。
- `lesson`：一句話，不要寫成摘要。
- 每天 4–7 張卡；卡片標題要是「判斷」而不是新聞標題。

## 5. 檢查清單

- [ ] `CSS` 常數裡沒有 `linear-gradient`、`box-shadow`、`backdrop-filter`；沒有寫死的色碼（`:root` 的 token 定義除外）。
- [ ] 深色與淺色都檢查過（`prefers-color-scheme` 兩種都開一次截圖）。
- [ ] 390px 寬度下無橫向捲軸，內文行長不超過約 40 個中文字。
- [ ] 日期切換、鍵盤 ← →、卡片錨點仍可用。
- [ ] `python3 build.py` 通過（欄位、主線 id、來源網址檢查）。
- [ ] 頁面沒有載入任何外部資源。
