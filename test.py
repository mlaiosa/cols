import doctest, glob, os, os.path, sys, shlex
import subprocess as S
import cols

from os.path import abspath, dirname, join

test_dir = abspath(join(dirname(__file__), "tests"))

def main():
	# Run the doctests
	fail_count, test_count = doctest.testmod(cols)
	print "Passed %d of %d doctests" % (test_count-fail_count, test_count)
	if fail_count != 0:
		return fail_count
	
	# Run the integration tests
	for fn in os.listdir(test_dir):
		stem = fn[:-3]
		if not fn.endswith(".in"): continue
		sys.stdout.write(stem + " ")
		sys.stdout.flush()
		try:
			args = shlex.split(open(join(test_dir, stem + ".args")).readline())
		except IOError:
			args = []
		p = S.Popen([join(test_dir, "..", "cols")] + args, 
				stdin=open(join(test_dir, fn)), 
				stdout=S.PIPE, stderr=S.PIPE)
		out, err = p.communicate()
		if p.returncode != 0:
			print "failed; returned %d" % (p.returncode,)
			return 1
		if err != "":
			print "failed; output on STDERR" 
			return 1
		with open(join(test_dir, stem + ".out"), "r") as fh:
			if fh.read() != out:
				print "failed; incorrect output on STDOUT"
				return 1
		print "passed"
	return 0


if __name__ == "__main__":
	sys.exit(main())
