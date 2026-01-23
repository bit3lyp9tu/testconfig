import sys
import tests.test

if tests.test.add(1,2,3) != 6:
	print('[FAIL] tests.test.add(1,2,3) != 6')
	sys.exit(1)

if tests.test.add(4,5,6) != 15:
	print('[FAIL] tests.test.add(4,5,6) != 15')
	sys.exit(1)

if tests.test.add(-1,1,1) != 1:
	print('[FAIL] tests.test.add(-1,1,1) != 1')
	sys.exit(1)

if tests.test.add(10,-10,5) != 5:
	print('[FAIL] tests.test.add(10,-10,5) != 5')
	sys.exit(1)

if tests.test.add(0.5,0.5,0.5) != 1.5:
	print('[FAIL] tests.test.add(0.5,0.5,0.5) != 1.5')
	sys.exit(1)

if tests.test.add(0.5,-0.5,0.5) != 0.5:
	print('[FAIL] tests.test.add(0.5,-0.5,0.5) != 0.5')
	sys.exit(1)

if tests.test.subtract(10,5) != 5:
	print('[FAIL] tests.test.subtract(10,5) != 5')
	sys.exit(1)

if tests.test.multiply(7,8,9) != 504:
	print('[FAIL] tests.test.multiply(7,8,9) != 504')
	sys.exit(1)

if tests.test.multiply(10,11,12) != 1320:
	print('[FAIL] tests.test.multiply(10,11,12) != 1320')
	sys.exit(1)

if tests.test.multiply(-1,10,1) != -10:
	print('[FAIL] tests.test.multiply(-1,10,1) != -10')
	sys.exit(1)

if tests.test.multiply(0.5,10,-1) != -5.0:
	print('[FAIL] tests.test.multiply(0.5,10,-1) != -5.0')
	sys.exit(1)

