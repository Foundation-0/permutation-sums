.PHONY: verify verify-fast certificates

export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1

verify verify-fast:
	python3 -B verify.py
	python3 -O -B verify.py
	PYTHONPATH=. python3 -O -B -m unittest discover -s tests -p 'test_*.py' -v

certificates:
	python3 -B verify.py --write
