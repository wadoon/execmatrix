#!/usr/bin/env python3
#-*- encoding: utf-8 -*-


from execmatrix import *


m = Environment(
    ("N", range(0,2))
)

p = ["sleep 1", "test"]
Runner(environment=m,
       programs=p,
       logging = "log/",
       results = "test.yaml"
)
