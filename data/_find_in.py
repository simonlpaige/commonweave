import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
with open(r'C:\Users\simon\.openclaw\workspace\commonweave\data\native_queries.py', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "'IN':" in line:
        print(f'Line {i+1}: {line}', end='')
        for j in range(i, min(i+20, len(lines))):
            print(f'  {j+1}: {lines[j]}', end='')
        break
