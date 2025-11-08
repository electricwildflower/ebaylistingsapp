# Requires -Version 5.0
Param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "Starting Ebay Listing App installer..." -ForegroundColor Cyan

function Get-LatestPythonVersion {
    Write-Host "Determining the latest Python 3 release..."
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $response = Invoke-WebRequest -Uri 'https://www.python.org/downloads/windows/' -UseBasicParsing
        $pattern = 'Latest Python 3 Release - Python (?<version>\d+\.\d+\.\d+)'
        $match = [Regex]::Match($response.Content, $pattern)
        if (-not $match.Success) {
            $alternativePattern = 'Python (?<version>\d+\.\d+\.\d+)'
            $match = [Regex]::Match($response.Content, $alternativePattern)
        }
        if (-not $match.Success) {
            throw 'Unable to parse the latest Python version from python.org.'
        }
        $latestVersion = [Version]$match.Groups['version'].Value
        Write-Host "Latest Python version found: $latestVersion"
        return $latestVersion
    }
    catch {
        throw "Failed to determine latest Python version: $($_.Exception.Message)"
    }
}

function Get-InstalledPythonVersion {
    Write-Host "Checking for existing Python installation..."
    try {
        $pythonCmd = Get-Command python.exe -ErrorAction Stop
        $output = & $pythonCmd.Source --version 2>&1
        $versionString = ($output -split ' ')[-1]
        $installedVersion = [Version]$versionString
        Write-Host "Python is installed: version $installedVersion"
        return @{ Path = $pythonCmd.Source; Version = $installedVersion }
    }
    catch {
        Write-Host "Python is not installed."
        return $null
    }
}

function Download-PythonInstaller {
    param(
        [Parameter(Mandatory=$true)][Version]$Version
    )
    $tempFile = Join-Path $env:TEMP "python-$Version-amd64.exe"
    if (Test-Path $tempFile) {
        Write-Host "Using existing downloaded installer at $tempFile"
        return $tempFile
    }
    $downloadUrl = "https://www.python.org/ftp/python/$Version/python-$Version-amd64.exe"
    Write-Host "Downloading Python $Version installer from $downloadUrl ..."
    Invoke-WebRequest -Uri $downloadUrl -OutFile $tempFile -UseBasicParsing
    Write-Host "Download complete: $tempFile"
    return $tempFile
}

function Install-Python {
    param(
        [Parameter(Mandatory=$true)][string]$InstallerPath
    )
    Write-Host "Running Python installer silently..."
    $arguments = @(
        '/quiet',
        'InstallAllUsers=1',
        'PrependPath=1',
        'Include_test=0'
    )
    $process = Start-Process -FilePath $InstallerPath -ArgumentList $arguments -Wait -PassThru
    if ($process.ExitCode -ne 0) {
        throw "Python installer exited with code $($process.ExitCode)"
    }
    Write-Host "Python installation completed successfully." -ForegroundColor Green
}

function Ensure-Python {
    $latestVersion = Get-LatestPythonVersion
    $installedInfo = Get-InstalledPythonVersion
    if ($null -eq $installedInfo) {
        Write-Host "Python needs to be installed."
        $installerPath = Download-PythonInstaller -Version $latestVersion
        Install-Python -InstallerPath $installerPath
        return @{ Version = $latestVersion }
    }
    if ($installedInfo.Version -lt $latestVersion) {
        Write-Host "Python version $($installedInfo.Version) detected, upgrading to $latestVersion."
        $installerPath = Download-PythonInstaller -Version $latestVersion
        Install-Python -InstallerPath $installerPath
        return @{ Version = $latestVersion }
    }
    Write-Host "Python is up to date."
    return $installedInfo
}

function Invoke-PythonCommand {
    param(
        [Parameter(Mandatory=$true)][string]$Arguments,
        [Parameter(Mandatory=$false)][string]$WorkingDirectory
    )
    Write-Host "Running: python $Arguments"
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = 'python'
    $psi.Arguments = $Arguments
    if ($WorkingDirectory) { $psi.WorkingDirectory = $WorkingDirectory }
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    $process.Start() | Out-Null
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()
    if ($stdout) { Write-Host $stdout.Trim() }
    if ($stderr) { Write-Host $stderr.Trim() -ForegroundColor Yellow }
    if ($process.ExitCode -ne 0) {
        throw "Command 'python $Arguments' failed with exit code $($process.ExitCode)"
    }
}

function Ensure-PythonEnvironment {
    param(
        [Parameter(Mandatory=$true)][string]$RequirementsPath
    )
    if (-not (Test-Path $RequirementsPath)) {
        throw "Requirements file not found at $RequirementsPath"
    }
    Invoke-PythonCommand -Arguments '-m pip install --upgrade pip'
    Invoke-PythonCommand -Arguments "-m pip install -r `"$RequirementsPath`""
}

function Ensure-DesktopShortcut {
    param(
        [Parameter(Mandatory=$true)][string]$ShortcutPath,
        [Parameter(Mandatory=$true)][string]$TargetPath,
        [Parameter(Mandatory=$true)][string]$Arguments,
        [Parameter(Mandatory=$true)][string]$WorkingDirectory
    )
    Write-Host "Creating or updating desktop shortcut at $ShortcutPath"
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($ShortcutPath)
    $shortcut.TargetPath = $TargetPath
    $shortcut.Arguments = $Arguments
    $shortcut.WorkingDirectory = $WorkingDirectory
    $shortcut.WindowStyle = 1
    $shortcut.IconLocation = $TargetPath
    $shortcut.Save()
}

try {
    $scriptPath = $MyInvocation.MyCommand.Definition
    if (-not [System.IO.Path]::IsPathRooted($scriptPath)) {
        $scriptPath = (Resolve-Path $scriptPath).Path
    }
    $scriptDir = Split-Path -Parent $scriptPath
    $projectRoot = Split-Path -Parent $scriptDir
    $appDir = Join-Path $projectRoot 'app'
    $requirementsPath = Join-Path $appDir 'requirements.txt'
    $mainPath = Join-Path $appDir 'main.py'

    $pythonInfo = Ensure-Python
    Ensure-PythonEnvironment -RequirementsPath $requirementsPath

    $desktop = [Environment]::GetFolderPath('Desktop')
    if (-not $desktop) {
        throw 'Unable to determine the current user desktop path.'
    }
    $shortcutPath = Join-Path $desktop 'Ebay Listing App.lnk'
    Ensure-DesktopShortcut -ShortcutPath $shortcutPath -TargetPath 'python' -Arguments "`"$mainPath`"" -WorkingDirectory $appDir

    Write-Host "Installation steps completed." -ForegroundColor Green
}
catch {
    Write-Host "Installer failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
