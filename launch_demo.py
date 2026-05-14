#!/usr/bin/env python
"""
Chat Demo Launcher
Khởi động toàn bộ hệ thống demo chat multi-agent
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_services():
    """Kiểm tra các services cần thiết"""
    print("🔍 Checking services...")

    # Check if Docker is running
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Docker is not running")
            return False
    except FileNotFoundError:
        print("❌ Docker is not installed")
        return False

    print("✅ Docker is running")
    return True

def start_docker_services():
    """Khởi động Docker services"""
    print("🐳 Starting Docker services...")

    try:
        # Start services in background
        subprocess.run([
            'docker-compose', '-f', 'docker/docker-compose.yml', 'up', '-d'
        ], check=True)

        print("✅ Docker services started")
        time.sleep(10)  # Wait for services to be ready
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Docker services: {e}")
        return False

def setup_database():
    """Setup Neo4j database"""
    print("🗄️ Setting up Neo4j database...")

    try:
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path.cwd())

        # Setup schema
        subprocess.run([
            sys.executable, 'scripts/setup_neo4j_schema.py'
        ], env=env, check=True)

        # Ingest data
        subprocess.run([
            sys.executable, 'scripts/ingest_data.py'
        ], env=env, check=True)

        print("✅ Database setup completed")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Database setup failed: {e}")
        return False

def start_api_server():
    """Khởi động FastAPI server"""
    print("🚀 Starting FastAPI server...")

    try:
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path.cwd())

        # Start server in background
        process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn',
            'app.main:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload'
        ], env=env)

        print("✅ FastAPI server started on http://localhost:8000")
        return process

    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def open_demo():
    """Mở chat demo trong trình duyệt"""
    print("🌐 Opening chat demo...")

    demo_path = Path.cwd() / 'chat_demo.html'
    if demo_path.exists():
        webbrowser.open(f'file://{demo_path}')
        print("✅ Chat demo opened in browser")
    else:
        print("❌ chat_demo.html not found")

def main():
    """Main launcher function"""
    print("🎯 Multi-Agent Coffee Shop Chat Demo Launcher")
    print("=" * 50)

    # Check prerequisites
    if not check_services():
        print("❌ Prerequisites not met. Please install/start required services.")
        return

    # Start Docker services
    if not start_docker_services():
        print("❌ Failed to start Docker services")
        return

    # Setup database
    if not setup_database():
        print("❌ Failed to setup database")
        return

    # Start API server
    api_process = start_api_server()
    if not api_process:
        print("❌ Failed to start API server")
        return

    # Wait a bit for server to start
    time.sleep(3)

    # Open demo
    open_demo()

    print("\n" + "=" * 50)
    print("🎉 Demo is ready!")
    print("📱 Chat interface: chat_demo.html")
    print("🔗 API endpoint: http://localhost:8000")
    print("📊 API docs: http://localhost:8000/docs")
    print("\n💡 Try these demo messages:")
    print("   • 'Wifi là gì?' (FAQ)")
    print("   • 'Các loại coffee của quán?' (Menu)")
    print("   • 'Tôi muốn đặt 2 ly latte' (Order)")
    print("\n🛑 Press Ctrl+C to stop all services")
    print("=" * 50)

    try:
        # Keep running until interrupted
        api_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")

        # Stop API server
        api_process.terminate()
        api_process.wait()

        # Stop Docker services
        try:
            subprocess.run(['docker-compose', '-f', 'docker/docker-compose.yml', 'down'])
            print("✅ Services stopped")
        except:
            pass

if __name__ == "__main__":
    main()