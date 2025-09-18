const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// 获取脚本所在目录（quant-frontend目录）
const scriptDir = path.dirname(__filename);
console.log(`脚本目录: ${scriptDir}`);

// 设置Node.js和vite.js的完整路径
const nodePath = path.resolve('C:\\Program Files\\nodejs\\node.exe');
const viteJsPath = path.join(scriptDir, 'node_modules', 'vite', 'bin', 'vite.js');

console.log('正在启动Vite开发服务器...');
console.log(`使用Node.js: ${nodePath}`);
console.log(`执行Vite: ${viteJsPath}`);

// 检查vite.js是否存在
if (!fs.existsSync(viteJsPath)) {
  console.error(`错误: 找不到vite.js文件在路径 ${viteJsPath}`);
  process.exit(1);
}

// 使用spawn启动Vite，设置cwd为quant-frontend目录
const viteProcess = spawn(nodePath, [viteJsPath], {
  stdio: 'inherit',
  cwd: scriptDir,
  shell: false // 不使用shell，避免路径解析问题
});

viteProcess.on('error', (err) => {
  console.error('启动Vite时出错:', err);
  process.exit(1);
});

viteProcess.on('close', (code) => {
  console.log(`Vite进程已退出，代码: ${code}`);
});