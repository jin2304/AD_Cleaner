import pandas as pd
import re
import emoji
import MeCab

# MeCab 설정
mecab = MeCab.Tagger("-d C:/mecab/mecab-ko-dic")

# 한국어 불용어 리스트
korean_stopwords = [
    '의', '가', '이', '은', '는', '들', '에', '와', '한', '하다', '것', '그', '되', '수', '아니', '같', '그렇', '위하', '말', '일',
    '때', '있', '하', '보', '않', '없', '감', '편', '좋', '아요', '번', '트', '게다가', '나', '사람', '주', '등', '년', '지', '로',
    '대하', '오', '그리고', '그래서', '크', 'ketohye', '에요', '차', '얼', '핑', '이제', '중', '에서', '넬로', '잘', '고', '을',
    '으로', '게', '를', '도', '다', '어', '기', '해', '후', '많', '다고', '링', '네요', '으면', 't', '아', '면', '니', '는데',
    '었', '과', '더', '시', '내산', '팔', '개', '문', '입니다', '백', '맛', '음', '노티', '마', '스타', '먹', '인', '만', '까지',
    '입', '할', '빗', '데', '다가', '천', '점', '넘', '명', '랑', '이나', '외', '아서', '덕스', '았', '습니다', '거', '세요',
    '적', '했', '님', '라', '어서', '봤', '맘', '용', '희', '맥', '함', '여름', '분', '안', '해요', '지만', '스', '신', '제',
    '집', '던', '용쓰', '네', '성', '받', '면서', '원', '아기', '해서', '아이', '저', '서', '살', '로워', '덕', '맞', '요',
    '겠', '싶', '타', '쓰', '어요', '반', '두', '자', '세', '죠', '내', '사', '플', '였', '에게', '께', '부터', '니까', '셨',
    '났', '인데', '으니', '된', '엔', '그런', '왔', '늘', '며', '스럽', '듯', '해야', '라고', '예요', '동안', '처럼', '은데',
    '더니', '다는', '한다', '는데요', '써', '다면', '나와', '쌈닭', '홀딱', '반한', '치킨', '편하', '강아지', '닭', '볼',
    '램', '룩', '사이', '블랙', '전', '티', '템', '애', '싸', '믿', '밀', '셀', '럽', '구', '선', '뭐', '쉽', '나왔', '영',
    '무', '덤', 'fff', '롬', '먹스', '셔', '쿠', '쥬', '든', '틱', '셔서', '피', '올', '첫', '네', '베', '킨', '베스', '니깐',
    '라베라', '시연', '룬', 'mlbb', 'nail', 'getregrammer', '권', '따', 's', '따', '재', '커리', '쉴', 'ROCFIT', '여', '엠',
    '왕', '칭', 'h', 'k', '수노', '베베', '무아애', 'cm', 'CM', '화', '브', 'mlbb', '노연', '용하', 'd', 'bitly',
    'huggieshappyhug', '제니', '옐로', '소희', '마시', '로토토', '얇', '노즈', 'MLBB', 'mlbb', 'midowatches',
    'ndmvopt', '헤', '율', '느냐', 'ssoh', 'm', '피너클', '텐', '웨', '피펫', '퐁', 'jieun', '리', '타월', '꿍', '밀키', '히피'
]


# 텍스트 전처리 함수 (이모지 및 특수문자 제거)
def preprocess_text(text):
    if isinstance(text, str):
        text = emoji.replace_emoji(text, replace='')  # 이모지 제거
        text = re.sub(r'[^가-힣0-9a-zA-Z%*\s]', '', text)  # 특수문자 제거
        text = re.sub(r'[\n\r]+', ' ', text).strip()  # 줄바꿈 및 공백 제거
        return text
    return ""

# 토큰 분리 함수
def split_custom_tokens(text):
    url_keywords = ["https", "http", "ftp", "www", "com"]
    url_pattern = r"(" + "|".join(url_keywords) + r")"
    text = re.sub(url_pattern, r" \1 ", text)

    korean_keywords = ["프로필", "링크", "협찬", "이벤트", "문의", "오픈", "가성비", "카톡", "공유"]
    korean_pattern = r"(" + "|".join(korean_keywords) + r")"
    text = re.sub(korean_pattern, r" \1 ", text)

    english_keywords = ["official", "repost", "010", "02", "055", "031", "000", "00",]
    english_pattern = r"(" + "|".join(english_keywords) + r")"
    text = re.sub(english_pattern, r" \1 ", text)

    text = re.sub(r"\s+", " ", text).strip()
    return text

# 토큰화 함수 (URL 분리 포함)
def tokenize_text(text):
    if isinstance(text, str):
        text = split_custom_tokens(text)
        text = re.sub(r'[\n\r]+', ' ', text).strip()
        tokens = mecab.parse(text).splitlines()[:-1]
        return [token.split('\t')[0] for token in tokens if token.split('\t')[0] not in korean_stopwords]
    return text

# 데이터 로드 및 전처리
def process_file(input_path, output_path):
    try:
        # 파일 로드
        data = pd.read_excel(input_path)
        if 'post_texts' not in data.columns:
            print("'post_texts' 열이 데이터에 없습니다. 확인해주세요.")
            return

        # 원본 텍스트 보존 및 전처리
        data['original_text'] = data['post_texts']  # 원본 텍스트 보존
        data['preprocessed_text'] = data['post_texts'].apply(preprocess_text)  # 전처리
        data['tokenized_text'] = data['preprocessed_text'].apply(tokenize_text)  # 토큰화

        # 파일 저장
        data.to_excel(output_path, index=False)
        print(f"전처리가 완료되었습니다. 결과가 '{output_path}'에 저장되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")

# 실행 예제
ad_input_file = 'data/4.통합/광고_통합.xlsx'  # 광고 데이터 입력 파일 경로
non_ad_input_file = 'data/4.통합/일반_통합.xlsx'  # 일반 데이터 입력 파일 경로

ad_output_file = 'data/5.전처리/광고_전처리.xlsx'  # 광고 데이터 출력 파일 경로
non_ad_output_file = 'data/5.전처리/일반_전처리.xlsx'  # 일반 데이터 출력 파일 경로

# 광고 데이터 처리
process_file(ad_input_file, ad_output_file)

# 일반 데이터 처리
process_file(non_ad_input_file, non_ad_output_file)