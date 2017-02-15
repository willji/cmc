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

function Get-AllResult
{
    [cmdletbinding()]

    param
    (
        [psobject]$Uri
    )

    $response = Invoke-RestMethod -Uri $Uri -Method Get -Headers $headers -WebSession $webSession -Verbose:$false
    Write-Output -InputObject $response.results
    
    if ($response.next -ne $null)
    {
        if ($response.next -like "*page=46")
        {
            Write-Verbose -Message ("Requesting {0} ..." -f "http://cmc.ops.ymatou.cn/api/tagvalue?page=47")
            Get-AllResult -Uri "http://cmc.ops.ymatou.cn/api/tagvalue?page=47"
        }
        else
        {
            Write-Verbose -Message ("Requesting {0} ..." -f $response.next)
            Get-AllResult -Uri $response.next
        }
    }    
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

$script:headers = @{
    "Authorization" = "Token $csrfToken";
}

#endregion

#region Get tag values

$tagValues = Get-AllResult -Uri ("http://{0}:{1}/api/tagvalue" -f @($computerName, $port)) -Verbose

$result = $tagValues | Group-Object -Property tag | Select-Object -Property "name", @{"name"="SIT1";Expression={($PSItem.Group | ?{$PSItem.environment -eq "SIT1"}).value}}, `
                                                                                    @{"name"="SIT2";Expression={($PSItem.Group | ?{$PSItem.environment -eq "SIT2"}).value}}, `
                                                                                    @{"name"="UAT";Expression={($PSItem.Group | ?{$PSItem.environment -eq "UAT"}).value}}, `
                                                                                    @{"name"="STAGING_PROD";Expression={($PSItem.Group | ?{$PSItem.environment -eq "STAGING_PROD"}).value}}

$result | Export-Csv -Path D:\temp\cmc_templatetags.csv -NoTypeInformation

#endregion