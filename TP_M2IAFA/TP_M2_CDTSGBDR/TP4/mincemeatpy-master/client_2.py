#!/usr/bin/env python
import mincemeat

client = mincemeat.Client()
client.password = "changeme".encode('utf-8')
client.conn("localhost", mincemeat.DEFAULT_PORT)