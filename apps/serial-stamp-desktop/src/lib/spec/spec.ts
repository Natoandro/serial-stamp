import { parse as parseToml, stringify as stringifyToml } from "smol-toml";

export type Color = string | [number, number, number] | [number, number, number, number];

export type Layout = {
  gridSize: [number, number];
  gap: number | [number, number];
  margin: number | [number, number] | [number, number, number, number];
};

export type TextSpec = {
  template: string;
  position: [number, number];
  ttf: string | null;
  size: number;
  color: Color;
};

export type OutputSpec = {
  backgroundColor: Color; // alias: background-color
};

export type IntParam = {
  name: string;
  type: "int" | "integer";
  values: number[];
  leadingZeros?: number | null;
};

export type StringParam = {
  name: string;
  type: "string" | "text";
  values: string[];
};

export type StringArrayParam = {
  name: string;
  type: "string[]" | "text[]";
  length: number;
  values: string[][];
};

export type IntRangeParam = {
  name: string;
  type: "int" | "integer";
  min: number;
  max: number;
  leadingZeros?: number | null;
};

export type Param = IntParam | StringParam | StringArrayParam | IntRangeParam;

export type Spec = {
  stackSize: number; // alias: stack-size
  sourceImage: string; // alias: source-image
  layout: Layout;
  texts: TextSpec[];
  params?: Param[] | null;
  table?: Array<Record<string, unknown>> | null;
  output: OutputSpec;
  background: Color;
};

export function defaultSpec(): Spec {
  return {
    stackSize: 1,
    sourceImage: "",
    layout: {
      gridSize: [1, 1],
      gap: 0,
      margin: 0,
    },
    texts: [
      {
        template: "Sample Text",
        position: [10, 10],
        ttf: null,
        size: 24,
        color: "black",
      },
    ],
    params: null,
    table: null,
    output: {
      backgroundColor: "white",
    },
    background: [255, 255, 255],
  };
}

type TomlObj = Record<string, unknown>;

function isNumber(x: unknown): x is number {
  return typeof x === "number" && Number.isFinite(x);
}

function isString(x: unknown): x is string {
  return typeof x === "string";
}

function asNumber(x: unknown, fallback: number): number {
  return isNumber(x) ? x : fallback;
}

function asString(x: unknown, fallback: string): string {
  return isString(x) ? x : fallback;
}

function isNumArr(x: unknown, len?: number): x is number[] {
  return Array.isArray(x) && x.every(isNumber) && (len == null || x.length === len);
}

function toTuple2(x: unknown, fallback: [number, number]): [number, number] {
  if (isNumArr(x, 2)) return [x[0], x[1]];
  return fallback;
}

function toTupleInt2(x: unknown, fallback: [number, number]): [number, number] {
  if (isNumArr(x, 2)) return [Math.trunc(x[0]), Math.trunc(x[1])];
  return fallback;
}

function normalizeColor(x: unknown, fallback: Color): Color {
  if (isString(x)) return x;
  if (Array.isArray(x) && (x.length === 3 || x.length === 4) && x.every((v) => typeof v === "number")) {
    const nums = x.map((v) => Math.trunc(v as number));
    return (nums.length === 3 ? [nums[0], nums[1], nums[2]] : [nums[0], nums[1], nums[2], nums[3]]) as Color;
  }
  return fallback;
}

function normalizeGap(x: unknown, fallback: number | [number, number]): number | [number, number] {
  if (isNumber(x)) return x;
  if (isNumArr(x, 2)) return [x[0], x[1]];
  return fallback;
}

function normalizeMargin(
  x: unknown,
  fallback: number | [number, number] | [number, number, number, number],
): number | [number, number] | [number, number, number, number] {
  if (isNumber(x)) return x;
  if (isNumArr(x, 2)) return [x[0], x[1]];
  if (isNumArr(x, 4)) return [x[0], x[1], x[2], x[3]];
  return fallback;
}

export function parseSpecToml(tomlText: string): Spec {
  let parsed: unknown;
  try {
    parsed = parseToml(tomlText) as unknown;
  } catch {
    // If parsing fails, fall back to defaults.
    return defaultSpec();
  }

  const root = (parsed ?? {}) as TomlObj;
  const d = defaultSpec();

  const layoutObj = (root["layout"] ?? {}) as TomlObj;
  const textsArr = Array.isArray(root["texts"]) ? (root["texts"] as unknown[]) : [];

  const outputObj = (root["output"] ?? {}) as TomlObj;

  const spec: Spec = {
    stackSize: Math.trunc(asNumber(root["stack-size"], d.stackSize)),
    sourceImage: asString(root["source-image"], d.sourceImage),
    layout: {
      gridSize: toTupleInt2(layoutObj["grid-size"], d.layout.gridSize),
      gap: normalizeGap(layoutObj["gap"], d.layout.gap),
      margin: normalizeMargin(layoutObj["margin"], d.layout.margin),
    },
    texts:
      textsArr.length > 0
        ? textsArr.map((t) => {
            const o = (t ?? {}) as TomlObj;
            return {
              template: asString(o["template"], d.texts[0]!.template),
              position: toTuple2(o["position"], d.texts[0]!.position),
              ttf: o["ttf"] == null ? null : asString(o["ttf"], ""),
              size: Math.trunc(asNumber(o["size"], d.texts[0]!.size)),
              color: normalizeColor(o["color"], d.texts[0]!.color),
            } satisfies TextSpec;
          })
        : d.texts,
    // V1 form UI can ignore params/table for now, but we preserve if present.
    params: (root["params"] as Param[] | null | undefined) ?? null,
    table: (root["table"] as Array<Record<string, unknown>> | null | undefined) ?? null,
    output: {
      backgroundColor: normalizeColor(outputObj["background-color"], d.output.backgroundColor),
    },
    background: normalizeColor(root["background"], d.background),
  };

  return spec;
}

export function serializeSpecToToml(spec: Spec): string {
  // Convert from camelCase TS to kebab-case TOML keys compatible with Python.
  const doc: TomlObj = {
    "stack-size": spec.stackSize,
    "source-image": spec.sourceImage,
    layout: {
      "grid-size": spec.layout.gridSize,
      gap: spec.layout.gap,
      margin: spec.layout.margin,
    },
    texts: spec.texts.map((t) => ({
      template: t.template,
      position: t.position,
      ttf: t.ttf ?? undefined,
      size: t.size,
      color: t.color,
    })),
    // Preserve optional fields if set (even though UI might not edit them yet)
    params: spec.params ?? undefined,
    table: spec.table ?? undefined,
    output: {
      "background-color": spec.output.backgroundColor,
    },
    background: spec.background,
  };

  // smol-toml will omit `undefined` keys.
  return stringifyToml(doc as any);
}
