"""Tostiyk (TK) ERP —— 后端应用包。

模块划分::

    app.config      路径、常量、可注入的默认凭据
    app.database    唯一数据库引擎 / Session / 依赖注入
    app.models      全部数据表（统一 SQLModel）
    app.schemas     请求体 Pydantic 模型
    app.services    可复用业务能力（审计日志 / BCV 汇率 / PDF 报价单）
    app.routers     按业务域拆分的 HTTP 路由
    app.main        FastAPI 实例装配
"""

__version__ = "4.4.0"
