import os
import shutil
import subprocess
import sys


# =========================
# НАСТРОЙКИ
# =========================

APP_NAME = "main_checker"
MAIN_FILE = "main_checker.py"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DIST_PATH = os.path.join(BASE_DIR, "dist")
BUILD_PATH = os.path.join(BASE_DIR, "build")
SPEC_PATH = os.path.join(BASE_DIR, "main_checker.spec")


# =========================
# ОЧИСТКА СТАРЫХ СБОРК
# =========================

def clean():
    print("🧹 Очистка старых сборок...")

    for path in [DIST_PATH, BUILD_PATH, SPEC_PATH]:
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        elif os.path.isfile(path):
            os.remove(path)


# =========================
# СБОРКА EXE
# =========================

def build():
    print("📦 Сборка приложения...")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--noconsole",
        "--name", APP_NAME,
        "--clean",
        MAIN_FILE,

        # ВАЖНО: добавляем файлы внутрь сборки
        "--add-data", f"credentials.json;.",
        "--add-data", f"config2.py;.",
        "--add-data", f"shops_config.py;.",
    ]

    hidden_imports = [
        "gspread",
        "google.oauth2",
        "google.auth",
        "requests",
        "pandas"
    ]

    for imp in hidden_imports:
        cmd += ["--hidden-import", imp]

    subprocess.run(cmd, check=True)


# =========================
# КОПИРОВАНИЕ ДОП. ФАЙЛОВ
# =========================

def copy_files():
    print("📁 Копирование дополнительных файлов...")

    dist_dir = os.path.join(DIST_PATH, APP_NAME)

    # если onefile — exe внутри dist
    if not os.path.exists(dist_dir):
        dist_dir = DIST_PATH

    files_to_copy = [
        "credentials.json",
        "config2.py"
    ]

    for file in files_to_copy:
        src = os.path.join(BASE_DIR, file)
        dst = os.path.join(dist_dir, file)

        if os.path.exists(src):
            shutil.copy(src, dst)
            print(f"✔ {file} скопирован")
        else:
            print(f"⚠ {file} не найден")


# =========================
# ЗАПУСК
# =========================

if __name__ == "__main__":
    clean()
    build()
    #copy_files()

    print("\n✅ Сборка завершена!")
    print("📂 EXE лежит в папке dist/")