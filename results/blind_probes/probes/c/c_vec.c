typedef float v8f __attribute__((vector_size(32)));
v8f add(v8f a, v8f b) { return a * b + a; }
int main(void){ v8f a = {1,2,3,4,5,6,7,8}; v8f r = add(a,a); return (int)r[7] == 72 ? 0 : 1; }
