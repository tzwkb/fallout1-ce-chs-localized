#!/usr/bin/env python3
"""
统一辐射翻译器 - 优化版
Ultimate Fallout Translator - Optimized Edition

主要优化:
- 更好的错误处理和重试机制
- 智能批量大小调整
- 内存优化和性能提升
- 更友好的用户界面
- 详细的日志记录
- 配置文件支持
"""

import os
import re
import json
import time
import pickle
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
import requests
import argparse
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fallout_translator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TranslationItem:
    """翻译项数据结构 - 优化版"""
    line_number: int
    original_text: str
    prefix: str
    suffix: str
    context: str = ""
    file_path: Optional[Path] = None
    msg_id: str = ""
    needs_translation: bool = True
    priority: int = 0  # 优先级：0=普通，1=重要，2=关键
    
    def __post_init__(self):
        """后处理：计算优先级"""
        if self.is_dialog():
            self.priority = 2  # 对话最重要
        elif self.is_ui_text():
            self.priority = 1  # UI文本重要
        else:
            self.priority = 0  # 其他普通
    
    def is_dialog(self) -> bool:
        """判断是否为对话文本"""
        return "DIALOG" in str(self.file_path) if self.file_path else False
    
    def is_ui_text(self) -> bool:
        """判断是否为UI文本"""
        return any(keyword in str(self.file_path).upper() 
                  for keyword in ["PIPBOY", "MAP", "PROTO"] if self.file_path)

@dataclass
class TranslationStats:
    """翻译统计信息"""
    total_files: int = 0
    completed_files: int = 0
    total_items: int = 0
    translated_items: int = 0
    skipped_items: int = 0
    failed_items: int = 0
    start_time: float = field(default_factory=time.time)
    
    @property
    def elapsed_time(self) -> float:
        return time.time() - self.start_time
    
    @property
    def progress_percentage(self) -> float:
        return (self.completed_files / self.total_files * 100) if self.total_files > 0 else 0
    
    def format_summary(self) -> str:
        """格式化统计摘要"""
        return f"""
📊 翻译统计摘要:
   总文件: {self.total_files}
   已完成: {self.completed_files} ({self.progress_percentage:.1f}%)
   总文本项: {self.total_items}
   已翻译: {self.translated_items}
   跳过: {self.skipped_items}
   失败: {self.failed_items}
   耗时: {self.elapsed_time:.1f}秒
   平均速度: {self.translated_items/(self.elapsed_time/60):.1f} 项/分钟
"""

class SmartBatchManager:
    """智能批量管理器"""
    
    def __init__(self, initial_size: int = 15, min_size: int = 5, max_size: int = 30):
        self.current_size = initial_size
        self.min_size = min_size
        self.max_size = max_size
        self.success_count = 0
        self.failure_count = 0
        
    def adjust_batch_size(self, success: bool, response_time: float):
        """根据成功率和响应时间动态调整批量大小"""
        if success:
            self.success_count += 1
            # 成功且响应快，可以增加批量大小
            if response_time < 10 and self.current_size < self.max_size:
                self.current_size = min(self.current_size + 2, self.max_size)
        else:
            self.failure_count += 1
            # 失败或响应慢，减少批量大小
            if self.current_size > self.min_size:
                self.current_size = max(self.current_size - 3, self.min_size)
    
    def get_current_size(self) -> int:
        return self.current_size

class ConfigManager:
    """配置管理器"""
    
    DEFAULT_CONFIG = {
        "api": {
            "url": "https://api.ai-gaochao.cn/v1/chat/completions",
            "model": "gpt-4o",
            "temperature": 0.3,
            "max_tokens": 8000,
            "timeout": 60,
            "max_retries": 3
        },
        "translation": {
            "batch_size": 15,
            "batch_delay": 1.0,
            "concurrent_files": 1
        },
        "technical_content": {
            "preserve_patterns": [
                r'^[\w]+\.(exe|map|dat|txt|dll|cfg|ini)$',
                r'^(dir|exit|cd|ls|pwd|mkdir|rmdir|cls)$',
                r'^[A-Z]{3,}!*$',
                r'^[0-9][a-z]$',
                r'^[A-Z]{2,4}$',
                r'^[\\/:>\\$#]+$',
                r'^U:\\.*>$',
                r'^Zzzz+\.\.\.?$'
            ]
        }
    }
    
    def __init__(self, config_file: str = "translator_config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 合并用户配置和默认配置
                    config = self.DEFAULT_CONFIG.copy()
                    self._deep_update(config, user_config)
                    return config
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}，使用默认配置")
        
        # 创建默认配置文件
        self.save_config(self.DEFAULT_CONFIG)
        return self.DEFAULT_CONFIG.copy()
    
    def save_config(self, config: dict):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
    
    def _deep_update(self, base_dict: dict, update_dict: dict):
        """深度更新字典"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

class UnifiedFalloutTranslatorOptimized:
    """优化版统一辐射翻译器"""
    
    def __init__(self, api_key: str, source_dir: str = "ENGLISH", config_file: str = None):
        self.api_key = api_key
        self.source_dir = Path(source_dir)
        
        # 加载配置
        self.config = ConfigManager(config_file or "translator_config.json")
        
        # 进度管理
        self.progress_file = Path("unified_translation_progress.pkl")
        self.completed_files: Set[str] = set()
        self.stats = TranslationStats()
        
        # 智能批量管理
        self.batch_manager = SmartBatchManager(
            initial_size=self.config.config["translation"]["batch_size"]
        )
        
        # 支持的文件格式
        self.supported_extensions = {'.msg', '.txt', '.sve'}
        self.patterns = {
            'msg': re.compile(r'^(\{\d+\}\{\})(.+)(\})$'),
            'txt': re.compile(r'^(\d+:)(.+)$'),
            'sve': re.compile(r'^(\d+:)(.+)$'),
        }
        
        # 编译技术内容正则表达式
        self.technical_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.config.config["technical_content"]["preserve_patterns"]
        ]
        
        # 缓存
        self._translation_cache = {}
        self._file_cache = {}
        
        self.load_progress()
        logger.info("翻译器初始化完成")
    
    def load_progress(self):
        """加载翻译进度"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'rb') as f:
                    data = pickle.load(f)
                    self.completed_files = data.get('completed_files', set())
                    # 加载统计信息（如果有）
                    if 'stats' in data:
                        saved_stats = data['stats']
                        self.stats.completed_files = saved_stats.get('completed_files', 0)
                        self.stats.translated_items = saved_stats.get('translated_items', 0)
                
                logger.info(f"加载进度：已完成 {len(self.completed_files)} 个文件")
            except Exception as e:
                logger.warning(f"加载进度失败: {e}，将从头开始")
                self.completed_files = set()
        else:
            logger.info("首次运行，从头开始翻译")
    
    def save_progress(self):
        """保存翻译进度"""
        try:
            data = {
                'completed_files': self.completed_files,
                'stats': {
                    'completed_files': self.stats.completed_files,
                    'translated_items': self.stats.translated_items,
                    'timestamp': datetime.now().isoformat()
                }
            }
            with open(self.progress_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            logger.error(f"保存进度失败: {e}")
    
    def is_technical_content(self, text: str) -> bool:
        """判断是否为应该保留的技术内容"""
        text_clean = text.strip()
        return any(pattern.match(text_clean) for pattern in self.technical_patterns)
    
    def needs_translation(self, text: str) -> bool:
        """智能判断文本是否需要翻译 - 优化版"""
        # 缓存检查
        cache_key = text.strip()
        if cache_key in self._translation_cache:
            return self._translation_cache[cache_key]
        
        result = self._analyze_translation_need(text)
        self._translation_cache[cache_key] = result
        return result
    
    def _analyze_translation_need(self, text: str) -> bool:
        """分析文本是否需要翻译"""
        # 1. 空文本或纯空白
        if not text or not text.strip():
            return False
        
        # 2. 不包含英文字母
        if not re.search(r'[a-zA-Z]', text):
            return False
        
        # 3. 已包含中文（可能已翻译）
        if re.search(r'[\u4e00-\u9fff]', text):
            return False
        
        # 4. 技术内容
        if self.is_technical_content(text):
            return False
        
        # 5. 特殊格式标记
        special_markers = ['**END-PAR**', '**END-DISK**', '**DISK**']
        if text.strip() in special_markers:
            return False
        
        # 6. 纯数字或符号
        if re.match(r'^[\d\s\-_+=.,;:!?()]+$', text.strip()):
            return False
        
        return True
    
    def extract_translatable_items(self, file_path: Path, file_type: str) -> List[TranslationItem]:
        """提取文件中的可翻译项目 - 优化版"""
        # 文件缓存
        cache_key = f"{file_path}:{file_path.stat().st_mtime}"
        if cache_key in self._file_cache:
            return self._file_cache[cache_key]
        
        items = self._extract_items_from_file(file_path, file_type)
        self._file_cache[cache_key] = items
        return items
    
    def _extract_items_from_file(self, file_path: Path, file_type: str) -> List[TranslationItem]:
        """从文件中提取翻译项目"""
        if not file_path.exists():
            return []
        
        items = []
        
        try:
            # 尝试多种编码
            content = self._read_file_with_encoding(file_path)
            lines = content.splitlines()
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {e}")
            return []
        
        pattern = self.patterns.get(file_type)
        if not pattern:
            return []
        
        for i, line in enumerate(lines):
            if line.startswith('#') or not line.strip():
                continue
            
            if file_type == 'msg':
                items.extend(self._extract_msg_items(file_path, i, line))
            else:
                item = self._extract_txt_item(file_path, i + 1, line, file_type)
                if item:
                    items.append(item)
        
        return items
    
    def _read_file_with_encoding(self, file_path: Path) -> str:
        """尝试多种编码读取文件"""
        encodings = ['utf-8', 'gbk', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        raise Exception(f"无法以任何编码读取文件: {file_path}")
    
    def _extract_msg_items(self, file_path: Path, line_index: int, line: str) -> List[TranslationItem]:
        """提取MSG格式的文本项 - 优化版"""
        items = []
        msg_pattern = re.compile(r'(\{\d+\}\{\})([^}]+?)(\})')
        
        for match in msg_pattern.finditer(line):
            prefix = match.group(1)
            text = match.group(2).strip()
            suffix = match.group(3)
            
            if not text:
                continue
            
            # 提取消息ID
            id_match = re.search(r'\{(\d+)\}', prefix)
            msg_id = id_match.group(1) if id_match else "unknown"
            
            item = TranslationItem(
                line_number=line_index + 1,
                original_text=text,
                prefix=prefix,
                suffix=suffix,
                context=f"游戏消息ID: {msg_id}",
                file_path=file_path,
                msg_id=msg_id,
                needs_translation=self.needs_translation(text)
            )
            items.append(item)
        
        return items
    
    def _extract_txt_item(self, file_path: Path, line_number: int, line: str, file_type: str) -> Optional[TranslationItem]:
        """提取TXT/SVE格式的文本项"""
        pattern = self.patterns[file_type]
        match = pattern.match(line)
        
        if not match:
            return None
        
        prefix = match.group(1)
        text = match.group(2).strip()
        
        if not text:
            return None
        
        return TranslationItem(
            line_number=line_number,
            original_text=text,
            prefix=prefix,
            suffix="",
            context="游戏旁白/过场动画",
            file_path=file_path,
            msg_id=prefix.rstrip(':'),
            needs_translation=self.needs_translation(text)
        )
    
    def translate_batch_with_retry(self, items: List[TranslationItem]) -> Tuple[Dict[str, str], float]:
        """带重试机制的批量翻译"""
        start_time = time.time()
        
        # 按优先级排序
        items_sorted = sorted(items, key=lambda x: x.priority, reverse=True)
        items_to_translate = [item for item in items_sorted if item.needs_translation]
        
        if not items_to_translate:
            return {}, 0
        
        config = self.config.config["api"]
        
        # 构建翻译请求
        texts_to_translate = {}
        for i, item in enumerate(items_to_translate):
            texts_to_translate[f"text_{i}"] = item.original_text
        
        # 优化的提示词
        prompt = self._build_translation_prompt(texts_to_translate, items_to_translate[0].file_path)
        
        payload = {
            "model": config["model"],
            "messages": [
                {
                    "role": "system",
                    "content": "你是专业的游戏本地化翻译专家，特别擅长《辐射》系列游戏的翻译。请确保术语一致性和游戏氛围的准确传达。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": config["temperature"],
            "max_tokens": config["max_tokens"],
            "stream": False
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 重试机制
        for attempt in range(config["max_retries"]):
            try:
                response = requests.post(
                    config["url"], 
                    json=payload, 
                    headers=headers, 
                    timeout=config["timeout"]
                )
                
                if response.status_code == 200:
                    result = self._parse_translation_response(response)
                    if result:
                        response_time = time.time() - start_time
                        self.batch_manager.adjust_batch_size(True, response_time)
                        return result, response_time
                
                elif response.status_code == 429:
                    wait_time = (attempt + 1) * 10
                    logger.warning(f"API限流，等待 {wait_time} 秒...")
                    time.sleep(wait_time)
                    continue
                
                else:
                    logger.warning(f"API错误 {response.status_code}: {response.text[:200]}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"请求超时，重试第 {attempt + 1} 次")
            except Exception as e:
                logger.error(f"翻译请求失败: {e}")
            
            if attempt < config["max_retries"] - 1:
                time.sleep(2 ** attempt)  # 指数退避
        
        # 所有重试都失败
        response_time = time.time() - start_time
        self.batch_manager.adjust_batch_size(False, response_time)
        return {}, response_time
    
    def _build_translation_prompt(self, texts: Dict[str, str], file_path: Path) -> str:
        """构建优化的翻译提示词"""
        file_type = "对话文本" if "DIALOG" in str(file_path) else "游戏文本"
        
        return f"""请翻译以下《辐射》游戏中的{file_type}，确保：

1. 游戏术语一致性（如：变种人、避难所、废土等）
2. 保持原文语气和情感色彩
3. 符合中文表达习惯
4. 适合游戏界面显示长度

要翻译的文本：
{json.dumps(texts, ensure_ascii=False, indent=2)}

请返回JSON格式的翻译结果，键名保持不变："""
    
    def _parse_translation_response(self, response) -> Optional[Dict[str, str]]:
        """解析翻译响应"""
        try:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            
            # 清理markdown代码块
            if content.startswith('```'):
                content = re.sub(r'^```[a-z]*\n', '', content)
            if content.endswith('```'):
                content = re.sub(r'\n```$', '', content)
            
            # 解析JSON
            translation_result = json.loads(content)
            
            if isinstance(translation_result, dict):
                logger.info(f"翻译成功，处理了 {len(translation_result)} 个文本")
                return translation_result
            else:
                logger.error("翻译结果格式错误")
                return None
                
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"解析翻译响应失败: {e}")
            return None
    
    def process_file_optimized(self, file_path: Path, force_retranslate: bool = False) -> bool:
        """优化的文件处理方法"""
        # 检查是否需要处理
        if not force_retranslate and str(file_path) in self.completed_files:
            logger.info(f"跳过已完成的文件: {file_path}")
            return True
        
        file_ext = file_path.suffix.lower().lstrip('.')
        if file_ext not in self.patterns:
            return False
        
        logger.info(f"处理文件: {file_path}")
        
        # 提取翻译项目
        items = self.extract_translatable_items(file_path, file_ext)
        
        if not items:
            logger.info(f"文件无内容: {file_path}")
            return True
        
        # 统计信息
        items_needing_translation = [item for item in items if item.needs_translation]
        self.stats.total_items += len(items)
        
        if not items_needing_translation:
            logger.info(f"文件已完全翻译: {file_path} (检查了 {len(items)} 个项目)")
            self.completed_files.add(str(file_path))
            self.stats.completed_files += 1
            self.stats.skipped_items += len(items)
            self.save_progress()
            return True
        
        logger.info(f"发现 {len(items)} 个文本项，其中 {len(items_needing_translation)} 个需要翻译")
        
        # 批量翻译
        all_translations = self._translate_items_in_batches(items_needing_translation)
        
        # 应用翻译结果
        if all_translations:
            success = self._apply_translations_to_file(file_path, items, all_translations)
            if success:
                self.completed_files.add(str(file_path))
                self.stats.completed_files += 1
                self.stats.translated_items += len(all_translations)
                self.save_progress()
                logger.info(f"翻译完成: {file_path}，成功翻译 {len(all_translations)} 个文本")
                return True
        
        self.stats.failed_items += len(items_needing_translation)
        logger.error(f"翻译失败: {file_path}")
        return False
    
    def _translate_items_in_batches(self, items: List[TranslationItem]) -> Dict[str, str]:
        """分批翻译文本项"""
        all_translations = {}
        
        for i in range(0, len(items), self.batch_manager.get_current_size()):
            batch = items[i:i + self.batch_manager.get_current_size()]
            batch_num = i // self.batch_manager.get_current_size() + 1
            total_batches = (len(items) - 1) // self.batch_manager.get_current_size() + 1
            
            if total_batches > 1:
                logger.info(f"处理第 {batch_num}/{total_batches} 批 ({len(batch)} 个文本)")
            
            translations, response_time = self.translate_batch_with_retry(batch)
            
            if translations:
                # 调整键名以匹配原始索引
                for local_key, translation in translations.items():
                    if local_key.startswith('text_'):
                        local_idx = int(local_key.split('_')[1])
                        global_key = f"text_{i + local_idx}"
                        all_translations[global_key] = translation
            else:
                logger.warning(f"第 {batch_num} 批翻译失败")
            
            # 批次间延迟
            if i + self.batch_manager.get_current_size() < len(items):
                delay = self.config.config["translation"]["batch_delay"]
                time.sleep(delay)
        
        return all_translations
    
    def _apply_translations_to_file(self, file_path: Path, items: List[TranslationItem], 
                                   translations: Dict[str, str]) -> bool:
        """将翻译结果应用到文件"""
        try:
            # 读取文件
            content = self._read_file_with_encoding(file_path)
            lines = content.splitlines(keepends=True)
            
            # 创建翻译映射
            items_with_translation = []
            translation_index = 0
            
            for item in items:
                if item.needs_translation:
                    key = f"text_{translation_index}"
                    if key in translations:
                        items_with_translation.append((item, translations[key]))
                    translation_index += 1
            
            # 按行号排序，从后往前处理
            items_with_translation.sort(key=lambda x: x[0].line_number, reverse=True)
            
            # 应用翻译
            for item, translation in items_with_translation:
                line_index = item.line_number - 1
                if 0 <= line_index < len(lines):
                    original_pattern = re.escape(f"{item.prefix}{item.original_text}{item.suffix}")
                    replacement = f"{item.prefix}{translation}{item.suffix}"
                    lines[line_index] = re.sub(original_pattern, replacement, lines[line_index])
            
            # 写回文件（保持原始编码）
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True
            
        except Exception as e:
            logger.error(f"应用翻译失败 {file_path}: {e}")
            return False
    
    def scan_and_analyze_enhanced(self) -> Dict:
        """增强的扫描分析功能"""
        logger.info("开始扫描分析...")
        
        if not self.source_dir.exists():
            logger.error(f"源目录不存在: {self.source_dir}")
            return {}
        
        all_files = list(self.source_dir.rglob("*"))
        supported_files = [f for f in all_files if f.suffix.lower() in self.supported_extensions]
        
        analysis = {
            'total_files': len(supported_files),
            'completed_files': len(self.completed_files),
            'pending_files': [],
            'file_types': {},
            'priority_distribution': {'high': 0, 'medium': 0, 'low': 0},
            'estimated_items': 0
        }
        
        for file_path in supported_files:
            if str(file_path) in self.completed_files:
                continue
            
            file_ext = file_path.suffix.lower().lstrip('.')
            analysis['file_types'][file_ext] = analysis['file_types'].get(file_ext, 0) + 1
            
            items = self.extract_translatable_items(file_path, file_ext)
            items_needing = [item for item in items if item.needs_translation]
            
            if items_needing:
                analysis['pending_files'].append({
                    'path': file_path,
                    'items_count': len(items_needing),
                    'priority': max(item.priority for item in items_needing)
                })
                analysis['estimated_items'] += len(items_needing)
                
                # 优先级分布
                high_priority = sum(1 for item in items_needing if item.priority == 2)
                medium_priority = sum(1 for item in items_needing if item.priority == 1)
                low_priority = len(items_needing) - high_priority - medium_priority
                
                analysis['priority_distribution']['high'] += high_priority
                analysis['priority_distribution']['medium'] += medium_priority
                analysis['priority_distribution']['low'] += low_priority
        
        # 排序待处理文件（按优先级和项目数量）
        analysis['pending_files'].sort(key=lambda x: (x['priority'], x['items_count']), reverse=True)
        
        return analysis
    
    def display_analysis_report(self, analysis: Dict):
        """显示分析报告"""
        print(f"""
🔍 翻译项目分析报告
{'='*50}
📊 总体统计:
   支持的文件: {analysis['total_files']}
   已完成: {analysis['completed_files']} ({analysis['completed_files']/analysis['total_files']*100:.1f}%)
   待处理: {len(analysis['pending_files'])}
   预估待翻译项: {analysis['estimated_items']}

📁 文件类型分布:""")
        
        for ext, count in analysis['file_types'].items():
            print(f"   .{ext}: {count} 个文件")
        
        print(f"""
🎯 优先级分布:
   高优先级 (对话): {analysis['priority_distribution']['high']} 项
   中优先级 (UI): {analysis['priority_distribution']['medium']} 项
   低优先级 (其他): {analysis['priority_distribution']['low']} 项

📝 待处理文件 (前10个):""")
        
        for i, file_info in enumerate(analysis['pending_files'][:10]):
            priority_name = ['低', '中', '高'][file_info['priority']]
            print(f"   {i+1}. {file_info['path'].name}: {file_info['items_count']} 项 ({priority_name}优先级)")
    
    def translate_all_enhanced(self, force_retranslate: bool = False, scan_only: bool = False):
        """增强的批量翻译功能"""
        logger.info("启动统一辐射翻译器 - 优化版")
        
        if scan_only:
            analysis = self.scan_and_analyze_enhanced()
            self.display_analysis_report(analysis)
            return
        
        # 收集文件
        all_files = list(self.source_dir.rglob("*"))
        supported_files = [f for f in all_files if f.suffix.lower() in self.supported_extensions]
        
        self.stats.total_files = len(supported_files)
        
        logger.info(f"源目录: {self.source_dir}")
        logger.info(f"总文件数: {len(supported_files)}")
        logger.info(f"模式: {'强制重译' if force_retranslate else '智能增量翻译'}")
        
        if force_retranslate:
            self.completed_files.clear()
            logger.info("强制重译模式：清空进度记录")
        
        # 过滤需要处理的文件
        remaining_files = [f for f in supported_files 
                          if force_retranslate or str(f) not in self.completed_files]
        
        logger.info(f"跳过已完成: {len(supported_files) - len(remaining_files)} 个文件")
        logger.info(f"待处理: {len(remaining_files)} 个文件")
        
        if not remaining_files:
            print("🎉 所有文件都已翻译完成！")
            return
        
        # 按优先级排序文件
        def get_file_priority(file_path):
            if "DIALOG" in str(file_path):
                return 2  # 对话优先
            elif any(keyword in str(file_path).upper() for keyword in ["PIPBOY", "MAP", "PROTO"]):
                return 1  # UI其次
            return 0  # 其他最后
        
        remaining_files.sort(key=get_file_priority, reverse=True)
        
        # 处理文件
        success_count = self.stats.completed_files
        
        try:
            for i, file_path in enumerate(remaining_files, 1):
                print(f"\n📄 [{success_count + i}/{len(supported_files)}] {file_path}")
                
                try:
                    if self.process_file_optimized(file_path, force_retranslate):
                        success_count += 1
                        
                        # 显示进度
                        if i % 10 == 0 or i == len(remaining_files):
                            progress = (success_count / len(supported_files)) * 100
                            print(f"📊 当前进度: {progress:.1f}% ({success_count}/{len(supported_files)})")
                            print(f"⏱️ 平均速度: {self.stats.translated_items/(self.stats.elapsed_time/60):.1f} 项/分钟")
                
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logger.error(f"处理文件失败 {file_path}: {e}")
                    continue
        
        except KeyboardInterrupt:
            print(f"\n⏸️ 用户中断翻译")
            print(f"📋 当前进度已保存，下次运行将从断点继续")
            print(self.stats.format_summary())
            return
        
        # 完成总结
        print(f"\n🎉 翻译完成！")
        print(self.stats.format_summary())
        
        if success_count < len(supported_files):
            print(f"⚠️ 有 {len(supported_files) - success_count} 个文件处理失败")

def main():
    parser = argparse.ArgumentParser(description='统一辐射翻译器 - 优化版')
    parser.add_argument('--force', action='store_true', help='强制重新翻译所有文件')
    parser.add_argument('--scan', action='store_true', help='只扫描分析，不翻译')
    parser.add_argument('--source', default='ENGLISH', help='源文件目录')
    parser.add_argument('--api-key', help='OpenAI API密钥')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='日志级别')
    
    args = parser.parse_args()
    
    # 设置日志级别
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # 获取API密钥
    api_key = args.api_key or os.getenv('OPENAI_API_KEY')
    if not api_key and not args.scan:
        print("❌ 请通过 --api-key 参数或环境变量 OPENAI_API_KEY 提供API密钥")
        return
    
    try:
        # 创建翻译器
        translator = UnifiedFalloutTranslatorOptimized(
            api_key or "dummy", 
            args.source, 
            args.config
        )
        
        # 执行翻译
        translator.translate_all_enhanced(
            force_retranslate=args.force, 
            scan_only=args.scan
        )
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        raise

if __name__ == "__main__":
    main() 