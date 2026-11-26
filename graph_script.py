import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path


# Settings
cwd = Path(__file__).parent

response = 'GFP_%'
ylabel = '% eGFP+'
lipo_ratio = 3

# Load data
df = pd.read_excel(cwd / r'468-040-01_tidy_data.xlsx', engine='calamine')
df['dna_dose, ng'] = df['dna_dose, ng'].fillna(0)
df['mrna_dose, ng'] = df['mrna_dose, ng'].fillna(0)

# Filter for lipofectamine
plot_df = df[(df['lipo_ratio, 1:'] == lipo_ratio)]

sample_order = [
     {'label': 'Mock',
      'filter': plot_df['fccs_sample_name'].str.contains('01_Mock', case=False, na=False),
      'dna': 0,
      'mrna': 0
      },

     {'label': 'Lipofectamine 1:3',
      'filter': plot_df['fccs_sample_name'].str.contains('03_Mock', case=False, na=False),
        'dna': 0,
      'mrna': 0
      },

      {'label': '0/50',
      'dna': 0,
      'mrna': 50
      },

      {'label': '0/100',
      'dna': 0,
      'mrna': 100
      },

      {'label': '100/50',
      'dna': 100,
      'mrna': 50
      },

      {'label': '100/100',
      'dna': 100,
      'mrna': 100
      },

      {'label': '100/150',
      'dna': 100,
      'mrna': 150
      },
      ]

# Automatic sample order
dna_doses = sorted({sample['dna'] for sample in sample_order if 'dna' in sample})
mrna_doses = sorted(df['mrna_dose, ng'].unique())

# Extract means and replicates
mean24 = []
mean48 = []

replicates24 = []
replicates48 = []

tick_labels = []

for sample in sample_order:
    print(sample['dna'], sample['mrna'])

    if 'filter' in sample:

        subset24 = plot_df[
            sample['filter'] & (df['time, h'] == 24)
            ]

        subset48 = plot_df[
            sample['filter'] & (df['time, h'] == 48)
            ]

    else:

        subset24 = plot_df[
        (plot_df['time, h'] == 24) &
        (plot_df['dna_dose, ng'] == sample['dna']) &
        (plot_df['mrna_dose, ng'] == sample['mrna'])
        ]

        subset48 = plot_df[
        (plot_df['time, h'] == 48) &
        (plot_df['dna_dose, ng'] == sample['dna']) &
        (plot_df['mrna_dose, ng'] == sample['mrna'])
        ]


    mean24.append(subset24[response].mean())
    mean48.append(subset48[response].mean())

    replicates24.append(subset24[response].values)
    replicates48.append(subset48[response].values)

print(subset24)
print(replicates24)

labels = [sample['label'] for sample in sample_order]
tick_labels = [sample['label'] for sample in sample_order]


# Plot
x = np.arange(len(sample_order))
w = 0.35

fig, ax = plt.subplots(figsize=(8,5))

bars24 = ax.bar(
    x - w/2,
    mean24,
    width=w,
    color='lightgreen',
    label='24h'
    )

bars48 = ax.bar(
    x + w/2,
    mean48,
    width=w,
    color='green',
    label='48h'
    )

# Technical replicates
for i, vals in enumerate(replicates24):

    if len(vals) == 0:
        continue

    jitter = np.linspace(-0.05, 0.05, len(vals))
    ax.scatter(
        np.repeat(x[i] - w/2, len(vals)) + jitter,
        vals,
        color='black',
        s=25,
        zorder=10
        )

for i, vals in enumerate(replicates48):

    if len(vals) == 0:
            continue

    jitter = np.linspace(-0.05, 0.05, len(vals))
    ax.scatter(
        np.repeat(x[i] + w/2, len(vals)) + jitter,
        vals,
        color='black',
        s=25,
        zorder=10
        )

# Axes formatting
ax.set_title(f'Lipofectamine 1:{lipo_ratio}')

ax.set_ylabel(ylabel)
ax.set_ylim(0,110)

ax.set_xlabel('mCherry dose (ng)')
ax.set_xticks(x)
ax.set_xticklabels(tick_labels)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.grid(axis='y', alpha=0.3)
ax.legend(loc='upper left', frameon=False)

# DNA group labels
for dna in dna_doses:

    positions = [i for i, sample in enumerate(sample_order) if sample.get('dna') == dna]

    start = min(positions)
    end = max(positions)

    center = (start + end) / 2

    ax.plot(
        [start, end],
        [-0.12, -0.12],
        transform=ax.get_xaxis_transform(),
        clip_on=False,
        color='black'
    )

    ax.text(
        center,
        -0.18,
        f'{dna} ng',
        transform=ax.get_xaxis_transform(),
        ha='center',
        fontsize=11
    )

# Row labels
ax.text(
    -0.02,
    -0.08,
    'mCherry dose (ng)',
    transform=ax.transAxes,
    ha='center'
)

ax.text(
    0.5,
    -0.28,
    'DNA dose',
    transform=ax.transAxes,
    ha='center'
)

plt.subplots_adjust(bottom=0.28)

plt.tight_layout()
plt.show()


# for filename, title, yl, d24, d48, co24, co48, base, hc in plots:

#     x=np.arange(6)
#     w=0.36

#     fig, ax= plt.subplots(figsize=(10,5))

#     b1=ax.bar(x-w/2,d24,w,color=base,alpha=.55,label='24 h')
#     b2=ax.bar(x+w/2,d48,w,color=base,label='48 h')

#     # np.minimum(dxx, coxx) caps hatch overlay at parent bar height
#     ax.bar(x-w/2,np.minimum(d24,co24),w,color='none',edgecolor=hc,hatch='////',label='Co-transfected')
#     ax.bar(x+w/2,np.minimum(d48,co48),w,color='none',edgecolor=hc,hatch='////')

#     for bars,vals,cos in [(b1,d24,co24),(b2,d48,co48)]:
#       for r,v,c in zip(bars,vals,cos):
#         x_pos=r.get_x()+r.get_width()/2
#         value_y=v+1
#         co_y=min(v,c)+1.6
#         if v>=1 and c>=1 and abs(value_y-co_y)<5:
#           if value_y>=co_y:
#             ax.text(x_pos,value_y,f'{v:.1f}',ha='center',fontsize=8)
#           else:
#             ax.text(x_pos,co_y,f'{c:.1f}',ha='center',fontsize=8,color='black')
#         else:
#           if v>=1: ax.text(x_pos,value_y,f'{v:.1f}',ha='center',fontsize=8)
#           if c>=1: ax.text(x_pos,co_y,f'{c:.1f}',ha='center',fontsize=8,color='black')

#     ax.set_ylim(0,110)
#     ax.spines['top'].set_visible(False)
#     ax.spines['right'].set_visible(False)
#     ax.set_axisbelow(True)
#     ax.grid(axis='y',which='major',color='gray',alpha=0.25,linewidth=0.8)
#     ax.set_ylabel(yl)
#     ax.set_title(title)

#     ax.set_xticks(range(6))
#     ax.set_xticklabels(['50','100','','','',''])

#     ax.legend(loc='upper left',frameon=False)

#     ax.plot([0.42,0.9],[-0.15,-0.15],transform=ax.transAxes,clip_on=False,color='black',lw=1.8)

#     ax.text(0.65,-0.22,'eGFP, 100 ng',transform=ax.transAxes,ha='center',fontsize=11)
#     ax.text(0.0,-0.1,'mCherry, ng',transform=ax.transAxes,ha='center',fontsize=11)

#     ax.text(0.42,-0.1,'-',transform=ax.transAxes,ha='center')
#     ax.text(0.58,-0.1,'50',transform=ax.transAxes,ha='center')
#     ax.text(0.74,-0.1,'100',transform=ax.transAxes,ha='center')
#     ax.text(0.9,-0.1,'150',transform=ax.transAxes,ha='center')

#     plt.subplots_adjust(bottom=0.2)

#     plt.savefig(cwd + f'/{filename}',dpi=300,bbox_inches='tight')
#     plt.close()

# print('done')

