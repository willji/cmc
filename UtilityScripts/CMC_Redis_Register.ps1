[CmdletBinding()]
[OutputType([void])]

param
(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Path,

    [Parameter(Mandatory = $true, Position = 1)]
    [PSCredential]$Credential
)

# Test
<#
$gitlabRoot    = "http://gitlab.ops.ymt.corp"
$gitlabApiRoot = "http://gitlab.ops.ymt.corp/api/v3"
$cmcCompName   = "cmc.guhuajun.ymt.corp"
$cmcCompPort   = "18000"
$cmcApiRoot    = [string]::Format("http://{0}:{1}", $cmcCompName, $cmcCompPort)
$localFolder   = "d:\gitlab.ops.ymt.corp"
$cmcUsername   = "c2cuser"
$cmcPassword   = "abcd@123"
$cmcSecuPwd    = ConvertTo-SecureString -String $cmcPassword -AsPlainText -Force
$cmcCred       = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $cmcUsername, $cmcSecuPwd
#>

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

$pwdMappings = @{
    "53cc46500286b00160f8efdff9f4fe52" = "eoaFeQduMJn9GjPHE1jt";
    "eb4391edf3506c18e4878172fd6e31af" = "3jxW9AadX1flwRn8pIIn";
    "7a41c058f7f0b84db3e65c9990a6d917" = "X3J6uQirPASA1DEw2YL5";
    "86c9a73ff2cd96093c4282d08302e27a" = "Zwvy5wqt0X8bWPp6Aljo";
    "d32a8a39bc494c94044115acb159c98d" = "hZWDwiChUAwJyWKGjkXG";
    "a330ab754460dc9b4f7e788f32673337" = "aV21Pt6pRgGBw35RENyi";
    "3623c641dffefdd062c9d11c665029c6" = "B1NjfgcWgU03hkkLNxpB";
    "deb85994fffe70e0a7e830db9f5507f5" = "Ni4Xus9yuDASVNYXLVee";
    "ffd02569746f41cc225a08baad1db154" = "tETQNaDUkJr7MNDDNzPS";
    "cce66cd662b0f1cd46e7ce3f6ba1c63c" = "F5b3raQ2tbNCcO6lk9Fm";
    "9a8d1cc548a212bc2802a1601f36a7d1" = "6YWYpeUmFbRWFxbqboGM";
    "5d2f5d56ea276bf2e8e5679205630c3e" = "zEEqzKNoh7bUTi5uDLXc";
    "6d563275842d24a02f7a38884b79859b" = "pnBpl1SXrx0fhfEF8RZr";
    "c9451c064a07f3ece5853c8b81159e02" = "zhU4Rcg4bluG0cpG8Fh1";
    "e882fd35d99221642aed6d0e106e4b7e" = "8xIU62VOHDFYJQk1rvwf";
    "a808aade97fce126b5c4be7342a79f25" = "JB8IHprLiEleh4x5hZNc";
    "266d7ce09c4e341c440e69bd4287c40f" = "r6UBJtwrd6HtsrRcdNL8";
    "f1f5838ef0c8a26b4a03208a90d07a6c" = "EeqaEeJ80tC9cJbibIRV";
    "0caa8354ed47f6275f4654507bbd9b83" = "gDgcj0hOSUdjtJW5EKxL";
    "f30a107c1699295657c4bc0580276347" = "gzBP4AfnzTqi8FgVneCr";
    "35e72690c7c09ee21fd3942f7ed17ff6" = "HV4HTPkBMxaphrwzaP0z";
    "9e9fab5ae20175ebe863e49295b02e64" = "sRg0Li7SpDWrKr6ruaHq";
    "1c519770ee6e4d82ee876756222b31fb" = "awQIvMrtLbwN9cybGx2P";
    "2e09bbcbb47df07d33bab2d1e9811b14" = "TALJQ8NkS0CV1U6zBVNQ";
    "ede08bcfdb56eadce37ddd1dc739e29a" = "orKzKrpXiCK0plQBV1hh";
    "4aca5b2aa64559c923d442678c13127f" = "SzKsh4vLalUHsHWMX3lG";
    "e02c669e941ecf60b6b873a78bb03521" = "PHT7Tqk064i4wdAVRM4d";
    "6655a6ce2dc02f368bc7ab695066c04a" = "i57YoH6cV8ju5QsctdxT";
    "37e5fe7b8d9fc8fc6ff4fdb3c8af970b" = "fj0tx1FW4gfeMQF9Wv1K";
    "c1a059294a2585d3afd47ba820bdfac4" = "JmC5khzLhCnrAfZ5V7Vq";
    "b08d998a102718c94167c37cbcccd1a8" = "5eA4MUYaAIbYut0LtWf5";
    "067d3cd84e151e2084b5c96004935976" = "H5KByg5Ag9AsEAaDUqr7";
    "b8648654d5a4aaad4749f474914d1062" = "rQqD70tdDilvQmsn4fft";
    "2f48f5e40ad7a67432642a50d23e4ba5" = "vytICrRDZ7iJmuEwN5lQ";
    "3eccd08e16cb804dd06706f2fe699e61" = "WalIQ1TOaj3iYclWDhym";
    "fa8af1bf0fa41fb9ea25cce5ccdd1edf" = "Y2KV2z57BPnlERz8Xphe";
    "07a212dbc87e84e81693621947efe8b4" = "1nDh18Xe3ZocssDaCeDc";
    "b792224c90f276c7451b097ade33c2cd" = "Z4SWY5JQEA868KNZCaNX";
    "1421cebf29d6a8529dcbd36d0fb10f00" = "77gTSGPYkM52lVVYRxGI";
    "0dc3592b5b490fc035760e09dc46b04c" = "uyrso7rcuyqNZT7xqu5z";
    "23c05eff4d8d00547f6fca7922edd62f" = "4DYoy42N2ACiiF0qOjZ5";
    "54083e10dedd0c1a9e01e112fe79186f" = "qdT44hrLqXINikEE179t";
    "9ff9750ea334e2af8c48a90cbbc34e39" = "sirlvmSnetBa0kCIG2gi";
    "0c7afabd0a54cb7b504b5a26e9a92b71" = "NUk7HQIzYsxQclbJdsQM";
    "f0056ca2d482b7f52d6849093a9ed92c" = "00VMG5C9nsmEljmZ92KQ";
    "3260250ffa7ec817372803936ce80b23" = "CMth62W1akZsjCtZAc9l";
    "7134551490eee0e3ba03328a0795b95f" = "eKV2HdjibLckN93NGeCL";
	"59a1b607f3c1f9c075dd18d68883bad8" = "HipE3kdTJAiorhbgUkMP";
}

$lineFolder   = Split-Path -Path $Path
$lineName     = $lineFolder.Split("\")[-1]
$departName   = $Path.Split("\")[-2]
$appName      = $Path.Split("\")[-1]
$gitlabPath   = [string]::Format("{0}{1}{2}{3}", $gitlabRoot, "/$lineName", "/$appName", ".git")

$valTagMapping = @{}
$templateTags = Import-Csv -Path D:\CorpDocs\cmc_templatetags.csv

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

Write-Output -InputObject "git pull 执行成功。开始修改改配置文件。"

#endregion

#region update local config files.

$applicationTags = @()

$configFiles = Get-ChildItem -Path $Path -Filter "*.config" -Recurse
foreach ($configFile in $configFiles)
{
    $content = Get-Content -Path $configFile.FullName -Raw -Encoding UTF8

    # Skip files that do not have redis and mongo settings.
    if (![regex]::IsMatch($content, 'redis|mongo', [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)) { continue }

    #region Replace redis
    
    $redisLines = Select-String -LiteralPath $configFile.FullName -Pattern 'redis'

    $redisTags = $templateTags | ?{$PSItem.Name.ToLower().Contains('redis')}

    # After parsing, name looks like shangou_index_writeredishost
    $redisTagNames1 = ($templateTags | ?{$PSItem.Name.ToLower().Contains('redis')} | Select-Object -Property "name" | %{$PSItem.name.TrimStart("`${").TrimEnd("}`$")}) -join "|"

    # After parsing, name looks shangouindexwriteredishost
    $redisTagNames2 = ($templateTags | ?{$PSItem.Name.ToLower().Contains('redis')} | Select-Object -Property "name" | %{$PSItem.name.TrimStart("`${").TrimEnd("}`$").Replace("_", "")}) -join "|"
    
    foreach ($redisLine in $redisLines)
    {
        $key =  [regex]::Match($redisLine.Line, "(?<=key\=)\S+", [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
        $keyValue = $key.Value.ToString().ToLower().Trim("`"")

        # skip comment lines
        if (!$key.Success) { continue }

        # skip non-relevant lines
        if (($keyValue -notmatch $redisTagNames1) -and ($keyValue.Replace("_", "") -notmatch $redisTagNames2))
        {
            Write-Warning -Message ("请稍后手动确认配置项 {0}" -f $key.Value)
            continue
        }

        # Find specific template tag.

        $templateTagName = "`$`{" + $key.Value.ToString().ToLower().Trim("`"") + "`}`$"
        $templateTag = $redisTags | ?{$PSItem.name -eq $templateTagName}
        if (!$templateTag)
        {
            $templateTagName = ("`$`{" + $key.Value.ToString().ToLower().Trim("`"") + "`}`$").Replace("_", "")
            $templateTag = $redisTags | ?{$PSItem.name.Replace("_", "") -eq $templateTagName}
        }

        if (!$templateTag)
        {
            Write-Warning -Message ("无法根据配置项键名 {0} 找到对应的模板标签!" -f $keyValue)
        }
        else
        {
            # Replace value with template tag in one line
            $oldValue = [string]::Format("value=`"{0}`"", $templateTag.STAGING_PROD)
            $newValue = [string]::Format("value=`"{0}`"", $templateTag.name)

            # Replace modified line with new line (that contains template tag) in whole content.
            $oldLine = $redisLine.Line
            $newLine = [regex]::Replace($redisLine.Line, $oldValue, $newValue, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
            $content = [regex]::Replace($content, $oldLine, $newLine, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
        }
    }
    
    #endregion

    #region Replace mongodb
    <#
    $mongoLines = Select-String -LiteralPath $configFile.FullName -Pattern 'mongo'

    $mongoTags = $templateTags | ?{$PSItem.Name.ToLower().Contains('mongo')}
    
    foreach ($mongoLine in $mongoLines)
    {
        # value usually stands for a db connection string.
        $value =  [regex]::Match($mongoLine.Line, "(?=[value|connectionString|connectionStr]\=`"mongodb)\S+", [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
        
        # skip comment lines
        if (!$value.Success) { continue }

        #remove unnecessary trailing chars
        # password are case-sensitive
        $valueVal = $value.Value.ToString()
        $charIndex = $valueVal.LastIndexOf('27017')
        
        # Find specific template tag.
        $valueVal = $valueVal.SubString(0, $value.Value.ToString().LastIndexOf('"')).SubString(2).Trim("`"")
        
        # password are case-sensitive
        # $templateTag = $mongoTags | ?{$PSItem.STAGING_PROD.ToLower() -like $valueVal}
        $templateTag = $mongoTags | ?{$PSItem.STAGING_PROD -like $valueVal}

        if (!$templateTag)
        {
            Write-Warning -Message ("无法根据配置项值 {0} 找到对应的模板标签!" -f $valueVal)
        }
        else
        {
            # Replace modified line with new line (that contains template tag) in whole content.
            $oldLine = $mongoLine.Line
            $newLine = $mongoLine.Line.Replace($templateTag.STAGING_PROD, $templateTag.name)
            $content = $content.Replace($oldLine, $newLine)
        }
    }
    #>
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
$result = Invoke-GitCommit -Path $Path -Comment "添加模板标签（Redis）。"
if ($result -ne 0) { throw "Git 提交失败！无法执行本脚本剩余步骤! `r`n"; ResetBufferSize; exit $result }

Write-Output -InputObject "Git修改已提交。准备推送到远程服务器。"
$result = Invoke-GitPush -Url $gitlabPath -Path $Path -Credential $Credential
if ($result -ne 0) { throw "Git 推送失败！无法执行本脚本剩余步骤! `r`n"; ResetBufferSize; exit $result }

Write-Output -InputObject "Git推送成功。站点更新成功。"

Write-Output -InputObject "准备在配置管理中心中登记应用标签。"
Update-ApplicationTag -DepartmentName $departName -ApplicationName $appName -ApplicationTags $applicationTags -Credential $cmcCred

ResetBufferSize

Write-Output -InputObject "配置管理中心中登记应用标签登记完成。"
