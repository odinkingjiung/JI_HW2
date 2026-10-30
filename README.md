# Steam Live Players

Steam 공개 Web API로 Counter-Strike 2, PUBG: BATTLEGROUNDS, Dota 2의 현재 동시접속자 수를 보여주는 Flask 웹 서비스입니다. 게임별 카드, 막대 그래프, 수동 새로고침, API 오류 메시지를 제공합니다.

## 로컬 실행

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py app.py
```

브라우저에서 http://127.0.0.1:5000 을 엽니다. 테스트는 `pytest -q`로 실행합니다.

## GitHub 및 Render 배포

1. GitHub에서 새 저장소를 만들고 이 폴더를 push합니다.
2. GitHub Actions의 `Test Flask app` workflow가 push와 pull request마다 테스트합니다.
3. Render에서 New > Web Service로 GitHub 저장소를 연결하고 `render.yaml`을 선택해 배포합니다. Render는 저장소 push를 감지해 자동 재배포합니다.
4. 공개 URL은 Render 대시보드가 생성한 주소입니다. 이 프로젝트에서는 계정 연결과 실제 배포 권한이 없어 URL을 미리 확정할 수 없습니다.

Steam API는 API 키 없이 현재 접속자 수를 조회하는 공개 엔드포인트를 사용합니다.
