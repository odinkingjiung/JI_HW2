# Steam Live Players (FastAPI)

Steam 공개 Web API를 이용해 Counter-Strike 2, PUBG: BATTLEGROUNDS, Dota 2의 현재 동시접속자 수를 보여주는 FastAPI 웹 서비스입니다.

## 주요 기능

- 게임별 현재 접속자 수 카드 표시
- 여러 게임의 접속자 수를 비교하는 막대 그래프
- 데이터 새로고침 버튼
- Steam API 연결 오류 및 잘못된 게임 정보 오류 메시지

## 사용 기술

- Python 3.13
- FastAPI, Uvicorn
- Requests
- HTML, CSS, JavaScript
- pytest
- GitHub Actions, Render 설정 파일

## 설치

Windows PowerShell에서 프로젝트 폴더로 이동한 뒤 실행합니다.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

가상환경 생성이 어려운 경우 Python이 설치된 환경에서 `py -m pip install -r requirements.txt`를 사용할 수 있습니다.

## 로컬 실행

```powershell
py -m uvicorn app:app --reload
```

브라우저에서 <http://127.0.0.1:8000>을 엽니다. Steam API 연결은 실행 컴퓨터의 네트워크 환경에 따라 달라질 수 있습니다.

## 테스트

```powershell
py -m pytest -q
```

FastAPI 변경 후 검증 결과는 다음과 같습니다.

- pytest 테스트 3개 모두 통과
- 로컬 Flask 페이지 HTTP 응답 정상 확인
- 잘못된 게임 정보에 대한 오류 응답 정상 확인
- 현재 실행 환경의 외부 네트워크 제한으로 Steam API 실제 조회는 실패
- 실제 브라우저 GUI 테스트는 수행하지 못함

따라서 사용자 컴퓨터에서 Steam API가 정상적으로 연결되는지는 별도로 확인해야 합니다.

## GitHub Actions 자동 테스트

`.github/workflows/ci.yml`은 GitHub 저장소에 push하거나 pull request를 생성할 때 Ubuntu 환경에서 Python을 설치하고 `python -m pytest -q`를 실행합니다.

## Render 배포

Render 배포는 아직 완료되지 않았습니다. 다음 절차로 직접 진행합니다.

1. GitHub에 새 저장소를 만들고 이 `upload` 폴더의 파일을 저장소에 업로드합니다.
2. Render에 로그인하고 **New > Web Service**를 선택합니다.
3. GitHub 계정을 연결한 뒤 해당 저장소를 선택합니다.
4. 저장소의 `render.yaml`을 사용하거나 Build Command에 `pip install -r requirements.txt`, Start Command에 `uvicorn app:app --host 0.0.0.0 --port $PORT`를 입력합니다.
5. 배포가 완료되면 Render 대시보드에서 생성된 공개 URL을 확인합니다.
6. 공개 URL에서 게임 카드, 그래프, 새로고침 및 오류 표시를 확인합니다.

이 패키지에는 실제 GitHub 저장소 주소나 Render 공개 URL이 포함되어 있지 않습니다. 계정 연결과 배포는 사용자가 직접 수행해야 합니다.
