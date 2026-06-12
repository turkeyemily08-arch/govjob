# -*- coding: utf-8 -*-
"""GOV잡 트래커 번들(INIT_JOBS) 안전 편집 도구.

사용법 (저장소 루트에서):
  python tools/jobs_tool.py list                      # 전체 공고 id/상태/기관명 출력
  python tools/jobs_tool.py dump                      # data/jobs.json 으로 백업 추출
  python tools/jobs_tool.py add new_job.json          # 새 공고 추가 (마지막 공고를 템플릿으로 복제 후 덮어씀)
  python tools/jobs_tool.py set <id> status=서류제출   # 기존 공고 필드 수정

new_job.json 예시 (지정한 필드만 덮어쓰고 나머지는 템플릿 값 유지):
  {"id": 35, "org": "기관명", "url": "https://...", "status": "접수중",
   "fit": 0, "fitReason": "", "memo": "", "collected": "", "driveUrl": ""}

안전장치:
- 필드 타입을 템플릿(마지막 공고)과 대조해 다르면 중단
- 저장 전 라운드트립(디코드→인코드→디코드) 검증
- 번들에서 atob 문자열 외의 바이트는 절대 건드리지 않음
저장 후: git add/commit/push 하면 GitHub Pages 자동 배포.
"""
import json, re, base64, sys, glob, os, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_bundle():
    files = glob.glob(os.path.join(ROOT, 'assets', 'index-*.js'))
    if len(files) != 1:
        sys.exit(f'번들 파일이 1개가 아닙니다: {files}')
    return files[0]


def load(path):
    src = open(path, encoding='utf-8').read()
    m = re.search(r'atob\("([A-Za-z0-9+/=]+)"\)', src)
    if not m:
        sys.exit('atob("...") 패턴을 찾지 못했습니다 — 번들 구조가 바뀌었을 수 있음')
    data = json.loads(base64.b64decode(m.group(1)).decode('utf-8'))
    return src, m.group(1), data


def save(path, src, old_b64, data):
    new_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    new_b64 = base64.b64encode(new_str.encode('utf-8')).decode('ascii')
    old_tok, new_tok = f'atob("{old_b64}")', f'atob("{new_b64}")'
    if src.count(old_tok) != 1:
        sys.exit('atob 토큰이 정확히 1번 나오지 않음 — 중단')
    new_src = src.replace(old_tok, new_tok)
    # 라운드트립 검증
    m2 = re.search(r'atob\("([A-Za-z0-9+/=]+)"\)', new_src)
    data2 = json.loads(base64.b64decode(m2.group(1)).decode('utf-8'))
    assert data2 == data, '라운드트립 검증 실패'
    # atob 외 부분이 동일한지 검증
    assert new_src.replace(new_tok, '') == src.replace(old_tok, ''), '번들 다른 부분이 변경됨'
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(new_src)
    print(f'저장 완료: {len(data)}건')


def check_types(template, job):
    for k, v in job.items():
        if k in template and not isinstance(v, type(template[k])):
            sys.exit(f"타입 불일치: '{k}' 는 {type(template[k]).__name__} 이어야 하는데 "
                     f"{type(v).__name__} 가 들어옴 (예: doc/written/final 은 \"-\" 문자열)")


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    cmd = sys.argv[1]
    path = find_bundle()
    src, b64, data = load(path)

    if cmd == 'list':
        for j in data:
            print(f"{j['id']} | {j.get('status','')} | {j.get('org','')}")
        print(f'총 {len(data)}건')

    elif cmd == 'dump':
        out = os.path.join(ROOT, 'data', 'jobs.json')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        print(f'백업 저장: {out} ({len(data)}건)')

    elif cmd == 'add':
        overrides = json.load(open(sys.argv[2], encoding='utf-8-sig'))
        template = data[-1]
        check_types(template, overrides)
        new_job = template.copy()
        # 템플릿 고유값은 비우고 시작
        for k in ('fitReason', 'duty', 'region', 'type', 'deadlineDoc', 'deadlineDocLabel',
                  'deadlineWritten', 'deadlineInterview', 'deadlineInterview2', 'deadlineAnnounce',
                  'ncs', 'memo', 'collected', 'docEvalType', 'docEvalRatio', 'salary', 'headcount',
                  'notice', 'deadlineTime', 'driveUrl', 'failReason', 'startDate'):
            new_job[k] = ''
        new_job.update({'doc': '-', 'written': '-', 'final': '-', 'fit': 0, 'status': '접수중'})
        new_job.update(overrides)
        if 'id' not in overrides:
            new_job['id'] = max(j['id'] for j in data) + 1
        if any(j['id'] == new_job['id'] for j in data):
            sys.exit(f"id {new_job['id']} 이미 존재")
        data.append(new_job)
        save(path, src, b64, data)
        print(f"추가됨: id={new_job['id']} {new_job['org']}")

    elif cmd == 'set':
        jid = int(sys.argv[2])
        job = next((j for j in data if j['id'] == jid), None)
        if not job:
            sys.exit(f'id {jid} 없음')
        for kv in sys.argv[3:]:
            k, v = kv.split('=', 1)
            if k in job and isinstance(job[k], int):
                v = int(v)
            job[k] = v
        save(path, src, b64, data)
        print(f"수정됨: id={jid} {job['org']}")

    else:
        print(__doc__)


if __name__ == '__main__':
    main()
