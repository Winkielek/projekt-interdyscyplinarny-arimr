#!/usr/bin/env python
# coding: utf-8

# In[33]:


import pyproj

y_in = 695148.4
x_in = 750315.6

input_proj = pyproj.Proj(init='epsg:2180')
output_proj = pyproj.Proj(init="epsg:4326")

x_out, y_out = pyproj.transform(input_proj, output_proj, x_in, y_in)
print (x_out, y_out)

