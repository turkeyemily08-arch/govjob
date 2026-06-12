# -*- coding: utf-8 -*-
# 일회성 UI 패치 (2026-06-12): 패스 별도 그룹 분리 + 회색 행 가독성 개선
import io, sys, glob, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = glob.glob(os.path.join(ROOT, 'assets', 'index-*.js'))[0]
src = open(path, encoding='utf-8').read()

EDITS = [
    # 1) ma(): 패스(미지원)를 그룹 4로 분리
    ("function ma(e){return e.fit===0||e.status.includes(`불합격`)||e.status.includes(`마감`)||e.status===`패스(미지원)`?3:da.has(e.status)?0:pa(e)?2:1}",
     "function ma(e){return e.status===`패스(미지원)`?4:e.fit===0||e.status.includes(`불합격`)||e.status.includes(`마감`)?3:da.has(e.status)?0:pa(e)?2:1}"),
    # 2) 그룹 헤더: 4번 추가, 3번 이름 정리
    ("ha={0:`📋 제출 진행중`,1:`📌 접수 예정 / 모니터링`,2:`🕐 보류 (상시 · 하반기 예정 · 미정)`,3:`⏹ 마감 · 불합격 · 패스`}",
     "ha={0:`📋 제출 진행중`,1:`📌 접수 예정 / 모니터링`,2:`🕐 보류 (상시 · 하반기 예정 · 미정)`,3:`⏹ 마감 · 불합격`,4:`🚫 패스(미지원)`}"),
    # 3) 회색 행 투명도 완화 (.55 → .8)
    ("opacity:o?.55:1", "opacity:o?.8:1"),
]

for old, new in EDITS:
    n = src.count(old)
    if n != 1:
        sys.exit(f'중단: 패턴이 {n}회 발견됨 (1회여야 함): {old[:60]}...')
    src = src.replace(old, new)
    print(f'OK: {old[:50]}...')

with open(path, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
print('패치 완료')
