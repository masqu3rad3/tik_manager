Set oShell = CreateObject ("Wscript.Shell") 
Dim strArgs
strArgs = "%comspec% /K ""C://Users//kutlu//Documents//maya//scripts//tik_manager//tik_manager//bin//SmPhotoshop.exe"" saveVersion"
oShell.Run strArgs, 0, false