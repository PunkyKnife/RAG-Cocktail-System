import subprocess
import os
import sys
import time


def main():
    # 确定虚拟环境的基础路径，假设 .venv 位于当前工作目录
    venv_base = os.path.join(os.getcwd(), ".venv")

    # 前端命令：使用虚拟环境中的 python 来运行 http.server
    # 仍明确使用虚拟环境的python，避免使用系统python
    if sys.platform == "win32":
        venv_python_executable = os.path.join(venv_base, "Scripts", "python.exe")
    else:
        venv_python_executable = os.path.join(venv_base, "bin", "python")

    # 定义后端和前端的启动命令
    # 后端命令：直接调用系统PATH中的 'uv' 命令，它会自动检测并使用本地的 .venv
    backend_command_parts = ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

    # 前端命令：使用虚拟环境中的 python 来运行 http.server
    frontend_command_parts = [venv_python_executable, "-m", "http.server", "8000"]

    processes = []

    print("正在启动后端服务器...")
    try:
        # 启动后端进程，依赖系统 PATH 中的 'uv' 命令
        backend_process = subprocess.Popen(backend_command_parts, cwd=os.getcwd())
        processes.append(backend_process)
        print(f"后端进程已启动，PID: {backend_process.pid}")
    except FileNotFoundError:
        print(f"错误：无法找到 'uv' 命令。请确保 'uv' 已安装在您的系统 PATH 中。")
        return
    except Exception as e:
        print(f"启动后端服务器失败: {e}")
        return

    # 等待后端服务器启动，给它一些时间
    time.sleep(3)

    print("正在启动前端服务器...")
    try:
        # 启动前端进程
        frontend_process = subprocess.Popen(frontend_command_parts, cwd=os.getcwd())
        processes.append(frontend_process)
        print(f"前端进程已启动，PID: {frontend_process.pid}")
    except FileNotFoundError:
        print(f"错误：无法找到虚拟环境中的 Python 可执行文件: {venv_python_executable}。请确保您的虚拟环境完整。")
        # 如果明确的虚拟环境 Python 路径失败，尝试回退到系统 PATH 中的 'python'
        try:
            frontend_process = subprocess.Popen(["python", "-m", "http.server", "8000"], cwd=os.getcwd())
            processes.append(frontend_process)
            print(f"前端进程已启动 (回退到系统 Python)，PID: {frontend_process.pid}")
        except Exception as e_fallback:
            print(f"启动前端服务器失败 (回退)：{e_fallback}")
            # 确保在前端启动失败时终止已启动的后端进程
            for p in processes:
                if p.poll() is None: p.terminate()
            return
    except Exception as e:
        print(f"启动前端服务器失败: {e}")
        # 确保在前端启动失败时终止已启动的后端进程
        for p in processes:
            if p.poll() is None: p.terminate()
        return

    print("\n服务器已成功运行。您可以通过以下地址访问应用程序： http://localhost:8000/")
    print("按下 Ctrl+C 即可停止所有服务器。")

    try:
        # 保持主脚本运行，并监控子进程
        while True:
            for p in processes:
                if p.poll() is not None:  # 如果任一子进程意外终止
                    print(f"\n一个服务器进程 (PID: {p.pid}) 意外终止。正在退出。")
                    return  # 退出主函数
            time.sleep(1)  # 每秒检查一次
    except KeyboardInterrupt:
        print("\n检测到 Ctrl+C。正在终止所有服务器...")
    finally:
        # 确保所有子进程都被终止
        for p in processes:
            if p.poll() is None:  # 如果进程仍在运行
                print(f"正在终止进程 PID: {p.pid}...")
                p.terminate()
                try:
                    p.wait(timeout=5)  # 给进程一些时间优雅地终止
                except subprocess.TimeoutExpired:
                    print(f"进程 {p.pid} 未能优雅终止，正在强制结束。")
                    p.kill()
            print(f"进程 {p.pid} 已结束。")


if __name__ == "__main__":
    main()