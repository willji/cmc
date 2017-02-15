function GetGitlabProject
{
    param
    (
        [string]$Name
    )

    $webSession = $null

    $token = [System.Text.Encoding]::UNICODE.GetString([System.Convert]::FromBase64String("UQBUAGYATAA5ADIAegBoAC0AeABvAHYAMwBGADIANwBkAE0AUwBOAA=="))
    
    $url = "http://gitlab.ops.ymt.corp/api/v3/projects?search=$Name"

    try
    {
        $headers = @{
            "PRIVATE-TOKEN" = $token;
        }

        $response = Invoke-RestMethod -Uri $url -Method Get -Headers $headers -WebSession $webSession
        if (!$response)
        {
            return $null
        }
        else
        {
            return $response
        }
    }
    catch
    {
        throw $_
    }
}

GetGitlabProject -Name "cs.ymatou.com"

<#
$department = "infra"
$appNames = @()
$apps = 1..3 | %{ GetGitlabProject -Page $PSItem } | ?{$PSItem.namespace.name -eq $department}
$apps | %{ $appNames += $PSItem.name }

$webSession = $null

$computerName = $env:COMPUTERNAME
$port = "8000"
$userName = "opsadmin"
$password = "Welcome123"
$loginURI = ("http://{0}:{1}/api/api-auth/login/" -f @($computerName, $port))

function ConvertTo-Unicode
{
    param
    (
        [string]$InputObject
    )

    $sb = New-Object -TypeName System.Text.StringBuilder
    foreach ($chr in $InputObject.ToCharArray())
    {
        [void]$sb.Append("\u");
        [void]$sb.Append([String]::Format("{0:x4}", [int]$chr));
    }
    return $sb.ToString()
}
#>

# Get token
<#
$webResponse = Invoke-WebRequest -Uri $loginURI -SessionVariable webSession
$csrfToken   = $webResponse.BaseResponse.Cookies['csrftoken'].Value

# Prepare authentication
$body = @{
    "csrfmiddlewaretoken" = $csrfToken;
    "username"            = $userName;
    "password"            = $password;
    "next"                = '/'
    'submit'              = 'Log in'
}

# Turn off auto redirection to get seesionid, this requires you user name and password is correct. Otherwise you will get a HTTP 200 (Loogin failed).
$webResponse = Invoke-WebRequest -Uri $loginURI -Method Post -Body $body -WebSession $webSession -MaximumRedirection 0 -ErrorAction Ignore

# Get new token and sessionid
$csrfToken = $webResponse.BaseResponse.Cookies['csrftoken'].Value
$sessionid = $webResponse.BaseResponse.Cookies['sessionid'].Value
#>

#region Import applications
<#
foreach ($appName in $appNames)
{
    $body = @{
        "csrfmiddlewaretoken" = $csrfToken;
        "sessionid"           = $sessionid;
    }

    $body = @{
        "name"                = $appName
    }

    $jsonBody = ConvertTo-Json -InputObject $body

    $headers = @{
        "X-CSRFToken" = $csrfToken;
    }
    Invoke-RestMethod -Uri ("http://{0}:{1}/api/application" -f @($computerName, $port)) -Method Post -Headers $headers -Body $jsonBody -ContentType "application/json" -WebSession $webSession
}
#>
#endregion


#region Assign applications
<#
$headers = @{
    "X-CSRFToken" = $csrfToken;
}

$url = Invoke-RestMethod -Uri ("http://{0}:{1}/api/department?name=$department" -f @($computerName, $port)) -Method Get -Headers $headers -WebSession $webSession

$body = @{
    "name"                = $department
    "applications"        = $appNames
}

$jsonBody = ConvertTo-Json -InputObject $body

$headers = @{
    "X-CSRFToken" = $csrfToken;
}
Invoke-RestMethod -Uri ($url.results[0].url) -Method Patch -Headers $headers -Body $jsonBody -ContentType "application/json" -WebSession $webSession
#>
#endregion


