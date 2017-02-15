[CmdletBinding()]
[OutputType([void])]

param
(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Path,

    [Parameter(Mandatory = $true, Position = 1)]
    [PSCredential]$Credential
)

# PROD

$gitlabRoot    = "http://gitlab.ops.ymatou.cn"
$gitlabApiRoot = "http://gitlab.ops.ymatou.cn/api/v3"
$cmcCompName   = "cmc.ops.ymatou.cn"
$cmcCompPort   = "80"
$cmcApiRoot    = [string]::Format("http://{0}:{1}", $cmcCompName, $cmcCompPort)
$localFolder   = "d:\gitlab.ops.ymatou.cn"
$cmcUsername   = "infrauser"
$cmcPassword   = "abcd@123"
$cmcSecuPwd    = ConvertTo-SecureString -String $cmcPassword -AsPlainText -Force
$cmcCred       = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $cmcUsername, $cmcSecuPwd

# Change console buffer width to avoid a git diff issue.
# Since the git window width inherites from its parent, if we use 80 or 120, long config lines are break.
# Thus we can not retrieve changes from git diff results.
$oldBufferSize = $Host.UI.RawUI.BufferSize
$newBufferSize = $oldBufferSize
$newBufferSize.Width = 1000
$Host.UI.RawUI.BufferSize = $newBufferSize

# Load Git Command Wrapper.
Import-Module -Name .\GitCmdWrapper.psm1 -Force -ErrorAction Stop

#region Main functions

function ResetBufferSize
{
    $Host.UI.RawUI.BufferSize = $oldBufferSize
}

function Show-Choice
{
    param
    (
        [string]$Title,
        [string]$Message
    )

    $choiceYes = New-Object -TypeName System.Management.Automation.Host.ChoiceDescription -ArgumentList @("是(&Y)", "配置文件已经修改完成")
    $choiceNo = New-Object -TypeName System.Management.Automation.Host.ChoiceDescription -ArgumentList @("否(&N)", "配置文件还需修改")
    $options = [System.Management.Automation.Host.ChoiceDescription[]]($choiceYes, $choiceNo)
    $result = $host.ui.PromptForChoice($title, $message, $options, 1)
    switch ($result)
    {
        0 {
            return $true
        }
        1 {
            return $false
        }
    }
}

function TestGitlabProject
{
    param
    (
        [string]$Name
    )

    $webSession = $null

    $token = [System.Text.Encoding]::UNICODE.GetString([System.Convert]::FromBase64String("UQBUAGYATAA5ADIAegBoAC0AeABvAHYAMwBGADIANwBkAE0AUwBOAA=="))
    
    $url = "$gitlabApiRoot/projects?per_page=100&search=$Name"

    try
    {
        $headers = @{
            "PRIVATE-TOKEN" = $token;
        }

        $response = Invoke-RestMethod -Uri $url -Method Get -Headers $headers -WebSession $webSession
        if (!$response)
        {
            return $false
        }
        else
        {
            foreach ($item in $response)
            {
                if ($item.name -eq $Name)
                {
                    return $true
                }
            }
        }
    }
    catch
    {
        throw $_
    }
}

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

function ConvertTo-MD5
{
    param
    (
        [string]$Password
    )
    
    # If Password is empty, return empty directly.
    if ([string]::IsNullOrEmpty($Password)) { return [string]::Empty }

    # Convert the input string to a byte array and compute the hash. 
    $md5 = [System.Security.Cryptography.MD5]::Create()
    $data = $md5.ComputeHash([System.Text.UTF8Encoding]::UTF8.GetBytes($Password))

    # Create a new Stringbuilder to collect the bytes 
    # and create a string.
    $stringBuilder = New-Object -TypeName System.Text.StringBuilder

    # Loop through each byte of the hashed data  
    # and format each one as a hexadecimal string. 
    for ($i = 0; $i -lt $data.Length; $i++)
    {
        [void]$stringBuilder.Append($data[$i].ToString("x2"));
    }

    # Return the hexadecimal string. 
    return $stringBuilder.ToString()
}

function Update-ApplicationTag
{
    param
    (
        [string]$DepartmentName,
        [string]$ApplicationName,
        [psobject[]]$ApplicationTags,
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

    # create or update application tags

    $headers = @{
        "Authorization" = "Token $csrfToken";
    }

    # Check application existence, create the application if it does not exist.
    $response = Invoke-RestMethod -Uri ("{0}/api/application?name={1}" -f @($cmcApiRoot, $ApplicationName)) -Method Get -Headers $headers -ContentType "application/json" -WebSession $webSession
    if ($response.count -eq 0)
    {
        Write-Output -InputObject ("正在创建应用 {0} ..." -f $ApplicationName)
        $body = @{
            "name" = $ApplicationName
        }
        $jsonBody = ConvertTo-Json -InputObject $body
        $response = Invoke-RestMethod -Uri ("{0}/api/application" -f $cmcApiRoot) -Method Post -Headers $headers -Body $jsonBody -ContentType "application/json" -WebSession $webSession
    }

    Write-Output -InputObject ("确认 {0} 关联应用列表 ..." -f $DepartmentName)
    $response = Invoke-RestMethod -Uri ("{0}/api/department?name={1}" -f @($cmcApiRoot, $DepartmentName)) -Method Get -Headers $headers -ContentType "application/json" -WebSession $webSession
    $department = $response.results[0]
    if ($ApplicationName -notin $department.applications)
    {
        Write-Output -InputObject ("更新 {0} 关联应用列表 ..." -f $DepartmentName)
        $department.applications += $ApplicationName

        $body = @{
            "applications" = $department.applications
        }
        $jsonBody = ConvertTo-Json -InputObject $body
        $response = Invoke-RestMethod -Uri $department.url -Method Patch -Headers $headers -Body $jsonBody -ContentType "application/json" -WebSession $webSession
    }

    foreach ($applicationTag in $ApplicationTags)
    {
        $response = Invoke-RestMethod -Uri ("{0}/api/applicationtag?application__name={1}&file_path={2}" -f @($cmcApiRoot, $applicationTag.application, $applicationTag.file_path)) -Method Get -Headers $headers -ContentType "application/json" -WebSession $webSession

        if ($response.count -eq 0)
        {
            # Create new application tag

            $body = @{
                "application" = $applicationTag.application
                "tags" = $applicationTag.tags
                "file_path" = $applicationTag.file_path
            }

            $jsonBody = ConvertTo-Json -InputObject $body
            $response = Invoke-RestMethod -Uri ("{0}/api/applicationtag" -f $cmcApiRoot) -Method Post -Headers $headers -Body $jsonBody -ContentType "application/json" -WebSession $webSession
            Write-Output -InputObject $response
        }
        else
        {
            $body = @{
                "tags" = $applicationTag.tags
            }

            $jsonBody = ConvertTo-Json -InputObject $body
            $response = Invoke-RestMethod -Uri $response.results[0].url -Method Patch -Headers $headers -Body $jsonBody -ContentType "application/json" -WebSession $webSession
            Write-Output -InputObject $response
        }    
    }
}

#endregion

#region Main Entry

$lineFolder   = Split-Path -Path $Path
$lineName     = $lineFolder.Split("\")[-1]
$departName   = $Path.Split("\")[-2]
$appName      = $Path.Split("\")[-1]
$gitlabPath   = [string]::Format("{0}{1}{2}{3}", $gitlabRoot, "/$lineName", "/$appName", ".git")

$valTagMapping = @{}
$templateTags = Import-Csv -Path D:\temp\passwords.csv

#region git pull

# Raw config files must be stored in d:\gitlab.ops.ymatou.cn\<linename>\<sitename>\.
if (!$Path.ToLower().StartsWith($localFolder)) { throw "请将原始配置文件夹放在 $localFolder 下！`r`n"; exit 1 }

if ($lineFolder.Split("\")[-1].ToLower() -notmatch "m2c|c2c|xlobo|infra|guhuajun") { throw "请将原始配置文件夹放在 $localFolder\<产线名> 下！`r`n"; exit 1 }

if (!(Test-Path -Path $Path))
{
    Write-Warning -Message "本地文件夹不存在！ 执行 git clone。"
    $result = Invoke-GitClone -Url $gitlabPath -Path $lineFolder -Credential $Credential
    if ($result -ne 0) { throw "git clone，无法执行脚本剩余步骤！`r`n"; exit $result }
}

# Check Gitlab Project.
$result = TestGitlabProject -Name $appName
if (!$result)
{
    throw "无法在 Gitlab 中找到该项目！无法执行本脚本剩余步骤! `r`n"
    exit 1
}

Write-Output -InputObject "正在执行 git stash 删除未缓存改动 ..."
$remoteUri = [string]::Format("{0}{1}{2}{3}", $gitlabRoot, "/$lineName", "/$appName", ".git")
$result = Invoke-GitVerb -Verb Stash -Path $Path
if ($result -ne 0)
{
    throw "git stash 执行失败！无法执行本脚本剩余步骤! `r`n"
    exit 1
}

Write-Output -InputObject "正在执行 git pull ..."
$result = Invoke-GitVerb -Verb Pull -Path $Path -Uri $gitlabPath
if ($result -ne 0)
{
    throw "git pull 执行失败！无法执行本脚本剩余步骤! `r`n"
    exit 1
}

Write-Output -InputObject "git pull 执行成功。开始修改配置文件。"

#endregion

#region update local config files.

$applicationTags = @()

$configFiles = Get-ChildItem -Path $Path -Filter "*.config" -Recurse
foreach ($configFile in $configFiles)
{
    $content = Get-Content -Path $configFile.FullName -Raw -Encoding UTF8

    # Convert content to UTF8

    #region Replace password MD5 with plain password, then replace plain password with tag name
    foreach ($pwdMapping in $pwdMappings.GetEnumerator())
    {
        $tags = $templateTags | ?{$PSItem.STAGING_PROD -eq $pwdMapping.Value}
        
        if ($tags.Count -gt 1)
        {
            throw "Found duplicate tags with same value!"
        }
        else
        {
            $tag = $tags.name
        }

        $content = $content.Replace($pwdMapping.Name, $tag)
        
        # Some gitlab projects are using plain password directly, we still need to make sure that the password should be replaced with tag.
        $content = $content.Replace($pwdMapping.Value, $tag)
    }
    #endregion

    #region Replace data source (server)
    $dbServerTags = $templateTags | ?{$PSItem.Name.ToLower().EndsWith('dbserver}$')}
    foreach ($dbServerTag in $dbServerTags)
    {
        $keyword = [string]::Format("data source={0}", $dbServerTag.STAGING_PROD)
        $value   = [string]::Format("data source={0}", $dbServerTag.name)
        $content = [regex]::Replace($content, $keyword, $value, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    }
    #endregion

    #region Replace data catalog (db name)
    $dbCatalogTags = $templateTags | ?{$PSItem.Name.ToLower().EndsWith('dbname}$')}
    foreach ($dbCatalogTag in $dbCatalogTags)
    {
        $keyword = [string]::Format("initial catalog={0}", $dbCatalogTag.STAGING_PROD)
        $value   = [string]::Format("initial catalog={0}", $dbCatalogTag.name)
        $content = [regex]::Replace($content, $keyword, $value, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    }
    #endregion

    #region Replace user id (username)
    $hasReadonlyUserName = $content | Select-String -Pattern "_r;"

    # replace readonly username first.
    $dbReadonlyUserNames = $templateTags | ?{$PSItem.Name.ToLower().EndsWith('readonly_dbusername}$')}
    foreach ($dbReadonlyUserName in $dbReadonlyUserNames)
    {
        $keyword = [string]::Format("user id={0}", $dbReadonlyUserName.STAGING_PROD)
        $value   = [string]::Format("user id={0}", $dbReadonlyUserName.name)
        $content = [regex]::Replace($content, $keyword, $value, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    }

    $dbUserNames = $templateTags | ?{$PSItem.Name.ToLower().EndsWith('dbusername}$')}
    foreach ($dbUserName in $dbUserNames)
    {
        $keyword = [string]::Format("user id={0}", $dbUserName.STAGING_PROD)
        $value   = [string]::Format("user id={0}", $dbUserName.name)
        $content = [regex]::Replace($content, $keyword, $value, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    }
    #endregion

    # try to find all used template tags in the content
    $ucTags = New-Object -TypeName System.Collections.ArrayList
    $cTags = [regex]::Matches($content, "\$\{\w+\}\$")
    $cTags | Select-Object -Property Value -Unique | %{[void]$ucTags.Add($PSItem.Value)}

    # collect application tags
    if ($ucTags.Count -gt 0)
    {
        $filePath = $configFile.FullName.Substring($configFile.FullName.IndexOf($appName) + $appName.Length).Replace("\", "/")
        $applicationTag = [PSCustomObject]@{
            "application" = $appName;
            "tags" = $ucTags;
            "file_path" = $filePath;
        }
        $applicationTags += $applicationTag
    }

    Set-Content -Path $configFile.FullName -Value $content -Force -Encoding UTF8
}

#endregion


Write-Output -InputObject "准备将最新配置上传至Gitlab。"

Write-Output -InputObject "准备缓存改动。"
$result = Invoke-GitAdd -Path $Path
if ($result -ne 0) { throw "Git 缓存失败！无法执行本脚本剩余步骤! `r`n"; ResetBufferSize; exit $result }

Write-Output -InputObject "Git缓存完成。准备提交修改。"
$result = Invoke-GitCommit -Path $Path -Comment "添加模板标签。"
if ($result -ne 0) { throw "Git 提交失败！无法执行本脚本剩余步骤! `r`n"; ResetBufferSize; exit $result }

Write-Output -InputObject "Git修改已提交。准备推送到远程服务器。"
$result = Invoke-GitPush -Url $gitlabPath -Path $Path -Credential $Credential
if ($result -ne 0) { throw "Git 推送失败！无法执行本脚本剩余步骤! `r`n"; ResetBufferSize; exit $result }

Write-Output -InputObject "Git推送成功。站点更新成功。"

Write-Output -InputObject "准备在配置管理中心中登记应用标签。"
Update-ApplicationTag -DepartmentName $departName -ApplicationName $appName -ApplicationTags $applicationTags -Credential $cmcCred

ResetBufferSize

Write-Output -InputObject "配置管理中心中登记应用标签登记完成。"


#endregion
