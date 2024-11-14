# 可选的体育课名称
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from lesson import Lesson


class Shadow:

    @classmethod
    def can_choice(cls, row_element) -> bool:
        info = Lesson(row_element)
        lesson_name = info.lesson_name
        lesson_time_and_place = info.lesson_time_and_place
        # 只对体育课进行判断
        if '公共体育' not in lesson_name and '非全' not in lesson_name:
            return True
        elif '公共体育' in lesson_name:
            if '星期四' in lesson_time_and_place:
                return False
            else:
                name_list = ['排球', '乒乓球', '羽毛球']
                for name in name_list:
                    if name in lesson_name:
                        return True
                return False
