float sum(const float *v, int n) {
#pragma clang fp reassociate(on)
  float s = 0.f; for (int i = 0; i < n; i++) s += v[i]; return s; }
float sum_plain(const float *v, int n) { float s = 0.f; for (int i = 0; i < n; i++) s += v[i]; return s; }
