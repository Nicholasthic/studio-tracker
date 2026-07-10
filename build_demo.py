#!/usr/bin/env python3
"""Build demo.html (marketing demo) from index.html (real tracker).

Transforms:
  1. Strip Supabase CDN script + credentials; cloud never initializes.
  2. Namespace every localStorage key with 'demo_' so the demo can never
     collide with real tracker data on the same origin.
  3. Replace real studio/staff names with fictional ones.
  4. Inject a DEMO MODE module: deterministic sample-data seeder, demo
     ribbon (tour + reset), pin hint, cloudUpdateStatus override.
  5. Replace INIT block: demoInit() instead of cloudInit()/Stripe.
"""
import sys, pathlib

SRC = pathlib.Path("/Users/nicko/Desktop/Studio Tracker/index.html")
DST = pathlib.Path("/Users/nicko/Desktop/Studio Tracker/demo.html")

html = SRC.read_text(encoding="utf-8")
errors = []

def rep(old, new, expect_min=1, expect_max=None):
    global html
    n = html.count(old)
    if n < expect_min or (expect_max is not None and n > expect_max):
        errors.append(f"count {n} for {old[:70]!r} (expected >={expect_min}" +
                      (f", <={expect_max}" if expect_max else "") + ")")
        return
    html = html.replace(old, new)

# ── 1. cloud stripping ──
rep('<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>',
    '<!-- demo build: no cloud library -->', 1, 1)
rep("const SB_URL = 'https://eyfgzzpusgdqhhypcaoz.supabase.co';", "const SB_URL = '';", 1, 1)
rep("const SB_KEY = 'sb_publishable_nNkUb72YURbfysUbgzNvAQ_sYi6C7F0';", "const SB_KEY = '';", 1, 1)
rep('<title>Lumin</title>', '<title>Lumin - Live Demo</title>', 1, 1)

# ── 2. storage namespacing ──
rep("function studioKey(base) { return base + '_' + activeStudio; }",
    "function studioKey(base) { return 'demo_' + base + '_' + activeStudio; }", 1, 1)
rep("'ejEntries_' + studioId", "'demo_ejEntries_' + studioId", 1, 1)
for key in ['ejStudios', 'ejActiveStudio', 'ejAutoLockMins', 'ejClickSound',
            'ejOwnerName', 'ejPendingBookingSystem', 'ejPendingStudioName',
            'ejAdminPIN', 'ejManagerPIN', 'ejStaffPINs', 'ejTheme', 'ejThemeMode']:
    rep(f"'{key}'", f"'demo_{key}'", 1)
# save click + "Saved" blip hook matches the demo_ key prefix instead
rep("k.indexOf('ej') === 0 && !cloudApplying", "k.indexOf('demo_ej') === 0 && !cloudApplying", 1, 1)

# ── 3. names ──
rep('Elyshia Jones Brow Studio', 'Luna Brow Studio', 1)
rep('Elyshia Jones Studio', 'Luna Brow Studio', 1)
rep('Elyshia Jones', 'Luna Brow Studio', 1)
rep('Elyshia', 'Ava', 1)
rep("'Angel'", "'Mia'", 1)
rep("'Ruby'", "'Chloe'", 1)
rep("'Saskia'", "'Sophie'", 1)

# ── 4 + 5. demo module + init ──
DEMO_MODULE = r"""
// ===================== DEMO MODE (sample data, no cloud) =====================
// Marketing demo build. Seeds a fictional studio (Luna Brow Studio) into
// 'demo_'-prefixed localStorage keys and never connects to the cloud.

function demoMulberry(seed) {
  return function () {
    seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function demoISO(d) {
  const p = n => String(n).padStart(2, '0');
  return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate());
}

const DEMO_STYLIST_NAMES = ['Ava', 'Mia', 'Chloe', 'Sophie'];

function demoSeedAll() {
  const R = demoMulberry(20260707);
  const pick = arr => arr[Math.floor(R() * arr.length)];
  const between = (a, b) => a + R() * (b - a);
  const K = base => 'demo_' + base + '_ej';

  localStorage.setItem('demo_ejStudios', JSON.stringify([{ id: 'ej', name: 'Luna Brow Studio', color: '#c9a96e' }]));
  localStorage.setItem(K('ejStylists'), JSON.stringify(DEMO_STYLIST_NAMES.map(n => ({ name: n, isContractor: false }))));
  localStorage.setItem(K('ejStudioRate'), '30');
  localStorage.setItem(K('ejContractorName'), 'Jess');
  localStorage.setItem('demo_ejOwnerName', 'Luna');
  localStorage.setItem('demo_ejAutoLockMins', '0');

  // ── Daily entries: Jan 1 2026 to today, closed Sun and Mon ──
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const start = new Date(2026, 0, 1);
  const end = today < new Date(2026, 11, 31) ? today : new Date(2026, 11, 31);
  const notesPool = ['Bridal party in today', 'Lash lift launch week', 'Instagram promo, new client special',
    'Market pop-up flyers went out', 'Team training morning, opened late', 'VIP loyalty night'];
  const entries = [];
  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    const dow = d.getDay();
    if (dow === 0 || dow === 1) continue;
    if (R() < 0.025) continue;
    const growth = 1 + d.getMonth() * 0.04;
    const isSat = dow === 6;
    const working = DEMO_STYLIST_NAMES.filter(() => R() < (isSat ? 0.97 : 0.8));
    if (!working.length) working.push('Ava');
    const sd = {};
    let ret = 0, retR = 0, newC = 0, newR = 0, svc = 0, prod = 0, prodQty = 0;
    working.forEach(name => {
      const clients = Math.round(between(3, isSat ? 8 : 6));
      const sRet = Math.round(clients * between(0.55, 0.8));
      const sNew = clients - sRet;
      const sRetR = Math.round(sRet * between(0.6, 0.85));
      const sNewR = Math.round(sNew * between(0.3, 0.6));
      const sSvc = Math.round(clients * between(95, 140) * growth / 5) * 5;
      const sQty = R() < 0.35 ? Math.round(between(1, 3)) : 0;
      const sProd = sQty ? Math.round(sQty * between(28, 70)) : 0;
      sd[name] = { c: clients, rr: sRetR, rnr: sRet - sRetR, nr: sNew, nrr: sNewR, nnr: sNew - sNewR,
                   svc: sSvc, prod: sProd, prodQty: sQty, tot: sSvc + sProd, shifts: 1 };
      ret += sRet; retR += sRetR; newC += sNew; newR += sNewR; svc += sSvc; prod += sProd; prodQty += sQty;
    });
    let contractor = null;
    if (isSat && R() < 0.6) {
      const cClients = Math.round(between(3, 6));
      const cSvc = Math.round(cClients * between(100, 130) / 5) * 5;
      contractor = { name: 'Jess', clients: cClients, svc: cSvc, prod: R() < 0.25 ? 45 : 0, cash: Math.round(cSvc * 0.2 / 5) * 5 };
    }
    entries.push({
      date: demoISO(d),
      ret, retR, retNR: ret - retR,
      newC, newR, newNR: newC - newR,
      prod, prodQty, svc, total: svc + prod,
      stylists: working.length,
      notes: R() < 0.07 ? pick(notesPool) : '',
      sd, contractor
    });
  }
  localStorage.setItem(K('ejEntries'), JSON.stringify(entries));

  // ── Client service log (with lapsed clients for follow-up features) ──
  const firstNames = ['Grace', 'Olivia', 'Ella', 'Isla', 'Zoe', 'Harper', 'Willow', 'Ivy', 'Matilda', 'Sienna',
    'Evie', 'Lily', 'Frankie', 'Billie', 'Daisy', 'Poppy', 'Georgia', 'Tahlia', 'Imogen', 'Ayla',
    'Charlotte', 'Amelia', 'Mackenzie', 'Indie', 'Lara', 'Maya', 'Bonnie', 'Stella', 'Kirra', 'Jade',
    'Holly', 'Paige', 'Tessa', 'Nina', 'Elsie', 'Freya', 'Marli', 'Sadie', 'Cleo', 'April',
    'Bree', 'Dana', 'Erin', 'Faith', 'Gemma', 'Heidi', 'Romy', 'Piper'];
  const lastInitials = 'ABCDEFGHJKLMNPRSTW';
  const services = ['Brow Lamination', 'Brow Sculpt + Tint', 'Hybrid Tint', 'Lash Lift', 'Brow Shape', 'Lash Lift + Tint'];
  const memos = ['Prefers mornings', 'Sensitive skin, patch tested', 'Referred by a friend', 'Loves the aftercare serum', 'Books 6 weeks ahead'];
  const usedNames = new Set();
  const clientLog = {};
  DEMO_STYLIST_NAMES.forEach(sname => {
    const rows = [];
    for (let i = 0; i < 12; i++) {
      let cname;
      do { cname = pick(firstNames) + ' ' + lastInitials[Math.floor(R() * lastInitials.length)] + '.'; } while (usedNames.has(cname));
      usedNames.add(cname);
      const daysAgo = Math.round(between(3, 130));
      const visit = new Date(today); visit.setDate(visit.getDate() - daysAgo);
      rows.push({
        name: cname + ' - ' + pick(services),
        consult: R() < 0.85, before: R() < 0.6, after: R() < 0.6, notes: R() < 0.4,
        rebook: daysAgo < 40 ? R() < 0.7 : R() < 0.35,
        product: R() < 0.3,
        memo: R() < 0.25 ? pick(memos) : '',
        lastVisit: demoISO(visit)
      });
    }
    clientLog[sname] = rows;
  });
  localStorage.setItem(K('ejClientServiceLog'), JSON.stringify(clientLog));

  // ── P&L inputs, goals, stock, business details ──
  localStorage.setItem(K('ejFixedExpenses'), JSON.stringify({
    rent: 2600, wages: 16800, stock: 850, marketing: 420, software: 190, insurance: 150, utilities: 260, professional: 120 }));
  localStorage.setItem(K('ejVariableDefaults'), JSON.stringify({ v_stock: 600, v_marketing: 250, v_supplies: 180 }));
  localStorage.setItem(K('ejGoals'), JSON.stringify({
    studio: { revenue: 52000, clients: 440, retRebookPct: 72, newRebookPct: 45, productRev: 2400 }, stylists: {} }));
  const ago = days => { const d = new Date(today); d.setDate(d.getDate() - days); return demoISO(d); };
  localStorage.setItem(K('ejStock'), JSON.stringify([
    { id: 'p_demo1', name: 'Brow Lamination Kit', sku: 'LBS-001', barcode: '', supplier: 'Luxe Beauty Supply', cost: 38, retail: 0,  stock: 6,  reorder: 3, reorderQty: 12, addedDate: ago(160) },
    { id: 'p_demo2', name: 'Hybrid Tint - Ash Brown', sku: 'LBS-002', barcode: '', supplier: 'Luxe Beauty Supply', cost: 14, retail: 0,  stock: 2,  reorder: 3, reorderQty: 10, addedDate: ago(150) },
    { id: 'p_demo3', name: 'Aftercare Serum', sku: 'LBS-003', barcode: '', supplier: 'Glow Wholesale', cost: 11, retail: 34, stock: 18, reorder: 6, reorderQty: 24, addedDate: ago(120) },
    { id: 'p_demo4', name: 'Brow Gel - Clear', sku: 'LBS-004', barcode: '', supplier: 'Glow Wholesale', cost: 8,  retail: 26, stock: 0,  reorder: 4, reorderQty: 12, addedDate: ago(110) },
    { id: 'p_demo5', name: 'Lash Lift Kit', sku: 'LBS-005', barcode: '', supplier: 'Luxe Beauty Supply', cost: 42, retail: 0,  stock: 5,  reorder: 2, reorderQty: 6,  addedDate: ago(90) },
    { id: 'p_demo6', name: 'Brow Pencil - Taupe', sku: 'LBS-006', barcode: '', supplier: 'Glow Wholesale', cost: 9,  retail: 29, stock: 14, reorder: 5, reorderQty: 15, addedDate: ago(75) }
  ]));
  localStorage.setItem(K('ejBizDetails'), JSON.stringify({
    'biz-name': 'Luna Brow Studio', 'biz-abn': '12 345 678 901', 'biz-phone': '0400 123 456',
    'biz-email': 'hello@lunabrow.example', 'biz-address': '12 Palm Street, Brisbane QLD 4000' }));
}

function demoResetData() {
  if (!confirm('Reset the demo back to fresh sample data?')) return;
  Object.keys(localStorage).filter(k => k.indexOf('demo_') === 0).forEach(k => localStorage.removeItem(k));
  location.reload();
}

// Demo build never connects to the cloud: keep the landing page hidden and
// show a friendly status in the sidebar instead. (Overrides the real one.)
function cloudUpdateStatus() {
  landingHide();
  const bar = document.getElementById('cloud-bar');
  if (bar) bar.innerHTML = '<div style="font-size:13px;color:var(--muted2)">Demo mode: cloud sync off</div>';
}

function demoRibbon() {
  if (document.getElementById('demo-ribbon')) return;
  const el = document.createElement('div');
  el.id = 'demo-ribbon';
  el.style.cssText = 'position:fixed;bottom:14px;left:50%;transform:translateX(-50%);z-index:99990;display:flex;align-items:center;gap:10px;background:var(--surface);border:1px solid var(--accent);border-radius:999px;padding:8px 10px 8px 18px;box-shadow:0 6px 24px rgba(0,0,0,.35);font-size:14px;color:var(--text);white-space:nowrap';
  el.innerHTML = '<span><strong style="color:var(--accent)">Demo</strong> · sample data only</span>' +
    '<button class="btn btn-ghost" style="font-size:13px;padding:6px 12px" onclick="startTour(\'owner\')">Take the tour</button>' +
    '<button class="btn btn-ghost" style="font-size:13px;padding:6px 12px" onclick="demoResetData()">Reset demo</button>';
  document.body.appendChild(el);
}

function demoPinHint() {
  const screen = document.getElementById('pin-lock-screen');
  if (!screen || document.getElementById('demo-pin-hint')) return;
  const el = document.createElement('div');
  el.id = 'demo-pin-hint';
  el.style.cssText = 'position:absolute;bottom:26px;left:0;right:0;text-align:center;font-size:14px;color:var(--muted)';
  el.textContent = 'Demo login: tap Owner, PIN 0000';
  screen.appendChild(el);
}

function demoInit() {
  try { if (!localStorage.getItem('demo_ejEntries_ej')) demoSeedAll(); } catch (e) { console.warn('demo seed failed', e); }
  try { localStorage.setItem('demo_ejActiveStudio', 'ej'); } catch (e) {}
  // Install the save hook (click + "Saved" blip). Cloud pushes can never fire:
  // cloudReady stays false in the demo build.
  try { cloudPatchLocalStorage(); } catch (e) {}
  reloadActiveStudioData();
  landingHide();
  pinLoginSuccess('admin');
  demoRibbon();
  demoPinHint();
}

"""

OLD_INIT = """// ===================== INIT =====================
renderSidebarStudios();
cloudInit();
try { handleStripeReturn(); } catch (e) {}
"""
NEW_INIT = DEMO_MODULE + """// ===================== INIT (DEMO) =====================
renderSidebarStudios();
demoInit();
"""
rep(OLD_INIT, NEW_INIT, 1, 1)

if errors:
    print("BUILD FAILED:")
    for e in errors:
        print(" -", e)
    sys.exit(1)

# safety sweep: no real names / credentials left
for bad in ['Elyshia', 'Saskia', 'eyfgzzpusgdqhhypcaoz', 'sb_publishable']:
    if bad in html:
        print("LEAK:", bad); sys.exit(1)

DST.write_text(html, encoding="utf-8")
print(f"OK -> {DST} ({len(html)} bytes)")
