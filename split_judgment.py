with open('判決書全文.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

LIMIT = 90000
title = '# 臺灣臺北地方法院刑事判決 113年度金訴字第51號'

# Find the best split lines: blank line closest to each 90k boundary
def find_split(lines, target_char, start_line=0):
    """Find the index of a blank line closest to target_char offset from start_line."""
    cumulative = sum(len(l) for l in lines[:start_line])
    best_line = start_line
    best_dist = float('inf')
    for i in range(start_line, len(lines)):
        cumulative += len(lines[i])
        if lines[i].strip() == '':
            dist = abs(cumulative - target_char)
            if dist < best_dist:
                best_dist = dist
                best_line = i
            if cumulative > target_char + 5000:
                break
    return best_line

split1 = find_split(lines, 90000, 0)
split2 = find_split(lines, 180000, split1)

print(f"Split 1 at line {split1+1}, cumulative chars: {sum(len(l) for l in lines[:split1]):,}")
print(f"Split 2 at line {split2+1}, cumulative chars: {sum(len(l) for l in lines[:split2]):,}")

part1 = lines[:split1]
part2 = lines[split1:split2]
part3 = lines[split2:]

def char_count(ls):
    return sum(len(l) for l in ls)

print(f"Part 1: {char_count(part1):,} chars")
print(f"Part 2: {char_count(part2):,} chars")
print(f"Part 3: {char_count(part3):,} chars")

# Write files
with open('判決書全文-1.md', 'w', encoding='utf-8') as f:
    f.writelines(part1)
    f.write(f'\n\n---\n*（下接 判決書全文-2）*\n')

with open('判決書全文-2.md', 'w', encoding='utf-8') as f:
    f.write(f'{title}（續二）\n\n')
    f.writelines(part2)
    f.write(f'\n\n---\n*（下接 判決書全文-3）*\n')

with open('判決書全文-3.md', 'w', encoding='utf-8') as f:
    f.write(f'{title}（續三）\n\n')
    f.writelines(part3)

print("Done.")
