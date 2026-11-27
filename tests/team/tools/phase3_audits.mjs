// Run Lighthouse snapshots and axe-core on the actual authenticated SPA states.
import {createRequire} from 'node:module';
import {mkdir, writeFile} from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const [stage, evidence] = process.argv.slice(2);
if (!['before', 'after'].includes(stage) || !evidence) throw Error('Usage: phase3_audits.mjs before|after evidence-path');
const require = createRequire(path.join(process.env.MEDIHUB_AUDIT_MODULES, 'package.json'));
const {chromium} = require('playwright');
const {default: AxeBuilder} = require('@axe-core/playwright');
const puppeteer = require('puppeteer-core');
const {startFlow, generateReport} = await import(pathToFileURL(require.resolve('lighthouse')).href);
const out = path.resolve(evidence, stage);
const shots = path.resolve(evidence, 'screenshots', stage);
await Promise.all([mkdir(out, {recursive: true}), mkdir(shots, {recursive: true})]);

const root = 'http://127.0.0.1:5001';
const viewport = {width: 1440, height: 1000};
const assets = new Map([
  ['https://unpkg.com/vue@3.5.46/dist/vue.global.js', ['vue.global.js', 'application/javascript']],
  ['https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js', ['bootstrap.bundle.min.js', 'application/javascript']],
  ['https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css', ['bootstrap.min.css', 'text/css']],
  ['https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css', ['bootstrap-icons.css', 'text/css']],
]);
const testedCommit = process.env.MEDIHUB_TESTED_COMMIT;
if (!/^[0-9a-f]{40}$/.test(testedCommit ?? '')) throw Error('Set MEDIHUB_TESTED_COMMIT to the tested source revision');
const browser = await puppeteer.launch({executablePath: process.env.MEDIHUB_CHROME, headless: true,
  defaultViewport: viewport, args: ['--no-first-run', '--disable-background-networking']});
const cdp = await chromium.connectOverCDP(browser.wsEndpoint());

try {
  for (const screen of ['booking', 'cancellation']) {
    const driver = await browser.newPage();
    const page = cdp.contexts()[0].pages().at(-1);
    await page.route('**/*', async route => {
      const url = route.request().url();
      if (url.startsWith(root + '/')) return route.continue();
      const item = assets.get(url) ?? (url.startsWith('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/fonts/bootstrap-icons.woff2')
        ? ['bootstrap-icons.woff2', 'font/woff2'] : null);
      if (!item) return route.abort();
      await route.fulfill({path: path.join(process.env.MEDIHUB_BROWSER_ASSETS, item[0]), contentType: item[1],
        headers: {'Access-Control-Allow-Origin': '*'}});
    });
    await page.goto(root);
    await page.locator('.btn-navbar-login').click();
    await page.getByPlaceholder('Enter your username').fill('arjun');
    await page.locator('input[type=password]').fill(process.env.MEDIHUB_PHASE3_TEST_PASSWORD);
    await page.locator('form button[type=submit]').click();
    await page.getByRole('button', {name:'Logout'}).waitFor();
    const task = page.locator(screen === 'booking' ? '#book' : '#patient-appointments');
    if (screen === 'booking') {
      await page.getByRole('tab', {name:'Book Appointment'}).click();
      await task.getByText('Cardiology', {exact:true}).click();
      await task.getByText('Dr. Ajay Kumar', {exact:true}).click();
      await task.locator('input[type=date]').fill('2030-01-16');
      await task.getByRole('button', {name:/^09:00 AM /}).click();
      await task.locator('textarea').waitFor();
    } else {
      await page.getByRole('tab', {name:'My Appointments'}).click();
      await task.getByText('Booked', {exact:true}).waitFor();
    }
    await task.waitFor({state: 'visible'});
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({path:path.join(shots, `${screen}-audited.png`), fullPage:true, animations:'disabled'});
    const axe = await new AxeBuilder({page}).analyze();
    const flow = await startFlow(driver, {name:`MediHub ${screen} ${stage}`, config: {extends:'lighthouse:default',
      settings:{onlyCategories:['accessibility','best-practices','seo'], formFactor:'desktop',
        screenEmulation:{...viewport, deviceScaleFactor:1, mobile:false, disabled:false}}}});
    await flow.snapshot({stepName:`Authenticated ${screen} ${stage}`});
    const flowResult = await flow.createFlowResult();
    const {steps:[{lhr}]} = flowResult;
    if (lhr.finalDisplayedUrl !== page.url() || !await task.isVisible() || !await page.getByRole('button', {name:'Logout'}).isVisible()) {
      throw Error(`Authenticated screen evidence failed for ${screen}`);
    }
    await writeFile(path.join(out, `lighthouse-flow-${screen}.html`), await flow.generateReport());
    await writeFile(path.join(out, `lighthouse-flow-${screen}.json`), JSON.stringify(flowResult, null, 2));
    const filename = path.join(out, `lighthouse-${screen}.html`);
    await writeFile(filename, generateReport(lhr, 'html'));
    const reportPage = await cdp.contexts()[0].newPage({viewport});
    await reportPage.setViewportSize(viewport);
    await reportPage.goto(pathToFileURL(filename).href);
    await reportPage.locator('.lh-category-header').first().waitFor();
    await reportPage.screenshot({path:path.join(shots, `lighthouse-${screen}.png`), animations:'disabled'});
    await reportPage.close();
    await writeFile(path.join(out, `axe-${screen}.json`), JSON.stringify(axe, null, 2));
    await writeFile(path.join(out, `lighthouse-${screen}.json`), JSON.stringify(lhr, null, 2));
    await writeFile(path.join(out, `context-${screen}.json`), JSON.stringify({screen, stage, testedCommit, url:page.url(),
      authenticated:true, panel:await task.getAttribute('id'), viewport, chromeVersion:await browser.version(),
      lighthouseVersion:lhr.lighthouseVersion, auditMode:lhr.gatherMode, axeVersion:axe.testEngine.version}, null, 2));
    console.log(screen, Object.fromEntries(Object.entries(lhr.categories).map(([k,v])=>[k,v.score])), axe.violations.map(v=>v.id));
    await page.evaluate(() => localStorage.clear());
    await driver.close();
  }
} finally {
  await browser.close();
  await cdp.close();
}
