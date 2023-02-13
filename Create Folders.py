import os

for i in range(914,931):
  folder_name = str(i)
  os.makedirs(folder_name + '/Before')
  os.makedirs(folder_name + '/After')