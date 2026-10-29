@echo off
echo =======================================================
echo Pushing CMNT Codec to https://github.com/knightsura/cmnt-codec
echo Authors: Surafel Wolde and Aziza Jemal
echo =======================================================

cd /d "%~dp0"

git init
git add .
git commit -m "Initial publication of CMNT Codec by Surafel Wolde and Aziza Jemal"
git branch -M main
git remote remove origin 2>nul
git remote add origin https://github.com/knightsura/cmnt-codec.git
git push -u origin main

echo.
echo =======================================================
echo If prompted, sign in via browser to authorize GitHub.
echo =======================================================
pause
