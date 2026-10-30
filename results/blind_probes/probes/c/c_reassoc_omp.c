float sum(const float *v, int n) { float s = 0.f;
#pragma omp simd reduction(+:s)
  for (int i = 0; i < n; i++) s += v[i]; return s; }
float sum_plain(const float *v, int n) { float s = 0.f; for (int i = 0; i < n; i++) s += v[i]; return s; }
