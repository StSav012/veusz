#    plotters.py
#    plotting classes

#    Copyright (C) 2004 Jeremy S. Sanders
#    Email: Jeremy Sanders <jeremy@jeremysanders.net>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
###############################################################################

# $Id$

import qt
import numarray as N

import widget
import widgetfactory
import axis
import graph
import setting

import utils

def _trim(x, x1, x2):
    """Truncate x in range x1->x2."""
    if x < x1: return x1
    if x > x2: return x2
    return x

class GenericPlotter(widget.Widget):
    """Generic plotter."""

    typename='genericplotter'
    allowedparenttypes=[graph.Graph]

    def __init__(self, parent, name=None):
        """Initialise object, setting axes."""
        widget.Widget.__init__(self, parent, name=name)

        s = self.settings
        s.add( setting.Str('xAxis', 'x',
                           descr = 'Name of X-axis to use') )
        s.add( setting.Str('yAxis', 'y',
                           descr = 'Name of Y-axis to use') )

    def getAxes(self):
        """Get the axes widgets to plot against."""

        xaxis = None
        yaxis = None

        x = self.settings.xAxis
        y = self.settings.yAxis
        
        for i in self.parent.getChildren():
            if i.getName() == x:
                xaxis = i
            if i.getName() == y:
                yaxis = i

        return (xaxis, yaxis)

########################################################################
        
class FunctionPlotter(GenericPlotter):
    """Function plotting class."""

    typename='function'
    allowusercreation=True
    description='Plot a function'
    
    def __init__(self, parent, name=None):
        """Initialise plotter with axes."""

        GenericPlotter.__init__(self, parent, name=name)

        # define environment to evaluate functions
        self.fnenviron = globals()
        exec 'from numarray import *' in self.fnenviron

        s = self.settings
        s.add( setting.Int('steps', 50,
                           descr = 'Number of steps to evaluate the function'
                           ' over'), 0 )
        s.add( setting.Choice('variable', ['x', 'y'], 'x',
                              descr='Variable the function is a function of'),
               0 )
        s.add( setting.Str('function', 'x',
                           descr='Function expression'), 0 )

        s.add( setting.Line('Line',
                            descr = 'Function line settings') )

        s.readDefaults()
        
    def getUserDescription(self):
        """User-friendly description."""
        return "%s = %s" % ( self.settings.variable,
                             self.settings.function )

    def _plotLine(self, painter, xpts, ypts, bounds):
        """ Plot the points in xpts, ypts."""
        x1, y1, x2, y2 = bounds

        # idea is to collect points until we go out of the bounds
        # or reach the end, then plot them
        pts = []
        for x, y in zip(xpts, ypts):

            if x >= x1 and x <= x2 and y >= y1 and y <= y2:
                pts.append(x)
                pts.append(y)
            else:
                if len(pts) >= 4:
                    painter.drawPolyline( qt.QPointArray(pts) )
                    pts = []

        if len(pts) >= 4:
            painter.drawPolyline( qt.QPointArray(pts) )

    def draw(self, parentposn, painter):
        """Draw the function."""

        posn = GenericPlotter.draw(self, parentposn, painter)
        x1, y1, x2, y2 = posn

        # get axes widgets
        axes = self.getAxes()

        # return if there's no proper axes
        if ( None in axes or
             axes[0].settings.direction != 'horizontal' or
             axes[1].settings.direction != 'vertical' ):
            return

        s = self.settings
        if s.variable == 'x':
            # x function
            delta = (x2 - x1) / s.steps
            pxpts = N.arange(x1, x2+delta, delta).astype(N.Int32)
            self.fnenviron['x'] = axes[0].plotterToGraphCoords(posn, pxpts)
            y = eval( s.function + ' + 0*x', self.fnenviron )
            pypts = axes[1].graphToPlotterCoords(posn, y)

        else:
            # y function
            delta = (y2 - y1) / s.steps
            pypts = N.arange(y1, y2+delta, delta).astype(N.Int32)
            self.fnenviron['y'] = axes[1].plotterToGraphCoords(posn, pypts)
            x = eval( s.function + ' + 0*y', self.fnenviron )
            pxpts = axes[0].graphToPlotterCoords(posn, x)

        painter.save()

        # draw the function line
        if not s.Line.hide:
            painter.setBrush( qt.QBrush() )
            painter.setPen( s.Line.makeQPen(painter) )
            self._plotLine(painter, pxpts, pypts, posn)

        painter.restore()

##     def _fillYFn(self, painter, xpts, ypts, bounds, leftfill):
##         """ Take the xpts and ypts, and fill above or below the line."""
##         if len(xpts) == 0:
##             return

##         x1, y1, x2, y2 = bounds

##         if leftfill:
##             pts = [x1, y1]
##         else:
##             pts = [x2, y1]

##         for x,y in zip(xpts, ypts):
##             pts.append( _trim(x, x1, x2) )
##             pts.append(y)

##         if leftfill:
##             pts.append(x2)
##         else:
##             pts.append(x1)
##         pts.append(y2)

##         painter.drawPolygon( qt.QPointArray(pts) )

##     def _fillXFn(self, painter, xpts, ypts, bounds, belowfill):
##         """ Take the xpts and ypts, and fill to left or right of the line."""
##         if len(ypts) == 0:
##             return

##         x1, y1, x2, y2 = bounds

##         if belowfill:
##             pts = [x1, y2]
##         else:
##             pts = [x1, y1]

##         for x,y in zip(xpts, ypts):
##             pts.append(x)
##             pts.append( _trim(y, y1, y2) )

##         pts.append( x2 )
##         if belowfill:
##             pts.append( y2 )
##         else:
##             pts.append( y1 )

##         painter.drawPolygon( qt.QPointArray(pts) )

##     def draw(self, parentposn, painter):
##         """Plot the function."""

##         posn = GenericPlotter.draw(self, parentposn, painter)

##         # the algorithm is to work out the fn for each pixel on the plot
##         # need to convert pixels -> graph coord -> calc fn -> pixels

##         x1, y1, x2, y2 = posn

##         ax1 = self.getAxisVar( self.axes[0] )
##         ax2 = self.getAxisVar( self.axes[1] )

##         if self.xfunc:
##             xplotter = numarray.arange(x1, x2+1, self.iter)
##             self.fnenviron['x'] = ax1.plotterToGraphCoords(posn, xplotter)
##             # HACK for constants
##             y = eval( self.function + " + (0*x)", self.fnenviron )
##             yplotter = ax2.graphToPlotterCoords(posn, y)
##         else:
##             yplotter = numarray.arange(y1, y2+1, self.iter)
##             self.fnenviron['y'] = ax2.plotterToGraphCoords(posn, yplotter)
##             # HACK for constants
##             x = eval( self.function + " + (0*y)", self.fnenviron )
##             xplotter = ax1.graphToPlotterCoords(posn, x)

##         # here we go through the generated points, and plot those that
##         # are in the plot (we can clip fairly easily).
##         # each time there is a section we can plot, we plot it
        
##         painter.save()
##         painter.setPen( qt.QPen( qt.QColor(), 0, qt.Qt.NoPen ) )

##         painter.setBrush( qt.QBrush(qt.QColor("darkcyan"),
##                                     qt.Qt.Dense6Pattern) )
##         self._fillXFn(painter, xplotter, yplotter, posn, 1)
        
##         painter.setBrush( qt.QBrush() )
##         painter.setPen( self.Line.makeQPen(painter) )
##         self._plotLine(painter, xplotter, yplotter, posn)

##         painter.restore()

# allow the factory to instantiate an function plotter
widgetfactory.thefactory.register( FunctionPlotter )

###############################################################################
        
class PointPlotter(GenericPlotter):
    """A class for plotting points and their errors."""

    typename='xy'
    allowusercreation=True
    description='Plot points with lines and errorbars'
    
    def __init__(self, parent, name=None):
        """Initialise XY plotter plotting (xdata, ydata).

        xdata and ydata are strings specifying the data in the document"""
        
        GenericPlotter.__init__(self, parent, name=name)
        s = self.settings
        s.add( setting.Distance('markerSize', '3pt'), 0 )
        s.add( setting.Choice('marker', utils.MarkerCodes, 'circle'), 0 )
        s.add( setting.Str('yData', 'y',
                           descr = 'Variable containing y data'), 0 )
        s.add( setting.Str('xData', 'x',
                           descr = 'Variable containing x data'), 0 )
        s.readDefaults()

        s.add( setting.Line('PlotLine',
                            descr = 'Plot line settings') )
        s.add( setting.Line('MarkerLine',
                            descr = 'Line around the marker settings') )
        s.add( setting.Brush('MarkerFill',
                             descr = 'Marker fill settings') )
        s.add( setting.Line('ErrorBarLine',
                            descr = 'Error bar line settings') )

    def getUserDescription(self):
        """User-friendly description."""

        s = self.settings
        return "x='%s', y='%s', marker='%s'" % (s.xData, s.yData,
                                                s.marker)

    def _plotErrors(self, posn, painter, xplotter, yplotter,
                    axes):
        """Plot error bars (horizontal and vertical)."""

        # list of output lines
        pts = []

        # get the data
        xdata = self.getDocument().getData(self.settings.xData)

        # draw horizontal error bars
        if xdata.hasErrors():
            xmin, xmax = xdata.getPointRanges()
                    
            # convert xmin and xmax to graph coordinates
            xmin = axes[0].graphToPlotterCoords(posn, xmin)
            xmax = axes[0].graphToPlotterCoords(posn, xmax)

            # draw lines between each of the points
            for i in zip(xmin, yplotter, xmax, yplotter):
                pts += i

        # draw vertical error bars
        # get data
        ydata = self.getDocument().getData(self.settings.yData)
        if ydata.hasErrors():
            ymin, ymax = ydata.getPointRanges()

            # convert ymin and ymax to graph coordinates
            ymin = axes[1].graphToPlotterCoords(posn, ymin)
            ymax = axes[1].graphToPlotterCoords(posn, ymax)

            # draw lines between each of the points
            for i in zip(xplotter, ymin, xplotter, ymax):
                pts += i

        # finally draw the lines
        if len(pts) != 0:
            painter.drawLineSegments( qt.QPointArray(pts) )
            
    def _autoAxis(self, dataname):
        """Determine range of data."""
        if self.getDocument().hasData(dataname):
            return self.getDocument().getData(dataname).getRange()
        else:
            return None

    def autoAxis(self, name):
        """Automatically determine the ranges of variable on the axes."""

        s = self.settings
        if name == s.xAxis:
            return self._autoAxis( s.xData )
        elif name == s.yAxis:
            return self._autoAxis( s.yData )
        else:
            return None

    def _drawPlotLine( self, painter, xvals, yvals ):
        """Draw the line connecting the points."""

        pts = []
        for xpt, ypt in zip(xvals, yvals):
            pts.append(xpt)
            pts.append(ypt)

        painter.drawPolyline( qt.QPointArray(pts) )

    def draw(self, parentposn, painter):
        """Plot the data on a plotter."""

        posn = GenericPlotter.draw(self, parentposn, painter)
        x1, y1, x2, y2 = posn

        # skip if there's no data
        d = self.getDocument()
        s = self.settings
        if not d.hasData(s.xData) or not d.hasData(s.yData):
            return
        
        # get axes widgets
        axes = self.getAxes()

        # return if there's no proper axes
        if ( None in axes or
             axes[0].settings.direction != 'horizontal' or
             axes[1].settings.direction != 'vertical' ):
            return

        xvals = d.getData(s.xData)
        yvals = d.getData(s.yData)

        # no points to plot
        if xvals.empty() or yvals.empty():
            return

        # clip data within bounds of plotter
        painter.save()
        painter.setClipRect( qt.QRect(x1, y1, x2-x1, y2-y1) )

        # calc plotter coords of x and y points
        xplotter = axes[0].graphToPlotterCoords(posn, xvals.data)
        yplotter = axes[1].graphToPlotterCoords(posn, yvals.data)

        # plot data line
        if not s.PlotLine.hide:
            painter.setPen( s.PlotLine.makeQPen(painter) )
            self._drawPlotLine( painter, xplotter, yplotter )

        # plot errors bars
        if not s.ErrorBarLine.hide:
            painter.setPen( s.ErrorBarLine.makeQPen(painter) )
            self._plotErrors(posn, painter, xplotter, yplotter,
                             axes)

        # plot the points (we do this last so they are on top)
        if not s.MarkerLine.hide or not s.MarkerFill.hide:
            size = int( utils.cnvtDist(s.markerSize, painter) )

            if not s.MarkerFill.hide:
                painter.setBrush( s.MarkerFill.makeQBrush() )

            if not s.MarkerLine.hide:
                painter.setPen( s.MarkerLine.makeQPen(painter) )
            else:
                painter.setPen( qt.QPen( qt.Qt.NoPen ) )
                
            utils.plotMarkers(painter, xplotter, yplotter, s.marker,
                              size)

        painter.restore()

# allow the factory to instantiate an x,y plotter
widgetfactory.thefactory.register( PointPlotter )

###############################################################################
