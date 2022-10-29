from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
import os
import time

main_url = "https://sinseo.sen.ms.kr"
login_url = "https://member.newhosting.ssem.or.kr/dggb/mber/mberLogin/mberLogin.do?baseInfo=phIfeH8nb1B4Tlm0NQxemvqm7ow2jMkX8lYM%2FDo1%2BQ0%3D&afterUrl=sinseo.sen.ms.kr"


def read_user_files():
    with open("user/id.txt", "r") as f:
        id = f.read().strip()

    with open("user/pw.txt", "r") as f:
        pw = f.read().strip()
    
    return id, pw


def latest_download_file():
    path = r"C:\Users\goood\Downloads"
    os.chdir(path)
    files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)
    newest = files[-1]

    return newest


def setup():
    try:
        import chromedriver_autoinstaller
    except ImportError:
        subprocess.check_call(["pip3", "install", "chromedriver-autoinstaller"])
        import chromedriver_autoinstaller

    chromedriver_autoinstaller.install(True)
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    driver_path = chromedriver_autoinstaller.get_chrome_version().split(".")[0] + "/chromedriver.exe"
    driver_path = os.path.realpath(driver_path)
    # os.system("cls")
    print(f"드라이버 설치를 완료했어요: {driver_path}")

    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(driver_path, options=options)
    # os.system("cls")
    print("드라이버를 실행했어요")

    return driver


def login(driver):
    driver.get(login_url)
    time.sleep(1)
    id, pw = read_user_files()
    id_input = driver.find_element(By.CSS_SELECTOR, "#userId")
    id_input.send_keys(id)
    time.sleep(0.5)
    pw_input = driver.find_element(By.CSS_SELECTOR, "#password")
    pw_input.send_keys(pw)
    time.sleep(0.5)
    pw_input.send_keys(Keys.RETURN)
    # os.system("cls")
    print(f"{id} 계정으로 로그인을 완료했어요")


def download_file(driver, year, grade, semester, exam_type, subject):
    driver.get("https://sinseo.sen.ms.kr/186943/subMenu.do")
    elements = driver.find_elements(By.TAG_NAME, "a")
    buttons = []

    for element in elements:
        if ("년" not in element.text) or ("학년" not in element.text):
            elements.remove(element)
            continue
        if element.get_attribute("href") == "javascript:void(0);":
            elements.remove(element)
            continue
        if element.text == "":
            elements.remove(element)
            continue
        element = {"text": element.text, "href": element.get_attribute("href")}
        buttons.append(element)

    for element in buttons:
        text = element["text"]
        if text == f"{year}년 {grade}학년":
            driver.get(element["href"])
            # os.system("cls")
            print(f"{year}년 {grade}학년 페이지로 이동했어요")
            break

    page_buttons = driver.find_elements(By.TAG_NAME, "a")
    for page_button in page_buttons:
        try:
            if not "fnPage" in page_button.get_attribute("onclick"):
                page_buttons.remove(page_button)
                continue
        except:
            pass
        
    for page_button in page_buttons:
        time.sleep(0.5)
        page_button.click()
        time.sleep(0.5)
        notices = driver.find_elements(By.CLASS_NAME, "samu")
        for notice in notices:
            notice_text = notice.text.strip()
            if semester+"학기" in notice_text and exam_type+"고사" in notice_text and subject in notice_text:
                if subject == "국어" and "중국어" in notice_text:
                    continue
                notice.click()
                time.sleep(0.5)
                # os.system("cls")
                print("파일을 찾았어요")

    teacher_name = driver.find_element(By.CSS_SELECTOR, "#board_area > table > tbody > tr:nth-child(1) > td:nth-child(2) > div").text.strip()
    file_extension = driver.find_element(By.CSS_SELECTOR, "#fileListTable > tbody > tr:nth-child(1) > td:nth-child(3)").text.strip().lower()
    file_name = f"{year}년 {grade}학년 {semester}학기 {exam_type}고사 {subject}과 {teacher_name}T.{file_extension}"
    download_button = driver.find_element(By.CSS_SELECTOR, "#fileListTable > tbody > tr:nth-child(1) > td:nth-child(5) > a")
    download_button.click()
    time.sleep(0.5)

    fileends = "crdownload"
    while "crdownload" == fileends:
        time.sleep(0.1)
        newest_file = latest_download_file()
        if "crdownload" in newest_file:
            fileends = "crdownload"
        else:
            os.rename(newest_file, file_name)

    # os.system("cls")
    print(f"{file_name} 파일을 다운로드했어요")


if __name__ == "__main__":
    driver = setup()
    driver.get(main_url)
    # os.system("cls")
    print(f"{main_url} 홈페이지에 접속했어요")
    login(driver)
    # os.system("cls")
    year = input("년도를 입력해주세요 >>> ")
    grade = input("학년을 입력해주세요 >>> ")
    semester = input("학기를 입력해주세요 >>> ")
    exam_type = input("고사 종류를 입력해주세요 >>> ")
    subject = input("과목을 입력해주세요 >>> ")
    download_file(driver, year, grade, semester, exam_type, subject)
    driver.quit()
