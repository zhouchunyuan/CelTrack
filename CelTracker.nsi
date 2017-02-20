; CelTracker.nsi
;
; It will install CelTracker into the [C:\Program File\CelTracker] directory 
;
;--------------------------------


;--------------------------------

; The name of the installer
Name "Moving object tracker for NIS-Elements"

; The file to write
OutFile "CelTrackerInst.exe"

; The default installation directory
InstallDir "$PROGRAMFILES64\CelTracker"

;--------------------------------

; Pages

Page directory
Page instfiles

;--------------------------------

; The stuff to install
Section "" ;No components page, name is not important

  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  ; Put file there
  FILE /r "build\exe.win-amd64-2.7\*.*"
  
SectionEnd ; end the section