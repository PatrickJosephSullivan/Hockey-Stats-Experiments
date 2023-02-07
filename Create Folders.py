import os

for i in range(700,731):
  folder_name = str(i)
  os.makedirs(folder_name + '/before')
  os.makedirs(folder_name + '/after')