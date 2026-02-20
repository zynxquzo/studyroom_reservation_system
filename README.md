# 🏠 대학생 스터디룸 예약 시스템 API

**SookSook**은 대학생들의 효율적인 학습 공간 이용을 위해 설계된 **FastAPI 기반의 스터디룸 예약 관리 백엔드 서비스**입니다. 복잡한 예약 규칙과 데이터 무결성을 보장하며, 사용자 경험과 보안을 동시에 고려한 설계를 지향합니다.

---

## 🛠 Tech Stack

* **Framework**: `FastAPI` (Asynchronous API Support)
* **Database**: `PostgreSQL`
* **Database Driver**: `asyncpg` (Asynchronous Python driver for PostgreSQL)
* **ORM**: `SQLAlchemy 2.0` (`AsyncSession` for non-blocking DB operations)
* **Authentication**: `JWT (JSON Web Token)`, `Passlib(bcrypt)`
* **Dependency Management**: `uv`
* **Environment**: `python-dotenv`

---

## 🏗 Database Structure (ERD)

![ERD](https://github.com/user-attachments/assets/13b0debe-da80-4df2-9fb5-8629181ca830)

데이터 무결성을 위해 `User`, `StudyRoom`, `Reservation`, `Review` 간의 관계를 설계하였으며, 특히 스터디룸과 편의시설 간의 `M:N(다대다)` 관계를 매핑 테이블로 처리했습니다.

---

## ✨ Key Features

### 🔐 User Management

* **Security**: JWT 기반 인증과 `bcrypt` 암호화 알고리즘을 사용한 안전한 회원가입 및 로그인.
* **Privacy**: 사용자 리뷰 조회 시 학번 마스킹(앞 4자리만 노출) 처리로 개인정보 보호.

### 📅 Advanced Reservation System

사용자 편의와 공정한 공간 이용을 위해 **이중 방어 로직**과 **비즈니스 규칙**을 적용했습니다.

* **예약 검증**: 조회와 생성 시점 모두 **7일 이내** 예약만 허용하는 이중 방어 로직.
* **자원 독점 방지**: 사용자별 **하루 최대 2시간(2회)** 예약 제한.
* **시간 제한**: 운영 시간(09:00 - 22:00) 외 예약 차단 및 지난 날짜 예약 원천 차단.
* **취소 정책**: 예약 시작 1시간 전까지만 취소 가능하며, 이미 완료/취소된 건은 재취소 불가.

### ⭐ Review & Rating System

* **신뢰도 보장**: 실제 이용이 완료된 예약(`Status: 이용완료`)에 대해서만 리뷰 작성 가능.
* **실시간 평점**: 리뷰 작성 시 `SQLAlchemy func.avg`를 활용해 스터디룸의 **평균 평점을 즉시 업데이트**.
* **무결성 유지**: 예약 데이터와 리뷰 데이터를 `1:1 Relationship`으로 연결하여 중복 리뷰 방지.

---

## 📖 API Documentation

![API](https://github.com/user-attachments/assets/37e11fd8-889f-431b-9745-84c9b969205a)

모든 API 명세는 Swagger UI를 통해 시각적으로 확인하고 테스트할 수 있습니다.

* **Docs 주소**: `http://localhost:8000/docs`

---

## 🚨 Troubleshooting

### 1. 세션 내 중복 트랜잭션 에러 (`InvalidRequestError`)

* **문제**: 복수의 서비스 로직을 처리하는 과정에서 `with db.begin()`이 중복 호출되어 트랜잭션 충돌 발생.
* **해결**: FastAPI의 의존성 주입(`get_db`) 방식에 맞춰 전역적인 세션 관리와 명시적 `db.commit()` 구조로 리팩토링하여 트랜잭션 원자성 확보.

### 2. 스키마 불일치 에러 (`422 Unprocessable Entity`)

* **문제**: 클라이언트 요청 데이터와 Pydantic 모델 간의 필드명/데이터 타입 불일치.
* **해결**: Swagger UI의 응답 스키마를 기준으로 Pydantic 모델을 재정의하고, 요청 데이터 유효성 검사를 강화하여 해결.

---

## ⚙️ Getting Started

```bash
# 1. 저장소 클론
git clone https://github.com/zynxquzo/studyroom_reservation_system.git
cd studyroom_reservation_system

# 2. 가상환경 설정 및 패키지 설치 (uv 사용 시)
uv sync

# 3. 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 DATABASE_URL과 SECRET_KEY를 설정하세요.

# 4. 서버 실행
uvicorn main:app --reload

```

---

## 🚀 Future Roadmap

* [x] **Asynchronous Support**: `SQLAlchemy AsyncSession` 도입을 통한 성능 최적화.
* [ ] **Frontend Integration**: React/Next.js 기반의 직관적인 예약 대시보드 구현.
* [ ] **Dockerizing**: 배포 편의성을 위한 Docker 컨테이너화.

---

## 📝 Retrospective

관계형 데이터베이스의 복잡한 비즈니스 로직을 다루며 **데이터 무결성**과 **트랜잭션 관리**의 중요성을 깊이 이해하게 된 프로젝트였습니다. 특히 예외 상황을 고려한 이중 방어 로직 설계를 통해 견고한 백엔드 시스템의 필요성을 체감했습니다.


