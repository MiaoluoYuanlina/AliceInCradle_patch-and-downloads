# 定义文件URL
$files = @(
    "https://api.xiaomiao-ica.top/AIC/file/AIC_patch.exe"

)

# 当前目录下的AICP文件夹路径
$aicpDirectory = Join-Path -Path (Get-Location) -ChildPath "AICP"

# 创建AICP文件夹，如果不存在
if (-Not (Test-Path -Path $aicpDirectory)) {
    New-Item -ItemType Directory -Path $aicpDirectory
}

# 下载文件
$downloadedFiles = @()
foreach ($file in $files) {
    $fileName = [System.IO.Path]::GetFileName($file)
    $destinationPath = Join-Path -Path $aicpDirectory -ChildPath $fileName
    Invoke-WebRequest -Uri $file -OutFile $destinationPath
    $downloadedFiles += $destinationPath
}

# 执行第一个下载的EXE文件并等待其关闭
& $downloadedFiles[0]


# 定义要检测和删除的目录路径
$directoryPath = ".\AIC"

# 检查目录是否存在
if (Test-Path -Path $directoryPath) {
    # 删除目录及其所有内容
    Remove-Item -Path $directoryPath -Recurse -Force
    Write-Host "目录已被删除: $directoryPath"
} else {
    Write-Host "目录不存在: $directoryPath"
}

# 定义要检测和删除的目录路径
$directoryPath = ".\d2l"

# 检查目录是否存在
if (Test-Path -Path $directoryPath) {
    # 删除目录及其所有内容
    Remove-Item -Path $directoryPath -Recurse -Force
    Write-Host "目录已被删除: $directoryPath"
} else {
    Write-Host "目录不存在: $directoryPath"
}

# 定义要检测和删除的目录路径
$directoryPath = ".\downloads"

# 检查目录是否存在
if (Test-Path -Path $directoryPath) {
    # 删除目录及其所有内容
    Remove-Item -Path $directoryPath -Recurse -Force
    Write-Host "目录已被删除: $directoryPath"
} else {
    Write-Host "目录不存在: $directoryPath"
}
