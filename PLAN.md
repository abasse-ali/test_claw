# Budget Manager - Plan

## M1 - Walking Skeleton
Requirements: R1, R7, E7
Verify: python3 -m pytest tests/test_m1.py -v
Status: done

## M2 - Core Budget Features (CRUD + Calculations)
Requirements: R2, R3, R4, R5, R6, R8, R9, R10, R11, E1, E2, E3, E4, E5, E6, E8
Verify: python3 -m pytest tests/test_m2.py -v
Status: done

## M3 - Month Navigation + Export
Requirements: E9, E10
Verify: python3 -m pytest tests/test_m3.py -v
Status: done

## Demo
Install:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Run:
```
python3 demo.py
```