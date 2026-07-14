"""
OpenSearch 客户端封装
提供索引管理、文档 CRUD、全文检索能力
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk

logger = logging.getLogger(__name__)


class OpenSearchClient:
    """OpenSearch 客户端单例封装"""

    _instance: Optional["OpenSearchClient"] = None
    _client: Optional[OpenSearch] = None

    def __new__(cls) -> "OpenSearchClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def init(
        cls,
        host: str = "localhost",
        port: int = 9200,
        user: str = "admin",
        password: str = "admin",
        use_ssl: bool = False,
        verify_certs: bool = False,
    ) -> "OpenSearchClient":
        """初始化 OpenSearch 连接"""
        instance = cls()
        instance._client = OpenSearch(
            hosts=[{"host": host, "port": port}],
            http_auth=(user, password),
            use_ssl=use_ssl,
            verify_certs=verify_certs,
            scheme="https" if use_ssl else "http",
            timeout=30,
            max_retries=3,
            retry_on_timeout=True,
        )
        return instance

    @property
    def client(self) -> OpenSearch:
        if self._client is None:
            raise RuntimeError("OpenSearch 客户端未初始化，请先调用 OpenSearchClient.init()")
        return self._client

    @property
    def is_initialized(self) -> bool:
        """是否已初始化"""
        return self._client is not None

    def ping(self) -> bool:
        """检查连接是否可用"""
        try:
            return self.client.ping() if self.is_initialized else False
        except Exception:
            return False

    def create_index(self, index_name: str, mappings: Dict[str, Any]) -> bool:
        """创建索引（如不存在）"""
        try:
            if self.client.indices.exists(index=index_name):
                logger.info(f"索引 {index_name} 已存在，跳过创建")
                return True
            body = {"mappings": mappings}
            self.client.indices.create(index=index_name, body=body)
            logger.info(f"索引 {index_name} 创建成功")
            return True
        except Exception as e:
            logger.error(f"创建索引 {index_name} 失败: {e}")
            return False

    def delete_index(self, index_name: str) -> bool:
        """删除索引"""
        try:
            if self.client.indices.exists(index=index_name):
                self.client.indices.delete(index=index_name)
                logger.info(f"索引 {index_name} 已删除")
            return True
        except Exception as e:
            logger.error(f"删除索引 {index_name} 失败: {e}")
            return False

    def index_document(self, index_name: str, doc_id: str, body: Dict[str, Any]) -> bool:
        """写入单条文档"""
        try:
            self.client.index(index=index_name, id=doc_id, body=body, refresh=True)
            return True
        except Exception as e:
            logger.error(f"写入文档到 {index_name} 失败: {e}")
            return False

    def bulk_index(self, index_name: str, documents: List[Dict[str, Any]], id_field: str = "id") -> int:
        """批量写入文档，返回成功条数"""
        actions = []
        for doc in documents:
            doc_id = str(doc.get(id_field, ""))
            action = {
                "_index": index_name,
                "_id": doc_id,
                "_source": doc,
            }
            actions.append(action)
        try:
            success, errors = bulk(self.client, actions, refresh=True)
            if errors:
                logger.warning(f"批量写入部分失败: {errors}")
            return success
        except Exception as e:
            logger.error(f"批量写入 {index_name} 失败: {e}")
            return 0

    def get_document(self, index_name: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """获取单条文档"""
        try:
            result = self.client.get(index=index_name, id=doc_id)
            return result.get("_source")
        except Exception:
            return None

    def search(
        self,
        index_name: str,
        query: Dict[str, Any],
        size: int = 20,
        from_: int = 0,
        sort: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """执行搜索查询"""
        try:
            body: Dict[str, Any] = {"query": query, "size": size, "from": from_}
            if sort:
                body["sort"] = sort
            result = self.client.search(index=index_name, body=body)
            return result
        except Exception as e:
            logger.error(f"搜索 {index_name} 失败: {e}")
            return {"hits": {"hits": [], "total": {"value": 0}}}

    def parse_search_results(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析搜索结果，返回文档列表"""
        hits = result.get("hits", {}).get("hits", [])
        return [hit.get("_source", {}) | {"_score": hit.get("_score", 0)} for hit in hits]


# 岗位索引的 mapping 定义——新增 company_type 字段
JOB_INDEX_MAPPINGS = {
    "properties": {
        "id": {"type": "integer"},
        "title": {
            "type": "text",
            "analyzer": "ik_max_word",
            "search_analyzer": "ik_smart",
        },
        "company": {
            "type": "text",
            "analyzer": "ik_max_word",
            "search_analyzer": "ik_smart",
        },
        "industry": {"type": "keyword"},
        "location": {"type": "keyword"},
        "salary_range": {"type": "keyword"},
        "experience_required": {"type": "keyword"},
        "education_required": {"type": "keyword"},
        "description": {
            "type": "text",
            "analyzer": "ik_max_word",
            "search_analyzer": "ik_smart",
        },
        "requirements": {
            "type": "text",
            "analyzer": "ik_max_word",
            "search_analyzer": "ik_smart",
        },
        "skills": {"type": "keyword"},
        "company_type": {"type": "keyword"},
        "status": {"type": "keyword"},
        "source": {"type": "keyword"},
    }
}


def get_opensearch_client() -> OpenSearchClient:
    """获取 OpenSearch 客户端单例"""
    return OpenSearchClient()
