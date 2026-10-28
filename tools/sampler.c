// sampler.c — profileur par échantillonnage maison (perf n'est pas installé et la VM n'a pas de PMU).
// Utilise perf_event_open avec l'événement LOGICIEL cpu-clock (autorisé sans PMU, paranoid=2 :
// espace utilisateur seulement), un événement par CPU hérité par tous les threads du processus
// lancé. Il collecte les adresses d'instruction (IP) et les projections exécutables (MMAP2),
// puis écrit :
//   * un histogramme des IP les plus fréquentes, avec le fichier et le décalage dans le fichier ;
//   * pour le code anonyme (JIT), une copie des octets autour des IP chaudes, lue pendant
//     l'exécution par process_vm_readv (à désassembler avec objdump -b binary).
// Usage : sampler [-f Hz] [-o prefixe] -- commande args...
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/perf_event.h>
#include <poll.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <sys/uio.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#define MAXCPU 64
#define PAGES 256  // 1 Mio de tampon par CPU
#define MAXIP (1 << 20)
#define MAXMAP 4096

typedef struct { uint64_t ip; uint64_t n; } Ent;
typedef struct { uint64_t start, len, pgoff; char name[256]; } Map;

static Ent *tab;     // table de hachage des IP
static Map maps[MAXMAP];
static int nmaps;
static uint64_t total, lost;
static pid_t child;

static Ent *slot(uint64_t ip) {
    uint64_t h = (ip * 0x9E3779B97F4A7C15ull) >> 44;  // 20 bits
    for (;;) {
        Ent *e = &tab[h & (MAXIP - 1)];
        if (e->ip == ip || e->ip == 0) { e->ip = ip; return e; }
        h++;
    }
}
static const Map *find_map(uint64_t ip) {
    const Map *best = NULL;
    for (int i = 0; i < nmaps; i++)  // la dernière projection couvrant l'adresse gagne
        if (ip >= maps[i].start && ip < maps[i].start + maps[i].len) best = &maps[i];
    return best;
}

static void drain(struct perf_event_mmap_page *mp) {
    char *data = (char *)mp + 4096;
    uint64_t size = (uint64_t)PAGES * 4096;
    uint64_t head = __atomic_load_n(&mp->data_head, __ATOMIC_ACQUIRE), tail = mp->data_tail;
    while (tail < head) {
        struct perf_event_header hdr;
        uint64_t off = tail % size;
        char buf[4096];
        // l'enregistrement peut chevaucher la fin du tampon circulaire
        for (size_t k = 0; k < sizeof hdr; k++) ((char *)&hdr)[k] = data[(off + k) % size];
        if (hdr.size > sizeof buf || hdr.size == 0) break;
        for (size_t k = 0; k < hdr.size; k++) buf[k] = data[(off + k) % size];
        if (hdr.type == PERF_RECORD_SAMPLE) {
            uint64_t ip = *(uint64_t *)(buf + sizeof hdr);
            slot(ip)->n++;
            total++;
        } else if (hdr.type == PERF_RECORD_MMAP2 && nmaps < MAXMAP) {
            // pid tid addr len pgoff maj min ino ino_gen prot flags filename
            char *p = buf + sizeof hdr + 8;
            Map *m = &maps[nmaps++];
            m->start = *(uint64_t *)p; m->len = *(uint64_t *)(p + 8); m->pgoff = *(uint64_t *)(p + 16);
            snprintf(m->name, sizeof m->name, "%s", p + 16 + 8 + 4 + 4 + 8 + 8 + 4 + 4);
        } else if (hdr.type == PERF_RECORD_LOST) {
            lost += *(uint64_t *)(buf + sizeof hdr + 8);
        }
        tail += hdr.size;
    }
    __atomic_store_n(&mp->data_tail, tail, __ATOMIC_RELEASE);
}

static int cmp(const void *a, const void *b) {
    const Ent *x = a, *y = b;
    return (y->n > x->n) - (y->n < x->n);
}

int main(int argc, char **argv) {
    int freq = 4000;
    const char *out = "sample";
    int i = 1;
    for (; i < argc && strcmp(argv[i], "--"); i++) {
        if (!strcmp(argv[i], "-f")) freq = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-o")) out = argv[++i];
    }
    if (i >= argc - 1) { fprintf(stderr, "usage: sampler [-f Hz] [-o prefixe] -- cmd...\n"); return 2; }
    char **cmd = argv + i + 1;
    tab = calloc(MAXIP, sizeof *tab);
    int go[2];
    if (pipe(go)) return 1;
    child = fork();
    if (child == 0) {
        char c;
        close(go[1]);
        if (read(go[0], &c, 1) != 1) _exit(1);  // attend que les compteurs soient ouverts
        execvp(cmd[0], cmd);
        perror("execvp");
        _exit(127);
    }
    close(go[0]);
    int ncpu = (int)sysconf(_SC_NPROCESSORS_ONLN);
    int fds[MAXCPU];
    struct perf_event_mmap_page *mps[MAXCPU];
    for (int c = 0; c < ncpu; c++) {
        struct perf_event_attr a;
        memset(&a, 0, sizeof a);
        a.size = sizeof a;
        a.type = PERF_TYPE_SOFTWARE;
        a.config = PERF_COUNT_SW_CPU_CLOCK;
        a.freq = 1;
        a.sample_freq = (uint64_t)freq;
        a.sample_type = PERF_SAMPLE_IP;
        a.exclude_kernel = 1;
        a.exclude_hv = 1;
        a.inherit = 1;
        a.enable_on_exec = 1;
        a.disabled = 1;
        a.mmap = 1;
        a.mmap2 = 1;
        a.sample_id_all = 0;
        fds[c] = (int)syscall(SYS_perf_event_open, &a, child, c, -1, PERF_FLAG_FD_CLOEXEC);
        if (fds[c] < 0) { perror("perf_event_open"); kill(child, SIGKILL); return 1; }
        mps[c] = mmap(NULL, (size_t)(PAGES + 1) * 4096, PROT_READ | PROT_WRITE, MAP_SHARED, fds[c], 0);
        if (mps[c] == MAP_FAILED) { perror("mmap"); kill(child, SIGKILL); return 1; }
    }
    if (write(go[1], "x", 1) != 1) return 1;
    close(go[1]);
    // pendant l'exécution : vidage des tampons et copies du code anonyme chaud (JIT)
    char path[512];
    snprintf(path, sizeof path, "%s.jit", out);
    int status = 0;
    struct timespec last = {0}, now;
    for (;;) {
        pid_t w = waitpid(child, &status, WNOHANG);
        for (int c = 0; c < ncpu; c++) drain(mps[c]);
        if (w == child) break;
        clock_gettime(CLOCK_MONOTONIC, &now);
        if (now.tv_sec - last.tv_sec >= 1) {  // chaque seconde : copie des 8 régions anonymes les plus chaudes
            last = now;
            FILE *jf = NULL;
            Ent top[8] = {0};
            for (int k = 0; k < MAXIP; k++) {
                if (!tab[k].n) continue;
                const Map *m = find_map(tab[k].ip);
                if (m && m->name[0] && m->name[0] != '/' && m->name[0] != '[') { /* //anon : JIT */ }
                else if (m) continue;
                for (int t = 0; t < 8; t++)
                    if (tab[k].n > top[t].n) { memmove(&top[t + 1], &top[t], (7 - t) * sizeof(Ent)); top[t] = tab[k]; break; }
            }
            for (int t = 0; t < 8 && top[t].n; t++) {
                unsigned char code[512];
                uint64_t base = top[t].ip - 256;
                struct iovec lv = {code, sizeof code}, rv = {(void *)base, sizeof code};
                if (process_vm_readv(child, &lv, 1, &rv, 1, 0) == (ssize_t)sizeof code) {
                    if (!jf) jf = fopen(path, "w");
                    fprintf(jf, "REGION 0x%llx %llu\n", (unsigned long long)base, (unsigned long long)top[t].n);
                    for (size_t b = 0; b < sizeof code; b++) fprintf(jf, "%02x", code[b]);
                    fprintf(jf, "\n");
                }
            }
            if (jf) fclose(jf);
        }
        struct timespec ts = {0, 20 * 1000 * 1000};
        nanosleep(&ts, NULL);
    }
    // histogramme
    int n = 0;
    for (int k = 0; k < MAXIP; k++) if (tab[k].n) tab[n++] = tab[k];
    qsort(tab, n, sizeof *tab, cmp);
    snprintf(path, sizeof path, "%s.ips", out);
    FILE *f = fopen(path, "w");
    fprintf(f, "# total=%llu perdus=%llu ip_distinctes=%d statut=%d\n", (unsigned long long)total,
            (unsigned long long)lost, n, WIFEXITED(status) ? WEXITSTATUS(status) : -1);
    for (int k = 0; k < n && k < 400; k++) {
        const Map *m = find_map(tab[k].ip);
        uint64_t off = m ? tab[k].ip - m->start + m->pgoff : 0;
        fprintf(f, "%llu %.3f%% 0x%llx %s 0x%llx\n", (unsigned long long)tab[k].n, 100.0 * tab[k].n / (total ? total : 1),
                (unsigned long long)tab[k].ip, m ? m->name : "?", (unsigned long long)off);
    }
    fclose(f);
    fprintf(stderr, "sampler: %llu échantillons, %d IP distinctes -> %s.ips\n", (unsigned long long)total, n, out);
    return WIFEXITED(status) ? WEXITSTATUS(status) : 1;
}
