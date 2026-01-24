from dataclasses import dataclass
from functools import reduce
from itertools import islice
from pathlib import Path
from typing import Any, Callable, Optional

from PIL import Image, ImageDraw

from serial_stamp.models import Spec
from serial_stamp.utils import cartesian_product, replace_vars


@dataclass
class Engine:
    spec: Spec
    output: Path
    source_image: Image.Image

    def _create_template(self) -> Image.Image:
        template = Image.new(
            "RGB",
            (self.source_image.width, self.source_image.height),
            self.spec.output.background_color,  # type: ignore
        )

        template.paste(
            self.source_image, (0, 0, self.source_image.width, self.source_image.height)
        )
        return template

    def _get_items_iterator(self):
        if self.spec.params is not None:
            return cartesian_product(
                *(param.get_values() for param in self.spec.params)
            )
        elif self.spec.table is not None:
            return iter(self.spec.table)
        return iter([])

    def _calculate_total_tickets(self) -> int:
        if self.spec.params is not None:
            return reduce(
                lambda x, y: x * y, map(lambda p: p.value_count, self.spec.params)
            )
        elif self.spec.table is not None:
            return len(self.spec.table)
        return 0

    def generate_preview(self) -> Image.Image:
        template = self._create_template()
        items = self._get_items_iterator()

        # We need enough items to fill the first page taking into account the stack stride
        tickets_per_page = self.spec.layout.grid_area
        count_needed = self.spec.stack_size * tickets_per_page
        stack_items = list(islice(items, count_needed))

        return self.print_page(template, 0, stack_items)

    def generate(self, progress_callback: Optional[Callable[[int, int], None]] = None):
        template = self._create_template()
        items = self._get_items_iterator()
        ticket_count = self._calculate_total_tickets()

        tickets_per_page = self.spec.layout.grid_area

        if tickets_per_page == 0:
            return

        min_page_count = (ticket_count - 1) // tickets_per_page + 1
        stack_count = (min_page_count - 1) // self.spec.stack_size + 1
        page_count = stack_count * self.spec.stack_size

        images = []

        for stack_index in range(stack_count):
            # stack_items = list(islice(items, self.spec.stack_size * tickets_per_page))
            stack_items = list(islice(items, self.spec.stack_size * tickets_per_page))
            for page_offset in range(self.spec.stack_size):
                page_no = 1 + stack_index * self.spec.stack_size + page_offset
                print(f"page {page_no}/{page_count}")

                if progress_callback:
                    progress_callback(page_no, page_count)

                res = self.print_page(template, page_offset, stack_items)
                images.append(res)

        if not images:
            return

        images[0].save(
            self.output, resolution=100.0, save_all=True, append_images=images[1:]
        )

    def print_page(
        self,
        template: Image.Image,
        page_offset: int,
        stack_items: list[tuple[str, ...]] | list[dict[str, Any]],
    ):
        layout = self.spec.layout
        width = int(
            (template.width + layout.gap_x) * layout.grid_size[0]
            - layout.gap_x
            + layout.margin_right
            + layout.margin_left
        )
        height = int(
            (template.height + layout.gap_y) * layout.grid_size[1]
            - layout.gap_y
            + layout.margin_top
            + layout.margin_bottom
        )

        image = Image.new("RGB", (width, height), self.spec.background)

        for i, item_index in enumerate(
            range(page_offset, len(stack_items), self.spec.stack_size)
        ):
            ticket_image = self.generate_ticket(template, stack_items[item_index])
            grid_pos = (i % layout.grid_size[0], i // layout.grid_size[0])
            # print(f"    {i}: {grid_pos}")
            left = layout.margin_left + grid_pos[0] * (template.width + layout.gap_x)
            top = layout.margin_top + grid_pos[1] * (template.height + layout.gap_y)
            image.paste(ticket_image, (int(left), int(top)))

        return image

    def generate_ticket(
        self,
        template_image: Image.Image,
        param_values: tuple[str, ...] | dict[str, Any],
    ):
        image = template_image.copy()
        values: dict[str, str] = {}
        if isinstance(param_values, dict):
            values = {name: str(value) for name, value in param_values.items()}
        elif self.spec.params is not None:
            values = {
                param.name: value
                for param, value in zip(self.spec.params, param_values)
            }

        for text in self.spec.texts:
            text_value = replace_vars(text.template, values)
            d = ImageDraw.Draw(image)
            d.text(text.position, text_value, font=text.font, fill=text.color)

        return image
