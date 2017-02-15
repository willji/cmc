#region Variables

$gitCmd = "C:\Program Files (x86)\git\cmd\git.exe"

#endregion


#region Git Functions

function Invoke-GitVerb
{
    param
    (
        [Parameter(Mandatory = $false, Position = 0)]
        [string]$Path = ((Get-Location).Path),

        [Parameter(Mandatory = $false, Position = 1)]
        [ValidateSet("Show", "Fetch", "Pull", "Init", "Stash")]
        [string]$Verb,

        [Parameter(Mandatory = $false, Position = 2)]
        [string]$Uri
    )

    $stdOutFile = [System.IO.Path]::GetTempFileName()
    $stdErrFile = [System.IO.Path]::GetTempFileName()

    if (![string]::IsNullOrEmpty($Uri))
    {
        if ($Verb -eq "Pull")
        {
            $gitArgs = @($Verb.ToLower(), $Uri)
        }
    }
    else
    {
        $gitArgs = @($Verb.ToLower())
    }
    
    $params  = @{
        "FilePath"               = $gitCmd;
        "ArgumentList"           = $gitArgs;
        "WorkingDirectory"       = $Path;
        "NoNewWindow"            = $true;
        "Wait"                   = $true;
        "RedirectStandardOutput" = $stdOutFile;
        "RedirectStandardError"  = $stdErrFile;
        "PassThru"               = $true;
    }

    $process = Start-Process @params
    
    if ($process.ExitCode -eq 0)
    {
        $message = Get-Content -Path $stdOutFile -Raw -Encoding UTF8
        if ($message) { Write-Verbose -Message $message }
    }
    else
    {
        $message = Get-Content -Path $stdErrFile -Raw -Encoding UTF8
        Write-Error -Message $message
    }

    Remove-Item -Path $stdOutFile -ErrorAction SilentlyContinue
    Remove-Item -Path $stdErrFile -ErrorAction SilentlyContinue

    return $process.ExitCode
}

function Invoke-GitClone
{
    param
    (
        [Parameter(Mandatory = $true,  Position = 0)]
        [string]$Url,

        [Parameter(Mandatory = $false, Position = 1)]
        [string]$Path = ((Get-Location).Path),

        [Parameter(Mandatory = $false, Position = 2)]
        [pscredential]$Credential = (Get-Credential)
    )

    if ($Credential)
    {
        if ($Credential.GetNetworkCredential().Password.IndexOf("@") -gt 0)
        {
            $password = $Credential.GetNetworkCredential().Password
            $password = $password.Replace("@", "%40")
        }
        else
        {
            $password = $Credential.GetNetworkCredential().Password
        }
        $credPrefix = "http://{0}:{1}@" -f $Credential.UserName, $password
        $Url = $Url.Replace("http://", $credPrefix)
    }

    $stdOutFile = [System.IO.Path]::GetTempFileName()
    $stdErrFile = [System.IO.Path]::GetTempFileName()

    $gitArgs = @("clone", $Url)
    $params  = @{
        "FilePath"               = $gitCmd;
        "ArgumentList"           = $gitArgs;
        "WorkingDirectory"       = $Path;
        "NoNewWindow"            = $true;
        "Wait"                   = $true;
        "RedirectStandardOutput" = $stdOutFile;
        "RedirectStandardError"  = $stdErrFile;
        "PassThru"               = $true;
    }

    $process = Start-Process @params
    
    if ($process.ExitCode -eq 0)
    {
        $message = Get-Content -Path $stdOutFile -Raw -Encoding UTF8
        if ($message) { Write-Verbose -Message $message }
    }
    else
    {
        $message = Get-Content -Path $stdErrFile -Raw -Encoding UTF8
        Write-Error -Message $message
    }

    Remove-Item -Path $stdOutFile -ErrorAction SilentlyContinue
    Remove-Item -Path $stdErrFile -ErrorAction SilentlyContinue

    return $process.ExitCode  
}

function Get-GitUntrackedFile
{
    [CmdletBinding()]
    [OutputType([string])]

    param
    (
        [Parameter(Mandatory = $false, Position = 0)]
        [string]$Path = ((Get-Location).Path)
    )

    process
    {
        $stdOutFile = [System.IO.Path]::GetTempFileName()
        $stdErrFile = [System.IO.Path]::GetTempFileName()

        # git ls-files --exclude-standard -m -o
        $gitArgs = @("ls-files", "--exclude-standard", "-m", "-o")
        $params  = @{
            "FilePath"               = $gitCmd;
            "ArgumentList"           = $gitArgs;
            "WorkingDirectory"       = $Path;
            "NoNewWindow"            = $true;
            "Wait"                   = $true;
            "RedirectStandardOutput" = $stdOutFile;
            "RedirectStandardError"  = $stdErrFile;
            "PassThru"               = $true;
        }

        $process = Start-Process @params
    
        if ($process.ExitCode -eq 0)
        {
            $result = Get-Content -Path $stdOutFile -Raw -Encoding UTF8
        }
        else
        {
            $result = Get-Content -Path $stdErrFile -Raw -Encoding UTF8
        }

        Remove-Item -Path $stdOutFile -ErrorAction SilentlyContinue
        Remove-Item -Path $stdErrFile -ErrorAction SilentlyContinue

        return $result
    }   
}

function Invoke-GitAdd
{
    [CmdletBinding()]
    [OutputType([string])]

    param
    (
        [Parameter(Mandatory = $false, Position = 0)]
        [string]$Path = ((Get-Location).Path)
    )

    process
    {
        $stdOutFile = [System.IO.Path]::GetTempFileName()
        $stdErrFile = [System.IO.Path]::GetTempFileName()

        $gitArgs  = @("add", "-A")
        $params  = @{
            "FilePath"               = $gitCmd;
            "ArgumentList"           = $gitArgs;
            "WorkingDirectory"       = $Path;
            "NoNewWindow"            = $true;
            "Wait"                   = $true;
            "RedirectStandardOutput" = $stdOutFile;
            "RedirectStandardError"  = $stdErrFile;
            "PassThru"               = $true;
        }

        $process = Start-Process @params
    
        if ($process.ExitCode -eq 0)
        {
            $message = Get-Content -Path $stdOutFile -Raw -Encoding UTF8
            if ($message) { Write-Verbose -Message $message }
        }
        else
        {
            $message = Get-Content -Path $stdErrFile -Raw -Encoding UTF8
            Write-Error -Message $message
        }

        Remove-Item -Path $stdOutFile -ErrorAction SilentlyContinue
        Remove-Item -Path $stdErrFile -ErrorAction SilentlyContinue

        return $process.ExitCode     
    }   
}

function Invoke-GitCommit
{
    [CmdletBinding()]
    [OutputType([string])]

    param
    (
        [Parameter(Mandatory = $false, Position = 0)]
        [string]$Path = ((Get-Location).Path),

        [Parameter(Mandatory = $true, Position = 1)]
        [string]$Comment
    )

    process
    {
        $stdOutFile = [System.IO.Path]::GetTempFileName()
        $stdErrFile = [System.IO.Path]::GetTempFileName()

        $gitArgs  = @("commit", "-a", "-m", "`"$Comment`"")
        $params  = @{
            "FilePath"               = $gitCmd;
            "ArgumentList"           = $gitArgs;
            "WorkingDirectory"       = $Path;
            "NoNewWindow"            = $true;
            "Wait"                   = $true;
            "RedirectStandardOutput" = $stdOutFile;
            "RedirectStandardError"  = $stdErrFile;
            "PassThru"               = $true;
        }

        $process = Start-Process @params
    
        if ($process.ExitCode -eq 0)
        {
            $message = Get-Content -Path $stdOutFile -Raw -Encoding UTF8
            if ($message) { Write-Verbose -Message $message }
        }
        else
        {
            $message = Get-Content -Path $stdErrFile -Raw -Encoding UTF8
            Write-Error -Message $message
        }

        Remove-Item -Path $stdOutFile -ErrorAction SilentlyContinue
        Remove-Item -Path $stdErrFile -ErrorAction SilentlyContinue

        return $process.ExitCode    
    }   
}

function Invoke-GitPush
{
    param
    (
        [Parameter(Mandatory = $true,  Position = 0)]
        [string]$Url,

        [Parameter(Mandatory = $false, Position = 1)]
        [string]$Path = ((Get-Location).Path),

        [Parameter(Mandatory = $false, Position = 2)]
        [pscredential]$Credential = (Get-Credential)
    )

    if ($Credential)
    {
        if ($Credential.GetNetworkCredential().Password.IndexOf("@") -gt 0)
        {
            $password = $Credential.GetNetworkCredential().Password
            $password = $password.Replace("@", "%40")
        }
        else
        {
            $password = $Credential.GetNetworkCredential().Password
        }
        $credPrefix = "http://{0}:{1}@" -f $Credential.UserName, $password
        $Url = $Url.Replace("http://", $credPrefix)
    }

    $stdOutFile = [System.IO.Path]::GetTempFileName()
    $stdErrFile = [System.IO.Path]::GetTempFileName()

    # Check remote
    $gitArgs = @("remote")
    $params  = @{
        "FilePath"               = $gitCmd;
        "ArgumentList"           = $gitArgs;
        "WorkingDirectory"       = $Path;
        "NoNewWindow"            = $true;
        "Wait"                   = $true;
        "RedirectStandardOutput" = $stdOutFile;
        "RedirectStandardError"  = $stdErrFile;
        "PassThru"               = $true;
    }

    $process = Start-Process @params
    
    if ($process.ExitCode -eq 0)
    {
        $message = Get-Content -Path $stdOutFile -Raw -Encoding UTF8
        if ([string]::IsNullOrEmpty($message))
        {
            # Add remote
            $gitArgs = @("remote", "add", "origin", $Url)
            $params  = @{
                "FilePath"               = $gitCmd;
                "ArgumentList"           = $gitArgs;
                "WorkingDirectory"       = $Path;
                "NoNewWindow"            = $true;
                "Wait"                   = $true;
                "RedirectStandardOutput" = $stdOutFile;
                "RedirectStandardError"  = $stdErrFile;
                "PassThru"               = $true;
            }

            $process = Start-Process @params
    
            if ($process.ExitCode -eq 0)
            {
                $message = Get-Content -Path $stdOutFile -Raw -Encoding UTF8
                if ($message) { Write-Verbose -Message $message }
            }
            else
            {
                $message = Get-Content -Path $stdErrFile -Raw -Encoding UTF8
                Write-Error -Message $message
            }        
        }
    }
    else
    {
        $message = "无法运行 git remote!"
        throw $message
    }

    # Git push
    $gitArgs = @("push", $Url)
    $params  = @{
        "FilePath"               = $gitCmd;
        "ArgumentList"           = $gitArgs;
        "WorkingDirectory"       = $Path;
        "NoNewWindow"            = $true;
        "Wait"                   = $true;
        "RedirectStandardOutput" = $stdOutFile;
        "RedirectStandardError"  = $stdErrFile;
        "PassThru"               = $true;
    }

    $process = Start-Process @params
    
    if ($process.ExitCode -eq 0)
    {
        $message = Get-Content -Path $stdOutFile -Raw -Encoding UTF8
        if ($message) { Write-Verbose -Message $message }
    }
    else
    {
        $message = Get-Content -Path $stdErrFile -Raw -Encoding UTF8
        Write-Error -Message $message
    }

    Remove-Item -Path $stdOutFile -ErrorAction SilentlyContinue
    Remove-Item -Path $stdErrFile -ErrorAction SilentlyContinue

    return $process.ExitCode
}

function Invoke-GitReset
{
    param
    (
        [Parameter(Mandatory = $false, Position = 0)]
        [string]$Path = ((Get-Location).Path),

        [Parameter(Mandatory = $false, Position = 1)]
        [ValidateSet("Soft", "Mixed", "Hard", "Merge", "Keep")]
        [string]$Mode
    )

    $stdOutFile = [System.IO.Path]::GetTempFileName()
    $stdErrFile = [System.IO.Path]::GetTempFileName()

    $gitArgs = @("reset", ([string]::Format("--{0}", $Mode.ToLower())))
    $params  = @{
        "FilePath"               = $gitCmd;
        "ArgumentList"           = $gitArgs;
        "WorkingDirectory"       = $Path;
        "NoNewWindow"            = $true;
        "Wait"                   = $true;
        "RedirectStandardOutput" = $stdOutFile;
        "RedirectStandardError"  = $stdErrFile;
        "PassThru"               = $true;
    }

    $process = Start-Process @params
    
    if ($process.ExitCode -eq 0)
    {
        $message = Get-Content -Path $stdOutFile -Raw -Encoding UTF8
        if ($message) { Write-Verbose -Message $message }
    }
    else
    {
        $message = Get-Content -Path $stdErrFile -Raw -Encoding UTF8
        Write-Error -Message $message
    }

    Remove-Item -Path $stdOutFile -ErrorAction SilentlyContinue
    Remove-Item -Path $stdErrFile -ErrorAction SilentlyContinue

    return $process.ExitCode
}


function Invoke-GitDiff
{
    param
    (
        [Parameter(Mandatory = $false, Position = 0)]
        [string]$Path = ((Get-Location).Path)
    )

    $stdOutFile = [System.IO.Path]::GetTempFileName()
    $stdErrFile = [System.IO.Path]::GetTempFileName()

    $gitArgs = @("diff", "--word-diff=porcelain")
    $params  = @{
        "FilePath"               = $gitCmd;
        "ArgumentList"           = $gitArgs;
        "WorkingDirectory"       = $Path;
        "NoNewWindow"            = $true;
        "Wait"                   = $true;
        "RedirectStandardOutput" = $stdOutFile;
        "RedirectStandardError"  = $stdErrFile;
        "PassThru"               = $true;
    }

    $process = Start-Process @params
    
    if ($process.ExitCode -eq 0)
    {
        $message = Get-Content -Path $stdOutFile -Raw -Encoding UTF8
        if ($message) { Write-Verbose -Message $message }
    }
    else
    {
        $message = Get-Content -Path $stdErrFile -Raw -Encoding UTF8
        Write-Error -Message $message
    }

    Remove-Item -Path $stdOutFile -ErrorAction SilentlyContinue
    Remove-Item -Path $stdErrFile -ErrorAction SilentlyContinue

    return $process.ExitCode
}

#endregion


Export-ModuleMember -Function *Git*