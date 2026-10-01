"""Validate all GO v1 rows, write decision report and standalone research plot."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from experiments.scan.go_switch import ALPHAS, SETTINGS, PRIMARY, GO_SWITCH
from experiments.scan.go_test import scenarios

ROOT = Path('results/go_test')


def failures(r, period):
    f = []
    if r['lo'] <= 0: f.append('CI chứa 0 hoặc âm')
    if r['d'] < .1*max(r['g_SC'],1e-9): f.append('Δ <10% gain SC')
    if period and max(r['sw_SC'],r['sw_K2']) > 1.2*r['H']/period: f.append('vượt trần đổi test')
    if max(r['h_SC'],r['h_K2']) > 1.5*r['alpha']: f.append('vượt trần harm test')
    return '; '.join(f) or 'Đạt'


def main():
    with (ROOT/'go_switch_v1.csv').open() as f: rows=list(csv.DictReader(f))
    for r in rows:
        for k in r:
            if k=='passed': r[k]=r[k]=='True'
            elif k not in ('name','setting'): r[k]=float(r[k])
    base,sweep=scenarios()
    settings={label:(period,cost) for label,period,cost in SETTINGS}
    expected={(s['name'],a,label) for s in base+sweep for a in ALPHAS for label in settings}
    assert len(rows)==120 and {(r['name'],r['alpha'],r['setting']) for r in rows}==expected
    for r in rows:
        period,_=settings[r['setting']]
        assert r['passed']==GO_SWITCH(r,r['alpha'],period)
        for rule in ('SC','K2'):
            assert r[f'cal_h_{rule}'] <= r['alpha']+1e-12
            assert not period or r[f'cal_sw_{rule}'] <= r['H']/period+1e-12
    with (ROOT/'go_switch_seeds.csv').open() as f: seeds=list(csv.DictReader(f))
    assert len(seeds)==2400
    for r in rows:
        sub=[x for x in seeds if x['name']==r['name'] and float(x['alpha'])==r['alpha'] and x['setting']==r['setting']]
        assert len(sub)==20 and len({x['seed'] for x in sub})==20
        assert abs(sum(float(x['d']) for x in sub)/20-r['d'])<1e-10
    out=['# GO switch v1 — 2026-10-01','',
         'Code, thiết kế và dự đoán khóa ở commit 2693695 trước lần chạy v1. Đã kiểm 120 dòng, 2400 dòng per-seed, đủ tổ hợp; GO_SWITCH khớp mọi cờ, mọi policy calibration giữ cả hai ngân sách.','',
         '## Quyết định chính: trần trung bình 1 lần/30 s','',
         '| Kịch bản | α | Δ ròng ngoài mẫu [CI 95%], ms | Gain SC/K2 ms | Harm SC/K2 | Tỉ lệ hành động SC/K2 | Kết quả |',
         '|---|---:|---|---|---|---|---|']
    for r in rows:
        if r['name'] in {s['name'] for s in base} and r['setting']==PRIMARY:
            out.append(f"| {r['name']} | {100*r['alpha']:g}% | {r['d']:+.6f} [{r['lo']:+.6f}; {r['hi']:+.6f}] | {r['g_SC']:.6f}/{r['g_K2']:.6f} | {100*r['h_SC']:.4f}%/{100*r['h_K2']:.4f}% | {100*r['sw_SC']:.3f}%/{100*r['sw_K2']:.3f}% | {failures(r,30)} |")
    for s in base:
        ok=[r['alpha'] for r in rows if r['name']==s['name'] and r['setting']==PRIMARY and r['passed']]
        out.extend(['',f"**{s['name']}: {'GO' if ok else 'NO-GO khi giới hạn số hành động đổi'}**"+(f' tại alpha={ok}' if ok else '')])
    r1=next(r for r in rows if r['name']=='R1_dualISP' and r['alpha']==.002 and r['setting']==PRIMARY)
    free=next(r for r in rows if r['name']=='R1_dualISP' and r['alpha']==.002 and r['setting']==SETTINGS[0][0])
    out+=['','## So dự đoán và ý nghĩa quy mô','',
          f"Dự đoán R1 NO-GO bị dữ liệu bác bỏ theo chính tiêu chí đã khóa: Δ/gain SC={100*r1['d']/r1['g_SC']:.4f}%, cận dưới CI={r1['lo']:.6f} ms. Đây là GO sát ngưỡng tương đối 10%, không phải hiệu ứng thực tế lớn.",
          f"Ở alpha=0,2%, giới hạn 30 s làm width R1 từ {free['d']:.6f} xuống {r1['d']:.6f} ms, giảm {100*(1-r1['d']/free['d']):.2f}%. Do đó nhận định lợi thế giảm mạnh được hỗ trợ; nhận định biến mất hoàn toàn tại 30 s không đúng trong lần đánh giá này.",
          'Số trong tài liệu người dùng là tối ưu trên test; lượt v1 là ngưỡng học calibration nên không đòi khớp các số đó. Dự đoán ô cùng nhịp và buffer nhỏ mất hiệu ứng cũng không đúng đồng loạt; xem bảng ô biên. Không thay tiêu chí sau khi thấy GO.',
          'SESOI VoIP 8,1 ms không đạt ở kết quả chính. Toàn bộ suite kiểm: 98 passed in 5.64s.']
    out+=['','## Ranh giới cost/tần suất R1 và R2','','| Kịch bản | α | Thiết lập | Δ ròng [CI 95%], ms | μ K2 | Điều kiện thiếu |','|---|---:|---|---|---:|---|']
    for r in rows:
        if r['name'] in {s['name'] for s in base}:
            out.append(f"| {r['name']} | {100*r['alpha']:g}% | {r['setting']} | {r['d']:+.4f} [{r['lo']:+.4f}; {r['hi']:+.4f}] | {r['mu_K2']:.0f} | {failures(r,settings[r['setting']][0])} |")
    out+=['','## Ô biên tại trần chính (không quyết định GO)','','| Ô | α | Δ ngoài mẫu ms | CI dưới ms | Kết quả |','|---|---:|---:|---:|---|']
    for r in rows:
        if r['name'] in {s['name'] for s in sweep} and r['setting']==PRIMARY:
            out.append(f"| {r['name']} | {100*r['alpha']:g}% | {r['d']:+.6f} | {r['lo']:+.6f} | {failures(r,30)} |")
    out+=['','## Phạm vi diễn giải','',
          '- Quyết định v0 GO vẫn đúng theo tiêu chí miễn phí đã khóa. V1 thêm điều kiện nên không sửa ngược số liệu v0. Không tự suy từ không đạt thống kê ra SC tối ưu tuyệt đối hay mọi ứng dụng đều NO-GO.',
          '- Những sw trong bảng là tỉ lệ đề nghị đổi trên quỹ đạo S0 tham chiếu, không phải tần suất của quỹ đạo triển khai riêng từng luật. Nghịch đảo H/sw chỉ là khoảng cách trung bình tương đương. Code không áp cooldown từng lần, có thể chọn nhiều hành động liền nhau. Muốn kết luận về đổi đường liên tục thực tế cần rollout riêng và mô hình jitter/reordering.',
          '- Dùng lại seed test 81001–81020 của v0 theo hướng dẫn; protocol v1 đã chịu ảnh hưởng bởi phân tích trên test. Tham số policy học riêng trên calibration nhưng đây không phải xác nhận độc lập trên test mới.',
          '- Cost 5/10 ms là chi phí tuyến tính mỗi hành động trong gain ròng. Harm vẫn định nghĩa I<−1 ms trước cost; period và cost thử riêng, không đồng thời. Không khẳng định chi phí này là jitter thực tế đã đo.',
          '- K2 chọn μ từ 0..80 ms và threshold ratio trên calibration, nhiều bậc tự do hơn SC. Không sửa lưới sau khi xem test; độ phủ/overfit của lưới vẫn là giới hạn.',
          '- Với μ=0 và λ≈0, chính sách được ràng Ibar>0; với μ>0 ràng Ibar>μ. Quỹ đạo tham chiếu S0 vẫn tune harm như v0, không tune cost/cap; giữ cố định để so có cùng trạng thái tham chiếu.',
          '- Chỉ twin đúng; chưa thêm 6 sai số v0. CI paired t trên 20 seed, không hiệu chỉnh nhiều phép kiểm. Các kịch bản vẫn có tham số giả định và telemetry bộ đếm gói.',
          '- Claim “bất định chỉ có ích khi ba điều kiện cùng xảy ra” mạnh hơn dữ liệu: trước đây một số ô cùng nhịp vẫn đạt với hiệu ứng nhỏ. Báo cáo ranh giới trong các cấu hình đã thử, không khẳng định điều kiện cần toàn cục.','',
          '## Artifact và tái lập','',
          '- results/go_test/go_switch_v1.csv: đủ 120 kết quả, ngưỡng và kiểm ngân sách calibration.',
          '- results/go_test/go_switch_seeds.csv: 2400 dòng per-seed.',
          '- results/go_test/go_switch_manifest.json: kịch bản/seed/lưới/thiết lập khóa.',
          '- results/go_test/go_switch_output.txt: log đầy đủ.',
          '- results/go_test/go_switch_boundary.png/.pdf: đồ thị hiệu ứng ngoài mẫu.',
          '- notes/map/go_switch_spec.md: dự đoán trước chạy.',
          '- Chạy lại: .venv/bin/python -m experiments.scan.go_switch; dựng báo cáo: .venv/bin/python -m experiments.scan.report_go_switch.']
    Path('notes/map/go_switch_report.md').write_text('\n'.join(out)+'\n')
    fig,axs=plt.subplots(1,2,figsize=(13,5),constrained_layout=True)
    labels=['Free','Cap 30s','Cap 60s','Cap 120s','Cost 5ms','Cost 10ms']
    for ax,s in zip(axs,base):
        for j,a in enumerate(ALPHAS):
            sub=[next(r for r in rows if r['name']==s['name'] and r['alpha']==a and r['setting']==label) for label,_,_ in SETTINGS]
            ax.errorbar([i+.12*j for i in range(6)],[r['d'] for r in sub],yerr=[[r['d']-r['lo'] for r in sub],[r['hi']-r['d'] for r in sub]],fmt='o',capsize=3,label=f'alpha={100*a:g}%')
        ax.axhline(0,color='black',linewidth=.7)
        ax.set_xticks(range(6),labels,rotation=30)
        ax.set_title(s['name'])
        ax.set_ylabel('Net K2 - SC (ms/decision), 95% paired t CI')
        ax.legend()
    fig.savefig(ROOT/'go_switch_boundary.png',dpi=180)
    fig.savefig(ROOT/'go_switch_boundary.pdf')
    print('Validated 120 rows and 2400 seed outcomes; report and figures saved.')


if __name__=='__main__': main()
