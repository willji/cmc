#requires -Version 4.0

param
(
    [PSCredential]$Credential = (Get-Credential)
)

# Update local template tags file.

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

$response = Get-AllResult -Uri ([string]::Format("{0}{1}", $cmcApiRoot, "/api/tagvalue")) -Verbose
$htValues = @{}
foreach ($item in $response)
{
    if (!$htValues.ContainsKey($item.tag))
    {
        $htValues.Add($item.tag, @{$item.environment = $item.value})       
    }
    else
    {
        $htValues[$item.tag].Add($item.environment, $item.value)
    }
}

$results = @()
$groupedItems = $response | Group-Object -Property tag
foreach ($groupedItem in $groupedItems)
{
    $result = [pscustomobject]@{
        "name" = $groupedItem.Name
        "sit1" = $htValues[$groupedItem.Name]['sit1']
        "sit2" = $htValues[$groupedItem.Name]['sit2']
        "uat" = $htValues[$groupedItem.Name]['uat']
        "staging_prod" = $htValues[$groupedItem.Name]['staging_prod']
    }
    $results += $result
}

$results