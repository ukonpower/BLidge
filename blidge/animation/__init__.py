"""アニメーション関連モジュール"""

from .fcurve_id import get_fcurve_id, get_fcurve_prop
from .parser import AnimationParser

__all__ = [
    "get_fcurve_id",
    "get_fcurve_prop",
    "AnimationParser",
]
