param(
  [string]$CadCommand = 'CPORTRAIT',
  [int]$SettleMs = 300,
  [switch]$UsePaste,
  [string]$WindowTitleHint = 'AutoCAD'
)

Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class Win32Send {
  public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
  [DllImport("user32.dll", SetLastError=true)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
}
"@
Add-Type -AssemblyName System.Windows.Forms

$target = $null
[Win32Send]::EnumWindows({
  param($h,$l)
  if(-not [Win32Send]::IsWindowVisible($h)){ return $true }
  $sb = New-Object System.Text.StringBuilder 1024
  [void][Win32Send]::GetWindowText($h,$sb,$sb.Capacity)
  $title = $sb.ToString()
  if($title -like "*$WindowTitleHint*"){
    $script:target = $h
    return $false
  }
  return $true
}, [IntPtr]::Zero) | Out-Null

if(-not $target){ throw "Visible AutoCAD window containing '$WindowTitleHint' not found." }

[Win32Send]::ShowWindow($target, 9) | Out-Null
Start-Sleep -Milliseconds 200
[Win32Send]::SetForegroundWindow($target) | Out-Null
Start-Sleep -Milliseconds $SettleMs

[System.Windows.Forms.SendKeys]::SendWait('{ESC}')
Start-Sleep -Milliseconds 120
[System.Windows.Forms.SendKeys]::SendWait('{ESC}')
Start-Sleep -Milliseconds 180

if($UsePaste){
  [System.Windows.Forms.Clipboard]::SetText($CadCommand)
  Start-Sleep -Milliseconds 100
  [System.Windows.Forms.SendKeys]::SendWait('^v')
} else {
  [System.Windows.Forms.SendKeys]::SendWait($CadCommand)
}

Start-Sleep -Milliseconds 120
[System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
Start-Sleep -Milliseconds 180
