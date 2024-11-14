import re
import time

import pandas as pd
import yaml
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from lesson import LessonQuery, Lesson
from shadow import Shadow
from user import User


class LessonSpider:
    def __init__(self):
        self.driver = self.initialize()
        self.wait = WebDriverWait(self.driver, 10, poll_frequency=0.001)
        with open('config.yaml', 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        self.N: int = config['maxQuery']  # 最大查询次数
        self.batch = config['batch']  # 选课批次，用于导出结果

    def initialize(self, options=None):
        if options is None:
            options = webdriver.ChromeOptions()
            # 无痕模式
            options.add_argument('--incognito')

            # 设置User-Agent为常见浏览器的User-Agent
            options.add_argument(
                'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36')

            # 禁用webdriver特征
            options.add_argument("--disable-blink-features=AutomationControlled")

            # 防止WebDriver被检测
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            # 隐藏WebDriver痕迹
            options.add_argument("--disable-extensions")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            # options.add_argument("--headless")

            driver = webdriver.Chrome(options=options)
            # 执行以下脚本，进一步隐藏自动化痕迹
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        else:
            driver = webdriver.Chrome()

        return driver

    def login(self):

        self.driver.get("https://yjsxk.shu.edu.cn/yjsxkapp/sys/xsxkapp/*default/index.do")
        self.driver.find_element(by=By.ID, value='username').send_keys(User.username)
        self.driver.find_element(by=By.ID, value='password').send_keys(User.password)
        self.driver.find_element(by=By.ID, value='submit-button').click()
        # 最多等待10秒，直到courseBtn元素出现
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "courseBtn")))
            print("登录成功")
        except:
            print("登录失败")

    def has_element(self, by, value):
        try:
            self.driver.find_element(by=by, value=value)
            return True
        except NoSuchElementException:
            return False

    def to_taget_page(self):
        while True:
            element = self.wait.until(EC.presence_of_element_located((By.ID, "courseBtn")))
            if 'disabled' in element.get_attribute('class') or element.get_attribute('disabled') == 'disabled':
                print("刷新页面")
                self.driver.refresh()
                time.sleep(0.08)
            else:
                print("进入选课页面")

                element.click()
                # 等待页面加载完成
                student_info = self.wait.until(lambda driver: driver.find_element(By.ID, 'xsInfoDiv').text)
                print(student_info)
                break

    def get_total_page(self):
        if self.has_element(By.XPATH, "//td[text()='没有数据显示！']"):
            return 0
        else:
            element = self.driver.find_element(By.CLASS_NAME, 'zero-grid-pagination-des')
            text = self.wait.until(EC.visibility_of(element)).text
            # 使用正则表达式匹配"分X页"的部分，捕获X
            match = re.search(r"分(\d+)页", text)
            if match:
                return int(match.group(1))
            else:
                return -1

    def get_total_item_num(self):

        if self.has_element(By.XPATH, "//td[text()='没有数据显示！']"):
            return 0
        else:
            text = self.driver.find_element(By.CLASS_NAME, 'zero-grid-pagination-des').text
            # 使用正则表达式匹配"分X页"的部分，捕获X
            match = re.search(r"共(\d+)条数据", text)
            if match:
                return int(match.group(1))
            else:
                return -1

    def get_page_length(self, total_item_num: int, page_index: int, page_size: int = 10):
        if total_item_num == 0:
            return 0
        elif total_item_num <= page_size:
            return total_item_num
        elif total_item_num % page_size == 0:
            return page_size
        elif page_index == total_item_num // page_size + 1:
            return total_item_num % page_size
        else:
            return page_size

    def query_lesson(self, lesson_query: LessonQuery):
        print(lesson_query)
        self.driver.refresh()
        category_xpath_expression = f"//li[normalize-space(text())='{lesson_query.category}']"
        self.wait.until(EC.presence_of_element_located((By.XPATH, category_xpath_expression))).click()

        self.wait.until(EC.element_to_be_clickable((By.NAME, 'query_keyword'))).send_keys(
            lesson_query.query_keyword)

        # 开课学院
        if lesson_query.school:
            school_select = Select(self.driver.find_element(By.NAME, 'query_kkyx'))
            school_select.select_by_visible_text(lesson_query.school)
        # 上课校区
        if lesson_query.campus:
            campus_select = Select(self.driver.find_element(By.NAME, 'query_xqdm'))
            campus_select.select_by_visible_text(lesson_query.campus)
        # 不冲突
        conflict_select = Select(self.driver.find_element(By.NAME, 'query_sfct'))
        conflict_select.select_by_visible_text('不冲突')
        # 可选的
        sfym = Select(self.driver.find_element(By.NAME, 'query_sfym'))
        sfym.select_by_visible_text('未满')

        query_button_expression = "//input[@value='查询']"
        query_button = self.driver.find_element(By.XPATH, query_button_expression)

        for n in range(1, 1 + self.N):
            query_button.click()
            # time.sleep(0.2)
            # 等待页面加载完成，ui_grid_loading不可见
            self.wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'ui_grid_loading')))
            total_page = self.get_total_page()
            total_item_num = self.get_total_item_num()
            if total_page == 0:
                print(f"第{n}次查询无结果")
                continue
            else:
                print(f"第{n}次查询结果共{total_page}页")
                for page in range(1, total_page + 1):
                    # time.sleep(0.2)
                    self.wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'ui_grid_loading')))
                    is_success = self.parse_page(self.get_page_length(total_item_num, page))
                    if is_success:
                        return is_success
                    if page != total_page:
                        next_page_button = self.driver.find_element(By.XPATH, "//a[@title='Go下一页']")
                        next_page_button.click()
        return False

    def parse_page(self, page_length: int = 10):
        for row in range(1, page_length + 1):
            lesson_name_xpath = f"//table/tbody/tr[{row}]/td[1]"
            row_xpath = f"//table/tbody/tr[{row}]"

            if self.has_element(By.XPATH, row_xpath):
                # row_element = self.driver.find_element(By.XPATH, row_xpath)
                row_element = self.wait.until(EC.visibility_of_element_located((By.XPATH, row_xpath)))
                # 能选，则选
                if Shadow.can_choice(row_element):
                    is_success = self.submit(row_element)
                    if is_success:
                        lesson_name = row_element.find_element(By.XPATH, './td[1]').text
                        print(f"选课成功：{lesson_name}")
                        return True
        return False

    def submit(self, row_element: WebElement):
        # select_button = row_element.find_element(By.XPATH, ".//a[text()='选课']")
        select_button = WebDriverWait(row_element, 10, poll_frequency=0.001).until(
            EC.element_to_be_clickable((By.XPATH, ".//a[text()='选课']")))
        lesson_name = row_element.find_element(By.XPATH, './td[1]').text
        lesson_time = row_element.find_element(By.XPATH, './td[7]').text

        select_button.click()

        while True:
            time.sleep(0.01)
            if self.has_element(By.XPATH, '//div[@zero-unique-container]'):
                window1 = self.wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//div[@zero-unique-container]')))

                state = window1.find_element(By.CLASS_NAME, 'zeromodal-title1').text
                state_message = window1.find_element(By.CLASS_NAME, 'zeromodal-title2').text
                window1.find_element(By.XPATH, './/button[text()="确定"]').click()
                lesson_time = row_element.find_element(By.XPATH, './td[7]').text
                print(lesson_name, lesson_time, state)
                print(state_message)
                if '成功' in state:
                    return True
                elif '失败' in state:
                    return False
                elif '确定要选择吗？' in state:
                    pass
            else:
                return True

    def get_info(self, row_element: WebElement):
        row = []
        td1 = row_element.find_element(By.XPATH, './td[1]').text
        if td1 != self.batch:
            return None
        td2 = row_element.find_element(By.XPATH, './td[2]').text
        lesson_name = td2.split('（')[0].split('-')[1]
        teacher_name = row_element.find_element(By.XPATH, './td[5]').text
        lesson_campus = row_element.find_element(By.XPATH, './td[4]').text
        lesson_time_and_classroom = row_element.find_element(By.XPATH, './td[9]').text
        if lesson_time_and_classroom:
            # 匹配字段 1-10周 星期四[5-8节]2-201
            match = re.search(r"(\d+-\d+周) (\S+?)\[(\d+-\d+节)\](.*)", lesson_time_and_classroom)
            if match:
                week, weekday, time_block, classroom = match.groups()
                day_to_num = {'星期一': 1, '星期二': 2, '星期三': 3, '星期四': 4, '星期五': 5, '星期六': 6,
                              '星期日': 7}
                row.append(lesson_name)
                row.append(day_to_num[weekday])
                start, end = time_block.split('-')
                row.append(int(start))
                row.append(int(end[:-1]))
                row.append(teacher_name)
                row.append(lesson_campus + ':' + classroom)
                row.append(week[:-1])
        return row

    def get_result_csv(self):
        element = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@role-title="已选课程"]')))
        element.click()
        self.wait.until(
            EC.invisibility_of_element_located((By.XPATH, '//*[@id="yjsxkjgGrid"]/div[@class="ui_grid_loading"]')))
        text = self.wait.until(EC.visibility_of_element_located(
            (By.XPATH, '//div[@id="yjsxkjgGrid"]//div[@class="zero-grid-pagination-des"]'))).text
        total_page = int(re.search(r"分(\d+)页", text).group(1))
        total_item_num = int(re.search(r"共(\d+)条数据", text).group(1))

        data = []

        for page_id in range(1, total_page + 1):
            row_xpath_str = '//*[@id="yjsxkjgGrid"]/table/tbody/tr'
            row_elements = self.driver.find_elements(By.XPATH, row_xpath_str)
            for row_element in row_elements:
                row = self.get_info(row_element)
                if row:
                    data.append(row)
            if page_id != total_page:
                next_page_button = self.driver.find_element(By.XPATH,
                                                            '//div[@id="yjsxkjgGrid"]//*[@title="Go下一页"]')
                next_page_button.click()

        df = pd.DataFrame(columns=['课程名称', '星期', '开始节数', '结束节数', '老师', '地点', '周数'], data=data)
        df.to_csv('result.csv', index=False, encoding='utf-8')
        print(df)
