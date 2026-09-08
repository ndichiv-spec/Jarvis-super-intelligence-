"""
Core AI Engine - Base abstraction for all AI processing.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class EngineType(Enum):
    """AI Engine types."""
    LLM = "llm"
    VISION = "vision"
    AUDIO = "audio"
    REASONING = "reasoning"
    MULTIMODAL = "multimodal"
    CUSTOM = "custom"


@dataclass
class EngineConfig:
    """Engine configuration."""
    name: str
    engine_type: EngineType
    enabled: bool = True
    max_workers: int = 8
    timeout: float = 30.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngineRequest:
    """Engine request."""
    task_id: str
    task_type: str
    input_data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngineResponse:
    """Engine response."""
    task_id: str
    status: str
    output_data: Dict[str, Any]
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AIEngine(ABC):
    """Base AI Engine abstract class."""
    
    def __init__(self, config: EngineConfig):
        """Initialize engine."""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{config.name}")
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize engine."""
        if self._initialized:
            return True
        
        self.logger.info(f"Initializing {self.config.name}...")
        try:
            result = await self._setup()
            self._initialized = result
            return result
        except Exception as e:
            self.logger.error(f"Failed to initialize: {e}")
            return False
    
    @abstractmethod
    async def _setup(self) -> bool:
        """Setup engine resources."""
        pass
    
    @abstractmethod
    async def process(self, request: EngineRequest) -> EngineResponse:
        """Process request."""
        pass
    
    async def shutdown(self) -> bool:
        """Shutdown engine."""
        self.logger.info(f"Shutting down {self.config.name}...")
        try:
            result = await self._cleanup()
            self._initialized = False
            return result
        except Exception as e:
            self.logger.error(f"Failed to shutdown: {e}")
            return False
    
    @abstractmethod
    async def _cleanup(self) -> bool:
        """Cleanup engine resources."""
        pass
    
    def is_initialized(self) -> bool:
        """Check if engine is initialized."""
        return self._initialized
