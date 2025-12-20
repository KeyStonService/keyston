const UNSAFE_PATTERN = /[;&|`$><()\\[\]{}\r\n]/;

type Pattern = {
  regex: RegExp;
  buildArgs: (match: RegExpMatchArray) => string[];
};

const COMMAND_PATTERNS: Pattern[] = [
  { regex: /^git status --porcelain$/, buildArgs: () => ["git", "status", "--porcelain"] },
  { regex: /^git add \.$/, buildArgs: () => ["git", "add", "."] },
  { regex: /^git rev-parse HEAD$/, buildArgs: () => ["git", "rev-parse", "HEAD"] },
  { regex: /^git rev-parse --abbrev-ref HEAD$/, buildArgs: () => ["git", "rev-parse", "--abbrev-ref", "HEAD"] },
  { regex: /^git stash push -m ['"]?(.+?)['"]?$/, buildArgs: m => ["git", "stash", "push", "-m", m[1]] },
  { regex: /^git stash pop$/, buildArgs: () => ["git", "stash", "pop"] },
  { regex: /^git reset --hard ([A-Za-z0-9._-]+)$/, buildArgs: m => ["git", "reset", "--hard", m[1]] },
  { regex: /^git push -u origin ([A-Za-z0-9._/-]+)$/, buildArgs: m => ["git", "push", "-u", "origin", m[1]] },
  { regex: /^git commit -m (.+)$/, buildArgs: m => buildCommitArgs(m[1]) },
  { regex: /^npm run lint$/, buildArgs: () => ["npm", "run", "lint"] },
  { regex: /^npm run build$/, buildArgs: () => ["npm", "run", "build"] },
  { regex: /^npm test$/, buildArgs: () => ["npm", "test"] },
  { regex: /^npm run type-check$/, buildArgs: () => ["npm", "run", "type-check"] },
  { regex: /^npm run format$/, buildArgs: () => ["npm", "run", "format"] },
  { regex: /^npx eslint --fix \.$/, buildArgs: () => ["npx", "eslint", "--fix", "."] },
  { regex: /^npx eslint --fix --ext \.ts,\.tsx,\.js,\.jsx \.$/, buildArgs: () => ["npx", "eslint", "--fix", "--ext", ".ts,.tsx,.js,.jsx", "."] },
  { regex: /^npx prettier --write \.$/, buildArgs: () => ["npx", "prettier", "--write", "."] },
  { regex: /^npx yaml-lint --fix \.$/, buildArgs: () => ["npx", "yaml-lint", "--fix", "."] },
  { regex: /^npx markdownlint --fix \.$/, buildArgs: () => ["npx", "markdownlint", "--fix", "."] },
];

function stripWrappingQuotes(value: string): string {
  if (!value) return value;
  const first = value[0];
  if ((first === "'" || first === '"') && value.endsWith(first)) {
    return value.slice(1, -1);
  }
  return value;
}

function buildCommitArgs(rawMessage: string): string[] {
  const startsWithQuote = rawMessage.startsWith("'") || rawMessage.startsWith('"');
  if (startsWithQuote && rawMessage.length < 2) {
    throw new Error("Invalid commit message quoting");
  }
  if (
    (rawMessage.startsWith("'") && !rawMessage.endsWith("'")) ||
    (rawMessage.startsWith('"') && !rawMessage.endsWith('"'))
  ) {
    throw new Error("Unbalanced commit message quotes");
  }
  const message = stripWrappingQuotes(rawMessage);
  if (UNSAFE_PATTERN.test(message)) {
    throw new Error("Unsafe commit message content");
  }
  return ["git", "commit", "-m", message];
}

function parseSegment(segment: string): string[] {
  if (UNSAFE_PATTERN.test(segment)) {
    throw new Error(`Unsafe command rejected: ${segment}`);
  }

  const trimmed = segment.trim();
  for (const pattern of COMMAND_PATTERNS) {
    const match = trimmed.match(pattern.regex);
    if (match) {
      return pattern.buildArgs(match);
    }
  }

  throw new Error(`Command not allowed: ${segment}`);
}

export function parseCommandSegments(command: string): string[][] {
  const segments = command
    .split("&&")
    .map(s => s.trim())
    .filter(Boolean);

  if (segments.length === 0) {
    throw new Error("No command to execute");
  }

  return segments.map(parseSegment);
}

export { UNSAFE_PATTERN };
