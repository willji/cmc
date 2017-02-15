Import-Module .\GitCmdWrapper.psm1

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
$namespace = "m2c"
$childProjects = $allprojects | ?{$PSItem.namespace.name -eq $namespace}

$localRootFolder = "d:\gitlab.ops.ymatou.cn\$namespace"
foreach ($childProject in $childProjects)
{
    $localProjectFolder = Join-Path $localRootFolder -ChildPath $childProject.name
    if (Test-Path -Path $localProjectFolder)
    {
        Write-Output -InputObject ("Pulling {0}" -f $childProject.name)
        $result = Invoke-GitVerb -Path $localProjectFolder -Verb Stash
        $result = Invoke-GitVerb -Verb Pull -Path $localProjectFolder -Uri $childProject.http_url_to_repo
    }
    else
    {
        Write-Output -InputObject ("Cloning {0}" -f $childProject.name)
        $result = Invoke-GitClone -Path $localRootFolder -Url $childProject.http_url_to_repo -Credential $cred
    }
}
