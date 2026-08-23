export type ChangelogEntry = {
  readonly version: string;
  readonly date: string;
  readonly changes: readonly string[];
};

export const CHANGELOG = [
  {
    version: "0.1.0",
    date: "2026-08-19",
    changes: ["创建项目。"],
  },
] as const satisfies readonly ChangelogEntry[];

export const CURRENT_VERSION = CHANGELOG[0].version;
