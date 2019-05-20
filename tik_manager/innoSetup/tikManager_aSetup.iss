; -- AllPagesExample.iss --
; Same as Example1.iss, but shows all the wizard pages Setup may potentially display

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!

[Setup]
AppName=My Program
AppVersion=1.5
WizardStyle=modern
DefaultDirName={commonpf}\TikManager
DefaultGroupName=My Program
UninstallDisplayIcon={app}\MyProg.exe
Compression=lzma2
SolidCompression=yes
OutputDir=userdocs:Inno Setup Examples Output

DisableWelcomePage=no
LicenseFile="..\..\LICENSE"
; InfoBeforeFile=readme.txt
; UserInfoPage=yes
; PrivilegesRequired=lowest
DisableDirPage=no
DisableProgramGroupPage=yes
InfoAfterFile="..\..\README.md"

[Files]
Source: "..\__init__.pyc"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\_version.pyc"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\adminPass.psw"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\assetEditorMaya.pyc"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\assetLibrary.pyc"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\ImageViewer.pyc"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\ImMaya.pyc"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\projectMaterials.pyc"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\pyseq.pyc"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\Qt.pyc"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\sceneManagerDefaults.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\sceneManagerUsers.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\seqCopyProgress.pyc"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\setup.exe"; DestDir: "{app}"; Flags: ignoreversion;
Source: "..\test.bat"; DestDir: "{app}"; Flags: ignoreversion; 
Source: "..\Sm3dsMax.pyc"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\SmHoudini.pyc"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\SmMaya.pyc"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\SmNuke.pyc"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\SmRoot.pyc"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\SmUIRoot.pyc"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\softwareDatabase.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\SubmitMayaToDeadlineCustom.mel"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\CSS\darkorange.stylesheet"; DestDir: "{app}\CSS"; Flags: ignoreversion
; Source: "..\bin\*"; DestDir: "{app}"; Flags: ignoreversion createallsubdirs recursesubdirs

[Icons]
Name: "{group}\My Program"; Filename: "{app}\MyProg.exe"

;[Components]
;Name: "Standalone"; Description: "Standalone";
;Name: "Maya"; Description: "Maya";
;Name: "_3dsMax"; Description: "3dsMax";
;Name: "Houdini"; Description: "Houdini";
;Name: "Nuke"; Description: "Nuke";
;Name: "Photoshop"; Description: "Photoshop";

[Tasks]
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

  InputDirWizardPage := CreateInputDirPage(AfterID, 'CreateInputDirPage', 'Select Common Database Folder', 'For single machine setup, this can be the same folder with installation folder.' + #13#13#10 + 'For team work, this should be a common folder where each workstation can reach', False, 'ANewFolderName');
  InputDirWizardPage.Add('&Common Folder:');
  InputDirWizardPage.Values[0] := ExpandConstant('{commonpf}\TikManager');
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



[Run]
Filename: "{app}\test.bat"; Parameters: """-n"" ""{code:GetDataDir}"" {code:GetActiveTasks}";




