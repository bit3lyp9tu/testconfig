import sys
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
module_path = ROOT / "tests/code/test.py"

spec = importlib.util.spec_from_file_location("test_module",module_path)
test_module = importlib.util.module_from_spec(spec) # type: ignore
spec.loader.exec_module(test_module) # type: ignore

if test_module.add(1,2,3) != 6:
	print('[FAIL] tests/code/test.py#add(1,2,3) != 6')
	sys.exit(1)

if test_module.add(4,5,6) != 15:
	print('[FAIL] tests/code/test.py#add(4,5,6) != 15')
	sys.exit(1)

if test_module.add(-1,1,1) != 1:
	print('[FAIL] tests/code/test.py#add(-1,1,1) != 1')
	sys.exit(1)

if test_module.add(10,-10,5) != 5:
	print('[FAIL] tests/code/test.py#add(10,-10,5) != 5')
	sys.exit(1)

if test_module.add(0.5,0.5,0.5) != 1.5:
	print('[FAIL] tests/code/test.py#add(0.5,0.5,0.5) != 1.5')
	sys.exit(1)

if test_module.add(0.5,-0.5,0.5) != 0.5:
	print('[FAIL] tests/code/test.py#add(0.5,-0.5,0.5) != 0.5')
	sys.exit(1)

if test_module.subtract(10,5) != 5:
	print('[FAIL] tests/code/test.py#subtract(10,5) != 5')
	sys.exit(1)

if test_module.multiply(7,8,9) != 504:
	print('[FAIL] tests/code/test.py#multiply(7,8,9) != 504')
	sys.exit(1)

if test_module.multiply(10,11,12) != 1320:
	print('[FAIL] tests/code/test.py#multiply(10,11,12) != 1320')
	sys.exit(1)

if test_module.multiply(-1,10,1) != -10:
	print('[FAIL] tests/code/test.py#multiply(-1,10,1) != -10')
	sys.exit(1)

if test_module.multiply(0.5,10,-1) != -5.0:
	print('[FAIL] tests/code/test.py#multiply(0.5,10,-1) != -5.0')
	sys.exit(1)

