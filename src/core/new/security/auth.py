"""
MachineNativeOps Security Framework
安全框架 - 認證、授權、加密
"""

import hashlib
import logging
import os
import secrets
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Permission(Enum):
    """權限枚舉"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"

@dataclass
class User:
    """用戶定義"""
    id: str
    username: str
    email: str
    created_at: datetime
    password_hash: str = ""  # Hashed password stored securely
    is_active: bool = True
    password_hash: str = ""

class SecurityManager:
    """安全管理器主類"""
    
    def __init__(self):
        self.users: dict[str, User] = {}
        self.is_initialized = False
        self.security_events: list = []
    
    def _hash_password(self, password: str) -> str:
        """對密碼進行哈希處理"""
        if password is None or not password:
            raise ValueError("Password cannot be empty or None")
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """驗證密碼是否匹配哈希值"""
        if plain_password is None or hashed_password is None or not plain_password or not hashed_password:
            return False
        return pwd_context.verify(plain_password, hashed_password)
    
    async def initialize(self):
        """初始化安全管理器"""
        if self.is_initialized:
            return
        
        logger.info("🔒 初始化安全管理器")
        
        # 創建默認管理員用戶
        await self._create_default_admin()
        
        self.is_initialized = True
        logger.info("✅ 安全管理器初始化完成")
    
    async def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """認證用戶 - 使用安全的密碼哈希驗證"""
        user = None
        for u in self.users.values():
            if u.username == username and u.is_active:
                user = u
                break
        
        if not user:
            logger.warning(f"⚠️ 用戶不存在: {username}")
            return None
        
        # 使用bcrypt驗證密碼哈希
        if self._verify_password(password, user.password_hash):
            token = f"token_{secrets.token_hex(16)}"
            await self._log_security_event("user_authenticated", {
                "username": username,
                "token": token[:10]
            })
            return token
        
        logger.warning(f"⚠️ 密碼驗證失敗: {username}")
        return None
    
    async def _create_default_admin(self):
        """創建默認管理員 - 使用安全的密碼哈希"""
        if not self.users:
            # 生成安全的隨機密碼並進行哈希處理
            # 優先從環境變量讀取管理員密碼（生產環境）
            import os
            default_password = os.environ.get('ADMIN_PASSWORD')
            if not default_password:
                # 僅在開發環境生成隨機密碼
                default_password = secrets.token_urlsafe(32)
                logger.warning("⚠️ 使用隨機生成的管理員密碼（僅限開發環境）")
            else:
                logger.info("✅ 從環境變量載入管理員密碼")
            
            password_hash = self._hash_password(default_password)
            
            admin_user = User(
                id="admin_001",
                username="admin",
                email="admin@mynativeops.ai",
                created_at=datetime.now(),
                password_hash=password_hash
            )
            self.users[admin_user.id] = admin_user
            logger.info("👑 創建默認管理員用戶")
            logger.warning("⚠️ 默認管理員密碼已生成並已加密存儲")
            logger.warning("🔒 生產環境請使用 ADMIN_PASSWORD 環境變量設置密碼")
    
    async def _log_security_event(self, event_type: str, details: dict[str, Any]):
        """記錄安全事件"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        
        self.security_events.append(event)
        logger.info(f"🛡️ 安全事件: {event_type}")

# 全局安全管理器實例
security_manager = SecurityManager()