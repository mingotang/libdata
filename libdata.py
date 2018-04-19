# -*- encoding: UTF-8 -*-
# ---------------------------------import------------------------------------
import logging

__i__ = logging.debug


# --------------------------------------------------------


# --------------------------------------------------------


if __name__ == '__main__':
    from utils.Logger import LogInfo, RunTimeCounter, set_logging
    set_logging()
    RunTimeCounter.get_instance()
    # ------------------------------

    # ------------------------------
    __i__(LogInfo.time_passed())
