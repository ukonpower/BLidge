"""座標変換ユーティリティ

Blender座標系(Y-up)からカスタム座標系(Z-up)への変換を提供
"""

from typing import Tuple, List
from mathutils import Vector, Euler


def convert_position(blender_position: Vector) -> List[float]:
    """位置ベクトルをBlender座標系からカスタム座標系に変換

    Args:
        blender_position: Blenderの位置ベクトル (x, y, z)

    Returns:
        カスタム座標系の位置リスト [x, z, -y]
    """
    return [
        blender_position.x,
        blender_position.z,
        -blender_position.y
    ]


def convert_rotation(blender_rotation: Euler) -> List[float]:
    """回転をBlender座標系からカスタム座標系に変換

    Args:
        blender_rotation: Blenderの回転オイラー角 (x, y, z)

    Returns:
        カスタム座標系の回転リスト [x, z, -y]
    """
    return [
        blender_rotation.x,
        blender_rotation.z,
        -blender_rotation.y
    ]


def convert_scale(blender_scale: Vector) -> List[float]:
    """スケールをBlender座標系からカスタム座標系に変換

    Args:
        blender_scale: Blenderのスケールベクトル (x, y, z)

    Returns:
        カスタム座標系のスケールリスト [x, z, y]
    """
    return [
        blender_scale.x,
        blender_scale.z,
        blender_scale.y
    ]


def convert_vector3(x: float, y: float, z: float) -> Tuple[float, float, float]:
    """3次元ベクトルをBlender座標系からカスタム座標系に変換

    Args:
        x: X座標
        y: Y座標
        z: Z座標

    Returns:
        カスタム座標系のベクトル (x, z, -y)
    """
    return (x, z, -y)


def convert_normal(blender_normal: Vector) -> List[float]:
    """法線ベクトルをBlender座標系からカスタム座標系に変換

    Args:
        blender_normal: Blenderの法線ベクトル (x, y, z)

    Returns:
        カスタム座標系の法線リスト [x, z, -y]
    """
    return [
        blender_normal[0],
        blender_normal[2],
        -blender_normal[1]
    ]
