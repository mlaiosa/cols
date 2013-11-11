import doctest, glob, os, os.path, sys, shlex, re
import subprocess as S
import cols

import coverage

from os.path import abspath, dirname, join

test_dir = abspath(join(dirname(__file__), "tests"))

class Test(object):
	def __init__(self, path, test):
		self.test = test
		self.stem = os.path.join(path, test)

	def get_args(self):
		try:
			return shlex.split(open(self.stem + ".args").readline())
		except IOError:
			return []
	
	def get_stdin_stream(self):
		return open(self.stem + ".in")

	def get_stdout(self):
		with open(self.stem + ".out") as fh:
			return fh.read()

	def get_returncode(self):
		try:
			with open(self.stem + ".ret", "r") as fh:
				return int(fh.read())
		except IOError:
			return 0

	__key_re = re.compile("([0-9]+)")
	def __key__(self):
		def convert(s):
			try:
				return long(s,0)
			except ValueError:
				return s
		return [convert(s) for s in self.__key_re.split(self.stem)]

	def __cmp__(self, other):
		assert isinstance(other, Test)
		return cmp(self.__key__(), other.__key__())

def list_tests(directory):
	for fn in os.listdir(directory):
		if fn.endswith(".in"):
			yield Test(directory, fn[:-3])

def main():
	C = coverage.coverage()
	C.erase()

	# Run the doctests
	C.start()
	fail_count, test_count = doctest.testmod(cols)
	C.stop()
	C.save()
	print "Passed %d of %d doctests" % (test_count-fail_count, test_count)
	if fail_count != 0:
		return fail_count
	
	# Run the integration tests
	for test in sorted(list_tests(test_dir)):
		sys.stdout.write(test.test + " ")
		sys.stdout.flush()
		p = S.Popen([sys.executable, '-m', 'coverage.__main__', 'run', '--append',
			    join(test_dir, "..", "cols")] + test.get_args(), 
				stdin=test.get_stdin_stream(), 
				stdout=S.PIPE, stderr=S.PIPE)
		out, err = p.communicate()
		if p.returncode != test.get_returncode():
			print "failed; returned %d" % (p.returncode,)
			return 1
		if err != "":
			print "failed; output on STDERR" 
			return 1
		if out != test.get_stdout():
			print "failed; incorrect output on STDOUT"
			return 1
		print "passed"

	# Check coverage
	print "Checking coverage",
	C.load()
	_, _, _, missing_lines, missing_lines_str = C.analysis2(cols)
	if len(missing_lines) != 0:
		print "- failed; cols line(s) not covered: %s" % missing_lines_str
		return 1
	else:
		print "- 100%"


	return 0


if __name__ == "__main__":
	sys.exit(main())
