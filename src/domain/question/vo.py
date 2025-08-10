from src.domain.common.vo.string import NonEmptyString


class QuestionText(NonEmptyString):
    min_length = 5
    max_length = 1024
