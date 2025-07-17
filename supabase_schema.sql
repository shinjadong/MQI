-- CCTV Google Sheets to Supabase 테이블 생성 스크립트
-- 이 스크립트를 Supabase SQL 에디터에서 실행하세요

-- 1. CCTV 관리 데이터 테이블
CREATE TABLE IF NOT EXISTS cctv_management (
    id SERIAL PRIMARY KEY,
    sheet_name TEXT NOT NULL,
    no TEXT,
    entry_date TEXT,
    inquiry_source TEXT,
    channel TEXT,
    region TEXT,
    form_type TEXT,
    consultation_content TEXT,
    consultation_request TEXT,
    phone_number TEXT,
    name TEXT,
    first_call TEXT,
    notes TEXT,
    sync_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 케어온 신청 데이터 테이블
CREATE TABLE IF NOT EXISTS careon_applications (
    id SERIAL PRIMARY KEY,
    application_datetime TEXT,
    name TEXT,
    phone_number TEXT,
    installation_location TEXT,
    address TEXT,
    installation_count TEXT,
    privacy_consent TEXT,
    sync_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 동기화 로그 테이블
CREATE TABLE IF NOT EXISTS sync_log (
    id SERIAL PRIMARY KEY,
    sync_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sheet_name TEXT,
    records_count INTEGER,
    status TEXT,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. 인덱스 생성 (성능 향상)
CREATE INDEX IF NOT EXISTS idx_cctv_management_sheet_name ON cctv_management(sheet_name);
CREATE INDEX IF NOT EXISTS idx_cctv_management_sync_timestamp ON cctv_management(sync_timestamp);
CREATE INDEX IF NOT EXISTS idx_careon_applications_sync_timestamp ON careon_applications(sync_timestamp);
CREATE INDEX IF NOT EXISTS idx_sync_log_sync_timestamp ON sync_log(sync_timestamp);

-- 5. RLS (Row Level Security) 설정 (선택사항)
-- ALTER TABLE cctv_management ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE careon_applications ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE sync_log ENABLE ROW LEVEL SECURITY;

-- 6. 테이블 코멘트
COMMENT ON TABLE cctv_management IS 'CCTV 관리 데이터 (Google Sheets 동기화)';
COMMENT ON TABLE careon_applications IS '케어온 신청 데이터 (Google Sheets 동기화)';
COMMENT ON TABLE sync_log IS '동기화 로그';

-- 7. 컬럼 코멘트
COMMENT ON COLUMN cctv_management.sheet_name IS '시트명';
COMMENT ON COLUMN cctv_management.no IS '번호';
COMMENT ON COLUMN cctv_management.entry_date IS '인입날짜';
COMMENT ON COLUMN cctv_management.inquiry_source IS '문의';
COMMENT ON COLUMN cctv_management.channel IS '채널';
COMMENT ON COLUMN cctv_management.region IS '지역';
COMMENT ON COLUMN cctv_management.form_type IS '형태';
COMMENT ON COLUMN cctv_management.consultation_content IS '상담내용(EA)';
COMMENT ON COLUMN cctv_management.consultation_request IS '상담요청';
COMMENT ON COLUMN cctv_management.phone_number IS '전화번호';
COMMENT ON COLUMN cctv_management.name IS '이름';
COMMENT ON COLUMN cctv_management.first_call IS '1차콜';
COMMENT ON COLUMN cctv_management.notes IS '비고';
COMMENT ON COLUMN cctv_management.sync_timestamp IS '동기화 시간';

COMMENT ON COLUMN careon_applications.application_datetime IS '신청일시';
COMMENT ON COLUMN careon_applications.name IS '이름';
COMMENT ON COLUMN careon_applications.phone_number IS '연락처';
COMMENT ON COLUMN careon_applications.installation_location IS '설치장소';
COMMENT ON COLUMN careon_applications.address IS '주소';
COMMENT ON COLUMN careon_applications.installation_count IS '설치대수';
COMMENT ON COLUMN careon_applications.privacy_consent IS '개인정보동의';
COMMENT ON COLUMN careon_applications.sync_timestamp IS '동기화 시간';

COMMENT ON COLUMN sync_log.sheet_name IS '시트명';
COMMENT ON COLUMN sync_log.records_count IS '레코드 수';
COMMENT ON COLUMN sync_log.status IS '상태 (SUCCESS/ERROR)';
COMMENT ON COLUMN sync_log.error_message IS '오류 메시지';
COMMENT ON COLUMN sync_log.sync_timestamp IS '동기화 시간';