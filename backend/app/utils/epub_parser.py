"""EPUB 解析器

支持标准 EPUB 2/3 格式，解析流程：
1. 通过 zipfile 打开 EPUB
2. 读取 container.xml → 定位 OPF
3. 解析 OPF → metadata / manifest / spine
4. 提取封面图片
5. 按 spine 顺序读取章节 HTML + 纯文本
6. 解析目录（NCX / nav）
"""

import os
import zipfile
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup

from app.core.exceptions import (
    FileCorruptedException,
    FileEncryptedException,
    ParseFailedException,
)

# EPUB 命名空间
NS = {
    "container": "urn:oasis:names:tc:opendocument:xmlns:container",
    "opf": "http://www.idpf.org/2007/opf",
    "dc": "http://purl.org/dc/elements/1.1/",
    "ncx": "http://www.daisy.org/z3986/2005/ncx/",
    "xhtml": "http://www.w3.org/1999/xhtml",
}


@dataclass
class BookMetadata:
    """书籍元数据"""
    title: str = ""
    author: str = ""
    publisher: Optional[str] = None
    language: str = "zh"
    isbn: Optional[str] = None
    description: Optional[str] = None


@dataclass
class ChapterData:
    """章节数据"""
    href: str
    html_content: str  # 原始 HTML
    plain_text: str  # 纯文本
    word_count: int = 0


@dataclass
class SpineItem:
    """Spine 项"""
    spine_index: int
    content_id: str
    href: str
    is_linear: bool = True


@dataclass
class TOCItem:
    """目录项"""
    spine_index: int
    content_id: str
    title: str
    sub_items: List["TOCItem"] = field(default_factory=list)


@dataclass
class EpubResult:
    """EPUB 解析结果"""
    metadata: BookMetadata
    cover_image: Optional[bytes]
    chapters: List[ChapterData]
    spine: List[SpineItem]
    toc: List[TOCItem]


class EpubParser:
    """EPUB 解析器"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.zip_file: Optional[zipfile.ZipFile] = None

    def parse(self) -> EpubResult:
        """主入口：解析 EPUB 文件"""
        try:
            self.zip_file = zipfile.ZipFile(self.file_path, "r")
        except zipfile.BadZipFile:
            raise FileCorruptedException()

        # 检测加密
        if self._is_encrypted():
            raise FileEncryptedException()

        try:
            # 1. 定位 OPF
            opf_path, opf_dir = self._get_opf_path()

            # 2. 解析 OPF
            metadata, manifest, spine = self._parse_opf(self.zip_file.read(opf_path), opf_dir)

            # 3. 提取封面
            cover_image = self._extract_cover(manifest)

            # 4. 按 spine 顺序读取章节
            chapters = self._read_chapters(spine, manifest)

            # 5. 解析目录
            toc = self._parse_toc(manifest, opf_dir)

            # 校验：至少有一个章节
            if not chapters:
                raise ParseFailedException("文件中未检测到有效章节内容")

            return EpubResult(
                metadata=metadata,
                cover_image=cover_image,
                chapters=chapters,
                spine=spine,
                toc=toc,
            )

        except FileCorruptedException:
            raise
        except FileEncryptedException:
            raise
        except ParseFailedException:
            raise
        except Exception as e:
            raise ParseFailedException(f"解析失败: {str(e)}")

        finally:
            if self.zip_file:
                self.zip_file.close()

    def _is_encrypted(self) -> bool:
        """检测 EPUB 是否加密"""
        if self.zip_file is None:
            return False
        try:
            self.zip_file.getinfo("META-INF/encryption.xml")
            return True
        except KeyError:
            return False
        except Exception:
            return False

    def _get_opf_path(self) -> Tuple[str, str]:
        """从 container.xml 获取 OPF 文件路径"""
        if self.zip_file is None:
            raise ParseFailedException("EPUB 文件未打开")

        try:
            container_xml = self.zip_file.read("META-INF/container.xml")
            root = ET.fromstring(container_xml)
            # 查找第一个 rootfile
            rootfile = root.find(".//container:rootfile", NS)
            if rootfile is None:
                raise ParseFailedException("container.xml 中未找到 rootfile 定义")
            opf_path = rootfile.get("full-path", "")
            if not opf_path:
                raise ParseFailedException("container.xml 中 rootfile 缺少 full-path 属性")
        except KeyError:
            raise FileCorruptedException("EPUB 缺少 META-INF/container.xml")
        except ET.ParseError:
            raise FileCorruptedException("container.xml 格式异常")

        opf_dir = os.path.dirname(opf_path)
        return opf_path, opf_dir

    def _resolve_href(self, href: str, opf_dir: str) -> str:
        """将 OPF 中的相对路径解析为 ZIP 内的绝对路径"""
        if href.startswith("/"):
            return href.lstrip("/")
        # 合并 OPF 目录和 href
        parts = [opf_dir, href] if opf_dir else [href]
        return "/".join(p for p in parts if p)

    def _parse_opf(
        self, opf_content: bytes, opf_dir: str
    ) -> Tuple[BookMetadata, dict, List[SpineItem]]:
        """解析 OPF 文件"""
        root = ET.fromstring(opf_content)

        # --- 解析 metadata ---
        metadata_elem = root.find("opf:metadata", NS)
        metadata = BookMetadata()

        if metadata_elem is not None:
            # 标题
            title_elem = metadata_elem.find("dc:title", NS)
            if title_elem is not None and title_elem.text:
                metadata.title = title_elem.text.strip()

            # 作者
            author_elem = metadata_elem.find("dc:creator", NS)
            if author_elem is not None and author_elem.text:
                metadata.author = author_elem.text.strip()

            # 出版社
            pub_elem = metadata_elem.find("dc:publisher", NS)
            if pub_elem is not None and pub_elem.text:
                metadata.publisher = pub_elem.text.strip()

            # 语言
            lang_elem = metadata_elem.find("dc:language", NS)
            if lang_elem is not None and lang_elem.text:
                metadata.language = lang_elem.text.strip()

            # ISBN
            for identifier in metadata_elem.findall("dc:identifier", NS):
                if identifier.text and ("isbn" in identifier.text.lower() or "urn:isbn" in identifier.text.lower()):
                    metadata.isbn = identifier.text.strip()
                    break
                elif identifier.text and "isbn" in (identifier.get("{%s}scheme" % NS["opf"], "") or "").lower():
                    metadata.isbn = identifier.text.strip()

            # 描述
            desc_elem = metadata_elem.find("dc:description", NS)
            if desc_elem is not None and desc_elem.text:
                metadata.description = desc_elem.text.strip()

        # --- 解析 manifest ---
        manifest_elem = root.find("opf:manifest", NS)
        manifest = {}
        if manifest_elem is not None:
            for item in manifest_elem.findall("opf:item", NS):
                item_id = item.get("id", "")
                href = item.get("href", "")
                media_type = item.get("media-type", "")
                # 解析相对路径
                resolved_href = self._resolve_href(href, opf_dir)
                manifest[item_id] = {
                    "href": resolved_href,
                    "media_type": media_type,
                    "id": item_id,
                }

        # --- 解析 spine ---
        spine_elem = root.find("opf:spine", NS)
        spine = []
        if spine_elem is not None:
            toc_id = spine_elem.get("toc", "")
            for index, itemref in enumerate(spine_elem.findall("opf:itemref", NS)):
                idref = itemref.get("idref", "")
                linear = itemref.get("linear", "yes").lower() == "yes"
                if idref in manifest:
                    spine.append(SpineItem(
                        spine_index=index,
                        content_id=idref,
                        href=manifest[idref]["href"],
                        is_linear=linear,
                    ))

        return metadata, manifest, spine

    def _extract_cover(self, manifest: dict) -> Optional[bytes]:
        """提取封面图片"""
        if self.zip_file is None:
            return None

        # 优先查找 cover 相关的 manifest 项
        cover_id = None
        for item_id, item in manifest.items():
            if item_id.lower() in ("cover", "cover-image", "coverimage"):
                cover_id = item_id
                break
            if "cover" in item_id.lower() and "image" in item.get("media_type", ""):
                cover_id = item_id
                break

        if cover_id and cover_id in manifest:
            try:
                return self.zip_file.read(manifest[cover_id]["href"])
            except Exception:
                pass

        return None

    def _read_chapters(self, spine: List[SpineItem], manifest: dict) -> List[ChapterData]:
        """按 spine 顺序读取所有章节内容"""
        if self.zip_file is None:
            return []

        chapters = []
        for spine_item in spine:
            try:
                content_bytes = self.zip_file.read(spine_item.href)
                # 尝试解码（自动检测编码）
                content_str = self._decode_content(content_bytes)
                # 提取纯文本
                plain_text = self._extract_plain_text(content_str)
                # 清理 HTML（保留结构）
                cleaned_html = self._clean_html(content_str)

                chapters.append(ChapterData(
                    href=spine_item.href,
                    html_content=cleaned_html,
                    plain_text=plain_text,
                    word_count=len(plain_text),
                ))
            except Exception:
                # 跳过无法读取的章节
                chapters.append(ChapterData(
                    href=spine_item.href,
                    html_content="<p>章节内容加载失败</p>",
                    plain_text="",
                    word_count=0,
                ))

        return chapters

    def _decode_content(self, content: bytes) -> str:
        """解码 HTML 内容，自动检测编码"""
        # 尝试从 XML declaration 或 meta 标签检测编码
        try:
            # 先尝试从内容中提取编码
            html_str = content.decode("utf-8", errors="ignore")
        except Exception:
            html_str = content.decode("utf-8", errors="replace")
        return html_str

    def _extract_plain_text(self, html_content: str) -> str:
        """从 HTML 中提取纯文本"""
        soup = BeautifulSoup(html_content, "lxml")
        # 移除 script 和 style
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        # 清理空白
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return "\n".join(lines)

    def _clean_html(self, html_content: str) -> str:
        """清洗 HTML，保留结构但移除危险标签"""
        soup = BeautifulSoup(html_content, "lxml")
        # 移除 script、style、iframe、object、embed
        for tag in soup(["script", "style", "noscript", "iframe", "object", "embed"]):
            tag.decompose()
        return str(soup.body) if soup.body else str(soup)

    def _parse_toc(self, manifest: dict, opf_dir: str) -> List[TOCItem]:
        """解析目录（NCX / nav）"""
        if self.zip_file is None:
            return []

        # 尝试解析 NCX
        for item_id, item in manifest.items():
            if "ncx" in item.get("media_type", "").lower() or item_id.lower() == "ncx":
                try:
                    ncx_content = self.zip_file.read(item["href"])
                    return self._parse_ncx(ncx_content)
                except Exception:
                    break

        # 尝试解析 nav (EPUB 3)
        for item_id, item in manifest.items():
            if "nav" in item.get("id", "").lower() or "nav" in item.get("properties", ""):
                try:
                    nav_content = self.zip_file.read(item["href"])
                    return self._parse_nav(nav_content)
                except Exception:
                    break

        # 从 spine 自动生成简单目录
        return [TOCItem(spine_index=i, content_id=item.id, title=f"第{i+1}章")
                for i, item in enumerate(self._get_spine_items())]

    def _get_spine_items(self):
        """获取 spine 项列表（内部辅助）"""
        return []

    def _parse_ncx(self, ncx_content: bytes) -> List[TOCItem]:
        """解析 NCX 目录"""
        try:
            root = ET.fromstring(ncx_content)
        except ET.ParseError:
            return []

        items = []
        nav_map = root.find(".//ncx:navMap", NS)
        if nav_map is None:
            return []

        for idx, nav_point in enumerate(nav_map.findall("ncx:navPoint", NS)):
            item = self._parse_ncx_point(nav_point, idx)
            if item:
                items.append(item)

        return items

    def _parse_ncx_point(self, nav_point: ET.Element, index: int) -> Optional[TOCItem]:
        """解析单个 NCX navPoint"""
        label = nav_point.find(".//ncx:navLabel/ncx:text", NS)
        content = nav_point.find("ncx:content", NS)

        title = label.text.strip() if label is not None and label.text else f"章节{index + 1}"
        href = content.get("src", "") if content is not None else ""

        item = TOCItem(
            spine_index=index,
            content_id=item_id_from_href(href),
            title=title,
        )

        # 解析子项
        for child in nav_point.findall("ncx:navPoint", NS):
            child_item = self._parse_ncx_point(child, index)
            if child_item:
                item.sub_items.append(child_item)

        return item

    def _parse_nav(self, nav_content: bytes) -> List[TOCItem]:
        """解析 EPUB 3 nav 目录"""
        try:
            root = ET.fromstring(nav_content)
        except ET.ParseError:
            return []

        items = []
        # 查找 nav 元素
        for nav in root.findall(".//xhtml:nav", NS):
            ol = nav.find("xhtml:ol", NS)
            if ol is not None:
                items = self._parse_nav_list(ol)
                break

        return items

    def _parse_nav_list(self, ol: ET.Element, depth: int = 0) -> List[TOCItem]:
        """递归解析 nav 列表"""
        items = []
        for idx, li in enumerate(ol.findall("xhtml:li", NS)):
            a = li.find("xhtml:a", NS)
            title = ""
            href = ""
            if a is not None:
                title = "".join(a.itertext()).strip()
                href = a.get("href", "")

            item = TOCItem(
                spine_index=idx,
                content_id=item_id_from_href(href),
                title=title or f"章节{idx + 1}",
            )

            # 递归解析子列表
            child_ol = li.find("xhtml:ol", NS)
            if child_ol is not None:
                item.sub_items = self._parse_nav_list(child_ol, depth + 1)

            items.append(item)

        return items


def item_id_from_href(href: str) -> str:
    """从 href 提取 content_id"""
    # 移除外部的 #fragment
    href = href.split("#")[0] if "#" in href else href
    # 取文件名（不含路径和扩展名）
    basename = os.path.basename(href)
    name, _ = os.path.splitext(basename)
    return name
