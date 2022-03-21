D:\nightly_etl\python.exe D:\LI_PLAN_REVIEW_FLAGS\PyFiles\PR_FLAGS_TABLE.py
if ERRORLEVEL 1 goto Failed
D:\nightly_etl\python.exe D:\LI_PLAN_REVIEW_FLAGS\PyFiles\ParcelBaseZoning.py
if ERRORLEVEL 1 goto Failed
D:\nightly_etl\python.exe D:\LI_PLAN_REVIEW_FLAGS\PyFiles\ParcelOverlayZoning.py
if ERRORLEVEL 1 goto Failed
D:\nightly_etl\python.exe D:\LI_PLAN_REVIEW_FLAGS\PyFiles\CopyToEnterprise.py
if ERRORLEVEL 1 goto Failed

goto Success

:Failed
set EXITCODE=1
:Success
EXIT /B %EXITCODE%