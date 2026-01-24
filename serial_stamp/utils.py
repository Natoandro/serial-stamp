from typing import Any

from typing_extensions import Generator, Iterable, Tuple


def cartesian_product(
    *iterables: Iterable[Any],
    materialize: bool = False,
) -> Generator[Tuple[Any, ...], None, None]:
    if not iterables:
        return

    if len(iterables) == 1:
        for item in iterables[0]:
            if isinstance(item, tuple):
                yield item
            else:
                yield (item,)
        return

    if materialize:
        # Convert all iterables to lists to allow reuse (needed for generators)
        materialized = [list(iterable) for iterable in iterables]
        first = materialized[0]
        rest = materialized[1:]

        for x in first:
            for y in cartesian_product(*rest, materialize=True):
                if isinstance(x, tuple):
                    yield x + y
                else:
                    yield (x,) + y
    else:
        first_iter = iter(iterables[0])
        rest_iter = iterables[1:]

        for x in first_iter:
            for y in cartesian_product(*rest_iter):
                if isinstance(x, tuple):
                    yield x + y
                else:
                    yield (x,) + y


def replace_vars(template: str, vars: dict[str, str]) -> str:
    vars = {**vars, "$": "$"}
    segments = []
    rest = template

    while rest:
        index = rest.find("$")
        if index < 0:
            segments.append(rest)
            break

        # Add everything before the $
        segments.append(rest[:index])
        rest = rest[index + 1 :]

        # Find the longest matching variable name
        best_match = None
        best_length = 0

        for k, v in vars.items():
            if rest.startswith(k) and len(k) > best_length:
                best_match = (k, v)
                best_length = len(k)

        if best_match:
            k, v = best_match
            segments.append(v)
            rest = rest[len(k) :]
        else:
            print(f"[warn] Unknown variable at ${rest}")
            segments.append("$")
            # For unknown variables, we need to continue processing
            # by moving past just one character to avoid infinite loops

    return "".join(segments)
