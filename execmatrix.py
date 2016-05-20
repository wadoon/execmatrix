#!/usr/bin/env python3
#-*- encoding: utf-8 -*-



"""


"""

import yaml
import subprocess
import logging
import itertools

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class Environment(object):
    """

    """

    def __init__(self, *dimensions):
        self.dimensions = list()
        self.hyperspace = list()
        self.names = list()

        for n,r in dimensions:
            self.dimensions.append(r)
            self.names.append(n)

        logger.info("Environment has following variables: %s", repr(self.names))

    def _generate_cube(self):
        rollout = list(map(list, self.dimensions))
        self._hyperspace = itertools.product(*rollout)
        #logger.info("Environment calculated, %d instances found" % len(self._hyperspace))
        self._filter_cube()
        logger.info("Environment filtered, %d instances survived" % len(self.hyperspace))
        return self.hyperspace

    def _filter_cube(self):
        self.hyperspace = list(self._hyperspace)

    def __iter__(self):
        def gen_iterator():
            for e in self.hyperspace:
                yield dict(zip(self.names, e))

        if not self.hyperspace:
            self._generate_cube()

        return gen_iterator()

def run_with_rusage(exe, args):
    """The format string
       The format is interpreted in the usual printf-like way.  Ordinary characters are directly copied,  tab,  new‐
       line  and  backslash  are  escaped  using \t, \n and \\, a percent sign is represented by %%, and otherwise %
       indicates a conversion.  The program time will always add a trailing newline itself.  The conversions follow.
       All of those used by tcsh(1) are supported.

       Time

       %E     Elapsed real time (in [hours:]minutes:seconds).
       %e     (Not in tcsh(1).)  Elapsed real time (in seconds).
       %S     Total number of CPU-seconds that the process spent in kernel mode.
       %U     Total number of CPU-seconds that the process spent in user mode.
       %P     Percentage of the CPU that this job got, computed as (%U + %S) / %E.

       Memory

       %M Maximum resident set size of the process during its lifetime, in
        Kbytes.

       %t (Not in tcsh(1).) Average resident set size of the process, in Kbytes.

       %K Average total (data+stack+text) memory use of the process, in Kbytes.

       %D Average size of the process's unshared data area, in Kbytes.

       %p (Not in tcsh(1).) Average size of the process's unshared stack space,
        in Kbytes.

       %X Average size of the process's shared text space, in Kbytes.

       %Z (Not in tcsh(1).) System's page size, in bytes. This is a per-system
              constant, but varies between systems.

       %F Number of major page faults that occurred while the process was
              running. These are faults where the page has to be read in from
              disk.

       %R Number of minor, or recoverable, page faults. These are faults for
              pages that are not valid but which have not yet been claimed by
              other virtual pages. Thus the data in the page is still valid but
              the system tables must be updated.

       %W Number of times the process was swapped out of main memory.

       %c Number of times the process was context-switched involuntarily
        (because the time slice expired).

       %w Number of waits: times that the program was context-switched
              voluntarily, for instance while waiting for an I/O operation to
              complete.

       I/O

       %I     Number of filesystem inputs by the process.
    """


    r = {}

    r['args'] = args
    cli = "/usr/bin/time -ao run.tmp %s" % (exe)
    r['command_line'] = cli

    env = {k: str(v)for k,v in args.items()}
    env['TIME'] = "{'E':TL('%E'), 'e':TL('%e'), 'S':TL(%S), 'U':TL(%U), 'P':PERCENT('%P'), 'M':%M, "+\
                  "'t':%t, 'K':%K, 'D':%D, 'p':%p, 'X':%X, 'Z':%Z, 'F':%F, 'R':%R, "+\
                  "'W':%W, 'c':%c, 'w':%w, 'I':%I}"

    logger.info("Execute %s", cli)
    process = subprocess.Popen(cli,
                               env=env,
                               stdout = subprocess.PIPE,
                               stderr = subprocess.PIPE,
                               shell=True)
    error = process.wait()
    r['error_code'] = error

    r['resouces'] = get_resources("run.tmp")

    out = ""
    err = ""

    for line in process.stdout:
        out += "OUT=> " + str(line)

    for line in process.stdout:
        err += "ERR=> " + str(err)

    r['out'] = out
    r['err'] = err

    if out: logger.info(out)

    if err: logger.error(err)

    return r

import re
TIME_FORMAT = re.compile(r'((?P<h>[0-9]+):)?((?P<m>[0-9]+):)?(?P<s>[0-9]+)(.(?P<u>[0-9]+))?')

def get_resources(filename):
    def TL(s):
        if not isinstance(s, str):
            return s

        # split on everything, that is not a digit
        matcher = TIME_FORMAT.match(s)
        h = matcher.group('h') or 0
        m = matcher.group('m') or 0
        s = matcher.group('s') or 0
        u = matcher.group('u') or 0

        if m == 0 and h != 0:
            m,h = h,m

        value = 60*60*int(h) + 60 * int(m) +  int(s) + int(u) / 1000
        return value

    def PERCENT(value):
        return int(value[:-1])

    with open(filename) as fp:
        line = ""
        for line in fp:
            pass
        return eval(line)

class Runner(object):
    def __init__(self,
                 environment = None,
                 programs = None,
                 logging = "log/",
                 results ="results.yaml"):
        self.environment = environment
        self.programs = programs
        self.logging = logging
        self.results = results
        self.results_catcher = []
        self._run()

    def _run(self):
        runs = []
        for e in self.environment:
            for p in self.programs:
                runs.append(
                    run_with_rusage(p, e))

        self._write(runs)

    def _write(self, runs):
        with open(self.results, 'w') as fp:
            yaml.dump(runs, fp)
