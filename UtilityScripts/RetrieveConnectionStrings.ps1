# After "git clone" all projects to your local folder, you can run following command to get mssql server connection strings.
# folder structure
<#
d:\gitlab.ops.ymatou.cn
|-c2c
|-m2c
|-xlobo
|-infra
#>

<#
PS C:\> cd d:\gitlab.ops.ymatou.cn
PS D:\gitlab.ops.ymatou.cn> Get-ChildItem -Filter *.config -Recurse | Select-String -Pattern "source=(\$\{\w+\}\$)" | Select-Object -Property @{Name="Line"; Expression={$PSItem.Line.Trim()}} -Unique | Sort-Object -Property Line | Export-Csv -Path d:\temp\mssql_connection_strings.csv -NoTypeInformation
#>