/**
 * 文本处理工具
 */

/**
 * 截断文本到指定长度
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength);
}

/**
 * 获取选中文本，支持 iframe 内文本
 */
export function getSelectedText(): string {
  // 优先获取 iframe 内的选中文本（Readest 阅读器使用 iframe）
  const iframes = document.querySelectorAll("iframe");
  for (const iframe of iframes) {
    try {
      const iframeDoc =
        iframe.contentDocument || iframe.contentWindow?.document;
      if (iframeDoc) {
        const selection = iframeDoc.getSelection();
        if (selection && selection.toString().trim()) {
          return selection.toString().trim();
        }
      }
    } catch {
      // 跨域 iframe 无法访问
    }
  }

  // 主窗口选中文本
  const selection = window.getSelection();
  if (selection && selection.toString().trim()) {
    return selection.toString().trim();
  }

  return "";
}

/**
 * 清理 HTML，保留纯文本
 */
export function stripHtml(html: string): string {
  const div = document.createElement("div");
  div.innerHTML = html;
  return div.textContent || div.innerText || "";
}
