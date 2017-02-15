# block running this script.
# exit 0

$webSession = $null

# test
# $computerName = "guhuajun"
# $port = "8000"
# $cmcApiRoot = ("http://{0}:{1}" -f @($computerName, $port))

# prod
$computerName = "cmc.ops.ymatou.cn"
$port = "80"
$cmcApiRoot = ("http://{0}:{1}" -f @($computerName, $port))

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

#region Get token

# Get token
$loginURI = [string]::Format("{0}{1}", $cmcApiRoot, "/api/token/")
$webSession = $null

# Get token

# Prepare authentication
$cred = Get-Credential

$body = @{
    "username"            = $cred.GetNetworkCredential().UserName;
    "password"            = $cred.GetNetworkCredential().Password;
}

$jsonBody = ConvertTo-Json -InputObject $body

$response = Invoke-RestMethod -Uri $loginURI -Method Post -Body $jsonBody -ContentType "application/json" -WebSession $webSession

# Get new token and sessionid
$csrfToken = $response.token

$headers = @{
    "Authorization" = "Token $csrfToken";
}

#endregion

#region Import applications
<#
$appNames = @()
20..99 | %{ $appNames += "m2c$PSItem" }
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

#region Import template tags

$rawTags = Import-Csv .\cmc_templatetags.csv
foreach ($rawTag in $rawTags)
{
    $body = @{
        "name"                = $rawTag.name
        "description"         = (ConvertTo-Unicode -InputObject $rawTag.description)
    }

    $jsonBody = ConvertTo-Json -InputObject $body
    $jsonBody = $jsonBody.Replace("\\", "\")

    $tagName = $rawTag.name
    Invoke-RestMethod -Uri ("http://{0}:{1}/api/templatetag" -f @($computerName, $port)) -Method Post -Headers $headers -Body $jsonBody -ContentType "application/json" -WebSession $webSession
}

#endregion

#region Import tag values

$rawTags = Import-Csv .\cmc_templatetags.csv
foreach ($rawTag in $rawTags)
{
    $envNames = @("SIT1", "SIT2", "UAT", "STAGING_PROD")

    foreach ($envName in $envNames)
    {
        $body = @{
            "environment"         = $envName
            "tag"                 = $rawTag.name
            "value"               = $rawTag.$envName
        }

        $jsonBody = ConvertTo-Json -InputObject $body
        $jsonBody = $jsonBody.Replace("\\", "\")

        Invoke-RestMethod -Uri ("http://{0}:{1}/api/tagvalue" -f @($computerName, $port)) -Method Post -Headers $headers -Body $jsonBody -ContentType "application/json" -WebSession $webSession    
    }
}

#endregion