import os
from datetime import datetime as dt
from tempfile import TemporaryFile

import param
import panel as pn
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt

from templates.template import template
from static.css import css
from static.description import description
from static.blockquote import blockquote
from interpolate import Interpolate
import config as c

pn.config.raw_css = [css,]

name = 'lidar-nn'
tmpl = pn.Template(template)
tmpl.add_variable('app_title', name)
tmpl.add_variable('description', description)
tmpl.add_variable('blockquote', blockquote)

class Interact(param.Parameterized):
    '''

    '''
    def __init__(self):
        super(Interact, self).__init__()
        self.filelist = os.listdir(name + '/data')
        self.filelist.sort()
        self.dates = [dt.strptime(fn[:8], '%Y%m%d') for fn in self.filelist]
        self.dict = {d.strftime('%Y-%m-%d'):i for i,d in enumerate(self.dates)}

    nums = [i for i in range(74)] #update this
    date = param.Selector(default=70, objects=nums)
    res = param.Integer(30, bounds=(10, 300), step=10)
    sigma = param.Number(1.0, bounds=(0.0, 3.0))

    @staticmethod
    def _format_plt(fig, ax, title, 
                    m=0.02, bgc='#292929', axc='#eee', lblc='#fff'):
        ax.margins(m)
        ax.set_aspect(aspect=1)
        ax.set_xlabel('Easting')
        ax.set_ylabel('Northing')
        ax.set_title(title, color=axc, loc='left', pad=20)
        ax.xaxis.label.set_color(lblc)
        ax.yaxis.label.set_color(lblc)
        ax.tick_params(axis='x', colors=lblc)
        ax.tick_params(axis='y', colors=lblc)
        ax.spines['bottom'].set_color(axc)
        ax.spines['top'].set_color(axc) 
        ax.spines['right'].set_color(axc)
        ax.spines['left'].set_color(axc)
        ax.set_facecolor(bgc)
        fig.patch.set_facecolor(bgc)

    @staticmethod
    def _set_title(fn, opt='scatter'):
        '''
        '''
        date = fn[:4] + '-' + fn[4:6] + '-' + fn[6:8]

        if opt == 'scatter':
            return date + ': LiDAR Pointcloud'
        if opt == 'grid':
            return date + ': Interpolation'

    @param.depends('date')
    def input(self):
        '''
        '''
        fig, ax = plt.subplots(1)

        self.filename = self.filelist[self.date]
        self.data = Interpolate(filename=self.filename, bounds=c.BOUNDS)
        xyz = self.data.xyz

        ax.scatter(x=xyz[:,0], y=xyz[:,1], c=xyz[:,2], cmap='viridis')
        
        title = self._set_title(fn=self.filename)
        self._format_plt(fig=fig, ax=ax, title=title)
        
        plt.close('all')

        return fig

    @param.depends('res', 'sigma')
    def output(self):
        '''
        '''
        fig, ax = plt.subplots(1)

        grid = self.data.interpolate_grid(xyz=self.data.xyz, res=self.res)
        self.array = ndimage.gaussian_filter(grid, sigma=self.sigma)

        ax.imshow(self.array, origin='lower')

        title = self._set_title(fn=self.data.filename, opt='grid')
        self._format_plt(fig=fig, ax=ax, title=title)

        plt.close('all')

        return fig

    def export(self):
        '''
        '''
        outfile = TemporaryFile()
        np.save(outfile, self.array)
        _ = outfile.seek(0)
        res = str(self.res) if len(str(self.res))==3 else '0'+str(self.res)
        params = f'R{res}S{str(self.sigma).replace(".", "")}'
        name = f'{self.filename[:8]}_NN{params}.npy'
        return pn.widgets.FileDownload(file=outfile, filename=name)


interact = Interact()

input_params = [interact.param.date,]
output_params = [interact.param.res, interact.param.sigma,]

tmpl.add_panel('A', pn.Column(interact.input, *input_params))
tmpl.add_panel('B', pn.Column(interact.output, *output_params))
tmpl.add_panel('C', interact.export)

tmpl.servable()
