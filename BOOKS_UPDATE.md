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
  笔记，帮我融进读书宇宙"。Claude 会判断是强化已有 `universalTruths` 还是新增一条，
  更新对应 `books[]` 的 `status`。
- **两边内容都要更新**（比如某天聊的东西同时涉及新日记和新书感悟）→ 直接说清楚就行，
  Claude 会分别写回两个 JSON，仍然只需要构建发布一次。如果内容本身就写得含糊，Claude
  会先确认再动手，不会瞎猜。

## 文件结构

```
data/book-os.json          ← 读书宇宙真源：四象限骨架（与日记共用同一套taxonomy）+ threads[]
                              （跨学科主线注册表）+ books[]（书目roster）+ universalTruths[]
src/template.html          ← 页面模板（与日记共用同一份），"普世智金字塔/关联图谱/书籍索引"
                              三个 Tab 渲染这份数据；关联图谱是纯 SVG + 原生 JS 手写的枢纽图
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

`src/template.html` 里"关联图谱" tab 是纯 SVG + 原生 JS 手写的枢纽图（不依赖任何外部
可视化库，因为 Artifact 的 CSP 不允许拉 CDN）：以 `threads[]` 里每条主线为一个枢纽节点，
所有标了该 thread 的 `universalTruths` 作为卫星节点画线连过去，节点按四象限配色、点击
跳转回金字塔里对应的完整卡片。没有标 thread 的条目会归到"待归类"分组，不会丢失，只是
暂时没连线——这也是提醒你它可能还没找到真正的跨学科连接。

## 书籍索引 tab 与 `books[]` 的 `status`

`status` 有三档：`queued`（还没开始梳理）、`in-progress`（有笔记但还没覆盖全书核心论点）、
`distilled`（核心论点已完整提炼）。新书完成梳理后记得把 `status` 更新到位——「书籍索引」
tab 顶部的覆盖率统计（"X / 40 已开始梳理"）直接读这个字段，是检验"金字塔到底盖了多少"
的唯一真实指标，不要让它长期停留在过时状态。

## 40 本书全量迁移怎么做（下一步，等你说开始再动）

当前 `data/book-os.json` 里只有 3 本书（认知觉醒/贪婪的多巴胺/掌控习惯）被处理成了
`universalTruths`，其余 37 本只进了 `books[]` 的 roster（`status: "queued"`）。全量迁移
的流程：

1. 用 `mcp__Google_Drive__read_file_content` 拉 5 个源文档全文（同日记系统一样，拉一次
   存本地复用，不要每次重新拉）。
2. 按 `##书名：《XX》` 分节，逐本书提炼 3-8 条核心论点，优先吃标了【特有感】的段落
   （这是原作者——也就是你——自己标的"这点对我有意义"信号，等价于日记的 context 挖掘
   线索）。
3. 每条论点判断归入四象限十二子类的哪个子类/簇，参考 `mind-os-classifier` 技能的
   `TAXONOMY.md`（同一套体系，不用改判定规则）。
4. 单本书内部的论点如果和其他书已有的 `universalTruths` 内核相同，合并（追加到
   `insights[]`/`books[]`），不是每本书都必须开新条目——**这正是"跨学科"的价值所在**：
   越多书落进同一条 `universalTruth`，说明这条越接近真正的普世智。
5. 跑 `python3 src/build.py`，republish，git commit。

这一步信息量很大（5 个文档、几十本书），建议分批做（比如一次一个文档），做完跟你确认
再继续下一批，而不是一次性全塞进一次对话上下文。
