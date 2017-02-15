$rootdir = "d:\gitlab.ops.ymatou.cn"

$results = @()

# ASP.NET
# redis
$rawLines = Get-ChildItem -Path $rootdir -Recurse -Filter "*.config" | Select-String -Pattern "redis" #| ?{!$PSItem.Line.Trim().StartsWith("<!--")}
foreach ($rawLine in $rawLines)
{
    $result = [PSCustomObject]@{
        "Type"       = "Redis";
        "Product"    = $rawLine.Path.Split("\")[2];
        "Path"       = $rawLine.Path;
        "File"       = $rawLine.Filename;
        "LineNumber" = $rawLine.LineNumber;
        "Line"       = $rawLine.Line.Trim()
        "Value"      = [regex]::Match($rawLine.Line.Trim(), "(?<=value\=)\S+")

    }
    $results += $result
}

# mongodb
$rawLines = Get-ChildItem -Path $rootdir -Recurse -Filter "*.config" | Select-String -Pattern "mongo://" #| ?{!$PSItem.Line.Trim().StartsWith("<!--")}
foreach ($rawLine in $rawLines)
{
    $result = [PSCustomObject]@{
        "Type"       = "mongo";
        "Product"    = $rawLine.Path.Split("\")[2];
        "Path"       = $rawLine.Path;
        "File"       = $rawLine.Filename;
        "LineNumber" = $rawLine.LineNumber;
        "Line"       = $rawLine.Line.Trim()
        "Value"      = [regex]::Match($rawLine.Line.Trim(), "(?<=value\=)\S+")

    }
    $results += $result
}

# mq
$rawLines = Get-ChildItem -Path $rootdir -Recurse -Filter "*.config" | Select-String -Pattern "mq" #| ?{!$PSItem.Line.Trim().StartsWith("<!--")}
foreach ($rawLine in $rawLines)
{
    $result = [PSCustomObject]@{
        "Type"       = "mq";
        "Product"    = $rawLine.Path.Split("\")[2];
        "Path"       = $rawLine.Path;
        "File"       = $rawLine.Filename;
        "LineNumber" = $rawLine.LineNumber;
        "Line"       = $rawLine.Line.Trim()
        "Value"      = [regex]::Match($rawLine.Line.Trim(), "(?<=value\=)\S+")
    }
    $results += $result
}

# node.js
# redis
$rawLines = Get-ChildItem -Path $rootdir -Recurse -Filter "config.js" | Select-String -Pattern "redis" #| ?{!$PSItem.Line.Trim().StartsWith("<!--")}
foreach ($rawLine in $rawLines)
{
    $result = [PSCustomObject]@{
        "Type"       = "Redis";
        "Product"    = $rawLine.Path.Split("\")[2];
        "Path"       = $rawLine.Path;
        "File"       = $rawLine.Filename;
        "LineNumber" = $rawLine.LineNumber;
        "Line"       = $rawLine.Line.Trim()
        "Value"      = [regex]::Match($rawLine.Line.Trim(), "(?<=value\=)\S+")
    }
    $results += $result
}

# mongodb
$rawLines = Get-ChildItem -Path $rootdir -Recurse -Filter "config.js" | Select-String -Pattern "mongo" #| ?{!$PSItem.Line.Trim().StartsWith("<!--")}
foreach ($rawLine in $rawLines)
{
    $result = [PSCustomObject]@{
        "Type"       = "mongo";
        "Product"    = $rawLine.Path.Split("\")[2];
        "Path"       = $rawLine.Path;
        "File"       = $rawLine.Filename;
        "LineNumber" = $rawLine.LineNumber;
        "Line"       = $rawLine.Line.Trim()
        "Value"      = [regex]::Match($rawLine.Line.Trim(), "(?<=value\=)\S+")
    }
    $results += $result
}

# mq
$rawLines = Get-ChildItem -Path $rootdir -Recurse -Filter "config.js" | Select-String -Pattern "mq" #| ?{!$PSItem.Line.Trim().StartsWith("<!--")}
foreach ($rawLine in $rawLines)
{
    $result = [PSCustomObject]@{
        "Type"       = "mq";
        "Product"    = $rawLine.Path.Split("\")[2];
        "Path"       = $rawLine.Path;
        "File"       = $rawLine.Filename;
        "LineNumber" = $rawLine.LineNumber;
        "Line"       = $rawLine.Line.Trim()
        "Value"      = [regex]::Match($rawLine.Line.Trim(), "(?<=value\=)\S+")
    }
    $results += $result
}

$results | Export-Csv -Path "D:\Temp\RedisMongoMQ.csv" -NoTypeInformation -Encoding UTF8