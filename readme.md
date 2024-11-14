# SHU 研究生选课脚本

## Requirements

- Python 3.9+
- pandas
- selenium
- pyyaml

以及 Google Chrome 浏览器

## Usage

1. 安装依赖

2. 修改 `config.yaml` 文件，填入自己的学号、密码、选课信息

> 您可能需要自行复制一份 `config.yaml.template` 文件，并将其命名为 `config.yaml`

3. 编辑 `shadow.py` 文件，设置您自己的规则

4. 编辑 `main.py` 文件，设置您需要选的课程

```python
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
```

当前代码中，我们选择了两门课程，分别是**公共体育**和**学术英语写作与交流**。
关于`LessonQuery`类的参数，您可以参考`lesson.py`文件中的注释。

5. 运行 `main.py` 文件

```shell
python main.py
```