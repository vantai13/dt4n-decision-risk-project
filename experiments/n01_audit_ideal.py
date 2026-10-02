"""Audit L1.2: xấp xỉ số của ideal; không đổi kết quả mô hình gốc. Chạy từ gốc repo."""
from pathlib import Path
import csv
import hashlib
import argparse
import re
import numpy as np
from experiments.scan.grid import controls
from experiments.scan.cell import get_curve
from experiments.scan.twin import posterior, var_box

ap=argparse.ArgumentParser(description="Audit số lý tưởng; tùy chọn đối chiếu nguyên bản script trong lesson.")
ap.add_argument("--lesson", type=Path, help="Attachment Lesson 1.2 (chỉ dùng tệp tin cậy do tác giả cung cấp)")
args=ap.parse_args()
_,cell=controls()
if args.lesson:
    source=Path(args.lesson).read_text()
    script=re.findall(r'```python\n(.*?)\n```',source,re.S)[1]
    namespace={'__name__':'supplied_lesson'}
    exec(compile(script,'<n01b supplied verbatim>','exec'),namespace)
    print('SHA256 script n01b trong attachment (LF, không newline cuối):',hashlib.sha256(script.encode()).hexdigest())
    for h in (.5,5.,30.):
        _,cell=controls();cell['H']=h
        curve,s=get_curve(cell)
        raw=np.load(f'results/raw/n01/n01b_H{h:g}_epochs.npz')
        for seed in range(9101,9111):
            got=namespace['one_seed'](seed,cell,curve,.5*s)
            selected=raw['seed']==seed
            for key in ('I','real','ideal','plug'):
                assert np.array_equal(got[key],raw[key][selected]),(h,seed,key)
        print(f'H={h:g}: NGUYÊN BẢN lesson khớp từng bit I/real/ideal/plug đã lưu, trên cả 10 seed.')
    print('=> Sai lệch số ideal so với bảng lesson tái hiện cả khi chạy nguyên bản; không do phần xuất số liệu thêm.')
rows=[]
for h in (.5,5.,30.):
    for path in 'AB':
        q=cell[path];tau=q['tau'];sigma=q['sigma'];mu=q['rho_bar'];a=cell['a']
        b=np.exp(-a/tau)*(-np.expm1(-h/tau))/(h/tau)
        vlimit=var_box(h,sigma,tau)-sigma*sigma*b*b
        m,v=posterior(mu+.1,a,1e-6,h,mu,sigma,tau,0)
        row=dict(H_s=h,path=path,var_W_relative=var_box(1e-6,sigma,tau)/sigma**2,
                 beta_W1e6=(m-mu)/.1,beta_point_limit=b,v_W1e6=float(v),v_point_limit=float(vlimit),
                 relative_variance_error=float(v/vlimit-1))
        rows.append(row)
        print(f'H={h:g}, {path}: Var(W)/sigma²={row["var_W_relative"]:.12f}; variance W=1e-6 {v:.12g}, point-limit {vlimit:.12g}, relative error {row["relative_variance_error"]:.3%}')
out=Path('experiments/results/n01b_ideal_numerical_audit.csv')
with out.open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
print('Giới hạn điểm tính cho OU liên tục: beta=exp(-a/tau)*(1-exp(-H/tau))/(H/tau); v=var_box(H)-sigma²*beta².')
print('Đây là audit xấp xỉ số, chưa xác định được nguyên nhân khác môi trường của bảng lesson; không thay kết quả chính.')
