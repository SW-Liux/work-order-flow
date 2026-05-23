#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const os = require("os");

const VERSION = require("../package.json").version;
const SKILL_NAME = "work-order-flow";

const PLATFORM_PATHS = {
  cursor: path.join(os.homedir(), ".cursor", "skills", SKILL_NAME),
  "claude-code": path.join(os.homedir(), ".claude", "skills", SKILL_NAME),
  codex: path.join(os.homedir(), ".agents", "skills", SKILL_NAME),
  windsurf: path.join(os.homedir(), ".windsurf", "skills", SKILL_NAME),
};

const COPY_ITEMS = [
  "SKILL.md",
  "CHANGELOG.md",
  "README.md",
  "scripts",
  "templates",
];

function detectPlatform() {
  for (const [platform, dir] of Object.entries(PLATFORM_PATHS)) {
    const parentDir = path.dirname(path.dirname(dir));
    if (fs.existsSync(parentDir)) return platform;
  }
  return null;
}

function copyRecursive(src, dest) {
  if (!fs.existsSync(src)) return;
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    fs.mkdirSync(dest, { recursive: true });
    for (const item of fs.readdirSync(src)) {
      copyRecursive(path.join(src, item), path.join(dest, item));
    }
  } else {
    fs.copyFileSync(src, dest);
  }
}

function install(targetDir) {
  const srcDir = path.resolve(__dirname, "..");
  fs.mkdirSync(targetDir, { recursive: true });

  for (const item of COPY_ITEMS) {
    const src = path.join(srcDir, item);
    const dest = path.join(targetDir, item);
    copyRecursive(src, dest);
  }

  const localDir = path.join(targetDir, "local");
  fs.mkdirSync(localDir, { recursive: true });

  const gitignorePath = path.join(targetDir, ".gitignore");
  if (!fs.existsSync(gitignorePath)) {
    fs.writeFileSync(gitignorePath, "local/\nnode_modules/\n");
  }

  console.log(`\n  ✅ work-order-flow v${VERSION} installed to:`);
  console.log(`     ${targetDir}\n`);
  console.log("  Usage: Tell your AI agent to read SKILL.md:");
  console.log(`     "Please read ${path.join(targetDir, "SKILL.md")} and follow the workflow."\n`);
}

function showHelp() {
  console.log(`
  work-order-flow v${VERSION}
  AI Agent workflow for order-driven development

  Commands:
    install [--platform <name>] [--path <dir>]   Install skill files
    update                                        Update to latest version
    version                                       Show version

  Platforms: cursor, claude-code, codex, windsurf

  Examples:
    npx @sw-liux/work-order-flow install
    npx @sw-liux/work-order-flow install --platform cursor
    npx @sw-liux/work-order-flow install --path ~/my-skills/work-order-flow
  `);
}

const args = process.argv.slice(2);
const command = args[0];

if (command === "install" || command === "update") {
  let targetDir = null;
  const pathIdx = args.indexOf("--path");
  const platformIdx = args.indexOf("--platform");

  if (pathIdx !== -1 && args[pathIdx + 1]) {
    targetDir = path.resolve(args[pathIdx + 1]);
  } else if (platformIdx !== -1 && args[platformIdx + 1]) {
    const platform = args[platformIdx + 1];
    targetDir = PLATFORM_PATHS[platform];
    if (!targetDir) {
      console.error(`  ❌ Unknown platform: ${platform}`);
      console.error(`  Available: ${Object.keys(PLATFORM_PATHS).join(", ")}`);
      process.exit(1);
    }
  } else {
    const detected = detectPlatform();
    if (detected) {
      targetDir = PLATFORM_PATHS[detected];
      console.log(`  Detected platform: ${detected}`);
    } else {
      targetDir = PLATFORM_PATHS.cursor;
      console.log("  No platform detected, defaulting to Cursor.");
    }
  }

  install(targetDir);
} else if (command === "version" || command === "-v" || command === "--version") {
  console.log(VERSION);
} else {
  showHelp();
}
