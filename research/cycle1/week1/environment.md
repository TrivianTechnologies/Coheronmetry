Coheronmetry Research Environment Record
========================================

Recorded: 2026-09-17
Checked:  2026-09-18

Established from repository documentation
-----------------------------------------
README.md Quick start and .github/workflows/tests.yml:

    python -m pip install -e '.[dev]'
    python -m pytest -q

pyproject.toml:
    requires-python >= 3.10
    runtime dependencies: none
    optional dev: pytest>=7.0, pytest-cov>=4.0

Repository
----------
Name:    coheronmetry 0.2.0
Path:    /Users/orca/Documents/My_Program/Coheronmetry
Remote:  https://github.com/TrivianInstitute/Coheronmetry.git
Branch:  main (up to date with origin/main)
Commit:  7d0144bd225519f9069d7df5e46277853fe62c24
Date:    2026-09-09 23:40:35 -0700
Message: Merge open-source Coheronmetry transition
Tree:    clean (no local patches)

System
------
OS:           macOS 26.3 (Build 25D125)
Kernel:       Darwin 25.3.0
Architecture: arm64
Host:         GarrydeMacBook-Pro.local

Python environment
------------------
Distribution: Anaconda / conda-forge
Python:       3.12.2
Executable:   /opt/anaconda3/bin/python
pip:          24.0

Resolved packages
-----------------
coheronmetry  0.2.0   editable → /Users/orca/Documents/My_Program/Coheronmetry
pytest        8.3.5
pytest-cov    7.1.0
pluggy        1.5.0

Baseline test runs
------------------
Code was not modified. The broader TRIA stack was not tested.

First run, following README / CI:
    python -m pytest -q
    91 passed in 0.08s
    Summary only; full log was not kept.

Second run, to preserve the complete results:
    python -m pytest -v
    91 passed in 0.06s
    Full output: test_results.txt
