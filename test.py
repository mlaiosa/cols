import doctest, glob, os, os.path, sys
import subprocess as S

from os.path import abspath, dirname, join

test_dir = abspath(join(dirname(__file__), "tests"))

def main():
	for fn in os.listdir(test_dir):
		if not fn.endswith(".in"): continue
		sys.stdout.write(fn + " ")
		sys.stdout.flush()
		p = S.Popen([join(test_dir, "..", "cols")], 
				stdin=open(join(test_dir, fn)), 
				stdout=S.PIPE, stderr=S.PIPE)
		out, err = p.communicate()
		if p.returncode != 0:
			print "failed; returned %d" % (p.returncode,)
			return 1
		if err != "":
			print "failed; output on STDERR" 
			return 1
		with open(join(test_dir, fn[:-3] + ".out"), "r") as fh:
			if fh.read() != out:
				print "failed; incorrect output on STDOUT"
				return 1
		print "passed"
	return 0


if __name__ == "__main__":
	sys.exit(main())
