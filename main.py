from lesson import LessonQuery
from spider import LessonSpider

if __name__ == "__main__":
    spider = LessonSpider()
    spider.login()
    spider.to_taget_page()

    lesson1 = LessonQuery('公共课', "公共体育")
    spider.query_lesson(lesson1)

    lesson2 = LessonQuery('公共课', "学术英语写作与交流", school="管理学院")
    spider.query_lesson(lesson2)
    # spider.get_result_csv()
