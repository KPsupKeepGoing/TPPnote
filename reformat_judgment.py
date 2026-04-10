"""
重新格式化判決書全文.md：
1. ### 主文/事實/理由  → ## 大節
2. 壹/貳/參...        → ### 中節 (h3)
3. 一/二/三...短標題  → #### 小節 (h4)
4. ㈠㈡...短標題      → ##### 子節 (h5)
5. 獨立日期行         → 前置空行
6. 過長段落中若出現「XXX年XX月XX日，」作為句首 → 前置空行（斷段）
"""
import re

with open('判決書全文.md', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. 主文 / 事實 / 理由 → h2 ──────────────────────────────────────
content = re.sub(r'###\s*主\s*文', '## 主文', content)
content = re.sub(r'###\s*事\s*實', '## 事實', content)
content = re.sub(r'###\s*理\s*由', '## 理由', content)

# ── 2. 壹/貳/參/肆/伍/陸/柒/捌/玖/拾 開頭的獨立行 → h3 ──────────
KANJI_L1 = '壹貳參肆伍陸柒捌玖拾'
def upgrade_l1(m):
    line = m.group(1)
    # 已有 ### 開頭則跳過
    if line.startswith('#'):
        return m.group(0)
    return f'\n### {line}\n'

content = re.sub(
    r'(?m)^([壹貳參肆伍陸柒捌玖拾][、，：].{0,60})$',
    upgrade_l1,
    content
)

# ── 3. 一、二、三... 短行 → h4 ──────────────────────────────────────
KANJI_L2 = '一二三四五六七八九十'
def upgrade_l2(m):
    line = m.group(1)
    if line.startswith('#'):
        return m.group(0)
    return f'\n#### {line}\n'

# 只有行長 ≤ 60 字的獨立行才升為標題（避免誤判長句）
content = re.sub(
    r'(?m)^([一二三四五六七八九十][一二三四五六七八九十]?[、，：].{0,55})$',
    upgrade_l2,
    content
)

# ── 4. ㈠㈡㈢... 短行 → h5（加粗段首） ──────────────────────────────
PAREN_NUMS = '㈠㈡㈢㈣㈤㈥㈦㈧㈨㈩'
def upgrade_l3(m):
    line = m.group(1)
    if line.startswith('#'):
        return m.group(0)
    return f'\n##### {line}\n'

content = re.sub(
    r'(?m)^([㈠㈡㈢㈣㈤㈥㈦㈧㈨㈩].{0,50})$',
    upgrade_l3,
    content
)

# ── 5. 獨立的日期行（行首即日期）→ 前置空行 ──────────────────────────
# 例如：「民國109年3月10日」、「109年3月10日（星期二）」
DATE_PAT = re.compile(
    r'(?m)^(?!#)(?=(?:民國\s*)?[0-9一二三四五六七八九十百]+年[0-9一二三四五六七八九十]+月[0-9一二三四五六七八九十]+日)'
)
def ensure_blank_before_date_line(content):
    lines = content.split('\n')
    result = []
    for i, line in enumerate(lines):
        # 如果這一行以日期開頭且前一非空行不是空行也不是標題
        if re.match(r'^(?:民國\s*)?[0-9一二三四五六七八九十百]+年[0-9一二三四五六七八九十]+月[0-9一二三四五六七八九十]+日', line):
            if result and result[-1].strip() != '' and not result[-1].startswith('#'):
                result.append('')
        result.append(line)
    return '\n'.join(result)

content = ensure_blank_before_date_line(content)

# ── 6. 在長段落中，遇到「，XXX年XX月XX日，」斷段 ──────────────────
# 找到「；XXX年」或「。XXX年」後接日期的位置，插入段落分隔
# （僅限理由書正文中，不在引言、標題行中）
def break_on_dates_in_paragraphs(content):
    """在「；民國XXX年」或句號後接年份前插入雙換行，讓每個時間節點自成一段。"""
    # 標記：句末標點後緊接日期，且前後都是同一段文字（不在標題行）
    pattern = re.compile(
        r'([；。])((?:民國\s*)?[0-9一二三四五六七八九十百]{2,4}年[0-9一二三四五六七八九十]{1,2}月[0-9一二三四五六七八九十]{1,2}日)'
    )
    return pattern.sub(r'\1\n\n\2', content)

content = break_on_dates_in_paragraphs(content)

# ── 7. 清除多餘空行（連續超過2個空行 → 2個空行）──────────────────
content = re.sub(r'\n{3,}', '\n\n', content)

# ── 寫出 ─────────────────────────────────────────────────────────────
with open('判決書全文.md', 'w', encoding='utf-8') as f:
    f.write(content)

lines = content.split('\n')
print(f"完成。共 {len(lines)} 行，{len(content)} 字元")

# 印出新標題結構預覽
print("\n=== 標題結構預覽 ===")
for i, line in enumerate(lines, 1):
    if line.startswith('#'):
        print(f"L{i:4d}  {line[:80]}")
