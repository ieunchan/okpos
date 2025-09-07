# OKPOS 백오피스 - 백엔드 코딩테스트

## 실행 방법 (로컬)
1) 의존성 설치
   - Python 3.8 권장
   - 가상환경 활성화 후:
   - `pip install -r requirements.txt`

2) 마이그레이션 및 실행
   - `python manage.py migrate`
   - `python manage.py runserver`

3) 접속 URL
   - API: `http://127.0.0.1:8000/shop/`
   - Swagger: `http://127.0.0.1:8000/doc/`

## 실행 방법 (Docker, 단일 컨테이너)
1) 이미지 빌드
   - `docker build -t okpos .`

2) 실행
   - `docker run --rm -p 8000:8000 okpos`
   - 컨테이너 기동 시 자동으로 `python manage.py migrate` 후 gunicorn으로 서비스가 시작됩니다.
   - 접속 URL: `http://127.0.0.1:8000/doc/`

## 테스트 (pytest)
1) 실행
   - `pytest`

## 요구사항 대응
- Django REST Framework: `ModelViewSet` + `WritableNestedModelSerializer` 기반 구현
- Product 생성 시 옵션/태그 중첩 처리, PATCH 시 전체 동기화, GET 시 nested 응답, DELETE 시 옵션만 함께 삭제
- ORM 최적화: `prefetch_related('option_set', 'tag_set')`
- Swagger 문서: `/doc/`
- Dockerfile 제공 및 docker-compose 예시 제공
