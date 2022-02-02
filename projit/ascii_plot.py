from math import log, exp
"""
    This function was taken from the GitHub gist https://gist.github.com/fransua/6165813
    It was modified to work with Python 3, provide neater formatting on the tick labels
    and fix some problems with extreme values being occasionally ommitted.
    Note: Plot title was removed because we will be using it within functions that precede
          the calls with their own titles.
"""

def ascii_plot (ydata, xdata=None, logscale=False, pch='o', 
                xlabel='X', ylabel='Y', width=72, height=50):
    """
    :param ydata: list of values to be plotted
    :param None xdata: x coordinate corresponding to ydata. If None will range
       between 1 and the length of ydata.
    :param False logscale: display data with logarithmic Y axis
    :param 'o' pch: string for points (whatever + = - * etc...)
    :param 'plot' title: string for title of the plot
    :param 'X' xlabel: label for the X axis
    :param 'Y' ylabel: label for the Y axis
    :param 100 width: width in term of characters
    :param 100 height: height in term of characters
    :returns: string corresponding to plot
    """
    if not xdata:
        xdata = range(1, len(ydata)+1)
    yydata = []
    logf = log if logscale else lambda x: x
    expf = exp if logscale else lambda x: x
    for i in ydata:
        try:
            yydata.append(logf(i))
        except ValueError:
            yydata.append(float('-inf'))
    ymax = max(yydata)
    ymax = ymax + (ymax*0.05)
    ydiff = float(abs(float(min(yydata)) - ymax)/(height * 2))
    y_arange = [(i - ydiff, i + ydiff) for i in
                sorted(arange(min(yydata), ymax + ydiff, ydiff * 2), reverse=True)]
    xdiff = float(abs(float(min(xdata)) - max(xdata)))/(width * 2)
    x_arange = [(i-xdiff, i+xdiff) for i in
                sorted(arange(float(min(xdata)), max(xdata) + xdiff, xdiff * 2))]
    graph = ylabel
    graph += '\n'
    val = 6 - max([len('{0:.0f}'.format(y)) for _, y in y_arange])
    form = '{' + ':<7.{}f'.format(val) + '}'

    def add_y_point(value):
        temp = form.format(value)
        temp2 = temp.rstrip(' ')
        spacer = len(temp) - len(temp2)
        temp2 = temp2.rstrip('0')
        if temp2[-1] == ".":
            temp2 += "0"
        diff = len(temp) - len(temp2) - spacer
        temp3 = (" "*spacer) + temp2 + (" "*diff) + "+"
        return temp3

    graph +=  add_y_point( expf(ymax) )
    for yval, (y1, y2) in enumerate(y_arange):
        graph+='\n'
        if not (yval)%5 and yval != 0:
            graph += add_y_point(expf((y1+y2)/2))
        else:
            graph += ' ' * 7 + '|'
        pos = 0
        for x1, x2 in x_arange:
            for i in range(pos, len(yydata)):
                if (y1 < yydata[i] <= y2 and
                    x1 < xdata[i]  <= x2):
                    graph += pch
                    pos += 1
                    break
            else:
                graph += ' '
    graph += '\n'
    if logscale:
        graph += ' 1/inf ' + ''.join(
            ['+' if not x%10 else '-' for x in range(width+1)]) + '\n'
    else:
        graph += '     0 ' + ''.join(
            ['+' if not x%10 else '-' for x in range(width+1)]) + '\n'
    val = 7 - max([len('{0:.0f}'.format(y)) for _, y in x_arange])
    form = '{' + ':<7.{}f'.format(val) + '}  '

    def add_x_point(value):
        temp = form.format(value)
        temp2 = temp.rstrip(' ')
        temp2 = temp2.rstrip('0')
        if temp2[-1] == ".":
            temp2 += "0"
        diff = len(temp) - len(temp2) 
        temp3 =  temp2 + (" "*diff) 
        return temp3

    graph += ' '*7 + ''.join(
        [ add_x_point(float(sum(x_arange[x])/2)) for x in range(0,width,10)]
    ) + ('' if width % 10 else add_x_point(float(sum(x_arange[-1])/2)))+ '\n'
    graph += ' ' * 7 + '{0:^{1}}'.format(xlabel, width)
    graph += '\n'
    return graph


def arange(beg, end, step):
    return [beg + i * step for i in range(int(abs(beg-end)/step+.5))]


