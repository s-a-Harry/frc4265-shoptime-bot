"""Checks for the post/skip decision in post_shoptime.py.

Run with:  python3 test_shoptime.py
No dependencies. Prints OK, or raises AssertionError on the first failure.
"""

from datetime import datetime

from post_shoptime import TEAM_TZ, skip_reason


def eastern(year, month, day, hour, minute):
    return datetime(year, month, day, hour, minute, tzinfo=TEAM_TZ)


# 2026-07-17 is a Friday.
FRIDAY_ONTIME = eastern(2026, 7, 17, 8, 30)   # summer 12:30 UTC run, on time
FRIDAY_LATE = eastern(2026, 7, 17, 10, 11)    # the delayed run GitHub actually fired
FRIDAY_SECOND = eastern(2026, 7, 17, 9, 30)   # summer 13:30 UTC run
FRIDAY_EARLY = eastern(2026, 7, 17, 7, 30)    # winter 12:30 UTC run, too early
SATURDAY = eastern(2026, 7, 18, 8, 30)

# The bug this fixes: a Friday run delayed past 8:30 must still post.
assert skip_reason(FRIDAY_LATE, scheduled=True) is None, "delayed Friday run must post"

# On-time, and the daylight-saving second run, also post; main()'s duplicate
# check is what stops the second run from posting twice.
assert skip_reason(FRIDAY_ONTIME, scheduled=True) is None
assert skip_reason(FRIDAY_SECOND, scheduled=True) is None

# Never post before the 8am window, or on the wrong day.
assert skip_reason(FRIDAY_EARLY, scheduled=True) is not None
assert skip_reason(SATURDAY, scheduled=True) is not None

# Manual runs always post, any day or time.
assert skip_reason(SATURDAY, scheduled=False) is None
assert skip_reason(FRIDAY_EARLY, scheduled=False) is None

print("OK: all skip_reason cases pass")
