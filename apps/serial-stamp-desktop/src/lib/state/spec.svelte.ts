export type Color = string | [number, number, number] | [number, number, number, number];

export interface Layout {
  "grid-size": [number, number];
  gap: number | [number, number];
  margin: number | [number, number] | [number, number, number, number];
}

export interface TextSpec {
  template: string;
  position: [number, number];
  ttf?: string;
  size: number;
  color: Color;
}

export interface OutputSpec {
  "background-color": Color;
}

export interface StampSpec {
  projectName?: string;
  "stack-size": number;
  "source-image": string;
  layout: Layout;
  texts: TextSpec[];
  params?: Array<{
    name: string;
    type: string;
    [key: string]: any;
  }>;
  output: OutputSpec;
  background: Color;
}

export const defaultSpec: StampSpec = {
  projectName: "Untitled Project",
  "stack-size": 1,
  "source-image": "",
  layout: {
    "grid-size": [1, 1],
    gap: 0,
    margin: 0,
  },
  texts: [
    {
      template: "Sample Text",
      position: [10, 10],
      size: 24,
      color: "black",
    },
  ],
  params: [],
  output: {
    "background-color": "white",
  },
  background: "white",
};

export class SpecState {
  current = $state<StampSpec>(structuredClone(defaultSpec));

  reset() {
    this.current = structuredClone(defaultSpec);
  }

  set(spec: StampSpec) {
    this.current = spec;
  }
}

export const specState = new SpecState();
