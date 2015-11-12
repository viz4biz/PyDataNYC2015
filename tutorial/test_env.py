"""
test local env
"""

import os

for k, v in os.environ.iteritems():
    print k, '=', v

