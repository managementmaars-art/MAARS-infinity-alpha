---
name: zipcode-search
description: Look up a Korean postcode from a known address with the official ePost road-name search page. Use when the user knows the address but wants the postal code quickly.
license: MIT
metadata:
  category: utility
  locale: ko-KR
  phase: v1
---

# Zipcode Search

## What this skill does

우체국 공식 도로명주소 검색 페이지를 조회해서 주소 키워드에 맞는 우편번호를 빠르게 찾는다.

## When to use

- "이 주소 우편번호 뭐야"
- "세종대로 209 우편번호 찾아줘"
- "판교역로 235 주소 코드만 빨리 알려줘"

## Prerequisites

- 인터넷 연결
- `curl`
- 선택 사항: `python3`

## Inputs

- 주소 키워드
  - 도로명 + 건물번호
  - 시/군/구 + 도로명
  - 동/리 + 지번

## Workflow

### 1. Query the official ePost page first

비공식 지도 검색이나 블로그 주소 데이터로 우회하지 말고 아래 우체국 공식 검색 페이지를 먼저 조회한다.

```text
https://parcel.epost.go.kr/parcel/comm/zipcode/comm_newzipcd_list.jsp
```

요청은 `keyword` 파라미터 하나만으로도 동작한다.

### 2. Fetch the HTML with curl and extract the candidate rows

현재 ePost 엔드포인트는 응답이 간헐적으로 reset/timeout 될 수 있으므로, 로컬 `python3` 기본 `urllib` 전송 대신 `curl --http1.1 --tls-max 1.2` + 재시도 경로를 기본 예시로 사용한다.

```bash
python3 - <<'PY'
import html
import re
import subprocess

query = "세종대로 209"
cmd = [
    "curl",
    "--http1.1",
    "--tls-max",
    "1.2",
    "--silent",
    "--show-error",
    "--location",
    "--retry",
    "3",
    "--retry-all-errors",
    "--retry-delay",
    "1",
    "--max-time",
    "20",
    "--get",
    "--data-urlencode",
    f"keyword={query}",
    "https://parcel.epost.go.kr/parcel/comm/zipcode/comm_newzipcd_list.jsp",
]
result = subprocess.run(
    cmd,
    check=True,
    capture_output=True,
    text=True,
    encoding="utf-8",
)
page = result.stdout

matches = re.findall(
    r'name="sch_zipcode"\s+value="([^"]+)".*?name="sch_address1"\s+value="([^"]+)".*?name="sch_bdNm"\s+value="([^"]*)"',
    page,
    re.S,
)

if not matches:
    raise SystemExit("검색 결과가 없습니다.")

for zip_code, address, building in matches[:5]:
    suffix = f" ({building})" if building else ""
    print(f"{zip_code}\t{html.unescape(address)}{suffix}")
PY
```

핵심 필드는 `sch_zipcode`(우편번호), `sch_address1`(기본 주소), `sch_bdNm`(건물명)이다.

바깥쪽 Python `timeout`은 두지 말고 `curl` 자체 제한(`--max-time` + `--retry`)으로 전송 시간을 제어한다. 전송 실패가 나도 바로 다른 소스로 우회하지 말고, 위 재시도 옵션 그대로 한 번 더 실행한 뒤 키워드를 더 구체화한다. 실전에서는 `세종대로 209` 같은 짧은 도로명 + 건물번호를 먼저 넣고, 실패하면 `서울 종로구 세종대로 209` 같은 시/군/구 포함 전체 주소 순으로 재시도한다.

### 3. Normalize for humans

응답은 raw HTML이므로 그대로 붙이지 말고 아래처럼 정리한다.

- 우편번호
- 표준 주소
- 건물명이 있으면 함께 표기
- 후보가 여러 개면 상위 3~5개만 보여주고 어느 항목이 가장 근접한지 짚기

### 4. Retry with tighter and fuller keywords when needed

검색 결과가 없거나 timeout/reset이 반복되면 아래 순서로 재시도한다.

- 짧은 도로명 + 건물번호: `세종대로 209`
- 시/군/구 포함 전체 주소: `서울 종로구 세종대로 209`
- 동/리 + 지번 또는 대체 표기: `세종로 209`

### 5. Prefer temp files in wrapped shells

CLI 래퍼나 에이전트 쉘에서는 here-doc + Python one-liner가 깨질 수 있으므로, 실전에서는 `mktemp` 같은 임시 파일에 HTML을 저장한 뒤 그 파일을 파싱하는 경로를 우선한다. 응답 일부만 보려고 `| head` 를 붙이면 다운스트림이 먼저 닫히면서 `curl: (23)` 이 보일 수 있으니, 이 경우도 전체 응답을 임시 파일에 저장한 뒤 확인한다.

## Done when

- 적어도 한 개의 우편번호 후보가 정리되어 있다
- 다중 후보일 때 사용자가 고를 수 있게 주소 차이가 보인다
- 검색 결과가 없으면 재검색 키워드 방향을 제안했다

## Failure modes

- 우체국 검색 페이지 마크업이 바뀌면 `sch_zipcode` 추출 규칙이 깨질 수 있다
- 주소 키워드가 너무 넓으면 결과가 과하게 많아질 수 있다
- 재시도 없이 한 번만 호출하면 timeout/reset 같은 일시 오류가 날 수 있다
- `curl` 없이 기본 `urllib` 전송으로 바로 붙으면 연결 reset이 날 수 있다

## Notes

- 조회형 스킬이다
- 상대 날짜/실시간 개념은 없으므로 주소 문자열 정제에 집중한다
