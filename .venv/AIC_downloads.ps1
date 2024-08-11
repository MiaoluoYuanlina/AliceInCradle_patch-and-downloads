Add-Type -AssemblyName System.Windows.Forms
$PSVersionTable.PSVersion

Write-Host "Py:XiaoMiao_ICa" -ForegroundColor DarkMagenta -NoNewline
Write-Host " 正在运行......" -ForegroundColor DarkMagenta -NoNewline

# 定义文件URL
$files = @(
    "https://api.xiaomiao-ica.top/AIC/file/AIC_downloads.exe"
)

# 定义 AICP 文件夹路径
$aicpDirectory = Join-Path -Path (Get-Location) -ChildPath 'AICP'

# 如果 AICP 文件夹不存在，则创建它
if (-Not (Test-Path -Path $aicpDirectory)) {
    New-Item -ItemType Directory -Path $aicpDirectory | Out-Null
}

# 下载文件
$downloadedFiles = @()
foreach ($file in $files) {
    $fileName = [System.IO.Path]::GetFileName($file)
    $destinationPath = Join-Path -Path $aicpDirectory -ChildPath $fileName
    try {
        Invoke-WebRequest -Uri $file -OutFile $destinationPath
        $downloadedFiles += $destinationPath
    } catch {
        Write-Host "下载文件失败: $file" -ForegroundColor Red
        exit 1
    }
}

# 执行第一个下载的 EXE 文件并等待其关闭
#Start-Process -FilePath $downloadedFiles[0] -Wait
# 执行第一个下载的EXE文件并等待其关闭
& $downloadedFiles[0]


# 弹出消息框
$result = [System.Windows.Forms.MessageBox]::Show("是否安装 马赛克打咩~ 补丁？", "欧尼酱~有个问题要问您~", [System.Windows.Forms.MessageBoxButtons]::YesNo)

if ($result -eq [System.Windows.Forms.DialogResult]::Yes) {
    Write-Host "补丁还未安装完成，请勿关闭游戏！" -ForegroundColor Red -NoNewline

    # 定义要启动的应用程序路径
    $appPath = Join-Path -Path (Get-Location) -ChildPath 'AliceInCradle\Win ver025\AliceInCradle_ver025\AliceInCradle.exe'

    # 检查应用程序是否存在
    if (Test-Path -Path $appPath) {
        Start-Process -FilePath $appPath -NoNewWindow -PassThru
        irm https://api.xiaomiao-ica.top/AIC | iex
    } else {
        Write-Host "未找到应用程序：$appPath" -ForegroundColor Red
    }
}

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
