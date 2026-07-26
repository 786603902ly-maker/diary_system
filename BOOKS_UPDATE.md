# 读书宇宙（Book OS）—— 操作手册

这是 `UPDATE.md`（日记 Mind OS 的操作手册）的读书笔记版。两套内容结构一致、真源都是仓库里
的 JSON 文件，只是来源不同：日记来自十年日记 PDF，读书宇宙来自 5 个读书笔记 Google Doc +
每天的 Mind Card 学习对话（见 `BOOK_LEARNING_SYSTEM.md`）。**两套数据渲染在同一个页面/
同一个 Artifact 里**（2026-07-25 从"两个独立 Artifact"合并过来，原因和取舍见 `CLAUDE.md`），
所以下面提到的"构建"、"发布"都只有一次，不是两次。

## 日常使用（你只需要做这一步）

跟日记系统完全一样的手动触发流程，不需要记细节：

- **一天的 Mind Card 学习聊完了** → 说一句"今天聊完了，帮我归档"。Claude 会把这次对话
  蒸馏成一条 `universalTruths[]` 条目（或强化已有条目），同时把"🔄 归还日记库"那部分
  直接写回 `data/mind-os.json` 对应 principle 的 `cases[]`（不再需要你手动复制粘贴到
  Google Doc），跑一次 `python3 src/build.py`、发布一次、提交一次。
- **某本书的笔记文档更新了 / 读完一本新书想补充笔记** → 把内容发给 Claude，说"这是新
  笔记，帮我融进读书思维库"。Claude 会：①在 `library[]` 里给这本书新增条目（新书就是新
  `book` 记录 + `status: "distilled"`，老书更新就在已有条目基础上增补/修订），②扫一遍
  已有 262+ 条条目找有没有真正的跨书连接，有就加 `relatedIds`，③如果这次内容本身分量够
  重、适合走一次 Mind Card 深度对话，还可以顺手问你要不要也走一遍 42 天流程产出一条
  `universalTruths`（但这不是必须的，读书思维库不依赖金字塔）。
- **两边内容都要更新**（比如某天聊的东西同时涉及新日记和新书感悟）→ 直接说清楚就行，
  Claude 会分别写回两个 JSON，仍然只需要构建发布一次。如果内容本身就写得含糊，Claude
  会先确认再动手，不会瞎猜。

## 文件结构

```
data/book-os.json          ← 读书宇宙真源：四象限骨架（与日记共用同一套taxonomy）+ threads[]
                              （跨学科主线注册表）+ books[]（书目roster）+ library[]（读书思维
                              库——40本书的全量索引）+ universalTruths[]（普世智金字塔）
src/template.html          ← 页面模板（与日记共用同一份），"普世智金字塔/读书思维库/关联图谱/
                              书籍索引"四个 Tab 渲染这份数据；关联图谱是纯 SVG + 原生 JS 手写
                              的可视化，内部有模式切换（思维库全景 / 金字塔主线两套图）
src/build.py                ← 构建脚本：把 mind-os.json 和 book-os.json 都内联进模板 → 生成
                              index.html（同一个脚本，两套数据一起构建）
BOOK_LEARNING_SYSTEM.md    ← 每日 Mind Card 学习法的完整规则（改造自 v4.3 Project Instruction）
```

**改内容永远改 `data/book-os.json`，改样式/交互永远改 `src/template.html`（日记那边也在用
同一份），然后跑 `python3 src/build.py` 重新生成 `index.html`，绝不直接手改 `index.html`。**

## universalTruths 的字段怎么填

每条对应一天的 Mind Card（或一次批量迁移得到的书本核心论点），字段直接对应 Mind Card
的模块，不用重新设计：

| Mind Card 模块 | JSON 字段 |
|---|---|
| Mind OS 定位（层级/子类） | `quadrant` / `subcat` / `cluster`（复用日记同一套四象限十二子类） |
| 核心论点（普世真理） | `core` |
| Day 递进 | `dayProgression`（不是每条都需要，纯粹迁移旧书笔记时可留空） |
| 核心洞察（通常 3 条，各标来源） | `insights[]`：`{title, source, mechanism, example, takeaway}` |
| 突触连接（跨学科跳跃） | `crossDomainAnalogy: {domain, text}` |
| 场景模拟（日记真实案例） | `scenario: {caseRef, caseText, question, hanging, answer}` |
| 我的内化 | `internalization: {identity, mantra, futureApplication}` |
| 关联书目 | `books: [bookId,...]` |
| 日记库锚点 | `mindOsRefs: [principleId,...]`（同时要去 `data/mind-os.json` 给对应
  principle 补一个反向的 `bookRefs: [truthId,...]`，两边互链才算完整） |
| 跨学科主线标签 | `threads: [threadId,...]`（可以为空——**不要为了填而硬凑**，说不清
  逻辑连接的主线就不标，这是 v4.3 准则一"逻辑连接自查"的延伸） |

编号规则和日记一致：`UT-象限-子类-数字`（如 `UT-MAS-A-10`），同一子类内新增在最大编号基础
上 +10。`threads[]` 是一个开放注册表（`data/book-os.json` 顶层 `threads` 数组），发现新的
跨学科主线可以随时注册一个新 thread，不必局限于最初的 5 条。

## library（读书思维库）的字段怎么填

这是 2026-07-25 新增的"百科全书"层，跟"每日强化考试"的普世智金字塔是两回事——不需要 Day
递进、场景审讯这些对话产物字段，只需要客观、完整地把一本书的论点 + 你当年的批注记下来：

| 字段 | 说明 |
|---|---|
| `id` | `LIB-象限-子类-数字`（如 `LIB-MAS-A-10`），同一子类内新增在最大编号基础上 +10 |
| `quadrant`/`subcat`/`cluster` | 同一套四象限十二子类taxonomy；`cluster` 可选，不确定就不填 |
| `book` | 对应 `books[]` 里的 bookId（**每条 library 条目只挂一本书**，不像 universalTruths
  可以挂多本——如果同一个论点在多本书里都出现，就分别建条目，再用 `relatedIds` 互相链接，
  不要合并成一条，这样能看清"这个道理是哪本书教我的"） |
| `keyword`/`title` | 短标签 + 一句话标题，跟思维库 principle 卡片一样 |
| `core` | 对书中论点的客观提炼（1-3句），这是"书说了什么" |
| `annotation` | 你自己的批注/反应（原文里的【特有感】标记、或你自己写的感想），这是"我怎么想
  的"——跟 `core` 分开放，是为了不把书的观点和你的反应混在一起，可以为空字符串 |
| `quote` | 原文里特别精炼值得保留的一句话，可以为空字符串 |
| `relatedIds` | 其它 library 条目的 id 数组，代表"这是同一个底层概念在不同书/不同领域的
  体现"——**这是跨学科连接的核心机制**，新增条目时要扫一遍已有条目找有没有真正说得清"为什么
  相关"的连接（参照 v4.3 准则一"逻辑连接自查"，说不清就不连），不要为了看起来热闹而乱连 |

跟 universalTruths 不同，library 条目**不需要** `mindOsRefs`（暂不做读书思维库↔日记的
双向链接，避免和金字塔的日记锚点混淆；如果确实发现某条 library 论点该链回某条日记
principle，可以照 universalTruths 的模式加，但不是默认要求）。

## 双向链接是怎么实现的

因为现在是同一个页面，跳转不是外链，是原地切 Tab + 展开卡片（点击瞬间完成，没有"确认跳转"
弹窗）：

- 读书宇宙里的 `universalTruth.mindOsRefs` → 渲染成 `🔗 日记 MAS-C-50 →` 这个 chip，点击后
  切到"思维库" Tab、展开 MAS-C-50。
- 日记里的 `principle.bookRefs` → 渲染成 `📚 读书宇宙 UT-MAS-C-10 →` 这个 chip，点击后切到
  "普世智金字塔" Tab、展开 UT-MAS-C-10。

这靠两边共用的 `data-jump-kb`/`data-jump-pyramid` data 属性和一套委托点击处理实现（`main`
上只挂一个 click listener，两套卡片共用同一批 class 名如 `.pcard-head`/`.chip-jump`，不用
分别写跳转函数）。页面加载时读 `location.hash` 也会自动判断该 ID 属于哪一边（`principleById`
还是 `truthById`）并展开对应 Tab。新增双向链接时，**两边的 JSON 都要改**，只改一边等于
链接单向。

## 「关联图谱」怎么工作

`src/template.html` 里"关联图谱" tab 内部有模式切换（顶部两个小按钮），两套图独立：

- **金字塔主线**：以 `threads[]` 里每条主线为一个枢纽节点，所有标了该 thread 的
  `universalTruths` 作为卫星节点画线连过去，节点按四象限配色、点击跳转回金字塔里对应的
  完整卡片。没有标 thread 的条目会归到"待归类"分组，不会丢失，只是暂时没连线。
- **思维库全景**（默认模式）：全部 `library[]` 条目按四象限分布的 SVG 全景图，**但 SVG
  本身只是索引/概览**——节点太多、太小，光看图点不出内容。真正能读的内容在图下方的
  "🔗 跨学科连接组"：把 `relatedIds` 构成的图做连通分量分解（同一组里的条目互相之间有
  路径可达，哪怕不是每一对都直接相连），每一组渲染成一张卡片，把组内所有条目的
  `keyword`/`book`/`title`/`core`/`annotation` 全部平铺展开——**不用点、不用悬停，直接
  往下滑就能看到"这几本书在讲同一件事"的具体内容**，卡片顶部还会把涉及到的书名全部列出来
  （`📚 书名A × 书名B × 书名C`），这就是"一个概念被好几本书印证"在页面上的直接体现。
  `libraryComponents()`（`src/template.html`）做连通分量分解，跟 `relatedIds` 数据结构强
  绑定，新增连接后这个列表会自动更新，不需要手动维护。

## 性能：为什么改成"局部更新"而不是每次点击都整页重渲染

`读书思维库` 一次性铺开 262 张卡片后，原来的实现是"任何一次点击（展开/标星）都调用
`render()`，把整个当前 Tab 的 HTML 全部重新拼一遍再整体替换进 DOM"——对 3 条金字塔卡片
无所谓，对 262 条读书思维库卡片就是浪费。现改成 `toggleCardExpand()`/`toggleStar()`
两个函数，只修改被点击的那一张卡片的 DOM（加/删 `.pcard-body`，切 class，改文字），
不碰其它 261 张。唯一的例外是"只看重点"筛选开着时点标星——因为这时候取消标星会让卡片从
列表里消失，必须触发一次完整的 `render()` 重新过滤。日记侧的思维库/原话集也共用这两个
函数，同样受益。

## 书籍索引 tab 与 `books[]` 的 `status`

`status` 有三档：`queued`（读书思维库还没收录）、`in-progress`（收录了但覆盖不全）、
`distilled`（核心论点已完整提炼）。这个字段现在代表的是"读书思维库覆盖到位了没有"，不是
金字塔进度（金字塔的进度看 `universalTruths.length` 和 `data/book-os-progress.json` 的
`lastCompletedDay`，两者是独立的两条进度线）。「书籍索引」tab 顶部的覆盖率统计直接读这个
字段，新书收录完记得更新到位，不要让它长期停留在过时状态。

## 40 本书全量迁移记录（2026-07-25 已完成）

`library[]` 目前有 262 条条目，40 本书全部覆盖（每本至少 3 条，多的到 8 条），带 40 条
精选的跨书/跨领域 `relatedIds` 连接。做法记录在此，方便理解现有数据是怎么来的，也是以后
"批量补更多书"时的可复用流程：

1. 5 个源文档（每个约 60-130KB 原文）**并行分给 5 个 subagent**分别用
   `mcp__Google_Drive__read_file_content` 拉全文、按 `##书名：《XX》` 分节提炼，每个
   agent 只处理自己那一份文档、互不干扰，把结果写成中间 JSON 存到 scratchpad——这样每个
   agent 自己的大量原文阅读不会占用主对话的上下文，5 份并行也比串行处理省时间。
2. 每个 agent 按 `mind-os-classifier` 的 `TAXONOMY.md` 判定规则分类，优先吃标了
   【特有感】（或用户自己写的第一人称感想句）的段落，塞进 `annotation` 字段；书的客观论点
   塞 `core`；原文精炼的句子留在 `quote`。
3. 5 份结果在主对话里合并、去重规则统一分配最终 `id`（`LIB-象限-子类-数字`），然后**手动
   扫一遍全部条目**，找真正说得清逻辑的跨书连接写成 `relatedIds`（这一步是判断力活，没有
   走自动化匹配，因为"两本书讲的是不是同一件事"需要读懂内容才能判断，机械关键词匹配容易
   乱连）。
4. 全部 40 本书的 `status` 更新为 `distilled`。

以后如果要一次性再补一批新书（比如你又存了新的读书笔记文档），同样的"多 agent 并行提炼→
主对话合并+连线"流程可以复用；如果只是零散加一两本书，走本文档最上面"日常使用"里的简单
流程就够，不需要再搞并行 agent。
