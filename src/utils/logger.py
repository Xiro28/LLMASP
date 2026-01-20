class Logger:
    console_print: bool = False
    _log_storage: list[str] = []

    @staticmethod
    def log(message: str) -> None:
        if Logger.console_print:
            print(f"[LOG] {message}")
        Logger._log_storage.append(message)

    @staticmethod
    def error(message: str) -> None:
        if Logger.console_print:
            print(f"[ERROR] {message}")
        Logger._log_storage.append(message)

    @staticmethod
    def debug(message: str) -> None:
        if Logger.console_print:
            print(f"[DEBUG] {message}")
        Logger._log_storage.append(message)

    @staticmethod
    def get_logs() -> list[str]:
        return Logger._log_storage
    
    @staticmethod
    def clear_logs() -> None:
        Logger._log_storage = []

    @staticmethod
    def enable_console_logging() -> None:
        Logger.console_print = True