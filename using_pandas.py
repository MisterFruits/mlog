
# coding: utf-8

# In[ ]:

get_ipython().magic('pylab inline')
import dateutil.parser
import pandas as pd

def is_date_parsable(datestr):
    try:
        dateutil.parser.parse(datestr);
        return True
    except ValueError:
        return False

just_parsed = pd.io.parsers.read_csv('module_compta_20151214', sep=';', error_bad_lines=False,
                            names=['module', 'date', 'host', 'uid', 'notafield'])
just_parsed = just_parsed[['module', 'date', 'host', 'uid']]
rule = [True] * len(just_parsed)
for el in just_parsed:
    rule = rule & just_parsed[el].map(lambda x:type(x) == type('str'))
just_parsed = just_parsed[rule]
for el in just_parsed:
    just_parsed[el] = just_parsed[el].map(lambda x:x.strip())

date_parsed = just_parsed[just_parsed['date'].map(is_date_parsable)]
date_parsed['date'] = date_parsed['date'].map(dateutil.parser.parse)
mindate, maxdate = min(df["date"]), max(df["date"])
# date_parsed['date'] = date_parsed['date'].map(lambda x: np.datetime64(x.date())) # useless, auto parsed in this format


# In[17]:

module_df = pd.DataFrame(list(date_parsed.module.str.split('/', 1)), columns=["module_name", "module_version"], index=date_parsed.index)
print(len(date_parsed), len(module_df))
df = pd.concat([date_parsed, module_df], axis=1)


# In[61]:

bins = pd.date_range(mindate, maxdate, freq='D')
fronteaux = df[(df.host == 'occigen50') | (df.host == 'occigen51') | (df.host == 'occigen52') | (df.host == 'occigen53') |(df.host == 'occigen54')]


# In[91]:

group = fronteaux.groupby([fronteaux.module_name, fronteaux.module_version, fronteaux.date.dt.date])
dir(group.agg({"uid": pd.Series.nunique}))


# In[84]:

fronteaux.groupby([fronteaux.date]).uid.nunique()
    


# In[ ]:




# In[32]:

xlim(bins[0], bins[-1])
xlabel('time')
ylabel('# number of loaded modules')
hist(df['date'], bins=bins)


# In[ ]:

df[is_oyelekci & is_python_module]
df = df[['module', 'date', 'host', 'uid']]
for el in ['module', 'host', 'uid']:
    df[el] = df[el].map(lambda x:x.strip())

def is_module(df, module_name):
    return df['module'].map(lambda x:x.startswith("{}/".format(module_name)))

is_python_module = is_module(df, "python")
is_oyelekci = df['uid'].map(lambda x:x.strip()) == "oyelekci"

