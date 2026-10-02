"""L1.3: kiểm và tổng hợp CSV theo seed; không chạy lại outcome."""
import csv
import hashlib
import itertools
import json
import platform
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import scipy

from experiments.n02_source_factorial import contrasts, write_csv

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'experiments/results'


def read(name):
    with (OUT/name).open() as f:
        return list(csv.DictReader(f))


def ci(x):
    m=float(np.mean(x)); half=float(stats.t.ppf(.975,len(x)-1)*np.std(x,ddof=1)/np.sqrt(len(x)))
    return m,half


def main():
    regs,effects,runs={},{},{}
    for prior in (.80,.70):
        tag=f'n02_H0.5_rho{prior:.2f}'
        rows=read(tag+'_seeds.csv')
        assert len(rows)==80
        reg={c:np.array([float(r['regret_ms']) for r in sorted(rows,key=lambda r:int(r['seed']))
                        if tuple(int(r[f]) for f in 'SMP')==c]) for c in itertools.product((0,1),repeat=3)}
        assert all(len(x)==10 and np.isfinite(x).all() for x in reg.values())
        effect=contrasts(reg)
        recorded=read(tag+'_contrasts_seeds.csv')
        for key,x in effect.items():
            values=np.array([float(r['value_ms']) for r in sorted(recorded,key=lambda r:int(r['seed'])) if r['contrast']==key])
            np.testing.assert_allclose(x,values,atol=1e-12,rtol=0)
        for order in itertools.permutations('SMP'):
            np.testing.assert_allclose(sum(effect[f"ladder:{''.join(order)}:{f}"] for f in order),reg[1,1,1]-reg[0,0,0],atol=1e-12)
        regs[prior],effects[prior]=reg,effect
        runs[prior]=json.loads((OUT/(tag+'_run.json')).read_text())
    assert runs[.8]['world_hashes']==runs[.7]['world_hashes']
    for s,m in itertools.product((0,1),repeat=2):
        np.testing.assert_array_equal(regs[.8][s,m,0],regs[.7][s,m,0])
    print('PASS: cùng hash thế giới giữa 2 mức sai tham số; P=0 trùng từng bit; mọi bậc thang/Shapley cộng đúng theo seed.')
    nested_rows=read('n02b_measurement_split_seeds.csv')
    assert len(nested_rows)==120
    modes=list(dict.fromkeys((r['A'],r['B']) for r in nested_rows))
    nested={}
    split_summary=[]
    for a,b in modes:
        for s in (0,1):
            x=np.array([float(r['regret_ms']) for r in sorted(nested_rows,key=lambda r:int(r['seed']))
                        if r['A']==a and r['B']==b and int(r['S'])==s])
            assert len(x)==10 and np.isfinite(x).all()
            nested[s,a,b]=x
            m,h=ci(x)
            split_summary.append(dict(S=s,A=a,B=b,mean_ms=m,ci95_half_ms=h))
    for s in (0,1):
        np.testing.assert_array_equal(nested[s,'inst','inst'],regs[.8][s,0,0])
        np.testing.assert_array_equal(nested[s,'noisy','noisy'],regs[.8][s,1,0])
    print('PASS: 4 endpoint n02b trùng từng bit với n02 theo seed; 120 dòng đo lồng nhau hữu hạn.')
    write_csv(OUT/'n02b_measurement_split_summary.csv',split_summary)
    split_effects={}
    for s in (0,1):
        n=lambda a,b:nested[s,a,b]
        split_effects[s,'aggregate_B']=n('inst','win')-n('inst','inst')
        split_effects[s,'aggregate_A']=n('win','inst')-n('inst','inst')
        split_effects[s,'noise_A']=n('noisy','inst')-n('win','inst')
        split_effects[s,'measurement_A']=n('noisy','inst')-n('inst','inst')
        split_effects[s,'aggregate_AB']=n('win','win')-n('inst','inst')
        split_effects[s,'noise_AB']=n('noisy','noisy')-n('win','win')
        split_effects[s,'noise_A_minus_aggregate_B']=split_effects[s,'noise_A']-split_effects[s,'aggregate_B']
    write_csv(OUT/'n02b_split_contrasts.csv',[dict(S=s,contrast=k,mean_ms=ci(x)[0],ci95_half_ms=ci(x)[1]) for (s,k),x in split_effects.items()])

    comparisons=[]
    def compare(name,value,expected,tolerance=.0005):
        comparisons.append(dict(metric=name,local=float(value),lesson=expected,delta=float(value)-expected,
                                tolerance=tolerance,match=abs(float(value)-expected)<=tolerance))
    expected_means=[.355,.353,3.671,3.675,3.156,3.224,4.562,4.823]
    expected_halves=[.038,.039,.292,.295,.314,.351,.343,.445]
    for c,m,h in zip(itertools.product((0,1),repeat=3),expected_means,expected_halves):
        actual,half=ci(regs[.8][c])
        compare(f'rho0.80 {c} mean',actual,m)
        compare(f'rho0.80 {c} CI95 half',half,h)
    for key,mean,half in [('interaction:S*P|M=0',.944,.345),('interaction:S*P|M=1',1.276,.426)]:
        m,h=ci(effects[.7][key]);compare(f'rho0.70 {key} mean',m,mean);compare(f'rho0.70 {key} CI95 half',h,half)
    compare('rho0.70 Shapley P',effects[.7]['shapley:P'].mean(),.68,.005)
    for mode,exp in [(('inst','inst'),(.355,3.156)),(('win','win'),(2.900,3.899)),(('noisy','noisy'),(3.671,4.562)),(('inst','win'),(2.391,3.508)),(('noisy','inst'),(.785,4.164))]:
        for s,expected in enumerate(exp):
            compare(f'n02b S={s} {mode}',nested[s,*mode].mean(),expected)
    write_csv(OUT/'n02_lesson_comparison.csv',comparisons)
    for r in comparisons:
        if not r['match']:
            print(f"DIFF {r['metric']}: local={r['local']:.6f}, lesson={r['lesson']}, delta={r['delta']:+.6f}")
    r=regs[.8];y00,y10,y01,y11=(r[c] for c in ((0,0,0),(1,0,0),(0,1,0),(1,1,0)))
    sm=dict(S_first=y10-y00,M_second=y11-y10,M_first=y01-y00,S_second=y11-y01,
            interaction=y11-y10-y01+y00,fix_S=y11-y01,fix_M=y11-y10,fix_both=y11-y00,
            shapley_S=((y10-y00)+(y11-y01))/2,shapley_M=((y01-y00)+(y11-y10))/2)
    write_csv(OUT/'n02_SM_P0_summary.csv',[dict(contrast=k,mean_ms=ci(x)[0],ci95_half_ms=ci(x)[1]) for k,x in sm.items()])
    fig,axes=plt.subplots(1,2,figsize=(11,4.7),layout='constrained')
    x=np.arange(2)
    S=np.array([sm['S_first'].mean(),sm['S_second'].mean()]);M=np.array([sm['M_second'].mean(),sm['M_first'].mean()])
    axes[0].bar(x,S,color='#507c9b',label='S: tuổi dữ liệu')
    axes[0].bar(x,M,bottom=S,color='#df994c',label='M: gộp + nhiễu')
    for i in (0,1):
        axes[0].text(i,S[i]/2,f'{S[i]:.3f}',ha='center',va='center',color='white')
        axes[0].text(i,S[i]+M[i]/2,f'{M[i]:.3f}',ha='center',va='center')
    axes[0].set(xticks=x,xticklabels=['Thứ tự S → M','Thứ tự M → S'],ylabel='Phần góp regret (ms/lần kiểm)',ylim=(0,5.5),title='Bậc thang hai nguồn, P=0')
    axes[0].legend(frameon=False,loc='upper left')
    for a,b,label,color in [('inst','inst','Tức thời / tức thời','#507c9b'),('win','win','Trung bình / trung bình','#75ab82'),('noisy','noisy','Đếm / đếm','#df994c')]:
        m=np.array([nested[s,a,b].mean() for s in (0,1)])
        err=np.array([ci(nested[s,a,b])[1] for s in (0,1)])
        offset={'inst':-.25,'win':0,'noisy':.25}[a]
        axes[1].bar(x+offset,m,.24,yerr=err,capsize=3,label=label,color=color)
    axes[1].set(xticks=x,xticklabels=['S tắt','S bật'],ylabel='Regret (ms/lần kiểm)',ylim=(0,6.8),title='Ba mức phép đo A / B; CI95 theo seed')
    axes[1].legend(frameon=False,loc='upper left',fontsize=9)
    for ax in axes:ax.spines[['top','right']].set_visible(False)
    fig.savefig(OUT/'n02_decomposition.png',dpi=160);plt.close(fig)

    report=['# L1.3 — Nguồn sai và phân rã: kết quả local (2026-10-02)','',
            '**Đã chạy n02 (ρ̄_B sai 0,80 và 0,70), n02b, tạo N2 và realism_sources.md.**', '',
            '10 seed pilot 9101–9110, POS_probeB, H=0,5 s, a=0,05 s, G_all, luôn ở A, PSA, luật Ī>0. '
            '40.000 epoch nền dùng chung trong n02; 8 cấu hình × 2 mức tham số = 160 đo theo seed. '
            'n02b có 120 đo theo seed (5 trường hợp của lesson + win/inst bổ sung, mỗi trường hợp 2 mức S). '
            'Đã thấy outcome trong lesson; không phải tiền đăng ký mù.','',
            '![Bậc thang và đo lồng nhau](n02_decomposition.png)','',
            '## 1. Regret factorial (ms/lần kiểm; trung bình ± nửa độ rộng CI95 t theo 10 seed)','',
            '| S M P | Twin tin B=0,80 | Twin tin B=0,70 |','|---|---:|---:|']
    for cfg in itertools.product((0,1),repeat=3):
        a,ah=ci(regs[.8][cfg]);b,bh=ci(regs[.7][cfg])
        report.append(f'| {cfg} | {a:.6f} ± {ah:.6f} | {b:.6f} ± {bh:.6f} |')
    report+=['','## 2. Bậc thang, tương tác và Shapley','',
             '| Thứ tự, P=0 | S (ms) | M (ms) |','|---|---:|---:|',
             f"| S → M | {sm['S_first'].mean():.6f} | {sm['M_second'].mean():.6f} |",
             f"| M → S | {sm['S_second'].mean():.6f} | {sm['M_first'].mean():.6f} |",'',
             f"S×M tại P=0 = **{sm['interaction'].mean():.6f} ± {ci(sm['interaction'])[1]:.6f} ms** (hiệu của hiệu). "
             f"Shapley hai nguồn: S={sm['shapley_S'].mean():.6f}, M={sm['shapley_M'].mean():.6f}; tổng={sm['fix_both'].mean():.6f} ms.", '',
             f"Từ S=M=1, sửa riêng S cứu {sm['fix_S'].mean():.6f} ms; sửa riêng M cứu {sm['fix_M'].mean():.6f}; "
             f"sửa cả hai cứu {sm['fix_both'].mean():.6f} ms. Sửa riêng vẫn có lợi trong ô này; không gọi là vô ích.", '',
             '| Shapley ba nguồn (ms, ±CI95 paired) | B=0,80 | B=0,70 |','|---|---:|---:|']
    for f in 'SMP':
        a,ah=ci(effects[.8]['shapley:'+f]);b,bh=ci(effects[.7]['shapley:'+f])
        report.append(f'| {f} | {a:.6f} ± {ah:.6f} | {b:.6f} ± {bh:.6f} |')
    report+=['','Shapley ba nguồn khác Shapley hai nguồn P=0. CSV còn có cả tương tác bậc ba và đủ 6 thứ tự; '
             'CI được tính sau khi lập hiệu/vector Shapley theo seed, không lấy hiệu hai CI riêng.', '',
             '| Tương tác S×P, twin tin B=0,70 | Mean (ms) | CI95 half (ms) |','|---|---:|---:|']
    for level in (0,1):
        m,h=ci(effects[.7][f'interaction:S*P|M={level}']);report.append(f'| M={level} | {m:.6f} | {h:.6f} |')
    report+=['','Chỉ sai ρ̄_B được thao tác trong P, lan vào cả tâm posterior và R ở nhánh đếm. '
             'Không suy rằng mọi sai mô hình chỉ hại khi dữ liệu cũ; sai K, dạng đường cong hoặc bỏ qua Δρ có thể hại ngay khi dữ liệu tươi.', '',
             '## 3. Gộp và nhiễu: tách đúng cơ chế','',
             '| Thông tin A / B | S=0: mean ±CI95 (ms) | S=1: mean ±CI95 (ms) |','|---|---:|---:|']
    for a,b in modes:
        m0,h0=ci(nested[0,a,b]);m1,h1=ci(nested[1,a,b]);report.append(f'| {a}/{b} | {m0:.6f} ± {h0:.6f} | {m1:.6f} ± {h1:.6f} |')
    report+=['','Dòng **win/inst** được bổ sung sau khi đọc lesson để tách nhiễu A khỏi gộp A. '
             'Hiệu noisy/inst−inst/inst trong lesson gồm cả hai cơ chế, không phải riêng nhiễu.','',
             '| Hiệu ứng (giữ phần còn lại theo cấu hình chỉ định) | S=0 (ms) | S=1 (ms) |','|---|---:|---:|']
    labels={'aggregate_B':'Gộp B: inst/win − inst/inst','aggregate_A':'Gộp A: win/inst − inst/inst',
            'noise_A':'Nhiễu A: noisy/inst − win/inst','aggregate_AB':'Gộp cả hai: win/win − inst/inst',
            'noise_AB':'Nhiễu cả hai: noisy/noisy − win/win'}
    for key,label in labels.items():
        m0,h0=ci(split_effects[0,key]);m1,h1=ci(split_effects[1,key]);report.append(f'| {label} | {m0:.6f} ± {h0:.6f} | {m1:.6f} ± {h1:.6f} |')
    report+=['','Đảo thứ hạng theo S được đọc có điều kiện trên ô/mức/luật/bộ sinh đã chọn. '
             'Các công tắc không tạo một cơ chế điều khiển vật lý và chưa có nguồn cho tính thực tế của mức 30 s hay sai ρ̄.','',
             '## 4. Kiểm chứng, sai lệch và giới hạn','',
             '- 81 kiểm thử đạt; thế giới không bị sửa bởi công tắc; cùng hash giữa hai mức sai tham số; P=0 và endpoint n02b trùng từng bit.',
             '- Audit AST: world, twin_info, regret_of (n02) và regret (n02b) giữ nguyên từ attachment. Chỉ thêm xuất số liệu, kiểm và trường hợp win/inst.',
             '- Các nhánh đo M=1 khớp số in ở lesson; một số nhánh tức thời M=0 không khớp. '
             'Giữ nguyên W=1e-6 để tái lập; giới hạn số học/quadrature và rời rạc hoá của ideal đã ghi ở L1.2 vẫn áp dụng. '
             'Chưa có code/môi trường đã sinh bảng lesson để xác định nguyên nhân sai lệch.',
             f"- Với B, có {runs[.8]['B_changed_count_on_same_report']}/{runs[.8]['B_repeated_report_adjacent_epochs']} cặp epoch liên tiếp cùng r_last nhưng số đếm khác: "
             'n02 lấy u độc lập theo epoch, trong khi telemetry gốc giữ nguyên số đếm của bản tin. '
             'CRN trong n02 có hiệu lực giữa cấu hình theo coupling này, không tái lập phụ thuộc thời gian của telemetry gốc.',
             '- Regret (1,1,0) gần n01b là kiểm mô tả, không phải neo từng bit; CI chồng lấp không chứng minh tương đương. '
             'Lịch report và các biên giữ liệu có thể cùng phân phối một epoch, nhưng quỹ đạo/RNG và tương quan nhiễu khác.',
             '- M=0 là quan sát tại một thời điểm, M=1 là trung bình cửa sổ+nhiễu. Hai σ-algebra này không lồng nhau hoàn toàn; '
             'ở dữ liệu cũ, trung bình cửa sổ chứa thông tin quá khứ mà một điểm đơn lẻ không chứa. '
             'Đây là factorial đổi cơ chế quan sát, không tự động là giá trị thông tin Bayes tối ưu của hai tập thông tin lồng nhau.',
             '- Trong code S tắt chỉ loại tuổi z; a luôn giữ. Có thể dùng L=z+a để mô tả gap và vẫn giữ chuẩn lý tưởng tại t. '
             'Chỉ khi quyết định loại luôn cả a khỏi phần regret nền mới cần chuẩn biết trạng thái tại t+a. '
             'Hai chuẩn khác nhau; chưa chạy chuẩn t+a ở đây.',
             '- Giảm z hay a cùng một lượng chỉ có thể được so tương đương khi giữ cùng phân phối W/nhiễu, '
             'điều kiện dừng và luật/bộ sinh phù hợp. Đổi T_tel thường phá các điều kiện đó.', '',
             '## 5. Đối chiếu số lesson','',
             '| Chỉ số không khớp ở độ chính xác đã in | Local | Lesson | Local − lesson |','|---|---:|---:|---:|']
    for row in comparisons:
        if not row['match']:
            label=row['metric'].replace('|', r'\|')
            report.append(f"| {label} | {row['local']:.6f} | {row['lesson']} | {row['delta']:+.6f} |")
    report+=['','## 6. Tệp kết quả và lệnh','',
             '- [Output factorial](n02_source_factorial_output.txt), [output tách đo](n02b_measurement_split_output.txt).',
             '- [Seed factorial 0,80](n02_H0.5_rho0.80_seeds.csv), [seed factorial 0,70](n02_H0.5_rho0.70_seeds.csv).',
             '- [Summary/CI 0,80](n02_H0.5_rho0.80_summary.csv), [summary/CI 0,70](n02_H0.5_rho0.70_summary.csv); `_contrasts_seeds.csv` lưu từng hiệu theo seed.',
             '- [120 đo lồng nhau](n02b_measurement_split_seeds.csv), [hiệu gộp/nhiễu](n02b_split_contrasts.csv), [S–M khi P=0](n02_SM_P0_summary.csv).',
             '- [So lesson](n02_lesson_comparison.csv), [audit source](n02_source_audit.json), [pytest](n02_tests_output.txt).',
             '- [N2](../../notes/novelty/N2_error_sources.md), [realism_sources](../../notes/novelty/realism_sources.md), [bài tính](../../notes/novelty/N2_calculation_examples.md).','',
             '```bash','.venv/bin/python -m experiments.n02_source_factorial --rho_b_wrong 0.80',
             '.venv/bin/python -m experiments.n02_source_factorial --rho_b_wrong 0.70',
             '.venv/bin/python -m experiments.n02b_measurement_split',
             '.venv/bin/python -m pytest tests/test_n02_sources.py tests/test_n01_verdict.py tests/test_scan.py tests/test_mdk.py -q',
             '.venv/bin/python -m experiments.n02_report','```','',
             'Lệch kế hoạch: thêm code minh hoạ, exporter/report, kiểm thử và một trường hợp tách nhiễu A. '
             'Không sửa ndtrisk, scan, f04b hay f08. Không gán việc tự kiểm/tính giấy cho tác giả. '
             'Các quyết định N-S2/N-S3 đang để đề xuất chờ tác giả; kết quả dùng mốc t như script cung cấp.']
    (OUT/'n02_report.md').write_text('\n'.join(report)+'\n')
    files=list((ROOT/'experiments').glob('n02*.py'))+[ROOT/'tests/test_n02_sources.py']
    files+=[ROOT/'experiments/scan'/n for n in ('world.py','twin.py','grid.py','cell.py')]
    files+=[p for p in OUT.glob('n02*') if p.is_file() and p.name not in ('n02_manifest.json','n02_validation_output.txt')]
    manifest=dict(date='2026-10-02',base_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,
                  hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    (OUT/'n02_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Đã lưu n02_report.md, n02_decomposition.png, các CSV tổng hợp/đối chiếu và manifest SHA-256.')


if __name__=='__main__':
    main()
