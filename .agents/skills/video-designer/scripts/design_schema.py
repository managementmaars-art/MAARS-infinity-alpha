from typing import Any, Annotated, Dict, List, Literal, Optional, Union
from enum import Enum
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    ConfigDict
)
import re


# ============================================================================
# ENUMS
# ============================================================================

class ElementType(str, Enum):
    """Valid element types in the design schema (from skill documentation)."""
    TEXT = "text"
    SHAPE = "shape"
    PATH = "path"
    # Non-documented types found in real data:
    ASSET = "asset"  # Treated same as shape (width/height, optional assetPath)
    PATTERN = "pattern"  # Treated same as shape


class PathType(str, Enum):
    """Valid path types for path elements."""
    LINEAR = "linear"
    ARC = "arc"
    BEZIER = "bezier"
    BOUNCE = "bounce"
    CIRCULAR = "circular"
    ELLIPTICAL = "elliptical"
    PARABOLIC = "parabolic"
    S_CURVE = "s_curve"
    SINE_WAVE = "sine_wave"
    SPIRAL = "spiral"
    SPLINE = "spline"
    ZIGZAG = "zigzag"


class TextAlign(str, Enum):
    """Valid text alignment values."""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class BackgroundType(str, Enum):
    """Valid background types for text containers."""
    NONE = "none"
    SOLID = "solid"
    GRADIENT = "gradient"
    FROSTED_GLASS = "frosted-glass"
    HIGHLIGHT = "highlight"


class GradientDirection(str, Enum):
    """Valid gradient directions."""
    TO_RIGHT = "to-right"
    TO_LEFT = "to-left"
    TO_BOTTOM = "to-bottom"
    TO_TOP = "to-top"
    TO_BR = "to-br"
    TO_BL = "to-bl"


class BackdropBlur(str, Enum):
    """Valid backdrop blur sizes."""
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"


class ArrowMarker(str, Enum):
    """Valid arrow marker types for paths."""
    HOLLOW = "hollow"
    FILL = "fill"
    LINE = "line"


# ============================================================================
# UTILITY VALIDATORS
# ============================================================================

def validate_hex_color(value: str) -> str:
    """Validate hex color format (#RGB or #RRGGBB)."""
    if value == "none":
        return value
    if not re.match(r"^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$", value):
        raise ValueError(
            f"Invalid color format '{value}'. Expected hex format like '#FFFFFF' or '#FFF'"
        )
    return value


def validate_viewport_size(value: str) -> str:
    """Validate viewport size format (WIDTHxHEIGHT)."""
    if not re.match(r"^\d+x\d+$", value):
        raise ValueError(
            f"Invalid viewport_size format '{value}'. Expected 'WIDTHxHEIGHT' (e.g., '1080x1920')"
        )
    return value


# ============================================================================
# NESTED MODELS (Bottom-up approach)
# ============================================================================

class LayoutModel(BaseModel):
    """Layout configuration for video metadata."""
    strategy: str = Field(..., description="Layout strategy for the scene")

    model_config = ConfigDict(extra='forbid')


class VideoMetadataModel(BaseModel):
    """Video metadata including viewport, background, and layout."""
    viewport_size: str = Field(..., description="Viewport dimensions in WIDTHxHEIGHT format")
    backgroundColor: str = Field(..., description="Background color in hex format")
    layout: LayoutModel = Field(..., description="Layout configuration")

    model_config = ConfigDict(extra='forbid')

    @field_validator('viewport_size')
    @classmethod
    def validate_viewport_format(cls, v: str) -> str:
        return validate_viewport_size(v)

    @field_validator('backgroundColor')
    @classmethod
    def validate_bg_color(cls, v: str) -> str:
        return validate_hex_color(v)


class GradientModel(BaseModel):
    """Gradient configuration for backgrounds."""
    from_: str = Field(..., alias="from", description="Start color in hex format")
    to: str = Field(..., description="End color in hex format")
    direction: Optional[GradientDirection] = Field(None, description="Gradient direction")

    model_config = ConfigDict(extra='forbid', populate_by_name=True)

    @field_validator('from_', 'to')
    @classmethod
    def validate_gradient_colors(cls, v: str) -> str:
        return validate_hex_color(v)


class BackgroundModel(BaseModel):
    """Background configuration for text containers."""
    type: BackgroundType = Field(..., description="Background type")
    color: Optional[str] = Field(None, description="Background color in hex format")
    opacity: Optional[float] = Field(None, ge=0, le=1, description="Background opacity (0-1)")
    gradient: Optional[GradientModel] = Field(None, description="Gradient configuration (required if type is gradient)")

    model_config = ConfigDict(extra='forbid')

    @field_validator('color')
    @classmethod
    def validate_color_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_hex_color(v)

    @model_validator(mode='after')
    def validate_gradient_required(self):
        """Ensure gradient is present when type is gradient."""
        if self.type == BackgroundType.GRADIENT and self.gradient is None:
            raise ValueError("Field 'gradient' is required when background type is 'gradient'")
        return self


class BorderModel(BaseModel):
    """Border configuration for text containers."""
    radius: Optional[float] = Field(None, ge=0, description="Border radius")
    width: Optional[float] = Field(None, ge=0, description="Border width")
    color: Optional[str] = Field(None, description="Border color in hex format")

    model_config = ConfigDict(extra='forbid')

    @field_validator('color')
    @classmethod
    def validate_color_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_hex_color(v)


class ContainerModel(BaseModel):
    """Container configuration for text elements."""
    padding: float = Field(..., ge=0, description="Container padding")
    background: BackgroundModel = Field(..., description="Background configuration")
    border: Optional[BorderModel] = Field(None, description="Border configuration")
    backdropBlur: Optional[BackdropBlur] = Field(None, description="Backdrop blur size (required if background type is frosted-glass)")

    model_config = ConfigDict(extra='forbid')

    @model_validator(mode='after')
    def validate_backdrop_blur(self):
        """Ensure backdropBlur is present when background type is frosted-glass."""
        if self.background.type == BackgroundType.FROSTED_GLASS and self.backdropBlur is None:
            raise ValueError("Field 'backdropBlur' is required when background type is 'frosted-glass'")
        return self


# ============================================================================
# ANIMATION MODELS
# ============================================================================

class AnimationConfigModel(BaseModel):
    """Animation configuration for entrance/exit animations."""
    type: str = Field(..., description="Animation type (handled by video-coder)")
    duration: float = Field(..., ge=0, description="Animation duration in milliseconds (0 for instant transitions like 'cut')")
    easing: Optional[str] = Field(None, description="Easing function (e.g., 'linear', 'easeInOut'). Must match follow-path easing when syncing path-draw with object movement.")

    model_config = ConfigDict(extra='forbid')


class FollowPathAction(BaseModel):
    """Follow-path animation action for moving elements along a path."""
    type: Literal["follow-path"] = Field(..., description="Action type for path following")
    pathId: str = Field(..., description="ID of the path element to follow")
    autoRotate: Optional[bool] = Field(True, description="Rotate element to face direction of travel")
    on: float = Field(..., description="Timestamp when action starts (absolute video time)")
    duration: float = Field(..., ge=0, description="Action duration in milliseconds (0 for instant transitions)")
    easing: Optional[str] = Field(None, description="Easing function")

    model_config = ConfigDict(extra='forbid')


class PropertyAction(BaseModel):
    """Property animation action for changing element properties over time."""
    targetProperty: str = Field(..., description="Property to animate (opacity, scale, x, y, rotation, etc.)")
    value: Any = Field(..., description="Target value for the property")
    on: float = Field(..., description="Timestamp when action starts (absolute video time)")
    duration: float = Field(..., ge=0, description="Action duration in milliseconds (0 for instant transitions)")
    easing: Optional[str] = Field(None, description="Easing function")

    model_config = ConfigDict(extra='forbid')


# Union type for animation actions - supports both follow-path and property animations
# Pydantic will try FollowPathAction first (checks for 'type' field), then PropertyAction
AnimationActionModel = Union[FollowPathAction, PropertyAction]


class AnimationModel(BaseModel):
    """Complete animation configuration for an element."""
    entrance: Optional[AnimationConfigModel] = Field(None, description="Entrance animation")
    exit: Optional[AnimationConfigModel] = Field(None, description="Exit animation")
    actions: Optional[List[AnimationActionModel]] = Field(None, description="Timeline actions")

    model_config = ConfigDict(extra='forbid')


# ============================================================================
# INSTANCE MODELS
# ============================================================================

class InstanceModel(BaseModel):
    """Instance configuration for creating multiple variations of an element."""
    useDefaults: Optional[bool] = Field(None, description="Use default values from parent (first instance only)")
    x: Optional[float] = Field(None, description="X position override")
    y: Optional[float] = Field(None, description="Y position override")

    model_config = ConfigDict(extra='allow')  # Allow additional fields for other overrides


# ============================================================================
# PATH PARAMETER MODELS
# ============================================================================

class LinearPathParams(BaseModel):
    """Parameters for linear path type."""
    type: Literal[PathType.LINEAR] = PathType.LINEAR
    start_x: float = Field(..., description="Starting X coordinate")
    start_y: float = Field(..., description="Starting Y coordinate")
    end_x: float = Field(..., description="Ending X coordinate")
    end_y: float = Field(..., description="Ending Y coordinate")
    instances: Optional[List[InstanceModel]] = Field(None, description="Multiple path instances")

    model_config = ConfigDict(extra='forbid')


class ArcPathParams(BaseModel):
    """Parameters for arc path type."""
    type: Literal[PathType.ARC] = PathType.ARC
    start_x: float = Field(..., description="Starting X coordinate")
    start_y: float = Field(..., description="Starting Y coordinate")
    end_x: float = Field(..., description="Ending X coordinate")
    end_y: float = Field(..., description="Ending Y coordinate")
    radius: float = Field(..., description="Arc radius")
    sweep: Optional[int] = Field(1, ge=0, le=1, description="Sweep direction: 1 for clockwise, 0 for counter-clockwise (default 1)")
    large_arc: Optional[int] = Field(0, ge=0, le=1, description="Large arc flag: 1 for arc > 180°, 0 for arc < 180° (default 0)")
    instances: Optional[List[InstanceModel]] = Field(None, description="Multiple path instances")

    model_config = ConfigDict(extra='forbid')


class BezierPathParams(BaseModel):
    """Parameters for bezier path type."""
    type: Literal[PathType.BEZIER] = PathType.BEZIER
    start_x: float = Field(..., description="Starting X coordinate")
    start_y: float = Field(..., description="Starting Y coordinate")
    cp1_x: float = Field(..., description="Control point 1 X coordinate")
    cp1_y: float = Field(..., description="Control point 1 Y coordinate")
    cp2_x: float = Field(..., description="Control point 2 X coordinate")
    cp2_y: float = Field(..., description="Control point 2 Y coordinate")
    end_x: float = Field(..., description="Ending X coordinate")
    end_y: float = Field(..., description="Ending Y coordinate")
    instances: Optional[List[InstanceModel]] = Field(None, description="Multiple path instances")

    model_config = ConfigDict(extra='forbid')


class BouncePathParams(BaseModel):
    """Parameters for bounce path type."""
    type: Literal[PathType.BOUNCE] = PathType.BOUNCE
    start_x: float = Field(..., description="Starting X coordinate")
    start_y: float = Field(..., description="Starting Y coordinate")
    end_x: float = Field(..., description="Ending X coordinate")
    ground_y: float = Field(..., description="Ground level Y coordinate")
    initial_height: float = Field(..., description="Initial bounce height")
    bounces: float = Field(..., description="Number of bounces")
    decay: Optional[float] = Field(0.6, gt=0, le=1, description="Height reduction factor per bounce (default 0.6)")
    instances: Optional[List[InstanceModel]] = Field(None, description="Multiple path instances")

    model_config = ConfigDict(extra='forbid')


class CircularPathParams(BaseModel):
    """Parameters for circular path type."""
    type: Literal[PathType.CIRCULAR] = PathType.CIRCULAR
    center_x: float = Field(..., description="Center X coordinate")
    center_y: float = Field(..., description="Center Y coordinate")
    radius: float = Field(..., description="Circle radius")
    instances: Optional[List[InstanceModel]] = Field(None, description="Multiple path instances")

    model_config = ConfigDict(extra='forbid')


class EllipticalPathParams(BaseModel):
    """Parameters for elliptical path type."""
    type: Literal[PathType.ELLIPTICAL] = PathType.ELLIPTICAL
    center_x: float = Field(..., description="Center X coordinate")
    center_y: float = Field(..., description="Center Y coordinate")
    radius_x: float = Field(..., description="Horizontal radius")
    radius_y: float = Field(..., description="Vertical radius")
    instances: Optional[List[InstanceModel]] = Field(None, description="Multiple path instances")

    model_config = ConfigDict(extra='forbid')


class ParabolicPathParams(BaseModel):
    """Parameters for parabolic path type."""
    type: Literal[PathType.PARABOLIC] = PathType.PARABOLIC
    start_x: float = Field(..., description="Starting X coordinate")
    start_y: float = Field(..., description="Starting Y coordinate")
    end_x: float = Field(..., description="Ending X coordinate")
    end_y: float = Field(..., description="Ending Y coordinate")
    arc_height: float = Field(..., description="Arc height")
    instances: Optional[List[InstanceModel]] = Field(None, description="Multiple path instances")

    model_config = ConfigDict(extra='forbid')


class SCurvePathParams(BaseModel):
    """Parameters for S-curve path type."""
    type: Literal[PathType.S_CURVE] = PathType.S_CURVE
    start_x: float = Field(..., description="Starting X coordinate")
    start_y: float = Field(..., description="Starting Y coordinate")
    end_x: float = Field(..., description="Ending X coordinate")
    end_y: float = Field(..., description="Ending Y coordinate")
    curvature: Optional[float] = Field(0.5, ge=0, le=1, description="Bend intensity, range 0-1 (default 0.5)")
    instances: Optional[List[InstanceModel]] = Field(None, description="Multiple path instances")

    model_config = ConfigDict(extra='forbid')


class SineWavePathParams(BaseModel):
    """Parameters for sine wave path type."""
    type: Literal[PathType.SINE_WAVE] = PathType.SINE_WAVE
    start_x: float = Field(..., description="Starting X coordinate")
    start_y: float = Field(..., description="Starting Y coordinate")
    end_x: float = Field(..., description="Ending X coordinate")
    end_y: float = Field(..., description="Ending Y coordinate")
    amplitude: float = Field(..., description="Wave amplitude (perpendicular to direction)")
    cycles: int = Field(..., description="Number of complete wave cycles")
    instances: Optional[List[InstanceModel]] = Field(None, description="Multiple path instances")

    model_config = ConfigDict(extra='forbid')


class SpiralPathParams(BaseModel):
    """Parameters for spiral path type."""
    type: Literal[PathType.SPIRAL] = PathType.SPIRAL
    center_x: float = Field(..., description="Center X coordinate")
    center_y: float = Field(..., description="Center Y coordinate")
    max_radius: float = Field(..., description="Maximum spiral radius")
    revolutions: float = Field(..., description="Number of revolutions")
    points: Optional[int] = Field(100, gt=0, description="Number of points for smoothness (default 100)")
    instances: Optional[List[InstanceModel]] = Field(None, description="Multiple path instances")

    model_config = ConfigDict(extra='forbid')


class SplinePathParams(BaseModel):
    """Parameters for spline path type."""
    type: Literal[PathType.SPLINE] = PathType.SPLINE
    points: List[List[float]] = Field(..., min_length=2, description="Array of [x, y] coordinate pairs")
    tension: Optional[float] = Field(0.3, ge=0, le=1, description="Controls curve tightness, 0-1 (default 0.3)")
    instances: Optional[List[InstanceModel]] = Field(None, description="Multiple path instances")

    model_config = ConfigDict(extra='forbid')

    @field_validator('points')
    @classmethod
    def validate_points(cls, v: List[List[float]]) -> List[List[float]]:
        """Ensure each point is a valid [x, y] pair."""
        for i, point in enumerate(v):
            if not isinstance(point, list) or len(point) != 2:
                raise ValueError(f"Point at index {i} must be an array of [x, y] coordinates")
            if not all(isinstance(coord, (int, float)) for coord in point):
                raise ValueError(f"Point at index {i} coordinates must be numbers")
        return v


class ZigzagPathParams(BaseModel):
    """Parameters for zigzag path type."""
    type: Literal[PathType.ZIGZAG] = PathType.ZIGZAG
    start_x: float = Field(..., description="Starting X coordinate")
    start_y: float = Field(..., description="Starting Y coordinate")
    end_x: float = Field(..., description="Ending X coordinate")
    end_y: float = Field(..., description="Ending Y coordinate")
    amplitude: float = Field(..., description="Zigzag amplitude (perpendicular to direction)")
    segments: int = Field(..., description="Number of zigzag segments")
    instances: Optional[List[InstanceModel]] = Field(None, description="Multiple path instances")

    model_config = ConfigDict(extra='forbid')


# Union of all path parameter types
PathParamsUnion = Union[
    LinearPathParams, ArcPathParams, BezierPathParams, BouncePathParams,
    CircularPathParams, EllipticalPathParams, ParabolicPathParams,
    SCurvePathParams, SineWavePathParams, SpiralPathParams,
    SplinePathParams, ZigzagPathParams
]


# ============================================================================
# BASE ELEMENT MODEL
# ============================================================================

class BaseElementModel(BaseModel):
    """Base model with common fields for all element types."""
    id: str = Field(..., description="Unique element identifier")
    type: ElementType = Field(..., description="Element type")
    content: str = Field(..., description="Description of the element's visual appearance")
    enterOn: int = Field(..., description="Timestamp when element enters (absolute video time)")
    exitOn: int = Field(..., description="Timestamp when element exits (absolute video time)")
    x: Optional[float] = Field(None, description="X position (optional for path elements or when using instances)")
    y: Optional[float] = Field(None, description="Y position (optional for path elements or when using instances)")
    zIndex: int = Field(..., description="Z-index for layering")
    rotation: Optional[float] = Field(None, description="Rotation in degrees")
    scale: Optional[float] = Field(None, gt=0, description="Scale factor")
    opacity: Optional[float] = Field(None, ge=0, le=1, description="Opacity (0-1)")
    fill: Optional[str] = Field(None, description="Fill color in hex format or 'none'")
    stroke: Optional[str] = Field(None, description="Stroke color in hex format or 'none'")
    strokeWidth: Optional[float] = Field(None, ge=0, description="Stroke width")
    strokeDasharray: Optional[str] = Field(None, description="Stroke dash pattern")
    animation: Optional[AnimationModel] = Field(None, description="Animation configuration")
    instances: Optional[List[InstanceModel]] = Field(None, min_length=2, description="Multiple element instances")

    model_config = ConfigDict(extra='allow')  # Allow extra fields not in skill documentation

    @field_validator('fill', 'stroke')
    @classmethod
    def validate_color_fields(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "none":
            return v
        return validate_hex_color(v)

    @model_validator(mode='after')
    def validate_timing(self):
        """Ensure exitOn > enterOn."""
        if self.exitOn <= self.enterOn:
            raise ValueError(f"exitOn ({self.exitOn}) must be greater than enterOn ({self.enterOn})")
        return self

    @model_validator(mode='after')
    def validate_instances_pattern(self):
        """Validate instances pattern: first instance must have useDefaults: true."""
        if self.instances and len(self.instances) > 0:
            if self.instances[0].useDefaults != True:
                raise ValueError("First instance must have 'useDefaults': true")
        return self


# ============================================================================
# ELEMENT TYPE-SPECIFIC MODELS
# ============================================================================

class TextElementModel(BaseElementModel):
    """Model for text elements."""
    type: Literal[ElementType.TEXT] = ElementType.TEXT
    text: str = Field(..., description="Text content to display")
    # width and height are calculated by validation using formulas - not required in design
    fontColor: Optional[str] = Field(None, description="Font color in hex format")
    fontSize: Optional[float] = Field(None, gt=0, description="Font size in pixels")
    textAlign: Optional[TextAlign] = Field(None, description="Text alignment")
    fontWeight: Optional[Union[int, str]] = Field(None, description="Font weight (number or string)")
    lineHeight: Optional[float] = Field(None, gt=0, description="Line height multiplier (default 1.5)")
    containerWidth: Optional[float] = Field(None, gt=0, description="Fixed container width - if set, text wraps within this width")
    padding: Optional[float] = Field(None, ge=0, description="Padding in pixels (default 8)")
    bgID: Optional[str] = Field(None, description="Background element ID reference")
    container: Optional[ContainerModel] = Field(None, description="Container configuration for background box")

    model_config = ConfigDict(extra='allow')  # Allow extra fields

    @field_validator('fontColor')
    @classmethod
    def validate_font_color(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_hex_color(v)


class ShapeElementModel(BaseElementModel):
    """Model for shape, icon, character, asset, and pattern elements (all use width/height)."""
    type: Literal[ElementType.SHAPE, ElementType.ASSET, ElementType.PATTERN]
    width: Optional[float] = Field(None, gt=0, description="Element width")
    height: Optional[float] = Field(None, gt=0, description="Element height")
    orientation: Optional[float] = Field(None, description="Asset orientation in degrees (required for assets with follow-path)")
    flipX: Optional[bool] = Field(None, description="Horizontal flip for asymmetric assets")
    flipY: Optional[bool] = Field(None, description="Vertical flip for asymmetric assets")

    model_config = ConfigDict(extra='allow')  # Allow extra fields like assetPath for non-documented types

    @model_validator(mode='after')
    def validate_asset_follow_path_orientation(self):
        """Ensure assets with follow-path action have orientation field."""
        # Only validate for ASSET type
        if self.type != ElementType.ASSET:
            return self

        # Check if element has follow-path action
        has_follow_path = False
        if self.animation and self.animation.actions:
            for action in self.animation.actions:
                if isinstance(action, FollowPathAction):
                    has_follow_path = True
                    break

        # If asset has follow-path but no orientation, raise error
        if has_follow_path and self.orientation is None:
            raise ValueError(
                f"Asset '{self.id}' has follow-path action but missing 'orientation' field. "
                f"Infer orientation from asset composition (0°=UP, 90°=RIGHT, 180°=DOWN, 270°=LEFT)."
            )

        return self


class PathElementModel(BaseElementModel):
    """Model for path elements."""
    type: Literal[ElementType.PATH] = ElementType.PATH
    path_params: Optional[Annotated[PathParamsUnion, Field(discriminator="type")]] = Field(None, description="Single path configuration")
    merge_path_params: Optional[List[Annotated[PathParamsUnion, Field(discriminator="type")]]] = Field(None, min_length=1, description="Composite path configuration")
    arrow_marker: Optional[ArrowMarker] = Field(None, description="Arrow marker type")
    width: Optional[float] = Field(None, gt=0, description="Path width (optional)")
    height: Optional[float] = Field(None, gt=0, description="Path height (optional)")

    model_config = ConfigDict(extra='allow')  # Allow extra fields

    @model_validator(mode='after')
    def validate_path_params(self):
        """Ensure exactly one of path_params or merge_path_params is present."""
        has_path = self.path_params is not None
        has_merge = self.merge_path_params is not None

        if has_path and has_merge:
            raise ValueError("Cannot have both 'path_params' and 'merge_path_params'. Use only one.")
        if not has_path and not has_merge:
            raise ValueError("Path elements must have either 'path_params' or 'merge_path_params'")

        return self


# ============================================================================
# DISCRIMINATED UNION FOR ALL ELEMENTS
# ============================================================================

ElementUnion = Union[
    TextElementModel,
    ShapeElementModel,
    PathElementModel
]


# ============================================================================
# TOP-LEVEL SCENE MODEL
# ============================================================================

class DesignSceneModel(BaseModel):
    """Complete model for a video design scene JSON file."""
    scene: int = Field(..., ge=0, description="Scene number/index")
    startTime: int = Field(..., ge=0, description="Scene start time in milliseconds")
    endTime: int = Field(..., description="Scene end time in milliseconds")
    video_metadata: VideoMetadataModel = Field(..., description="Video metadata configuration")
    elements: List[Annotated[ElementUnion, Field(discriminator="type")]] = Field(..., min_length=1, description="Array of scene elements")
    scene_description: Optional[str] = Field(None, description="Optional scene description")

    model_config = ConfigDict(extra='allow')  # Allow extra fields not in skill documentation

    @model_validator(mode='after')
    def validate_scene_timing(self):
        """Ensure endTime > startTime."""
        if self.endTime <= self.startTime:
            raise ValueError(f"endTime ({self.endTime}) must be greater than startTime ({self.startTime})")
        return self

    @model_validator(mode='after')
    def validate_element_timing_bounds(self):
        """Ensure all elements' timing is within scene bounds."""
        for element in self.elements:
            if element.enterOn < self.startTime:
                raise ValueError(
                    f"Element '{element.id}' enterOn ({element.enterOn}) must be >= scene startTime ({self.startTime})"
                )
            if element.enterOn > self.endTime:
                raise ValueError(
                    f"Element '{element.id}' enterOn ({element.enterOn}) cannot be > scene endTime ({self.endTime})"
                )
            if element.exitOn < self.startTime:
                raise ValueError(
                    f"Element '{element.id}' exitOn ({element.exitOn}) must be >= scene startTime ({self.startTime})"
                )
            if element.exitOn > self.endTime:
                raise ValueError(
                    f"Element '{element.id}' exitOn ({element.exitOn}) cannot be > scene endTime ({self.endTime})"
                )

            # Validate animation action timing if present
            if element.animation and element.animation.actions:
                for i, action in enumerate(element.animation.actions):
                    if action.on < self.startTime:
                        raise ValueError(
                            f"Element '{element.id}' animation action[{i}].on ({action.on}) must be >= scene startTime ({self.startTime})"
                        )
                    if action.on > self.endTime:
                        raise ValueError(
                            f"Element '{element.id}' animation action[{i}].on ({action.on}) cannot be > scene endTime ({self.endTime})"
                        )

        return self

    @model_validator(mode='after')
    def validate_unique_element_ids(self):
        """Ensure all element IDs are unique."""
        ids = [element.id for element in self.elements]
        duplicates = [id for id in ids if ids.count(id) > 1]
        if duplicates:
            raise ValueError(f"Duplicate element IDs found: {set(duplicates)}")
        return self

    @model_validator(mode='after')
    def validate_follow_path_easing_sync(self):
        """Ensure follow-path easing matches the referenced path's path-draw easing."""
        # Build map of path elements with path-draw entrance
        path_easings = {}
        for element in self.elements:
            if element.type == ElementType.PATH:
                if element.animation and element.animation.entrance:
                    if element.animation.entrance.type == "path-draw":
                        path_easings[element.id] = element.animation.entrance.easing

        # Check follow-path actions reference paths with matching easing
        for element in self.elements:
            if element.animation and element.animation.actions:
                for action in element.animation.actions:
                    if isinstance(action, FollowPathAction):
                        path_easing = path_easings.get(action.pathId)
                        if path_easing and action.easing and path_easing != action.easing:
                            raise ValueError(
                                f"Element '{element.id}' follow-path easing '{action.easing}' "
                                f"doesn't match path '{action.pathId}' path-draw easing '{path_easing}'. "
                                f"Both must use the same easing for synchronized animation."
                            )
        return self
