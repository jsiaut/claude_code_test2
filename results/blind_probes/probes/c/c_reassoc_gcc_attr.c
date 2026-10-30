__attribute__((optimize("associative-math","no-signed-zeros","no-trapping-math")))
float sum(const float *v, int n) { float s = 0.f; for (int i = 0; i < n; i++) s += v[i]; return s; }
float sum_plain(const float *v, int n) { float s = 0.f; for (int i = 0; i < n; i++) s += v[i]; return s; }
