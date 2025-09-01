@echo off
for /l %%x in (1, 1, 3) do (
    start cmd /k "python gencek7.py"
)