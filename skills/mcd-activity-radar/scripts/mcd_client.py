"""麦当劳 MCP Streamable HTTP 客户端（纯标准库）。

只做一件事：把 JSON-RPC 请求打到 https://mcp.mcd.cn，把 result 取回来。
不依赖任何第三方库，WorkBuddy 沙箱可直接运行。
"""
import json
import os
import urllib.error
import urllib.request

DEFAULT_URL = "https://mcp.mcd.cn"
PROTOCOL_VERSION = "2025-06-18"


class MCDError(RuntimeError):
    pass


class MCDClient:
    def __init__(self, token=None, url=None, timeout=60):
        self.token = token or os.environ.get("MCD_MCP_TOKEN", "")
        if not self.token:
            raise MCDError("缺少 MCP Token：请设置环境变量 MCD_MCP_TOKEN")
        self.url = url or os.environ.get("MCD_MCP_URL", DEFAULT_URL)
        self.timeout = timeout
        self._session_id = None
        self._rid = 0

    # ---- 底层 ----
    def _post(self, payload):
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self._session_id:
            headers["mcp-session-id"] = self._session_id
        req = urllib.request.Request(self.url, data=data, headers=headers, method="POST")
        try:
            resp = urllib.request.urlopen(req, timeout=self.timeout)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:500]
            if e.code == 401:
                raise MCDError("401 Token 无效或已过期") from None
            if e.code == 429:
                raise MCDError("429 触发限流（600 次/分钟）") from None
            raise MCDError("HTTP %s: %s" % (e.code, body)) from None
        sid = resp.headers.get("mcp-session-id")
        if sid:
            self._session_id = sid
        raw = resp.read().decode("utf-8", "replace")
        if not raw.strip():
            return None  # notifications 返回 202 空体
        return self._parse(raw)

    @staticmethod
    def _parse(raw):
        last = None
        for line in raw.splitlines():
            line = line.strip()
            if line.startswith("data:"):
                line = line[5:].strip()
            if not line:
                continue
            try:
                last = json.loads(line)
            except Exception:
                continue
        if last is None:
            try:
                last = json.loads(raw)
            except Exception:
                raise MCDError("无法解析响应: %s" % raw[:200]) from None
        return last

    def _rpc(self, method, params=None):
        self._rid += 1
        body = {"jsonrpc": "2.0", "id": self._rid, "method": method}
        if params is not None:
            body["params"] = params
        r = self._post(body)
        if isinstance(r, dict) and "error" in r:
            raise MCDError("MCP 错误: %s" % json.dumps(r["error"], ensure_ascii=False))
        return r

    # ---- 生命周期 ----
    def initialize(self):
        r = self._rpc("initialize", {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "mcd-activity-radar", "version": "0.1"},
        })
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        return r

    def list_tools(self):
        r = self._rpc("tools/list", {})
        return r.get("result", {}).get("tools", [])

    # ---- 调用工具 ----
    def call(self, name, arguments=None):
        """调用一个 MCP Tool，返回 (text, structured)。

        text: 工具返回的 markdown/文本
        structured: 若工具返回 structuredContent 则为 dict，否则 None
        """
        r = self._rpc("tools/call", {"name": name, "arguments": arguments or {}})
        res = r.get("result", {})
        if res.get("isError"):
            raise MCDError("工具 %s 报错: %s" % (name, res))
        text = "\n".join(c.get("text", "") for c in res.get("content", []))
        return text, res.get("structuredContent")


def extract_json(text):
    """从「描述 + Original Response」格式的工具输出里取出真实 JSON。"""
    i = text.rfind('{"success"')
    if i < 0:
        return None
    try:
        return json.loads(text[i:])
    except Exception:
        return None
