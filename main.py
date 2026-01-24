import argparse
from pathlib import Path
import tomllib

from tiknum.engine import Engine
from tiknum.models import Spec
from PIL import Image


def main():
    parser = argparse.ArgumentParser(
        description="Tool for adding iterative numbers to ticket images"
    )

    parser.add_argument("filename")
    parser.add_argument("-o", "--output")

    args = parser.parse_args()

    with open(args.filename, "rb") as spec_file:
        spec = Spec(**tomllib.load(spec_file))

    print(f"source image: {spec.source_image}")
    with Image.open(spec.source_image) as source_image:
        app = Engine(spec, Path(args.output).resolve(), source_image)
        app.generate()


if __name__ == "__main__":
    main()
