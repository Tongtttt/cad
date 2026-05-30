Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class Win32Cad {
  public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
  [DllImport("user32.dll", SetLastError=true)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);
}
"@
$rows = New-Object System.Collections.Generic.List[object]
[Win32Cad]::EnumWindows({
  param($h,$l)
  if(-not [Win32Cad]::IsWindowVisible($h)){ return $true }
  $sb = New-Object System.Text.StringBuilder 1024
  [void][Win32Cad]::GetWindowText($h,$sb,$sb.Capacity)
  $title = $sb.ToString()
  if([string]::IsNullOrWhiteSpace($title)){ return $true }
  [uint32]$procId = 0
  [void][Win32Cad]::GetWindowThreadProcessId($h,[ref]$procId)
  $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
  if($proc -and $proc.ProcessName -eq 'acad'){
    $rows.Add([PSCustomObject]@{
      ProcessId = $procId
      WindowTitle = $title
      Hwnd = [int64]$h
      IsAutomationInstance = ($title -eq 'SystemResourceNotifyWindow')
    }) | Out-Null
  }
  return $true
}, [IntPtr]::Zero) | Out-Null
$rows | Sort-Object IsAutomationInstance,ProcessId | ConvertTo-Json -Depth 3
