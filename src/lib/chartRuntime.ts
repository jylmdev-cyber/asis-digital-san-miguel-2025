import {init,use} from 'echarts/core';
import {BarChart} from 'echarts/charts';
import {GridComponent,TooltipComponent,LegendComponent,AriaComponent} from 'echarts/components';
import {CanvasRenderer} from 'echarts/renderers';
use([BarChart,GridComponent,TooltipComponent,LegendComponent,AriaComponent,CanvasRenderer]);
export {init};
