# This batch file is to run this on windows and tunnel it to ngrok for public access if you want 
@ECHO OFF
#start C:\Program Files\ngrok\ngrok.exe http --domain=foxhound-immune-rattler.ngrok-free.app 8501
#@ECHO DONE ngrok process enter to proceed
#pause
set root=C:\Users\tomar\Documents\Work\Projects\VulnerabilityR\VulnR
call %root%\Scripts\activate.bat
cd C:\Users\tomar\Documents\Work\Projects\VulnerabilityR
@ECHO HELLO
call streamlit run main.py --server.headless true
pause