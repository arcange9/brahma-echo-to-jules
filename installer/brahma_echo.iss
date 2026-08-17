; Brahma Echo — Inno Setup Installer Script
; Produces: Brahma-Echo-Setup.exe
; Compatible with Windows 10/11 x64
;
; This installer:
;   - Installs the Brahma Echo application to a user-selected directory
;   - Creates Start Menu and Desktop shortcuts
;   - Provides a complete uninstaller
;   - Preserves user config/data on uninstall
;   - Optionally runs Playwright browser setup

#define MyAppName "Brahma Echo"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Brahma Echo"
#define MyAppURL "https://github.com/arcange9/brahma-echo-to-jules"
#define MyAppExeName "BrahmaEcho.exe"
#define MyAppExeDebugName "BrahmaEchoDebug.exe"

[Setup]
AppId={{B5A7C3E2-1D4F-4A6B-9C8E-7F3D2A1B5C6E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\Brahma Echo
DefaultGroupName=Brahma Echo
AllowNoIcons=yes
OutputDir=output
OutputBaseFilename=Brahma-Echo-Setup
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
DisableDirPage=no
DisableProgramGroupPage=no
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName=Brahma Echo
SetupIconFile=..\assets\Brahma_Lite_Logo.ico
VersionInfoName=Brahma Echo
VersionInfoProductName=Brahma Echo
VersionInfoCompany=Brahma Echo
VersionInfoDescription=Brahma Echo - Windows Desktop AI Assistant
VersionInfoTextVersion=1.0.0
VersionInfoVersion=1.0.0.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional shortcuts:"
Name: "startupicon"; Description: "Start with &Windows"; GroupDescription: "Additional shortcuts:"; Flags: unchecked
Name: "playwright"; Description: "Download Playwright Chromium browser (for browser automation)"; GroupDescription: "Additional components:"

[Files]
; Main application directory (PyInstaller onedir output)
Source: "..\dist\BrahmaEcho\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Config templates (read-only, used to initialize user config on first run)
Source: "..\config\templates\*"; DestDir: "{app}\config\templates"; Flags: ignoreversion

; Bundled read-only config
Source: "..\config\brahma_connect.json"; DestDir: "{app}\config"; Flags: ignoreversion
Source: "..\config\models\*"; DestDir: "{app}\config\models"; Flags: ignoreversion recursesubdirs

; Assets
Source: "..\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs

; Core files
Source: "..\core\*"; DestDir: "{app}\core"; Flags: ignoreversion recursesubdirs

; Playwright setup script
Source: "..\installer\playwright_setup.ps1"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Brahma Echo"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\Brahma_Lite_Logo.ico"
Name: "{group}\Brahma Echo (Debug Mode)"; Filename: "{app}\{#MyAppExeDebugName}"; IconFilename: "{app}\assets\Brahma_Lite_Logo.ico"; Check: FileExists(ExpandConstant('{app}\{#MyAppExeDebugName}'))
Name: "{group}\Uninstall Brahma Echo"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Brahma Echo"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\Brahma_Lite_Logo.ico"; Tasks: desktopicon
Name: "{userstartup}\Brahma Echo"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\Brahma_Lite_Logo.ico"; Tasks: startupicon

[Run]
; Optionally download Playwright Chromium
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\playwright_setup.ps1"""; Flags: waituntilterminated postinstall; Tasks: playwright; StatusMsg: "Setting up Playwright browser..."

; Launch Brahma Echo after installation
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Brahma Echo now"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Delete logs on uninstall
Type: filesandordirs; Name: "{localappdata}\Brahma Echo\logs"
; Note: We do NOT delete the user's config, memory, or workspace data on uninstall.
; User data lives in %LOCALAPPDATA%\Brahma Echo\ and persists after uninstall.

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
