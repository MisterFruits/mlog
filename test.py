
# coding: utf-8

# In[82]:

import pandas as pd
import numpy as np
import datetime
import faker

faker = faker.Faker()
def random_date(start, end, position=None):
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    delta = (end - start).total_seconds()
    if position is None:
        offset = np.random.uniform(0., delta)
    else:
        offset = position * delta
    offset = pd.offsets.Second(offset)
    t = start + offset
    return t

modules = {faker.file_name().split('.')[0]: [faker.ipv4() for _ in range(faker.random_int(min=1, max=3))] for _ in range(20)}
def pick_module():
    name = faker.random_element(modules.keys())
    version = faker.random_element(modules[name])
    return name, version



# In[93]:

dates = sorted([random_date(datetime.datetime(2015, 1, 1), datetime.datetime(2016, 1, 1)) for _ in range(1000)])
users = [faker.user_name().split('.')[0] for _ in range(100)]
datas = []
for date, user in zip(dates, [faker.random_element(users) for _ in dates]):
    datas.extend([(date, user, pick_module()) for _ in range(faker.random_int(min=3, max=7))])
df = pd.DataFrame(datas, columns=['date',"uid", 'module'])
df['module_name'] = df.module.map(lambda x: x[0])
df['module_version'] = df.module.map(lambda x: x[1])


# In[98]:

grouped = df.groupby([df.date.dt.year, df.date.dt.month, df.module_name, df.module_version])
count = grouped.count()
count


# In[72]:

test =df['module']


# In[76]:

test[:,0]


# In[79]:

range(*[4,3])


# In[ ]:



