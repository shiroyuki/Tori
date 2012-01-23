''' App bootstrap '''

import os
import sys

app_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.append(app_path)