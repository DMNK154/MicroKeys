; Inno Setup script for the MicroKeys Windows installer.
; Built by packaging/make_release.ps1, which passes these defines:
;   Version    e.g. 0.1.0
;   StageDir   folder holding MicroKeys.vst3, MicroKeys.exe, "MicroKeys Scales",
;              LICENSE.txt, THIRD_PARTY_NOTICES.txt and "HOW TO INSTALL.txt"
;   OutDir     where the installer is written
;
; Command-line overrides (used for testing without touching the real folders):
;   /VST3DIR=<folder>     instead of C:\Program Files\Common Files\VST3
;   /TUNINGSDIR=<folder>  instead of Documents\MicroKeys Scales

#ifndef Version
  #error Define Version, StageDir and OutDir (see packaging/make_release.ps1)
#endif

[Setup]
AppId={{8C3E0F5A-4B7D-4E21-9A6C-2F1D5B8E7A90}
AppName=MicroKeys
AppVersion={#Version}
AppVerName=MicroKeys {#Version}
AppPublisher=W Ross Warren
AppPublisherURL=https://github.com/DMNK154/MicroKeys
AppSupportURL=https://github.com/DMNK154/MicroKeys/issues
DefaultDirName={autopf}\MicroKeys
DefaultGroupName=MicroKeys
DisableProgramGroupPage=yes
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=commandline
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
InfoBeforeFile={#StageDir}\HOW TO INSTALL.txt
OutputDir={#OutDir}
OutputBaseFilename=MicroKeys-{#Version}-Windows-Setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
UninstallDisplayIcon={app}\MicroKeys.exe
UsedUserAreasWarning=no

[Types]
Name: "full"; Description: "Plugin, standalone app and tunings"
Name: "custom"; Description: "Choose what to install"; Flags: iscustom

[Components]
Name: "vst3"; Description: "VST3 plugin (for FL Studio and other music software)"; Types: full custom
Name: "standalone"; Description: "Standalone app"; Types: full custom
Name: "tunings"; Description: "Tunings (copied to Documents\MicroKeys Scales; existing files are kept)"; Types: full custom

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut for the standalone app"; Components: standalone; Flags: unchecked

[Files]
Source: "{#StageDir}\MicroKeys.vst3\*"; DestDir: "{code:Vst3Dir}\MicroKeys.vst3"; Components: vst3; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "{#StageDir}\MicroKeys.exe"; DestDir: "{app}"; Components: standalone; Flags: ignoreversion
Source: "{#StageDir}\MicroKeys Scales\*"; DestDir: "{code:TuningsDir}"; Components: tunings; Flags: recursesubdirs createallsubdirs onlyifdoesntexist uninsneveruninstall
Source: "{#StageDir}\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#StageDir}\THIRD_PARTY_NOTICES.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#StageDir}\HOW TO INSTALL.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\MicroKeys"; Filename: "{app}\MicroKeys.exe"; Components: standalone
Name: "{group}\How to use MicroKeys"; Filename: "{app}\HOW TO INSTALL.txt"
Name: "{group}\Uninstall MicroKeys"; Filename: "{uninstallexe}"
Name: "{autodesktop}\MicroKeys"; Filename: "{app}\MicroKeys.exe"; Tasks: desktopicon

[Code]
function Vst3Dir(Param: String): String;
begin
  Result := ExpandConstant('{param:VST3DIR|}');
  if Result = '' then
    Result := ExpandConstant('{commoncf64}\VST3');
end;

function TuningsDir(Param: String): String;
begin
  Result := ExpandConstant('{param:TUNINGSDIR|}');
  if Result = '' then
    Result := ExpandConstant('{userdocs}\MicroKeys Scales');
end;
