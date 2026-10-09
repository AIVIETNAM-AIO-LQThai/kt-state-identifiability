"""Read-only Opus check (X4-F09): does a damped Newton polish, or a higher L-BFGS iteration cap, reach a certified optimum for the
2PL B2 fits that stop at 3000 iterations?  Usage: polish_check.py CASE   (A = V5 N300 r0 recovery; B = V4 N1000 r1 warp)."""
import sys, time, json
import numpy as np
from kt_trial.composite_likelihood import pair_counts
from kt_trial.config import load_yaml, rng_for
from kt_trial.fit import _one_start, make_starts
from kt_trial.moments import Theta
from difficulty_free import jobs as DJ
from discrimination_free.fit import fit_2pl, B_JITTER_SD, W_JITTER_SD
from discrimination_free.model import Objective2PL, Param2PL

case = sys.argv[1]
st = load_yaml('configs/experiment_04/stage_pilot.yaml')
sid, N, rep, tag = {'A': ('V5', 300, 0, ('2pl',)), 'B': ('V4', 1000, 1, ('2pl',))}[case]
spec = DJ.spec_of(st, sid); cfg, ts, ids, ds = DJ.make_dataset(st, spec, N, rep)
pc = pair_counts(ds.Y, ds.template_id, len(ts)); K, ms = 4, st['master_seed']
skey = (sid, N, rep) + tag if case == 'A' else (sid, N, rep, '2pl')
cf = cfg['fit']

def active(pm, x, th):
    tol = cf['boundary_tol']
    a = [i for i in range(pm.n) if pm.lb[i] + tol < x[i] < pm.ub[i] - tol]
    if th.sigma2_F <= tol:
        a = [i for i in a if pm.names[i] != 'tau_F']
    return a

def hess(obj, x, act):
    S = obj.scale; H = np.zeros((len(act), len(act)))
    for k, i in enumerate(act):
        h = cf['hess_step'] * max(1.0, abs(x[i])); xp, xm = x.copy(), x.copy(); xp[i] += h; xm[i] -= h
        H[k] = ((obj(xp)[1] - obj(xm)[1]) / (2 * h))[act] * S
    return 0.5 * (H + H.T)

def polish(pm, obj, x, steps=8):
    x = np.array(x, float); hist = []
    for s in range(steps):
        th = pm.x_to_theta(x); act = active(pm, x, th)
        f, g = obj(x); g = g[act] * obj.scale
        H = hess(obj, x, act); ev = np.linalg.eigvalsh(H); mu = 0.0 if ev.min() > 1e-8 * ev.max() else (1e-8 * ev.max() - ev.min())
        d = -np.linalg.solve(H + mu * np.eye(len(act)), g); dec = float(-0.5 * g @ d)
        hist.append(dict(step=s, ll=-f * obj.scale, dec=dec, min_eig=float(ev.min()), damped=mu > 0))
        if dec < 1e-7:
            break
        t = 1.0
        while t > 1e-4:
            xn = x.copy(); xn[act] += t * d; xn = np.clip(xn, pm.lb, pm.ub)
            if obj(xn)[0] < f:
                x = xn; break
            t /= 2
        else:
            hist.append(dict(step=s, note='line search failed')); break
    return x, hist

out = {'case': case}
t0 = time.time()
g1 = fit_2pl('B1', ts, pc, cf, K, ids, 48, skey, ms)
out['B1'] = dict(ll=g1['ll'], conv=g1['converged'], dec=g1['certificate']['newton_decrement'], sec=time.time() - t0)
pm = Param2PL('B2', K, 48); obj = Objective2PL(pm, ts, pc, ids)
x1p, h1 = polish(Param2PL('B1', K, 48), Objective2PL(Param2PL('B1', K, 48), ts, pc, ids), np.array(g1['x']))
out['B1_polish'] = h1[-1]
rng = rng_for(ms, 'fit2pl', 'B2', *skey)
warm = (Theta.from_dict(g1['theta']), np.array(g1['b']), np.array(g1['lam'])); w0 = pm.P.T @ np.log(warm[2])
starts = []
for i, xt in enumerate(make_starts('B2', pm.base, cf, K, rng, warm[0])):
    bj = warm[1] if i == 0 else warm[1] + rng.normal(0.0, B_JITTER_SD, size=48)
    wj = w0 if i == 0 else w0 + rng.normal(0.0, W_JITTER_SD, size=47)
    starts.append(np.clip(np.concatenate([xt, bj, wj]), pm.lb, pm.ub))
out['B2_starts'] = []
for i, x0 in enumerate(starts):
    t1 = time.time(); r = _one_start(obj, x0, cf); tr = time.time() - t1
    t2 = time.time(); xp, h = polish(pm, obj, np.array(r['x'])); tp = time.time() - t2
    thp = pm.x_to_theta(xp)
    out['B2_starts'].append(dict(start=i, nit=r['n_iter'], msg=r['message'][:40], ll=r['ll'], sec=tr, polish_ll=h[-1].get('ll'),
                                 polish_dec=h[-1].get('dec'), polish_steps=len(h), polish_sec=tp, sigma2_F=thp.sigma2_F, tau_F=thp.tau_F,
                                 sigma2_F_lbfgs=pm.x_to_theta(np.array(r['x'])).sigma2_F))
    print(json.dumps(out['B2_starts'][-1]), flush=True)
t3 = time.time(); r = _one_start(obj, starts[0], dict(cf, max_iter=30000))
out['B2_start0_maxiter30000'] = dict(nit=r['n_iter'], msg=r['message'][:40], ll=r['ll'], sec=time.time() - t3, conv=r['converged'])
best_pol = max(s['polish_ll'] for s in out['B2_starts'])
out['T_lbfgs'] = 2 * (max(s['ll'] for s in out['B2_starts']) - g1['ll'])
out['T_polished'] = 2 * (best_pol - h1[-1]['ll'])
print(json.dumps(out, indent=1, default=float))
