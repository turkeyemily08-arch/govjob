# GOV잡 트래커 (배포 저장소)

이 폴더는 **빌드 결과물(dist) 전용** git 저장소다. 소스(src/, package.json)는 이 PC에 없다.
push하면 GitHub Pages(https://turkeyemily08-arch.github.io/govjob/)로 자동 배포된다.

## 공고 데이터 수정 — 반드시 tools/jobs_tool.py 사용 (번들 직접 수정 금지!)

데이터는 `assets/index-*.js` 안의 `atob("...")` base64 문자열(INIT_JOBS)에 내장돼 있다.
즉석 스크립트로 직접 수정하다 번들이 깨진 사고가 있었음(2026-06-12, 흰 화면).
필드 타입 검증·라운드트립 검증이 내장된 전용 도구를 쓸 것:

```
python tools/jobs_tool.py list                   # 공고 목록
python tools/jobs_tool.py dump                   # data/jobs.json 백업 추출
python tools/jobs_tool.py add new_job.json       # 새 공고 추가 (id 자동 부여)
python tools/jobs_tool.py set 34 status=서류제출  # 필드 수정
```

new_job.json 최소 예시: `{"org":"기관명","url":"https://...","status":"접수중"}`
나머지 필드는 빈 값/기본값으로 자동 채워진다. 세부 정보는 `set`으로 추가.

수정 후 배포:
```
python tools/jobs_tool.py dump   # 백업 갱신
git add -A && git commit -m "..." && git push origin main
```

## 주의사항

- **doc/written/final 필드는 "-" 문자열** (boolean 넣으면 앱이 e.match 에러로 흰 화면)
- 사용자(규리)의 실시간 상태는 본인 크롬(turkey 프로필)의 localStorage에만 있다.
  번들 INIT_JOBS는 초기값일 뿐이며, 같은 id는 사용자 저장본이 우선, 새 id는 자동 병합된다.
- `data/jobs.json`은 최근 백업 스냅샷 — 데이터 유실 시 이 파일로 INIT_JOBS를 복원할 수 있다.
- 배포 확인: push 후 1~2분 뒤 사이트에서 Ctrl+Shift+R
