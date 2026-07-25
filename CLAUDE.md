# 项目背景（每次新会话都先读这个）

这个 repo 只做一件事：把用户 2016–2026 的日记，蒸馏成一个私人知识库网页
「个人思维操作系统 · Mind OS」，发布为一个**私密 Artifact**（用户手机/电脑随时打开）。

**当前线上链接（固定，不要发布成新链接）**：
https://claude.ai/code/artifact/354d6b9a-e846-4293-a021-7a01cc768be0

每次改完都用 `Artifact` 工具把 `index.html` 重新发布到**这同一个 url**（传 `url` 参数），
这样用户不需要换书签。

## 第二套系统：读书宇宙 · Book OS（2026-07-25 新增，同一个 repo 里）

这个 repo 现在维护**两套独立但互链的系统**：上面的日记 Mind OS，和读书笔记「读书宇宙 ·
Book OS」——40 本书的读书笔记（5 个 Google Doc）+ 一套 42 天跨学科 Mind Card 学习法
蒸馏成的"普世智金字塔"。两套系统**不合并成一个页面**（用户明确选择过"两个独立 Artifact +
双向链接"，不要改成合并），但共用同一套四象限十二子类分类体系，卡片之间可以互相跳转。

**Book OS 当前线上链接（固定，不要发布成新链接）**：
https://claude.ai/code/artifact/2614e44c-ee3d-4f86-add4-668ff07b7f23

Book OS 的真源是 `data/book-os.json`，模板是 `src/book_template.html`，构建脚本是
`src/build_books.py`，生成产物 `book-os.html`。操作手册见 `BOOKS_UPDATE.md`；每日 42 天
学习法的完整规则（角色设定/语言风格/书单/交互流程/Mind Card 格式/质量检查）见
`BOOK_LEARNING_SYSTEM.md`（改造自用户原有的 v4.3 Project Instruction，把依赖 Claude.ai
Projects 的 `recent_chats`/`project_knowledge_search` 换成了仓库原生实现，见该文件末尾
"与 v4.3 的差异"表格）。跨系统进度记在 `data/book-os-progress.json`（上次完成到 Day 几、
有没有悬挂问题——这是仓库版替代"搜索历史对话"的机制）。

**两套系统怎么互链**：`mind-os.json` 里某条 principle 如果有 `bookRefs: ["UT-xxx"]`，
渲染成一个跳转到 book-os.html#UT-xxx 的外链；反过来 `book-os.json` 里某条 universalTruth
如果有 `mindOsRefs: ["MAS-x-xx"]`，渲染成跳转到 index.html#MAS-x-xx 的外链。两个模板都在
加载时读 `location.hash` 自动展开命中的卡片。**新增双向链接时两边 JSON 都要改**，只改
一边等于单向链接。

**新内容进来时怎么判断归哪个系统（不确定就问用户，不要瞎猜）**：
- 内容是日常生活片段/情绪反思/某天发生的事 → Mind OS，走 `UPDATE.md` 的流程。
- 内容是读书笔记、书摘、Mind Card 学习法的每日产出、跨学科论点 → Book OS，走
  `BOOKS_UPDATE.md` / `BOOK_LEARNING_SYSTEM.md` 的流程。
- 内容同时涉及两边（比如某天的 Mind Card 学习本身就要把"归还日记库"那部分写回
  `mind-os.json`）→ 两个文件都要改，这是正常情况，不是例外。
- 两套系统的 Google Doc 源文件（无论是读书笔记 5 个文档，还是用户另外维护的"日记思维库
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
CLAUDE.md               ← 本文件：项目背景/长期约定，每次新会话自动加载
UPDATE.md                ← 操作手册：怎么把新日记融入、怎么构建、编辑系统怎么用
data/mind-os.json        ← 唯一真源：四象限骨架 + 全部 principles + lifeRecords + healthLog
src/template.html        ← 页面模板（HTML/CSS/JS，__MIND_OS_DATA__ 是数据占位符）
src/build.py             ← 构建脚本：把 JSON 内联进模板 → 生成 index.html
index.html               ← 生成产物，自包含单文件，发布为 Artifact
```

**改内容永远改 `data/mind-os.json`，改样式/交互永远改 `src/template.html`，
然后跑 `python3 src/build.py` 重新生成 `index.html`，绝不直接手改 `index.html`。**

（读书宇宙 Book OS 是同样的模式，另一套文件：`data/book-os.json` / `src/book_template.html` /
`src/build_books.py` / `book-os.html`，详见上面"第二套系统"一节。）

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
python3 src/build.py     # 改完 data/mind-os.json 或 src/template.html 后重新生成 index.html
```

发布用 `Artifact` 工具，`file_path` 传 `index.html`，`url` 传上面的固定链接，
`capabilities` 传 `{"downloads": true}`（编辑系统的导出功能要用）。
改完记得 `git add` + commit + push 到当前分支（不要新建分支，除非用户要求）。

Book OS 同理：`python3 src/build_books.py` 生成 `book-os.html`，`Artifact` 工具发布到
`file_path: book-os.html`、`url` 传本文件"第二套系统"一节里的 Book OS 固定链接。如果同一次
改动两边都动了（比如一天的 Mind Card 学习产出既写了 `book-os.json` 又写了 `mind-os.json`），
两个 `build` 脚本都要跑、两个 Artifact 都要重新发布。
