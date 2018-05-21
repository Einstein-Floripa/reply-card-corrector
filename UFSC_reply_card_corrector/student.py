class Student:
    def __init__(self, name='', cpf='', answers=dict(), quota='', lang=''):
        self.__name = name
        self.__cpf = str()
        self.__cpf = cpf
        self.__answers = answers
        self.__quota = quota
        self.__lang = lang

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def cpf(self):
        return self.__cpf

    @cpf.setter
    def cpf(self, cpf):
        self.__cpf = cpf

    @property
    def answers(self):
        return self.__answers

    @answers.setter
    def answers(self, answers):
        self.__answers = answers

    @property
    def quota(self):
        return self.__quota

    @quota.setter
    def quota(self, quota):
        self.__quota = quota

    @property
    def lang(self):
        return self.__lang

    @lang.setter
    def lang(self, lang):
        self.__lang = lang
