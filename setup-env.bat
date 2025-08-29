@echo off
REM ======== Setup Conda Environment for HandTracking ========

echo [1/3] Creating conda environment...
conda env create -f environment.yml

echo [2/3] Activating environment...
call conda activate handtracking-env

echo [3/3] Installing Jupyter kernel...
python -m ipykernel install --user --name=handtracking-env --display-name "Python (handtracking-env)"

echo ==========================================================
echo   Environment 'handtracking-env' is ready!
echo   You can activate it with:
echo      conda activate handtracking-env
echo ==========================================================

pause
REM ======== End of setup ========