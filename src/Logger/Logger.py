import datetime, os

class Logger():

    def get_time_str(self) -> str:
        return str(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))

    def info(self, message: str):
        message = "<"+self.get_time_str()+"> "+message
        print("\033[34m", message, "\033[0m")
        self.write_to_file(message)

    def success(self, message: str):
        message = "<"+self.get_time_str()+"> "+message
        print("\033[32m", message, "\033[0m")
        self.write_to_file(message)

    def error(self, message: str):
        message = "<"+self.get_time_str()+"> "+message
        print("\033[31m", message, "\033[0m")
        self.write_to_file(message)

    def write_to_file(self, logger_content: str):
        with open(str(os.getenv("ERRORFILE_PATH")), 'a', encoding='utf-8') as f:
            f.write(logger_content,"\n")
