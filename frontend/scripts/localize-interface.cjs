// One-time, repeat-safe migration of display text; protocol values and styles are untouched.
const fs = require("node:fs");
const ts = require("typescript");
const files = ["src/app/page.tsx", "src/app/login/page.tsx", "src/app/scheme-finder/page.tsx", ...fs.readdirSync("src/components/plant-monitor").filter((name) => name.endsWith(".tsx")).map((name) => `src/components/plant-monitor/${name}`)];
const entities = { amp: "&", apos: "'", quot: '"', bull: "•", lt: "<", gt: ">", ldquo: "“", rdquo: "”", nbsp: " " };
const normalize = (value) => value.replace(/&([a-z]+);/g, (match, key) => entities[key] || match).replace(/\s+/g, " ").trim();
function scalar(node) {
  let hasJsx = false;
  function findJsx(child) { if (ts.isJsxElement(child) || ts.isJsxSelfClosingElement(child) || ts.isJsxFragment(child)) hasJsx = true; else ts.forEachChild(child, findJsx); }
  findJsx(node);
  if (hasJsx) return false;
  if (ts.isJsxElement(node) || ts.isJsxSelfClosingElement(node) || ts.isJsxFragment(node) || ts.isArrayLiteralExpression(node) || ts.isArrowFunction(node)) return false;
  if (ts.isConditionalExpression(node)) return scalar(node.whenTrue) && scalar(node.whenFalse);
  return true;
}
function containsWords(node) {
  if ((ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node) || ts.isTemplateExpression(node)) && /[A-Za-z]{2}/.test(node.getText())) return true;
  return ts.forEachChild(node, containsWords) || false;
}
for (const file of files) {
  let source = fs.readFileSync(file, "utf8");
  const alreadyLocalized = source.includes("useLanguage");
  // Do not translate a React subtree as a string; localize its text leaves instead.
  const preliminary = ts.createSourceFile(file, source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
  const unwrap = [];
  function clean(node) {
    if (ts.isCallExpression(node) && node.expression.getText(preliminary) === "t" && node.arguments[0] && !scalar(node.arguments[0])) {
      unwrap.push({ start: node.getStart(preliminary), end: node.end, replacement: node.arguments[0].getText(preliminary) });
      return;
    }
    ts.forEachChild(node, clean);
  }
  clean(preliminary);
  for (const edit of unwrap.sort((a,b) => b.start-a.start)) source = source.slice(0,edit.start)+edit.replacement+source.slice(edit.end);
  if (file.includes("scheme-finder")) source = source.replace("s.tags.map(t =>", "s.tags.map(tag =>").replace("key={t}", "key={tag}").replace("{t}</span>", "{tag}</span>");
  const ast = ts.createSourceFile(file, source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
  const edits = [];
  const used = new Set();
  function record(node, replacement) {
    edits.push({ start: node.getStart(ast), end: node.end, replacement });
    let owner = node.parent;
    while (owner && !ts.isFunctionDeclaration(owner)) owner = owner.parent;
    if (owner?.body) used.add(owner);
  }
  function walk(node) {
    if (ts.isJsxText(node)) {
      const text = normalize(node.text);
      if (/[A-Za-z]{2}/.test(text) && !/^KrishiNidhi$|^GPIO |^ADC |^1-Wire |^% RH$|^NodeMCU ESP8266 ESP-12E$/.test(text)) {
        const leading = !node.text.includes("\n") && /^\s/.test(node.text) ? '{" "}' : "";
        const trailing = !node.text.includes("\n") && /\s$/.test(node.text) ? '{" "}' : "";
        edits.push({ start: node.pos, end: node.end, replacement: `${leading}{t(${JSON.stringify(text)})}${trailing}` });
        let owner = node.parent; while (owner && !ts.isFunctionDeclaration(owner)) owner = owner.parent;
        if (owner?.body) used.add(owner);
      }
      return;
    }
    if (ts.isJsxAttribute(node) && ["aria-label", "placeholder", "title"].includes(node.name.getText(ast)) && node.initializer && ts.isStringLiteral(node.initializer) && /[A-Za-z]{2}/.test(node.initializer.text)) {
      record(node.initializer, `{t(${JSON.stringify(node.initializer.text)})}`); return;
    }
    if (ts.isJsxExpression(node) && node.expression && !ts.isJsxAttribute(node.parent)) {
      const expression = node.expression;
      const text = expression.getText(ast);
      const dynamic = /^(?:item\.(?:title|badge|desc|cta)|s\.(?:title|desc|eligibility|benefit)|(?:cat|tag|status|severity|obs|rec|error|errorMsg|pendingAction|plantName)|m)$/.test(text);
      if ((containsWords(expression) && scalar(expression) && !text.includes("=>") && !text.startsWith("t(")) || dynamic) {
        record(expression, `t(${text})`); return;
      }
    }
    ts.forEachChild(node, walk);
  }
  walk(ast);
  if (!edits.length && !unwrap.length) continue;
  for (const owner of used) if (!owner.body.getText(ast).includes("= useLanguage()")) edits.push({ start: owner.body.getStart(ast) + 1, end: owner.body.getStart(ast) + 1, replacement: "\n  const { t, intlLocale } = useLanguage();\n" });
  for (const edit of edits.sort((a, b) => b.start - a.start)) source = source.slice(0, edit.start) + edit.replacement + source.slice(edit.end);
  source = source.replace(/\.toLocaleTimeString\(\[\]/g, ".toLocaleTimeString(intlLocale").replace(/\.toLocaleDateString\(\[\]/g, ".toLocaleDateString(intlLocale");
  if (!source.includes("toLocaleTimeString(intlLocale") && !source.includes("toLocaleDateString(intlLocale")) source = source.replaceAll("const { t, intlLocale } = useLanguage();", "const { t } = useLanguage();");
  if (!alreadyLocalized) source = `import { useLanguage } from "@/components/LanguageProvider";\n${source}`;
  source = source.replace(/^import ([\s\S]*?)"use client";\s*/, '"use client";\n\nimport $1');
  if (!source.startsWith('"use client"')) source = '"use client";\n\n' + source;
  fs.writeFileSync(file, source);
  console.log(file);
}
