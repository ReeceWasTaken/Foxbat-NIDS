; Foxbat NIDS - Inno Setup 6/7 installer
; Build Foxbat with build-windows.ps1 first.
#define AppName "Foxbat NIDS"
#include "version.iss"
#define AppPublisher "Foxbat NIDS"
#define AppExeName "Foxbat.exe"

[Setup]
AppId={{E4929BE1-6E4D-4D9C-8AF2-22B74732EFB9}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} v{#AppVersion}
AppPublisher={#AppPublisher}
; A per-user location outside Programs avoids the freeze seen on test machines.
DefaultDirName={localappdata}\Foxbat NIDS
; Do not silently reuse the v0.8.8 install directory during upgrades.
UsePreviousAppDir=no
DefaultGroupName={#AppName}
PrivilegesRequired=lowest
OutputDir=installer-output
OutputBaseFilename=Foxbat-NIDS-Setup-v{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=assets\foxbat.ico
UninstallDisplayIcon={app}\{#AppExeName}
CloseApplications=yes
RestartApplications=no
ArchitecturesAllowed=x64compatible

[Files]
Source: "assets\foxbat.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Foxbat\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Icons]
Name: "{group}\Foxbat NIDS"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\foxbat.ico"
Name: "{group}\Uninstall Foxbat NIDS"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Foxbat NIDS"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\foxbat.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch Foxbat NIDS"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then
    WizardForm.FinishedLabel.Caption :=
      'Foxbat NIDS is installed.' + #13#10 + #13#10 +
      'Live packet capture requires Npcap to be installed separately. ' +
      'Microsoft Edge WebView2 Runtime is also required for the desktop interface.';
end;
