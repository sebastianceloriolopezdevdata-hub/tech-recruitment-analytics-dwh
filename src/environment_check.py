import sys

import pandas as pd
import great_expectations as gx
from data_profiling import ProfileReport


print("Python executable:", sys.executable)
print("Python version:", sys.version)
print("pandas version:", pd.__version__)
print("GX version:", gx.__version__)
print("Data Profiling import: OK")