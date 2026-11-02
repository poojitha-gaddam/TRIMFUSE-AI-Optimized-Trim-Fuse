@echo off
python -m backend.training.train_models
if errorlevel 1 exit /b 1
echo Model training completed.
