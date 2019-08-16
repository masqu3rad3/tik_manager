; -- AllPagesExample.iss --
; Same as Example1.iss, but shows all the wizard pages Setup may potentially display

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!

#define appName "Tik Manager"
#define appVersion "3.0.49"

[Setup]
AppName={#appName}
AppVersion={#appVersion}
AppId={{AA2F0401-A42C-40F6-BAB7-62487C4EB248}
WizardStyle=modern
DefaultDirName={commonpf}\TikWorks\tik_manager
DefaultGroupName=Tik Works
UninstallDisplayIcon={app}\MyProg.exe
Compression=lzma2
SolidCompression=yes
OutputBaseFilename=TikManager_v{#appVersion}
OutputDir="..\..\"

DisableWelcomePage=no
LicenseFile="..\..\LICENSE"
; InfoBeforeFile=readme.txt
; UserInfoPage=yes
; PrivilegesRequired=lowest
DisableDirPage=no
DisableProgramGroupPage=yes
InfoAfterFile="..\..\README.md"

[Files]
Source: "..\__init__.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\_version.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\assetEditor3dsMax.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\assetEditorMaya.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\assetEditorHoudini.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\assetLibrary.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\iconsSource.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\ImageViewer.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\ImMaya.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\projectMaterials.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\pyseq.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\Qt.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\seqCopyProgress.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\setup.exe"; DestDir: "{app}"; Flags: ignoreversion;
Source: "..\Sm3dsMax.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\SmHoudini.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\SmMaya.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\SmNuke.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\SmRoot.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\SmUIRoot.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\compatibility.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\CSS\tikManager.qss"; DestDir: "{app}\CSS"; Flags: ignoreversion

Source: "..\icons\*"; DestDir: "{app}\icons"; Flags: ignoreversion createallsubdirs recursesubdirs
Source: "..\coreFunctions\*"; DestDir: "{app}\coreFunctions"; Flags: ignoreversion createallsubdirs recursesubdirs
Source: "..\setupFiles\*"; DestDir: "{app}\setupFiles"; Flags: ignoreversion createallsubdirs recursesubdirs
Source: "..\TikManager_Commons\*"; DestDir: "{app}\TikManager_Commons"; Flags: ignoreversion createallsubdirs recursesubdirs
Source: "..\bin\*"; DestDir: "{app}\bin"; Flags: ignoreversion createallsubdirs recursesubdirs

[Icons]
Name: "{group}\{#appName}"; Filename: "{app}\MyProg.exe"
Name: "{autoprograms}\{#appName}"; Filename: "{app}\bin\SmStandalone.exe"
Name: "{autoprograms}\TikPhotoshop"; Filename: "{app}\bin\SmPhotoshop.exe"
Name: "{autodesktop}\{#appName}"; Filename: "{app}\bin\SmStandalone.exe"; Tasks: desktopicon
Name: "{autodesktop}\TikPhotoshop"; Filename: "{app}\bin\SmPhotoshop.exe"; Tasks: desktopicon

;[Components]
;Name: "Standalone"; Description: "Standalone";
;Name: "Maya"; Description: "Maya";
;Name: "_3dsMax"; Description: "3dsMax";
;Name: "Houdini"; Description: "Houdini";
;Name: "Nuke"; Description: "Nuke";
;Name: "Photoshop"; Description: "Photoshop";

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "Maya"; Description: "Maya"; Flags: checkedonce
Name: "_3dsMax"; Description: "3dsMax"; Flags: checkedonce
Name: "Houdini"; Description: "Houdini"; Flags: checkedonce
Name: "Nuke"; Description: "Nuke"; Flags: checkedonce
Name: "Photoshop"; Description: "Photoshop"; Flags: checkedonce

[Code]
type
  IntegerArray = array [1..10] of integer;
var
  OutputProgressWizardPage: TOutputProgressWizardPage;
  OutputProgressWizardPageAfterID: Integer;
  InputDirWizardPage: TInputDirWizardPage;

procedure InitializeWizard;
var
  //InputQueryWizardPage: TInputQueryWizardPage;
  //InputOptionWizardPage: TInputOptionWizardPage;
  
  //InputFileWizardPage: TInputFileWizardPage;
  //OutputMsgWizardPage: TOutputMsgWizardPage;
  //OutputMsgMemoWizardPage: TOutputMsgMemoWizardPage;
  AfterID: Integer;

  begin

  AfterID := wpSelectTasks;

  InputDirWizardPage := CreateInputDirPage(AfterID, 'Define the path to the COMMON FOLDER', 'Select Common Database Folder', 'For single machine setup, this can be the same folder with installation folder.' + #13#13#10 + 'For team work, this should be a common folder where each workstation can reach', False, 'TikCommons');
  InputDirWizardPage.Add('&Common Folder:');
  InputDirWizardPage.Values[0] := ExpandConstant('{commonpf}\TikWorks\tik_manager\TikManager_Commons');
  AfterID := InputDirWizardPage.ID;

end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  Position, Max: Integer;
begin
  if CurPageID = OutputProgressWizardPageAfterID then begin
    try
      Max := 25;
      for Position := 0 to Max do begin
        OutputProgressWizardPage.SetProgress(Position, Max);
        if Position = 0 then
          OutputProgressWizardPage.Show;
        Sleep(2000 div Max);
      end;
    finally
      OutputProgressWizardPage.Hide;
    end;
  end;
  Result := True;
end;

function GetDataDir(ss: String): String;
begin
    result := InputDirWizardPage.Values[0];
end;

function GetActiveTasks(ss: String): String;
var
  strFlag: String;
begin
  strFlag := ' ';
    if WizardIsTaskSelected('Maya') then
      strFlag := strFlag + 'Maya';
    if WizardIsTaskSelected('_3dsMax') then
      strFlag := strFlag + ' ' + '3dsMax';
    if WizardIsTaskSelected('Houdini') then
      strFlag := strFlag + ' ' + 'Houdini';
    if WizardIsTaskSelected('Nuke') then
      strFlag := strFlag + ' ' + 'Nuke';
    if WizardIsTaskSelected('Photoshop') then
      strFlag := strFlag + ' ' + 'Photoshop';
result := strFlag;
end;

////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////
function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstallString: String;
begin
  sUnInstPath := ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{#emit SetupSetting("AppId")}_is1');
  sUnInstallString := '';
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;


/////////////////////////////////////////////////////////////////////
function IsUpgrade(): Boolean;
begin
  Result := (GetUninstallString() <> '');
end;


/////////////////////////////////////////////////////////////////////
function UnInstallOldVersion(): Integer;
var
  sUnInstallString: String;
  iResultCode: Integer;
begin
// Return Values:
// 1 - uninstall string is empty
// 2 - error executing the UnInstallString
// 3 - successfully executed the UnInstallString

  // default return value
  Result := 0;

  // get the uninstall string of the old app
  sUnInstallString := GetUninstallString();
  if sUnInstallString <> '' then begin
    sUnInstallString := RemoveQuotes(sUnInstallString);
    if Exec(sUnInstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES','', SW_HIDE, ewWaitUntilTerminated, iResultCode) then
      Result := 3
    else
      Result := 2;
  end else
    Result := 1;
end;

/////////////////////////////////////////////////////////////////////
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep=ssInstall) then
  begin
    if (IsUpgrade()) then
    begin
      UnInstallOldVersion();
    end;
  end;
end;


[Run]
Filename: "{app}\setup.exe"; Parameters: """-n"" ""{code:GetDataDir}"" {code:GetActiveTasks}";




