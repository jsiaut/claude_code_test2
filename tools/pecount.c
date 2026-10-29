// pecount : compteurs du noyau pour un processus et tous ses threads, sans PMU matérielle ni binaire perf.
// Ouvre, avant l'exec de la commande, des compteurs perf_event_open (hérités par les threads, activés à l'exec) :
//   * logiciels : temps CPU (task-clock), changements de contexte, migrations, défauts de page (dont majeurs) ;
//   * tracepoints : raw_syscalls/sys_enter (tous les appels système) et syscalls/sys_enter_<nom> (option -t) ;
//   * uprobes : entrée d'une fonction d'une bibliothèque ou d'un exécutable (option -u nom=chemin:décalage),
//     définies dans tracefs (uprobe_events) et comptées comme tracepoints : la PMU « uprobe » de perf_event_open
//     relit un pointeur utilisateur à chaque héritage, ce qui fait échouer les fork de la commande ;
//   * points d'arrêt matériels en écriture (option -w nom=adresse:longueur), pour un exécutable sans ASLR.
// Usage : pecount [-o sortie.json] [-t catégorie/événement]... [-u nom=chemin:décalage]... -- commande args...
// La sortie standard et l'erreur de la commande sont transmises telles quelles ; les comptes vont dans le JSON.
// Construction : cc -O2 -o /opt/pecount tools/pecount.c
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/hw_breakpoint.h>
#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <unistd.h>

#define MAXEV 64
static struct { char name[96]; struct perf_event_attr a; int fd; } ev[MAXEV];
static int nev;

static struct perf_event_attr *add(const char *name, uint32_t type, uint64_t config) {
    if (nev == MAXEV) { fprintf(stderr, "pecount : trop d'événements\n"); exit(2); }
    memset(&ev[nev], 0, sizeof ev[nev]);
    snprintf(ev[nev].name, sizeof ev[nev].name, "%s", name);
    struct perf_event_attr *a = &ev[nev].a;
    a->size = sizeof *a; a->type = type; a->config = config;
    a->disabled = 1; a->inherit = 1; a->enable_on_exec = 1;
    a->read_format = PERF_FORMAT_TOTAL_TIME_ENABLED | PERF_FORMAT_TOTAL_TIME_RUNNING;
    nev++;
    return a;
}

static char uprobes[MAXEV][96];
static int nup;

static int write_str(const char *path, const char *s) {  // open/write directs : fopen("a") échoue sur tracefs (lseek)
    int fd = open(path, O_WRONLY | O_APPEND);
    if (fd < 0) return -1;
    ssize_t n = write(fd, s, strlen(s));
    close(fd);
    return n == (ssize_t)strlen(s) ? 0 : -1;
}

static void remove_uprobes(void) {
    for (int k = 0; k < nup; k++) {
        char c[128]; snprintf(c, sizeof c, "-:pecount/%.90s\n", uprobes[k]);
        write_str("/sys/kernel/tracing/uprobe_events", c);
    }
}

static long read_long(const char *path) {
    FILE *f = fopen(path, "r");
    long v = -1;
    if (f) { if (fscanf(f, "%ld", &v) != 1) v = -1; fclose(f); }
    return v;
}

int main(int argc, char **argv) {
    const char *out = NULL;
    add("task_clock_ns", PERF_TYPE_SOFTWARE, PERF_COUNT_SW_TASK_CLOCK);
    add("context_switches", PERF_TYPE_SOFTWARE, PERF_COUNT_SW_CONTEXT_SWITCHES);
    add("cpu_migrations", PERF_TYPE_SOFTWARE, PERF_COUNT_SW_CPU_MIGRATIONS);
    add("page_faults", PERF_TYPE_SOFTWARE, PERF_COUNT_SW_PAGE_FAULTS);
    add("major_faults", PERF_TYPE_SOFTWARE, PERF_COUNT_SW_PAGE_FAULTS_MAJ);
    long sysid = read_long("/sys/kernel/tracing/events/raw_syscalls/sys_enter/id");
    if (sysid >= 0) add("syscalls", PERF_TYPE_TRACEPOINT, (uint64_t)sysid);
    int i = 1;
    for (; i < argc && strcmp(argv[i], "--"); i++) {
        if (!strcmp(argv[i], "-o") && i + 1 < argc) { out = argv[++i]; continue; }
        if (!strcmp(argv[i], "-t") && i + 1 < argc) {  // -t syscalls/sys_enter_futex
            char p[512]; snprintf(p, sizeof p, "/sys/kernel/tracing/events/%s/id", argv[++i]);
            long id = read_long(p);
            if (id < 0) { fprintf(stderr, "pecount : tracepoint absent : %s\n", argv[i]); continue; }
            const char *nm = strrchr(argv[i], '/'); add(nm ? nm + 1 : argv[i], PERF_TYPE_TRACEPOINT, (uint64_t)id);
            continue;
        }
        if (!strcmp(argv[i], "-u") && i + 1 < argc) {  // -u malloc=/lib/x86_64-linux-gnu/libc.so.6:0xad750
            char buf[640]; snprintf(buf, sizeof buf, "%s", argv[++i]);
            char *eq = strchr(buf, '=');
            if (!eq || nup == MAXEV) { fprintf(stderr, "pecount : uprobe invalide : %s\n", argv[i]); continue; }
            *eq = 0;
            char def[800], idp[256];
            snprintf(def, sizeof def, "-:pecount/%.80s\n", buf);
            write_str("/sys/kernel/tracing/uprobe_events", def);  // reste d'une exécution interrompue
            snprintf(def, sizeof def, "p:pecount/%.80s %.600s\n", buf, eq + 1);
            if (write_str("/sys/kernel/tracing/uprobe_events", def)) { fprintf(stderr, "pecount : uprobe refusée : %s\n", argv[i]); continue; }
            snprintf(uprobes[nup++], sizeof uprobes[0], "%.80s", buf);
            snprintf(idp, sizeof idp, "/sys/kernel/tracing/events/pecount/%.80s/id", buf);
            long id = read_long(idp);
            if (id < 0) { fprintf(stderr, "pecount : uprobe sans identifiant : %s\n", argv[i]); continue; }
            char nm[96]; snprintf(nm, sizeof nm, "uprobe_%.80s", buf);
            add(nm, PERF_TYPE_TRACEPOINT, (uint64_t)id);
            continue;
        }
        if (!strcmp(argv[i], "-w") && i + 1 < argc) {  // -w compteur=0x4c1040:8
            char buf[256]; snprintf(buf, sizeof buf, "%s", argv[++i]);
            char *eq = strchr(buf, '='), *col = strrchr(buf, ':');
            if (!eq || !col) { fprintf(stderr, "pecount : point d'arrêt invalide : %s\n", argv[i]); continue; }
            *eq = 0; *col = 0;
            char nm[96]; snprintf(nm, sizeof nm, "writes_%.80s", buf);
            struct perf_event_attr *a = add(nm, PERF_TYPE_BREAKPOINT, 0);
            a->bp_type = HW_BREAKPOINT_W; a->bp_addr = strtoull(eq + 1, NULL, 0); a->bp_len = strtoull(col + 1, NULL, 0);
            continue;
        }
        fprintf(stderr, "pecount : option inconnue : %s\n", argv[i]); return 2;
    }
    if (i + 1 >= argc) { fprintf(stderr, "usage : pecount [-o f.json] [-t cat/ev]... [-u nom=chemin:déc]... -- cmd...\n"); remove_uprobes(); return 2; }
    char **cmd = &argv[i + 1];
    int go[2];
    if (pipe(go)) { perror("pipe"); return 2; }
    pid_t child = fork();
    if (child < 0) { perror("fork"); return 2; }
    if (child == 0) {  // attend que les compteurs soient ouverts, puis exec
        close(go[1]);
        char c;
        if (read(go[0], &c, 1) != 1) _exit(127);
        close(go[0]);
        execvp(cmd[0], cmd);
        perror("execvp");
        _exit(127);
    }
    close(go[0]);
    for (int k = 0; k < nev; k++) {
        ev[k].fd = (int)syscall(SYS_perf_event_open, &ev[k].a, child, -1, -1, 0);
        if (ev[k].fd < 0) fprintf(stderr, "pecount : %s : %s\n", ev[k].name, strerror(errno));
    }
    if (write(go[1], "x", 1) != 1) { perror("write"); return 2; }
    close(go[1]);
    int status = 0;
    while (waitpid(child, &status, 0) < 0 && errno == EINTR) {}
    int rc = WIFEXITED(status) ? WEXITSTATUS(status) : 128 + WTERMSIG(status);
    FILE *o = out ? fopen(out, "w") : stderr;
    if (!o) { perror("sortie"); return 2; }
    fprintf(o, "{\"rc\": %d, \"counts\": {", rc);
    int first = 1;
    for (int k = 0; k < nev; k++) {
        if (ev[k].fd < 0) continue;
        uint64_t v[3] = {0, 0, 0};
        if (read(ev[k].fd, v, sizeof v) != (ssize_t)sizeof v) continue;
        // v[1] temps activé, v[2] temps en cours : égaux sans multiplexage (événements logiciels et tracepoints)
        fprintf(o, "%s\"%s\": %llu", first ? "" : ", ", ev[k].name, (unsigned long long)v[0]);
        if (v[1] != v[2]) fprintf(o, ", \"%s_scaled_ratio\": %.6f", ev[k].name, v[1] ? (double)v[2] / v[1] : 0.0);
        first = 0;
        close(ev[k].fd);
    }
    fprintf(o, "}}\n");
    if (out) fclose(o);
    remove_uprobes();
    return rc;
}
