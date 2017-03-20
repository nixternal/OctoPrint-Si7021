#!/usr/bin/env python
# coding=utf-8
from si7021 import Si7021
from smbus import SMBus

sensor = Si7021(SMBus(1))
rh, c = sensor.read()
f = c * 9/5.0 + 32
print rh, c, f
