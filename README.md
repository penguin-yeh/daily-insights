# Penguin 每日洞察

網站：https://penguin-yeh.github.io/daily-insights/
對應新聞統整：https://penguin-yeh.github.io/daily-news/（repo `penguin-yeh/daily-news`）

這裡不重列新聞，而是把每天值得關注的點寫成**洞察**：今日判讀、洞察卡（分析、我的見解、學到什麼）、跨日關聯，以及持續追蹤的主線。

`build.py` 會把 `data/` 裡**所有**日期打包成**一個**自含的 `index.html`（CSS、JS 都寫在檔案裡，不需要任何外部資源）。頁首有「◀ 前一天／日期下拉／後一天 ▶」，預設顯示最新一天，也可以用網址 `#YYYY-MM-DD`（或某張卡 `#YYYY-MM-DD--i3`）和鍵盤 ← → 切換。手機可用，並支援淺色與深色模式。

## 每日更新步驟（例：2026-10-28）
1. 等「每天發生的事」完成 `/workspace/daily-news/data/2026-10-28.json`（每天 9 點多）。
2. 讀當天新聞 JSON，挑 4–7 個**值得關注的點**（不是逐條摘要），寫 `data/2026-10-28.json`（格式見下）。
   - `analysis`：發生什麼、為什麼重要、接下來看什麼。事實與數字**只能**取自新聞 JSON，不可自行補。
   - `view`（我的見解）：第一人稱，說明為什麼值得看；標成分析觀點。
   - `lesson`（學到什麼）：一句可帶走的心得。
   - `sources`：只用新聞 JSON 裡的真實網址（build 會檢查）。
   - `threads`：掛上 `data/threads.json` 的主線 id。**同一公司、同一事件後續、同一趨勢**就掛同一條，系統會自動在卡片顯示「關聯（之前）」與「後續」，並更新「持續追蹤」。新主線就先在 `threads.json` 加一筆。
   - 在 `view` 裡可以直接點名之前哪一天的哪件事（例如「延續 10/26 的降價潮」）。
   - 選填 `related`：連到不是洞察卡的東西，例如 `{"date":"2026-10-25","title":"…","href":"https://penguin-yeh.github.io/daily-news/#2026-10-25"}`。
3. 產生頁面並發佈：
   ```bash
   cd /workspace/daily-insights
   python3 build.py            # 檢查欄位、主線 id、來源網址都在新聞 JSON 裡，寫出 index.html
   git add -A && git commit -m "insights: 2026-10-28" && git push
   ```
   GitHub Pages 約 1 分鐘內更新。確認：`curl -s https://penguin-yeh.github.io/daily-insights/ | grep -c 2026-10-28`
4. （選用）看畫面：`google-chrome --headless=new --no-sandbox --screenshot=/tmp/x.png --window-size=390,1400 "file://$PWD/index.html#2026-10-28"`

`build.py` 選項：`--news DIR`（新聞 JSON 目錄，預設 `/workspace/daily-news/data`；目錄不存在時略過網址檢查）、`-o out.html`。

## JSON 格式
`data/YYYY-MM-DD.json`
```json
{
  "date": "2026-10-28",
  "label": "10/28（三）",
  "news_url": "https://penguin-yeh.github.io/daily-news/#2026-10-28",
  "verdict": "今日判讀：一段話說明今天代表什麼（分析觀點）",
  "learned": "今日學到：一句話",
  "insights": [{
    "id": "i1", "icon": "💸",
    "headline": "尖銳的標題",
    "analysis": "2–4 句：事實＋為什麼重要＋接下來看什麼",
    "view": "我的見解（第一人稱）",
    "lesson": "學到什麼",
    "threads": ["nvidia-financing"],
    "sources": [{"title": "連結文字", "href": "https://新聞 JSON 裡的網址"}],
    "related": [{"date": "2026-10-25", "id": "i1"}]
  }]
}
```
`data/threads.json`：`[{"id": "...", "name": "主線名稱", "desc": "一句說明"}]`

## 連結設計
和 daily-news 一樣：外部連結是純 `<a href rel="noopener noreferrer">`、不加 target，JS 只在允許彈窗時改開新分頁，避免在 sandboxed iframe 預覽裡點了沒反應。
