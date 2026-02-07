from typing import Any, Literal

from PIL import ImageFont
from pydantic import BaseModel, Field
from pydantic.fields import cached_property

Color = tuple[int, int, int] | tuple[int, int, int, int] | str


class Layout(BaseModel):
    grid_size: tuple[int, int] = Field(alias="grid-size")
    gap: tuple[float, float] | float
    margin: float | tuple[float, float] | tuple[float, float, float, float]

    @property
    def grid_area(self):
        return self.grid_size[0] * self.grid_size[1]

    @property
    def gap_x(self):
        return self.gap[0] if isinstance(self.gap, tuple) else self.gap

    @property
    def gap_y(self):
        return self.gap[1] if isinstance(self.gap, tuple) else self.gap

    @property
    def margin_top(self):
        return self.margin[0] if isinstance(self.margin, tuple) else self.margin

    @property
    def margin_right(self):
        return self.margin[1] if isinstance(self.margin, tuple) else self.margin

    @property
    def margin_bottom(self):
        if isinstance(self.margin, tuple):
            if len(self.margin) == 2:
                return self.margin[0]
            else:
                return self.margin[2]
        return self.margin

    @property
    def margin_left(self):
        if isinstance(self.margin, tuple):
            if len(self.margin) == 2:
                return self.margin[1]
            else:
                return self.margin[3]
        return self.margin


class Text(BaseModel):
    template: str
    position: tuple[float, float]
    ttf: str | None = None
    size: int = 16
    color: Color = (0, 0, 0)

    @cached_property
    def font(self):
        if self.ttf is not None:
            return ImageFont.truetype(self.ttf, self.size)

        try:
            return ImageFont.truetype("Arial.ttf", self.size)
        except OSError:
            return ImageFont.load_default(self.size)


class IntParam(BaseModel):
    model_config = {"populate_by_name": True}

    name: str
    type: Literal["int", "integer"] = "integer"
    values: list[int]
    leading_zeros: int | None = Field(default=None, alias="leading-zeros")

    @property
    def value_count(self):
        return len(self.values)

    def get_values(self):
        def render(value: int) -> str:
            return (
                f"{value:0{self.leading_zeros}d}" if self.leading_zeros else str(value)
            )

        return map(render, self.values)


class StringParam(BaseModel):
    name: str
    type: Literal["string", "text"] = "string"
    values: list[str]

    @property
    def value_count(self):
        return len(self.values)

    def get_values(self):
        return self.values


class StringArrayParam(BaseModel):
    name: str
    type: Literal["string[]", "text[]"] = "string[]"
    length: int
    values: list[list[str]]

    @property
    def value_count(self):
        return len(self.values)

    def get_values(self):
        return self.values


class IntRangeParam(BaseModel):
    model_config = {"populate_by_name": True}

    name: str
    type: Literal["int", "integer"] = "integer"
    min: int
    max: int
    leading_zeros: int | None = Field(default=None, alias="leading-zeros")

    @property
    def value_count(self):
        return self.max - self.min + 1

    def get_values(self):
        def render(value: int) -> str:
            return (
                f"{value:0{self.leading_zeros}d}" if self.leading_zeros else str(value)
            )

        return map(render, range(self.min, self.max + 1))
        return range(self.min, self.max + 1)


class Output(BaseModel):
    background_color: Color = Field(alias="background-color", default="white")


class Spec(BaseModel):
    stack_size: int = Field(alias="stack-size", default=1)
    source_image: str = Field(alias="source-image")
    layout: Layout
    texts: list[Text]
    params: list[
        IntParam | StringParam | IntRangeParam | StringArrayParam
    ] | None = Field(default=None)
    table: list[dict[str, Any]] | None = Field(default=None)
    output: Output = Field(default_factory=Output)
    background: Color = (255, 255, 255)
