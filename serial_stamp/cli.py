import argparse
import sys
import tomllib
from pathlib import Path

from PIL import Image

from serial_stamp.engine import Engine
from serial_stamp.models import Spec
from serial_stamp.project import Project, init_project, pack_project


def generate_handler(args):
    try:
        with Project(args.input) as project:
            print(f"Loaded project from: {project.root_path}")
            print(f"Working directory: {project.work_dir}")

            if not project.spec_path.exists():
                print(f"Error: Spec file not found at {project.spec_path}")
                sys.exit(1)

            with open(project.spec_path, "rb") as f:
                data = tomllib.load(f)

            spec = Spec(**data)

            # Resolve source image path relative to the project working directory
            img_path = project.work_dir / spec.source_image

            if not img_path.exists():
                print(f"Error: Source image not found at {img_path}")
                sys.exit(1)

            print(f"Source image: {img_path}")

            output_path = Path(args.output).resolve()

            with Image.open(img_path) as source_image:
                app = Engine(spec, output_path, source_image)
                app.generate()

            print(f"Successfully generated: {output_path}")

    except Exception as e:
        print(f"Error during generation: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="serial-stamp", description="SerialStamp - Ticket and Document Generator"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- INIT ---
    parser_init = subparsers.add_parser("init", help="Initialize a new project folder")
    parser_init.add_argument("path", help="Directory path to create")

    # --- PACK ---
    parser_pack = subparsers.add_parser(
        "pack", help="Bundle a project directory into a .stamp file"
    )
    parser_pack.add_argument("source", help="Source project directory")
    parser_pack.add_argument(
        "-o", "--output", required=True, help="Output .stamp file path"
    )

    # --- GENERATE ---
    parser_gen = subparsers.add_parser("generate", help="Generate PDF from a project")
    parser_gen.add_argument(
        "input", help="Input .stamp file, .toml file, or project directory"
    )
    parser_gen.add_argument(
        "-o", "--output", required=True, help="Output PDF file path"
    )

    # Default to 'generate' if the first argument doesn't match a subcommand
    if len(sys.argv) > 1 and sys.argv[1] not in [
        "init",
        "pack",
        "generate",
        "-h",
        "--help",
    ]:
        sys.argv.insert(1, "generate")

    # If no arguments provided, print help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    if args.command == "init":
        try:
            init_project(args.path)
            print(f"Initialized new project at: {args.path}")
        except Exception as e:
            print(f"Error initializing project: {e}")
            sys.exit(1)

    elif args.command == "pack":
        try:
            pack_project(args.source, args.output)
            print(f"Packed '{args.source}' to '{args.output}'")
        except Exception as e:
            print(f"Error packing project: {e}")
            sys.exit(1)

    elif args.command == "generate":
        generate_handler(args)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
