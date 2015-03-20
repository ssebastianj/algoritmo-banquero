#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Sebastián J. Seba

from __future__ import print_function

import itertools


class DeadLock(object):
    def __init__(self, asignados, maximos, disponible):
        self._asignados = asignados
        self._maximos = maximos
        self._disponible = disponible
        self._proc_count = len(asignados)
        self._calcular_necesidades()

    def _calcular_necesidades(self):
        self._necesidades = [[i - j for i, j in zip(x, y)]
                             for x, y in zip(self._maximos, self._asignados)]

    def is_secure(self, secuencia):
        final = [False for f in range(self._proc_count)]
        trabajo = self._disponible

        for m in secuencia:
            if (final[m] is False) \
                and self._less_equal(self._necesidades[m], trabajo):
                final[m] = True
                trabajo = [x + y for x, y in zip(trabajo, self._asignados[m])]
            else:
                break

        try:
            final.index(False)
            secure = False
        except ValueError:
            secure = True

        return secure

    def get_secure_sequences(self):
        permutaciones = list(itertools.permutations(range(self._proc_count)))
        secuencias = [per for per in permutaciones if self.is_secure(per)]

        return secuencias

    def _save_status(self):
        self._asignados_bkp = list(self._asignados)
        self._disponible_bkp = list(self._disponible)
        self._maximos_bkp = list(self._maximos)
        self._necesidades_bkp = list(self._necesidades)

    def _rollback(self):
        self._asignados = self._asignados_bkp
        self._disponible = self._disponible_bkp
        self._maximos = self._maximos_bkp
        self._necesidades = self._necesidades_bkp

    def assign_resources(self, nro_proceso, solicitud, auto_rollback=True):
        cond1 = self._less_equal(solicitud, self._necesidades[nro_proceso])
        cond2 = self._less_equal(solicitud, self._disponible)

        if cond1 and cond2:
            self._save_status()
            self._disponible = [x - y
                                for x, y
                                in zip(self._disponible, solicitud)]
            self._asignados[nro_proceso] = [a + b
                                            for a, b
                                            in zip(self._asignados[nro_proceso],
                                                                   solicitud)]
            self._necesidades[nro_proceso] = [c - d
                                              for c, d
                                              in zip(self._necesidades[
                                                  nro_proceso], solicitud)]

            if auto_rollback:
                self._rollback()

            return True
        else:
            return False

    def assign_and_test(self, nro_proceso, solicitud, auto_rollback=True):
        secure = False
        if self.assign_resources(nro_proceso, solicitud, False):
            if self.get_secure_sequences():
                secure = True

            if auto_rollback:
                self._rollback()

        return secure

    def _less_equal(self, iterable1, iterable2):
        res = [i for i, j in zip(iterable1, iterable2) if i > j]

        if res:
            return True
        else:
            return False

    @property
    def necesidades(self):
        return self._necesidades

    @property
    def asignados(self):
        return self._asignados

    @property
    def maximos(self):
        return self._maximos

    @property
    def disponible(self):
        return self._disponible

    @property
    def proc_count(self):
        return self._proc_count

if __name__ == '__main__':
    deadlock = DeadLock([[2, 1, 1, 1], [1, 0, 0, 1], [1, 0, 3, 1],
                        [3, 0, 0, 1], [1, 2, 1, 3]], [[3, 2, 1, 1],
                        [2, 1, 3, 3], [3, 1, 3, 3], [4, 2, 1, 2],
                        [3, 3, 2, 5]], [1, 2, 3, 2])

    print(deadlock.assign_and_test(3, [1, 0, 0, 2]))
    print(deadlock.assign_and_test(2, [1, 1, 0, 1]))
    print(deadlock.assign_and_test(1, [1, 1, 3, 1]))
    print(deadlock.assign_and_test(0, [3, 2, 0, 0]))
