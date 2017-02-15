#requires -Version 4.0

param
(
    [PSCredential]$Credential = (Get-Credential)
)

$webSession = $null
$cmcCompName   = "cmc.ops.ymatou.cn"
$cmcCompPort   = "80"
$cmcApiRoot    = [string]::Format("http://{0}:{1}", $cmcCompName, $cmcCompPort)

function Get-Token
{
    param
    (
        [PSCredential]$Credential
    )

    # Get token
    $loginURI = [string]::Format("{0}{1}", $cmcApiRoot, "/api/token/")
    $webSession = $null

    # Get token

    # Prepare authentication
    $body = @{
        "username"            = $Credential.GetNetworkCredential().UserName;
        "password"            = $Credential.GetNetworkCredential().Password;
    }

    $jsonBody = ConvertTo-Json -InputObject $body

    $response = Invoke-RestMethod -Uri $loginURI -Method Post -Body $jsonBody -ContentType "application/json" -WebSession $webSession

    # Get new token and sessionid
    $csrfToken = $response.token

    return $csrfToken
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
        Write-Verbose -Message ("Requesting {0} ..." -f $response.next)
        Get-AllResult -Uri $response.next
    }
}

# get template tags and values

$token = Get-Token -Credential $Credential
$headers = @{
    "Authorization" = "Token $token";
}

$htServerIPs = @{
    "mongorep1db1.db.ymatou.com" = "10.11.11.1"
    "mongorep1db2.db.ymatou.com" = "10.11.11.2"
    "mongorep1db3.db.ymatou.com" = "10.11.11.4"
}
$ipPatterns = $htServerIPs.Values -join "|"

$mongoTemplateTags = Import-Csv -Path D:\CorpDocs\cmc_templatetags.csv -Encoding UTF8
$filteredMTTs = $mongoTemplateTags | ?{$PSItem.staging_prod -match $ipPatterns}

foreach ($filteredMTT in $filteredMTTs)
{
    $tagName = $filteredMTT.name
    $response = Invoke-RestMethod -Uri ([string]::Format("{0}{1}", $cmcApiRoot, "/api/tagvalue?tag__name=$tagName&environment__name=STAGING_PROD")) -Method Get -Headers $headers -ContentType "application/json" -WebSession $webSession
    $tagValue = $response.results[0]
    
    $newValue = $tagValue.value
    $htServerIPs.GetEnumerator() | %{$newValue = $newValue.replace($PSItem.Value, $PSItem.Key)}

    $jsonBody = ConvertTo-Json -InputObject @{"value" = $newValue}
    Invoke-RestMethod -Uri $tagValue.url -Method Patch -Headers $headers -Body $jsonBody -ContentType "application/json" -WebSession $webSession
}