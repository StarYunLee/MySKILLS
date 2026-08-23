# 用户 App 脚手架

给用户自有、长期维护的 Scripting App 用。一次性脚本和官方示例不要用这套。

复制本目录四个文件到 `/var/minis/mounts/Scripting scripts/<Name>/`：

- `script.json`
- `changelog.ts`
- `.gitignore`
- `tsconfig.json`

然后按官方生命周期另选 `index.tsx`（通常从 `../index-page.tsx` 起步）。不要默认复制三 Tab、玻璃组件或 Widget。

`script.json.name` 必须等于目录名。`changelog.ts` 首条版本必须等于 `script.json.version`。本地 `git init`，不要擅自加 remote。
