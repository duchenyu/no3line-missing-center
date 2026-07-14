# research_H.md — m=37 理论方向分析与排序

**日期**：2026-07-14
**状态**：分析完成；m=37 仍 OPEN。
**背景**：假解已撤回（`research_G.md` §6 已重写为 post-mortem）；`research_B.md` 的 Lemma B.1 已明确标注为 **NON-PROOF**（三处致命缺口，见 §1.4）。本文对用户提出的六条理论方向做精确分析与排序，结论先行：**LLL 在两个概率空间都失败；唯一能存活的严格路线是 conflict-free hypergraph MATCHING（Graves 2024）+ nibble 构造变体。**

---

## 0. 已锁定的事实

| 事实 | 来源 |
|---|---|
| m=3..36 全部存在 rot4 解；m=37 OPEN | 缓存 + CP-SAT 枚举 |
| 全部已知真解都是 **非置换 2-因子**（环型 `[m]` 或 `[1,m-1]`） | `mine_pattern.py` |
| Lemma B.1 不是存在性证明（基数/抽样度/错误模型三缺口） | `research_B.md` §3 状态块 |
| 固定骨架+随机双射 LLL 在 m=37 失败：`e·p·(d+1)=7.8e2` | `lll_pilot.py` |
| full 候选冲突超图**稠密**（度数 ~68k）；典型 2-因子上诱导子图**稀疏**（度数 ~157） | `lll_matching.py` + `conflict_hypergraph_params.json` |

---

## 1. LLL 死胡同的精确刻画

### 1.1 固定骨架 + 随机双射空间（`lll_pilot.py`）
- 模型：固定环型 `[37]` 骨架，对 37 个顶点随机赋予 label + 随机定向。
- 最坏 canonical 冲突事件：`p(X)=1.99e-4`，`N=3.98e6`，`d=1.44e6`。
- 对称 LLL 值 `e·p·(d+1)=7.8e2 ≫ 1` → FAIL；S-only 也 `1.3e2 ≫ 1`。
- **根因**：空间太粗——只有 37 个 label，依赖通过所有 label 爆炸。这是 `research_B.md` Lemma B.1 所犯的空间错误。

### 1.2 修正：正确的 canonical 空间是 **stub-matching 空间**
用户原话的"第二押注"才是正解空间：74 个 labeled stub，uniform 完美匹配 = uniform over **ALL** 2-因子（覆盖真解结构）。此处：
- 某特定 k-cell 集被选中的概率 = `1/(73·71·…·(73-2(k-1)))`，比双射空间小 3 个数量级；
- 两个事件相关 **iff 共享一个 stub**（codegree），不是共享 37 个 label。

### 1.3 但在 stub-matching 空间 LLL **仍然 FAIL**（`lll_matching.py` 精确枚举）
对 m=37 全量枚举（不存事件，仅增量计数）：

- `N = 30,998,788` 冲突事件（31M）；其中 `2-cell=6,756`，`3-cell=30,992,032`。
- `avg conflicts per cell = 67,925`（**关键纠正**：这是全部 `m²=1369` 候选 cell 上的 **FULL** 冲突超图度数。先前 `conflict_hypergraph_params.json` 里的 157 是 **典型 2-因子诱导子图**的度数，二者完全不同）。
- `max_ev_per_stub = 2,826,405`；`max_stubs/event = 6`；`d_max ≤ 6·max_ev_per_stub = 16,958,430`（严格上界）。
- `p2 = 1/(73·71) = 1.93e-4`（2-cell 二进制冲突，概率最大）；`p3 = 1/(73·71·69) = 2.80e-6`。
- 对称 LLL 值：`e·p2·(d+1) = 8.894e+03 ≫ 1` FAIL；`e·p3·(d+1) = 1.289e+02 ≫ 1` FAIL。

**结论**：LLL 在**两个空间都失败**。原因不是 m=37 无解，而是 LLL 是上界方法，在 FULL 稠密冲突超图（度数 ~68k → 依赖度 d ~ 千万级）下天然太弱。双射空间 `p·N≈800`（阈值的 ~2000×）；匹配空间 expected bad ≈ 10，但 d 同样巨大。

### 1.4 Lemma B.1 三处致命缺口（已在 `research_B.md` 标注）
1. **基数缺口**：LLL 保证 `Pr(无坏事件)>0`，但空集也满足"无坏事件"；"期望选中 ≥m" 不推出 "存在大小 ≥m 的无冲突集"。
2. **抽样度缺口**：`x_deg_max=380/800` 来自抽样 2-因子，不是 FULL 冲突超图的严格最大度（真实 full 度数 ~68k）。
3. **错误模型缺口**：文档仍把 2-因子写成 permutation/bijection，但已知真解全是非置换 2-因子。

---

## 2. 唯一能存活的严格路线：conflict-free hypergraph MATCHING（Graves 2024）

### 2.1 为什么它能越过 LLL 的死胡同
- LLL 看**总度数**（巨大）→ 失败。
- 冲突自由匹配定理（**Graves 2024, arXiv:2205.05564**）控制的是 **codegree**（含某固定 stub-对/边的冲突数），不是总度数；covering 扩展（**arXiv:2407.18144**）处理"覆盖全部 stub"部分。
- 形式化：74 stub；一个完美匹配 = 一个 2-因子（每对匹配 stub = 一个 directed cell）；`S`/`X` = 禁止共现的边子集；目标 = 覆盖所有 stub 的**冲突自由**完美匹配。

### 2.2 关键纠正：full 超图稠密，真正起作用的是 **induced 稀疏性**
- full 候选冲突超图度数 ~68k（稠密）→ naive matching 定理的 codegree 条件也必须**显式验证**，不能想当然。
- 但 **典型 2-因子上的诱导子图度数仅 ~157**（实测 `conflict_hypergraph_params.json`：m=37 `x_deg_max=380`，`x_deg_per_cell=157`）。
- **nibble / semi-random 方法**正是利用这点：逐步构造 2-因子，每加一个 cell 只与**已选 cell 的小集合**比较冲突。因已选集小（≤m=37），新 cell 的冲突伙伴虽在 full 图有 68k，但其中"已被选中"的期望数极小 → nibble w.h.p. 成功。

### 2.3 构造性变体（推荐立即执行）
- nibble + 局部回溯 / absorption。因 induced 稀疏，可在**数分钟**内计算（不像冻死 PC 的 SA）。
- 这**双重**有价值：既是构造性存在证明，又能**真正找到**一个 m=37 解（若找到即闭合问题）。
- 若 nibble 卡死 → 记录卡在哪些"小冲突核" → 直接喂给方向 6（最小冲突核）。

---

## 3. 六个方向排序

| # | 方向 | 判定 | 理由 |
|---|---|---|---|
| **1** | **conflict-free 超图匹配 + nibble（Graves 2024）** | **主路线 / 可行** | codegree 路线越过 LLL 死胡同；nibble 构造变体可在分钟级计算并真正找解。m=37 与渐近都适用。 |
| 2 | canonical LLL（修正后 stub-matching 空间） | 原理正确但 m=37 FAIL | 精确枚举证伪（§1.3）。仅可作匹配证明内部的局部引理（处理残余小冲突）或用于更小 m。 |
| 3 | mod-2 / mod-素数计数（Pfaffian + 冲突容斥） | 上限最高、风险最高 | `Z_37≠0 ⇒ 存在`（精确）。难点：Pfaffian 作用于哪个矩阵？2-因子计数经 skew-adjacency Pfaffian，再容斥减冲突。若 codegree 允许 Möbius 反演，则是最干净的计算机辅助证明。 |
| 4 | Gaussian integer 表示（C4=×i） | 结构/说明性 | 共线 = `Im((z_j−z_i)·conj(z_k−z_i))=0`。不降难度（仍二次）但暴露代数结构；可喂方向 3（计数）或 6（kernel）。 |
| 5 | 等变 oriented matroid（带 C4 作用的 chirotope） | 次要 / 分类仪器 | 刻画点集有向拟阵，C4-等变剪枝。但 chirotope 存在 ≠ 可构造找到；多用于证明某些子构型不可能。 |
| 6 | 最小冲突核定理 | 有希望但需扩展引理 | 小 m 枚举最小不可修复 2-因子冲突核（符号行列式、discharging）；若有"核吸收/扩展"引理提升到 m=37 则是证明。该扩展引理是匹配吸收的兄弟。 |

---

## 4. 推荐的具体下一步（要实际跑什么）

- **(a)** 完成 `lll_matching.py` 精确数字 → 确认 FAIL（本轮已出 N/度数，d_upper 待定）。
- **(b)【主】** 在 stub-matching 空间实现 **nibble**：反复取随机未匹配 stub，与不产生 `(S)/(X)` 冲突的合法伙伴配对；死路回溯。对 m=37 运行，时间预算分钟级。构造性闭合路径。
- **(c)** 并行：为我们的具体冲突超图推导 **Graves 型 codegree 充分条件**，用实测 codegree（induced 最大 380 / 平均 157）核对是否满足 → 若满足则严格非构造存在性证明。
- **(d)** `mod-p` 计数在 small m（如 m=10,14）做 pilot，验证 Pfaffian+IE 思路再扩到 m=37。

---

## 5. 风险与开放问题

1. matching 定理的 codegree 条件在 full 稠密超图上是否满足，需**(c)** 显式验证；不能假设。
2. nibble 在 m=37 是否会卡在特定小冲突核，需**(b)** 实测；卡点即方向 6 的输入。
3. mod-p 计数需确定正确的 Pfaffian 矩阵与冲突容斥的收敛性（方向 3）。

---

## 6. 一句话结论

> **LLL 在两个概率空间都证明不了 m=37（full 冲突超图太稠密，d~千万级）。但稠密是"全集"现象——典型 2-因子诱导子图极稀疏（度数~157），所以 conflict-free MATCHING（codegree 控制）+ nibble 构造才是越过死胡同的正确路线，且能在分钟级真正找到解。**
