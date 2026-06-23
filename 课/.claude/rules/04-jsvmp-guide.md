---
description: JSVMP 与极难加密通用逆向指南（AI 辅助、五步法、扣代码优先）
alwaysApply: false
---

# JSVMP 与极难加密通用逆向指南

## 0. Phase 0: 智能化情报收集 (Reconnaissance)

在正式动手之前，利用 AI 进行自动化预研，识别目标网站的技术栈与常见对抗手段。

* **目标**: 确定加密特征，减少盲目调试。
* **Agent 自动化流程**:
    1. **搜索关键词**: Agent 使用 Search Tool 搜索：`"{网站域名} reverse engineering"`，`"{网站域名} jsvmp"`，`"{网站域名} signature"`。
    2. **GitHub 遍历**: 搜索 GitHub 仓库，查找相关项目的 Issue、Readme 或核心代码，提取可能涉及的加密算法（如：AES, RSA, 自定义 VM 指令集）。
    3. **指纹比对**: 自动识别目标是否使用了已知的防护方案（如：瑞数、Cloudflare, Akamai, 或常见的 JSVMP 框架），并调取对应的处理模版。
* **推荐 Prompt**: "搜索关于 {target_url} 的最新逆向技术文章或开源项目，分析其防护逻辑（如：JSVMP 还是其他），并总结该站点的加密特征。"

## 1. JSVMP 核心架构拆解

JSVMP (JavaScript Virtual Machine Protection) 的核心逻辑是将源码虚拟化为私有字节码，通过自定义虚拟机进行解释执行。

* **Bytecode**: 加密后的指令流。
* **Dispatcher**: 虚拟机的"分发器"，通常是 `switch-case` 或 `if-else` 结构。
* **Handler**: 指令集处理器（如 `OP_ADD`, `OP_PUSH`）。
* **Virtual Stack/Registers**: 运行时的内存状态空间。

## 2. 通用逆向五步法

> **核心理念**：不管多难的加密，本质都是 **插桩定位 → 扣取代码 → 补环境 → 本地复现**

### Step 1: 插桩定位加密位置

**目标**：找到生成加密参数的函数位置

**方法**：
```javascript
// 1. Hook 网络请求
const origFetch = window.fetch;
window.fetch = function(url, options) {
    if (url.includes('加密参数名')) {
        console.log('找到请求:', url);
        console.trace(); // 打印调用栈
    }
    return origFetch.apply(this, arguments);
};

// 2. Hook XHR
const origSend = XMLHttpRequest.prototype.send;
XMLHttpRequest.prototype.send = function() {
    if (this._url && this._url.includes('加密参数')) {
        console.log('XHR 请求:', this._url);
        console.trace();
    }
    return origSend.apply(this, arguments);
};

// 3. 观察调用栈，找到加密函数
// 通常在调用栈的第 3-8 层
```

**关键技巧**：
- 使用 `console.trace()` 打印完整调用栈
- 从下往上找，找到第一个业务代码（非框架代码）
- 记录文件名和函数名

### Step 2: 识别加密方法和输入输出

**分析要点**：

#### 输入数据
```javascript
// 常见输入：
- URL 路径和参数
- 时间戳 (Date.now())
- UserAgent
- Cookie (ttwid, msToken等)
- 浏览器指纹 (Canvas, WebGL, Screen)
- 随机数 (Math.random())
```

#### 加密过程
```javascript
// 常见算法：
- MD5 / SHA1 / SHA256
- HMAC (带密钥的哈希)
- AES / DES (对称加密)
- RSA (非对称加密)
- 自定义算法 (位运算、异或、查表)
- JSVMP (虚拟机保护)
```

#### 输出格式
```javascript
// 常见编码：
- Base64: ABCabc123+/=
- Hex: 0123456789abcdef
- URL编码: %20%2F%3D
- 自定义编码表
```

### Step 3: 完整扣取 JS 代码

**目标**：获取加密函数的完整代码及其所有依赖

**方法1：直接复制**
```javascript
// 1. 在 Sources 面板找到加密函数
// 2. 右键 → Copy function body
// 3. 粘贴到本地文件
// 4. 检查是否有未定义的变量/函数
// 5. 递归查找依赖，直到没有缺失
```

**方法2：使用脚本导出**
```javascript
// 在控制台执行
function exportFunction(fn) {
    console.log(fn.toString());
}

// 找到加密函数后
exportFunction(window.加密函数名);
```

**扣取 checklist**：
- [ ] 主加密函数
- [ ] 调用的子函数
- [ ] 全局变量
- [ ] 原型链方法
- [ ] 常量定义
- [ ] 加密密钥
- [ ] 字节码数据（如果是 JSVMP）

### Step 4: 本地补环境

**目标**：让扣取的代码在 Node.js 中正常运行

**核心原则**：**缺什么补什么，不要过度补环境**

#### 4.1 运行代码，观察报错

```bash
node encrypt.js

# 常见错误：
# ReferenceError: window is not defined
# ReferenceError: navigator is not defined
# TypeError: Cannot read property 'userAgent' of undefined
```

#### 4.2 使用 watch 自动发现缺失项

```javascript
// 通用 watch 函数
function watch(obj, name) {
    return new Proxy(obj, {
        get(target, prop) {
            if (!(prop in target)) {
                console.log(`❌ 缺失: ${name}.${String(prop)}`);
                return undefined;
            }
            const value = target[prop];
            if (typeof value === 'function') {
                return function(...args) {
                    console.log(`[调用] ${name}.${String(prop)}(${args.join(', ')})`);
                    return value.apply(this, args);
                };
            }
            if (value && typeof value === 'object') {
                return watch(value, `${name}.${String(prop)}`);
            }
            return value;
        }
    });
}

// 使用示例
window = watch({}, 'window');
document = watch({}, 'document');
navigator = watch({}, 'navigator');
```

#### 4.3 渐进式补全环境

```javascript
// 第1层：基础对象
if (typeof window === 'undefined') window = globalThis;
if (typeof global === 'undefined') global = window;

// 第2层：浏览器 API
if (typeof navigator === 'undefined') {
    navigator = {
        userAgent: 'Mozilla/5.0...',
        platform: 'Win32',
        language: 'zh-CN',
        // 根据报错逐步添加
    };
}

// 第3层：DOM API
if (typeof document === 'undefined') {
    document = {
        cookie: '',
        createElement: function(tag) {
            return {
                getContext: function() { return null; },
                toDataURL: function() { return ''; }
            };
        }
    };
}

// 第4层：加密库
const CryptoJS = require('crypto-js');
// 或者
const crypto = require('crypto');

// 第5层：时间函数
const _now = Date.now;
Date.now = function() {
    return 固定时间戳; // 便于调试
};
```

**补环境 checklist**：
- [ ] window / global / self
- [ ] navigator (userAgent, platform, language)
- [ ] screen (width, height, colorDepth)
- [ ] location (href, hostname, pathname)
- [ ] document (cookie, createElement)
- [ ] Canvas API (getContext, toDataURL)
- [ ] localStorage / sessionStorage
- [ ] Date / Math 函数
- [ ] btoa / atob
- [ ] 加密库 (CryptoJS / crypto)

### Step 5: 测试验证

**目标**：确保本地生成的加密参数与浏览器一致

#### 5.1 对比测试

```javascript
// 浏览器生成的值（从抓包获取）
const browserResult = '从 Network 面板复制的加密参数';

// 本地生成的值
const localResult = generateEncrypt(params);

console.log('浏览器:', browserResult);
console.log('本地:', localResult);
console.log('是否一致:', browserResult === localResult);
```

#### 5.2 Python + PyExecJS2 标准流程（推荐）

**安装依赖**：
```bash
pip install requests PyExecJS2
# PyExecJS2 是 PyExecJS 的维护版本，支持 Node.js 18+
```

**Python 测试脚本**：
```python
import requests
import execjs  # PyExecJS2
import time

def generate_sign(params):
    with open('encrypt.js', 'r', encoding='utf-8') as f:
        js_code = f.read()
    ctx = execjs.compile(js_code)
    return ctx.call('generateSign', params)

def fetch_data():
    params = {
        'offset': 0,
        'channel_id': '94349549395',
    }
    sign = generate_sign(params)
    params['sign'] = sign
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    response = requests.get('https://api.example.com/data', params=params, headers=headers)
    if response.status_code == 200:
        print('✅ 请求成功！')
        return response.json()
    else:
        print(f'❌ 请求失败: {response.status_code}')
        return None

if __name__ == '__main__':
    fetch_data()
```

## 3. AI 辅助集成方案

利用 MCP 协议，将 AI Agent 引入逆向工作流：

| 逆向阶段 | 推荐工具 | 自动化策略 |
| :--- | :--- | :--- |
| **情报收集 (Phase 0)** | Google Search, GitHub API | 自动化获取最新技术文档，快速定位加密类型。 |
| **入口感知** | `jshookmcp`, `Camoufox` | 自动注入 Hook，询问 AI 定位 Dispatcher。 |
| **字节码分析** | `JS Reverse MCP` | 直接读取字节码，要求 AI 分析 Handler 语义。 |
| **逻辑还原** | `xbsReverseSkill`, `reverse-skill` | 使用 AST 模块进行混淆恢复与代码坍缩。 |

## 4. 关键阻碍与对策

| 阻碍点 | 对策 |
| :--- | :--- |
| **Opcode 随机化** | 寻找 Dispatcher 索引映射表，确保在模拟环境映射一致。 |
| **堆栈混淆** | 绘制堆栈增长趋势图，对比还原前后的内存状态。 |
| **自修改代码** | 模拟器内加入写保护监测机制。 |

## 5. 常见加密类型及应对策略

| 加密类型 | 特征 | 逆向难度 | 应对策略 |
|---------|------|---------|---------|
| **简单混淆** | 变量名混淆，字符串加密 | ⭐⭐ | 直接脱混淆，扣代码 |
| **Webpack 打包** | 模块化，`__webpack_require__` | ⭐⭐ | 还原模块依赖 |
| **JSVMP** | 字节码，虚拟机执行 | ⭐⭐⭐⭐⭐ | 插桩分析字节码，扣代码补环境 |
| **WASM** | WebAssembly 模块 | ⭐⭐⭐⭐ | 反编译 WASM |
| **OLLVM** | 控制流平坦化 | ⭐⭐⭐⭐ | AST 分析 |
| **浏览器指纹** | 检测环境一致性 | ⭐⭐⭐ | 完整补环境 |

## 6. 实施建议

1. **情报驱动**: 优先执行 Phase 0，往往能直接找到现成的破解思路或补环境策略。
2. **扣代码优先**: 对于 JSVMP 等极难加密，**直接扣取 JS 文件 + 补环境运行**，不要尝试纯算还原（除非用户明确要求）。
3. **黑盒兜底**: 若 VM 极其复杂，优先利用 Hook 记录 I/O 映射，实现"黑盒式"纯算调用。
4. **本地部署**: 涉及敏感业务代码时，务必在本地部署开源 LLM (如 DeepSeek/Llama)，避免代码外泄。
