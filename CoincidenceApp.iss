[Setup]
AppName=CoincidenceApp
AppVersion=1.0
DefaultDirName={pf}\CoincidenceApp
DefaultGroupName=CoincidenceApp
OutputDir=.
OutputBaseFilename=CoincidenceApp_Installer
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\manage.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\buscador\*"; DestDir: "{app}\buscador"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\.env"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{commondesktop}\CoincidenceApp"; Filename: "{app}\manage.exe"
Name: "{group}\CoincidenceApp"; Filename: "{app}\manage.exe"
