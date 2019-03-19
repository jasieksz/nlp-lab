#%%
from lab1 import processor
resource_path = 'resources/ustawy/'
filename1 = '1999_804.txt'
filename2 = '1995_681.txt'
filename3 = '2004_2699.txt'
sp = processor.StatuteProcessor(resource_path + filename1)
sp.get_external_references()

