"""Ước lượng OU từ telemetry calibration; không nhận tham số thật hay delay.

Bản nháp để review trước khi mở seed DES 90001–90020/91001–91020.
Khoảng đo không chồng lấn, outage độc lập tải, OU dừng và Poisson có điều kiện.
Đơn vị: tải chuẩn hoá, thời gian giây. Không suy diễn CI từ residual least squares.
"""
from dataclasses import dataclass

import numpy as np
from scipy.optimize import least_squares


@dataclass(frozen=True)
class FreshSeries:
    ticks: np.ndarray
    values: np.ndarray
    source_epochs: int
    rejected_old_updates: int


@dataclass(frozen=True)
class FitResult:
    rho_bar: float
    sigma: float
    tau: float
    count_noise_variance: float
    measured_variance: float
    predicted_variance: float
    n_messages: int
    lags: tuple
    covariances: tuple
    pair_counts: tuple
    fitted_covariances: tuple
    warnings: tuple


def fresh_series(rhohat, age, decision_times, period_s, max_age_s=None):
    """Mỗi timestamp đo chỉ dùng một lần; loại bản tin mới nhưng quá cũ.

    Timestamp đo = timestamp quyết định − tuổi. Tick là số chu kỳ telemetry,
    không phải thứ tự sau khi bỏ outage. Dùng chênh tick để giữ đúng lag thật.
    Mặc định 'tươi' là tuổi <= 2T; có thể khoá max_age_s khác trước lần chạy.
    """
    y, age, t = (np.asarray(x, dtype=float) for x in (rhohat, age, decision_times))
    if period_s <= 0 or not np.isfinite(period_s):
        raise ValueError("period_s phải hữu hạn và dương")
    if y.ndim != 1 or y.shape != age.shape or y.shape != t.shape or len(y) < 2:
        raise ValueError("Cần ba chuỗi 1D cùng độ dài >= 2")
    if not all(np.isfinite(x).all() for x in (y, age, t)) or np.any(age < 0) or np.any(y < 0):
        raise ValueError("Telemetry phải hữu hạn, tuổi/tải không âm")
    if np.any(np.diff(t) <= 0):
        raise ValueError("Timestamp quyết định phải tăng ngặt")
    measured_at = t - age
    tol = max(1e-7 * period_s, 1e-9)
    if np.any(np.diff(measured_at) < -tol):
        raise ValueError("Timestamp bản tin mới nhất không được đi lùi")
    updated = np.r_[True, np.diff(measured_at) > tol]
    if max_age_s is None:
        max_age_s = 2 * period_s
    if not np.isfinite(max_age_s) or max_age_s < 0:
        raise ValueError("max_age_s phải hữu hạn, không âm")
    keep = updated & (age <= max_age_s)
    if keep.sum() < 3:
        raise ValueError("Không đủ bản tin tươi riêng biệt")
    times = measured_at[keep]
    ticks_float = (times - times[0]) / period_s
    ticks = np.rint(ticks_float).astype(np.int64)
    if not np.allclose(ticks_float, ticks, rtol=0, atol=1e-5):
        raise ValueError("Bản tin không nằm trên lưới T; cần estimator irregular-window khác")
    if np.any(np.diff(ticks) <= 0):
        raise ValueError("Mỗi tick đo phải riêng biệt")
    return FreshSeries(ticks, y[keep], len(y), int((updated & ~keep).sum()))


def box_variance(period_s, sigma, tau):
    """V(T)=2σ²(x−1+exp(−x))/x², ổn định khi x=T/τ nhỏ."""
    x = period_s / tau
    if x < 1e-3:
        factor = 1 - x / 3 + x*x / 12 - x**3 / 60 + x**4 / 360
    else:
        factor = 2 * (x + np.expm1(-x)) / (x*x)
    return sigma*sigma * factor


def window_covariance(lags, period_s, sigma, tau):
    """Cov(Y_i,Y_{i+k}) = σ² [τ/T(1−exp(−T/τ))]² exp(−(k−1)T/τ)."""
    lags = np.asarray(lags, dtype=float)
    if period_s <= 0 or sigma <= 0 or tau <= 0 or np.any(lags < 1):
        raise ValueError("T, σ, τ dương; k >= 1 (cửa sổ không chồng lấn)")
    x = period_s / tau
    amplitude = (-np.expm1(-x) / x)**2
    return sigma*sigma * amplitude * np.exp(-(lags - 1) * x)


def empirical_moments(series, lags):
    """Gộp các seed nhưng KHÔNG tạo cặp giữa hai seed; giữ lag clock thật."""
    if not series:
        raise ValueError("Cần ít nhất một chuỗi calibration")
    all_y = np.concatenate([s.values for s in series])
    mean = float(all_y.mean())
    covariance, counts = [], []
    for lag in lags:
        total, count = 0., 0
        for s in series:
            j = np.searchsorted(s.ticks, s.ticks + lag)
            i = np.flatnonzero(j < len(s.ticks))
            i = i[s.ticks[j[i]] == s.ticks[i] + lag]
            if len(i):
                total += np.sum((s.values[i] - mean) * (s.values[j[i]] - mean))
                count += len(i)
        covariance.append(total / count if count else np.nan)
        counts.append(count)
    return mean, float(np.mean((all_y - mean)**2)), np.array(covariance), np.array(counts)


def fit_covariances(lags, covariance, pair_counts, period_s,
                    tau_bounds_s=(.1, 3600.), sigma_bounds=(1e-5, 2.)):
    """WLS trên covariance ở k>=1; KHÔNG trừ R khỏi covariance hay bỏ lag âm.

    Trọng số sqrt(n_pairs) là heuristic, không xử lý phụ thuộc giữa các lag.
    Lấy nghiệm tốt nhất từ ba khởi đầu τ, bounds phải khoá trước test.
    """
    lags, covariance, counts = (np.asarray(x) for x in (lags, covariance, pair_counts))
    if lags.ndim != 1 or covariance.shape != lags.shape or counts.shape != lags.shape:
        raise ValueError("Lag, covariance và pair_counts phải cùng shape 1D")
    if period_s <= 0 or not np.isfinite(period_s) or not np.isfinite(lags).all():
        raise ValueError("T dương hữu hạn, lags hữu hạn")
    if np.any(lags < 1) or np.any(lags != np.floor(lags)) or len(np.unique(lags)) != len(lags):
        raise ValueError("Lags phải là các số nguyên >=1 riêng biệt")
    lo = np.array([sigma_bounds[0], tau_bounds_s[0]], float)
    hi = np.array([sigma_bounds[1], tau_bounds_s[1]], float)
    if not np.isfinite(np.r_[lo, hi]).all() or np.any(lo <= 0) or np.any(hi <= lo):
        raise ValueError("Bounds phải hữu hạn và 0 < lower < upper")
    if np.any(counts < 0) or not np.isfinite(counts).all():
        raise ValueError("Pair counts phải hữu hạn, không âm")
    valid = np.isfinite(covariance) & (counts >= 100)
    if valid.sum() < 3 or np.max(covariance[valid]) <= 0:
        raise ValueError("Cần >=3 lag có >=100 cặp và có covariance dương")
    k, c, n = lags[valid], covariance[valid], counts[valid]
    scale = max(np.max(np.abs(c)), 1e-12)
    weights = np.sqrt(n / n.max())
    bounds = (np.log(lo), np.log(hi))
    def residual(z):
        sig, tau = np.exp(z)
        return weights * (window_covariance(k, period_s, sig, tau) - c) / scale
    sig0 = np.clip(np.sqrt(np.max(c)), lo[0]*1.01, hi[0]/1.01)
    starts = np.geomspace(lo[1]*1.01, hi[1]/1.01, 3)
    fits = [least_squares(residual, np.log([sig0, t]), bounds=bounds,
                          xtol=1e-12, ftol=1e-12, gtol=1e-12, max_nfev=2000) for t in starts]
    fit = min(fits, key=lambda x: np.sum(x.fun*x.fun))
    if not fit.success:
        raise ValueError(f"Fit không hội tụ: {fit.message}")
    sig, tau = np.exp(fit.x)
    warnings = []
    if np.any((fit.x - bounds[0] < .01) | (bounds[1] - fit.x < .01)):
        warnings.append("parameter_at_bound: không coi là ước lượng đáng tin khi chạm bounds")
    if np.linalg.cond(fit.jac.T @ fit.jac) > 1e8:
        warnings.append("weak_identification: covariance không đủ phân giải σ và τ")
    return float(sig), float(tau), tuple(warnings)


def estimate(observations, period_s, service_time_s, *,
             lags=(1, 2, 4, 8, 16, 32, 64, 128, 256), max_age_s=None,
             tau_bounds_s=(.1, 3600.), sigma_bounds=(1e-5, 2.)):
    """observations chỉ đọc rhohat, age, decision_times; không đọc D/ρ̄/σ/τ thật.

    ρ̄ = trung bình bản tin tươi; R = ρ̄·S/T theo Poisson.
    σ,τ khớp covariance off-diagonal. V(T)+R là kiểm mô hình, không objective fit.
    """
    if service_time_s <= 0 or not np.isfinite(service_time_s):
        raise ValueError("service_time_s phải hữu hạn và dương")
    series = [fresh_series(o['rhohat'], o['age'], o['decision_times'], period_s, max_age_s)
              for o in observations]
    mean, variance, cov, counts = empirical_moments(series, lags)
    sig, tau, warnings = fit_covariances(lags, cov, counts, period_s, tau_bounds_s, sigma_bounds)
    noise = mean * service_time_s / period_s
    predicted = box_variance(period_s, sig, tau) + noise
    if abs(variance - predicted) / max(predicted, 1e-12) > .2:
        warnings += ("variance_mismatch_gt20pct: Poisson/OU/stationarity cần kiểm lại",)
    if any(s.rejected_old_updates for s in series):
        warnings += ("old_updates_rejected",)
    return FitResult(mean, sig, tau, noise, variance, predicted,
                     sum(len(s.values) for s in series), tuple(lags),
                     tuple(float(x) if np.isfinite(x) else None for x in cov),
                     tuple(int(x) for x in counts),
                     tuple(float(x) for x in window_covariance(lags, period_s, sig, tau)), warnings)
