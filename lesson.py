import time

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LessonQuery:
    def __init__(self, category: str, query_keyword: str, *,
                 school: str = None, campus: str = None, teacher_name: str = None):
        """
        初始化课程查询对象

        Args:
            category (str): 课程类别
            query_keyword (str): 查询关键字
            school (str, 可选): 学院名称
            campus (str, 可选): 校区名称
            teacher_name (str, 可选): 教师姓名
        """
        self.category = category
        self.query_keyword = query_keyword
        self.school = school
        self.campus = campus
        self.teacher_name = teacher_name

    def __str__(self):
        return f"LessonQuery(category={self.category}, query_keyword={self.query_keyword}, school={self.school}, campus={self.campus}, teacher_name={self.teacher_name})"


class Lesson:
    def __init__(self, *args, **kwargs):
        if args:
            for x in args:
                if isinstance(x, WebElement):
                    self.__from_webElement(x)
        elif kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def __from_webElement(self, element: WebElement):
        # time.sleep(0.01)
        driver = element._parent
        # 等待元素可见
        wait = WebDriverWait(element, 10, poll_frequency=0.01)
        wait.until(EC.visibility_of(element))

        self.lesson_name: str = wait.until(EC.presence_of_element_located((By.XPATH, './td[1]'))).text
        self.school: str = wait.until(EC.presence_of_element_located((By.XPATH, './td[2]'))).text
        self.teacher_name: str = wait.until(EC.presence_of_element_located((By.XPATH, './td[3]'))).text
        self.campus_name: str = wait.until(EC.presence_of_element_located((By.XPATH, './td[4]'))).text
        self.language: str = wait.until(EC.presence_of_element_located((By.XPATH, './td[5]'))).text
        self.credit: float = float(wait.until(EC.presence_of_element_located((By.XPATH, './td[6]'))).text)
        self.lesson_time_and_place: str = wait.until(EC.presence_of_element_located((By.XPATH, './td[7]'))).text
        self.lesson_capacity: str = wait.until(EC.presence_of_element_located((By.XPATH, './td[8]'))).text
        self.free_capacity: int = int(self.lesson_capacity.split('/')[1]) - int(self.lesson_capacity.split('/')[0])

    def __str__(self):
        return f"Lesson(lesson_name={self.lesson_name}, school={self.school}, teacher_name={self.teacher_name}, campus_name={self.campus_name}, language={self.language}, credit={self.credit}, lesson_time_and_place={self.lesson_time_and_place}, lesson_capacity={self.lesson_capacity}, free_capacity={self.free_capacity})"
