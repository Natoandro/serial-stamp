from PIL import Image, ImageFont, ImageDraw
from typing import Callable, Optional, List, Literal, Tuple
import argparse
from dataclasses import dataclass
from functools import reduce

font_size = 30
font = ImageFont.truetype("fonts/Roboto-Medium.ttf", font_size)


# def add_ticket_number(
#     number: Callable[[int], int],
# ) -> Callable[[Image.Image, int], Image.Image]:
#     def prepare(im: Image.Image, i: int) -> Image.Image:
#         n = number(i)
#         d = ImageDraw.Draw(im)
#         d.text((160, 300), f"Nº {n:03}", font=font, fill=(48, 64, 128, 255))
#         d.text((1000, 300), f"Nº {n:03}", font=font, fill=(48, 64, 128, 255))
#
#         return im
#
#     return prepare


# def stack(
#     im: Image.Image,
#     *,
#     repeat: int,
#     gap=0,
#     prepare: Optional[Callable[[Image.Image, int], Image.Image]] = None,
# ) -> Image.Image:
#     if repeat < 1:
#         raise ValueError("repeat must be greater than 0")
#
#     width = im.width
#     height = im.height * repeat + gap * (repeat - 1)
#
#     image = Image.new("RGB", (width, height), (127, 127, 127))
#
#     get_image: Callable[[int], Image.Image] = (
#         (lambda i: prepare(im.copy(), i)) if prepare is not None else lambda i: im
#     )
#
#     for i in range(repeat):
#         top = (im.height + gap) * i
#         bottom = top + im.height
#         image.paste(get_image(i), (0, top, width, bottom))
#
#     return image


@dataclass
class Output:
    path: str
    stack_size: int


class LayoutParam:
    x: int
    y: int

    def __init__(self, arg: str, sep: str = ","):
        vals = [int(v) for v in arg.split(sep)]
        match len(vals):
            case 0:
                [x, y] = [0, 0]
            case 1:
                [x, y] = [vals[0], vals[0]]
            case _:
                [x, y] = [vals[0], vals[1]]
        self.x = x
        self.y = y


@dataclass
class Layout:
    repeat: LayoutParam
    gap: LayoutParam
    margin: LayoutParam


# TODO add support for csv source
class Param:
    name: str
    type: Literal["number"]  # TODO support for other types
    range: Tuple[str, str]
    format: Optional[str]

    # -p no,type=number,value=1-500,format=000
    def __init__(self, arg: str):
        [name, *others] = arg.split(",")
        self.name = name
        self.type = "number"
        self.range = ("1", "1")
        self.format = None
        for param in others:
            [key, val] = param.split("=")
            match key:
                case "type":
                    if val != "number":
                        raise Exception(f"Unknown type '{val}'")
                    self.type = val
                case "value":
                    [start, end] = val.split("-")
                    end = start if end is None else end
                    self.range = (start, end)
                case "format":
                    self.format = val

    def integer_range(self) -> Tuple[int, int]:
        return (int(self.range[0]), int(self.range[1]))

    def range_size(self) -> int:
        [start, end] = self.integer_range()
        return end - start + 1


@dataclass
class Text:
    text: str
    position: Tuple[int, int]
    size: int
    font: ImageFont.FreeTypeFont
    # TODO font

    @staticmethod
    def parse_args(args: List[str]) -> List["Text"]:
        res = []
        for arg in args:
            if arg.startswith("#"):
                res.append(
                    Text(
                        text=arg.removeprefix("#"),
                        position=(0, 0),
                        size=(16),
                        font=font,
                    )
                )
            else:
                entries = arg.split(",")
                t = res[-1]
                for entry in entries:
                    [key, val] = entry.split("=")
                    match key:
                        case "x":
                            t.position = (int(val), t.position[1])
                        case "y":
                            t.position = (t.position[0], int(val))
                        case "size":
                            t.size = int(val)
                            t.font = ImageFont.truetype(
                                "fonts/Roboto-Medium.ttf", t.size
                            )

        return res


@dataclass
class Drawing:
    params: List[Param]
    texts: List[Text]


class App:
    source: str
    output: Output
    layout: Layout
    params: List[Param]
    texts: List[Text]

    def __init__(self, args: argparse.Namespace):
        self.source = args.ticket_image
        self.output = Output(
            path=args.output,
            stack_size=args.stack_size if args.stack_size is not None else 1,
        )
        self.layout = Layout(
            repeat=LayoutParam(
                args.repeat if args.repeat is not None else "1", sep="x"
            ),
            gap=LayoutParam(args.gap if args.gap is not None else "0"),
            margin=LayoutParam(args.margin if args.margin is not None else "0"),
        )
        self.params = [Param(p) for p in (args.param if args.param is not None else [])]
        self.texts = Text.parse_args(args.text if args.text is not None else [])

    def run(self):
        with Image.open(self.source) as orig:
            # TODO config for background color
            im = Image.new("RGB", (orig.width, orig.height), (255, 255, 255))

            im.paste(orig, (0, 0, orig.width, orig.height))

            images = []

            ticket_count = reduce(
                lambda x, y: x * y, map(lambda p: p.range_size(), self.params)
            )
            ticket_count_per_page = self.layout.repeat.x * self.layout.repeat.y
            page_count = (ticket_count - 1) // ticket_count_per_page + 1
            stack_count = (page_count - 1) // self.output.stack_size + 1
            for stack_index in range(stack_count):
                for page_offset in range(self.output.stack_size):
                    page_no = 1 + stack_index * self.output.stack_size + page_offset
                    print(f"page: {page_no}/{page_count}")
                    res = self.print_page(im, stack_index, page_offset)

                    images.append(res)

            images[0].save(
                self.output.path,
                resolution=100.0,
                save_all=True,
                append_images=images[1:],
            )

    def print_page(self, ticket_image: Image.Image, stack_index: int, page_offset: int):
        width = (
            (ticket_image.width + self.layout.gap.x) * self.layout.repeat.x
            + self.layout.margin.x * 2
            - self.layout.gap.x
        )
        height = (
            (ticket_image.height + self.layout.gap.y) * self.layout.repeat.y
            + self.layout.margin.y * 2
            - self.layout.gap.y
        )

        # TODO configurable background color
        image = Image.new("RGB", (width, height), (255, 255, 255))
        ticket_width = ticket_image.width
        ticket_height = ticket_image.height

        rep_x = self.layout.repeat.x
        rep_y = self.layout.repeat.y

        for x in range(rep_x):
            for y in range(rep_y):
                im = ticket_image.copy()
                # Currently, we only consider the first param
                # FIXME
                param = (
                    int(self.params[0].range[0])
                    + stack_index * self.output.stack_size * rep_x * rep_y
                    + ((x * rep_y) + y) * self.output.stack_size
                    + page_offset
                )

                for text in self.texts:
                    value = text.text.replace("$" + self.params[0].name, f"{param:03}")
                    # TODO font size
                    d = ImageDraw.Draw(im)
                    # TODO configurable text color
                    d.text(
                        text.position, value, font=text.font, fill=(48, 64, 128, 255)
                    )
                left = self.layout.margin.x + x * (ticket_width + self.layout.gap.x)
                top = self.layout.margin.y + y * (ticket_height + self.layout.gap.y)
                image.paste(im, (left, top, left + ticket_width, top + ticket_height))

        return image


def main():
    parser = argparse.ArgumentParser(
        prog="ticketid",
        description="add identification labels to tickets",
    )

    source = parser.add_argument_group("source image")
    source.add_argument("-i", "--ticket-image")

    output = parser.add_argument_group("output target")
    output.add_argument("-o", "--output")
    output.add_argument("--pdf", action="store_true")
    output.add_argument("--stack-size", type=int)

    layout = parser.add_argument_group("output layout")
    layout.add_argument("-r", "--repeat")
    layout.add_argument("-g", "--gap")
    layout.add_argument("-m", "--margin")

    draw = parser.add_argument_group("drawing")
    draw.add_argument("-t", "--text", action="append")
    draw.add_argument("-p", "--param", action="append")

    args = parser.parse_args()
    app = App(args)

    app.run()


if __name__ == "__main__":
    main()
