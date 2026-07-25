# 项目背景（每次新会话都先读这个）

这个 repo 把用户的两块长期积累蒸馏成一个私人知识网页：2016–2026 的日记「个人思维操作系统 ·
Mind OS」，和 40 本书读书笔记「读书宇宙 · Book OS」。**两者渲染在同一个页面、发布为同一个
私密 Artifact**（顶部标题栏"🧠 个人思维操作系统 · 📚 读书宇宙"并排，下面是两组 Tab：
思维库/原话集/生活记录 属于日记，普世智金字塔/关联图谱/书籍索引 属于读书）。

**当前线上链接（固定，不要发布成新链接）**：
https://claude.ai/code/artifact/354d6b9a-e846-4293-a021-7a01cc768be0

每次改完都用 `Artifact` 工具把 `index.html` 重新发布到**这同一个 url**（传 `url` 参数），
这样用户不需要换书签。

**2026-07-25 曾经短暂发布过一个独立的 Book OS Artifact**
（`https://claude.ai/code/artifact/2614e44c-ee3d-4f86-add4-668ff07b7f23`），当天晚些时候
用户体验后发现"点跨系统链接要弹窗确认跳转"太打断心流，要求合并成一个页面——**这个独立
链接已经不再维护，是历史遗留的旧快照，不要再往那个 url 发布，也不要参考它的代码**（对应的
`src/book_template.html` / `src/build_books.py` / `book-os.html` 已从仓库删除）。

## 数据仍然是两套独立源文件，只是渲染合一（2026-07-25）

`data/mind-os.json`（日记）和 `data/book-os.json`（读书）是两个独立维护的真源，**不要合并
成一个 JSON 文件**——分开维护更清楚哪块内容属于哪边，PR/diff 也更干净。真正合一的只是
`src/template.html`（一份模板同时渲染两套数据，两个 `<script type="application/json">`
标签分别嵌 `__MIND_OS_DATA__` 和 `__BOOK_OS_DATA__`）和 `src/build.py`（一次构建同时读两个
JSON、生成同一个 `index.html`）。两套数据共用同一套四象限十二子类分类体系（`quadrants`
结构在两个 JSON 里逐字相同），所以左右两组 Tab 的顶部快捷跳转条、卡片展开机制、编辑/高亮/
标星系统都是同一段代码在跑两份数据，不是分别实现的。

读书宇宙操作手册见 `BOOKS_UPDATE.md`；每日 42 天学习法的完整规则（角色设定/语言风格/书单/
交互流程/Mind Card 格式/质量检查）见 `BOOK_LEARNING_SYSTEM.md`（改造自用户原有的 v4.3
Project Instruction，把依赖 Claude.ai Projects 的 `recent_chats`/`project_knowledge_search`
换成了仓库原生实现，见该文件末尾"与 v4.3 的差异"表格）。跨系统进度记在
`data/book-os-progress.json`（上次完成到 Day 几、有没有悬挂问题——这是仓库版替代"搜索历史
对话"的机制）。

**两套数据怎么互链（现在是同页面内瞬间跳转，不是外部链接）**：`mind-os.json` 里某条
principle 如果有 `bookRefs: ["UT-xxx"]`，渲染成一个可点击的 chip，点击后原地切到"普世智
金字塔" Tab 并展开对应卡片；反过来 `book-os.json` 里某条 universalTruth 如果有
`mindOsRefs: ["MAS-x-xx"]`，点击后原地切到"思维库" Tab 并展开。这靠共享的 `overlay`/
`state.expanded` 和 `data-jump-kb`/`data-jump-pyramid` 这两个通用 data 属性 + 一套委托点击
处理实现，两边卡片结构 class 名一致（`.pcard-head`/`.star-btn`/`.chip-jump`），点击逻辑
天然通用，不需要为两边分别写跳转函数。页面加载时读 `location.hash` 也会自动判断该 ID
属于哪一边（`principleById` 还是 `truthById`）并展开。**新增双向链接时两边 JSON 都要改**，
只改一边等于单向链接。

**新内容进来时怎么判断归哪套数据（不确定就问用户，不要瞎猜）**：
- 内容是日常生活片段/情绪反思/某天发生的事 → 改 `data/mind-os.json`，走 `UPDATE.md` 的流程。
- 内容是读书笔记、书摘、Mind Card 学习法的每日产出、跨学科论点 → 改 `data/book-os.json`，走
  `BOOKS_UPDATE.md` / `BOOK_LEARNING_SYSTEM.md` 的流程。
- 内容同时涉及两边（比如某天的 Mind Card 学习本身就要把"归还日记库"那部分写回
  `mind-os.json`）→ 两个文件都要改，这是正常情况，不是例外。改完只需要跑一次
  `python3 src/build.py`、发布一次（因为现在是同一个 `index.html`/同一个 Artifact）。
- 两套数据的 Google Doc 源文件（无论是读书笔记 5 个文档，还是用户另外维护的"日记思维库
  2026"这类导出副本）**都不会被这个 repo 自动感知更新**——不存在被动监听 Google Drive
  文件变化的机制。用户想让新内容生效，必须在对话里明确说一声（"这本书读完了/这周日记
  更新了，帮我融进去"），Claude 才会去读文档、分类、改 JSON、重新构建发布。这是用户
  刻意选择的路径（手动触发，不建自动化基础设施），不要主动去接类似 Drive webhook 的
  自动同步方案，除非用户明确要求。

## 用户是谁 / 想要什么（不要重新问一遍）

- 这是个人向的成长笔记系统，不是给别人看的。用户看重的是**内容抓重点的能力和文字的"人味"**，
  超过看重某一次具体的分类是否完美——所以**内容允许持续被推倒重来**，不用小心翼翼只做增量。
- 明确要求**聚焦最近 3–4 年（2022 起）**的感悟。十年前的旧内容默认不收录，除非：
  1. 作为"过去的教训"挂在近年条目下（`era:"root"`，默认折叠）；
  2. 证明某个想法十年如一日一致；
  3. 至今仍适用、但近年日记里忘了再提的重大教训 → 标 `recency:"evergreen"`，
     即使打开"只看近 3–4 年"也保留可见。
- 讨厌单文档线性结构，要金字塔：先看到关键词/结构，再逐层点深入，**不要跳转新页面**，
  要在原地展开（accordion）。
- 思维库和原话集必须是同一套结构、互相锚定链接，不是两个独立的东西；生活记录（琐碎但有意义
  的生活片段）单独放，不进思维库的金字塔，避免喧宾夺主。
- 允许在网页里直接编辑文字/高亮/标星（用于日后回顾时标记重点），但**这个 Claude 账号目前没有
  Artifact 的云端存储能力**，所以编辑只存在 localStorage（单设备）。用户已经决定：暂时不追求
  自动跨设备同步，改用"发现想改的东西就在对话里告诉 Claude，Claude 直接改 canonical 数据并
  重新发布同一个链接"这个路径（因为对话本身跨设备同步）。不要主动去接 Google Drive 之类的
  MCP 云同步，除非用户明确要求。

## 文件结构与真源

```
CLAUDE.md                  ← 本文件：项目背景/长期约定，每次新会话自动加载
UPDATE.md                  ← 操作手册：怎么把新日记融入、怎么构建、编辑系统怎么用
BOOKS_UPDATE.md            ← 操作手册：怎么把新书/新 Mind Card 融入读书宇宙
BOOK_LEARNING_SYSTEM.md    ← 42 天跨学科 Mind Card 学习法的完整规则
data/mind-os.json          ← 日记真源：四象限骨架 + 全部 principles + lifeRecords + healthLog
data/book-os.json          ← 读书真源：同一套四象限骨架 + threads + books + universalTruths
data/book-os-progress.json ← 42 天学习法的跨会话进度（上次 Day 几/有没有悬挂问题）
src/template.html          ← 唯一的页面模板，同时渲染两套数据（HTML/CSS/JS，
                              __MIND_OS_DATA__ 和 __BOOK_OS_DATA__ 是两个数据占位符）
src/build.py                ← 构建脚本：把两个 JSON 都内联进模板 → 生成 index.html
index.html                  ← 生成产物，自包含单文件，发布为唯一的 Artifact
```

**改日记内容永远改 `data/mind-os.json`，改读书内容永远改 `data/book-os.json`，
改样式/交互永远改 `src/template.html`（两边共用同一份），然后跑 `python3 src/build.py`
重新生成 `index.html`，绝不直接手改 `index.html`。**

## 分类体系

用户自己发明的"四象限十二子类"分类法（处理自我/解释世界/应对他人/杠杆与博弈，每象限再分
2–4 个子类）。完整判定规则在 `mind-os-classifier` 技能的 `TAXONOMY.md` 里
（触发方式：把新日记内容丢给 Claude 时会自动用这个技能分类）。**这套顶层四象限十二子类是
用户自己的固定框架，不要改动它的结构**；但子类内部允许有"主题簇"这种展示层面的二级分组
（见下）——那是为了解决单个子类卡片堆太多、失去"总→分"层次感的问题，不影响底层分类 ID。

编号规则：`PREFIX-LETTER-NUMBER`（如 `MAS-A-10`），新增在该子类最大编号基础上 +10，
插入用中间整数，同子类内不能有重复编号。

## 已经走过的迭代（避免重新踩坑）

1. 从单个 Google 文档重建成结构化 JSON + 金字塔网页（v1）。
2. 配色刻意避开"暖米白+赭石"的 AI 默认审美，用冷调石灰纸+深松石绿；四象限各配一个辨识色。
3. 导航从"点三四层才看到内容"改成"打开即扁平连续滚动看到全部 12 个子类"，卡片原地展开
   （flex-basis 100% 打断栅格换行），配一个可跳转+滚动高亮当前区块的顶部快捷条。
4. 原话集改成和思维库完全一样的象限/子类分组结构，卡片标 ID，和思维库双向跳转互链。
5. 加了本机编辑系统（contenteditable + execCommand 高亮/文字色 + 标星），localStorage 持久化，
   导出/导入 JSON 作为跨设备桥梁；说明见上面"用户是谁"里的取舍。
6. 视觉语言手工照 shadcn/ui 的"new-york"风格复刻（Tabs 分段控件/Badge/卡片内 Accordion/
   聚焦环），因为 Artifact 是自包含单文件、CSP 禁止拉外部脚本，没法真的安装 shadcn 的
   React 组件源码——这是刻意的技术取舍，不是偷懒。
7. 加了"主题簇"二级分组（子类内按主题再分组，恢复金字塔"总→分"层次感），并对全部 120 条
   principles 做过一轮内容质检（分类/案例代表性/副标题去重复）。
8. 加了"查看原始日记片段"（`context` 字段）：思维库和原话集共用同一套 `quoteBlockHTML`/
   `caseItemHTML`/`ctxToggleHTML`，生活记录（含健康追踪）也接上了同一套机制——三处的
   "原文展开"是完全统一的同一段代码，不是分别实现的。字段没内容时按钮不渲染，不强行填充。
   目前覆盖：120 条 principles 里 45 条、63 条 lifeRecords 里 24 条挂了原文，年份覆盖
   2021–2025（2016–2020 root era 按用户指示暂不挖，除非用户明确要求）。
9. 修过一个"卡片区块显示不一致"的误报：`⏳ 历史回溯（近年）`这个标签命名是反的（近年内容
   不该叫"回溯历史"），已改名为平实的`📎 案例`；真正的旧年内容还是叫`🕰 历史根系`，折叠展示。
10. 修过一个真 bug：快捷跳转导航条点击没反应。根因是 `<body>` 上设了 `overflow-x:hidden`——
    这是个经典 CSS 陷阱，会让 `body` 变成一个独立滚动容器，从而破坏子孙元素的
    `position:sticky`（顶部导航栏实际上并没有真正吸顶）。**以后遇到"sticky 元素明明设了
    却不生效"，第一反应检查祖先链上是不是有非 visible 的 overflow。** 修法：overflow-x:hidden
    只放在 `html` 上，不放 `body`；`scrollToSection` 也从 `scrollIntoView()` 改成了在点击时
    实测头部实际高度再算精确的 `window.scrollTo` 偏移量，不依赖写死的 CSS scroll-margin-top。

## 原始日记源文件（Google Drive fileId 对照表，避免重新翻找）

10 个 PDF，每年一个，文件名形如"2016年1-12月.pdf"。用
`mcp__Google_Drive__read_file_content` 读全文（内容较长时会自动存成本地文件，用 Read 工具分段读）：

| 年份 | fileId |
|---|---|
| 2016 | `1kvXMgVQ1UsmZ_aWGpWD0xYEQMOA-EP8o` |
| 2017 | `1t35Cf7aAeyaEB5VwOK0wHy2ZJdZD65Sp` |
| 2018 | `1wYyCOqODxDg822yBO5BpIrx4Ne8lnafj` |
| 2019 | `1pkwEBl2JZTsGjqoVURFMdQEWH0vg3fol` |
| 2020 | `1U8pU7lE78zjr_fDrz1aPpngpWf3IjsQr` |
| 2021 | `1mz3PvSmZnZQRIy4y1Z3L3qdc-otWQKn9` |
| 2022 | `1bH5hBQ5qOugBAeIYIJ7_TJBaa49V7DUQ` |
| 2023 | `1lCpe8vwsq-GpIPCDcxWo98bNDICYFOKa` |
| 2024 | `1MQBAir50oBPfey0YL6e9gUYcu9130-Ea` |
| 2025 | `18ms0LmAFy5hury2iNIPQzz-67vRg5RtS` |

挖 `context` 原文片段的流程（如果用户要求继续往 2016–2020 补，或某年份想补更多条目）：
1. `read_file_content` 拉全年文本，本地存一份纯文本（不要每次都重新拉一遍全文再扫，存下来复用）。
2. 用日期做锚点匹配：`data/mind-os.json` 里每条 `quotes[]`/`cases[]` 都有 `date` 字段，去原文里找
   对应日期的日记条目（原文格式通常是"M/D(标题）\n\n年月日 星期X 时间\n\n正文"），把正文原样摘出来
   （不是重新概括），只在真的比现有摘要更长更完整时才补 `context`，宁可少补也不要编。
3. 补完跑 `python3 src/build.py` 重建、发布、提交推送。

## 构建 / 发布 / 提交的标准动作

```bash
python3 src/build.py     # 改完 data/mind-os.json、data/book-os.json 或 src/template.html
                          # 后重新生成 index.html——不管改的是哪一边的数据，只需要跑这一个脚本
```

发布用 `Artifact` 工具，`file_path` 传 `index.html`，`url` 传上面的固定链接，
`capabilities` 传 `{"downloads": true}`（编辑系统的导出功能要用）。
改完记得 `git add` + commit + push 到当前分支（不要新建分支，除非用户要求）。
