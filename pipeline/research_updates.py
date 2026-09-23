"""Read-only post-run analyses and concise research pages. No paid calls."""
import hashlib
import json
from statistics import mean
try:
    from pipeline.catalogue import ROOT,DOCS,esc,a,shell
except ModuleNotFoundError:
    from catalogue import ROOT,DOCS,esc,a,shell


def signal_audit(data):
    pairs={}
    for key,row in data['by_pair'].items():
        if row['set']!='hancock':continue
        target,partner=key.split(' | ')
        pair=tuple(sorted((target,partner)))
        p=pairs.setdefault(pair,dict(names=list(pair),completed=0,first=0,directions=[]))
        p['completed']+=row['n'];p['first']+=row['rank1']
        p['directions'].append(dict(target=target,partner=partner,completed=row['n'],first=row['rank1'],rate=row['rank1']/row['n']))
    records=sorted(pairs.values(),key=lambda p:(-p['first']/p['completed'],p['names']))
    completed=sum(p['completed'] for p in records);first=sum(p['first'] for p in records)
    for p in records:p['rate']=p['first']/p['completed']
    original=data['by_set']['hancock']['all']
    if (completed,first)!=(original['n'],original['rank1']):raise ValueError('Pair totals disagree with saved headline')
    return dict(status='Post-run descriptive audit, not a rerun or preregistered test',completed=completed,first=first,rate=first/completed,
                directed_pairings=sum(len(p['directions']) for p in records),unordered_pairings=len(records),
                equal_pair_mean=mean(p['rate'] for p in records),pairs=records,
                limitations=['The same figures recur across pairings; even the 11 pairs are not independent cultural histories.','Unequal completed lineups, modern summaries, recognisability and mismatched narrative roles remain.','Direction reversals used different candidate lineups; differences cannot be attributed to order alone.','No new AI judgments, revised p-values or worldwide rarity estimate.'])


def signal_page(r):
    rendered=[]
    for pair in r['pairs']:
        directions='<br>'.join('{} → {}: {}/{}'.format(esc(v['target']),esc(v['partner']),v['first'],v['completed']) for v in pair['directions'])
        rate=100*pair['rate']
        rendered.append(f'<tr><th scope="row">{esc(" / ".join(pair["names"]))}</th><td>{pair["first"]}/{pair["completed"]}</td><td><div class="rate-bar"><span style="width:{rate:.2f}%"></span></div>{rate:.1f}%</td><td>{directions}</td></tr>')
    rows=''.join(rendered)
    body=f'''<main id="main"><header class="dossier-heading cat-wrap"><a class="back-link" href="research-review.html">← Research</a><div class="micro">Teaching figures · post-run audit</div><h1>Where is the signal?</h1><p class="dossier-deck">The 62.5% result is real as a description of the saved lineups. It is not equally strong across the proposed pairs.</p></header><section class="cat-wrap lab-intro"><div class="lab-stat"><strong>{r['first']}/{r['completed']}</strong><span>Completed lineups with the proposed partner first</span></div><div><p>Those lineups reuse <b>{r['unordered_pairings']} pairings</b>, each tested in both directions. Several figures recur across pairs, so these are not 397 independent traditions—or even 11 independent histories.</p><p>Giving each pooled pair equal weight produces <b>{100*r['equal_pair_mean']:.1f}%</b>. The aggregate signal is not just an artefact of unequal completed counts. Its interpretation still depends on the sources, descriptions and competing candidates.</p></div></section><section class="cat-wrap lab-section"><h2>Open the average.</h2><p>First-place selections among completed lineups. Direction rows use different candidate lineups; this is not a controlled order experiment.</p><div class="table-scroll"><table class="feature-matrix signal-table"><thead><tr><th>Proposed pair</th><th>First / completed</th><th>Rate</th><th>Both directions</th></tr></thead><tbody>{rows}</tbody></table></div><p class="image-credit">Recalculated from the saved V1 <a href="https://github.com/ejhong/birdmen/blob/main/data/s4/results.json">by-pair results</a>. Failed or missing responses are not scored as last place.</p></section><section class="cat-wrap lab-section"><h2>The retest worth doing.</h2><p>Start with the <a href="civilisers.html">existing source passages</a>: compare complete episodes from teachers and founders, cite each proposed match on both sides, and score specific relationships separately from generic “teaching” or “travel”. Preserve uncertain readings.</p><p>Test a small reading rubric first, including changed actors and reversed arrival/departure checks. Then freeze a larger source collection, use close role-matched alternatives, and report every pair and its strongest competitors.</p><p>A high score would establish a resemblance within that collection. A shared origin would still require a historical argument.</p><div class="dossier-links"><a href="study4/redo-protocol-draft.md">Full source-based design ↗</a><a href="data/next-tests.md">Small next-step protocols ↗</a><a href="data/signal-audit.json">Download this audit ↗</a><a href="heroes.html">Original V1 results ↗</a></div></section></main>'''
    return shell('Where is the signal?','A descriptive audit of the 62.5% teaching-figure result, broken into its repeated pairings.',body,extra='<link rel="stylesheet" href="research.css">',current='research-review.html')


def bath_page(r):
    rows=''.join(f'<tr><th scope="row">{v["spacing_m"]:g} m</th><td>{v["valid_blocks"]:,}</td><td>{100*v["local_variance_retained"]:.2f}%</td><td>{100*v["depth_rmse_m"]:.2f} cm</td></tr>' for v in r['results'])
    native=r['grid'];coarse=r['results'][-1]
    body=f'''<main id="main"><header class="dossier-heading cat-wrap"><a class="back-link" href="submerged.html">← Submerged worlds</a><div class="micro">A first data experiment · actual AUV survey</div><h1>What a coarse<br>grid erases.</h1><p class="dossier-deck">Can the data preserve a small feature before we ask AI to find it?</p></header><section class="cat-wrap lab-intro"><div class="lab-stat"><strong>{100*coarse['local_variance_retained']:.1f}%</strong><span>Local relief variance retained at 115 m in this averaging test</span></div><div><p>We downloaded the <b>0.5 m AUV survey of the Baltic stone alignment</b> and averaged its measured cells at six resolutions. Small-scale relief fades while the average depth remains comparatively close.</p><p>This is a numerical resolution test. No AI detector, archaeological labels or new discovery are claimed. The published structure gives us a known site for developing a better benchmark.</p></div></section><section class="cat-wrap lab-section"><figure class="survey-figure"><a href="img/submerged/baltic-resolution.png"><img src="img/submerged/baltic-resolution.png" width="1890" height="1815" alt="The same measured Baltic survey at 0.5, 2, 10 and 115 metre spacing. Fine local relief fades under averaging; all panels use the same colour scale." loading="lazy"></a><figcaption>Measured survey, fixed colour scale. Blue background masks unsurveyed or insufficiently supported cells; it is not a deeper seabed. Relief is relative to a 10 m Gaussian neighbourhood. <a href="img/submerged/baltic-resolution.png">Download the figure</a>.</figcaption></figure></section><section class="cat-wrap lab-section"><h2>Detail loss, measured.</h2><div class="table-scroll"><table class="feature-matrix"><thead><tr><th>Grid spacing</th><th>Observed blocks</th><th>Local variance retained</th><th>Depth RMSE</th></tr></thead><tbody>{rows}</tbody></table></div><p>Depth RMSE measures disagreement with the original grid after averaging. It is <b>not survey accuracy</b>. Local variance includes noise and natural relief; it is <b>not the percentage of a wall recovered</b>.</p><details class="lab-method"><summary>Method, source and reproducibility</summary><p>{native['valid_cells']:,} valid cells in a {native['width']:,} × {native['height']:,} raster. Means use observed cells only, including partial blocks, aligned at the upper-left corner. Missing cells never become zero depths.</p><p>For the detail diagnostic, subtract a normalised Gaussian mean (σ = 10 m) from the original depth, then average that fixed residual field. Compare variance at the same {r['method']['local_support_cells']:,} well-supported source cells at every resolution. Plotted boundaries retain the original support mask.</p><p>The 115 m squares illustrate scale loss. They do not reproduce EMODnet’s angular grid, contributing surveys or interpolation. One site and one grid alignment do not establish a universal detection threshold.</p><p>Horizontal coordinates: WGS 84 / UTM zone 32N. The vertical datum was not resolved from the GeoTIFF metadata; this test uses within-survey differences, with no cross-dataset or ancient-shoreline inference.</p><p><a href="https://doi.iow.de/10.12754/DATA-2024-0001">J. Geersen, 2024 dataset · CC BY 4.0</a>. AUV survey by DLR, Littorina L0123 (2023). <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC10895374/">Original archaeological study</a>.</p><div class="dossier-links"><a href="data/submerged/resolution-result.json">Measurements, hashes &amp; metadata</a><a href="https://github.com/ejhong/birdmen/blob/main/pipeline/bathymetry_resolution.py">Reproduction code</a><a href="https://github.com/ejhong/birdmen/blob/main/data/submerged/baltic/data-2024-0001.zip">Retained source archive</a></div></details></section><section class="cat-wrap lab-section"><h2>A useful next AI test.</h2><p>Use independently labelled structure segments and difficult natural look-alikes from several surveys. Compare a model with simple relief and line-detection baselines. Hold out entire survey areas, score false alarms per surveyed area, and repeat at degraded resolutions.</p><p>The immediate gap is the benchmark: independently checked labels, geological controls and separate validation areas. Training and testing on neighbouring pixels of this one wall would overstate what the system learned.</p><p><a href="https://projects.au.dk/subnordica/research/work-package-3">SUBNORDICA is investigating AI methods for submerged Stone Age archaeology</a>. A small, documented benchmark here could complement that work.</p><p><a href="data/next-tests.md">The proposed protocol and other feasible tests →</a></p></section></main>'''
    return shell('What a coarse grid erases','A reproducible resolution experiment on the published Baltic AUV survey.',body,extra='<link rel="stylesheet" href="research.css">',current='research-review.html')


def outputs():
    original=ROOT/'data/s4/results.json';r=signal_audit(json.loads(original.read_text()))
    r['source_path']='data/s4/results.json';r['source_sha256']=hashlib.sha256(original.read_bytes()).hexdigest()
    bath=json.loads((ROOT/'research/submerged/resolution-result.json').read_text())
    if hashlib.sha256((ROOT/bath['source']['path']).read_bytes()).hexdigest()!=bath['source']['sha256']:
        raise ValueError('Survey archive changed')
    if hashlib.sha256((DOCS/bath['figure']['path']).read_bytes()).hexdigest()!=bath['figure']['sha256']:
        raise ValueError('Survey figure changed')
    return {DOCS/'signal-audit.html':signal_page(r),DOCS/'data/signal-audit.json':json.dumps(r,ensure_ascii=False,indent=2)+'\n',
            DOCS/'bathymetry-lab.html':bath_page(bath),DOCS/'data/submerged/resolution-result.json':json.dumps(bath,indent=2)+'\n',
            DOCS/'data/next-tests.md':(ROOT/'research/NEXT-TESTS.md').read_text()}
