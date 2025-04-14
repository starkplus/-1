import json
import re
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pandas as pd
from typing import List, Dict, Tuple, Optional

class OvarianCancerVectorSearch:
    def __init__(self, json_path: str):
        """初始化向量搜索系统
        
        Args:
            json_path: 卵巢癌数据JSON文件路径
        """
        self.data = self._load_data(json_path)
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        self.index = None
        self.preprocessed_data = []
        self.initialize_index()
        
    def _load_data(self, json_path: str) -> List[Dict]:
        """加载JSON数据"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    def preprocess_data(self) -> List[Dict]:
        """预处理数据，提取关键信息"""
        preprocessed = []
        
        for idx, item in enumerate(self.data):
            extracted_info = {
                "id": idx,
                "链接": item.get("链接", ""),
                "标题": item.get("标题", ""),
                "纳入标准": item.get("纳入标准", ""),
                "年龄": self._extract_age(item.get("纳入标准", "")),
                "病理类型": self._extract_pathology(item.get("纳入标准", "")),
                "既往治疗线数": self._extract_previous_treatment_lines(item.get("纳入标准", "")),
                "ECOG": self._extract_ecog(item.get("纳入标准", ""))
            }
            
            # 创建描述文本用于向量化
            description = (
                f"年龄: {extracted_info['年龄']} "
                f"病理类型: {extracted_info['病理类型']} "
                f"既往治疗线数: {extracted_info['既往治疗线数']} "
                f"ECOG: {extracted_info['ECOG']} "
                f"{item.get('纳入标准', '')}"
            )
            
            extracted_info["description"] = description
            preprocessed.append(extracted_info)
        
        return preprocessed
    
    def _extract_age(self, text: str) -> str:
        """提取年龄信息"""
        # 匹配常见的年龄表达方式
        patterns = [
            r'(\d+)\s*[岁周]?\s*[≤<]?\s*年龄\s*[≤<]?\s*(\d+)\s*[岁周]?',
            r'年龄\s*[：:≥>]?\s*(\d+)\s*[岁周]?',
            r'年龄\s*(\d+)[-～至]\s*(\d+)\s*[岁周]?',
            r'年龄\s*[≤<]?\s*(\d+)\s*[岁周]?',
            r'(\d+)\s*[岁周]?\s*[≤<]?\s*年龄',
            r'(\d+)\s*[-～至]\s*(\d+)\s*岁'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 2:
                    lower, upper = match.groups()
                    return f"{lower}-{upper}岁"
                else:
                    return f"{match.group(1)}岁"
        
        return "未指定"
    
    def _extract_pathology(self, text: str) -> str:
        """提取病理类型信息"""
        pathology_types = [
            "上皮性卵巢癌", "浆液性卵巢癌", "高级别浆液性卵巢癌", 
            "浆液性腺癌", "子宫内膜样卵巢癌", "粘液性卵巢癌", 
            "透明细胞癌", "输卵管癌", "原发性腹膜癌"
        ]
        
        found_types = []
        for path_type in pathology_types:
            if path_type in text:
                found_types.append(path_type)
        
        if found_types:
            return "、".join(found_types)
        
        return "未指定"
    
    def _extract_previous_treatment_lines(self, text: str) -> str:
        """提取既往治疗线数"""
        patterns = [
            r'(\d+)\s*线[以化疗上]',
            r'[接受过经历].*?(\d+)\s*线.*?[化疗方案治疗]',
            r'[治疗方案线数].*?不[超过限制].*?(\d+)\s*[线个]'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)}线"
        
        return "未指定"
    
    def _extract_ecog(self, text: str) -> str:
        """提取ECOG评分"""
        patterns = [
            r'ECOG.*?(\d+)[-～](\d+)',
            r'ECOG.*?[≤≦].*?(\d+)',
            r'PS.*?(\d+)[-～](\d+)',
            r'[体力状态评分体能状态].*?(\d+)[-～至](\d+)',
            r'ECOG.*?(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 2:
                    lower, upper = match.groups()
                    return f"{lower}-{upper}分"
                else:
                    return f"{match.group(1)}分"
                
        return "未指定"
    
    def initialize_index(self):
        """初始化faiss索引"""
        self.preprocessed_data = self.preprocess_data()
        
        # 向量化文本描述
        descriptions = [item["description"] for item in self.preprocessed_data]
        embeddings = self.model.encode(descriptions)
        
        # 创建并配置faiss索引
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        faiss.normalize_L2(embeddings)
        self.index = faiss.IndexFlatIP(dimension)  # 使用内积作为相似度度量
        self.index.add(embeddings)
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """搜索相关信息
        
        Args:
            query: 查询文本，包含年龄、病理类型、既往治疗线数、ECOG等关键词
            top_k: 返回结果数量
            
        Returns:
            匹配的记录列表
        """
        # 向量化查询
        query_vector = self.model.encode([query])
        faiss.normalize_L2(query_vector)
        
        # 搜索
        scores, indices = self.index.search(query_vector, top_k)
        
        # 返回结果
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < 0:  # faiss可能返回-1表示无结果
                continue
            
            item = self.preprocessed_data[idx]
            result = {
                "id": item["id"],
                "链接": item["链接"],
                "标题": item["标题"],
                "纳入标准": item["纳入标准"],
                "年龄": item["年龄"],
                "病理类型": item["病理类型"],
                "既往治疗线数": item["既往治疗线数"],
                "ECOG": item["ECOG"],
                "相似度": float(scores[0][i])
            }
            results.append(result)
        
        return results
    
    def create_summary_dataframe(self) -> pd.DataFrame:
        """创建数据摘要DataFrame"""
        data = []
        for item in self.preprocessed_data:
            data.append({
                "id": item["id"],
                "年龄": item["年龄"],
                "病理类型": item["病理类型"],
                "既往治疗线数": item["既往治疗线数"],
                "ECOG": item["ECOG"],
                "标题": item["标题"]
            })
        
        return pd.DataFrame(data)

# 示例使用
if __name__ == "__main__":
    json_path = "D:/AAAlearnings/新建文件夹/learning/dian/智慧医疗组/获取网页信息学习/ovarian_cancer_data.json"
    
    search_system = OvarianCancerVectorSearch(json_path)
    
    # 打印摘要信息
    df = search_system.create_summary_dataframe()
    print(df.head())
    
    # 示例查询
    query1 = "年龄50-65岁，高级别浆液性卵巢癌，2线治疗，ECOG 0-1分"
    results1 = search_system.search(query1, top_k=3)
    
    print("\n查询1结果:")
    for res in results1:
        print(f"ID: {res['id']}")
        print(f"标题: {res['标题']}")
        print(f"年龄: {res['年龄']}")
        print(f"病理类型: {res['病理类型']}")
        print(f"既往治疗线数: {res['既往治疗线数']}")
        print(f"ECOG: {res['ECOG']}")
        print(f"相似度: {res['相似度']:.4f}")
        print("-" * 50)
    
    # 另一个示例查询
    query2 = "铂耐药复发卵巢癌，ECOG 0-2分"
    results2 = search_system.search(query2, top_k=3)
    
    print("\n查询2结果:")
    for res in results2:
        print(f"ID: {res['id']}")
        print(f"标题: {res['标题']}")
        print(f"年龄: {res['年龄']}")
        print(f"病理类型: {res['病理类型']}")
        print(f"既往治疗线数: {res['既往治疗线数']}")
        print(f"ECOG: {res['ECOG']}")
        print(f"相似度: {res['相似度']:.4f}")
        print("-" * 50)