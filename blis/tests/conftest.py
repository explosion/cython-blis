import pytest
from hypothesis import settings

# Functionally disable deadline settings for tests
# to prevent spurious test failures in CI builds.
settings.register_profile("no_deadlines", deadline=2 * 60 * 1000)  # in ms
settings.load_profile("no_deadlines")
