import os
import time
import openpyxl
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 수집할 게시글 개수 설정
repeat_count = 30

# 로그인 정보
username = 인스타그램 아이디
password = 인스타그램 비밀번호

# 엑셀 파일 이름 및 해시태그 설정
# 광고성 리뷰 게시글 설정
csv_filename = "../data/1.raw/광고.xlsx"
hashtags = ["광고", "제품제공", "협찬제품", "협찬리뷰", "협찬", "광고입니다"]

# 일반 리뷰 게시글 설정
#csv_filename = "../data/1.raw/일반.xlsx"
#hashtags = ["내돈내산후기", ["내돈내산", "내돈내산후기", "광고아님", "협찬아님", "찐후기"]


# 크롬 드라이버를 자동으로 업데이트하고 설정
chrome_options = Options()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


# 로그인 함수
def login():
    login_url = 'https://www.instagram.com/'
    driver.get(login_url)
    time.sleep(5)

    # 로그인 폼 찾기
    username_input = driver.find_element('name', 'username')
    password_input = driver.find_element('name', 'password')
    login_button = driver.find_element('css selector', 'button[type="submit"]')

    # 로그인 정보 입력 및 제출
    username_input.send_keys(username)
    password_input.send_keys(password)
    login_button.click()
    time.sleep(7)
    print("로그인이 완료되었습니다.")

# 각 해시태그에 대해 게시글 수집 함수
def scrape_hashtag(hashtag):
    driver.get('https://www.instagram.com/explore/tags/' + hashtag + '/')
    time.sleep(5)  # 페이지 로딩 대기

    # 스크롤 다운하여 게시글 로드
    screen_height = driver.execute_script("return window.screen.height;")
    i = 1
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(6)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == screen_height:
            break
        screen_height = new_height
        i += 1
        if i == 2:
            break

    # 포스트를 저장할 리스트
    post_texts = []
    post_hashtags = []

    # 각 게시물의 텍스트와 해시태그를 가져와서 저장
    posts = driver.find_elements('tag name', 'a')
    print("총 게시글 수", len(posts))
    time.sleep(7)

    # 게시글의 URL 리스트를 저장하여 추적
    post_links = [post.get_attribute('href') for post in posts if '/p/' in post.get_attribute('href')]

    # 각 게시물을 클릭하여 모달을 열고 텍스트와 해시태그를 가져옴
    count = 0
    for href in post_links:
        if count == repeat_count:  # 설정한 게시글 수만큼 수집하면 중단
            break

        driver.get(href)  # 해당 게시글로 이동
        time.sleep(4)  # 페이지 로딩 대기

        try:
            # 주어진 클래스명을 사용하여 게시글 본문 추출
            post_text_element = driver.find_element(
                'css selector',
                'span.x193iq5w.xeuugli.x1fj9vlw.x13faqbe.x1vvkbs.xt0psk2.x1i0vuye.xvs91rp.xo1l8bm.x5n08af.x10wh9bi.x1wdrske.x8viiok.x18hxmgj'
            ).text
            print("ㅡ" * 80)
            print("게시글 텍스트:", post_text_element)

            # 해시태그 필터링: '#'으로 시작하는 것만 추출
            hashtags_in_post = [a.text for a in driver.find_elements('css selector', 'span.x193iq5w a') if
                                a.text.startswith('#')]
            post_hashtags.append(', '.join(hashtags_in_post))
            post_texts.append(post_text_element)
            count += 1
            print(f"현재까지 수집한 게시글 수: {count}/{repeat_count}")
        except Exception as e:
            print("Exception occurred:", e)

        # 다음 게시글로 넘어가기 전에 잠시 대기
        time.sleep(4)

    return post_hashtags, post_texts

# 데이터를 엑셀 파일에 저장 함수
def save_to_excel(post_hashtags, post_texts):
    file_exists = os.path.isfile(csv_filename)
    wb = openpyxl.load_workbook(csv_filename) if file_exists else openpyxl.Workbook()
    sheet = wb.active

    for i in range(len(post_texts)):
        sheet.append([post_hashtags[i], post_texts[i]])

    wb.save(csv_filename)
    print(f"'{csv_filename}' 파일에 데이터가 저장되었습니다.")

# 메인 함수
def main():
    login()  # 로그인 수행
    for hashtag in hashtags:
        post_hashtags, post_texts = scrape_hashtag(hashtag)  # 해시태그로 게시글 텍스트/해시태그 수집
        save_to_excel(post_hashtags, post_texts)

    driver.quit()  # 웹 드라이버 종료

if __name__ == "__main__":
    main()
