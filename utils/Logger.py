# -*- encoding: UTF-8 -*-
import logbook

logbook.set_datetime_format("local")

# 系统日志
system_log = logbook.Logger("system_log")

# 调试系统日志
info_log = logbook.Logger("info_log")

# 危险日志
warning_log = logbook.Logger("warning_log")
