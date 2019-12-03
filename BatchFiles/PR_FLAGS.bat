E:\ArcGISPro\bin\Python\envs\nightly_etl\python.exe E:\LI_PLAN_REVIEW_FLAGS\PyFiles\PR_FLAGS_TABLE.py
if ERRORLEVEL 1 goto Failed
E:\ArcGISPro\bin\Python\envs\nightly_etl\python.exe E:\LI_PLAN_REVIEW_FLAGS\PyFiles\ParcelBaseZoning.py
if ERRORLEVEL 1 goto Failed
E:\ArcGISPro\bin\Python\envs\nightly_etl\python.exe E:\LI_PLAN_REVIEW_FLAGS\PyFiles\ParcelOverlayZoning.py
if ERRORLEVEL 1 goto Failed

E:\ArcGISPro\bin\Python\envs\nightly_etl\python.exe E:\LI_PLAN_REVIEW_FLAGS\PyFiles\CopyToEnterprise.py
if ERRORLEVEL 1 goto Failed

goto Success

:Failed
set EXITCODE=1
:Success
EXIT /B %EXITCODE%