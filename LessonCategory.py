class LessonCategory:
    _data = {
        '公共课': 'H',
        '专业基础课': 'K',
        '专业选修课': 'J',
        '创新创业课': 'M',
        '学术规范与写作课': 'P',
        '学术研讨课': 'L'
    }

    @classmethod
    def get_code(cls, category):
        return cls._data[category]
