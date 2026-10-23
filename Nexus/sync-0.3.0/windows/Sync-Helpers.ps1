function Get-StreamHash($Stream) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash($Stream))).Replace('-', '').ToLowerInvariant() }
    finally { $sha.Dispose() }
}

function New-StableSnapshot {
    param([string]$Source, [string]$Destination, [int]$QuietSeconds = 15, [int]$SampleSeconds = 10)
    $info = Get-Item -LiteralPath $Source
    if ($info.Length -le 0 -or $info.Length -gt 64MB) { throw 'Source is empty or exceeds 64 MiB.' }
    if (([DateTime]::UtcNow - $info.LastWriteTimeUtc).TotalSeconds -lt $QuietSeconds) {
        throw [IO.IOException]::new('Source was recently written.')
    }
    # FileShare.Read refuses concurrent writers/deleters. Locks are held only for
    # hashing/copying, never during the sampling delay or network transfer.
    $first = [IO.File]::Open($Source, 'Open', 'Read', 'Read')
    try { $before = Get-StreamHash $first } finally { $first.Dispose() }
    Start-Sleep -Seconds $SampleSeconds
    $inputStream = [IO.File]::Open($Source, 'Open', 'Read', 'Read')
    try {
        if ($inputStream.Length -ne $info.Length) { throw [IO.IOException]::new('Source length changed.') }
        $afterInfo = Get-Item -LiteralPath $Source
        if ($afterInfo.LastWriteTimeUtc -ne $info.LastWriteTimeUtc) { throw [IO.IOException]::new('Source timestamp changed.') }
        $after = Get-StreamHash $inputStream
        if ($before -ne $after) { throw [IO.IOException]::new('Source content changed.') }
        $inputStream.Position = 0
        $outputStream = [IO.File]::Open($Destination, 'Create', 'Write', 'None')
        try { $inputStream.CopyTo($outputStream); $outputStream.Flush($true) }
        finally { $outputStream.Dispose() }
    } finally { $inputStream.Dispose() }
    return $after
}

function Quote-NativeArgument([string]$Value) {
    # Windows CommandLineToArgvW quoting, including spaces and trailing backslashes.
    if ($Value.Contains("`n") -or $Value.Contains("`r")) { throw 'Newlines are not valid arguments.' }
    return '"' + [regex]::Replace([regex]::Replace($Value, '(\\*)"', '$1$1\"'), '(\\+)$', '$1$1') + '"'
}

function Invoke-SyncSsh {
    param($Config, [string]$Command, [string]$InputFile)
    $known = $Config.KnownHostsFile.Replace('\', '/')
    if ($known.Contains('"')) { throw 'Invalid known_hosts path' }
    $arguments = @('-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
        '-o','IdentitiesOnly=yes','-o','PasswordAuthentication=no','-o','KbdInteractiveAuthentication=no',
        '-o','ConnectTimeout=15','-o','ServerAliveInterval=15','-o','ServerAliveCountMax=3',
        '-o',('UserKnownHostsFile="' + $known + '"'), '-i', $Config.IdentityFile,
        ($Config.UserName + '@' + $Config.HostName), $Command)
    $start = New-Object Diagnostics.ProcessStartInfo
    $start.FileName = "$env:WINDIR\System32\OpenSSH\ssh.exe"
    $start.Arguments = ($arguments | ForEach-Object { Quote-NativeArgument $_ }) -join ' '
    $start.UseShellExecute = $false
    $start.CreateNoWindow = $true
    $start.RedirectStandardInput = $true
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $process = New-Object Diagnostics.Process
    $process.StartInfo = $start
    $source = $null
    try {
        if (-not $process.Start()) { throw 'SSH failed to start' }
        $stdout = $process.StandardOutput.ReadToEndAsync()
        $stderr = $process.StandardError.ReadToEndAsync()
        if ($InputFile) {
            $source = [IO.File]::OpenRead($InputFile)
            $copy = $source.CopyToAsync($process.StandardInput.BaseStream)
            if (-not $copy.Wait(180000)) { throw 'SSH upload timed out' }
        }
        # Close the binary pipe directly; never flush a text encoder into Lua bytes.
        $process.StandardInput.BaseStream.Close()
        if (-not $process.WaitForExit(30000)) { throw 'SSH response timed out' }
        if ($process.ExitCode -ne 0) { throw ('SSH failed: ' + $stderr.Result.Trim()) }
        return $stdout.Result.Trim()
    } finally {
        if ($source) { $source.Dispose() }
        if ($process.Id -and -not $process.HasExited) { $process.Kill(); $process.WaitForExit() }
        $process.Dispose()
    }
}
