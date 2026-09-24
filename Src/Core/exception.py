class arguments_exception(Exception):
    __stack_trace: str = ""
    __message: str = ""
    __field: str = ""

    def __init__(self, field, message = "", stack_trace = ""):
        self.__field = field.strip()
        self.__message = message.strip()
        self.__stack_trace = message.strip()

    def __str__(self):
        return  f"Ошибка. Некореректный аргумент!\n {self.__message}\n {self.__stack_trace}"
