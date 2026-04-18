#!/usr/bin/env python3
"""
UTF8转GBK编码转换脚本
将翻译后的文件从UTF8编码转换为GBK编码，以便游戏正确显示中文
"""

import os
import shutil
from pathlib import Path
import chardet

class UTF8ToGBKConverter:
    def __init__(self, source_dir="ENGLISH", backup_dir="ENGLISH_UTF8_BACKUP"):
        self.source_dir = Path(source_dir)
        self.backup_dir = Path(backup_dir)
        
        # 支持的文件扩展名
        self.supported_extensions = {'.msg', '.txt', '.sve'}
        
    def detect_encoding(self, file_path):
        """检测文件编码"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                return result['encoding']
        except Exception as e:
            print(f"  ❌ 编码检测失败: {e}")
            return None
    
    def backup_original_files(self):
        """备份原始UTF8文件"""
        if self.backup_dir.exists():
            print(f"📁 备份目录已存在: {self.backup_dir}")
            response = input("是否覆盖现有备份？(y/N): ")
            if response.lower() != 'y':
                print("❌ 取消备份，程序退出")
                return False
            shutil.rmtree(self.backup_dir)
        
        print(f"📋 创建备份: {self.source_dir} -> {self.backup_dir}")
        shutil.copytree(self.source_dir, self.backup_dir)
        print("✅ 备份完成")
        return True
    
    def convert_file(self, file_path):
        """转换单个文件从UTF8到GBK"""
        try:
            # 检测当前编码
            current_encoding = self.detect_encoding(file_path)
            
            if current_encoding and current_encoding.lower() in ['gb2312', 'gbk', 'gb18030']:
                print(f"  ⏭️ 已是GBK编码，跳过")
                return True
                
            # 读取UTF8文件
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # 如果UTF8读取失败，尝试其他编码
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    print(f"  ⚠️ UTF8读取有问题，使用ignore模式")
            
            # 检查是否包含中文
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in content)
            
            if not has_chinese:
                print(f"  📄 无中文内容，保持原编码")
                return True
            
            # 转换为GBK编码
            try:
                with open(file_path, 'w', encoding='gbk') as f:
                    f.write(content)
                print(f"  ✅ 转换成功: UTF8 -> GBK")
                return True
                
            except UnicodeEncodeError as e:
                print(f"  ❌ GBK编码失败: {e}")
                print(f"  💡 可能包含GBK不支持的字符")
                
                # 尝试使用错误处理模式
                try:
                    with open(file_path, 'w', encoding='gbk', errors='replace') as f:
                        f.write(content)
                    print(f"  ⚠️ 使用replace模式转换完成")
                    return True
                except Exception as e2:
                    print(f"  ❌ 转换彻底失败: {e2}")
                    return False
                    
        except Exception as e:
            print(f"  ❌ 处理文件失败: {e}")
            return False
    
    def convert_all_files(self):
        """转换所有支持的文件"""
        if not self.source_dir.exists():
            print(f"❌ 源目录不存在: {self.source_dir}")
            return
        
        # 收集所有需要转换的文件
        files_to_convert = []
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in self.supported_extensions:
                    files_to_convert.append(file_path)
        
        if not files_to_convert:
            print(f"❌ 在 {self.source_dir} 中没有找到支持的文件")
            return
        
        print(f"📋 找到 {len(files_to_convert)} 个文件需要转换")
        print(f"📁 源目录: {self.source_dir}")
        print(f"📂 支持格式: {', '.join(self.supported_extensions)}")
        
        # 确认转换
        response = input(f"\n是否开始转换？(y/N): ")
        if response.lower() != 'y':
            print("❌ 用户取消转换")
            return
        
        # 备份原文件
        if not self.backup_original_files():
            return
        
        # 执行转换
        success_count = 0
        print(f"\n🔄 开始转换文件...")
        
        for i, file_path in enumerate(files_to_convert, 1):
            relative_path = file_path.relative_to(self.source_dir)
            print(f"\n[{i}/{len(files_to_convert)}] {relative_path}")
            
            if self.convert_file(file_path):
                success_count += 1
            
        print(f"\n🎉 转换完成！")
        print(f"✅ 成功: {success_count}/{len(files_to_convert)} 个文件")
        print(f"📁 备份位置: {self.backup_dir}")
        
        if success_count < len(files_to_convert):
            print(f"⚠️ 有 {len(files_to_convert) - success_count} 个文件转换失败，请检查日志")

def main():
    print("🔄 UTF8转GBK编码转换工具")
    print("=" * 50)
    
    converter = UTF8ToGBKConverter()
    converter.convert_all_files()

if __name__ == "__main__":
    main() 