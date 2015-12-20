import sys
import matplotlib.pyplot as plt
import numpy as np
import mysql.connector
from scipy import optimize
from scipy import interpolate
import pickle
import math
import time
from lmfit import Model
from matplotlib.backends.backend_pdf import PdfPages


PEAK_FIT_WIDTH = 25
DATEPLOT_TABLE = 'dateplots_mgw'
DATEPLOT_TYPE = 273
MEASUREMENT_TABLE = 'measurements_tof'
XY_VALUES_TABLE= 'xy_values_tof'
NORMALISATION_FIELD = 'tof_iterations'

def fit_peak(time, peaks, data, ax=None):
    center = np.where(Data[:,0] > time)[0][0]
    Start = center - 125 #Display range
    End = center + 125
    X_values = Data[Start:End,0]
    Y_values = Data[Start:End,1]
    center = np.where(Y_values == max(Y_values))[0][0]

    background = np.mean(Y_values[center-3*PEAK_FIT_WIDTH:center-2*PEAK_FIT_WIDTH])
    print('Background: ' + str(background))

    fit_width = PEAK_FIT_WIDTH + PEAK_FIT_WIDTH * (peaks-1) * 0.5
    #Fitting range
    x_values = X_values[center-fit_width:center+fit_width]
    y_values = Y_values[center-fit_width:center+fit_width]

    if peaks == 1:
        fitfunc = lambda p, x: p[0]*math.e ** (-1 * ((x - time - p[2]) ** 2) / p[1])
        p0 = [max(Y_values)-2, 0.00001, 0] # Initial guess for the parameters
    if peaks == 2:
        fitfunc = lambda p, x: p[0]*math.e ** (-1 * ((x - time - p[2]) ** 2) / p[1])
        p0 = [max(Y_values)-2, 0.00001, 0] # Initial guess for the parameters
        
        #fitfunc = lambda p, x: p[0]*math.e ** (-1 * ((x - time - p[2]) ** 2) / p[1]) + p[3]*math.e ** (-1 * ((x - time - p[4]) ** 2) / p[5])
        #p0 = [max(Y_values)-2, 0.00001, 0, max(Y_values)-2, 0.00001, 0.02] # Initial guess for the parameters
    errfunc = lambda p, x, y: fitfunc(p, x) - y # Distance to the target function

    try:
        p1, success = optimize.leastsq(errfunc, p0[:], args=(x_values, y_values-background),maxfev=10000) 
    except: # Fit failed
        p1 = p0
        success = 0
    usefull = (p1[0] > 1.5) and (p1[1] < 1e-3) and (success==1) # Only use the values if fit succeeded and peak has decent height
    area_fit = math.sqrt(math.pi)*p1[0] * math.sqrt(p1[1])
    
    area_count = np.sum(Y_values) - background*len(Y_values)
    if ax is not None:
        ax.plot(X_values, Y_values, 'k-')
        ax.plot(X_values, fitfunc(p1, X_values)+background, 'r-')
        ax.axvline(X_values[center-fit_width])
        ax.axvline(X_values[center+fit_width])
        ax.annotate(str(time), xy=(.05,.85), xycoords='axes fraction',fontsize=8)
        ax.annotate("Fit Area: {0:.0f}".format(area_fit*2500), xy=(.05,.8), xycoords='axes fraction',fontsize=8)
        ax.annotate("Count Area: {0:.0f}".format(area_count), xy=(.05,.75), xycoords='axes fraction',fontsize=8)
        ax.annotate("Usefull: " + str(usefull), xy=(.05,.7), xycoords='axes fraction',fontsize=8)
        #plt.show()
    return usefull, p1, area_count

def fit_peak_lm(time, peaks, data, ax=None):
    center = np.where(Data[:,0] > time)[0][0]
    Start = center - 125 #Display range
    End = center + 125
    X_values = Data[Start:End,0]
    Y_values = Data[Start:End,1]
    center = np.where(Y_values == max(Y_values))[0][0]

    background = np.mean(Y_values[center-3*PEAK_FIT_WIDTH:center-2*PEAK_FIT_WIDTH])
    print('Background: ' + str(background))

    fit_width = PEAK_FIT_WIDTH + PEAK_FIT_WIDTH * (peaks-1) * 0.5
    #Fitting range
    x_values = X_values[center-fit_width:center+fit_width]
    y_values = Y_values[center-fit_width:center+fit_width]

    if peaks == 1:
        fitfunc = lambda p, x: p[0]*math.e ** (-1 * ((x - time - p[2]) ** 2) / p[1])
        p0 = [max(Y_values)-2, 0.00001, 0] # Initial guess for the parameters
    if peaks == 2:
        fitfunc = lambda p, x: p[0]*math.e ** (-1 * ((x - time - p[2]) ** 2) / p[1])
        p0 = [max(Y_values)-2, 0.00001, 0] # Initial guess for the parameters
        
        #fitfunc = lambda p, x: p[0]*math.e ** (-1 * ((x - time - p[2]) ** 2) / p[1]) + p[3]*math.e ** (-1 * ((x - time - p[4]) ** 2) / p[5])
        #p0 = [max(Y_values)-2, 0.00001, 0, max(Y_values)-2, 0.00001, 0.02] # Initial guess for the parameters
    errfunc = lambda p, x, y: fitfunc(p, x) - y # Distance to the target function

    try:
        p1, success = optimize.leastsq(errfunc, p0[:], args=(x_values, y_values-background),maxfev=10000) 
    except: # Fit failed
        p1 = p0
        success = 0
    usefull = (p1[0] > 1.5) and (p1[1] < 1e-3) and (success==1) # Only use the values if fit succeeded and peak has decent height
    area_fit = math.sqrt(math.pi)*p1[0] * math.sqrt(p1[1])
    
    area_count = np.sum(Y_values) - background*len(Y_values)
    if ax is not None:
        ax.plot(X_values, Y_values, 'k-')
        ax.plot(X_values, fitfunc(p1, X_values)+background, 'r-')
        ax.axvline(X_values[center-fit_width])
        ax.axvline(X_values[center+fit_width])
        ax.annotate(str(time), xy=(.05,.85), xycoords='axes fraction',fontsize=8)
        ax.annotate("Fit Area: {0:.0f}".format(area_fit*2500), xy=(.05,.8), xycoords='axes fraction',fontsize=8)
        ax.annotate("Count Area: {0:.0f}".format(area_count), xy=(.05,.75), xycoords='axes fraction',fontsize=8)
        ax.annotate("Usefull: " + str(usefull), xy=(.05,.7), xycoords='axes fraction',fontsize=8)
        #plt.show()
    return usefull, p1, area_count


db = mysql.connector.connect(host="servcinf-sql.fysik.dtu.dk", user="cinf_reader",passwd = "cinf_reader", db = "cinfdata")
cursor = db.cursor()

#spectrum_numbers = range(4160, 4255)
spectrum_numbers = range(4160, 4161)

x_values = {}
x_values['M4'] = {}
x_values['M4']['flighttime'] = [5.53]
x_values['M4']['peaks'] = 1
x_values['M4']['names'] = ['He']
"""
x_values['11.46'] = {}
x_values['11.46']['flighttime'] = [11.44, 11.46]
x_values['11.46']['names'] = ['11.46-low', '11.46-high']

x_values['11.82'] = {}
x_values['11.82']['flighttime'] = [11.81, 11.83]
x_values['11.82']['names'] = ['11.82-low', '11.82-high']
"""
#Todo: Also include fit-information such as exact peak position

#x_values = [5.53, 11.82, 39.81]
#x_values = [39.81]

dateplot_values = []
timestamps = []

for x in x_values:
    x_values[x]['peak_area'] = []
    x_values[x]['errors'] = []

pp = PdfPages('multipage.pdf')
for spectrum_number in spectrum_numbers:
    print(spectrum_number)
    t = time.time()
    try:
        Data = pickle.load(open(str(spectrum_number) + '.p', 'rb'), encoding='latin1')
    except (IOError, EOFError):
        cursor.execute('SELECT x*1000000,y FROM ' + XY_VALUES_TABLE +  ' where measurement = ' + str(spectrum_number))
        Data = np.array(cursor.fetchall())
        pickle.dump(Data, open(str(spectrum_number) + '.p', 'wb'))
    print(time.time() - t)

    try:
        NORMALISATION_FIELD
        query = 'select time, unix_timestamp(time), ' + NORMALISATION_FIELD + ' from ' + MEASUREMENT_TABLE + ' where id = "' + str(spectrum_number) + '"'
    except NameError: # No normalisation
        query = 'select time, unix_timestamp(time), 1 from ' + MEASUREMENT_TABLE + ' where id = "' + str(spectrum_number) + '"'
    cursor.execute(query)
    spectrum_info = cursor.fetchone()

    query = 'SELECT unix_timestamp(time), value FROM ' + DATEPLOT_TABLE + ' where type = ' + str(DATEPLOT_TYPE) + ' and time < "' + str(spectrum_info[0]) + '" order by time desc limit 1';
    cursor.execute(query)
    before_value = cursor.fetchone()
    time_before = spectrum_info[1] - before_value[0]
    assert(time_before > 0)

    query = 'SELECT unix_timestamp(time), value FROM ' + DATEPLOT_TABLE + ' where type = ' + str(DATEPLOT_TYPE) + ' and time > "' + str(spectrum_info[0]) + '" order by time limit 1';
    cursor.execute(query)
    after_value = cursor.fetchone()
    time_after = after_value[0] - spectrum_info[1]
    assert(time_before > 0)

    calculated_temp = (before_value[1] * time_before + after_value[1] * time_after) / (time_after + time_before)
    dateplot_values.append(calculated_temp)

    i = 0
    pdffig = plt.figure()    
    for x in x_values:
        i = i + 1
        axis = pdffig.add_subplot(2,2,i)
        if i == 1:
            axis.text(0,1.2,'Spectrum id: ' + str(spectrum_number),fontsize=12,transform = axis.transAxes)
            axis.text(0,1.1,'Sweeps: {0:.2e}'.format(spectrum_info[2]),fontsize=12,transform = axis.transAxes)
        usefull, p1, count = fit_peak(x_values[x]['flighttime'], x_values[x]['peaks'], Data, axis)
        area = math.sqrt(math.pi)*p1[0] * math.sqrt(p1[1])
        if usefull:
            x_values[x]['peak_area'].append(area * 2500 / spectrum_info[2])
            x_values[x]['errors'].append(math.sqrt(area * 2500) / spectrum_info[2]) 
        else:
            x_values[x]['peak_area'].append(None)
            x_values[x]['errors'].append(None) 
        print(usefull)
   
    timestamps.append(spectrum_info[1])
    plt.savefig(pp, format='pdf')                                                                      
    plt.close()
pp.close()

timestamps[:] = [t - timestamps[0] for t in timestamps]

fig = plt.figure()
axis = fig.add_subplot(1, 1, 1)

for x in x_values:
    try:
        axis.errorbar(timestamps, x_values[x]['peak_area'], linestyle='-', marker='o', label=x, yerr=x_values[x]['errors'])
    except TypeError: # Cannot plot errorbars on plots with missing points
        axis.plot(timestamps, x_values[x]['peak_area'], linestyle='-', marker='o', label=str(x))

axis2 = axis.twinx()
axis2.plot(timestamps, dateplot_values, 'k-', label='test')

axis.set_ylabel('Integraged peak area')
axis2.set_ylabel('Temperature')
axis.set_xlabel('Time / s')
#axis.set_yscale('log')

axis.legend(loc='upper left')

plt.show()

#print('----')
#print(dateplot_values)
#print('----')
#print(peak_areas)
#print('----')
