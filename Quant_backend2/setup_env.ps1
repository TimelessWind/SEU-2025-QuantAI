# 虚拟环境配置脚本 - PowerShell版本

# 设置执行策略，允许运行脚本
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force

# 设置变量
$VENV_DIR = ".venv"
$REQUIREMENTS_FILE = "requirements.txt"

# 检查Python是否已安装
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Host "错误: 未找到Python。请先安装Python并确保它在系统PATH中。" -ForegroundColor Red
    Read-Host "按Enter键退出..."
    exit 1
}

# 检查pip是否已安装
if (-not (Get-Command "pip" -ErrorAction SilentlyContinue)) {
    Write-Host "错误: 未找到pip。请先安装pip。" -ForegroundColor Red
    Read-Host "按Enter键退出..."
    exit 1
}

# 创建虚拟环境（如果不存在）
if (-not (Test-Path $VENV_DIR)) {
    Write-Host "创建虚拟环境..."
    python -m venv $VENV_DIR
    if ($LASTEXITCODE -ne 0) {
        Write-Host "创建虚拟环境失败！" -ForegroundColor Red
        Read-Host "按Enter键退出..."
        exit 1
    }
    Write-Host "虚拟环境创建成功！" -ForegroundColor Green
} 
else {
    Write-Host "虚拟环境已存在。"
}

# 激活虚拟环境
Write-Host "激活虚拟环境..."
$ACTIVATE_SCRIPT = Join-Path $VENV_DIR "Scripts\Activate.ps1"
if (Test-Path $ACTIVATE_SCRIPT) {
    & $ACTIVATE_SCRIPT
    Write-Host "虚拟环境已激活！" -ForegroundColor Green
} 
else {
    Write-Host "错误: 无法找到激活脚本。虚拟环境可能已损坏。" -ForegroundColor Red
    Read-Host "按Enter键退出..."
    exit 1
}

# 安装依赖包
Write-Host "安装依赖包..."
if (Test-Path $REQUIREMENTS_FILE) {
    pip install -r $REQUIREMENTS_FILE
    if ($LASTEXITCODE -ne 0) {
        Write-Host "安装依赖包失败！" -ForegroundColor Red
        Read-Host "按Enter键退出..."
        exit 1
    }
    Write-Host "所有依赖包安装成功！" -ForegroundColor Green
} 
else {
    Write-Host "错误: 未找到requirements.txt文件。" -ForegroundColor Red
    Read-Host "按Enter键退出..."
    exit 1
}

# 验证tushare是否安装成功
try {
    python -c "import tushare as ts; print('tushare已成功安装，版本:', ts.__version__)" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "tushare库验证成功！" -ForegroundColor Green
    } 
    else {
        Write-Host "tushare安装失败，正在尝试重新安装..." -ForegroundColor Red
        pip install tushare
        python -c "import tushare as ts; print('tushare已成功安装，版本:', ts.__version__)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "tushare库验证成功！" -ForegroundColor Green
        } else {
            Write-Host "tushare库验证失败！" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "tushare安装失败，正在尝试重新安装..." -ForegroundColor Red
    pip install tushare
    try {
        python -c "import tushare as ts; print('tushare已成功安装，版本:', ts.__version__)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "tushare库验证成功！" -ForegroundColor Green
        } else {
            Write-Host "tushare库验证失败！" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "tushare库验证失败！" -ForegroundColor Yellow
    }
}

# 输出使用说明
Write-Host "\n===== 虚拟环境配置完成！=====" -ForegroundColor Cyan
Write-Host "使用方法："
Write-Host "1. 每次运行Python脚本前，请先激活虚拟环境："
Write-Host "   .\.venv\Scripts\Activate.ps1"
Write-Host "2. 然后可以运行您的Python脚本："
Write-Host "   python stock_analysis_workflow.py"
Write-Host "3. 完成后，可以运行以下命令退出虚拟环境："
Write-Host "   deactivate"
Write-Host "\n注意事项："
Write-Host "- 如果您使用VS Code，请确保选择了正确的Python解释器（.venv\Scripts\python.exe）" -ForegroundColor Yellow
Write-Host "- 如果直接双击运行.py文件，可能会使用系统Python而非虚拟环境中的Python" -ForegroundColor Yellow
Write-Host "- 推荐在激活虚拟环境的终端中运行Python脚本，以确保所有依赖都可用" -ForegroundColor Yellow

Read-Host "\n按Enter键退出..."