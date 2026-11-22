/*
 * Capture and measure the screens of an app, the same way for every app.
 * Used for the UI review of 2026-11 and for the screenshots a
 * pull request that changes a screen attaches. See README.md.
 *
 *   const { run } = require('<path>/shoot.cjs')
 *   run({
 *     app: 'nutrition',
 *     base: 'http://127.0.0.1:5172',
 *     out: '<a folder outside the repository>',
 *     headers: { 'Remote-User': 'demo' },       // optional, sent with every request
 *     locale: 'de-DE',                           // browser language
 *     beforeEach: async (context) => {},         // optional: cookies, routes, localStorage
 *     only: ['today'],                           // optional: only these screens
 *     screens: [
 *       { name: 'today', path: '/' },
 *       { name: 'food-form-open', path: '/foods', prepare: async (page) => { await page.getByRole('button', { name: 'Neu' }).click() } },
 *       { name: 'today-error', path: '/', route: async (page) => { await page.route('**\/api/today', r => r.fulfill({ status: 500, body: '{}' })) } },
 *       { name: 'today-loading', path: '/', route: async (page) => { await page.route('**\/api/today', () => {}) }, settle: 800 },
 *     ],
 *   })
 *
 * Each screen is captured at 412 and 1280 px wide, light and dark (4 PNGs),
 * full page, deviceScaleFactor 2. `route` runs before navigation (mock or stall
 * requests), `prepare` after the page has settled (open forms, panels, lists).
 * Measurements are taken in light at both widths, axe in light and dark at 412.
 * Output: <out>/shots/<name>--<width>--<scheme>.png and <out>/measure.json.
 * Per screen also: `locale`, `waitFor` (a selector), `skipFocus`, `note`.
 */
const { chromium } = require('playwright')
const fs = require('node:fs')
const path = require('node:path')

// axe-core is optional: without it the accessibility rules are skipped and measure.json says so.
let AXE = null
try {
  AXE = require.resolve('axe-core/axe.min.js')
} catch {
  console.warn('shoot: axe-core is not installed here (npm ci in this folder); accessibility rules are skipped')
}
const WIDTHS = [
  { width: 412, height: 915 },
  { width: 1280, height: 800 },
]
const SCHEMES = ['light', 'dark']

/* Runs in the page. Returns the facts the cross-app comparison needs. */
function measureInPage() {
  const visible = (el) => {
    const r = el.getBoundingClientRect()
    const s = getComputedStyle(el)
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && Number(s.opacity) > 0
  }
  const text = (el) => (el.getAttribute('aria-label') || el.innerText || el.value || el.getAttribute('title') || '').trim().replace(/\s+/g, ' ').slice(0, 40)
  const px = (v) => Math.round(parseFloat(v) * 10) / 10
  const box = (el) => {
    const r = el.getBoundingClientRect()
    return { w: Math.round(r.width), h: Math.round(r.height) }
  }
  const style = (el) => {
    const s = getComputedStyle(el)
    return {
      ...box(el),
      font: `${px(s.fontSize)}px/${s.fontWeight}`,
      radius: s.borderTopLeftRadius,
      padding: `${s.paddingTop} ${s.paddingRight}`,
      bg: s.backgroundColor,
      color: s.color,
      border: s.borderTopWidth === '0px' ? 'none' : `${s.borderTopWidth} ${s.borderTopColor}`,
    }
  }
  const group = (els) => {
    const seen = new Map()
    for (const el of els) {
      const st = style(el)
      const key = JSON.stringify({ ...st, w: undefined })
      const hit = seen.get(key)
      if (hit) {
        hit.count += 1
        if (hit.examples.length < 3) hit.examples.push(text(el))
      } else seen.set(key, { ...st, w: undefined, count: 1, examples: [text(el)], cls: el.className && String(el.className).slice(0, 60) })
    }
    return [...seen.values()]
  }
  const all = (sel) => [...document.querySelectorAll(sel)].filter(visible)

  const html = document.documentElement
  const body = getComputedStyle(document.body)
  const interactive = all('a[href], button, input:not([type=hidden]), select, textarea, summary, [role=button], [role=tab], [role=link], [tabindex]:not([tabindex="-1"])')
  const small = interactive
    .map((el) => ({ el, ...box(el) }))
    .filter(({ el, w, h }) => {
      // inline links inside running text are exempt (WCAG 2.5.8)
      if (el.tagName === 'A' && getComputedStyle(el).display === 'inline' && el.parentElement && el.parentElement.innerText.trim().length > el.innerText.trim().length + 20) return false
      if (el.tagName === 'INPUT' && ['checkbox', 'radio'].includes(el.type)) {
        const label = el.closest('label') || (el.id && document.querySelector(`label[for="${CSS.escape(el.id)}"]`))
        if (label) {
          const lb = label.getBoundingClientRect()
          return lb.height < 44 || lb.width < 44
        }
      }
      return w < 44 || h < 44
    })
    .map(({ el, w, h }) => ({ tag: el.tagName.toLowerCase(), text: text(el), w, h }))

  const navs = all('nav, [role=navigation]').map((el) => {
    const r = el.getBoundingClientRect()
    const s = getComputedStyle(el)
    const where = s.position === 'fixed' || s.position === 'sticky' ? `${s.position} ${r.top < innerHeight / 2 ? 'top' : 'bottom'}` : r.width < innerWidth * 0.5 && r.height > innerHeight * 0.5 ? 'side' : 'in flow'
    return { label: el.getAttribute('aria-label'), where, ...box(el), top: Math.round(r.top), left: Math.round(r.left), items: [...el.querySelectorAll('a, button')].filter(visible).map(text).slice(0, 12) }
  })
  const header = document.querySelector('header')
  const headings = ['h1', 'h2', 'h3'].map((t) => {
    const el = all(t)[0]
    if (!el) return null
    const s = getComputedStyle(el)
    return { tag: t, text: text(el), font: `${px(s.fontSize)}px/${s.fontWeight}`, lineHeight: s.lineHeight, marginTop: s.marginTop, marginBottom: s.marginBottom, color: s.color }
  }).filter(Boolean)
  const main = document.querySelector('main') || document.body
  const mainStyle = getComputedStyle(main)

  return {
    lang: html.lang,
    title: document.title,
    theme: html.getAttribute('data-theme'),
    viewport: innerWidth,
    scrollWidth: html.scrollWidth,
    overflowX: html.scrollWidth > innerWidth + 1,
    pageHeight: html.scrollHeight,
    body: { fontFamily: body.fontFamily.slice(0, 80), fontSize: body.fontSize, lineHeight: body.lineHeight, color: body.color, bg: body.backgroundColor },
    main: { maxWidth: mainStyle.maxWidth, paddingInline: `${mainStyle.paddingLeft} ${mainStyle.paddingRight}`, width: Math.round(main.getBoundingClientRect().width) },
    header: header && visible(header) ? { ...box(header), position: getComputedStyle(header).position, text: text(header) } : null,
    navs,
    headings,
    buttons: group(all('button, a.button, a.btn, [role=button], input[type=submit]')),
    fields: group(all('input:not([type=hidden]):not([type=checkbox]):not([type=radio]):not([type=submit]), select, textarea')),
    labels: group(all('label')).slice(0, 6),
    tables: all('table').map((t) => ({ ...box(t), cols: t.rows[0] ? t.rows[0].cells.length : 0, scrollBox: (() => { let p = t.parentElement; while (p && p !== document.body) { if (/(auto|scroll)/.test(getComputedStyle(p).overflowX)) return true; p = p.parentElement } return false })() })),
    lists: all('ul, ol').filter((l) => l.children.length > 1 && !l.closest('nav')).slice(0, 6).map((l) => { const li = l.children[0]; const s = getComputedStyle(li); return { cls: String(l.className).slice(0, 50), items: l.children.length, rowHeight: Math.round(li.getBoundingClientRect().height), rowPadding: `${s.paddingTop} ${s.paddingRight}`, rowBorder: s.borderBottomWidth, rowBg: s.backgroundColor, rowRadius: s.borderTopLeftRadius } }),
    dialogs: all('dialog, [role=dialog], [role=alertdialog]').map((d) => ({ tag: d.tagName.toLowerCase(), ...box(d), radius: getComputedStyle(d).borderTopLeftRadius, labelled: !!(d.getAttribute('aria-label') || d.getAttribute('aria-labelledby')) })),
    alerts: all('[role=alert], [role=status], [aria-live]').map((a) => ({ role: a.getAttribute('role') || `aria-live=${a.getAttribute('aria-live')}`, text: text(a), bg: getComputedStyle(a).backgroundColor, color: getComputedStyle(a).color })).filter((a) => a.text).slice(0, 8),
    images: { svg: all('svg').length, img: all('img').length, iconFontOrEmoji: /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/u.test(document.body.innerText) },
    interactiveCount: interactive.length,
    smallTargets: small.slice(0, 40),
    smallTargetCount: small.length,
  }
}

/* Tab through the page and report focused elements without a visible indicator. */
async function focusCheck(page, steps = 15) {
  const missing = []
  let reached = 0
  for (let i = 0; i < steps; i += 1) {
    await page.keyboard.press('Tab')
    const r = await page.evaluate(() => {
      const el = document.activeElement
      if (!el || el === document.body) return null
      const s = getComputedStyle(el)
      const outline = s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0
      const ring = s.boxShadow && s.boxShadow !== 'none'
      return { tag: el.tagName.toLowerCase(), text: (el.getAttribute('aria-label') || el.innerText || el.getAttribute('name') || '').trim().slice(0, 40), outline: outline ? `${s.outlineWidth} ${s.outlineStyle} ${s.outlineColor} offset ${s.outlineOffset}` : null, ring: ring ? s.boxShadow.slice(0, 60) : null }
    })
    if (!r) continue
    reached += 1
    if (!r.outline && !r.ring) missing.push(r)
  }
  const sample = await page.evaluate(() => {
    const el = document.activeElement
    if (!el || el === document.body) return null
    const s = getComputedStyle(el)
    return `${s.outlineWidth} ${s.outlineStyle} ${s.outlineColor} offset ${s.outlineOffset}`
  })
  return { reached, missing, sampleOutline: sample }
}

async function axe(page) {
  if (!AXE) return [{ id: 'axe-not-installed', help: 'run npm ci in the capture folder' }]
  try {
    await page.addScriptTag({ path: AXE })
    const result = await page.evaluate(async () => {
      const r = await window.axe.run(document, { resultTypes: ['violations'] })
      return r.violations.map((v) => ({ id: v.id, impact: v.impact, help: v.help, count: v.nodes.length, nodes: v.nodes.slice(0, 4).map((n) => ({ target: String(n.target[0]).slice(0, 90), summary: (n.failureSummary || '').replace(/\s+/g, ' ').slice(0, 220) })) }))
    })
    return result
  } catch (error) {
    return [{ id: 'axe-failed', help: String(error).slice(0, 200) }]
  }
}

async function run({ app, base, out, headers, locale = 'de-DE', beforeEach, screens, only }) {
  fs.mkdirSync(path.join(out, 'shots'), { recursive: true })
  const browser = await chromium.launch()
  const results = {}
  const baseOrigin = new URL(base).origin
  for (const screen of screens) {
    if (only && !only.includes(screen.name)) continue
    const entry = { path: screen.path, note: screen.note, measure: {}, axe: {}, console: [], externalRequests: [], failedRequests: [] }
    for (const viewport of WIDTHS) {
      for (const scheme of SCHEMES) {
        const context = await browser.newContext({ viewport, deviceScaleFactor: 2, colorScheme: scheme, locale: screen.locale || locale, extraHTTPHeaders: headers, hasTouch: viewport.width < 600, reducedMotion: 'reduce' })
        if (beforeEach) await beforeEach(context, { scheme, viewport })
        const page = await context.newPage()
        const first = viewport.width === 412 && scheme === 'light'
        page.on('console', (m) => { if (first && m.type() === 'error') entry.console.push(m.text().slice(0, 200)) })
        page.on('pageerror', (e) => { if (first) entry.console.push(`pageerror: ${String(e).slice(0, 200)}`) })
        page.on('request', (r) => { const u = r.url(); if (first && /^https?:/.test(u) && new URL(u).origin !== baseOrigin && !/^https?:\/\/(127\.0\.0\.1|localhost)[:/]/.test(u)) entry.externalRequests.push(`${r.resourceType()} ${u.slice(0, 120)}`) })
        page.on('response', (r) => { if (first && r.status() >= 400) entry.failedRequests.push(`${r.status()} ${r.url().replace(baseOrigin, '').slice(0, 100)}`) })
        try {
          if (screen.route) await screen.route(page)
          await page.goto(base + screen.path, { waitUntil: 'domcontentloaded', timeout: 20000 })
          if (screen.settle) await page.waitForTimeout(screen.settle)
          else await page.waitForLoadState('networkidle', { timeout: 8000 }).catch(() => {})
          if (screen.waitFor) await page.waitForSelector(screen.waitFor, { timeout: 8000 }).catch(() => {})
          if (screen.prepare) await screen.prepare(page, { scheme, viewport })
          await page.waitForTimeout(250)
          const file = path.join(out, 'shots', `${screen.name}--${viewport.width}--${scheme}.png`)
          await page.screenshot({ path: file, fullPage: true })
          if (scheme === 'light') entry.measure[viewport.width] = await page.evaluate(measureInPage)
          if (viewport.width === 412) entry.axe[scheme] = await axe(page)
          if (first && !screen.skipFocus) entry.focus = await focusCheck(page)
        } catch (error) {
          entry.error = `${viewport.width}/${scheme}: ${String(error).slice(0, 300)}`
          console.error(`[${app}] ${screen.name} ${viewport.width} ${scheme}: ${String(error).split('\n')[0]}`)
        }
        await context.close()
      }
    }
    results[screen.name] = entry
    const m = entry.measure[412]
    console.log(`[${app}] ${screen.name}: ${m ? `overflow412=${m.overflowX} small=${m.smallTargetCount}/${m.interactiveCount}` : 'no measure'} axeL=${(entry.axe.light || []).map((v) => `${v.id}×${v.count}`).join(',') || '-'} axeD=${(entry.axe.dark || []).map((v) => `${v.id}×${v.count}`).join(',') || '-'} focusMissing=${entry.focus ? entry.focus.missing.length : '-'} ext=${entry.externalRequests.length} console=${entry.console.length}`)
  }
  await browser.close()
  const file = path.join(out, 'measure.json')
  const previous = fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, 'utf8')) : {}
  fs.writeFileSync(file, JSON.stringify({ ...previous, ...results }, null, 1))
  return results
}

module.exports = { run }
