// Records a real screen capture of the running Policy Copilot UI: opens it, asks a
// few policy questions, and lets the answers stream in — saved as a video + stills.
// Run against the local server (localhost:8099).
//
//   NODE_PATH=~/Projects/llmstudy/node_modules node scripts/record_ui.mjs
import { chromium } from "file:///Users/muse/Projects/llmstudy/node_modules/playwright/index.mjs";
import { fileURLToPath } from "url";
import path from "path";

const __dir = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dir, "..", "capture");
const URL = process.env.PC_URL || "http://127.0.0.1:8099";

const QUESTIONS = [
  "How many vacation days do I get?",
  "What's the remote work policy?",
  "How do I expense a work laptop?",
  "Can I bring my dog to the office?",
];

const W = 1920, H = 1080;

async function typeHuman(page, sel, text) {
  await page.click(sel);
  for (const ch of text) {
    await page.type(sel, ch, { delay: 28 + Math.floor(28 * ((ch.charCodeAt(0) % 5) / 5)) });
  }
}

async function waitForAnswer(page, prevCount) {
  // wait until a new bot bubble finished streaming (cursor removed)
  await page.waitForFunction((n) => {
    const rows = document.querySelectorAll(".msg-row .avatar.bot");
    if (rows.length < n) return false;
    const last = document.querySelectorAll(".msg-row");
    const lastContent = last[last.length - 1]?.querySelector(".content");
    return lastContent && !lastContent.querySelector(".cursor") && lastContent.textContent.length > 4;
  }, prevCount, { timeout: 30000 });
}

const browser = await chromium.launch();
const context = await browser.newContext({
  viewport: { width: W, height: H },
  deviceScaleFactor: 2,
  recordVideo: { dir: OUT, size: { width: W, height: H } },
});
const page = await context.newPage();
await page.goto(URL, { waitUntil: "networkidle" });
await page.waitForTimeout(1200);
await page.screenshot({ path: path.join(OUT, "01_welcome.png") });

let botCount = 0;
for (let i = 0; i < QUESTIONS.length; i++) {
  await typeHuman(page, "#input", QUESTIONS[i]);
  await page.waitForTimeout(350);
  await page.screenshot({ path: path.join(OUT, `q${i + 1}_typed.png`) });
  await page.click("#send");
  botCount += 1;
  await waitForAnswer(page, botCount);
  await page.waitForTimeout(900);
  await page.screenshot({ path: path.join(OUT, `q${i + 1}_answer.png`) });
  await page.waitForTimeout(600);
}
await page.waitForTimeout(1500);

await context.close(); // finalizes the video
await browser.close();
console.log("done -> capture/*.png + capture/*.webm");
