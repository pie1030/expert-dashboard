#!/usr/bin/env python3
"""
专家画像 Dashboard 启动脚本

使用方式：
    python run.py              # 默认 8080 端口
    python run.py --port 3000  # 指定端口
    python run.py --reload     # 开发模式（热重载）
"""

import argparse
import os
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="启动专家画像 Dashboard")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="绑定地址 (默认: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", 8080)),
        help="端口号 (默认: 8080，支持 PORT 环境变量)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="开发模式，启用热重载"
    )
    
    args = parser.parse_args()
    
    print(f"""
╔════════════════════════════════════════════════════════╗
║              专家画像 Dashboard                         ║
╠════════════════════════════════════════════════════════╣
║  启动中...                                              ║
║  地址: http://{args.host}:{args.port:<5}                         ║
║  API 文档: http://{args.host}:{args.port}/docs                   ║
║                                                        ║
║  按 Ctrl+C 停止服务                                     ║
╚════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == "__main__":
    main()
