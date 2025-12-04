"""
batch/lib内の.pyファイルをバックアップして削除するスクリプト

Cython化完了後、秘匿性を完全にするために元の.pyファイルを削除します。
削除前にバックアップを作成し、安全に処理を行います。
"""

import os
import shutil
from pathlib import Path

# プロジェクトルート
PROJECT_ROOT = Path(__file__).parent.absolute()
BATCH_LIB_DIR = PROJECT_ROOT / "batch" / "lib"
BACKUP_DIR = PROJECT_ROOT / "batch" / "lib_backup"


def backup_py_files():
    """batch/lib内の.pyファイルをバックアップ"""
    print("=" * 60)
    print("📦 batch/lib バックアップスクリプト")
    print("=" * 60)
    
    # バックアップディレクトリの作成
    if BACKUP_DIR.exists():
        print(f"\n⚠️  バックアップディレクトリが既に存在します: {BACKUP_DIR}")
        response = input("上書きしますか? (y/N): ")
        if response.lower() != 'y':
            print("❌ 処理を中止しました")
            return False
        shutil.rmtree(BACKUP_DIR)
    
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n✓ バックアップディレクトリを作成: {BACKUP_DIR}")
    
    # .pyファイルを検索
    py_files = [f for f in BATCH_LIB_DIR.glob("*.py") if f.name != "__init__.py"]
    
    if not py_files:
        print("\n⚠️  バックアップ対象の.pyファイルが見つかりません")
        return False
    
    print(f"\n📄 バックアップ対象: {len(py_files)}個のファイル\n")
    
    # バックアップ実行
    for py_file in sorted(py_files):
        backup_path = BACKUP_DIR / py_file.name
        shutil.copy2(py_file, backup_path)
        print(f"  ✓ {py_file.name}")
    
    print(f"\n✅ バックアップ完了: {BACKUP_DIR}")
    return True


def remove_py_files():
    """batch/lib内の.pyファイルを削除"""
    print("\n" + "=" * 60)
    print("🗑️  元の.pyファイルを削除")
    print("=" * 60)
    
    # .pydファイルの存在確認
    pyd_files = list(BATCH_LIB_DIR.glob("*.pyd"))
    
    if not pyd_files:
        print("\n❌ エラー: .pydファイルが見つかりません")
        print("   先にCython化を実行してください: python cythonize_batch_lib.py")
        return False
    
    print(f"\n✓ {len(pyd_files)}個の.pydファイルを確認")
    
    # .pyファイルを検索
    py_files = [f for f in BATCH_LIB_DIR.glob("*.py") if f.name != "__init__.py"]
    
    if not py_files:
        print("\n⚠️  削除対象の.pyファイルが見つかりません(既に削除済み?)")
        return True
    
    print(f"\n📄 削除対象: {len(py_files)}個のファイル\n")
    
    for py_file in sorted(py_files):
        print(f"  - {py_file.name}")
    
    print("\n⚠️  この操作は元に戻せません(Gitリポジトリからは復元可能)")
    response = input("\n削除を実行しますか? (yes/N): ")
    
    if response.lower() != 'yes':
        print("❌ 処理を中止しました")
        return False
    
    # 削除実行
    print("\n🗑️  削除中...")
    for py_file in py_files:
        py_file.unlink()
        print(f"  ✓ 削除: {py_file.name}")
    
    print("\n✅ 削除完了!")
    return True


def verify_pyd_files():
    """生成された.pydファイルを確認"""
    print("\n" + "=" * 60)
    print("🔍 .pydファイルの確認")
    print("=" * 60)
    
    pyd_files = sorted(BATCH_LIB_DIR.glob("*.pyd"))
    
    if not pyd_files:
        print("\n❌ .pydファイルが見つかりません")
        return False
    
    print(f"\n📦 生成されたバイナリファイル: {len(pyd_files)}個\n")
    
    for pyd_file in pyd_files:
        size_kb = pyd_file.stat().st_size / 1024
        print(f"  ✓ {pyd_file.name} ({size_kb:.1f} KB)")
    
    return True


def main():
    """メイン処理"""
    print("\n" + "=" * 60)
    print("🔒 batch/lib 秘匿性向上スクリプト")
    print("=" * 60)
    print("\nこのスクリプトは以下の処理を行います:")
    print("  1. batch/lib/*.py をバックアップ")
    print("  2. .pydファイルの存在確認")
    print("  3. 元の.pyファイルを削除")
    print("\n⚠️  実行前に必ずCython化を完了させてください!")
    print("   コマンド: python cythonize_batch_lib.py")
    
    response = input("\n続行しますか? (y/N): ")
    if response.lower() != 'y':
        print("\n❌ 処理を中止しました")
        return
    
    # ステップ1: バックアップ
    if not backup_py_files():
        return
    
    # ステップ2: .pydファイルの確認
    if not verify_pyd_files():
        print("\n❌ エラー: .pydファイルが見つかりません")
        print("   先にCython化を実行してください")
        return
    
    # ステップ3: .pyファイルの削除
    if remove_py_files():
        print("\n" + "=" * 60)
        print("🎉 すべての処理が完了しました!")
        print("=" * 60)
        print(f"\n✓ バックアップ: {BACKUP_DIR}")
        print(f"✓ バイナリファイル: {BATCH_LIB_DIR}/*.pyd")
        print("\n次のステップ:")
        print("  1. 動作確認: python batch/init_db.py")
        print("  2. Webアプリ起動: python app.py")


if __name__ == "__main__":
    main()
