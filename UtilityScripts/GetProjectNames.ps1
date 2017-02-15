param
(
	[string]$NameSpace
)

function GetGitlabProject
{
    param
    (
        [string]$Page
    )

    $webSession = $null

    $token = [System.Text.Encoding]::UNICODE.GetString([System.Convert]::FromBase64String("UQBUAGYATAA5ADIAegBoAC0AeABvAHYAMwBGADIANwBkAE0AUwBOAA=="))
    
    $url = "http://gitlab.ops.ymatou.cn/api/v3/projects?per_page=100&page=$Page"

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

$allprojects = @()
1..3 | %{
    $response = GetGitlabProject -Page $PSItem
    $allprojects += $response
    if (!$response)
    {
        break
    }
}

$cred = Get-Credential -UserName guhuajun -Message "Providing user credential for connecting gitlab."
$childProjects = $allprojects | ?{$PSItem.namespace.name -eq $NameSpace}

foreach ($childProject in $childProjects)
{
    Write-Output -InputObject $childProject.name
}
